# Estado de sesión — Punto de retorno (2026-10-02)

> **Para qué sirve este archivo:** resume exactamente dónde quedamos al cerrar esta sesión, para retomar enviando **este archivo** (y en su defecto `arquitectura.md` + `capacidades/CATALOGO.md`). Contiene: estado alcanzado, evidencia verificada en vivo, comandos, entorno, pendientes y próximos pasos. Está escrito para que un asistente no tenga que "adivinar" el contexto.

---

## 1. Estado alcanzado

**Bloque Control Contable COMPLETO: las 6 capabilities READ implementadas y verificadas contra Oracle QA real.**

| # | Capability | SQL | Estado |
| --- | --- | --- | --- |
| 1 | `consultar_ingresos_por_tipo_pago` | Q1 | ✅ implementada (sesión previa) |
| 2 | `consultar_resumen_deuda` | Q3 | ✅ implementada + paridad viva |
| 3 | `consultar_ingresos_por_tipo_tarjeta` | Q10 | ✅ implementada + paridad viva |
| 4 | `consultar_ingresos_por_tipo_prevision` | Q11 | ✅ implementada + paridad viva |
| 5 | `consultar_boletas_emitidas_por_usuario` | Q8 | ✅ implementada + paridad viva |
| 6 | `consultar_boletas_anuladas_por_usuario` | Q9 | ✅ implementada + paridad viva |

- **Capability Registry** (`application/registry.py`) como fuente única de contratos, roles, paths, descripciones y annotations MCP.
- **Composition root** (`composition.py`): REST y MCP comparten una **misma instancia** de `ContabilidadRepository` y `ContabilidadService`.
- **DOCUMENTACIÓN COMPLETA:** 6 fichas de 17 secciones + `capacidades/CATALOGO.md` + `arquitectura.md` actualizado + esta bitácora.
- **Suite de tests: 196 passed in ~2.7s**.
- **Paridad numérica Nivel 0** contra Oracle QA para Q3, Q10, Q11, Q8 y Q9 (20 tests).

Estado del proceso: **server detenido** durante el trabajo; toda la verificación se hizo vía la suite de pruebas (que abre el pool Oracle real).

---

## 2. Dónde está el código

Proyecto: `/Users/fernandosalvo/Desktop/humbold/enablement-layer/` (venv en `.venv`, Python 3.12.6).

```
enablement-layer/
├── .env                  # real: ORACLE_* + 4 tokens de dev (no versionado)
├── .env.example
├── app.py                # FastAPI: lifespan (pool + session manager MCP), middleware,
│                         #   mount /mcp, /health, handlers de error
├── config.py             # Settings pydantic-settings (lee .env)
├── database.py           # pool oracledb: create_pool/calentamiento, acquire/release, get_pool_stats
├── composition.py        # ★ NUEVO: composition root; instancia única de repo + service
├── security.py           # BearerAuthMiddleware, require_roles, require_contract,
│                         #   authorize_contract, identity_from_mcp; CONTABILIDAD_ROLES ← registry
├── observability.py      # structlog configurado
├── application/
│   ├── errors.py         # DomainError + error_code
│   ├── registry.py       # ★ NUEVO: CapabilityContract, OperationMode, CAPABILITIES (6),
│   │                     #   get_contract, all_contracts, contracts_by_name, _validate
│   └── contabilidad/
│       ├── models.py     # contratos Pydantic de las 6 capabilities
│       ├── ports.py      # ContabilidadPort (Protocol) + rows
│       └── service.py    # ContabilidadService: orquesta repo, mapeos, orden canónico, totales
├── infrastructure/oracle/
│   └── contabilidad_repository.py  # Q1, Q3, Q10×3, Q11, Q8, Q9 (bind :fecha, owner explícito)
├── adapters/
│   ├── rest/contabilidad.py    # 6 endpoints registry-driven
│   └── mcp/contabilidad.py     # 6 tools registry-driven, annotations derivadas
└── tests/
    ├── conftest.py             # tokens de test + fixture client session-scoped
    ├── test_registry.py        # 51
    ├── test_service.py         # 34
    ├── test_repository_sql.py  # 54
    ├── test_contracts.py       # 37
    └── test_paridad_oracle.py  # 20
```

