"""
Generatore della mappa HTML standalone interattiva con il design system
Geo-Intelligence 3D (MapLibre GL, KPI strip, Aside con schede e avatar guida).
Autore: Nicola Valigi Engine System
"""

import shutil
from pathlib import Path

def build_standalone_map(output_path: Path) -> Path:
    src_html = Path(__file__).resolve().parent / "web" / "index.html"
    if src_html.exists():
        shutil.copy2(src_html, output_path)
    return output_path

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "output" / "solar_land_map_standalone.html"
    build_standalone_map(out)
    print(f"Mappa generata in: {out}")
