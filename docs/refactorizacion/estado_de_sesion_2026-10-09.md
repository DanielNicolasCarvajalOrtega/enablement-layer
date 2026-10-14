# Estado de sesión · 2026-10-09

> **Tema:** Proyecto 1 (hacia atrás) y Proyecto 2 (hacia adelante) sobre MCP; contratos de
> salida, estrategia de contexto y cómo evitar que las respuestas gordas revienten al LLM.
>
> **Estado:** diseño/exploración. **No se implementó nada.** La decisión de estrategia
> queda pendiente de un **JSON representativo de ~1.500 filas** que el dueño construirá
> manualmente para probar cuál es la mejor forma de implementar P1 y P2.
>
> **Cómo retomar:** leer de §1 a §10 para el modelo, §11 para lo ya decidido, §16 para el
> juego de capacidades, §17 para lo que falta decidir y §18 para el próximo paso.

---

## 1. Contexto de origen

- Existe la **Enablement Layer** (`~/Desktop/humbold/enablement-layer`): un servidor
  Python **FastAPI + FastMCP sobre Oracle** que hoy expone 7 capacidades de solo lectura
  (6 de Control Contable + 1 de Pacientes), en repositorio publicado
  (`github.com/fdosalvo/enablement-layer`), con Capability Registry, roles Bearer,
  paridad con el legacy y 240 tests.
- De esa base venimos discutiendo un problema nuevo: **capacidades analíticas** de agenda
  clínica que devuelven **mucha información anidada** (boletas + pagos + citas + agenda +
  acciones + diagnósticos) y que, pasadas al contexto del LLM, lo saturan.
- La conversación derivó en el diseño de **dos proyectos** (retrospectivo y prospectivo)
  que se apoyan en MCP como capa de consulta autorizada, estructurada y trazable.

---

## 2. Visión estratégica (la imagen del CEO / INO)

Estructura general:

| Lado | Nombre | Pregunta central | Naturaleza |
| :--- | :--- | :--- | :--- |
| Izquierdo (rojo) | **Proyecto 1 – Hacia atrás** | ¿Qué pasó? | Reportes de lo ya ocurrido |
| Derecho (verde) | **Proyecto 2 – Hacia adelante** | ¿Qué viene mañana? | Reportes de lo que sucederá |
| Centro | **Base de datos + MCP + Llaves comunes** | — | Fuente única + consultas controladas |
| Abajo | **Inteligencia Artificial** | — | Cruza, detecta, predice y recomienda |

**Proyecto 1 – Hacia atrás.** Tres capas:

1. Pacientes que vinieron → asistencia (sí/no) + existencia de boleta asociada.
2. Boletas → área, monto, odontólogo (especialidad), asistente, administrativa.
3. Clínico (todos) → notas del doctor, materiales, epicrisis.

**Proyecto 2 – Hacia adelante.** Lo que viene:

- Reservados → por área, tipo de tratamiento, doctor.
- Disponibilidad → cortes (tarde-noche + mañana), confirmación del doctor, confirmación
  del paciente, recursos (doctor, sillón, equipo, paciente).
- Cruce capacidad vs demanda → doctores por área vs pacientes que vienen.

**Llaves comunes** (el cruce P1 ↔ P2): **`ficha` (anonimizada), `area`, `tratamiento`,
`doctor`**. (Y en la práctica se agregan `fecha`, `hora`/franja.)

**Rol de la IA:** no consulta la base directamente; **consume los resultados de las
capacidades MCP** y cruza, detecta anomalías, encuentra patrones, predice y recomienda.

**Mensaje de valor:** "Datos que hoy informan, mañana transforman".

---

## 3. Contrato JSON de partida · `agenda.consultar_agenda_clinica_dia`

Se propuso una capacidad MCP orientada a **Agenda Clínica del día** que sirve tanto a P1
como a P2. Estructura (resumida a lo esencial):