> Los `test_*.py` sueltos en la raíz del proyecto (`test_mcp.py`, `test_ollama_*.py`) son scripts de exploración de la sesión anterior; **no** los recoge `pytest` del directorio `tests/` y no forman parte de la suite.

---

## 3. Stack y versiones instaladas (exactas)

| Paquete | Versión | Nota |
| --- | --- | --- |
| Python | 3.12.6 | venv `.venv` |
| fastapi | 0.141.1 | |
| uvicorn | 0.54.0 | `[standard]` |
| **mcp** | 1.30.0 | **pine `mcp<2` OBLIGATORIO** |
| **fastmcp** | 2.14.7 | se usa `mcp.server.fastmcp` (incluido); el paquete standalone `fastmcp` >2 no se usa |
| **oracledb** | 26.0.1 | nombre PyPI `oracledb` |
| pydantic | 2.13.5 | |
| pydantic-settings | 2.15.0 | |
| structlog | 26.1.0 | |
| pytest | 9.1.1 | |
| httpx | 0.28.1 | |

---

## 4. Decisiones confirmadas (▣ cerradas)

1. **Puerto `8090`** para REST + MCP. Ver `arquitectura.md` §4.
2. **Bearer estático por rol** desde `.env`; enforcement único (`BearerAuthMiddleware`) cubre `/api/*` y `/mcp`. Roles del bloque: `contador`, `analista_financiero`, `gerente_finanzas`, `ai_agent` (derivados del registry).
3. **Pool python-oracledb**: `min=2 / max=5 / increment=1 / timeout=30`.
4. **`dent_ciclo` verificado (2026-10-02):** `test.ino.cl` resuelve `192.168.0.25`, puerto `1521` abierto, DB `XE`. `DENT_CICLO.boleta` existe en el **mismo motor Oracle** (1 pool). La tabla tiene **0 filas**; el `union all` se conserva por fidelidad legacy.
5. **Capability Registry + composition root** implementados. REST y MCP comparten instancia (verificado por test).
6. **`USURUT` nunca se selecciona** en ninguna query del bloque.
7. **Divergencias conscientes y declaradas** vs el legacy: uso de bind parameters (no concatenación), `Decimal` en vez de `Long.parseLong`, y cálculo de totales en el service (no el bug de `resp.size()`). Todas documentadas por capability.

---

## 5. Detalles de implementación que NO repetir de cero

### 5.1 Entorno Oracle (resuelto en esta sesión)

- `test.ino.cl` → `192.168.0.25`, `:1521` abierto, DB `XE`.
- **No hay `tnsnames.ora`** para el alias, pero el DSN actual conecta sin problema (python-oracledb armó la ruta). No tocar la config de conexión: funciona.
- Datos medidos: `DENT.boleta` = **171.922 filas**; `DENT_CICLO.boleta` = **0 filas**; `DENT.bat_deuda` = 1.820 filas, **termina en 2023-03-30**.
- `FEC_BOL` en `DENT.boleta`: 163.369 filas a medianoche, 8.553 con hora, resto con hora real. Esto hace material la diferencia entre el filtro exacto (Q9, Q10-CAJA) y el rango (Q8, Q11).

### 5.2 Capability Registry

- Fuente única de verdad: `CAPABILITIES: dict[str, CapabilityContract]` con 6 entradas.
- `_validate()` corre al importar el módulo y hace **fail-fast**: nombres únicos, versión, roles no vacíos, paths y descripciones presentes, y que **ningún texto de negocio exponga nombres internos** (`NUM_DOCTO`, `id_impresora`, SQL).
- Las **annotations MCP se derivan** de `OperationMode.READ` (V2 R17); no se escriben a mano.
- `CONTABILIDAD_ROLES` en `security.py` se deriva del contrato Q1, no de una lista local.

