import asyncio
import json

import pytest
from fastapi.exceptions import RequestValidationError

from app import app, validation_error_handler
from application.registry import all_contracts
from database import OracleNotConfiguredError

TOKEN = {"Authorization": "Bearer tok-contador-test"}
# El único rol que todas las capabilities comparten: sirve para los tests que recorren
# todos los endpoints (Oracle caído) sin que un 403 por rol tape un 503 por datos.
TOKEN_COMUN = {"Authorization": "Bearer tok-gerente-test"}

FECHA = {"fecha": "2025-05-12"}

# (ruta, parámetros canónicos de la llamada válida). El bloque de pacientes no
# acepta filtros, así que su entrada canónica va vacía: los tests de auth se
# parametrizan igual, pero los de `fecha` solo corren donde la fecha es contrato.
ENDPOINTS = [
    ("/api/contabilidad/ingresos-por-tipo-pago", FECHA),
    ("/api/contabilidad/resumen-deuda", FECHA),
    ("/api/contabilidad/ingresos-por-tipo-tarjeta", FECHA),
    ("/api/contabilidad/ingresos-por-tipo-prevision", FECHA),
    ("/api/contabilidad/boletas-emitidas-por-usuario", FECHA),
    ("/api/contabilidad/boletas-anuladas-por-usuario", FECHA),
    ("/api/pacientes/pacientes-por-ciudad-chile", {}),
]
ENDPOINT_IDS = [p for p, _ in ENDPOINTS]
ENDPOINTS_CON_FECHA = [(p, q) for p, q in ENDPOINTS if q]
ENDPOINT_IDS_CON_FECHA = [p for p, _ in ENDPOINTS_CON_FECHA]

REPO_POR_PATH = {
    "/api/contabilidad/": "infrastructure.oracle.contabilidad_repository.ContabilidadRepository.pool",
    "/api/pacientes/": "infrastructure.oracle.pacientes_repository.PacientesRepository.pool",
}


def test_health_sin_auth(client):
    # No requiere auth. El estado del pool depende de si el DSN está alcanzable,
    # así que el aserto no depende del entorno del que corre la suite.
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["pool"]["status"] in {"ok", "not_configured"}


# --------------------------------------------------------------------------- #
# Superficie pública: todo endpoint del registry existe en OpenAPI
# --------------------------------------------------------------------------- #


def test_registro_y_openapi_coinciden(client):
    # Si el registry declara una ruta que no está montada, el agente recibe 404.
    spec = client.get("/openapi.json").json()
    montadas = {p for p in spec["paths"]}
    declaradas = {c.rest_path for c in all_contracts()}
    assert declaradas <= montadas, f"endpoints del registry sin montar: {declaradas - montadas}"
    assert set(ENDPOINT_IDS) == declaradas


# --------------------------------------------------------------------------- #
# Autenticación y autorización (Nivel 2)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("path,params", ENDPOINTS, ids=ENDPOINT_IDS)
def test_sin_token_es_401(client, path, params):
    resp = client.get(path, params=params)
    assert resp.status_code == 401
    assert resp.json()["error_code"] == "UNAUTHORIZED"


@pytest.mark.parametrize("path,params", ENDPOINTS, ids=ENDPOINT_IDS)
def test_token_invalido_es_401(client, path, params):
    resp = client.get(
        path,
        params=params,
        headers={"Authorization": "Bearer token-inexistente"},
    )
    assert resp.status_code == 401


@pytest.mark.parametrize("path,params", ENDPOINTS_CON_FECHA, ids=ENDPOINT_IDS_CON_FECHA)
def test_fecha_invalida_es_400_invalid_argument(client, path, params):
    resp = client.get(path, params={"fecha": "banana"}, headers=TOKEN)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error_code"] == "INVALID_ARGUMENT"
    # R18: el mensaje nombra el campo que falló. Acá ese campo es `fecha` y el
    # handler lo deriva de la validación, no de una constante.
    assert "fecha" in body["message"]


@pytest.mark.parametrize("path,params", ENDPOINTS_CON_FECHA, ids=ENDPOINT_IDS_CON_FECHA)
def test_fecha_ausente_es_400(client, path, params):
    resp = client.get(path, headers=TOKEN)
    assert resp.status_code == 400
    assert resp.json()["error_code"] == "INVALID_ARGUMENT"


def test_token_del_contador_no_alcanza_pacientes(client):
    # El censo por ciudad no expone el token contable: `contador` no está en los
    # roles de la capability.
    resp = client.get(
        "/api/pacientes/pacientes-por-ciudad-chile",
        headers=TOKEN,
    )
    assert resp.status_code == 403
    assert resp.json()["error_code"] == "FORBIDDEN"


@pytest.mark.parametrize(
    "token",
    ["tok-analista-test", "tok-gerente-test", "tok-ai-test"],
)
def test_los_tres_roles_de_pacientes_pueden_acceder(client, token):
    resp = client.get(
        "/api/pacientes/pacientes-por-ciudad-chile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code != 401
    assert resp.status_code != 403


def test_origen_invalido_es_400(client):
    resp = client.get(
        "/api/contabilidad/ingresos-por-tipo-tarjeta",
        params={"fecha": "2025-05-12", "origen": "CAJITA"},
        headers=TOKEN,
    )
    assert resp.status_code == 400
    assert resp.json()["error_code"] == "INVALID_ARGUMENT"


def test_el_handler_de_validacion_deriva_el_mensaje_del_error():
    # R18: el 400 tiene que ser accionable, así que nombra el campo que falló.
    # El handler fijaba "fecha debe ser YYYY-MM-DD" para cualquier error, lo que
    # funciona mientras todos los filtros se llamen `fecha` y miente en cuanto
    # aparezca uno distinto.
    #
    # Hoy no hay ningún endpoint que dispare esa rama con un campo no-fecha:
    # `origen` entra como `str | None` y lo rechaza el service, no FastAPI. Se
    # invoca el handler directamente para fijar el comportamiento antes de que
    # exista ese filtro.
    exc = RequestValidationError(
        [
            {
                "type": "int_parsing",
                "loc": ("query", "plazas"),
                "msg": "Input should be a valid integer",
                "input": "muchas",
            }
        ]
    )
    resp = asyncio.run(validation_error_handler(None, exc))
    body = json.loads(resp.body)
    assert resp.status_code == 400
    assert body["error_code"] == "INVALID_ARGUMENT"
    assert "plazas" in body["message"]
    assert "fecha" not in body["message"]


@pytest.mark.parametrize(
    "token",
    ["tok-contador-test", "tok-analista-test", "tok-gerente-test", "tok-ai-test"],
)
def test_todos_los_roles_del_contrato_pueden_acceder(client, token):
    resp = client.get(
        "/api/contabilidad/resumen-deuda",
        params={"fecha": "2025-05-12"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code != 403


# --------------------------------------------------------------------------- #
# Caída de Oracle nunca se disfraza de "tabla vacía" (Nivel 2)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("path,params", ENDPOINTS, ids=ENDPOINT_IDS)
def test_oracle_caido_es_503_unavailable(client, monkeypatch, path, params):
    objetivo = next(v for prefijo, v in REPO_POR_PATH.items() if path.startswith(prefijo))
    monkeypatch.setattr(
        objetivo,
        property(lambda self: (_ for _ in ()).throw(OracleNotConfiguredError("sin Oracle"))),
    )
    resp = client.get(path, params=params, headers=TOKEN_COMUN)
    # Nunca 200 con items vacíos: una caída de Oracle es UNAVAILABLE, no NO_DATA.
    assert resp.status_code == 503
    assert resp.json()["error_code"] == "UNAVAILABLE"