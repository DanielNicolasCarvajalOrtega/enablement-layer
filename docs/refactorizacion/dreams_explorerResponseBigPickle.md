# BigPickle — Lectura crítica y reencuadre operativo de DREAMS Explorer

> **Documento analizado:** `dreams_explorer.md` (DREAMS_02 · Agosto 2026)
> **Fecha de respuesta:** Septiembre 2026
> **Autor:** BigPickle (opencode/big-pickle)
> **Naturaleza:** Veredicto honesto + cierre de decisiones + plan de arranque. No es otra tormenta de ideas: es una opinión directa sobre qué hacer el lunes.

---

## 0. Resumen ejecutivo (la respuesta en 10 líneas)

1. **Vas por buen camino.** El documento está muy por encima del promedio de "planes de modernización". El reencuadre de los pasos 30-39 (el legacy no es el enemigo; el dolor real es explotar el conocimiento) es profesional y está bien argumentado.
2. **Pero el documento ya cumplió su función.** Es un documento de *exploración* de 1933 líneas y 39 pasos. Lo que te falta no es más análisis: te falta **cerrar decisiones y ejecutar un piloto**.
3. **El riesgo más grande ahora es la parálisis de análisis.** El documento ofrece tantas estrategias "válidas" con tantas salvedades que es posible quedarse explorando para siempre. Hay que elegir un camino principal y uno de contingencia.
4. **Empieza por los datos, en modo lectura.** No por la BD (no migres), no por toda la app (no reescribas). Empieza por *profiling + semántica*: convertir el "0 FK" en un informe de salud de relaciones real, y construir una capa de lectura limpia.
5. **Sí a tu decisión emergente: Django + MCP (JSON-RPC) + Oracle sin tocar.** Es coherente y viable. Solo hay que afinar tres cosas: (a) dos superficies de API, no una sola, (b) reglas claras para convivir con las 0 FK, (c) las decisiones ocultas que el documento no cubre (procedures Oracle, escritura, secuencias).
6. **El plano tecno es sólido.** Donde está la brecha real es en *infraestructura de ejecución*: código en control de versiones, instancia del legacy ejecutándose, métricas de uso real, y un "definition of done" para cada gate.
7. **El stack "Oracle primero, PostgreSQL después" está bien, pero conviene añadir una capa barata desde el día 1:** una copia analítica (snapshot) PostgreSQL. No es migración, es un gemelo analítico. De-risquea todo.
8. **Propongo un primer sprint de 30 días con 6 entregables concretos**, uno de ellos un demo de IA sobre cartera vencida para el CEO.
9. **Tu documento debe evolucionar, no morir.** Convertirlo en un ADR + backlog de 90 días con gates con DoD medible.
10. **Frase de trabajo:** *"Entendimiento adquirido; ahora decisión y evidencia."*

---

## 1. Cómo veo tu documento

### 1.1 Lo que está muy bien (y que yo no tocaría)

| Fortaleza | Por qué es real |
|-----------|-----------------|
| **El reencuadre (pasos 30-39)** | Distinguir Problema A (legacy), Problema B (modelo de info) y Problema C (explotación del conocimiento) es la decisión conceptual más inteligente del documento. El C no exige resolver A y B. |
| **El dossier como Knowledge Graph** | Ya no es "documentación": es un grafo de conocimiento human-readable (y, con los 689 RICH, machine-readable). Es el activo diferenciador de todo el proyecto. |
| **Los 689 archivos RICH con código incrustado** | Esto es estadísticamente raro. La mayoría de los legacy no tiene ni inventario. Tú tienes el *código completo* documentado. La Fase A (Understand) está genuinamente cerrada. |
| **"Una dimensión por vez" + gates** | El antídoto correcto contra el Big Bang. Los 6 gates con "evidencia reproducible, no opinión" es la disciplina que va a salvar el proyecto. |
| **Characterization testing / Shadow mode** | Es la única forma honesta de demostrar equivalencia. Sin esto, todo lo demás es fe. |
| **MCP sobre 239 helpers** | Los helpers ya SON la API no documentada del sistema. Formalizarlos como tools es bajo riesgo y alto valor. Muy bien visto. |
| **La honestidad sobre lo que no se sabe** | Sección 11 ("el análisis es sobre el dossier, no sobre el código") es la marca de un analista serio. |

### 1.2 Dónde se queda corto (crítica constructiva)