```jsonc
{
  "fecha_consulta": "2026-10-09",
  "tipo_reporte": "agenda_clinica_dia",
  "base": "pacientes_con_atencion_programada",
  "resumen": {                      // totales calculados por la capa
    "total_atenciones": 3, "asistieron": 2, "no_asistieron": 1,
    "con_boleta": 2, "sin_boleta": 1, "total_monto_boletas": "125000.00"
  },
  "items": [ {                      // una fila por atención (nodo gordo)
    "atencion_id": 1045821, "ficha": "F-88421", "paciente_anonimizado": "PAC-88421",
    "hora": "09:00", "area": "ORTODONCIA", "tratamiento": "Control de aparatos",
    "doctor": { "codigo": "DOC-032", "nombre": "DRA. MARÍA FERNÁNDEZ", "especialidad": "Ortodoncia" },
    "asistente": "CAROLINA SOTO", "administrativa": "PATRICIA LAGOS",
    "asistencia": { "asistio": true, "hora_llegada": "08:52", "estado": "ATENDIDO" },
    "boleta": { "tiene_boleta": true, "numero": 789456, "fecha_emision": "2026-10-09",
                "monto": "45000.00", "tipo_pago": "TRJ", "estado": "ACT",
                "usuario_emisor": "MORALES VICENTE" },
    "clinico": { "notas_doctor": "...", "materiales": ["Arco NiTi 0.016", "Ligaduras elásticas"],
                 "epicrisis": "..." },
    "llaves_comunes": { "ficha": "F-88421", "area": "ORTODONCIA",
                        "tratamiento": "Control de aparatos", "doctor": "DOC-032" }
  } ],
  "cruce_capacidad_demanda": { "por_area": [ { "area": "ORTODONCIA",
      "atenciones_programadas": 1, "asistieron": 1, "no_asistieron": 0,
      "doctores_disponibles": 2 } ] },
  "metadata": { "capability_id": "agenda.consultar_agenda_clinica_dia",
                "oracle_sql_id": "ENC.AGENDA_CLINICA_DIA",
                "generado_en": "2026-10-09T16:28:00-03:00", "registros_devueltos": 3 }
}
```

Notas de diseño **a favor** (declaradas por el dueño): llaves comunes siempre presentes;
asistencia y boleta como objetos anidados claros; clínico **solo cuando asistió**; resumen
calculado por la capa (el LLM no suma); cruce capacidad/demanda incluido; anonimización de
paciente (`PAC-…` + `ficha`).

---

## 4. Crítica al contrato de partida (por qué reproduciría el problema)

Con 3 atenciones se ve sano; con 300 atenciones del día o al reutilizarlo para rangos,
**es el mismo problema de las "filas gordas"**:

1. **Peso por fila:** `notas_doctor` + `materiales[]` + `epicrisis` son texto libre de
   largo variable → es lo que engorda cada fila.
2. **Duplicación:** `ficha`, `area`, `tratamiento`, `doctor` aparecen al tope **y** en
   `llaves_comunes`.
3. **Nulos verbosos:** cuando no hay boleta ni clínico, igual se emiten todas las claves en
   `null` (el "clínico solo si asistió" debería extenderse a `boleta`).
4. **PII + clínico mezclados con financiero:** se anonimiza el paciente pero **no**
   `doctor.nombre`, `asistente`, `administrativa`, `usuario_emisor`; y `notas/epicrisis`
   pueden re-identificar. Mezclar `clinical` + `financial_pii` en un mismo payload amplía
   el radio de exposición (un agente contable no debería recibir narrativa clínica).
5. **`cruce_capacidad_demanda` mezcla fuentes:** `doctores_disponibles` es P2;
   `asistieron/no_asistieron` es P1. Conviene que sea **capacidad propia**.
6. **Ids a normalizar:** `ficha` vs `paciente_anonimizado`; `DOC-032` como surrogate del
   `USURUT` (que el registry prohíbe exponer) → definir el mapeo estable.

