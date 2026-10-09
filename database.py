import logging

import oracledb

from config import settings

logger = logging.getLogger(__name__)

_pool: oracledb.ConnectionPool | None = None


class OracleNotConfiguredError(RuntimeError):
    """Oracle no está configurado (.env)."""


def _init_oracle_client() -> None:
    lib_dir = settings.ORACLE_INSTANT_CLIENT_DIR
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)


def create_pool() -> oracledb.ConnectionPool | None:
    """Crea el pool una sola vez y calienta las sesiones mínimas.

    Si Oracle no está configurado en .env, no falla al arrancar: la app bootea
    para /health y el Nivel 3 de pruebas, y el repository devuelve UNAVAILABLE
    cuando se intenta consultar.
    """
    global _pool
    if not settings.oracle_configured:
        logger.warning("ORACLE_DSN/ORACLE_USER vacíos en .env: pool NO creado. Queries → UNAVAILABLE.")
        return None

    _init_oracle_client()

    _pool = oracledb.create_pool(
        user=settings.ORACLE_USER,
        password=settings.ORACLE_PASSWORD,
        dsn=settings.ORACLE_DSN,
        min=settings.DB_POOL_MIN,
        max=settings.DB_POOL_MAX,
        increment=settings.DB_POOL_INCREMENT,
        getmode=oracledb.PoolGetMode.WAIT,
        timeout=settings.DB_POOL_TIMEOUT,
    )
    _warm_pool()
    logger.info("Pool Oracle creado: min=%s max=%s dsn=%s",
                settings.DB_POOL_MIN, settings.DB_POOL_MAX, settings.ORACLE_DSN)
    return _pool


def _warm_pool() -> None:
    if _pool is None:
        return
    for _ in range(settings.DB_POOL_MIN):
        conn = _pool.acquire()
        try:
            with conn.cursor() as cur:
                cur.execute("select 1 from dual")
        finally:
            _pool.release(conn)


def get_pool() -> oracledb.ConnectionPool:
    if _pool is None:
        if not settings.oracle_configured:
            raise OracleNotConfiguredError("Oracle no configurado en .env")
        raise RuntimeError("Pool Oracle no inicializado (¿lifespan no corrió?)")
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        logger.info("Pool Oracle cerrado.")
        _pool = None


def pool_stats() -> dict:
    if _pool is None:
        return {"status": "not_configured"}
    return {
        "status": "ok",
        "opened": _pool.opened,
        "busy": _pool.busy,
        "max": _pool.max,
        "min": _pool.min,
    }