1. **Es un documento de pensamiento, no de decisión.** En la sección 27, casi todo está en "hipótesis" o "aún no decidido". Un documento así debe tener *una* columna "decisión" que se actualice con fecha. Hoy el que lo lea (tú, un consultor, un LLM) no puede saber qué aplicar.
2. **La arquitectura escrita y la arquitectura emergente ya no coinciden.** El documento recomienda Spring Boot + Vue + REST/tradicional. Tu conversación actual es Django + MCP + JSON-RPC + "mantener Oracle tal cual". Ese cambio mayor todavía no está reflejado en el documento, y eso genera que *cada asistente que consulte el documento* razonará desde el stack viejo.
3. **"Oracle → PostgreSQL" sigue siendo tratado como destino casi obligatorio.** Es una hipótesis razonable, pero no está demostrada como necesaria. Podrías terminar *nunca* migrando el operacional y teniendo PostgreSQL solo como capa analítica. Dejarlo como "decisión pendiente de evidencia" está bien; dejarlo como "jugada maestra" está demasiado afirmado.
4. **Falta el problema de la escritura.** Todo el documento piensa la modernización como si fuera lectura (inteligencia, BI, RAG). Pero la reimplementación de la app requiere *escribir* contra tablas que tienen triggers, procedures y secuencias gestionadas desde el legacy. No hay estrategia de write-path parity. Esto es una decisión oculta enorme.
5. **No hay métricas de uso real.** 268 clases, 439 JSP, 102 templates… ¿pero cuáles están vivos? Sin esto, el módulo "representativo" del piloto se elige a ciegas.
6. **Sin plan para el COMO de la ejecución diaria.** El roadmap del paso 28 termina en "definir roadmap basado en evidencia". Necesita un "qué hago exactamente los próximos 30 días, con qué repos, qué scripts, qué assets".

---

## 2. Tu pregunta directa: ¿por dónde empiezo? ¿BD, app o datos?

**Empieza por los datos — pero como lectura, entendimiento y semántica — y por UN MÓDULO PILOTO acotado, en paralelo. La BD (Oracle→PostgreSQL) NO se toca en el arranque. La app completa NO se reescribe en el arranque.**

| Frente | ¿Tocarlo ahora? | Por qué |
|--------|----------------|---------|
| **Datos (profiling + semántica)** | **SÍ, primero** | Es el denominador común de todo lo demás: MCP, ORM con relaciones, IA. Convertir "0 FK" en un informe de salud numérico es de bajo riesgo y despeja todas las decisiones posteriores. |
| **Capa de lectura (MCP + ORM)** | **SÍ, primero** | Es tu prueba de fuego técnica: ¿puedo mapear estas tablas feas a modelos limpios y exponerlos por JSON-RPC? Se demuestra en semanas con valor real. |
| **App (un módulo piloto E2E)** | **SÍ, pero UNO** | Elegir el módulo de mayor valor y menor acoplamiento, y reemplazarlo de verdad (pantallas incluidas). Es la medida del esfuerzo real que pide el documento. |
| **BD (Oracle→PostgreSQL)** | **NO** | Oracle permanece estable como punto de comparación. Solo añades un "gemelo analítico" Postgres (snapshot) como capa barata de experimentación. |
| **App completa / JSP→Vue masivo** | **NO** | Masterplan anti-reescritura: vuelve a "selective re-platform" (sección 5). |

> **Una frase:** "datos primero como lectura y semántica, app en un módulo piloto, BD al final" — en ese orden.

---

## 3. Tu decisión emergente bajo la lupa: Django + MCP + Oracle con 0 FK

Esta sección es el núcleo de mi aporte. Te la digo sin rodeos: **la combinación es viable y es probablemente la mejor opción para tu situación**. Pero tiene tres condiciones que hay que gestionar.

### 3.1 Django: es la elección correcta, y te digo por qué

El documento elegía Spring Boot para "reducir variables". Ese argumento era válido cuando el equipo pensaba en Java. Pero tu realidad emergente es: **equipo mínimo (probablemente tú + agentes de IA), fuerte apuesta por IA, y una BD envejecida**. Bajo esa realidad, Django gana por varias razones concretas:

