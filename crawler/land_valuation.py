"""
Land Valuation & Zoning Gatekeeper Module per SunPro (Nicola Valigi Engine System).
Determina il valore fondiario dei terreni sulla base di:
1. Destinazione Urbanistica (PRG/PGT: Zona E Agricola vs Zona D Edificabile)
2. Benchmark di Mercato Fondiario Reale (VAM Agenzia Entrate / Quotazioni ISMEA / OMI)
3. Caratteristiche Fisiche & Posizionali (Accessibilità viaria, orografia, buffer Z.I.)
4. Gatekeeper Anti-Inacquistabilità: Filtra ed esclude lotti edificabili industriali/commerciali (> 15 €/mq)
5. Modello del Premio di Trasformazione Energetica (+40% - +80% su valore agricolo per target 7.50 - 9.50 €/mq)
6. Moltiplicatore di Rendita Agraria (Canone Diritto di Superficie 3.000 €/ha/anno vs affitto agrario ordinario)

Autore: Nicola Valigi Engine System
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# ==============================================================================
# BENCHMARK FONDIARI AGRICOLI REGIONALI & PROVINCIALI (ISMEA / VAM / OMI 2025-2026)
# Valori medi in €/mq per terreni agricoli (Seminativo irriguo di pianura / asciutto)
# ==============================================================================
REGIONAL_AGRICULTURAL_BENCHMARKS = {
    # Lombardia: Alta produttività agraria di pianura, seminativo irriguo
    "Lombardia": {
        "default": 4.80,
        "province": {
            "Cremona": 5.40,
            "Brescia": 5.60,
            "Lodi": 5.20,
            "Pavia": 4.30,
            "Mantova": 4.90,
            "Bergamo": 5.10,
            "Milano": 5.30,
            "Monza e della Brianza": 5.50,
            "Sondrio": 2.20,
            "Como": 3.80,
            "Lecco": 3.90,
            "Varese": 4.20
        },
        "affitto_agrario_medio_ha": 650.0  # €/ha/anno ordinario
    },
    # Veneto: Pianura veneta irrigua
    "Veneto": {
        "default": 4.70,
        "province": {
            "Verona": 5.20,
            "Padova": 5.00,
            "Vicenza": 4.90,
            "Treviso": 5.10,
            "Rovigo": 3.90,
            "Venezia": 4.40,
            "Belluno": 2.10
        },
        "affitto_agrario_medio_ha": 600.0
    },
    # Emilia-Romagna: Terreni alluvionali altamente fertili
    "Emilia-Romagna": {
        "default": 4.60,
        "province": {
            "Bologna": 5.10,
            "Modena": 5.30,
            "Reggio Emilia": 5.00,
            "Parma": 4.80,
            "Piacenza": 4.50,
            "Ravenna": 4.40,
            "Forlì-Cesena": 4.20,
            "Ferrara": 3.70,
            "Rimini": 4.10
        },
        "affitto_agrario_medio_ha": 580.0
    },
    # Piemonte: Risicoltura e seminativi
    "Piemonte": {
        "default": 3.80,
        "province": {
            "Torino": 4.20,
            "Novara": 4.30,
            "Alessandria": 3.40,
            "Cuneo": 4.50,
            "Asti": 3.20,
            "Vercelli": 3.90,
            "Biella": 3.00,
            "Verbano-Cusio-Ossola": 2.00
        },
        "affitto_agrario_medio_ha": 500.0
    },
    # Toscana: Terreni collinari e pianure litoranee/valli
    "Toscana": {
        "default": 3.20,
        "province": {
            "Firenze": 3.80,
            "Pisa": 3.50,
            "Livorno": 3.40,
            "Arezzo": 3.10,
            "Siena": 3.00,
            "Grosseto": 2.80,
            "Lucca": 3.60,
            "Pistoia": 3.70
        },
        "affitto_agrario_medio_ha": 420.0
    },
    # Umbria / Marche
    "Umbria": {
        "default": 2.90,
        "province": {"Perugia": 3.00, "Terni": 2.80},
        "affitto_agrario_medio_ha": 380.0
    },
    "Marche": {
        "default": 3.10,
        "province": {"Ancona": 3.40, "Pesaro e Urbino": 3.20, "Macerata": 3.00, "Ascoli Piceno": 2.90},
        "affitto_agrario_medio_ha": 400.0
    },
    # Sud & Isole: Valori fondiari agricoli inferiori, elevata irradiazione
    "Puglia": {
        "default": 2.40,
        "province": {"Bari": 2.80, "Foggia": 2.30, "Lecce": 2.50, "Taranto": 2.40, "Brindisi": 2.60, "Barletta-Andria-Trani": 2.50},
        "affitto_agrario_medio_ha": 350.0
    },
    "Sicilia": {
        "default": 2.20,
        "province": {"Palermo": 2.30, "Catania": 2.60, "Siracusa": 2.50, "Trapani": 2.10, "Agrigento": 1.90, "Caltanissetta": 1.80},
        "affitto_agrario_medio_ha": 320.0
    }
}

# Soglia massima ammissibile per acquisizione fotovoltaica ground-mounted utility-scale
MAX_ACQUISITION_PRICE_EUR_MQ = 15.00  # Oltre questa soglia il terreno è NON ACQUISTABILE per FV a terra

# Canone Diritto di Superficie trentennale target bancabile
TARGET_SURFACE_RIGHT_RENT_EUR_HA = 3000.0  # €/ha/anno


@dataclass
class LandValuationReport:
    """Rapporto di valutazione estimativa e verifica di acquistabilità del terreno."""
    lead_id: str
    destinazione_urbanistica: str
    codice_zona_prg: str  # es. 'ZONA_E_AGRICOLA', 'ZONA_D_INDUSTRIALE', 'EX_CAVA', 'BROWNFIELD'
    valore_agricolo_base_eur_mq: float
    coefficiente_posizionale: float
    valore_mercato_ordinario_eur_mq: float
    valore_mercato_ordinario_totale_eur: float
    premio_trasformazione_pct: float
    prezzo_acquisto_target_eur_mq: float
    prezzo_acquisto_target_totale_eur: float
    affitto_agrario_ordinario_eur_ha: float
    canone_diritto_superficie_eur_ha: float
    moltiplicatore_rendita_proprietario: float
    status_acquistabilita: str  # 'ACQUISTABILE_BANCABILE' vs 'NON_ACQUISTABILE_SOVRASTIMATO'
    motivazione_acquistabilita: str
    sintesi_perizia: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "destinazione_urbanistica": self.destinazione_urbanistica,
            "codice_zona_prg": self.codice_zona_prg,
            "valore_agricolo_base_eur_mq": self.valore_agricolo_base_eur_mq,
            "coefficiente_posizionale": self.coefficiente_posizionale,
            "valore_mercato_ordinario_eur_mq": self.valore_mercato_ordinario_eur_mq,
            "valore_mercato_ordinario_totale_eur": self.valore_mercato_ordinario_totale_eur,
            "premio_trasformazione_pct": self.premio_trasformazione_pct,
            "prezzo_acquisto_target_eur_mq": self.prezzo_acquisto_target_eur_mq,
            "prezzo_acquisto_target_totale_eur": self.prezzo_acquisto_target_totale_eur,
            "affitto_agrario_ordinario_eur_ha": self.affitto_agrario_ordinario_eur_ha,
            "canone_diritto_superficie_eur_ha": self.canone_diritto_superficie_eur_ha,
            "moltiplicatore_rendita_proprietario": self.moltiplicatore_rendita_proprietario,
            "status_acquistabilita": self.status_acquistabilita,
            "motivazione_acquistabilita": self.motivazione_acquistabilita,
            "sintesi_perizia": self.sintesi_perizia
        }


def get_agricultural_benchmark(regione: str, provincia: str) -> Tuple[float, float]:
    """
    Restituisce (valore_agricolo_base_mq, affitto_agrario_medio_ha) per la data provincia/regione.
    """
    reg_data = REGIONAL_AGRICULTURAL_BENCHMARKS.get(regione)
    if not reg_data:
        # Fallback nazionale standard
        return 3.50, 450.0
    
    val_base = reg_data["province"].get(provincia, reg_data["default"])
    affitto_medio = reg_data.get("affitto_agrario_medio_ha", 450.0)
    return float(val_base), float(affitto_medio)


def evaluate_land_market_value(
    lead_id: str,
    regione: str,
    provincia: str,
    comune: str,
    superficie_mq: float,
    tipologia: str,
    distanza_zona_industriale_m: float = 100.0,
    distanza_autostrada_m: float = 500.0,
    destinazione_urbanistica_forzata: Optional[str] = None
) -> LandValuationReport:
    """
    Esegue la perizia estimativa comparativa fondiaria e applica il filtro gatekeeper di acquistabilità.
    
    Razionale Estimativo di SunPro:
    - NON calcola il prezzo del terreno in base alla resa energetica solare (evita valutazioni astratte o circolari).
    - Determina il valore reale di mercato del fondo in base alla DESTINAZIONE URBANISTICA (PRG/PGT) e POSIZIONE.
    - Se il terreno è un lotto edificabile industriale D (> 50-100 €/mq) -> SCARTA come NON ACQUISTABILE.
    - Se il terreno è ZONA E AGRICOLA entro 350m dalla Z.I. o 300m autostrada:
      applica il valore agricolo provinciale reale (VAM/ISMEA) + premio di trasformazione del +40%/+80%
      per arrivare al prezzo target bancabile (7.50 - 9.50 €/mq) che convince l'agricoltore a vendere.
    - Se il terreno è CAVA DISMESSA o BROWNFIELD DEGRADATO:
      valore residuo basso (2.50 - 4.50 €/mq) valorizzato con offerta transattiva a 7.50 - 8.20 €/mq.
    """
    # 1. Determinazione Destinazione Urbanistica e Codice PRG
    if destinazione_urbanistica_forzata:
        dest_urb = destinazione_urbanistica_forzata
        if "D" in dest_urb.upper() or "INDUSTRIALE" in dest_urb.upper():
            codice_zona = "ZONA_D_INDUSTRIALE"
        elif "E" in dest_urb.upper() or "AGRICOL" in dest_urb.upper():
            codice_zona = "ZONA_E_AGRICOLA"
        else:
            codice_zona = "ZONA_SPECIALE"
    else:
        if tipologia == "EX_CAVA":
            dest_urb = "Ambito Estrattivo Dismesso / Recupero Ambientale (Zona F/Speciale)"
            codice_zona = "EX_CAVA"
        elif tipologia == "BROWNFIELD":
            dest_urb = "Sito Degradato / Ex Polo Produttivo Dismesso (Brownfield)"
            codice_zona = "BROWNFIELD"
        elif tipologia == "BUFFER_AUTOSTRADALE_300M":
            dest_urb = "Zona E — Agricola Ordinaria (Fascia di Rispetto Infrastrutturale Autostradale 300m)"
            codice_zona = "ZONA_E_AGRICOLA"
        else:
            # Tipologia standard D.Lgs. 199/2021: terreno agricolo contiguo alla zona industriale
            dest_urb = "Zona E — Agricola Ordinaria (Fascia Perimetrale 350m contigua a Polo Produttivo)"
            codice_zona = "ZONA_E_AGRICOLA"

    # 2. Benchmark Agricolo di Mercato
    valore_base_agri, affitto_medio_ha = get_agricultural_benchmark(regione, provincia)

    # 3. Verifica Gatekeeper di Acquistabilità Fondiaria
    if codice_zona == "ZONA_D_INDUSTRIALE":
        # Terreno edificabile a destinazione produttiva/logistica (PIP)
        # Valore di mercato 50 - 120 €/mq -> Totalmente inacquistabile per parchi solari utility-scale a terra
        val_mercato_edificabile = 75.00
        return LandValuationReport(
            lead_id=lead_id,
            destinazione_urbanistica=dest_urb,
            codice_zona_prg=codice_zona,
            valore_agricolo_base_eur_mq=valore_base_agri,
            coefficiente_posizionale=1.0,
            valore_mercato_ordinario_eur_mq=val_mercato_edificabile,
            valore_mercato_ordinario_totale_eur=round(superficie_mq * val_mercato_edificabile, 0),
            premio_trasformazione_pct=0.0,
            prezzo_acquisto_target_eur_mq=val_mercato_edificabile,
            prezzo_acquisto_target_totale_eur=round(superficie_mq * val_mercato_edificabile, 0),
            affitto_agrario_ordinario_eur_ha=affitto_medio_ha,
            canone_diritto_superficie_eur_ha=TARGET_SURFACE_RIGHT_RENT_EUR_HA,
            moltiplicatore_rendita_proprietario=1.0,
            status_acquistabilita="NON_ACQUISTABILE_SOVRASTIMATO",
            motivazione_acquistabilita=(
                f"Lotto a destinazione urbanistica produttiva/edificabile Zona D (Valore stimato {val_mercato_edificabile} €/mq > {MAX_ACQUISITION_PRICE_EUR_MQ} €/mq). "
                "Inacquistabile per parchi fotovoltaici ground-mounted poiché il costo fondiario supererebbe il CAPEX dell'intero impianto. "
                "SunPro scarta questi lotti per concentrarsi solo su Zona E contigua."
            ),
            sintesi_perizia="SCARTATO: Destinazione urbanistica industriale con indice edificatorio oneroso."
        )

    # 4. Calcolo Coefficiente Posizionale e Valore Ordinario di Mercato
    # Fattori:
    # - Prossimità ad assi viari primari (facilità logistica cantiere): +5% a +10%
    # - Contiguità con polo produttivo (valore di aspettativa agricola): +5%
    coeff_posizionale = 1.00
    if distanza_autostrada_m <= 1000:
        coeff_posizionale += 0.05
    if distanza_zona_industriale_m <= 200:
        coeff_posizionale += 0.05

    if codice_zona in ["EX_CAVA", "BROWNFIELD"]:
        # Aree degradate: valore di mercato ordinario depresso per passività ambientali e ripristino morfologico
        valore_mercato_ordinario_mq = round(valore_base_agri * 0.75, 2)  # es. 3.00 - 4.00 €/mq
        # Premio di valorizzazione per transazione rapida
        prezzo_target_mq = 7.80 if codice_zona == "EX_CAVA" else 8.10
        premio_pct = round(((prezzo_target_mq - valore_mercato_ordinario_mq) / valore_mercato_ordinario_mq) * 100.0, 1)
    else:
        # ZONA E AGRICOLA ordinaria
        valore_mercato_ordinario_mq = round(valore_base_agri * coeff_posizionale, 2)  # es. 4.50 - 5.80 €/mq
        # Premio di Acquisizione Energetica / Trasformazione Fondiaria (+50% - +75% rispetto al valore agricolo)
        # Formula target SunPro: clamp(valore_mercato * 1.60, 7.50, 9.20)
        target_prezzo_stimato = valore_mercato_ordinario_mq * 1.60
        prezzo_target_mq = round(min(9.20, max(7.80, target_prezzo_stimato)), 2)
        premio_pct = round(((prezzo_target_mq - valore_mercato_ordinario_mq) / valore_mercato_ordinario_mq) * 100.0, 1)

    valore_mercato_totale = round(superficie_mq * valore_mercato_ordinario_mq, 0)
    prezzo_target_totale = round(superficie_mq * prezzo_target_mq, 0)

    # 5. Modello Diritto di Superficie vs Affitto Agrario
    ha = superficie_mq / 10000.0
    moltiplicatore_rendita = round(TARGET_SURFACE_RIGHT_RENT_EUR_HA / max(100.0, affitto_medio_ha), 1)

    sintesi = (
        f"Terreno censito in {dest_urb}. Valore agricolo ordinario VAM/ISMEA di zona: {valore_mercato_ordinario_mq:.2f} €/mq "
        f"({int(valore_mercato_totale):,} €). Offerta target SunPro: {prezzo_target_mq:.2f} €/mq ({int(prezzo_target_totale):,} €), "
        f"con un premio di trasformazione del +{premio_pct:.1f}% che rende l'offerta altamente competitiva per la proprietà. "
        f"In alternativa, il canone di superficie a 3.000 €/ha/anno garantisce {moltiplicatore_rendita:.1f}x il reddito dell'affitto agrario ordinario."
    )

    return LandValuationReport(
        lead_id=lead_id,
        destinazione_urbanistica=dest_urb,
        codice_zona_prg=codice_zona,
        valore_agricolo_base_eur_mq=valore_base_agri,
        coefficiente_posizionale=coeff_posizionale,
        valore_mercato_ordinario_eur_mq=valore_mercato_ordinario_mq,
        valore_mercato_ordinario_totale_eur=valore_mercato_totale,
        premio_trasformazione_pct=premio_pct,
        prezzo_acquisto_target_eur_mq=prezzo_target_mq,
        prezzo_acquisto_target_totale_eur=prezzo_target_totale,
        affitto_agrario_ordinario_eur_ha=affitto_medio_ha,
        canone_diritto_superficie_eur_ha=TARGET_SURFACE_RIGHT_RENT_EUR_HA,
        moltiplicatore_rendita_proprietario=moltiplicatore_rendita,
        status_acquistabilita="ACQUISTABILE_BANCABILE",
        motivazione_acquistabilita="Terreno a vocazione agricola o industriale dismessa con parametri di costo compatibili con il modello LCOE fotovoltaico.",
        sintesi_perizia=sintesi
    )
