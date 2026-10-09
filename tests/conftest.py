import os

import pytest
from fastapi.testclient import TestClient

# Asignación y no setdefault: si el shell del desarrollador tiene exportado un
# AUTH_TOKEN_* real (es lo habitual para probar contra el server corriendo), un
# setdefault no sobreescribe nada y la suite queda autenticada con el token real.
# Los tests deben ser herméticos: o fallan por el código, o por el entorno local.
os.environ["AUTH_TOKEN_CONTADOR"] = "tok-contador-test"
os.environ["AUTH_TOKEN_ANALISTA_FINANCIERO"] = "tok-analista-test"
os.environ["AUTH_TOKEN_GERENTE_FINANZAS"] = "tok-gerente-test"
os.environ["AUTH_TOKEN_AI_AGENT"] = "tok-ai-test"
os.environ.setdefault("API_PORT", "8090")


@pytest.fixture(scope="session")
def client():
    """TestClient único para toda la sesión.

    El app monta el streamable-http de MCP, cuyo session manager solo admite un
    lifespan por proceso. Un fixture por módulo lo dejaría como
    'StreamableHTTPSessionManager .run() can only be called once'.
    """
    from app import app

    with TestClient(app) as c:
        yield c