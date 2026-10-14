Eres un implementador de capacidades READ en la Enablement Layer (FastAPI + FastMCP sobre Oracle).

Documentación obligatoria (léela completa antes de proponer nada):
1. /Users/fernandosalvo/Desktop/humbold/enablement-layer/README.md de enablement-layer (arquitectura, registry, composition root, reglas R1–R10, errores, tests).
2. /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/capacidades/PLANTILLA_CAPACIDAD.md (12 pasos, hallazgos H1–H5, Definition of Done).
3. /Users/fernandosalvo/Desktop/humbold/docs/go/encuentros.md. Solo implementaremos la capacidad **"Pendiente MCP correo (Agenda)"** (3 querys).
4. Fichas modelo: `capacidades/consultar_ingresos_por_tipo_tarjeta.md` (una capability con varias SQL / «nodos» bajo una sola llamada) y `capacidades/consultar_pacientes_por_ciudad_chile.md` (dominio nuevo, roles propios).
5. `capacidades/_plantilla/` (esqueleto copiable con marcadores TODO).


Reglas no negociables (rigen R1–R10 del README §18.1; resumen operativo):
- Paridad exacta con la fuente normativa: no innovar filtros (R10).
- El registry es la fuente única del contrato (nombres, descripción, roles, ruta, annotations).
- REST y MCP llaman a la MISMA instancia de service (composition.py). El adapter no tiene lógica.
- El SQL vive solo en el repository; el service no conoce tablas.
- Las annotations MCP se derivan de mode=READ; nunca se escriben a mano.
- La autorización ocurre antes de ejecutar, en un único punto (`require_contract`). Nunca dentro de la query ni del service.
- NO_DATA (404) ≠ UNAVAILABLE (503).
- El total lo calcula la capa, nunca el LLM.
- `from mcp.server.fastmcp import ...`, nunca el paquete standalone `fastmcp`.


====================================================================
CAPACIDAD DE ESTA TANDA
====================================================================

Decisiones ya fijadas por el dueño (no las re-litigues). Si alguna te parece que
rompe la paridad con la fuente, DETENTE y avísame ANTES de codificar.

- **Dominio NUEVO `agenda`** → aplica PASO 6b (`composition.py` + `app.py`).
- **UNA sola capability** que agrupa las **3 queries** del correo (no 3 tools). Modelo
  canónico: `consultar_ingresos_por_tipo_tarjeta` (#3), que son tres SQL bajo una llamada.
  La salida es **un JSON con tres secciones/nodos**.
- **Rol único: `ai_agent`** (ya existe en `KNOWN_ROLES`; NO se agrega rol nuevo, NO aplica H4).
- **`data_profile`: `operational`** (conteos de citas/bloqueos; sin PII de pacientes ni
  nombres de personas).
- **Entrada `fecha` OPCIONAL** (YYYY-MM-DD). Es el día del reporte:
  - si viene → se usa esa fecha para las secciones 1 y 3;
  - si viene `null`/ausente → `TRUNC(SYSDATE)` (comportamiento legacy).
- **Sección "agendados para mañana" = día + 1**: `D = fecha` si viene, si no
  `TRUNC(SYSDATE)`; el filtro usa `D + 1`. Por lo tanto:
  - `fecha` null → `TRUNC(SYSDATE)+1` (paridad exacta con el legacy);
  - `fecha` explícita → `fecha+1` (generalización pedida: "para cualquier fecha"; se
    reescribe el parámetro, si va null usa `sysdate+1`).
- **`NO_DATA` SOLO si las TRES secciones vienen vacías.** Si al menos una trae filas, se
  responde 200 y las vacías van como listas `[]` (mismo criterio que los canales de #3).
- **Mapeo de estados se hace en la CAPA** (no en SQL), exponiendo `codigo_estado` crudo +
  `estado` etiqueta. Tabla fijada:

  | `codigo_estado` | `estado` |
  |---|---|
  | `TRM` | Terminada |
  | `RSV`, `ING` | Reservada |
  | `RCP` | Recepcionada |
  | `INJ` | Injustificada |
  | `TMP` | Bloqueo |
  | `ASG` | Asignado |
  | `SUS` | Suspendida |
  | `DRV` | Derivada |
  | (cualquier otro) | el código crudo (paridad con el `else` del legacy) |

  Justificación: el correo real (`docs/refactorizacion/_build/data/agenda.json`) muestra
  `Bloqueo` como estado, y `TMP` es el estado de bloqueo de agenda
  (`Agenda.java:45-48` inserta `IND_ESTADO='TMP'` con `OBSERVACION='Bloqueo'`); en QA
  `TMP` es, con diferencia, el estado más numeroso. El snapshot Java
  (`ResumenControl.java:341-349`) rotula `TMP`→"Paciente Temporal": **se aparta a
  propósito** porque la fuente normativa del correo manda. Ojo: `RSV` e `ING` comparten
  etiqueta → el correo trae **dos filas "Reservada"**; se replica agrupando por **código**,
  no por etiqueta. `ASR`/`VIR`/`INF` no están mapeados → salen crudos (paridad).

Las 3 queries, con su fuente (respetar `count(id_agenda)` vs `count(1)` y el
`order by` tal cual; parametrizar con bind, nunca concatenar):

- **Sección 1 · Estado de citas** — `ResumenControl.setTablaAgendaHoy` (`ResumenControl.java:320`)
  ```sql
  select ind_estado, count(id_agenda) cantidad
  from DENT.agenda
  where fec_cita = to_date(:fecha,'YYYY-MM-DD')
    and cita_secuencia = 1
  group by ind_estado
  ```
  La capa agrega `TOTAL` (suma de cantidades) y aplica el mapeo de estados.

- **Sección 2 · Pacientes agendados para mañana** — `setTablaAgendaManana` (`:229`)
  ```sql
  select count(id_agenda) cantidad
  from DENT.agenda
  where fec_cita = to_date(:fecha_manana,'YYYY-MM-DD')
    and cita_secuencia = 1
    and ind_estado = 'RSV'
  ```
  Fila única; etiqueta fija `"Reservada"`; sin total. `:fecha_manana` lo calcula la capa
  (ver decisión de `fecha`). No le corresponde réplica `DENT_CICLO`.

- **Sección 3 · Citas por tipo previsión** — `getCitasPorTipoPrevision` (`:716`)
  ```sql
  select do.DOMIDESCRI, count(1) cantidad
  from DENT.agenda ag, DENT.fichas fi, DENT.dominio do
  where ag.FEC_CITA = to_date(:fecha,'YYYY-MM-DD')
    and ag.cita_secuencia = 1
    and ag.COD_PACIENTE = fi.NUM_FICHA
    and fi.TIP_PREVISION = do.DOMICODIGO
    and do.DOMINOMBRE = 'TIPO_PREVISION'
  group by do.DOMIDESCRI
  order by do.DOMIDESCRI
  ```
  La capa agrega `TOTAL`. `DOMIDESCRI` son literales del maestro: no consolidar ni
  interpretar (ej. `2022 Bracket Metálico` vs `2022 BRACKET METALICO V2`).

Forma de salida propuesta (ajústala si el encargo lo pide; tres nodos):
```json
{
  "fecha": "2026-09-23",
  "fecha_manana": "2026-09-24",
  "citas_por_estado":     {"items": [{"codigo_estado": "ASG", "estado": "Asignado", "cantidad": 3}], "total": 22087},
  "agendados_manana":     {"estado": "Reservada", "cantidad": 2108},
  "citas_por_prevision":  {"items": [{"prevision": "FONASA B", "cantidad": 2}, {"prevision": "2022 Bracket Metálico", "cantidad": 14}], "total": 3667}
}
```


Antes de escribir una sola línea de código debes:
A) Completar el "encargo" YAML de abajo (ya viene prellenado; corrige/confirma).
B) Responder las 6 preguntas de la PLANTILLA (§2), con las respuestas tentativas de abajo.
C) Decirme qué archivos tocarás en cada uno de los 12 pasos.
D) Señalar si el dominio es nuevo (SÍ: PASO 6b) y confirmar que NO se agrega rol nuevo.
E) Confirmar que agregarás `agenda.agenda_del_dia` a `CON_FECHA` en `test_registry.py`
   (acepta `fecha`, aunque sea opcional: NO va en `SIN_ARGUMENTOS`).
