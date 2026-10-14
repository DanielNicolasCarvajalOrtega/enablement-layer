# Estado de sesión B — Punto de retorno (2026-10-02, tarde)

> **Para qué sirve este archivo:** complementa a `estado_de_sesion_2026-10-02.md` (sesión A, que cerró el bloque Control Contable). Esta sesión B se dedicó a **conectar los clientes MCP** (opencode y Claude Desktop), **exponer el bloque a la gerencia** (demo `analsismcp.html`) y **dejar la hoja de ruta** para las próximas 5 capabilities. Para retomar el lunes, pásame **este archivo**; si falta contexto, suma `arquitectura.md` §11 y `capacidades/CATALOGO.md`.

---

## 1. Resumen ejecutivo de la sesión B

1. **opencode quedó conectado** al MCP `control-contable` (macOS). Config final con token **literal** + `oauth: false`.
2. **Claude Desktop** quedó documentado paso a paso para **macOS** y **Windows** (con sus dos variantes: servidor remoto nativo y puente `mcp-remote`).
3. Se descubrió y resolvió que **el servidor llevaba corriendo desde el Oct 1**, antes de implementar las 6 capabilities → exponía **1 tool**. Tras reiniciarlo, expone las **6**.
4. Se respondieron **7 consultas reales** vía MCP (control contable) y se validó que la capa responde de punta a punta.
5. Se generó **`analsismcp.html`**: SPA autocontenido con KPIs, gráficos y grillas (ordenar/buscar/paginar) a partir de esas 7 consultas. Aprobado por el usuario ("así está bien", "estoy maravillado").
6. Se acordó la **estrategia scaffold** para las próximas **5 capabilities** (§9 de este doc).

---

## 2. Configuración de clientes MCP (resultado final)

> Detalle completo y reproducible en **`arquitectura.md` §11** ("Configurando MCP en cliente opencode y Claude").

### 2.1 opencode en macOS (ESTE equipo) — funcionando

- Archivo: `~/.config/opencode/opencode.json` (global), entrada dentro de `"mcp"`. **`chmod 600`** aplicado.
- Entrada final:

```json
"control-contable": {
  "type": "remote",
  "enabled": true,
  "url": "http://127.0.0.1:8090/mcp/",
  "oauth": false,
  "headers": {
    "Authorization": "Bearer <AUTH_TOKEN_AI_AGENT literal, leído del .env>"
  }
}
```

- **Decisiones y hallazgos:**
  - `oauth` **debe** ser `false`: ante un `401`, opencode intenta OAuth por defecto y reporta *"needs auth"* / *"SSE error: Non-200 status code (401)"*. Nuestro server usa Bearer estático.
  - **Token literal** en la config (no `{env:...}`). opencode **no** lee el `.env` del proyecto, y `{file:...}` inyecta el archivo **completo** (no una clave). Con `{env:AUTH_TOKEN_AI_AGENT}` el header quedaba `Bearer ` vacío si opencode no se lanzaba desde una shell con la variable → `401`.
  - **URL con slash final** (`/mcp/`): `POST /mcp` responde `307`; `/mcp/` responde directo.
  - Se dejó un `export AUTH_TOKEN_AI_AGENT=...` en `~/.zshrc` (lee del `.env` con `sed`, sin `source`). **Ya no es necesario** para opencode; se puede eliminar para no tener el token en cada shell (pendiente menor).
  - opencode versión: **1.18.34**. Verificación: `opencode mcp list` → las 4 MCP `connected`.

### 2.2 Claude Desktop (macOS y Windows) — documentado, no instalado

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- Dos variantes por sistema:
  - **Opción A — remoto nativo:** `{ "type": "http", "url": "http://127.0.0.1:8090/mcp/", "headers": { "Authorization": "Bearer <token>" } }`.
  - **Opción B — puente `mcp-remote`** (Node 18+): `npx -y mcp-remote http://127.0.0.1:8090/mcp/ --allow-http --header "Authorization: Bearer <token>"`. En **Windows** hay bug de espacios en `args` → usar `env` + `--header "Authorization:${AUTH_HEADER}"` (sin espacios alrededor de `:`) o `--header-file`.