Recomendaciones de refinamiento (sin perder la visión): eliminar duplicación; omitir
objetos vacíos; clínico opt-in y por rol; agregar metadata de página (`total`,
`truncated`, `next_cursor`); gobierno de campos `allowed_fields`/`forbidden_fields`
(hoy **no** implementado en la capa).

---

## 5. El problema central y la estrategia de 5 mecanismos

**Problema:** un tool MCP devuelve un JSON gordo (p. ej. 3.000 filas) que satura el
contexto: costo superlineal, latencia, costo económico, degradación del razonamiento y
riesgo de **truncado silencioso** por parte del cliente.

**Principio rector:** *el payload del tool es la respuesta, no la base de datos.* Lo que
viaja al contexto es una **vista resumida y acotada**; los KPIs/totales los calcula la
capa (extensión de la regla R9 de la estrategia).

Mecanismos (combinables):

| # | Mecanismo | Qué hace |
| :-- | :--- | :--- |
| A | **Drill-down (varias capacidades)** | resumen → listado paginado → detalle por id; nunca un tool que devuelve todo |
| B | **Agregación en la capa** | KPIs en SQL/`GROUP BY` + service; el LLM solo interpreta |
| C | **Paginación con contrato** | `page`/`page_size` o cursor, `max_records` duro, metadata `{total, returned, truncated, next_cursor}` |
| D | **Proyección / poda de campos** | el listado trae 6–8 campos; el detalle trae el resto; `allowed/forbidden_fields` |
| E | **Compactación de serialización** | normalizar catálogos, evitar anidamiento repetido, claves cortas; CSV/TSV para tabular |
| F | **Externalización por handle** | guardar el crudo y devolver `query_id`/URI + resumen |

Guardrails transversales: presupuesto de tokens/bytes por llamada (`bytes/4 ≈ tokens`),
`execution_policy` (`max_records`, `timeout`, rate/burst/concurrency — hoy no implementada),
telemetría de `records`/`bytes` sin payload.

---

## 6. Proyecto 1 como árbol / embudo (no como lista)

El dueño lo describió como un embudo. Ejemplo con sus números: **1.000 citas → 500 no
vinieron / 500 vinieron → 250 con boleta / 250 sin boleta.**

```
DÍA (fecha)
├── N0 · Foto de la agenda — OFERTA
│      capacidad (xx atenciones), horas disponibles (mm)
│      ├─ horas reservadas (nn)
│      ├─ horas bloqueadas (uu)
│      └─ horas libres
├── N1 · Citas del día — DEMANDA (total = 1000)
│      ├── N2a · NO ASISTIÓ (500)
│      │        └─ corte por: hora · doctor · especialidad · área · previsión · …
│      └── N2b · ASISTIÓ (500)
│               ├── N3a · CON BOLETA (250)
│               │        ├─ financiamiento: EFE / TAR / DEB / CRE
│               │        ├─ diagnósticos (agregados)
│               │        └─ acciones (agregadas)
│               └── N3b · SIN BOLETA (250)
│                        └─ motivo: garantía · prepago · campaña free · cita previa
```

**La clave:** el LLM pide el **árbol (chico)**, no las **hojas (gordas)**. Las hojas
(citas/pacientes) se piden **por id**, paginadas y proyectadas.

---

## 7. Capa semántica compartida: medidas + dimensiones + jerarquía

Mismo cubo para P1 y P2; cambia si el hecho es **observado** (P1) o **esperado** (P2).

**Medidas**

| Grupo | Medidas |
| :--- | :--- |
| Oferta | `slots_capacidad`, `horas_disponibles`, `horas_bloqueadas`, `horas_reservadas`, `horas_libres`, `doctores_disponibles` |
| Demanda | `citas_programadas`, `citas_reservadas` |
| Resultado P1 | `asistidas`, `no_show`, `con_boleta`, `sin_boleta`, `monto` |
| Proyección P2 | `p_no_show`, `esperados = reservados × (1 − p_no_show)` |

