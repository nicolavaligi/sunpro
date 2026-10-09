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
Modulo PVGIS Client per SunPro (Nicola Valigi Engine System).
Interroga l'API scientifica PVGIS della Commissione Europea (JRC)
per estrarre l'irraggiamento solare reale (kWh/m2/anno) e la resa specifica (kWh/kWp/anno).
Autore & Titolare IP: Nicola Valigi (Houdinick)
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import httpx

from config import DATA_DIR

CACHE_FILE = DATA_DIR / "cache_pvgis.json"

class PVGISClient:
    """Client scientifico per l'API PVGIS JRC della Commissione Europea."""
    BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def _cache_key(self, lat: float, lon: float) -> str:
        return f"{lat:.2f},{lon:.2f}"

    def get_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Restituisce i dati energetici scientifici PVGIS:
        - kwh_kwp_anno: produzione specifica annua per kWp installato (E_y)
        - kwh_m2_anno: irraggiamento solare globale annuo (H(i)_y)
        - inclinazione_ottimale: tilt ottimale dei moduli
        - fonte: 'PVGIS_JRC_API' oppure 'MODELLO_SCIENTIFICO_REGIONAL_FALLBACK'
        """
        key = self._cache_key(lat, lon)
        if key in self.cache:
            res = self.cache[key]
            res["cached"] = True
            return res

        params = {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "peakpower": 1.0,
            "loss": 14.0,           # Perdite standard BOS (inverter, cavi, sporcamento)
            "optimalinclination": 1,
            "outputformat": "json"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    totals = data.get("outputs", {}).get("totals", {}).get("fixed", {})
                    e_y = float(totals.get("E_y", 0.0))
                    h_y = float(totals.get("H(i)_y", 0.0))
                    opt_angle = totals.get("opt_angle") or 30

                    # Calcolo producibilità con Tracker Monoassiale asse N-S (rotazione E-W)
                    # Basato su modelli standard PVsyst / JRC per l'Italia (boost medio +19% - +22%)
                    boost_tracker_pct = round(19.2 + max(0.0, (45.0 - lat)) * 0.22, 1)
                    kwh_kwp_tracker = round(e_y * (1.0 + (boost_tracker_pct / 100.0)), 1)
                    kwh_m2_tracker = round(h_y * (1.0 + (boost_tracker_pct / 100.0)), 1)

                    result = {
                        "lat": round(lat, 4),
                        "lon": round(lon, 4),
                        "kwh_kwp_anno": round(e_y, 1),
                        "kwh_m2_anno": round(h_y, 1),
                        "kwh_kwp_tracker": kwh_kwp_tracker,
                        "kwh_m2_tracker": kwh_m2_tracker,
                        "boost_tracker_pct": boost_tracker_pct,
                        "inclinazione_ottimale": opt_angle,
                        "fonte": "PVGIS_JRC_COMMISSIONE_EUROPEA_v5.2",
                        "cached": False
                    }
                    self.cache[key] = result
                    self._save_cache()
                    return result
        except Exception:
            pass

        # Fallback scientifico ad alta precisione per l'Italia (gradiente latitudinale ENEA)
        # 46.5°N (Alpi) ~ 1220 kWh/kWp -> 37.0°N (Sicilia) ~ 1680 kWh/kWp
        lat_clamped = max(36.0, min(47.0, lat))
        kwh_kwp = round(1700.0 - ((lat_clamped - 36.5) * 45.0), 1)
        kwh_m2 = round(kwh_kwp * 1.30, 1)
        opt_angle = round(max(25, min(36, 48 - lat * 0.35)))

        boost_tracker_pct = round(19.2 + max(0.0, (45.0 - lat)) * 0.22, 1)
        kwh_kwp_tracker = round(kwh_kwp * (1.0 + (boost_tracker_pct / 100.0)), 1)
        kwh_m2_tracker = round(kwh_m2 * (1.0 + (boost_tracker_pct / 100.0)), 1)

        result = {
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "kwh_kwp_anno": kwh_kwp,
            "kwh_m2_anno": kwh_m2,
            "kwh_kwp_tracker": kwh_kwp_tracker,
            "kwh_m2_tracker": kwh_m2_tracker,
            "boost_tracker_pct": boost_tracker_pct,
            "inclinazione_ottimale": opt_angle,
            "fonte": "MODELLO_SCIENTIFICO_ENEA_FALLBACK",
            "cached": False
        }
        self.cache[key] = result
        self._save_cache()
        return result

# Singleton client per riuso
pvgis_client = PVGISClient()

def get_pvgis_irradiance(lat: float, lon: float) -> Dict[str, Any]:
    """Helper rapido per ottenere l'irraggiamento solare PVGIS."""
    return pvgis_client.get_solar_data(lat, lon)

def get_solar_comparison(lat: float, lon: float) -> Dict[str, Any]:
    """Restituisce il confronto scientifico di producibilità: Strutture Fisse vs Inseguitori Tracker."""
    data = pvgis_client.get_solar_data(lat, lon)
    return {
        "fisso_kwh_kwp": data["kwh_kwp_anno"],
        "tracker_kwh_kwp": data.get("kwh_kwp_tracker", round(data["kwh_kwp_anno"] * 1.20, 1)),
        "boost_pct": data.get("boost_tracker_pct", 20.0),
        "inclinazione_ottimale": data.get("inclinazione_ottimale", 30),
        "fonte": data.get("fonte", "PVGIS_JRC")
    }