- **Claude Desktop no sigue redirects** → obligatorio `/mcp/` con slash.
- **Claude Desktop no expande `${VAR}`** en el config → token literal (o `mcp-remote` con `env`).
- **Caveat de red:** el server escucha en `127.0.0.1`. Para consumirlo desde **otra** máquina (Windows) hay que, o correr el server ahí, o en la Mac poner `API_HOST=0.0.0.0` + abrir firewall + usar `http://<IP_Mac>:8090/mcp/` (token en texto plano → solo LAN/VPN).

---

## 3. Estado del servidor y de las 6 tools (verificado en vivo)

- **Hallazgo:** el proceso `uvicorn` activo se había iniciado **Oct 1 17:28**, pero el código se modificó **Oct 2 12:16–12:18** (6 capabilities). Resultado: el server viejo exponía **solo 1 tool** (`consultar_ingresos_por_tipo_pago`).
- **Acción:** se reinició. Ahora corre en background con `nohup`, log en `enablement-layer/.server.log`.
  - Comando: `.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8090`
  - Última PID observada: **30189** (puede cambiar; ver §8).
- **Verificación `list_tools` (6/6):**
  1. `consultar_ingresos_por_tipo_pago` (Q1)
  2. `consultar_resumen_deuda` (Q3)
  3. `consultar_ingresos_por_tipo_tarjeta` (Q10)
  4. `consultar_ingresos_por_tipo_prevision` (Q11)
  5. `consultar_boletas_emitidas_por_usuario` (Q8)
  6. `consultar_boletas_anuladas_por_usuario` (Q9)
- **Regla de oro:** después de tocar código, **reiniciar el server**; opencode/Claude cachean la lista de tools al conectar.

---

## 4. Las 7 consultas respondidas en vivo (evidencia)

| # | Pregunta | Tool | Fecha | Resultado |
| --- | --- | --- | --- | --- |
| 1 | Ingresos por tipo de pago | Q1 | 2026-09-29 | TRJ/CAJA-TARJETA `61576` · TOTEM `1814000` → **total `1875576`** |
| 2 | Deuda (4 meses) | Q3 | 2017-12-15 | `12-2017: 900601075` · `11-2017: 896653783` · `10-2017: 891873367` · `09-2017: 896509697` |
| 3 | Ingresos por tipo de tarjeta | Q10 | 2025-05-12 | CAJA 1086/`45783100` · TOTEM 11/`298500` · WEBPAY 60/`2831500` → **1157/`48913100`** |
| 4 | Ingresos por tipo de previsión | Q11 | 2025-05-12 | **34 filas, 1305/`54151100`** |
| 5 | Ingresos por tipo de pago | Q1 | 2026-09-25 | TRJ/CAJA-TARJETA `420741` · TOTEM `629500` → **total `1050241`** |
| 6 | Boletas emitidas por usuario | Q8 | 2025-05-12 | **23 usuarios, 1305/`54151100`** |
| 7 | Boletas anuladas por usuario | Q9 | 2025-05-12 | **2 usuarios, 45/`4428000`** |

**Valores derivados usados en la demo:** ticket promedio tarjeta `$42.276`; tasa de anulación (45/(1305+45)) `3,33%`; tarjeta/total boletas `90,3%`; variación 25-sep → 29-sep `+78,6%`.

> Nota Q1 (28/29-sep-2026): solo aparecen `TRJ` y `TOTEM`; no hay efectivo/cheque/webpay/caja vecina con movimiento esos días.

---

## 5. Entregable: `analsismcp.html`

- **Ruta:** `enablement-layer/analsismcp.html` (raíz del proyecto; ~36 KB).
- **Tipo:** SPA de una sola hoja, **autocontenida** (sin CDN, sin librerías): HTML5 + CSS + **JavaScript vanilla** + gráficos en **Canvas** dibujados a mano.
- **Contenido:**
  - **10 KPIs** calculados en JS (recaudación 29-sep vs 25-sep con delta, deuda promedio, tarjeta, ticket, emitidas, anuladas + tasa, share tarjeta, previsión líder, canal líder).
  - **6 gráficos** (doughnut canal, doughnut tipo de tarjeta, barras deuda mensual, barras horizontales top-previsión y top-usuario, barras agrupadas pagos 2 días).
  - **6 grillas de alto impacto** (Q1, Q3, Q10, Q11, Q8, Q9) con **búsqueda**, **orden por columna** y **paginación**, más data-bars y badges.
  - Footer con advertencias de interpretación (fechas mezcladas, deuda = promedio diario, filtros exactos, PII).
