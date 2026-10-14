# Estado de sesión — Punto de retorno (2026-09-28)

> **Para qué sirve este archivo:** resume exactamente dónde quedamos al cerrar esta sesión, para retomar enviando **este archivo** (y en su defecto `arquitectura.md` + `capacidades/consultar_ingresos_por_tipo_pago.md`). Contiene: estado alcanzado, evidencia verificada en vivo, comandos, entorno, pendientes y próximos pasos. Está escrito para que un asistente no tenga que "adivinar" el contexto.

---

## 1. Estado alcanzado

**Capability #1 `consultar_ingresos_por_tipo_pago` (Q1) IMPLEMENTADA y VERIFICADA contra Oracle QA real.**

- Servidor Python FastAPI + FastMCP en `enablement-layer/`, exponiendo REST y MCP sobre el mismo pool Oracle.
- Pool Oracle autentica contra el DSN QA (ambiente QA, usuario de lectura).
- La query Q1 corre idéntica al legacy (`dent.boleta` + `dent_ciclo.boleta`, 8 bloques / 7 `union all`).
- Encontré **datos de prueba en QA solo para `2026-09-16`: `EFE → CAJA - EFECTIVO 1000`, total 1000.00.** Otras fechas probadas devuelven `NO_DATA` (decisión de diseño: nunca "tabla vacía").
- **Los dos canales responden bien:** REST devuelve el JSON; MCP devuelve la misma carga con `isError: false` cuando hay datos y `isError: true` + `[NO_DATA]` cuando no.

Estado del proceso: **server detenido** (se levantó para la prueba y se apagó con `pkill -f "uvicorn app:app"`).

---

## 2. Dónde está el código

Proyecto: `/Users/fernandosalvo/Desktop/humbold/enablement-layer/` (venv en `.venv`, Python 3.12.6).

```
enablement-layer/
├── .env                  # real: ORACLE_* completados por el usuario (QA), 4 tokens de dev generados
├── .env.example          # plantilla versionable (sin secretos)
├── .gitignore            # ignora .env, .venv, __pycache__, logs
├── requirements.txt
├── README.md
├── app.py                # composition root: lifespan (pool + session manager MCP), middleware,
│                         #   mount /mcp, /health, handlers de error
├── config.py             # Settings pydantic-settings (lee .env)
├── database.py           # pool oracledb: create_pool/calentamiento, acquire/release, get_pool_stats
├── security.py           # BearerAuthMiddleware (ASGI puro), require_roles, CONTABILIDAD_ROLES,
│                         #   identity_from_mcp
├── observability.py      # structlog configurado
├── application/
│   ├── errors.py         # DomainError, ValidationError, NotFoundError, AuthorizationError,
│   │                     #   InfrastructureError + error_code
│   └── contabilidad/
│       ├── models.py     # contratos Pydantic (request/response, monto como str o Decimal por contrato)
│       ├── ports.py      # ContabilidadRepositoryPort (Protocol)
│       └── service.py    # ContabilidadService: orquesta repo, mapeo de etiquetas, orden canónico, total
├── infrastructure/oracle/
│   └── contabilidad_repository.py  # Q1_SQL (bind :fecha, dent+dent_ciclo, filtros por impresora,
│                                  #   ind_estado 'ACT', banda 00:00:00-23:59:59) + traducción de errores
├── adapters/
│   ├── rest/contabilidad.py   # router FastAPI /api/contabilidad/ingresos-por-tipo-pago
│   └── mcp/contabilidad.py    # FastMCP "control-contable" + tool consultar_ingresos_por_tipo_pago
└── tests/
    ├── conftest.py            # tokens de test por env antes de importar app
    ├── test_service.py        # mapeo, orden canónico, NO_DATA, INVALID_ARGUMENT
    ├── test_contracts.py      # 401/400/404/503 + health (usa fixture client scope=module)
    └── test_repository_sql.py # guardas de SQL: 8 bloques, 7 union all, bind único :fecha, filtros
```

---

## 3. Stack y versiones instaladas (exactas)

| Paquete | Versión | Nota |
| --- | --- | --- |
| Python | 3.12.6 | venv `.venv` |
| fastapi | 0.141.1 | `>=0.141` |
| uvicorn | 0.54.0 | `[standard]` |
| **mcp** | 1.30.0 | **pine `mcp<2` OBLIGATORIO** |
| **fastmcp** | 2.14.7 | **pine `fastmcp>=2.14,<3` OBLIGATORIO** (fastmcp 4.x usa mcp 2.x con API renombrada MCPServer) |
| **oracledb** | 26.0.1 | nombre del paquete PyPI es `oracledb`, NO `python-oracledb` |
| pydantic | 2.13.5 | |
| pydantic-settings | 2.15.0 | |
| structlog | 26.1.0 | |
| pytest | 9.1.1 | |
| httpx | 0.28.1 | (cliente para TestClient + cliente streamable-http) |

