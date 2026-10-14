---
title: "Retroalimentación estratégica — DREAMS / DentWeb12"
date: 2026-09-21
tags: [modernizacion, legacy, django, mcp, oracle, estrategia]
status: "review-externa"
---

# Retroalimentación estratégica — DREAMS / DentWeb12

> Documento de respuesta a la solicitud: evaluación crítica de la estrategia documentada en `dreams_explorer.md`, brecha entre estrategia ideal y real, y orientación sobre el punto de inicio. Incluye respuesta directa a las tres inclinaciones actuales del autor: (1) arquitectura Django, (2) MCP/JSON-RPC como mecanismo de integración preferente, (3) mantener Oracle 11g XE sin relaciones explícitas y declararlas en el ORM.

---

## 0. Resumen ejecutivo

**Veredicto corto:** vas por muy buen camino. El documento está en el ~75–80% de lo que una estrategia de modernización seria necesita, y en algunos aspectos está por encima del estándar de la industria (la separación de los tres problemas, los gates con evidencia, el characterization testing, el activo RICH). **La brecha que te resta no es de ideas, sino de decisiones operativas, restricciones técnicas no registradas y elementos de ejecución que todavía no aparecen en el papel.**

Tres hallazgos centrales de esta revisión:

1. **Existe un conflicto técnico real que el documento no registra: Django moderno ↔ Oracle 11g XE.** Las versiones actuales de Django soportan oficialmente Oracle 12.1+ (2.2) y 12.2+ (versiones recientes); 11g quedó fuera del soporte oficial. Y el driver `python-oracledb` requiere *thick mode* (Instant Client) para conectar a 11g. Esto no invalida tu estrategia, pero obliga a reformular la pregunta "¿dónde empiezo?" y probablemente a invertir el orden de llegada de PostgreSQL: no como migración operacional, sino como **plataforma del nuevo desarrollo**.

2. **MCP es correcto como capa de inteligencia, pero riesgoso como capa de integración principal del core.** MCP no es "JSON-RPC en vez de REST": es un protocolo de exposición de *herramientas para LLMs* que usa JSON-RPC 2.0 como transporte. Su valor está en el consumo por agentes, no en reemplazar a OpenAPI para aplicaciones. La arquitectura sana es: **un Service Layer interno, con dos fachadas (MCP para IA, OpenAPI para apps)**. Y las tools deben ser *gruesas y de dominio*, no un reflejo 1:1 de los 239 helpers.

3. **"Mantener Oracle tal cual" y "nueva plataforma en Django moderno" son incompatibles en el tiempo.** Toda herramienta moderna que agregues (drivers, ORM, CDC, dbt, frameworks) pagará un "impuesto de compatibilidad 11g". La salida elegante — y coherente con tu propia lógica de Intelligence-First — es **meter PostgreSQL primero por el lado analítico/del piloto**, dejando Oracle operacional intacto. Oracle deja de ser "para siempre" y pasa a ser "hasta que el piloto demuestre el camino".

**Respuesta directa a "¿dónde empiezo?"**: ni por la BD ni por la app completa. Empieza por **un dominio acotado + un harness de caracterización**. La base de datos con 0 FK no es el punto de partida; es un riesgo que se encapsula. La app completa no es el punto de partida; es la suma de dominios que irás estrangulando. El punto de partida correcto es: *módulo piloto elegido con criterio, datos de prueba sanitizados, y evidencia de comportamiento*. Todo lo demás cuelga de eso.

---

## 1. Evaluación general del documento

### 1.1 Lo que está genuinamente bien (no es cortesía)

**a) La separación de los tres problemas (A/B/C) es el mejor contenido del documento.**
Separar "legacy tecnológico", "modelo de información" y "explotación del conocimiento" no es un ejercicio retórico: es la decisión que evita el error más común de las modernizaciones, que es financiar tecnología con argumentos de tecnología. Tu reformulación de la conversación con el CEO (paso 38) es correcta y es, en la práctica, lo que separa los proyectos que obtienen presupuesto de los que mueren en comité. Este reencuadre está alineado con lo que la industria ha aprendido en la última década sobre *modernización dirigida por valor* frente a *reescritura dirigida por tecnología*.