### 5.3 Montaje MCP dentro de FastAPI (fastmcp 2.14) — recordatorio

- `FastMCP("control-contable", streamable_http_path="/")` (si se deja `/mcp`, queda `/mcp/mcp` → 404).
- Hay que correr el **lifespan del sub-app MCP** dentro del lifespan de FastAPI, o el session manager falla con `Task group is not initialized`.
- El session manager corre **una vez por instancia**: por eso `tests/conftest.py` expone el fixture `client` **session-scoped**. No volver a `with TestClient(app)` por test.

### 5.4 SQL: aprendido en esta sesión

- Oracle **no** acepta un alias de `select` dentro del `group by` (falla `ORA-00904`). En Q10 los SQL agrupan por la columna real `codigo`, y el `decode` se aplica en el `select` exterior.
- Todos los SQL usan **owner explícito** (`DENT.boleta`, `DENT_CICLO.boleta`, `DENT.fichas`, `DENT.dominio`, `DENT.usuarios`, `DENT.bat_deuda`) — V2 §19 h6.
- `_fetchall()` traduce **cualquier** excepción de Oracle a `InfrastructureError` → `503 UNAVAILABLE`. Una caída nunca se disfraza de "tabla vacía".

### 5.5 Forma de los contratos

- Q8 y Q9 comparten `BoletaPorUsuarioItem` / `ConsultarBoletasPorUsuarioOutput` (misma forma, distinto SQL).
- Q10 devuelve `items` + `totales` (por canal, incluye ceros) + `total` (objeto `{cantidad, monto}`).
- Q3 agrega `meses_consultados: int` y `deuda_es_promedio_diario: bool` para que el agente no confunda el promedio con el saldo.
- Q10 expone `tipo_tarjeta` (uniforme), `codigo_tarjeta` (crudo) y `etiqueta_correo` (paridad con el legacy, que es asimétrico entre canales).

---

## 6. Cómo arrancar / probar

```bash
cd /Users/fernandosalvo/Desktop/humbold/enablement-layer
source .venv/bin/activate

# 1) Suite completa (196 tests; usa Oracle real si hay DSN)
pytest -q

# 2) Levantar server
uvicorn app:app --host 127.0.0.1 --port 8090

# 3) Salud
curl -s http://127.0.0.1:8090/health

# 4) REST (token de .env)
curl -s -H "Authorization: Bearer $AUTH_TOKEN_CONTADOR" \
  "http://127.0.0.1:8090/api/contabilidad/resumen-deuda?fecha=2017-12-15"

# 5) Detener
pkill -f "uvicorn app:app"
```

Los tests de paridad **se saltan solos** si no hay pool configurado; con DSN configurado exigen conexión real. La suite es verde en ambos escenarios.

---

## 7. Verificación de paridad hecha en vivo (evidencia)

Fecha de paridad usada: **2025-05-12** (salvo Q3, que usa 2017-12-15 por ser la fecha con datos de deuda).

| Capability | Fecha | Resultado verificado |
| --- | --- | --- |
| Q3 `resumen_deuda` | 2017-12-15 | `12-2017: 900601075` · `11-2017: 896653783` · `10-2017: 891873367` · `09-2017: 896509697` |
| Q10 CAJA | 2025-05-12 | CRD1 243/`15749600` · DEB1 843/`30033500` → total 1086/`45783100` |
| Q10 TOTEM | 2025-05-12 | CRD1 4/`92000` · DEB1 7/`206500` → total 11/`298500` |
| Q10 WEBPAY | 2025-05-12 | CRD1 16/`939000` · DEB1 44/`1892500` → total 60/`2831500` |
| Q10 gran total | 2025-05-12 | **1157 / `48913100`** |
| Q11 previsión | 2025-05-12 | **34 filas, 1305 / `54151100`** (top: `2022 BRACKET ESTETICO V2` 9/`643000`; `2024 BRACKET METALICO` 534/`28414500`) |
| Q8 emitidas | 2025-05-12 | **23 usuarios, 1305 / `54151100`** (top: `MENDEZ ROXANA IVETTE` 114/`2735000`; `. SISTEMA` 71/`3130000`) |
| Q9 anuladas | 2025-05-12 | **2 usuarios, 45 / `4428000`** (`MORALES VICENTE` 28/`3247000`; `ZELADA KATHALINA ALEJANDRA` 17/`1181000`) |