---

## 4. Decisiones confirmadas (▣ cerradas)

1. **Puerto `8090`** para REST + MCP (el `8000` es de Django/Django). Ver `arquitectura.md` §4.
2. **Bearer estático por rol** desde `.env`: `AUTH_TOKEN_CONTADOR`, `AUTH_TOKEN_ANALISTA_FINANCIERO`, `AUTH_TOKEN_GERENTE_FINANZAS`, `AUTH_TOKEN_AI_AGENT`. Enforcement point único (`BearerAuthMiddleware`) cubre `/api/*` y `/mcp`. Roles permitidos (default contables): `contador`, `analista_financiero`, `gerente_finanzas`, `ai_agent`.
3. **Pool python-oracledb**: `min=2 / max=5 / increment=1 / timeout=30` vía `.env`, calentado en startup. `dent_ciclo` asumido como esquema del mismo Oracle (1 solo pool) hasta Nivel 2.
4. **Oracle Instant Client (modo thick)** en local via `ORACLE_INSTANT_CLIENT_DIR=/Users/fernandosalvo/Downloads/instantclient_23_26` (existe, arm64). En Debian iría thin mode (sin cliente) — falta confirmar cadena de conexión.
5. **Toda config por `.env`** (pydantic-settings); el repo versiona `.env.example` nomás.
6. **Despliegue:** local con uvicorn + `.env` ahora; `systemd` + `.env.debian` después. Docker opción futura.

---

## 5. Detalles de implementación que NO repetir de cero

### 5.1 API de oracledb 26 (cambió vs versiones viejas)
- El pool se tipa `oracledb.ConnectionPool` (no existe `oracledb.Pool`).
- `create_pool(..., getmode=oracledb.PoolGetMode.WAIT, ...)`.
- Métricas disponibles: `pool.opened`, `pool.busy`, `pool.max`, `pool.min` (NO `checked_out`/`session_count`).
- `release()` devuelve la sesión al pool.

### 5.2 Montaje MCP dentro de FastAPI (fastmcp 2.14)
- `FastMCP("control-contable", streamable_http_path="/")` — si se deja el default `/mcp`, montado en `/mcp` queda `/mcp/mcp` → 404.
- Se monta con `app.mount(settings.MCP_PATH, _mcp_app)`.
- **Obligatorio correr el lifespan del sub-app MCP** dentro del lifespan de FastAPI, porque el session manager necesita un task group:
  ```python
  _mcp_app = mcp.streamable_http_app()
  async with _mcp_app.router.lifespan_context(_app):
      yield
  ```
  Sin esto: `RuntimeError: Task group is not initialized. Make sure to use run().`
- El session manager solo puede correr **una vez por instancia**: por eso los tests de contratos usan fixture `client` con `scope="module"` (un solo `with TestClient(app)`), no `with` por test.

### 5.3 Errores y contrato
| CLI | error_code | MCP |
| --- | --- | --- |
| `400` | `INVALID_ARGUMENT` | `isError: true` + `[INVALID_ARGUMENT] …` |
| `404` | `NO_DATA` | `isError: true` + `[NO_DATA] …` (mensaje: "Resultado válido, no es un fallo") |
| `403` | `FORBIDDEN` | `[FORBIDDEN] No autorizado.` (oculta regla) |
| `503` | `UNAVAILABLE` | `[UNAVAILABLE] No se pudo consultar la fuente de datos…` |
- FastMCP envuelve excepciones en `ToolError` → `isError` con texto legible (sin traceback): el adapter MCP relanza como `RuntimeError(f"[{exc.error_code}] {exc.message}")`.
- **`NO_DATA` ≠ UNAVAILABLE**: réplica/BD caída nunca debe verse como "tabla vacía/cero".

### 5.4 Cliente MCP para pruebas
- `from fastmcp import Client` NO importa (roto entre fastmcp 2.14 y mcp 1.30). Usar el cliente nativo:
  ```python
  from mcp.client.streamable_http import streamablehttp_client
  ```
  (`mcp.client.http` era el módulo viejo).
- Handshake: `streamablehttp_client(url, headers={"Authorization": "Bearer <tok>"})` → `ClientSession` → `await session.initialize()`, `session.list_tools()`, `session.call_tool(nombre, {"fecha": ...})`.