**b) Intelligence-First es estratégicamente sólido y coherente contigo mismo.**
La secuencia Expose → Intelligence → Modernize no contradice el strangler: lo financia. El ciclo virtuso que describes (inteligencia demuestra valor → valor financia modernización → modernización mejora datos → mejores datos potencian inteligencia) es el argumento correcto. Mantenlo como columna vertebral.

**c) Los gates con evidencia reproducible son exactamente la práctica diferenciadora.**
"Ningún gate se supera sin evidencia concreta y reproducible" (paso 22) es la frase más valiosa del documento junto con la del paso 39. La mayoría de las modernizaciones legacy fallan por avanzar por opinión. Tu mecanismo es el correcto. Lo que falta (ver §6) es definir *qué instrumentos producen esa evidencia*.

**d) El characterization testing y el shadow mode son la técnica correcta.**
Tu Idea 7 (backend nuevo en paralelo comparando outputs) es, de las diez ideas de la tormenta, la más valiosa técnicamente. La equivalencia funcional no se asume: se mide. Eso es testeo diferencial y es la base de cualquier reemplazo seguro de un sistema sin tests.

**e) El activo RICH es real y raro.**
689 archivos con código fuente incrustado, verificados línea a línea, con metadata estructurada: esto está por encima del 95% de los proyectos legacy en cuanto a inteligibilidad previa. Es literalmente el insumo que hace viable tu estrategia "con fuerte asistencia de IA". Sin este activo, la mitad del documento sería wishful thinking.

**f) La crítica a las estimaciones tradicionales y el piloto calibrador son maduros.**
Rechazar las estimaciones pre-piloto y proponer medición real de horas humanas, iteraciones de IA y equivalencia funcional es lo correcto. No calibrar con un piloto es el error #1 de estimación en este tipo de proyectos.

### 1.2 Debilidades estructurales del documento

**a) Es un documento de posibles; le faltan decisiones cerradas con criterio de reversa.**
Tienes 39 pasos más 5 estrategias más 10 ideas más una recomendación. Eso es excelente como espacio de exploración, pero el riesgo evidente es que el documento se convierta en una tormenta permanente donde nada se cierra. Cada decisión que vayas tomando (Django, MCP, Oracle-temporal, módulo piloto) debería registrarse como un **ADR (Architecture Decision Record)** con: contexto, opciones, decisión, consecuencias, y condición de reversa. Sugerencia concreta: agrega una sección "Decisiones tomadas" con estado Confirmado/Hipótesis/Descartado y fecha. Hoy eso está disperso en el paso 27.

**b) No hay modelo económico.**
Mencionas el costo de licenciamiento Oracle y el costo de oportunidad, pero no hay números: cuánto cuesta Oracle hoy, cuánto cuesta una hora de desarrollo legacy vs moderno, cuánto valdría el primer caso de inteligencia. Sin esto, la conversación con el CEO sigue siendo cualitativa.

**c) No hay definición de "valor" medible para la línea de inteligencia.**
Los ejemplos del paso 35 (alertas de stock, riesgo de cartera, retrasos de laboratorio) son buenos, pero no hay KPIs ni línea base. "Entregar valor en semanas" necesita un instrumento: ¿qué métrica de negocio se mueve, en cuánto, medido cómo? Sin eso, la Fase C no es demostrable ante el CEO; es una promesa.

**d) Solapamiento y redundancia.**
Los pasos 12–15, 26–29 y buena parte de la Parte III dicen cosas similares con distinto nivel de detalle. El documento ganaría claridad con una poda: una sola fuente de verdad por tema, con referencias cruzadas. En Obsidian esto es natural: notas atómicas con links, en vez de un monolito de 39 secciones.

---

## 2. La brecha ideal vs real (la pregunta central)