**Dimensiones (allowlist):** `fecha`, `jornada` (AM/PM), `hora`/franja, `doctor`,
`unidad/especialidad`, `area`, `tratamiento`, `prevision`, `estado_cita`, `tipo_pago`,
`financiamiento`, `motivo_sin_boleta`, `tipo_pool` (BASE/LIB/REE/SOL).

**Llaves comunes:** `ficha`, `area`, `tratamiento`, `doctor` (+ `fecha`, `hora`).

Un nodo = `{ filtro, medidas, dimensiones abribles, conteo }`. El agente navega el árbol.

---

## 8. Proyecto 2 como espejo prospectivo

Mismo árbol, invertido en el tiempo, con incertidumbre (probabilidad / valor esperado):

```
MAÑANA (fecha+1)
├── P0 · Oferta planificada (disponibilidad)
│      doctores por unidad/especialidad, sillones, equipos; franjas AM/PM
│      ├─ confirmación doctor (sí/no/pendiente)
│      └─ confirmación paciente
├── P1 · Demanda comprometida — RESERVADOS
│      por área · tipo de tratamiento · doctor
│      └─ esperados = reservados × (1 − p_no_show)
├── P2 · Cruce capacidad vs demanda
│      disponibles vs esperados por área y franja → sobrecupo / huecos / cuellos
└── P3 · Riesgo / simulación
       ├─ p_no_show(dims)  ← viene de P1 (ventana histórica)
       └─ "¿y si el doctor X no viene?" → afectados · alternativas · impacto
```

---

## 9. Bisagra P1 → P2: `p_no_show`

Las distribuciones de P1 se convierten en probabilidades de P2:

- P1 entrega `p_no_show` por `doctor × jornada × unidad` (y combinaciones).
- P2 la aplica a las reservas de mañana → `esperados = reservados × (1 − p_no_show)`.
- Resultado: el cruce capacidad/demanda pasa de conteo plano a **riesgo**.

Diseño propuesto:
- Capacidad `agenda.tasa_no_show(dimensiones, desde, hasta)`.
- **Ventana histórica** parametrizable: por defecto `hoy() − x días` (el dueño dijo que
  "generalmente importa el ayer", pero quiere considerar `hoy() − x días`).
- **Fallback jerárquico** si una celda tiene pocos casos (evitar sobreajuste): subir a
  `unidad × jornada` → global.

---

## 10. Escenario "un doctor no asiste" (P3 de P2)

Capacidad de simulación `READ` (what-if, no toca la agenda real):

1. **Afectados:** citas reservadas del doctor en la ventana (`RSV/ASG/ASR/RCP/ING/TRM`).
2. **Alternativas:** otros doctores de la misma unidad con `CALENDAR_DOC` vigente y carga
   menor a su capacidad.
3. **Reasignación propuesta** + impacto en horas/ocupación.
4. **Pacientes a avisar.**

Distinción **READ vs ACT:** simular es `READ`; **reagendar de verdad es `ACT`** (escritura),
que exige gobierno de escritura, confirmación y trazabilidad. La capa hoy es solo lectura →
`ACT` queda explícitamente fuera de la fase actual (salvo decisión en contrario).

---

## 11. Decisiones ya confirmadas por el dueño

| Tema | Decisión |
| :--- | :--- |
| Diseño | **Híbrido**: árbol jerárquico + agregación genérica acotada (allowlist) + capacidades curadas |
| Oferta P2 | Existe en `DENT`: (`CALENDAR_DOC` + `AGENDA` + `UNIDAD` + `USUARIOS`) |
| `p_no_show` | **Ventana histórica** parametrizable (`hoy() − x`; `x=1` = "ayer") |
| Rol IA | Existe un **rol IA** como consumidor de primera clase |