- **Validación hecha:** `node --check` OK (sintaxis JS), `<script>`/`<div>` balanceados.
- **Origen de datos:** literales embebidos (salida de las 7 consultas). **No** consume MCP en vivo aún.
- **Próximo paso natural (postergado):** que la página haga `fetch` al MCP en vivo en vez de datos embebidos. Requiere resolver auth/CORS en el navegador (ver §9.5).

---

## 6. Decisiones tomadas en esta sesión

1. Token **literal** en la config de opencode (se abandona `{env:...}` y `{file:...}` para este caso).
2. **`oauth: false`** obligatorio para el MCP Bearer estático.
3. URL canónica **con slash final** (`/mcp/`).
4. Se documenta la configuración de clientes en **`arquitectura.md` §11** (no en un archivo aparte).
5. Prioridad del lunes: **terminar las 5 capabilities restantes → tests → producción**, usando el scaffold de §9. El HTML queda con datos embebidos por ahora.

---

## 7. Archivos tocados / creados en la sesión B

| Archivo | Cambio |
| --- | --- |
| `~/.config/opencode/opencode.json` | Entrada `mcp.control-contable` (remote, `oauth:false`, token literal, `/mcp/`). `chmod 600`. Varios respaldos `.bak-<timestamp>` en la misma carpeta. |
| `~/.zshrc` | `export AUTH_TOKEN_AI_AGENT` leyendo el `.env` (ya no requerido por opencode; opcional eliminar). |
| `docs/refactorizacion/arquitectura.md` | Nueva **§11** "Configurando MCP en cliente opencode y Claude" (+ renumerada §12 Referencias). |
| `enablement-layer/analsismcp.html` | **NUEVO**: SPA autocontenido (demo para gerencia). |
| `enablement-layer/.server.log` | Log del server reiniciado por `nohup`. |
| `docs/refactorizacion/estado_de_sesion_2026-10-02-B.md` | **Este archivo.** |

---

## 8. Cómo arrancar / verificar (comandos)

```bash
cd /Users/fernandosalvo/Desktop/humbold/enablement-layer
source .venv/bin/activate

# (Re)levantar server en background con log
pkill -f "uvicorn app:app" 2>/dev/null
nohup .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8090 > .server.log 2>&1 &

# Salud (sin auth)
curl -s http://127.0.0.1:8090/health

# Listar las 6 tools vía MCP (necesita el token del .env)
opencode mcp list        # si se corre opencode: debe salir "control-contable connected"

# Suite de tests (196 tests; usa Oracle real si hay DSN)
pytest -q
```

**Diagnóstico de conexión:** `POST /mcp/` sin token → `401`; con token → pasa auth (un `400` de body vacío es señal de que la auth está OK). `POST /mcp` (sin slash) → `307`.

---

## 9. Scaffold de las 5 capabilities (estrategia / plantilla)