| Dimensión | Estrategia ideal | Estado en tu documento | Brecha |
|---|---|---|---|
| Stack backend | Decisión cerrada con evidencia del piloto | Hipótesis Spring Boot → migración de simpatía hacia Django | Falta el piloto que la decida; Django arrastra conflicto con 11g XE (ver §3) |
| Estrategia BD | Modelo explícito antes de modernizar datos | Oracle se mantiene "estable" indefinidamente | No registrado que 11g XE es EOL, limitado (11GB/1CPU/1GB RAM) y con impuesto de compatibilidad |
| Relaciones sin FK | Patrón viable como ACL temporal, con reglas | Mencionado como opción (SQLAlchemy section) | Faltan las reglas de operación: quién escribe, auditoría de huérfanos, fecha de vencimiento de la deuda |
| Modelo relacional | Profiling + saneamiento antes de FK | Bien definido (paso 3) | Postergado por Intelligence-First: falta al menos un *data quality audit* ligero previo al Semantic Layer |
| Pruebas | Characterization + diferencial con tolerancias | Bien planteado conceptualmente | Falta el instrumento: harness, dataset dorado, umbrales de equivalencia, métricas por gate |
| Datos de prueba | Snapshot sanitizado + casos dorados | No mencionado | **Hueco crítico**: sin esto, no hay characterization testing serio |
| NFRs | Performance baseline, disponibilidad, RTO/RPO | Ausente | Hueco |
| Seguridad | AuthN/Z del nuevo backend; reglas para tools | Mencionada genéricamente | Falta política de exposición MCP (read-first, allowlists, auditoría) |
| Reporting | Plan para los 102 Jasper | Inventariado, sin plan de reemplazo | Hueco: varios son documentos fiscales/legales, no reemplazables por BI |
| Equipo/capacidad | Modelo de quién ejecuta y cuánto | Item 5 de la Parte II (prioridad baja) | Subestimado: condiciona todo el cronograma |
| Observabilidad | Logs/métricas/trazas del nuevo y del legacy | Ausente | Necesaria para gates y shadow mode |
| Ambientes | Dev/staging con copia Oracle | Ausente | Necesario antes de escribir la primera línea |
| Rollback | Runbook por gate | Ausente | Un gate sin reversa es una apuesta, no un control |
| Gobernanza | ADRs, versionado del dossier | Ausente | El dossier se pudre si no es un artefacto vivo |

**Lectura de la tabla:** la brecha no es conceptual, es de *ejecución y gobernanza*. Tienes el "qué" y el "por qué" mejor resueltos que la mayoría; te falta el "con qué instrumentos" y "quién y cuándo".

---

## 3. La decisión Django: análisis honesto

### 3.1 Por qué Django es defendible

- Productividad muy alta para CRUDs, formularios, tablas y workflows administrativos — que es exactamente el 80% de una aplicación de clínica dental.
- ORM maduro, migraciones, admin generable, DRF para APIs, ecosistema enorme de talento.
- Coherente con tu apuesta por IA: Python es el ecosistema natural de LangChain, pandas, scikit-learn.
- Encaja con tu hipótesis de "AI-Augmented Refactoring": el mismo lenguaje para el agente y para el producto reduce fricción.

Si el piloto calibra y Django gana en evidencia, adelante. La decisión debe ser del piloto, no de la simpatía — y tu propio documento lo dice (paso 14). Solo ten presente que cambiar de Java a Python es una dimensión adicional de cambio (lenguaje + ecosistema + mentalidad), y tu principio de "una dimensión crítica a la vez" pesa aquí. Spring Boot + Vue hubiera conservado el lenguaje; Django cambia dos dimensiones a la vez. No es un veto, es un costo que debes registrar en tu ADR.

### 3.2 El problema que el documento no registra: Django moderno + Oracle 11g XE

Hechos verificados (septiembre 2026):

- Django 2.2 soporta oficialmente Oracle **12.1+**; las versiones recientes de Django (4.2 LTS, 5.x) requieren Oracle **12.2+ / 19c**. Oracle 11g quedó fuera del soporte oficial del framework hace años. Puede *funcionar* con acomodos, pero estarás construyendo sobre una combinación no soportada.
- El driver moderno `python-oracledb` opera en *thin mode* (sin clientes Oracle) solo contra Oracle **12.1+**. Para 11g requiere **thick mode** con Oracle Instant Client 19+, lo que reintroduce dependencia nativa en tu runtime — exactamente el tipo de acoplamiento que quieres eliminar.
- Oracle 11g XE además tiene límites duros (~11 GB de datos, 1 CPU, 1 GB RAM) y está fuera de soporte/párcheo desde hace años.

**Conclusión:** tu inclinación actual es internamente inconsistente tal como está formulada. "Backend nuevo en Django moderno" + "Oracle 11g XE sin tocar por años" genera una tensión creciente: cada versión nueva de Django, del driver, de cualquier herramienta del ecosistema Python, pagará un impuesto de compatibilidad con 11g. Ese impuesto es exactamente el tipo de deuda técnica que tu documento critica.

### 3.3 Las tres salidas posibles (y una recomendación)