- **Productividad bruta en CRUD y admin:** un sistema de clínica (fichas, citas, pagos, stock, laboratorio) es 80% CRUD + workflows. Django Admin te da pantallas de administración editables *gratis*, de calidad, seguras, con audit, mientras construyes las pantallas propias. Eso es oro para un equipo pequeño.
- **ORM maduro que soporta Oracle nativamente** (`django.db.backends.oracle`) con `python-oracledb` en modo thin (sin instalar clientes Oracle). Con modernas versiones de Django puedes apuntar el mismo código a Oracle hoy y a PostgreSQL mañana.
- **El "schema-as-code" de Django (migrations)** es la herramienta perfecta para tu plan de "las relaciones se declaran en el código": los modelos Django *son* el contrato. (Detalle en 3.4.)
- **Ecosistema de IA de primera clase:** LangChain, LlamaIndex, FastMCP, agentes, RAG... todo es de primera en Python. Y el MCP Server queda en el mismo lenguaje y repo que la app (compartes modelos y helpers). Con Spring tendrías la capa IA en Python igual, pero partida en dos mundos.
- **Los volúmenes de una clínica** (miles, no millones de registros) no exigen la maquinaria de Spring Boot.

**La única objeción seria es el cambio de lenguaje** — que el documento correctamente marcó como la variable de mayor salto. Mi respuesta: el riesgo de cambio de lenguaje se mitiga con lo que ya decretaste — *mantener Oracle y hacer un módulo piloto antes de comprometer el stack*. Si el piloto sale bien en Django, el salto quedó pagado. Estás controlando la dimensión de lenguaje con el gate del piloto. Correcto.

### 3.2 MCP como API "casi única": sí, pero con dos superficies

Tu intuición de MCP sobre REST tradicional es buena para *agentes de IA* e *integraciones machine-to-machine*. Pero hay que evitar un error común: **hacer de MCP la única superficie de la aplicación web**.

Matiz técnico honesto:

| Consumidor | ¿MCP/JSON-RPC es lo natural? | Alternativa |
|-----------|------------------------------|-------------|
| Agentes LLM / RAG / copilotos | **Sí, nativo.** MCP fue diseñado para esto. | — |
| Integraciones server-to-server | **Sí, funciona.** JSON-RPC 2.0 sobre HTTP/Streamable está bien. | REST |
| La web de la clínica (pantallas CRUD) | **Fricción innecesaria.** El frontend necesita endpoints de datos por recurso, sesiones, auth, error codes estándar. | Django views/JSON + templates/HTMX, o DRF liviano solo donde haga falta |
| App móvil futura | Funciona, pero REST es más estándar para móvil. | REST |

**La arquitectura que te propongo — "un servicio, múltiples superficies delgadas":**

```
Django Domain / Service Layer (modelos + helpers 239 portados aquí)
        │
        ├── Django views / JSON  → la web (JSP nuevo, templates+HTMX o Vue puntual)
        ├── MCP Server (FastMCP) → agentes de IA, copiloto, integraciones (JSON-RPC 2.0)
        └── (futuro) REST liviano → app móvil, terceros
```

Nunca dupliques la lógica: el service layer es único. Las superficies son adaptadores de ~50 líneas. Esto conserva tu amor por MCP (que es correcto para el lado IA) sin hipotecar la web.

> Nota técnica: los MCP Servers con FastMCP exponen los `tools` como JSON-RPC 2.0 (método `tools/call`), como ya está bien esquematizado en tu documento. Solo puntualizo: esto es maravilloso para LLMs; para la UI de la clínica que manipula edad→botón→tabla, un endpoint por recurso Django es más simple.

### 3.3 Oracle sin FK + ORM con relaciones declaradas: viable, con 4 reglas

Tu idea de "mantener Oracle tal cual, incluso sin relaciones explícitas, y declarar las relaciones en los programas con ORM" es **una decisión de arquitectura legítima y quizá la más pragmática**. No es "la precaria"; es una postura profesional (los DWH y los sistemas agnósticos de motor hacen esto todo el tiempo: el modelo lógico vive en la capa de aplicación). Pero para que no se vuelva una trampa, aplica estas 4 reglas:

**Regla 1 — La declaración en ORM es una hipótesis, no un hecho. Valídala contra los datos.**
Antes de confiar en cada relación declarada, corre un *reconciliador*: para cada par tabla-columna que declares como FK, ejecuta un `COUNT` de huérfanos. El output es un **"Informe de Salud de Relaciones"**:

| Relación declarada | Columnas | Huérfanos | % | Veredicto |
|--------------------|----------|-----------|-----|-----------|
| FICHAS.NUM_FICHA → PACIENTES.PAC_CODIGO | ... | 12 | 0.02% | Limpia → confiar y luego promover a FK real |
| ... | ... | 3,451 | 41% | Ficción → decisión de negocio antes que cualquier modelado |