> **Entrega vigente:** [`capacidades/PLANTILLA_CAPACIDAD.md`](./capacidades/PLANTILLA_CAPACIDAD.md)
> + esqueleto copiable en [`capacidades/_plantilla/`](./capacidades/_plantilla/). Esta
> sección queda como registro histórico de cómo se construyó el bloque Control
> Contable; los conteos, nombres de test y hallazgos de aquí abajo no se mantienen.
>
> **Lunes: primero confírmame la lista de las 5** (nombre funcional, Q# del legacy y de `resumencontrolRICH.md`, método Java de origen, si devuelve PII). Con eso arrancamos en serie con el molde de abajo.

### 9.0 Principio

Cada capability es una **instancia del mismo molde**: *contrato → SQL → service → adapters → tests → ficha*. Los adapters no tienen lógica; todo el contrato sale del **registry**. El objetivo es que agregar la capability N+1 no toque los adapters existentes (solo agregar).

### 9.1 Receta (10 pasos)

> Los pasos 2 a 7 se repiten **por dominio**. `contabilidad/` fue el primero; `pacientes/` (censo por ciudad, 2026-10-05) confirmó que el molde sirve igual con dos diferencias: sin `fecha` y con `roles` propios. Abajo la columna "contabilidad" es la ruta de siempre.

1. **Registry** — agregar entrada en `CAPABILITIES` (`application/registry.py`) con todos los campos de §9.2. `_validate()` falla al importar si algo falta → **fail-fast**.
2. **Modelos** — `application/<dominio>/models.py`: `...Item` y `...Output` (Pydantic v2).
3. **Puerto** — `application/<dominio>/ports.py`: método nuevo en `<Dominio>Port`.
4. **Repositorio (SQL)** — `infrastructure/oracle/<dominio>_repository.py`: `<Qxx>_SQL` + método. Reglas: **bind parameters** (`:fecha`), **owner explícito** (`DENT.*`, `DENT_CICLO.*`), **nunca `USURUT`**, agrupar por columna real (no alias del `select`, por `ORA-00904`).
5. **Service** — `application/<dominio>/service.py`: orquesta el repo, mapea a modelos, aplica orden canónico y calcula totales en la capa (no replicar el bug `resp.size()` de Java).
6. **Adapter REST** — `adapters/rest/<dominio>.py`: router propio (`prefix="/api/<dominio>"`) + endpoint con `Depends(require_contract("<id>"))` y `response_model=...`.
7. **Adapter MCP** — `adapters/mcp/<dominio>.py`: tool con `@mcp.tool(**_tool(<ID>, "<título>"))`; `annotations`/`description` **derivadas del registry**. La instancia `FastMCP` se importa de `adapters/mcp/server.py`, no se crea por dominio.
8. **Tests** — §9.4.
9. **Ficha** — `docs/refactorizacion/capacidades/<nombre>.md` con las **mismas 17 secciones** que la ficha de Q1 (§9.5) + actualizar `capacidades/CATALOGO.md`.
10. **Cierre** — `pytest -q` verde, paridad viva, **reiniciar server** y `list_tools` para confirmar que aparece.

**Al agregar un dominio nuevo** (no una capability a uno existente) además de lo anterior:

- Instanciar repo + service en `composition.py` y montar el router en `app.py`.
- Importar el módulo MCP **por efecto** en `app.py` (`from adapters.mcp import <dominio>  # noqa: F401`): las tools se registran al importar el módulo.
- Declarar `<DOMINIO>_ROLES` en el registry si los roles no coinciden con los contables.
- Añadir el test de paridad en `test_contracts.py` parametrizando el repo que se cae, para no dejar un endpoint sin cobertura de `UNAVAILABLE`.

### 9.2 Plantilla de contrato (`CapabilityContract`)

Campos exactos (dataclass en `application/registry.py`):

```python
"<dominio>.<nombre_snake>": CapabilityContract(
    id="<dominio>.<nombre_snake>",
    name="consultar_<nombre_snake>",          # nombre del tool MCP, SIN versión (R10)
    title="<título corto legible>",
    mode=OperationMode.READ,                   # READ/ANALYZE/ACT; deriva las annotations
    description="<qué hace y CUÁNDO usarla; fecha obligatoria (YYYY-MM-DD). Solo lectura.>",
    usage_notes="<CUÁNDO NO usarla; remite a las capabilities vecinas; advertencias>",
    rest_method="GET",
    rest_path="/api/contabilidad/<kebab-case>",
    roles=CONTABILIDAD_ROLES,
    oracle_sql_id="Q<n>",
    legacy_method="ResumenControl.<metodo>",
    legacy_lines="<a-b>",
    data_profile="financial" | "financial_pii" | ...,
    examples=({"fecha": "<YYYY-MM-DD>"},),
)
```

**Invariantes que valida `_validate()`** (no las repitas a mano): `id` == key; `name` sin sufijo `_vN`; `description`, `usage_notes` y `examples` no vacíos; `name` y `(rest_method, rest_path)` únicos; roles ⊆ `KNOWN_ROLES`; roles no vacíos. Y un test contrasta `KNOWN_ROLES` contra los tokens reales del `.env`.

### 9.3 Checklist de archivos a tocar

Capability dentro de un dominio existente:

- [ ] `application/registry.py` (entrada)
- [ ] `application/<dominio>/models.py` (Item/Output)
- [ ] `application/<dominio>/ports.py` (puerto)
- [ ] `infrastructure/oracle/<dominio>_repository.py` (SQL + método)
- [ ] `application/<dominio>/service.py` (método)
- [ ] `adapters/rest/<dominio>.py` (endpoint)
- [ ] `adapters/mcp/<dominio>.py` (tool)
- [ ] `tests/test_registry.py`, `test_contracts.py`, `test_repository_sql.py`, `test_service.py`, `test_paridad_oracle.py`
- [ ] `docs/refactorizacion/capacidades/<nombre>.md` + `CATALOGO.md`
- [ ] (si es de cara a gerencia) `analsismcp.html`

Dominio nuevo (todo lo anterior, menos nada, **más**):

- [ ] `adapters/mcp/server.py` — nada que cambiar si ya existe (instancia compartida)
- [ ] `composition.py` — repo + service instanciados
- [ ] `app.py` — `include_router` + import MCP por efecto
- [ ] `tests/test_service_<dominio>.py` (suite propia, si el dominio no tiene una)

### 9.4 Tests mínimos por capability

| Suite | Qué agrega |
| --- | --- |
| `test_registry.py` | contrato presente, válido, sin fuga de internals (`NUM_DOCTO`, `id_impresora`, SQL), nombre/ruta únicos |
| `test_contracts.py` | validación Pydantic de entrada/salida; campos obligatorios; casos `NO_DATA` |
| `test_repository_sql.py` | usa bind, **owner explícito**, **no** selecciona `USURUT`, no concatena |
| `test_service.py` | mapeo, orden canónico, cálculo de totales, normalización |
| `test_paridad_oracle.py` | valores reales contra Oracle para **una fecha con datos** (Nivel 0, V2 §12) |

**Variante sin golden file.** Un censo (no un corte del día) cambia con cada registro nuevo, así que fijar números lo rompe sin que nadie haya tocado el código. En ese caso la paridad se verifica por **comparación**: el service contra el mismo SQL corrido a mano en la BD, más invariantes (orden, suma de filas, cobertura). Ver #7 en `test_paridad_oracle.py`.

Regla práctica: el total nuevo de la suite sube al número que corresponda. Referencia actual: **240** con 7 capabilities (196 del bloque Control Contable + 43 del censo por ciudad + 1 de mensajes de error). Una capability con `fecha` suma ≈ +20–35; #7, sin parámetros y con paridad por comparación en vez de golden file, sumó 43.

### 9.5 Ficha (17 secciones) — esqueleto

Usar como plantilla la ficha de Q1 (`capacidades/consultar_ingresos_por_tipo_pago.md`). Esqueleto:

1. Identidad (id, tool, versión) · 2. Objetivo · 3. Contrato de entrada · 4. Contrato de salida (shape) · 5. Fuente legacy (método + líneas) · 6. SQL (Q#) · 7. Semántica/replicación · 8. Casos límite y divergencias conscientes · 9. Ejemplos (fechas reales) · 10. Roles y seguridad · 11. PII / minimización · 12. Errores (`NOT_FOUND`, `NO_DATA`, `UNAVAILABLE`, `INVALID_ARGUMENT`) · 13. Paridad verificada (valores) · 14. Rendimiento · 15. Observabilidad · 16. Tests que la cubren · 17. Referencias.

> Al cerrar cada capability, actualizar la fila correspondiente en `capacidades/CATALOGO.md` y, si aplica, `arquitectura.md` §10.

### 9.6 Definition of Done

- [ ] `pytest -q` verde (base actual **240**).
- [ ] Paridad viva contra Oracle para la fecha elegida, o paridad por comparación si el dato es un censo cambiante.
- [ ] Ficha de 17 secciones + `CATALOGO.md` actualizados.
- [ ] Tool visible en `opencode mcp list` / `list_tools` (server **reiniciado**).
- [ ] Si publica datos sensibles: nota de PII en la ficha y en la descripción MCP.
- [ ] `arquitectura.md` sin pendientes nuevos en §10.1.

### 9.7 Tabla de seguimiento (completar el lunes)

| # | Capability | Q# | Origen legacy | PII | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | `consultar_pacientes_por_ciudad_chile` | `ENC.PACIENTES_POR_CIUDAD` | `docs/go/encuentros.md` (no el JSP) | no (agregado) | ✅ 2026-10-05 |
| 2 | _(por confirmar)_ | | | | pendiente |
| 3 | _(por confirmar)_ | | | | pendiente |
| 4 | _(por confirmar)_ | | | | pendiente |
| 5 | _(por confirmar)_ | | | | pendiente |

> #1 ya no está pendiente: se implementó como el **segundo dominio** de la capa, para validar que el molde de §9.1 sirve fuera de Control Contable. Resultado: sin `fecha`, con schema MCP vacío y con roles propios (`contador` excluido).

### 9.8 Gotchas ya conocidos (no repetir)

- Oracle **no** acepta alias del `select` en el `group by` (`ORA-00904`): agrupar por la columna real.
- El **filtro exacto vs `trunc`** cambia el resultado: respetar la semántica legacy por capability (Q9/Q10-CAJA exactos; Q8/Q11 de rango).
- `create_pool()` no traduce `ORA-12154` de arranque (solo fallos de consulta → `503`).
- **No** instalar el paquete standalone `fastmcp`; el server usa `mcp.server.fastmcp` (pin `mcp<2`).
- `FastMCP(..., streamable_http_path="/")` + lifespan del sub-app dentro del de FastAPI + fixture `client` **session-scoped**.
- Después de cambiar código, **reiniciar el server** o los clientes MCP ven la lista vieja de tools.
- **`os.environ.setdefault` en `conftest.py` no alcanza para los tokens.** Si el shell tiene exportado un `AUTH_TOKEN_*` real, el `setdefault` no sobreescribe y la suite queda autenticada con el token de producción: el test de `ai_agent` pasaba solo porque miraba `!= 403` y un 401 lo cumplía igual. Asignar (`os.environ[X] = ...`) sí. La suite debe ser hermética.
- **Un test que solo chequea `!= 403` es verde con un 401.** Para probar autorización hay que afirmar el código exacto, o afirmar las dos cosas (`!= 401` y `!= 403`).

---

## 10. Hoja de ruta (después de las 5 capabilities)

1. **Regenerar la suite de tests** para el bloque ampliado y dejar todo verde.
2. **Producción:** empaquetado/despliegue Debian (V2 §11; `arquitectura.md` §9), variables por entorno, rotación de tokens.
3. **SDD (Spec-Driven Development) con agentes:** orquestación, diseño, implementación y review. El **registry + contratos + paridad** son el sustrato natural de "spec verificable".
4. **Evangelización a TI:** audiencia mitad digital / mitad waterfall. Los artefactos que venden el método: contrato publicado, paridad verificada contra Oracle, suite de tests, ficha por capability.
5. **Nice-to-have:** que `analsismcp.html` consuma MCP en vivo (resolver auth/CORS del navegador) y `tools/paridad.py` (CLI de paridad, hoy solo en tests).

---

## 11. Cómo retomar el lunes

1. Pásame **este archivo** (y `arquitectura.md` §11 si quieres repasar la config de clientes).
2. Dime **cuáles son las 5 capabilities** + su Q# y método legacy → llenamos la tabla §9.7.
3. Confirmamos si arrancamos por la más simple para validar el molde end-to-end, y luego en serie.
4. Recordatorio de arranque: `pytest -q` (base **240**, 7 capabilities) y `nohup .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8090 > .server.log 2>&1 &`.

---

## 12. Referencias

- Sesión A (bloque Control Contable completo, 6 capabilities, 196 tests): `estado_de_sesion_2026-10-02.md`.
- Estrategia autoritativa: `000_MiEstrategiaV2.md`.
- Catálogo de las 7 capabilities: `capacidades/CATALOGO.md`.
- Arquitectura del server + **§11 config de clientes**: `arquitectura.md`.
- Fichas: `capacidades/consultar_ingresos_por_tipo_pago.md` · `consultar_resumen_deuda.md` · `consultar_ingresos_por_tipo_tarjeta.md` · `consultar_ingresos_por_tipo_prevision.md` · `consultar_boletas_emitidas_por_usuario.md` · `consultar_boletas_anuladas_por_usuario.md` · `consultar_pacientes_por_ciudad_chile.md`.
- Código: `enablement-layer/` (`application/registry.py`, `application/contabilidad/*`, `application/pacientes/*`, `infrastructure/oracle/*_repository.py`, `adapters/rest/*`, `adapters/mcp/{server,contabilidad,pacientes}.py`, `tests/*`).
- Demo: `enablement-layer/analsismcp.html` (hoy solo cubre el bloque Control Contable).
- Fuente legacy: `~/Desktop/ino/assesstment/app/DentWeb12_Java21/src/cl/llm/batch/ResumenControl.java` y `.../dent/ConsultaControl.java`.
