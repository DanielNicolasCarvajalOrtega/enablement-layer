import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import database
from adapters.mcp.contabilidad import mcp
from adapters.mcp import pacientes  # noqa: F401  · importa por efecto: registra sus tools
from adapters.rest.contabilidad import router as contabilidad_router
from adapters.rest.pacientes import router as pacientes_router
from application.errors import DomainError, HTTP_STATUS_BY_ERROR
from config import settings
from observability import configure_logging
from security import BearerAuthMiddleware

configure_logging()

_START = time.time()

# Programa el server MCP; necesita su lifespan (task group) corriendo: se entra
# desde el lifespan de FastAPI (mcp_app.router.lifespan_context).
_mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.create_pool()
    async with _mcp_app.router.lifespan_context(_app):
        yield
    database.close_pool()


app = FastAPI(
    title="Enablement Layer — Control Contable + Pacientes",
    description=(
        "Capa de habilitación: REST + MCP sobre Oracle. Réplica del correo Control "
        "Contable y censo de pacientes por ciudad."
    ),
    version="1",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(BearerAuthMiddleware, settings=settings)

app.include_router(contabilidad_router)
app.include_router(pacientes_router)

app.mount(settings.MCP_PATH, _mcp_app)


@app.get("/health", tags=["ops"], include_in_schema=False)
def health() -> dict:
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - _START),
        "pool": database.pool_stats(),
        "mcp": settings.MCP_PATH,
    }


@app.exception_handler(DomainError)
async def domain_error_handler(_request, exc: DomainError):
    status = HTTP_STATUS_BY_ERROR.get(type(exc), 500)
    return JSONResponse(status_code=status, content={"error_code": exc.error_code, "message": exc.message})


# R18: el mensaje de error tiene que ser accionable, así que nombra el campo que
# efectivamente falló. No se hardcodea `fecha`: capabilities sin fecha (o con un
# filtro distinto) recibirían un mensaje que manda a corregir algo que no existe.
_VALIDATION_LOCS_EXCLUIDAS = ("query", "path", "body")


def _campo_invalido(error: dict) -> str:
    loc = [str(p) for p in error.get("loc", ()) if p not in _VALIDATION_LOCS_EXCLUIDAS]
    return ".".join(loc) or "argumentos"


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request, exc: RequestValidationError):
    campos = sorted({_campo_invalido(e) for e in exc.errors()})
    return JSONResponse(
        status_code=400,
        content={
            "error_code": "INVALID_ARGUMENT",
            "message": f"Argumentos inválidos: {', '.join(campos)}.",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": str(exc.detail), "message": str(exc.detail)},
    )