---

## 12. Hallazgos de fuentes para P2 (de `docs/serverMCP/`)

El dueño no recordaba las tablas de disponibilidad; se encontraron en sus propios docs,
donde hay un plan previo del servidor `dentweb-mcp` con una query **verificada en QA
(2026)**:

- **Pool / disponibilidad:** `CALENDAR_DOC` → `TIPO` (`BASE/LIB/REE/SOL`), `RUT_DOC`,
  `COD_ESTACION`, `DIA_SEMANA`, `JORNADA` (1=Mañana, 2=Tarde), vigencia `FEC_INI/FEC_TRM`,
  `ESTADO='A'`.
- **Carga del día:** `AGENDA` → `TIP_DOC = UNIDAD.UNI_CODIGO`, `COD_MEDICO = USUARIOS.USURUT`,
  `FEC_CITA`, `HOR_CITA` (`HH24:MI:SS`), estados `RSV,ASG,ASR,RCP,ING,TRM,INJ,DRV,SUS,TMP,INF,BLQ`.
  Una cita puede tener varias filas (`CITA_SECUENCIA`) → contar `DISTINCT ID_AGENDA`.
- **Sillones:** `UNIDAD.UNI_NRO_SILLON`. **Doctor:** `USUARIOS` (`USURUT`, `USUNOMC`,
  `USUAPEP`, `USUTELEFONO`).
- Pendientes documentados: `BASE` vs `LIB` (liberada) / `REE` (reemplazo); corte AM/PM
  (fijo en 13:00 vs colación real `UNI_HRA_INI_COL`); NLS de `DIA_SEMANA`; fórmula de
  capacidad y umbrales los define la dirección clínica.
- Referencias: `docs/serverMCP/mcp-servidores.md` §6, `docs/serverMCP/02-contrato-tools.md`.

---

## 13. Contradicción abierta: formato de "sobre" (envelope)

Coexisten dos estilos incompatibles:

- **Enablement Layer** (la viva y publicada): `{fecha, items, total}` + Capability
  Registry + roles + tests.
- **`docs/serverMCP`**: `{success, data[], metadata{}, error}`.

**Recomendación:** alinear P1/P2 al estilo de la Enablement Layer, porque ya tiene
registry, roles, paridad y tests. Decisión pendiente del dueño.

---

## 14. ¿Pandas en el service? Factibilidad (exploración)

Escenario imaginado por el dueño: un service MCP corre ~30 `SELECT * FROM tabla WHERE
fecha = fecha−1` (y otras con `fecha+1`), trae todo a **pandas**, hace todos los KPIs, y
devuelve ~1.000 filas agrupadas (en vez de 5.000).

Veredicto: **factible**, y es la dirección correcta para P1/P2, **con matices**:

- 30 queries × 5.000 = 150.000 filas: para pandas es trivial; el cómputo **no** es el
  problema. El problema es **qué columnas y de qué ventana** se traen.
- Riesgos: `SELECT *` (anti-patrón; traer solo columnas necesarias); 30 viajes a Oracle
  (latencia N+1) → consolidar/paralelizar; **dinero en `float`** (usar entero de centavos
  o `Decimal`); memoria por request y concurrencia; paridad (mover agregación a Python
  rompe "SQL idéntico al legacy" — aceptable solo para analítica **nueva**); PII/clínico en
  el proceso; determinismo (`groupby` no garantiza orden); `pandas` **no está** en
  `requirements.txt` (dependencia nueva y pesada; alternativa `DuckDB` o SQL analítico).
- Regla propuesta: **SQL agrega primero, Python compone después.** Filtrar/reducir y
  `GROUP BY` en SQL; pandas/DuckDB solo para reshape/pivot/ratios.
- 1.000 filas finales **pueden seguir siendo mucho** (~150 KB) → el árbol debe apuntar a
  **decenas de nodos**, no a 1.000 filas.