**Control cruzado:** Q11 y Q8 dan el mismo total (1305 / `54151100`) para la misma fecha, evidencia de que ambas recorren el mismo universo de boletas activas y solo cambian la clave de agrupación.

**Q3 sin datos recientes:** `DENT.bat_deuda` termina en 2023-03-30; cualquier fecha de hoy devuelve `NO_DATA` (correcto, cubierto por test).

---

## 8. Documentación producida en esta sesión

| Archivo | Contenido |
| --- | --- |
| `capacidades/CATALOGO.md` | Índice de las 6, contrato transversal, cómo elegir, advertencias de interpretación, PII, casos límite, tests, orden de construcción |
| `capacidades/consultar_resumen_deuda.md` | Ficha Q3 (17 secciones) |
| `capacidades/consultar_ingresos_por_tipo_tarjeta.md` | Ficha Q10 (17 secciones) |
| `capacidades/consultar_ingresos_por_tipo_prevision.md` | Ficha Q11 (17 secciones) |
| `capacidades/consultar_boletas_emitidas_por_usuario.md` | Ficha Q8 (17 secciones) |
| `capacidades/consultar_boletas_anuladas_por_usuario.md` | Ficha Q9 (17 secciones) |
| `arquitectura.md` | §3.1 composition root, §3.2 registry, §10 decisions verificadas, §10.1 follow-ups, §11 referencias |
| `estado_de_sesion_2026-10-02.md` | Este archivo |

La ficha de Q1 (`consultar_ingresos_por_tipo_pago.md`, sesión previa) ofició de plantilla de las 17 secciones.

---

## 9. Pendientes / próximos pasos

Nada crítico quedó a medias en el bloque Control Contable. Lo abierto es de endurecimiento:

1. **`tools/paridad.py`**: se propuso un script CLI de paridad contra Oracle, pero no se implementó. Hoy la paridad vive solo en `tests/test_paridad_oracle.py`.
2. **`create_pool()` ante DSN configurado pero inalcanzable**: el arranque lanza `ORA-12154` sin traducción; el `503 UNAVAILABLE` cubre fallos de consulta, no de arranque. Endurecer en Nivel 2.
3. **Paquete standalone `fastmcp`**: incompatible con `mcp` 1.30. No instalarlo; el servidor usa `mcp.server.fastmcp`.
4. **HTML real del correo**: no se pudo hacer diff visual contra el HTML legacy (solo paridad de valores numéricos, que es el criterio Nivel 0 de V2 §12).
5. **Próximo bloque**: fuera de Control Contable quedaron Agenda, Funcionarios/Turning, Notas clínicas y Becas/alignment (ver `CATALOGO.md` → "Fuera de alcance").

---

## 10. Referencias

- Estrategia: `000_MiEstrategiaV2.md` (autoritativa).
- Catálogo del bloque: `capacidades/CATALOGO.md`.
- Arquitectura del servidor: `arquitectura.md`.
- Fichas: `capacidades/consultar_ingresos_por_tipo_pago.md` · `consultar_resumen_deuda.md` · `consultar_ingresos_por_tipo_tarjeta.md` · `consultar_ingresos_por_tipo_prevision.md` · `consultar_boletas_emitidas_por_usuario.md` · `consultar_boletas_anuladas_por_usuario.md`.
- Queries validadas: `resumencontrolRICH.md` (Q1–Q15).
- Fuente legacy: `~/Desktop/ino/assesstment/app/DentWeb12_Java21/src/cl/llm/batch/ResumenControl.java` y `.../dent/ConsultaControl.java`.
- Notas de encuentros: `encuentros.md`.