**Salida 1 — Django contra Oracle 11g con thick mode y acomodos.**
Funciona, pero: combinación no soportada oficialmente, dependencia nativa (Instant Client), modelos Django con `managed=False` contra esquema ajeno, y deuda registrada desde el día 1. Viable solo como puente corto y explícito.

**Salida 2 — PostgreSQL entra primero por el lado del nuevo desarrollo (analítico + piloto), Oracle sigue operando.**
Django vive contra PostgreSQL (combinación de primera clase, thin mode, sin clientes nativos). Oracle se mantiene como sistema operacional intacto, alimentando por ETL programado un almacén PostgreSQL que sirve (a) la capa de inteligencia y (b) el dominio del módulo piloto en modo lectura. La migración operacional completa queda para después, cuando el piloto haya demostrado el camino. **Esta salida resuelve además tu duda de BD con elegancia: PostgreSQL no llega como "migración de Oracle" (gran, riesgosa) sino como "plataforma del nuevo" (pequeña, reversible).**

**Salida 3 — Quedarte en SQLAlchemy + FastAPI contra Oracle si insistes en Oracle primero.**
Elimina el problema Django/11g pero sacrifica la productividad del framework completo y mantiene el impuesto 11g para siempre.

> **Recomendación: Salida 2.** Es la única que hace compatibles tus tres inclinaciones (Django, MCP, Oracle-temporal) sin deuda silenciosa. Y es fiel a tu propio principio de Intelligence-First: PostgreSQL entra por la puerta de la inteligencia, no por la de la cirugía mayor.

### 3.4 Si usas Django contra esquema legacy (Oracle o PostgreSQL): las reglas del juego

Independientemente del motor, declarar relaciones en el ORM sin FK en la BD es un patrón válido — es literalmente tu Anti-Corruption Layer del paso 18. Pero requiere reglas explícitas:

1. **`managed=False` en todos los modelos legacy.** Las migraciones de Django nunca tocan el esquema viejo. Las tablas nuevas del piloto sí pueden ser gestionadas.
2. **Toda tabla necesita PK declarada en el modelo.** Django exige una primary key; en tablas legacy sin PK usable, designa el campo real (ROWID u otro) y documéntalo.
3. **Relaciones declaradas solo como "lectura semántica".** `ForeignKey(..., db_constraint=False)` te da el JOIN sin crear constraint en BD.
4. **Las escrituras del piloto pasan solo por el nuevo backend**, nunca por SQL manual, y envueltas en transacciones que validan integridad en aplicación.
5. **Auditoría periódica de huérfanos** (queries programadas) para el dominio del piloto, mientras la deuda persista.
6. **Fecha de vencimiento registrada:** esta deuda muere cuando el dominio migra a PostgreSQL con FK reales. Sin fecha, se convierte en la próxima década de ambigüedad.
7. **Funciones PL/SQL (get_edad, get_comuna_pcte, etc.) se envuelven** en funciones propias del ORM (Func/expressions) para que el día de la migración cambien de implementación en un solo punto.

---

## 4. MCP: el matiz que necesita tu documento

### 4.1 Corrección conceptual importante

Tu formulación "no API tradicional sino JSON-RPC" mezcla dos cosas. MCP (Model Context Protocol) **es** JSON-RPC 2.0 como transporte, pero su valor no es el transporte: es el *contrato semántico de herramientas auto-describibles pensado para LLMs*. JSON-RPC puro no te da nada de eso; y REST no es el enemigo — es el estándar maduro para consumo por aplicaciones. La comparación correcta no es "MCP vs REST", sino **"¿qué consumidores estoy sirviendo?"**:

| Consumidor | Protocolo correcto |
|---|---|
| Agentes de IA / RAG / chatbots | MCP |
| Apps web, móviles, terceros, integraciones | OpenAPI/REST (o GraphQL si aplica) |
| El equipo de desarrollo (exploración) | Ambos |

### 4.2 Por qué MCP como capa principal del core es riesgoso hoy