- Si el cómputo se repite ("ayer importa") → **mart nocturno** (ETL a tabla/vistas
  materializadas) y el MCP **lee el mart**; el "hoy()−x" reciente se calcula on-demand.

---

## 15. Plano de control vs plano de datos (sandbox / progressive disclosure)

Observación del dueño: cuando usa opencode/Claude Code/Codex como clientes MCP, el JSON
gordo se mete al contexto y da problemas; pero en una sesión como esta (con sandbox) el
LLM escribe programas y analiza sin problema. ¿Por qué el cliente no detecta el tamaño y
usa sandbox?

- **Plano de control** (chico): qué capacidad, schema, parámetros, resumen, KPIs → lo
  procesa el LLM.
- **Plano de datos** (grande): las filas gordas → lo procesa **código**.
- Un tool MCP **devuelve datos como mensaje de contexto**: no hay indirección; el plano de
  datos aterriza en el de control.
- **No es capacidad del protocolo MCP**, es del **agente/cliente**: MCP no "ve el tamaño y
  desvía"; no todos los clientes tienen sandbox (Claude Desktop, n8n no ejecutan código);
  el umbral es heurístico; persistir/ejecutar tiene implicancias de seguridad; y hay
  **truncado silencioso** (peor que fallar).
- **No se puede depender de que el cliente lo haga.** Hay que diseñar la capa:

| Nivel | Mecanismo | Para quién |
| :--- | :--- | :--- |
| 1 | **Respuesta acotada por contrato** (árbol + metadata) | todos los clientes |
| 2 | **Artefacto + referencia** (`resource_link`/URI + schema + muestra + conteo) | clientes con sandbox |
| 3 | **Análisis server-side** (tool `analizar(...)`) | clientes sin código |

- **Truco clave:** la capa ya expone **MCP y REST** → usar **MCP para el plano de control**
  (descubrir, decidir, resumen) y **REST para el bulk** (el sandbox hace `curl`→archivo y
  analiza con código). Así no se depende de que el cliente MCP desvíe la respuesta.
- La conclusión: **no delegar en el cliente**; default acotado (Nivel 1) + artefacto
  (Nivel 2) + análisis server-side (Nivel 3).

---

## 16. Juego de capacidades propuesto (híbrido, sin implementar)

| Proyecto | Capa | Capacidad | Modo |
| :--- | :--- | :--- | :--- |
| P1 | curada | `agenda.resumen_dia(fecha)` — N0+N1 | READ |
| P1 | curada | `agenda.embudo_dia(fecha)` — conteos del árbol | READ |
| P1 | genérica | `agenda.agregar(desde, hasta, nodo, dimension, page)` | READ |
| P1 | detalle | `agenda.atenciones(fecha, filtros, page)` | READ |
| P1 | detalle | `agenda.detalle_atencion(atencion_id)` | READ |
| P1/P2 | métrica | `agenda.tasa_no_show(dimensiones, desde, hasta)` | READ |
| P2 | curada | `planificacion.disponibilidad(fecha, unidad)` — `CALENDAR_DOC` | READ |
| P2 | curada | `planificacion.reservados(fecha, dimension)` | READ |
| P2 | curada | `planificacion.cruce_capacidad_demanda(fecha)` | READ |
| P2 | curada | `planificacion.simular_ausencia_doctor(fecha, doctor, jornada)` | READ |

Todas con techo (`max_records`/`max_cells`), paginación y `total/returned/truncated` en
metadata. El árbol nunca viaja como filas; las hojas solo por `id`.

Encaje con la arquitectura actual:
- Dominio **nuevo** (`agenda` / `planificacion`) → PASO 6b de `PLANTILLA_CAPACIDAD.md`
  (composition root + `app.py`).