Ese informe es el puente entre "0 FK" (problema abstracto) y "qué hago el lunes" (problema concreto). Es además el insumo objetivo para decidir qué relaciones promover a constraints reales más adelante. **No necesitas esperar a tener FKs para avanzar; necesitas saber cuánto miente cada relación.**

**Regla 2 — Modo `managed = False` para las tablas Oracle, y entender qué significa.**
Con `managed = False`, Django no crea/alterea tablas (no harás migraciones destructivas contra el operacional), pero:
- Las relaciones declaradas (`ForeignKey`, `ManyToMany`) **sí generan JOINs correctos en lectura** (`select_related`, `prefetch_related`). Eso es exactamente lo que quieres.
- En **escritura**, Django NO impone ni gestiona integridad, y el borrado en cascada no ocurre en la BD. Toda la integridad de escritura queda a cargo de tu service layer. Esto es una responsabilidad, no un bug: debes centralizar la escritura en servicios que validen explícitamente ("no crear cita sin ficha activa") en vez de repartirla en las vistas.
- Las secuencias Oracle: modelos que insertan con `Sequence` gestionan el autoincremento; pero en tu caso las secuencias probablemente las dispara código del legacy o triggers. **Antes de escribir contra cualquier tabla, mapea cómo se genera su PK hoy** (sequence, trigger, prepend de código). Eso está en `raw_db_metadata`.

**Regla 3 — Las funciones Oracle (get_edad, get_comuna_pcte) se encapsulan en el dominio, no se replican.**
Tu propio ejemplo lo muestra bien: `get_edad(PAC_FEC_NACIMIENTO)` y `get_comuna_pcte(ficha)` son reglas de negocio viviendo en Oracle. Opciones:
- (a) Llamarlas vía `func.get_edad(...)` en el ORM (como tu ejemplo) — cero cambio, las tratas como stored functions del motor. Perfecto para la etapa Oracle.
- (b) Migrarlas a Python cuando llegue PostgreSQL.
La clave es que el ORM (y después el dominio) las trate como un *concepto de dominio* (`edad_paciente`), no como "SQL raro de Oracle". Eso es ya práctica de separación de modelo físico vs modelo lógico — que tu documento defiende en el punto 18. Continúa con esa lógica.

**Regla 4 — EAV y columnas sobrecargadas rompen al ORM: ahí entra la capa semántica.**
Mencionas EAV en tu documento (dato 31). Las tablas EAV (entity-attribute-value) y las columnas polisémicas no se modelan bien con `ForeignKey` clásica. Para esas, dos caminos:
- Modelar la pieza EAV en Django con un modelo genérico (`Atributo(clave, valor, ficha_id)`) — fiel pero incómodo.
- **Aplastarla en la capa semántica**: un modelo analítico "aplanado" (paciente con columnas ya resueltas) alimentado por views/materializaciones. Eso es exactamente tu "Semantic Data Layer" del paso 33. No obligues al ORM a entender EAV; haz que la capa semántica lo resuelva una sola vez.

### 3.4 Tu ejemplo "SQLAlchemy" vs la decisión Django: no los mezcles sin frontera

En el documento, la sección "Versión REST API con ORM (SQLAlchemy)" es un buen demo, pero ojo: **si la app es Django, el ORM es el de Django**. No necesitas SQLAlchemy en la app (dos ORMs en el mismo proceso = dos mundos de sesiones, IDs y convenciones).

Donde SÍ podría tener sentido SQLAlchemy es en **la capa de pipelines/ELT analítica** (copy de Oracle a Postgres, la capa semántica), donde vas a operar con pandas/polars/SQL crudo y no quieres la maquinaria de Django. Regla simple:
- **App de negocio (MCP + web): Django ORM.**
- **Pipelines analíticos / ELT / semántica:** SQLAlchemy (o SQL + polars) en procesos separados.

Frontera clara por proceso y por responsabilidad. Si lo mantienes, lo demás funciona.

### 3.5 La decisión oculta que tu documento no cubre: los procedures / triggers / "tramites" de Oracle

Esto es lo que más le falta a tu documento, y es **crítico**. Tú dices en el punto 1 que Oracle contiene "procedures, trámites, triggers" con reglas de negocio. Si una parte sustancial del negocio vive en PL/SQL:

