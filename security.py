import json
import secrets

from fastapi import HTTPException, Request

from application.registry import get_contract

# Re-exportado por compatibilidad: la lista de roles ahora vive en el registry.
CONTABILIDAD_ROLES = get_contract("contabilidad.ingresos_por_tipo_pago").roles


class BearerAuthMiddleware:
    """Enforcement point único (ASGI): valida Bearer en /api/* y /mcp*.

    El middleware solo autentica (token → rol). La autorización por rol de la
    capability la aplica el router/dependency (REST) o el adapter (MCP).
    """

    def __init__(self, app, settings=None):
        self.app = app
        self.mcp_path = (getattr(settings, "MCP_PATH", None) or "/mcp").rstrip("/")
        self.token_roles = dict(getattr(settings, "token_roles", {}))

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path") or ""
        if not (path.startswith("/api/") or path.startswith(self.mcp_path + "/") or path == self.mcp_path):
            await self.app(scope, receive, send)
            return

        role = self._resolve(self._extract_token(scope))
        if role is None:
            await self._reject(send, 401, "UNAUTHORIZED", "Token inválido o ausente.")
            return

        state = scope.get("state") or {}
        state["identity"] = {"role": role}
        scope["state"] = state
        await self.app(scope, receive, send)

    @staticmethod
    def _extract_token(scope) -> str:
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode("utf-8", "ignore")
        if auth.startswith("Bearer "):
            return auth[len("Bearer "):].strip()
        return ""

    def _resolve(self, token: str) -> str | None:
        if not token:
            return None
        for known, role in self.token_roles.items():
            if known and secrets.compare_digest(known, token):
                return role
        return None

    @staticmethod
    async def _reject(send, status: int, error_code: str, message: str) -> None:
        body = json.dumps({"error_code": error_code, "message": message}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode()),
            ],
        })
        await send({"type": "http.response.body", "body": body})


def require_roles(*roles: str):
    """Dependency FastAPI: autoriza por rol antes de ejecutar la capability (R8)."""

    def dependency(request: Request) -> dict:
        identity = getattr(request.state, "identity", None)
        if not identity or identity.get("role") not in roles:
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        return identity

    return dependency


def require_contract(capability_id: str):
    """Dependency FastAPI que toma los roles del contrato, no de una lista local.

    Evita que la autorización de una capability se desincronice del registry.
    """
    contract = get_contract(capability_id)
    return require_roles(*contract.roles)


def authorize_contract(capability_id: str, identity: dict | None) -> None:
    """Equivalente MCP de :func:`require_contract`.

    ``identity`` es best-effort: si el middleware no pudo inyectarla, la tool no
    puede distinguir "anónimo" de "servidor local", así que solo rechaza cuando
    conoce la identidad y el rol no está autorizado.
    """
    contract = get_contract(capability_id)
    if identity is not None and identity.get("role") not in contract.roles:
        raise RuntimeError("[FORBIDDEN] No autorizado.")


def identity_from_mcp(ctx) -> dict | None:
    """Lee la identidad inyectada por el middleware dentro de una tool MCP (best-effort)."""
    try:
        req = getattr(ctx, "request", None)
        state = getattr(req, "state", None)
        identity = getattr(state, "identity", None)
        return identity if isinstance(identity, dict) and identity.get("role") else None
    except Exception:
        return None