- `oracle_sql_id` `ENC.AGENDA_CLINICA_DIA` es una **composición nueva**, no una query del
  legacy; la fuente normativa son las consultas de `docs/go/encuentros.md` (`DENT.agenda`,
  `DENT.acciones`, `DENT.prod_out_enc`, `DENT.fichas`, `DENT.boleta`, `DENT.usuarios`) más
  la disponibilidad de `docs/serverMCP`.
- Tensión con R7/R15 ("el service no conoce columnas") si se usan DataFrames crudos en el
  service → resolver con módulo de analítica e interface tipada, o aceptar la excepción de
  forma explícita.

---

## 17. Preguntas abiertas / pendientes de decidir

1. **¿Dónde viven P1/P2?** ¿Se extiende la Enablement Layer (nuevos dominios
   `agenda`/`planificacion`) o el `dentweb-mcp` de `docs/serverMCP`? Decide registry,
   roles, envelope y tests.
2. **Envelope:** ¿estilo Enablement Layer (`resumen`+`items`+`metadata`) o `{success, data,
   metadata, error}` de serverMCP? (Recomendado: Enablement Layer.)
3. **Simulación:** ¿`READ` what-if por ahora, o se quiere llegar a `ACT` (reagendar) en el
   corto plazo?
4. **`x` default** de la ventana histórica y granularidad mínima de `p_no_show`
   (`doctor × jornada × unidad` con fallback propuesto).
5. **Gobierno de clínico/PII:** qué rol ve `notas/epicrisis` y nombres de empleados; si el
   rol IA ve todo; construcción de `allowed_fields`/`forbidden_fields` (hoy inexistente).
6. **Fuente de la oferta:** ¿se toma la query de disponibilidad de `docs/serverMCP` como
   normativa, o se re-verifica contra la base actual?
7. **Nivel 2/3:** ¿el plan contempla **artefacto + `resource_link` + REST** como mecanismo
   oficial, o el default es solo análisis server-side y el sandbox queda como opción
   avanzada? (Y: quién puede descargar el crudo con PII clínica.)
8. **Volumen real** de un día pico (define si el listado necesita paginación o basta techo).
9. **Alcance temporal de P1:** ¿solo "hoy" o también rangos (semana/mes) para alimentar
   `p_no_show`?
10. **Pandas vs SQL-first/DuckDB** para el reshape (pandas agrega ~60 MB de dependencias).

---

## 18. Próximo paso inmediato (definido por el dueño)

- El dueño **construirá manualmente un JSON representativo de ~1.500 filas** con la data
  de agenda clínica, para iniciar pruebas de **cuál es la mejor estrategia de
  implementación**. Todo orientado a **P1 y P2**.
- Con ese fixture se probarán, sobre datos realistas:
  - el peso/contexto de la respuesta (arbol vs filas),
  - el corte (drill-down) y la paginación,
  - la agregación server-side vs pandas/DuckDB,
  - el patrón artefacto + REST + sandbox (Niveles 2/3),
  - y la derivación de `p_no_show` (P1 → P2).
- **No implementar** hasta cerrar las decisiones de §17 (en especial 1, 2 y 3).

---

## 19. Referencias

- `arquitectura.md` — arquitectura del servidor (enablement-layer).
- `000_MiEstrategiaV2.md` — reglas R1–R20 (R9 totales en la capa; R10 no inventar filtros).
- `capacidades/CATALOGO.md` y `capacidades/PLANTILLA_CAPACIDAD.md` — patrón de capacidades
  y hallazgo H5 (`allowed_fields`/`forbidden_fields`/`performance` no implementados).
- `../go/encuentros.md` — queries normativas (Agenda, Funcionarios, Notas, etc.).
- `../serverMCP/mcp-servidores.md` y `../serverMCP/02-contrato-tools.md` — disponibilidad
  (`CALENDAR_DOC` + `AGENDA` + `UNIDAD` + `USUARIOS`), envelope `{success, data, metadata,
  error}`.
- Repositorio: `github.com/fdosalvo/enablement-layer`.