- Un reescritura a Django que ignore los procedures los *rompe*. Un reescritura que los *replique* en Python duplica trazabilidad y riesgo.
- La jugada intermedia: **durante la fase de chatarras, exponer los procedures Oracle tal cual vía MCP tools** (el MCP Server llama `BEGIN pkg.tratamiento_insert(...)`), exactamente como el legacy los llama. Y solo portar a Python la lógica de un módulo **en el momento en que ese módulo se estrangule y su procedure correspondiente se retire**.
- Esto significa: el inventario de PL/SQL (packages, procedures, triggers con su lógica) es tan prioritario como el inventario de Java/JSP. Falta en tu "Hidden Logic Inventory" (dato 10) una línea explícita de *procedures que serializan flujos de negocio* y qué reglas contienen. Es adentro del **"cuál es la frontera de qué secribe donde"** para la escritura.

---

## 4. Brecha entre la estrategia ideal y la real

### 4.1 El cuadro honesto

| Dimensión | Ideal (según tu documento) | Real hoy | Brecha |
|-----------|---------------------------|----------|--------|
| **Entendimiento** | Assessment + dossier + fase A cerrada | ✅ Verdadero. Es tu mayor fortaleza. | Baja |
| **Decisiones** | Un camino principal cerrado | Todo sigue en "hipótesis" | **Alta — es la brecha #1** |
| **Fuentes de verdad** | Código real bajo control de versiones | 689 RICH (copias) sin SVN, sin builds | **Alta — impide CI, diff, ejecutar legacy** |
| **Stack** | Coherente con la decisión | El doc dice Spring+Vue; la conversación dice Django+MCP | **Alta — hay que reconciliar** |
| **Equipo / capacidad** | Definido | Sin definir (¿1 dev + IA? ¿equipo?) | Media (impacta todo el cronograma) |
| **Métricas de uso** | Foco en el 20% que importa | Sin datos de qué usan los usuarios | Alta — sin esto el piloto se elige a ciegas |
| **Gates** | Definidos | Definidos como concepto, sin DoD medible | Media |
| **Estrategia ante procedures/triggers** | No mencionada | No existe | **Alta — riesgo real de romper el negocio** |
| **Write-path (escritura nueva)** | No mencionado | No existe | Alta |
| **Presupuesto/vendor** | "Oracle caro" como driver | Sin números para el CEO | Media |
| **Ejecución diaria** | Roadmap de 10 pasos | Suena como investigación, no como sprint | Alta |

### 4.2 Los 6 huecos concretos que más pesan

1. **No hay repositorio de código de verdad.** Los RICH sirven para leer, no para correr ni diffear. *Sí o sí*: recuperar el SVN (o al menos exportar el código a un git privado) es el habilitador de CI, de characterization tests ejecutables y de control de cambios.
2. **No hay instancia ejecutable del legacy.** Para characterization/shadow testing necesitas el JSP+Payara corriendo y capturando outputs reales. Sin eso, la equivalencia funcional es teórica.
3. **No hay métricas de uso.** Elige el módulo piloto con datos (qué pantallas se frecuentan, qué queries son pesadas, qué tablas más traficadas). Evita adivinar.
4. **La "decisión" del stack no está cerrada en el papel.** Django+MCP+Oracle-first es tu dirección emergente; el documento todavía dice otra cosa. Hay que refundir el documento con las decisiones tomadas, con fecha y firma.
5. **No hay definición de "listo" para cada gate.** "Nueva app funciona sobre Oracle" (Gate 1) sin % de casos cubiertos, sin umbral de equivalencia, sin criterio de aceptación no es un gate, es un deseo.
6. **No hay un plan de riesgo de negocio.** Si un procedure central falla durante la convivencia, ¿qué pasa? Un runbook de contingencia y un feature flag maestro ("volver a legacy en 5 minutos") debería ser parte del diseño desde el día 1.

> **Veredicto de brecha:** la brecha NO está en el *qué* (tu estrategia es correcta). Está en el *cómo lo sostengo y lo ejecuto* (infra de código, instancia, métricas, decisiones) y en *una* decisión estratégica no pensada (procedures Oracle / write-path). Es una brecha de ejecución, no de visión.

### 4.3 El riesgo nº 1: nunca salir de Fase A

