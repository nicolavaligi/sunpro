"""
FastAPI / Starlette ASGI Server per Geo-Intelligence 3D — SunPro.
Serve l'interfaccia 100vh MapLibre GL 3D, gli endpoint REST e la generazione al volo dei PDF.
Autore: Nicola Valigi Engine System
"""

import os
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse, HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import uvicorn

from data.storage import get_all_leads, get_lead
from reports.generator import generate_pdf_dossier
from sync_to_drive import sync_prototype_to_drive

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
INDEX_HTML = WEB_DIR / "index.html"

async def homepage(request):
    if not INDEX_HTML.exists():
        return HTMLResponse("<h1>Index non trovato</h1>", status_code=404)
    return FileResponse(INDEX_HTML, media_type="text/html")

async def api_leads(request):
    regione = request.query_params.get("regione")
    min_score = float(request.query_params.get("min_score", 0.0))
    leads = get_all_leads(regione=regione if regione != "Tutte" else None, min_score=min_score)
    return JSONResponse(leads)

async def api_lead_detail(request):
    lead_id = request.path_params["lead_id"]
    lead = get_lead(lead_id)
    if not lead:
        return JSONResponse({"error": "Lead not found"}, status_code=404)
    return JSONResponse(lead)

async def api_download_dossier(request):
    lead_id = request.path_params["lead_id"]
    lead = get_lead(lead_id)
    if not lead:
        return JSONResponse({"error": "Lead not found"}, status_code=404)
    pdf_path = generate_pdf_dossier(lead)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"dossier_{lead_id}_{lead['comune'].lower()}.pdf"
    )

async def api_sync_drive_endpoint(request):
    try:
        sync_prototype_to_drive()
        return JSONResponse({"status": "success", "message": "Sincronizzazione completata con Google Drive!"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

routes = [
    Route("/", homepage),
    Route("/api/leads", api_leads),
    Route("/api/leads/{lead_id}", api_lead_detail),
    Route("/api/dossier/{lead_id}", api_download_dossier),
    Route("/api/sync-drive", api_sync_drive_endpoint, methods=["POST", "GET"]),
]

app = Starlette(routes=routes)

def run():
    print("☀️ Avvio Geo-Intelligence 3D su http://localhost:8503...")
    uvicorn.run(app, host="0.0.0.0", port=8503, log_level="info")

if __name__ == "__main__":
    run()
