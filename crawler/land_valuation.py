# ==============================================================================
# PROPRIETARY AND CONFIDENTIAL — NICOLA VALIGI (HOUDINICK)
# SunPro Geo-Intelligence 3D — Nicola Valigi Engine System
# Copyright (c) 2026 Nicola Valigi. All Rights Reserved.
# Autore & Titolare Esclusivo della Proprietà Intellettuale: Nicola Valigi (Houdinick)
# Email: 305862309+nicolavaligi@users.noreply.github.com | GitHub: nicolavaligi
# 
# Vietata la riproduzione, copia o appropriazione non autorizzata (L. 633/1941).
# ==============================================================================
"""
Land Valuation & Zoning Gatekeeper Module per SunPro (Nicola Valigi Engine System).
Determina il valore fondiario dei terreni sulla base di:
1. Destinazione Urbanistica (PRG/PGT: Zona E Agricola vs Zona D Edificabile)
2. Benchmark VAM 2026 Ufficiali (es. BURERT n. 75 del 02/04/2026: Cadeo 5,45 €/mq, Pontenure 5,85 €/mq) e Quotazioni ISMEA
3. Distinzione rigorosa tra Valore Amministrativo VAM (€/mq) e Prezzo Target di Trattativa (tetto ≤ 8,00 €/mq)
4. Gatekeeper Anti-Inacquistabilità: Filtra ed esclude lotti edificabili industriali/commerciali (> 15 €/mq)
5. Moltiplicatore di Rendita Agraria (Canone Diritto di Superficie 3.000 €/ha/anno vs affitto agrario ordinario)

Autore & Titolare IP: Nicola Valigi (Houdinick)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# Valori Agricoli Medi (VAM 2026) puntuali per comune (Seminativo Irriguo di Pianura, €/mq)
# Fonti: BUR Emilia-Romagna n. 75 del 02/04/2026, Commissioni Provinciali Espropri Lombardia/Piemonte/Veneto
COMUNE_VAM_2026_EUR_MQ: Dict[str, float] = {
    "Cadeo": 5.45,
    "Pontenure": 5.85,
    "Piacenza": 5.65,
    "Fiorenzuola d'Arda": 5.45,
    "Alseno": 5.45,
    "Caorso": 5.55,
    "San Pietro in Cerro": 5.50,
    "Monticelli d'Ongina": 5.50,
    "Castelvetro Piacentino": 5.50,
    "Rottofreno": 5.65,
    "Calendasco": 5.65,
    "Sarmato": 5.60,
    "Castel San Giovanni": 5.60,
    "Fidenza": 5.15,
    "Fontevivo": 5.10,
    "Santhià": 3.95,
    "Galliate": 4.30,
    "Felizzano": 3.45,
    "Tortona": 3.65,
    "Alessandria": 3.50,
    "Casei Gerola": 4.35,
    "Cava Manara": 4.25,
    "Casalpusterlengo": 5.25,
    "Codogno": 5.20,
    "Turano Lodigiano": 5.10,
    "Montanaso Lombardo": 5.15,
    "Manerbio": 5.55,
    "Leno": 5.50,
    "Calcinato": 5.45,
    "Orzinuovi": 5.40,
    "Bagnolo Mella": 5.45,
    "Verolanuova": 5.40,
    "Caravaggio": 5.15,
    "Calcio": 5.10,
    "Sommacampagna": 5.20,
    "Nogarole Rocca": 5.10,
    "Gambellara": 4.95,
    "Campogalliano": 5.30,
    "Forlì": 4.35,
    "Longiano": 4.25,
    "Faenza": 4.40,
    "Jesi": 3.45,
    "Terranuova Bracciolini": 3.20,
    "Montevarchi": 3.15,
}

REGIONAL_AGRICULTURAL_BENCHMARKS = {
    "Lombardia": {
        "default": 4.80,
        "province": {
            "Cremona": 5.20,
            "Brescia": 5.45,
            "Lodi": 5.15,
            "Pavia": 4.30,
            "Mantova": 4.85,
            "Bergamo": 5.10,
            "Milano": 5.30,
            "Monza e della Brianza": 5.50,
            "Sondrio": 2.20,
            "Como": 3.80,
            "Lecco": 3.90,
            "Varese": 4.20
        },
        "affitto_agrario_medio_ha": 650.0
    },
    "Veneto": {
        "default": 4.70,
        "province": {
            "Verona": 5.15,
            "Padova": 5.00,
            "Vicenza": 4.90,
            "Treviso": 5.10,
            "Rovigo": 3.90,
            "Venezia": 4.40,
            "Belluno": 2.10
        },
        "affitto_agrario_medio_ha": 600.0
    },
    "Emilia-Romagna": {
        "default": 4.60,
        "province": {
            "Bologna": 5.10,
            "Modena": 5.30,
            "Reggio Emilia": 5.00,
            "Parma": 5.10,
            "Piacenza": 5.45,
            "Ravenna": 4.40,
            "Forlì-Cesena": 4.30,
            "Ferrara": 3.70,
            "Rimini": 4.10
        },
        "affitto_agrario_medio_ha": 580.0
    },
    "Piemonte": {
        "default": 3.80,
        "province": {
            "Torino": 4.20,
            "Novara": 4.30,
            "Alessandria": 3.55,
            "Cuneo": 4.50,
            "Asti": 3.20,
            "Vercelli": 3.95,
            "Biella": 3.00,
            "Verbano-Cusio-Ossola": 2.00
        },
        "affitto_agrario_medio_ha": 500.0
    },
    "Toscana": {
        "default": 3.20,
        "province": {
            "Firenze": 3.80,
            "Pisa": 3.50,
            "Livorno": 3.40,
            "Arezzo": 3.15,
            "Siena": 3.00,
            "Grosseto": 2.80,
            "Lucca": 3.60,
            "Pistoia": 3.70
        },
        "affitto_agrario_medio_ha": 420.0
    },
    "Umbria": {
        "default": 2.90,
        "province": {"Perugia": 3.00, "Terni": 2.80},
        "affitto_agrario_medio_ha": 380.0
    },
    "Marche": {
        "default": 3.10,
        "province": {"Ancona": 3.45, "Pesaro e Urbino": 3.20, "Macerata": 3.00, "Ascoli Piceno": 2.90},
        "affitto_agrario_medio_ha": 400.0
    },
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
MAX_ACQUISITION_PRICE_EUR_MQ = 15.00
# Soglia operativa target richiesta dal mandato investitore (≤ 8,00 €/mq)
TARGET_MAX_BUY_PRICE_EUR_MQ = 8.00
# Canone Diritto di Superficie trentennale target bancabile
TARGET_SURFACE_RIGHT_RENT_EUR_HA = 3000.0


@dataclass
class LandValuationReport:
    """Rapporto di valutazione estimativa VAM 2026 vs Trattativa e verifica di acquistabilità."""
    lead_id: str
    destinazione_urbanistica: str
    codice_zona_prg: str
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
    status_acquistabilita: str
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


def get_agricultural_benchmark(regione: str, provincia: str, comune: str = "") -> Tuple[float, float]:
    """
    Restituisce (valore_vam_2026_mq, affitto_agrario_medio_ha) dando priorità al VAM 2026 comunale.
    """
    reg_data = REGIONAL_AGRICULTURAL_BENCHMARKS.get(regione)
    affitto_medio = reg_data.get("affitto_agrario_medio_ha", 450.0) if reg_data else 450.0

    if comune and comune in COMUNE_VAM_2026_EUR_MQ:
        return float(COMUNE_VAM_2026_EUR_MQ[comune]), float(affitto_medio)

    if not reg_data:
        return 3.50, 450.0

    val_base = reg_data["province"].get(provincia, reg_data["default"])
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
    Esegue la perizia estimativa distinguendo tra:
    - Valore Agricolo Medio VAM 2026 (valore amministrativo provinciale/comunale, es. 5,45 €/mq a Cadeo, 5,85 €/mq a Pontenure)
    - Prezzo Target Massimale di Acquisto in Trattativa (calibrato entro la soglia ≤ 8,00 €/mq richiesta dal mandato).
    """
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
            dest_urb = "Ambito Estrattivo Dismesso / Recupero Ambientale (Da confermare in CDU)"
            codice_zona = "EX_CAVA"
        elif tipologia == "BROWNFIELD":
            dest_urb = "Sito Degradato / Ex Comparto Produttivo Dismesso (Brownfield)"
            codice_zona = "BROWNFIELD"
        elif distanza_autostrada_m <= 300:
            dest_urb = "Zona E — Agricola Ordinaria (Fascia ≤300m Autostrada D.Lgs. 199/2021 — CDU da verificare)"
            codice_zona = "ZONA_E_AGRICOLA"
        else:
            dest_urb = "Zona E — Agricola Ordinaria (Buffer ≤350m Polo Produttivo D.Lgs. 199/2021 — CDU da verificare)"
            codice_zona = "ZONA_E_AGRICOLA"

    valore_base_agri, affitto_medio_ha = get_agricultural_benchmark(regione, provincia, comune)

    if codice_zona == "ZONA_D_INDUSTRIALE":
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
                f"Lotto a destinazione urbanistica produttiva/edificabile Zona D (Valore stimato {val_mercato_edificabile} €/mq > {MAX_ACQUISITION_PRICE_EUR_MQ} €/mq)."
            ),
            sintesi_perizia="SCARTATO: Destinazione urbanistica industriale con indice edificatorio oneroso."
        )

    coeff_posizionale = 1.00
    if distanza_autostrada_m <= 300:
        coeff_posizionale += 0.05
    if distanza_zona_industriale_m <= 200:
        coeff_posizionale += 0.04

    if codice_zona in ["EX_CAVA", "BROWNFIELD"]:
        valore_mercato_ordinario_mq = round(valore_base_agri * 0.80, 2)
        prezzo_target_mq = 7.20 if codice_zona == "EX_CAVA" else 7.50
        premio_pct = round(((prezzo_target_mq - valore_mercato_ordinario_mq) / max(0.5, valore_mercato_ordinario_mq)) * 100.0, 1)
    else:
        # ZONA E AGRICOLA: VAM amministrativo di partenza + premio negoziale contenuto entro il tetto di 8,00 €/mq
        valore_mercato_ordinario_mq = round(valore_base_agri * coeff_posizionale, 2)
        target_prezzo_stimato = valore_mercato_ordinario_mq * 1.32
        prezzo_target_mq = round(min(TARGET_MAX_BUY_PRICE_EUR_MQ, max(6.50, target_prezzo_stimato)), 2)
        premio_pct = round(((prezzo_target_mq - valore_base_agri) / max(0.5, valore_base_agri)) * 100.0, 1)

    valore_mercato_totale = round(superficie_mq * valore_mercato_ordinario_mq, 0)
    prezzo_target_totale = round(superficie_mq * prezzo_target_mq, 0)

    moltiplicatore_rendita = round(TARGET_SURFACE_RIGHT_RENT_EUR_HA / max(100.0, affitto_medio_ha), 1)

    sintesi = (
        f"Riferimento amministrativo VAM 2026 ({comune}): {valore_base_agri:.2f} €/mq "
        f"(stima mercato agricolo ordinario: {valore_mercato_ordinario_mq:.2f} €/mq). "
        f"Tetto offerta di acquisto in trattativa: {prezzo_target_mq:.2f} €/mq (≤ 8,00 €/mq, tot. {int(prezzo_target_totale):,} €), "
        f"pari a +{premio_pct:.1f}% sul VAM amministrativo. "
        f"Nota: il prezzo reale emerge solo dalla trattativa con la proprietà; la destinazione urbanistica puntuale va confermata tramite CDU."
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
        status_acquistabilita="COMPATIBILE_SOGLIA_8_EUR_MQ",
        motivazione_acquistabilita="Valore VAM e target di negoziazione pienamente entro la soglia massima di 8,00 €/mq.",
        sintesi_perizia=sintesi
    )