Lo digo con honestidad: documentos como el tuyo son tan buenos que el riesgo más probable no es diseñar mal, es **seguir diseñando**. Fase A está cerrada. Todo lo que hoy produce más análisis tiene rendimiento decreciente. Lo que produce valor es un *piloto que falle rápido y enseñe*. Si no tienes un entregable con el CEO en 30 días, el proyecto morirá de éxito documental.

---

## 5. Ideas para abrir la mente (aportes frescos, no repetidos)

Estas son aportaciones que *no vi* en tu documento ni en las respuestas habituales. Algunas son deliberadamente provocadoras.

### Idea A — El "gemelo analítico" PostgreSQL (stop pensando en migración, empieza a pensar en copia)
En vez de "¿cuándo migramos Oracle→PostgreSQL?", pregúntate "¿cuándo montamos una **copia analítica** PostgreSQL de las tablas que importan?". Un snapshot diario (incremental por fecha) de las ~30 tablas operativas clave te da:
- Un banco de pruebas para toda la línea de inteligencia (BI, RAG, pipelines) **sin tocar Oracle**.
- Un entorno de desarrollo seguro para los modelos Django y las migrations futuras.
- La "prueba de fuego" de la migración en miniatura: si los ELT funcionan, la migración de un módulo es solo cambiar de origen.
- De-risquea la muerte súbita de Oracle XE (es 11g, des-soportada hace años, single instance, límite 11GB).

Esto **no es** migrar la BD primero: Oracle sigue siendo el maestro operacional. Es separar "datos" de "cómputo analítico". Muy dolor-1/aumur pequeña.

### Idea B — Schema-as-code: un solo contrato, dos motores
Con Django esto es elegante de verdad:
- Los modelos Django con `managed=False` sobre Oracle = el mapa lógico (tu plan actual).
- Cuando un dominio esté validado (Regla 1 de la sección 3.3), defines el mismo modelo con `managed=True` apuntando a PostgreSQL = el esquema futuro.
- La migración de un módulo se vuelve: *correr `migrate` en Postgres, copiar datos, validar, flipar el flujo*.
Un solo archivo de modelos es la fuente de verdad. Ya no "definimos la BD en SQL nuevo": la definimos en el ORM. Esto convierte "migrar la BD" en "publicar el esquema que ya escribimos". **El documento (dato 16: no migrar primero) y esto son perfectamente compatibles.**

### Idea C — Selective re-platform, no reescritura
Cuestiono el supuesto de "la app necesita modernizarse profunda". Quizá del 100% de flujos:
- **20% genera el 80% del valor** (agenda, odontograma, cobros, laboratorio) → se reimplementan.
- **30% es funcionalidad de relleno que trabaja aceptablemente** → se envuelve tras MCP tools y se deja como está (tu dato 39: "que el resto muera lentamente").
- **50% posiblemente está muerto** → se documenta y se archiva.
El "inventario de uso real" (hueco 4.2) te dice exactamente qué pertenece a cada grupo. Una **tecnología de envoltura** (MCP tools = 239 helpers = 239 comportamientos de negocio usables por agentes y apps) hace que "no reescribir" deje de ser un pecado y se vuelva una estrategia legítima.

### Idea D — El "DentWeb Copilot" como primer producto que se enseña
Fusiona tu idea 8 (AI Knowledge Agent) con tu capa MCP:
- RAG sobre los 689 RICH → responde "¿cómo funciona el cobro de laboratorio?".
- MCP tools sobre Oracle → responde "muéstrame la lista de pacientes con más retraso de pago".
Un único chat que contesta preguntas de *código* y preguntas de *datos* vivos. Es el mejor vehículo para vender el proyecto al CEO y a los médicos: es tangible, no prometen una arquitectura, prometen una respuesta.

### Idea E — Shadow tests en el test runner de Django (equivalencia continua)
Construye un script que, para el módulo piloto: corre la query legacy y la query nueva sobre la MISMA Oracle con los mismos parámetros, compara resultados y reporta divergencias. Eso es tu "Shadow Mode" (idea 7), pero acomodado al django test runner como una suite regular que corre en CI. La equivalencia deja de ser un evento puntual y pasa a ser *un test que corre cada vez*.

### Idea F — Entregables "package-of-value" por módulo
Cada módulo que estrangules debe salir como una **release visible para el usuario** ("nueva agenda para recepción", "nuevo panel para el doctor"), no como un "módulo de refactorización completado". Esto mantiene al negocio del lado tuyo y te da feedback real de aceptación, no solo pruebas unitarias.

