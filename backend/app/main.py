"""
Aplicación Principal FastAPI para EcoNorma Perú
Plataforma de Consulta de Estándares Ambientales del Perú
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager

from .config import APP_NAME, APP_TAGLINE, APP_SUBTITLE, APP_VERSION, DB_PATH
from .database import init_db, get_all_raw_parameters, get_all_norms
from .routers import parameters, norms, comparator, stats, contact, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar Base de Datos y Seeds
    init_db()
    yield

app = FastAPI(
    title=APP_NAME,
    description=APP_TAGLINE,
    version=APP_VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Routers
app.include_router(parameters.router)
app.include_router(norms.router)
app.include_router(comparator.router)
app.include_router(stats.router)
app.include_router(contact.router)
app.include_router(admin.router)

# Montar Archivos Estáticos
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/robots.txt")
def robots_txt():
    content = "User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: /sitemap.xml\n"
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml")
def sitemap_xml():
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>',
        '  <url><loc>/#eca</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        '  <url><loc>/#lmp</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        '  <url><loc>/#vma</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        '  <url><loc>/#comparador</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        '  <url><loc>/#normas</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        '  <url><loc>/#fuentes</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>',
        '  <url><loc>/#contacto</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>'
    ]
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml")

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(full_path: str):
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>EcoNorma Perú en construcción</h1>", status_code=200)