### 5.5 Peculiaridad de la shell (opencode)
- La shell persistente arranca en `~/Desktop/humbold/docs/refactorizacion`; usar rutas absolutas o `workdir` hacia `enablement-layer` (p. ej. nunca `curl` con path relativo al `.env` sin `workdir`).

---

## 6. Cómo arrancar / probar

```bash
cd /Users/fernandosalvo/Desktop/humbold/enablement-layer
source .venv/bin/activate

# 1) Levantar server
uvicorn app:app --host 127.0.0.1 --port 8090   # API_PORT se lee de .env igual

# 2) Salud
curl -s http://127.0.0.1:8090/health
# → {"status":"ok","pool":{"status":"ok","opened":2,"busy":0,"max":5,"min":2},"mcp":"/mcp"}

# 3) REST (token de .env)
curl -s -H "Authorization: Bearer $AUTH_TOKEN_CONTADOR" \
  "http://127.0.0.1:8090/api/contabilidad/ingresos-por-tipo-pago?fecha=2026-09-16"

# 4) Tests
pytest -q    # → 15 passed

# 5) Detener
pkill -f "uvicorn app:app"
```

Tokens de desarrollo generados (en `.env`, no versionados): `AUTH_TOKEN_CONTADOR=-ekgZWIJQf9cm_NhkC9ARSkYxQx…` y análogos. Rotan cambiando `.env` y reiniciando.

---

## 7. Verificaciones hechas en vivo (evidencia)

- `/health` con Oracle configurado: `pool.status=ok`, `opened=2`, `max=5` (el primer intento falló por `ORA-01005`/DPY-4001 porque el usuario había olvidado la password; tras completarla en `.env`, autenticó OK).
- REST barrido de fechas: `2026-09-25/28, 2025-09-26, 2026-09-23/24/21/18/17/15/14/11/10` → `404 NO_DATA`; **`2026-09-16` → `200`** con `{"fecha":"2026-09-16","items":[{"tipo_pago":"EFE","etiqueta":"CAJA - EFECTIVO","monto":"1000"}],"total":"1000.00"}` (respuesta ~27ms, primera query ~real).
- MCP: `list_tools` → `consultar_ingresos_por_tipo_pago` con annotations `readOnly=true, destructive=false, idempotent=true, openWorld=false`; `call_tool(2026-09-16)` → `isError=false` + JSON; `call_tool(2026-09-17)` → `isError=true` + `[NO_DATA]`.
- Pytest: **15 passed** (service, contracts, SQL guards).
- OpenAPI expone el path REST; `/mcp` responde (GET → 401 sin Bearer).

---

## 8. Pendientes / próximos pasos

1. **Test de paridad Nivel 0** (capability vs correo legacy) usando el seed QA de `2026-09-16`. Definir cuándo y con qué trazadora de fecha lo validamos; la fecha `2026-09-16` es la única con datos en QA hasta ahora.
2. **Capability #2 `consultar_resumen_deuda` (Q3)** — siguiente en la cola; crear `capacidades/consultar_resumen_deuda.md` (ficha igual que la Q1) y repetir Nivel 0 de verificación de la query contra `resumencontrolRICH.md` + `ResumenControl.java` antes de implementar.
3. **Verificación `dent_ciclo` (Nivel 2):** confirmar si es el mismo Oracle o réplica Postgres (hoy asumido: mismo Oracle).
4. **Despliegue Debian/systemd** cuando se decida (diseño en `arquitectura.md` §9). En Debian usar thin mode.
5. **Fechas de QA para QA-Q2..Q15:** mapear qué días tienen data sembrada para no bloquear las próximas capabilities.

> Nota: en la próxima reunión el dueño definió variar algunas actividades; este punto de retorno permite reanudar donde quedamos e repriorizar con el contexto intacto.

---

## 9. Referencias

- Estrategia: `000_MiEstrategiaV2.md` (1.424 líneas, 21 secciones).
- Arquitectura del servidor: `arquitectura.md` (decisones ▣ confirmadas).
- Ficha de la capability implementada: `capacidades/consultar_ingresos_por_tipo_pago.md`.
- Queries validadas: `resumencontrolRICH.md` (Q1–Q15) · fuente legacy `ResumenControl.java` (`setTablaIngresoPago` :132-189 en `~/Desktop/ino/assesstment/app/DentWeb12_Java21/src/cl/llm/batch/`).
- Encuentros/notas: `encuentros.md`.