### Idea G — El frontend lo decide el odontograma, no una preferencia estética
El documento siente simpatía por Vue. Mi matiz: la UI de una clínica es 80% formularios y tablas servidor-renderizadas (Django templates + HTMX bastan y sobra), y hay **un** componente genuinamente interactivo que justifica un SPA/Painter: el **odontograma** (mapa dental clicable). Decisión correcta probable: **templates + HTMX para el CRUD; Vue/Canvas solo donde la interacción lo exige**. Más rápido de construir, menos deuda frontend, y evitas "reescribir las 439 JSP a Vue" (reescritura innecesaria).

### Idea H — Empieza el piloto por el módulo más "aburrido", no el más "sexy"
El instinto dice "el módulo que impresione al CEO". El piloto debe ser el que **maximice señal y minimice riesgo**: usado diariamente, de complejidad media, datos limpios de leer, y sin depender del peor spaghetti. Si acumulas dos módulos candidatos y corres el Informe de Salud de Relaciones sobre ambos, la evidencia te elige el módulo por ti.

### Pushbacks a supuestos sagrados (para abrir tu mente)

| Supuesto del documento | Mi pushback |
|-----------------------|-------------|
| "Oracle→PostgreSQL es la jugada maestra" | Quizá nunca migres el operacional; PostgreSQL como capa analítica/copia puede ser suficiente. La licencia de Oracle como *driver* pierde fuerza si usas una copia analítica en Postgres y dejas Oracle 11g trabajando bajo el servidor. |
| "El frontend debe ser moderno (SPA)" | El 80% no necesita SPA. Over-engineer frontend es la forma más común de desperdiciar presupuesto en Apps de clínica. |
| "MCP es la API del futuro" | MCP es el estándar para *agentes*, no (todavía) para apps. Dos superficies delgadas sobre un service layer es lo robusto. |
| "Hay que limpiar el modelo de datos antes de todo" | El modelo perfecto es el enemigo del valor temprano. La capa semántica aplana el EAV sin que el operacional cambie una columna. |
| "Hay un solo camino estratégico" | Tienes dos líneas (inteligencia + modernización) que avanzan a velocidad distinta. Esa dualidad es tu ventaja, no tu indecisión. |

---

## 6. Plan de arranque concreto (los primeros 90 días)

Este es el puente entre lo que tienes documentado y lo que tienes que hacer. Es un plan de *ejecución*, con entregables medibles.

### Horizonte 0 — Días 1 a 30 (construir la base de evidencia)

| # | Entregable | Criterio de éxito medible | Costo estimado |
|---|-----------|----------------------------|----------------|
| 1 | **Repositorio de código de verdad** | Exportar SVN (o copiar fuentes) a git privado; los 689 RICH verificables contra el repo (diff de 3 archivos da 0). | 3-5 días |
| 2 | **Instancia legacy ejecutable** | JSP+Payara+Oracle corriendo en local/docker; login de prueba; 1 flujo E2E grabado (outputs capturados). | 5-10 días |
| 3 | **Perfil de uso real** | Tabla de top-JSPs usados, top-tablas traficadas, queries pesadas (AWR/auditor general o logs del app server). | 3-5 días |
| 4 | **Informe de Salud de Relaciones** | Script que profile 6-8 relaciones clave de 2 módulos candidatos; reporte numérico de huérfanos. | 4-6 días |
| 5 | **Esqueleto Django + Oracle + MCP** | App Django 5.x conectada a Oracle (python-oracledb thin); MCP Server con 5-10 tools de los 239 helpers documentados; `tools/list` funcionando. | 5-8 días |
| 6 | **Demo de inteligencia al CEO** | "Cartera vencida": risk-score por cliente con MCP tool + RAG sobre dossier. Frase: "¿qué debería preocuparme?" | 4-6 días |

> **Regla del horizonte 0:** nada de esto toca Oracle operativo (solo lecturas SNAPSHOT/idempotentes) ni toca la app legacy. Riesgo técnico ~cero. Se carga el esqueleto que todas las demás fases van a usar (repo + instancia + perfil + esqueleto Django/MCP).

### Horizonte 1 — Semanas 5 a 16 (el gate del piloto, que decide el stack)