1. **Madurez:** en autenticación/autorización fina, versionado de contratos, paginación, rate limiting, observabilidad, generación de clientes, testing de contratos y ecosistema de herramientas, OpenAPI lleva una década de ventaja. Construir el core de una clínica sobre el protocolo más joven del menú es una apuesta que tu propio documento no justificaría si fuera honesto consigo mismo (tu principio #1 es reducir riesgo).
2. **Granularidad:** tu Idea 9/10 ("239 helpers = 239 tools MCP") es conceptualmente limpia pero peligrosa: replica 1:1 la granularidad, la semántica de décadas y los defectos del legacy (helpers con SQL de riesgo, sin autorización por contexto de usuario, sin validación moderna). Los LLMs consumen bien tools *gruesas de dominio* ("agenda_del_dia(odontologo, fecha)", "riesgo_cartera(cliente)") y consumen mal — o de forma insegura — catálogos de 239 primitivas.
3. **Escritura:** exponer tools de escritura a un LLM sobre datos clínicos y financieros exige authZ fina, allowlists, confirmación humana y auditoría. Tu documento no tiene aún una política de exposición. Regla sana: **MCP en modo lectura durante las primeras fases**; las escrituras pasan por la API con humano en el loop.

### 4.3 Correcciones puntuales a tu tabla comparativa

- "Requiere CORS" no es una ventaja de MCP: cualquier HTTP consumido desde navegador enfrenta CORS igual.
- "Validación automática por el protocolo" también la tienes con FastAPI/Pydantic + OpenAPI; no es diferencial real.
- "El LLM obtiene las tools disponibles" es cierto, pero no elimina el diseño del contrato: un tool mal diseño es un endpoint mal diseño, solo que ahora lo invoca un modelo.

### 4.4 Arquitectura recomendada: una sola lógica, dos fachadas

```
┌────────────────────────────────────────────┐
│              Service Layer                  │
│   (casos de uso de dominio, validaciones,   │
│    authZ, transacciones, auditoría)         │
└───────┬───────────────────────┬─────────────┘
        │                       │
┌───────▼───────┐       ┌───────▼────────┐
│  MCP fachada  │       │ OpenAPI fachada │
│ (tools gruesas,│       │ (para apps,     │
│  read-first)  │       │  móvil, terceros)│
└───────┬───────┘       └───────┬────────┘
        │                       │
   Agentes IA              Vue / apps
```

El MCP Server de tu documento está bien **como fachada**, mal como *capa de servicios*. Una sola implementación de negocio; dos protocolos de salida. Eso preserva tu visión MCP-First para la inteligencia sin hipotecar el core.

---

## 5. Oracle 11g XE: el elefante que el documento trata como mueble

Tu estrategia de "no migrar Oracle primero" sigue siendo correcta — cambiar motor y aplicación a la vez es multiplicar variables. Pero el documento subestima dos cosas:

1. **"Oracle estable" es relativo.** 11g XE está fuera de soporte, sin parches de seguridad, con límites de 11GB/1CPU/1GB. Es estable funcionalmente y frágil operativamente. Cada mes que pasa, el argumento "no tocar Oracle" se vuelve más débil, no más fuerte — aunque la decisión de *no migrar primero* siga siendo válida.
2. **CDC/integración en XE es limitado.** Sin GoldenGate ni herramientas enterprise, tus opciones realistas para alimentar el Semantic Layer son: ETL programado (Python + oracledb thick), vistas en Oracle, o export periódico (Data Pump). Ninguna es trivial y ninguna aparece planificada en el documento.

**Consecuencias prácticas a agregar al documento:**
- Plan de respaldo/restore **verificado con ensayo real** (no asumido).
- Data Baseline del paso 5 ampliado: no solo snapshot, sino procedimiento documentado de restauración.
- El ETL hacia PostgreSQL analítico debe ser diseñado temprano porque es el cuello de botella real de la Fase B (Expose).
- Registrar explícitamente la contingencia: si Oracle XE falla mañana, ¿cuánto tardan en reponer operación? Eso define tu verdadera urgencia.

---

## 6. Lo que falta agregar al documento (checklist accionable)

1. **ADRs.** Un registro por decisión (Django, MCP, Oracle-temporal, módulo piloto). Formato: contexto → opciones → decisión → consecuencias → condición de reversa → fecha.
2. **Criterios de selección del módulo piloto.** Matriz de puntuación: complejidad de negocio, valor demostrable, riesgo, carácterizabilidad (¿tiene entradas/salidas comparables?), volumen de uso, acoplamiento. Recomendación: un dominio **read-first** como Paciente/Agenda (evita el problema de doble escritura temprano), NO Caja/Contable (dinero real = máximo riesgo para un piloto).
3. **Estrategia de datos de prueba.** Snapshot de producción **sanitizado** (datos de salud: sensibles bajo la Ley 19.628 en Chile; anonimización/pseudonimización obligatoria en ambientes no productivos), más un "dataset dorado" de casos de negocio con outputs esperados. Cómo se refresca.
4. **Harness de pruebas diferenciales.** Definición técnica: cómo se comparan salidas legacy vs nuevas (JSON diff con tolerancias), umbrales de equivalencia por gate, reporte de reconciliación. Este es el instrumento que convierte tus gates de opinión en gates de evidencia.
5. **NFRs.** Línea base de performance del legacy para el dominio piloto, objetivos del nuevo, RTO/RPO.
6. **Política de seguridad del ecosistema MCP.** Read-first, allowlists por tool, authZ por usuario clínico, auditoría de invocaciones, prohibición de tools de escritura en fases tempranas, confirmación humana para operaciones sensibles.
7. **Plan de reporting.** De los 102 templates Jasper: clasificarlos en (a) reemplazables por BI/dashboards del Semantic Layer, (b) documentos legales/fiscales que requieren reimplementación cuidadosa (boletas, informes), (c) muertos.
8. **KPIs de valor para la Fase C.** 2–3 métricas de negocio con línea base: ej. "% de trabajos de laboratorio fuera de SLA", "días de stock restante crítico", "cartera vencida por tramo". Sin línea base no hay demostración de valor.
9. **Capacidad del equipo y modelo económico.** ¿Quién ejecuta? ¿Un dev + IA? ¿Dos? Costo mensual, costo de Oracle, costo evitado.
10. **Observabilidad y ambientes.** Repo, CI/CD desde el día 1, dev/staging con copia Oracle, logs/métricas/trazas del nuevo backend y — al menos básicas — del legacy durante el shadow mode.
11. **Runbook de rollback por gate.** Qué se revierte y cómo, si un gate falla.
12. **Data quality audit ligero previo al Semantic Layer.** No el Frente 1 completo: un perfilado de las 10–15 tablas del dominio inteligencia más valioso, para no construir semántica sobre datos podridos.

---

## 7. Ruta sugerida de inicio (0–90 días)

Coherente con tus tres inclinaciones (Django, MCP, Oracle-temporal) y con tu propia secuencia A–F:

**Semanas 1–2 — Fase 0: fundaciones (sin escribir lógica de negocio).**
Repo, CI, ambientes dev/staging, snapshot sanitizado de Oracle, verificación de respaldo/restore, ADR #1 (Django + PostgreSQL-del-piloto + Oracle operacional), selección del módulo piloto con la matriz del §6.2.
*Gate 0: puedo restaurar Oracle en staging y tengo datos de prueba sanitizados.*

**Semanas 3–6 — Fase 1: caracterización del dominio piloto.**
Extraer del dossier RICH los casos de uso del módulo elegido; escribir characterization tests contra el legacy (o contra sus outputs capturados); definir dataset dorado. En paralelo: esqueleto Django + PostgreSQL, ETL inicial desde Oracle hacia el almacén del piloto (read-only).
*Gate 1: tengo evidencia reproducible del comportamiento actual del dominio.*

**Semanas 7–10 — Fase 2: implementación del dominio en Django.**
Modelos (`managed=False` o tablas nuevas según corresponda), Service Layer, pruebas diferenciales legacy-vs-nuevo corriendo en shadow mode. Sin MCP todavía.
*Gate 2: equivalencia funcional demostrada en el dataset dorado + muestreo real.*

**Semanas 11–13 — Fase 3: primera fachada MCP (read-only) + primer caso de inteligencia.**
3–5 tools gruesas de dominio ("agenda_del_dia", "datos_paciente", "resumen_paciente"), consumidas por un agente. Un solo KPI de negocio con línea base y dashboard mínimo (Laboratorio o Stock son buenos candidatos por su valor perceptible).
*Gate 3: el CEO ve valor medible sin que tocamos la app operacional.*

**Después:** presentar resultados, calibrar estimaciones (tu paso 8 del roadmap), y recién entonces decidir el siguiente dominio y la profundización de PostgreSQL.

**Nota sobre escrituras:** el piloto es read-first a propósito. La primera escritura del nuevo sistema (ej. "tomar hora") introduce el problema de doble fuente de verdad y exige una estrategia de sincronización (outbox, routing por entidad, o cutover por dominio). No lo abordes en el piloto: abórdalo como segundo dominio, con el harness ya existente.

---

## 8. Riesgos principales a vigilar

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Conflicto silencioso Django ↔ 11g XE genera deuda desde el día 1 | PostgreSQL del piloto (Salida 2, §3.3); thick mode solo si es puente explícito y corto |
| 2 | Semantic Layer construido sobre datos no perfilados propaga errores de negocio con autoridad nueva | Data quality audit ligero previo (§6.12) |
| 3 | MCP con granularidad 1:1 de helpers replica el legacy dentro del protocolo nuevo | Tools gruesas de dominio; service layer único (§4.4) |
| 4 | 11g XE falla antes de que exista contingencia | Ensayo real de restore; ETL diseñado temprano; registro de RTO real |
| 5 | El piloto elige el dominio equivocado (Caja) y quema la credibilidad | Matriz de selección; read-first; evitar dinero en piloto 1 |
| 6 | El documento nunca cierra decisiones (tormenta permanente) | ADRs con fecha y condición de reversa |
| 7 | Datos de salud expuestos a ambientes/agentes sin sanitización | Anonimización obligatoria; authZ en tools; auditoría |
| 8 | La línea de inteligencia promete "valor en semanas" sin KPIs y se vuelve demostración vacía | Línea base de 2–3 KPIs antes de la Fase C |

---

## 9. Preguntas duras que el documento aún no se ha respondido

1. ¿Qué pasa con Oracle 11g XE si muere mañana? (RTO/RPO real, no deseado)
2. ¿Quién escribe código los próximos 90 días, y cuántas horas semanales reales tiene?
3. ¿Cuál es el KPI #1 que el CEO aceptará como "valor demostrado"?
4. ¿Qué dominio tiene entradas/salidas suficientemente comparables para caracterizar, y por qué ese y no otro?
5. ¿Quién valida funcionalmente? (Tu propia tabla dice: validación funcional = esfuerzo humano muy alto, riesgo crítico. ¿Quién es ese humano y cuánto tiempo tiene?)
6. ¿Cuál es la condición de reversa de la decisión Django si el piloto la contradice?
7. ¿Qué pasa con los 102 Jasper que son documentos fiscales?
8. ¿Qué herramienta del ecosistema 11g te va a fallar primero: driver, ORM, o el propio XE (11GB)?
9. ¿El Semantic Layer tiene dueño? (Sin dueño, muere como murió la documentación anterior)
10. ¿Qué decisión tomarías hoy si supieras que el proyecto tendrá solo la mitad del presupuesto esperado?

---

## 10. Conclusión

Vas por buen camino — mejor que la mayoría de las estrategias de modernización que se documentan en este tipo de sistemas. Tu ventaja no es la tecnología candidata (Django, Spring, Vue): es el **método** (tres problemas separados, gates con evidencia, caracterización antes de reemplazo, piloto calibrador, IA con validación humana) y el **activo** (dossier RICH con código verificado). Protégelos.

La brecha ideal-real, resumida en una frase: **tienes una estrategia de exploración de nivel avanzado que todavía necesita convertirse en un plan de ejecución instrumentado** — ADRs cerrados, piloto elegido con criterio, datos de prueba, harness diferencial, NFRs, seguridad de tools, plan de reporting, modelo económico y runbooks de reversa.

Y corrige temprano las dos inconsistencias detectadas: la de Django↔11g XE (resuélvela con PostgreSQL entrando por el lado del nuevo desarrollo, no por la migración operacional) y la de MCP↔core (MCP como fachada de inteligencia sobre un service layer único; OpenAPI para el resto; tools gruesas, read-first).

> Frase de trabajo sugerida para la siguiente iteración del documento:
> *"Un dominio por vez, con evidencia de equivalencia, datos de prueba sanitizados y decisiones registradas como ADR. PostgreSQL entra por la inteligencia, MCP por la fachada, y Oracle se queda quieto hasta que la evidencia diga lo contrario."*

---

### Fuentes técnicas consultadas

- Django — Databases (soporte oficial de versiones Oracle): https://docs.djangoproject.com/en/6.1/ref/databases/
- python-oracledb — Thin mode requiere Oracle 12.1+; Thick mode para 11g: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html
- python-oracledb — feature matrix Thin/Thick: https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_b.html