F) Fijar por escrito la tabla de decisiones replicadas (paso 6 de la ficha) y el mapeo
   de estados, y decirme cómo vas a manejar el `fecha` opcional en la firma MCP
   (agregar un `Annotated` opcional en `adapters/mcp/server.py`, hoy `FechaArg` es obligatorio).

Solo después de que yo apruebe el encargo y el plan de archivos, procedes paso a paso.
Empieza por el PASO 1 (registry) y espera confirmación antes de seguir.

---
ENCARGO (revisa y completa; deja en blanco solo lo que no aplique):

nombre_funcion:          # Agenda del día (las 3 tablas del correo "Resumen Control (Agenda)")
nombre_snake:            # agenda_del_dia
nombre_tool:             # consultar_agenda_del_dia   (sin versión, R10)
dominio:                 # agenda   (NUEVO → PASO 6b)
id_capability:           # agenda.agenda_del_dia
rest_path:               # /api/agenda/agenda-del-dia
sql_id:                  # ENC.AGENDA_DIA (o Q<n> local del repository; la fuente no trae id)
fuente_normativa:        # src/cl/llm/batch/ResumenControl.java:320 (hoy), :229 (mañana), :716 (previsión); correo docs/refactorizacion/_build/data/agenda.json
metodo_legacy:           # ResumenControl.setTablaAgendaHoy / setTablaAgendaManana / getCitasPorTipoPrevision (ConsultaControl TIPO_CONSULTA=1)
data_profile:            # operational
roles:                   # ("ai_agent",)
acepta_fecha:            # sí, OPCIONAL (null → TRUNC(SYSDATE); sección "mañana" → +1 día)
acepta_otros_filtros:    # ninguno
expone_pii:              # no (solo conteos; no proyecta nombres ni identificadores)
es_censo_variable:       # no → golden file (usar 2026-09-23 con datos + una fecha sin citas)

---
RESPUESTAS TENTATIVAS a las 6 preguntas (confírmalas o corrígelas antes de codificar):

1. Fuente normativa: `ResumenControl.java:320/229/716` (Java) + el correo real en
   `docs/refactorizacion/_build/data/agenda.json` (fuente de verdad para el mapeo de
   estados y el orden de las filas del correo).
2. ¿Reporte legacy más parecido que no es la fuente? La vista web
   `ConsultaControl.java` (TIPO_CONSULTA=1) usa el MISMO `ResumenControl`, así que no hay
   divergencia salvo la generalización de `fecha`.
3. Decisiones del legacy que se replican: agrupar por `ind_estado` (código crudo) y mapear
   a etiqueta en la capa; `cita_secuencia=1`; sección "mañana" filtra `ind_estado='RSV'`;
   sección 3 join `dominio.DOMINOMBRE='TIPO_PREVISION'`; `RSV`+`ING` → "Reservada" (dos
   filas); `TOTAL` calculado en la capa; "mañana" es relativo (día+1).
4. `allowed_fields`/`forbidden_fields`: `operational`. Excluir siempre `USURUT`/`USULOGIN`.
5. Roles: solo `ai_agent` (no entra `contador`: no es trabajo financiero).
6. PII: no expone PII.