| # | Entregable | Criterio de éxito |
|---|-----------|-------------------|
| 1 | Seleccionar módulo piloto con el Informe de Relaciones + perfil de uso (no por simpatía) | Módulo elegido con evidencia documentada |
| 2 | Modelos Django `managed=False` del módulo + relaciones declaradas validadas por el informe | 100% de relaciones entendidas; huérfanos clasificados |
| 3 | Characterization/shadow tests: query legacy vs query nueva en CI | Suite verde con umbral acordado (ej: 100% de casos conocidos) |
| 4 | Estrangular 1 pantalla real detrás de flag (Feature Flag: misma URL, el usuario ve el nuevo) | Usuarios reales operando el nuevo sin conocerlo o con A/B |
| 5 | MCP tools del módulo completas (de los helpers que toca) | Cada tool con docstring, schema y tests |
| 6 | Médico: horas humanas, tokens, iteraciones de IA, % reutilización del legacy | **Esto responde la pregunta de stack del documento (paso 28 #8)** |

> **La decisión "seguir Django a todo el proyecto" o "re-evaluar" se toma al final de este horizonte con los números del piloto.** Nada de decidir el stack completo en abstracto: los números del piloto deciden.

### Horizonte 2 — Trimestre 2 y 3 (escalar con memoria)

| # | Entregable | Criterio de éxito |
|---|-----------|-------------------|
| 1 | Gemelo analítico PostgreSQL (snapshot diario de las tablas clave) | ELT estable; tablas listas para BI |
| 2 | Semantic Data Layer sobre el gemelo (aplanar EAV, vistas analíticas amigables) | Text-to-SQL/LLM consume el modelo semántico, no las 100 columnas |
| 3 | Rollout módulo a módulo (por release de valor, no por "tarea técnica") | 1-2 módulos más estrangulados |
| 4 | División de la lógica PL/SQL crítica ("tramites"): portar con cada módulo que muera | Cero procedures críticos huérfanos sin dueño |
| 5 | Decidir si se promueven FKs en Oracle o se deja "Oracle sin tocar, Postgres limpio" | Decisión documentada con evidencia de huérfanos |

### Regla transversal de todo el proyecto

> **Un demo de valor de negocio cada 4-6 semanas**, sin excepción. La línea de inteligencia (barata, low-risk) financia la paciencia de la línea de modernización (cara, lenta). Eso es tu ciclo virtuoso del paso 38 hecho operativo.

---

## 7. El siguiente paso del documento (convertirlo en decisión viva)

No dejes `dreams_explorer.md` congelado como "documento histórico de 39 pasos". Propongo evolucionarlo en **dos artefactos**:

1. **`estrategia_decidida.md` (nuevo, corto, vivo)**:
   - Stack decidido: Django + MCP/JSON-RPC + Oracle-first con relaciones declaradas (managed=False) + gemelo analítico Postgres + frontend templates/HTMX + Vue solo para odontograma/dashboards.
   - Secuencia decidida: datos (lectura) → módulo piloto → semántica → roll-out → BD-al-final.
   - 6 gates con **DoD medible** (umbrales de equivalencia, % de casos, criterios de aceptación).
   - ADR: por qué no (a la fecha) Spring, por qué no SPA total, por qué no migrar Oracle primero, por qué sí managed=False sin FKs. Cada ADR con fecha y firma.
   - Backlog de 90 días (los horizontes de la sección 6) con dueños.
2. **Actualización mínima de `dreams_explorer.md`**: anotar en sección 27 que las hipótesis Spring/Vue quedaron *desplazadas* por la decisión Django/MCP (con referencia al ADR), para que cualquier lector futuro (y cualquier LLM) trate el stack de forma coherente.

> Sin ese refondeo, cada agente que consultes mañana seguirá tirándote hacia Spring Boot + REST tradicional y te hará perder tiempo. El documento es bueno; la disciplina es *decidir y congelar*.

---

## 8. Cierre

Tu situación no es "estamos al inicio de un proyecto enorme". Es "tenemos el mapa, el contexto y el activo de código documentado; nos falta la expedición". El documento ya respondió las preguntas difíciles (qué, por qué, con qué orden). Lo que queda es responder *"¿qué hago mañana a las 9?"* — y en esta respuesta tienes un plan concreto para eso.

> **Frase de trabajo:** "Entendimiento adquirido; ahora decisión y evidencia. Un módulo piloto que enseñe vale más que otro capítulo de estrategia."

> Y el recordatorio de oro: **el dossier no es documentación: es el mapa del tesoro. No lo dejes dormir** — conviértelo en el copiloto y en el schema del MCP Server esta misma semana, y tendrás valor demostrable antes de que el primer byte de Oracle se mueva.