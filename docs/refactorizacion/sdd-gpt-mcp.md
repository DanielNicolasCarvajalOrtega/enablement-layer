# Plan en las pruebs

Sí, y de hecho lo que describes ya es **una prueba bastante más significativa que simplemente "tengo un MCP funcionando"**.

Lo que estás probando es un **flujo agentic completo**, aunque todavía sea controlado por tu script Python.

### El flujo que tienes ahora

```text
                    ┌─────────────────────┐
                    │       Usuario       │
                    │ "¿Qué ...?"         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        LLM          │
                    │                     │
                    │ Catálogo de Tools   │
                    │        +            │
                    │     Pregunta        │
                    └──────────┬──────────┘
                               │
                     decide tool(s)
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Python Agent     │
                    │                     │
                    │ await tools.xxx()   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    MCP Server       │
                    │                     │
                    │      Tool           │
                    │        ↓            │
                    │   Service Layer     │
                    │        ↓            │
                    │      Oracle         │
                    └──────────┬──────────┘
                               │
                            datos
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Python Agent     │
                    └──────────┬──────────┘
                               │
                         datos + contexto
                               │
                               ▼
                    ┌─────────────────────┐
                    │        LLM          │
                    │                     │
                    │ interpreta datos    │
                    │ genera respuesta    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Respuesta usuario  │
                    └─────────────────────┘
```

Y hay algo especialmente interesante:

> **El LLM no está accediendo directamente a Oracle ni ejecutando SQL.**

Está haciendo:

```text
Pregunta
   ↓
selección de capability
   ↓
Tool
   ↓
datos estructurados
   ↓
razonamiento
   ↓
respuesta
```

Eso está muy alineado con la arquitectura que vienes planteando para el **Enablement Layer**.

---

## Y estás probando dos cosas distintas

Tu prueba "API" demuestra:

```text
Cliente
  ↓
REST API
  ↓
Service
  ↓
Oracle
```

Mientras que la prueba MCP demuestra:

```text
Cliente/Agent
  ↓
MCP
  ↓
Tool
  ↓
Service
  ↓
Oracle
```

Y eso es importante porque te permite validar la idea que veníamos trabajando:

> **La capacidad de negocio es una sola; API y MCP son dos formas de exponerla.**

Si ambos caminos terminan en la misma capacidad interna, tienes una arquitectura mucho más limpia que:

```text
API → implementación propia
MCP → otra implementación
```

---

## Hay otra cosa que me parece especialmente buena de tu experimento

Tu script está haciendo explícitamente:

### 1. Discovery

```python
tools = await client.list_tools()
```

### 2. Tool selection

```text
LLM
  ↓
"para responder esto necesito consultar X"
```

### 3. Tool execution

```python
result = await tools.xxx(...)
```

### 4. Observation

```text
resultado de la herramienta
        ↓
       LLM
```

### 5. Synthesis

```text
datos + pregunta original
        ↓
       LLM
        ↓
respuesta
```

Eso ya es básicamente el patrón:

**Discover → Decide → Act → Observe → Reason → Answer**

Y después puedes evolucionarlo a:

```text
READ
 ↓
ANALYZE
 ↓
ACT
```

que es justamente la separación que has estado planteando para el Enablement Layer.

---

## Ahora yo no agregaría más complejidad todavía

Si esto está funcionando, **yo congelaría momentáneamente la arquitectura y empezaría a probarla con preguntas difíciles**.

Por ejemplo:

### Caso 1 — una tool

> ¿Cuál es la disponibilidad de agenda para mañana?

```text
LLM
 ↓
consultar_disponibilidad
 ↓
resultado
 ↓
LLM
 ↓
respuesta
```

### Caso 2 — varias tools

> ¿Qué pacientes tienen deuda vencida y además tienen atención próxima?

Podría necesitar:

```text
deuda_vencida
       ↓
datos
       ↓
agenda_proxima
       ↓
correlación
       ↓
LLM
```

### Caso 3 — razonamiento sobre datos

> ¿Qué sucursales presentan señales de baja utilización?

Aquí ya no basta con recuperar un registro. El LLM tiene que **interpretar datos estructurados**.

### Caso 4 — tool equivocada

Haz deliberadamente preguntas ambiguas y observa si:

```text
LLM → tool equivocada
```

o si pide información adicional.

### Caso 5 — información insuficiente

Una prueba muy importante:

> "¿Por qué bajó la producción?"

Si tus tools solamente entregan producción pero no tienen dimensión temporal suficiente, el agente debería **reconocer que no puede demostrar causalidad**, no inventarla.

---

## Y hay una prueba todavía más importante

Yo mediría el sistema separando:

| Etapa        | Qué validar                                  |
| ------------ | -------------------------------------------- |
| Discovery    | ¿El LLM entiende qué hace cada tool?         |
| Selection    | ¿elige la capability correcta?               |
| Arguments    | ¿construye correctamente los parámetros?     |
| Execution    | ¿la tool funciona?                           |
| Data         | ¿los datos son suficientes?                  |
| Reasoning    | ¿interpreta correctamente?                   |
| Grounding    | ¿la respuesta está respaldada por los datos? |
| Final answer | ¿responde exactamente la pregunta?           |

Porque ahí empiezas a pasar de:

> **"Tengo un MCP funcionando."**

a:

> **"Tengo una capacidad de ejecución y razonamiento sobre datos empresariales que puede ser evaluada."**

Y eso, para el proyecto que estás construyendo, es bastante más valioso.

Además, tu experimento está validando una hipótesis arquitectónica que vienes trabajando hace semanas: **la API y MCP no deberían competir por la lógica de negocio; deberían consumir la misma capacidad canónica**. Si eso ya lo estás viendo funcionar en tu prueba, yo consideraría esa parte de la arquitectura bastante bien encaminada.



# Desarrollo segundo servicio

Sí. Y al leer este extracto junto con lo que acabas de descubrir experimentando con API + MCP, aparece algo muy interesante: **tu estrategia ya está preparada para el siguiente experimento**. De hecho, yo haría que ese experimento use precisamente estas capacidades de la milla cero.

## 1. Tu sección 8 está conceptualmente bien separada

La separación:

```text
READ
  ↓
ANALYZE
  ↓
ACT
```

no es solamente una clasificación técnica. Está definiendo **niveles de responsabilidad**.

En tu caso:

### READ

Las capabilities recuperan información empresarial:

```text
consultar_resumen_deuda
consultar_ingresos_por_tipo_pago
consultar_ingresos_por_tipo_tarjeta
consultar_ingresos_por_tipo_prevision
...
```

### ANALYZE

Las capabilities producen conocimiento derivado:

```text
calcular_variacion_deuda
calcular_aceleracion_deuda
...
```

### ACT

Eventualmente:

```text
enviar_correo
generar_alerta
registrar_compromiso
...
```

Y hay una decisión de tu documento que considero especialmente importante:

> **el LLM no calcula los KPI.**

Eso está muy bien.

El LLM debería interpretar:

```json
{
  "saldo_deuda": 4913240404,
  "variacion_mensual": 76464426,
  "variacion_pct": 1.58,
  "aceleracion": 0.66
}
```

y producir:

> "La deuda presenta un aumento mensual de 1,58%, superior al crecimiento observado el mes anterior..."

Pero **no debería recibir cuatro tablas y hacer él mismo las matemáticas financieras**.

Eso mantiene la semántica empresarial fuera del modelo probabilístico.

---

# 2. Y ahora tu próximo experimento calza PERFECTAMENTE

Tu prueba anterior tenía algo parecido a:

```text
Pregunta
   ↓
LLM
   ↓
Tool A
   ↓
respuesta
```

Ahora yo utilizaría tus capacidades reales.

Por ejemplo, construiría una pregunta como:

> **"¿Cómo vamos con la deuda este mes? Analiza la situación considerando la evolución de la deuda y los ingresos del período, y entrega una explicación ejecutiva."**

Y le entregaría al LLM únicamente el catálogo de las capacidades disponibles.

Por ejemplo:

```text
1. consultar_resumen_deuda
2. consultar_ingresos_por_tipo_pago
```

Pero **no le diría qué tools debe utilizar**.

Tu experimento consiste justamente en observar qué hace.

---

# 3. Incluso puedes hacer el experimento más interesante

Yo prepararía **dos tools deliberadamente complementarias**.

Por ejemplo:

```text
Tool A
consultar_resumen_deuda

Tool B
consultar_ingresos_por_tipo_pago
```

Y pregunta:

> **"¿Cómo vamos con la deuda este mes? Compara la evolución de la deuda con el comportamiento de los ingresos por tipo de pago y dame una explicación ejecutiva."**

Ahora hay una dependencia lógica:

```text
                    pregunta
                       │
                       ▼
                      LLM
                   ┌───┴───┐
                   ▼       ▼
                deuda   ingresos
                   │       │
                   └───┬───┘
                       ▼
                      LLM
                       │
                       ▼
                análisis ejecutivo
```

Ahí podrás observar si el LLM:

1. descubre que necesita **ambas capacidades**;
2. ejecuta la primera;
3. recibe el resultado;
4. determina que todavía necesita la segunda;
5. ejecuta la segunda;
6. recibe el resultado;
7. integra ambas fuentes;
8. responde.

Eso sería una prueba muy buena de **orquestación multi-tool**.

---

# 4. Pero hay una cuestión todavía más interesante en tu diseño

Tu sección 8.2 actualmente dice:

> Pregunta del CEO: "¿Cómo vamos con la deuda este mes?"

Y muestras:

```text
consultar_resumen_deuda
consultar_ingresos_por_tipo_pago
consultar_ingresos_por_tipo_tarjeta
consultar_ingresos_por_tipo_prevision
```

Eso es prácticamente un **plan de ejecución implícito**.

Yo haría un pequeño cambio conceptual en esa sección.

No diría inicialmente:

> para responder esta pregunta se ejecutan A, B, C y D.

Porque eso mezcla **el diseño de la capacidad** con **la estrategia de resolución de la pregunta**.

Preferiría:

```text
Pregunta CEO
    ↓
LLM
    ↓
selecciona capacidades necesarias
    ↓
ejecuta
    ↓
observa resultados
    ↓
determina si necesita más capacidades
    ↓
ANALYZE
    ↓
respuesta
```

Entonces tu catálogo se convierte en algo más poderoso:

> **El catálogo no solamente documenta qué puede hacer el sistema; constituye el espacio de acciones que el agente puede seleccionar.**

Eso es exactamente lo que estás descubriendo con tus pruebas.

---

# 5. Hay una distinción que yo incorporaría a tu MD

Actualmente tienes:

### Capacidad

```text
consultar_resumen_deuda
```

### KPI

```text
variacion_mensual_deuda
```

Pero agregaría conceptualmente una tercera cosa:

### Pregunta / intención empresarial

```text
"¿Cómo vamos con la deuda este mes?"
```

Y tendrías:

```text
INTENCIÓN
    ↓
CAPACIDADES READ
    ↓
DATOS
    ↓
CAPACIDADES ANALYZE
    ↓
CONOCIMIENTO
    ↓
LLM
    ↓
RESPUESTA
```

Esto te permite distinguir tres niveles:

| Nivel                    | Ejemplo                     |
| ------------------------ | --------------------------- |
| **Pregunta empresarial** | "¿Cómo vamos con la deuda?" |
| **Capability**           | `consultar_resumen_deuda`   |
| **KPI**                  | `variacion_mensual_deuda`   |

El LLM trabaja principalmente en el primer salto:

```text
Pregunta → capabilities necesarias
```

Y posteriormente:

```text
Datos → interpretación
```

Pero **la definición matemática del KPI pertenece al sistema**, no al LLM.

---

# 6. Y tu hallazgo sobre `avg(bat_deuda)` es MUY importante

Esta parte:

> el "saldo de deuda" que el correo muestra es `round(avg(bat_deuda),0)` del mes — promedio diario del mes, no saldo de cierre.

es exactamente el tipo de cosa que hace que una arquitectura de capabilities sea mejor que simplemente "poner SQL detrás de MCP".

Porque si mañana alguien crea:

```text
calcular_variacion_deuda
```

y accidentalmente interpreta:

```text
saldo_deuda = último día del mes
```

en lugar de:

```text
saldo_deuda = promedio diario del mes
```

tendrás un KPI matemáticamente correcto pero **semánticamente incorrecto**.

Por eso tu observación de §19 h1 debería sobrevivir hasta el contrato de la capability.

Algo conceptualmente como:

```text
consultar_resumen_deuda

Semántica:
"saldo_deuda" representa el promedio diario mensual
de bat_deuda, redondeado a entero.

No representa saldo de cierre.
```

Eso es **contrato de negocio**, no detalle de implementación.

---

# 7. Y aquí veo una evolución muy buena de tu experimento

Yo haría ahora esta secuencia:

### Experimento 01 — selección

```text
Pregunta
 ↓
LLM
 ↓
Tool A
```

Ya lo hiciste.

### Experimento 02 — multi-tool

```text
Pregunta
 ↓
LLM
 ↓
Tool A
 ↓
resultado
 ↓
LLM
 ↓
Tool B
 ↓
resultado
 ↓
respuesta
```

**Este es el que estás planteando ahora.**

### Experimento 03 — tool chaining

```text
Pregunta
 ↓
Tool A
 ↓
resultado A
 ↓
LLM genera argumentos para B
 ↓
Tool B
 ↓
resultado B
 ↓
LLM
 ↓
respuesta
```

Aquí ya aparece algo mucho más cercano a un agente real.

### Experimento 04 — READ → ANALYZE

```text
Pregunta
 ↓
READ tools
 ↓
datos
 ↓
ANALYZE capability
 ↓
KPI
 ↓
LLM
 ↓
respuesta ejecutiva
```

Y este último es, en mi opinión, **el experimento que más valor tiene para tu estrategia del Enablement Layer**, porque demuestra que el LLM no necesita convertirse en calculadora ni en SQL generator.

---

## Y hay una conclusión importante

Lo que estás haciendo ahora no es simplemente probar si **MCP funciona**.

Estás descubriendo experimentalmente cuál debe ser el límite entre:

```text
LLM
```

```text
Agent runtime
```

```text
MCP
```

```text
Service Layer
```

```text
Oracle
```

y además estás empezando a descubrir dónde debe vivir el **conocimiento empresarial**.

Eso es justamente lo que necesitabas antes de cerrar la arquitectura definitiva.

Y yo **no tocaría todavía tu estrategia general**. Primero terminaría estos experimentos: especialmente **multi-tool → chaining → READ/ANALYZE**. Después volvería al MD y actualizaría la arquitectura con lo que realmente observaste, en lugar de diseñarla solamente desde supuestos.



# MCP Modo API y modo CLI

Sí. Y **esa distinción merece quedar explícita en tu documento**, porque estás hablando de dos formas diferentes de consumir el mismo servidor MCP.

La diferencia fundamental es **quién hace de MCP client/orquestador**.

## 1. Consumo desde un programa propio

Por ejemplo, tu Python:

```text
┌─────────────────────────────┐
│       Tu aplicación         │
│          Python             │
│                             │
│  1. descubre tools          │
│  2. entrega catálogo al LLM │
│  3. recibe decisión         │
│  4. ejecuta tool MCP        │
│  5. devuelve resultado LLM  │
│  6. continúa el ciclo        │
└──────────────┬──────────────┘
               │ MCP
               ▼
        ┌──────────────┐
        │ MCP Server   │
        └──────────────┘
```

Aquí **tú tienes que programar el agente**.

Por ejemplo:

```python
tools = await mcp_client.list_tools()

# catálogo → LLM

decision = await llm(...)

# decisión → ejecución

result = await mcp_client.call_tool(...)
```

El LLM **no tiene una conexión MCP propia**. Tu programa es el intermediario.

Esto es justamente lo que acabas de descubrir.

---

# 2. Consumo desde Claude / Codex / OpenCode

Aquí cambia radicalmente el escenario.

Tú configuras el MCP Server en el cliente:

```text
┌───────────────────┐
│ Claude / Codex /  │
│ OpenCode          │
│                   │
│ MCP Client        │
└─────────┬─────────┘
          │
          │ MCP
          ▼
┌───────────────────┐
│    MCP Server     │
│                   │
│     Tools         │
└───────────────────┘
```

El cliente ya implementa el ciclo MCP.

Por eso tú **no necesitas escribir**:

```python
list_tools()
```

ni:

```python
call_tool()
```

ni construir manualmente el loop:

```text
LLM
 ↓
tool
 ↓
resultado
 ↓
LLM
 ↓
tool
 ↓
resultado
 ↓
respuesta
```

El cliente se encarga de eso.

---

# 3. Y aquí está la distinción que yo pondría en tu MD

No diría simplemente:

> "MCP se puede consumir desde Python o Claude."

Eso puede generar una confusión importante.

Lo expresaría como:

### Modelo A — Aplicación propia

**La aplicación implementa el MCP Client y el ciclo de orquestación.**

```text
Aplicación
 ├── MCP Client
 ├── LLM API
 ├── Tool selection
 ├── Tool execution
 └── Agent loop
          │
          ▼
      MCP Server
```

Ejemplos:

* Python
* Java
* Node.js
* cualquier aplicación que implemente un MCP Client

---

### Modelo B — Cliente AI con soporte MCP

**El cliente AI ya implementa el MCP Client y la orquestación.**

```text
Claude / Codex / OpenCode
          │
          ├── MCP Client
          ├── Tool discovery
          ├── Tool selection
          ├── Tool execution
          └── Agent loop
                    │
                    ▼
                MCP Server
```

Ejemplos:

* Claude
* Codex
* OpenCode

---

# 4. Hay una frase que creo que resume muy bien tu descubrimiento

> **MCP define el protocolo de interacción con las capacidades; no define quién implementa el agente que decide cuándo y cómo utilizarlas.**

Eso explica perfectamente por qué tu experiencia fue distinta.

En tu script:

```text
Python = MCP Client + Agent Runtime
LLM = razonador
MCP Server = capabilities
```

Mientras que en Claude/OpenCode/Codex:

```text
Claude/OpenCode/Codex
       │
       ├── MCP Client
       ├── Agent Runtime
       └── LLM
              │
              ▼
         MCP Server
```

---

# 5. Esto además tiene una consecuencia arquitectónica importante para tu Enablement Layer

Tu servidor **no debería saber quién lo consume**.

Puede recibir:

```text
Claude
Codex
OpenCode
Python
Java
otro agente
otra aplicación
```

y debería exponer exactamente las mismas capabilities:

```text
consultar_resumen_deuda
consultar_ingresos_por_tipo_pago
...
```

El servidor no necesita saber si detrás existe:

```text
un humano usando Claude
```

o:

```text
un script Python con DeepSeek
```

o:

```text
OpenCode
```

Eso refuerza muchísimo tu concepto de:

> **Capability como unidad canónica; MCP y API como mecanismos de exposición.**

Y yo agregaría una tabla a esa sección:

| Consumo          | MCP Client    | Agent loop | Tool discovery | LLM                |
| ---------------- | ------------- | ---------- | -------------- | ------------------ |
| Python + API LLM | Tu aplicación | Tu código  | Tu código      | API DeepSeek/etc.  |
| Java + API LLM   | Tu aplicación | Tu código  | Tu código      | API LLM            |
| Claude           | Claude        | Claude     | Claude         | Claude             |
| Codex            | Codex         | Codex      | Codex          | Codex              |
| OpenCode         | OpenCode      | OpenCode   | OpenCode       | Modelo configurado |

**Ese cuadro probablemente le va a aclarar muchísimo al grupo de trabajo por qué "consumir un MCP desde Python" y "configurar un MCP en Claude/OpenCode/Codex" son experiencias técnicamente diferentes aunque estén hablando con el mismo servidor.**



# SDD


Sí. Y te diría que **no estás armando un cañón porque sí**. Estás haciendo algo bastante más estratégico: estás usando `consultar_resumen_deuda` como **laboratorio controlado para definir el método de ingeniería asistida por IA que después pretendes aplicar a la refactorización del legacy**.

La clave es que el objetivo ya no es solamente implementar una capability.

Es validar este modelo:

```text
                    Fernando-orquestado
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Diseñador     Implementador    Tester/Validador
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    Capability
               consultar_resumen_deuda
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
                API                  MCP
                 │                   │
                 └─────────┬─────────┘
                           ▼
                        Oracle
```

Y eso cambia bastante la naturaleza del experimento.

## Lo que estás construyendo realmente

Yo separaría **tres productos** que estás creando simultáneamente:

### 1. El producto funcional

Por ejemplo:

```text
consultar_resumen_deuda
```

Que debe:

* consultar correctamente Oracle;
* respetar la semántica legacy;
* exponer la capability vía API;
* exponerla vía MCP;
* entregar datos estructurados;
* tener contrato claro.

### 2. El producto metodológico

Estás definiendo:

```text
Requerimiento
    ↓
Diseño
    ↓
Implementación
    ↓
Pruebas
    ↓
Validación
    ↓
Capability
```

pero con agentes especializados.

### 3. El producto organizacional

Estás estableciendo **cómo quieres que el Departamento TI desarrolle software con IA**.

Y este tercero es el más importante para lo que viene.

---

# Sobre SDD: aquí sí veo sentido probarlo

Pero haría una distinción.

No adoptaría SDD porque "es moderno" o porque los agentes lo recomiendan.

Lo adoptaría si demuestra que consigue esto:

> **reducir la ambigüedad entre intención, diseño, implementación y validación cuando el código es generado/modificado por IA.**

En tu caso tiene mucho sentido porque vas a trabajar con un sistema legacy donde la dificultad no será escribir Python.

La dificultad será:

```text
¿Qué significa realmente esta capability?
       ↓
¿Qué comportamiento existente debo preservar?
       ↓
¿Qué contrato debe tener?
       ↓
¿Qué datos son fuente de verdad?
       ↓
¿Qué casos borde existen?
       ↓
¿Cómo demuestro paridad?
```

Ahí una especificación estructurada antes del código puede ser tremendamente útil.

---

# Y hay algo que cambiaría en tu planteamiento de agentes

Mencionaste:

> Fernando-orquestado
> Diseñador
> Implementador
> otro implementador

Yo evitaría que los dos implementadores sean simplemente "más agentes que programan".

Haría que tengan **responsabilidades distintas y verificables**.

Por ejemplo:

```text
Fernando-orquestado
        │
        ▼
   Diseñador
        │
        ▼
  Implementador
        │
        ▼
   Verificador
```

### Diseñador

No toca código.

Produce:

```text
SPEC
CONTRACT
DOMAIN SEMANTICS
TEST CASES
ACCEPTANCE CRITERIA
```

### Implementador

Recibe la especificación.

Produce:

```text
Service
API adapter
MCP adapter
tests
```

### Verificador

**No debería confiar en el Implementador.**

Revisa:

```text
SPEC
  ↕
IMPLEMENTATION
  ↕
TESTS
  ↕
LEGACY RESULT
```

y determina:

```text
PASS
FAIL
NEEDS_REVIEW
```

Eso es especialmente importante en tu escenario.

Porque si haces:

```text
Diseñador IA
    ↓
Implementador IA
    ↓
"se ve bien"
```

tienes tres agentes que pueden compartir el mismo error conceptual.

---

# Y aquí tienes una oportunidad enorme con `consultar_resumen_deuda`

Tu hallazgo de:

> `round(avg(bat_deuda),0)` = promedio diario mensual, no saldo de cierre.

es **perfecto para probar el modelo SDD**.

El Diseñador debería generar una especificación que diga explícitamente:

```text
Semantic rule:

El saldo de deuda mensual corresponde al promedio diario
de bat_deuda para el período consultado.

No corresponde al saldo del último día del período.
```

Después el Implementador implementa.

Después el Verificador prueba:

```text
Legacy:
round(avg(bat_deuda),0)

Nuevo:
consultar_resumen_deuda(...)

¿Resultado equivalente?
```

Ahí estás enseñándole a tus agentes algo mucho más importante que Python:

**preservación de semántica de negocio.**

Y eso es exactamente lo que vas a necesitar cuando empieces a extraer capabilities del Java 2008.

---

# Porque el verdadero desafío futuro no será `consultar_resumen_deuda`

Será algo así:

```text
Java 2008
   │
   ├── JSP
   ├── Java
   ├── SQL
   ├── lógica mezclada
   ├── HTML generado
   ├── dependencias implícitas
   └── comportamiento no documentado
             │
             ▼
       nueva capability
```

Ahí necesitas que la IA sea capaz de hacer:

```text
DESCUBRIR
   ↓
INTERPRETAR
   ↓
ESPECIFICAR
   ↓
IMPLEMENTAR
   ↓
COMPARAR
   ↓
VALIDAR
```

Y no simplemente:

```text
"toma este Java y pásalo a Python"
```

Tu **assessment de los ~700 MD** y el trabajo de recuperación de conocimiento que ya hiciste adquieren mucho más valor en ese punto: esos documentos pasan a ser **evidencia/contexto para los agentes**, no necesariamente la especificación definitiva.

---

# Por eso me gusta tu decisión de NO usar tus MD clásicos como base

Los usaría como:

> **fuente de evidencia**

y no como:

> **fuente normativa de implementación**.

La diferencia es fundamental.

Podrías tener:

```text
Legacy Evidence
       │
       ├── Java
       ├── JSP
       ├── SQL
       ├── MD
       ├── Oracle metadata
       └── comportamiento observado
                │
                ▼
          Diseñador IA
                │
                ▼
       SPEC / CONTRACT
                │
                ▼
         Implementador
                │
                ▼
          Verificador
                │
                ▼
        Capability nueva
```

La **specificación generada y validada** se convierte entonces en el nuevo artefacto contractual.

---

## Y aquí sí pondría un freno al "cañón"

No por la cantidad de agentes.

El riesgo real es **sobre-orquestar**.

Si para implementar una función de 30 líneas necesitas:

```text
orquestador
→ diseñador
→ arquitecto
→ implementador
→ reviewer
→ tester
→ documentación
→ otro reviewer
```

y el proceso tarda más que escribirla tú mismo, tienes una fábrica de burocracia asistida por IA.

Por eso tu `consultar_resumen_deuda` es un excelente **caso piloto**.

Mide cosas concretas:

| Métrica       | Qué quieres descubrir                          |
| ------------- | ---------------------------------------------- |
| Tiempo humano | ¿Cuánto intervienes tú?                        |
| Iteraciones   | ¿Cuántas veces corriges agentes?               |
| Defectos      | ¿Qué errores aparecen?                         |
| Semántica     | ¿Preserva el comportamiento legacy?            |
| Cobertura     | ¿Genera casos borde?                           |
| Trazabilidad  | ¿Puedes explicar por qué se implementó así?    |
| Reutilización | ¿El método sirve para la siguiente capability? |

Si después de 5–10 capabilities descubres que el patrón se mantiene, entonces ya no es un experimento.

Es **un método de desarrollo para tu TI**.

Y ahí sí tiene mucho sentido llevarlo a la refactorización gruesa.

### En otras palabras

No estás intentando demostrar:

> "Miren qué impresionante es hacer software con 4 agentes."

Estás intentando demostrar:

> **"Podemos convertir conocimiento legacy + especificación + agentes especializados + validación automatizada en una línea de producción controlada para construir las nuevas capacidades que reemplazarán progresivamente al legacy."**

Esa segunda formulación es, a mi juicio, mucho más cercana a lo que realmente estás construyendo.

---
# Administrar mas de 200 tools
---

Sí, pero con una precisión importante: **no resolvería el problema simplemente haciendo RAG sobre las 200 tools**.

Lo que estás describiendo es un problema clásico de **Tool Discovery / Tool Routing**: tienes muchas capacidades disponibles, pero no quieres entregar todas sus definiciones al LLM en cada turno.

La arquitectura que estás construyendo puede evolucionar de esto:

```text
Usuario
   ↓
Python
   ↓
[catálogo completo de 200 tools]
   ↓
LLM
   ↓
tool seleccionada
   ↓
Python ejecuta
   ↓
resultado
   ↓
LLM
   ↓
respuesta
```

hacia esto:

```text
Usuario
   ↓
Python Orquestador
   ↓
Tool Discovery / Router
   ↓
[5-10 tools relevantes]
   ↓
LLM
   ↓
tool seleccionada
   ↓
MCP
   ↓
resultado
   ↓
LLM
   ↓
respuesta
```

Y **sí, RAG puede ser parte del Tool Discovery**, pero yo no lo diseñaría como un RAG tradicional de documentos.

## 1. El problema real no son las 200 tools

Supongamos que tienes:

```text
consultar_ventas_dia
consultar_ventas_periodo
consultar_ventas_por_sucursal
consultar_ventas_por_producto
consultar_ventas_por_vendedor
consultar_devoluciones
consultar_pagos
consultar_deuda
consultar_morosidad
consultar_produccion
...
```

La pregunta:

> "¿Cuánto vendí el día 30-09-2026?"

no necesita conocer las 200.

Necesita encontrar algo parecido a:

```text
consultar_ventas_dia
```

Entonces tienes dos problemas diferentes:

### Problema A — Discovery

> ¿Qué capacidades existen que podrían responder esta pregunta?

### Problema B — Tool Calling

> De las capacidades encontradas, ¿cuál debo ejecutar y con qué parámetros?

Tu arquitectura actual resuelve muy bien B.

Lo que necesitas agregar es A.

---

# 2. Yo construiría un "Tool Registry"

Esto encaja muchísimo con lo que vienes planteando anteriormente sobre **Tool Contract + Tool Registry**.

En vez de pensar:

> "Tengo 200 MCP tools."

piensa:

> "Tengo 200 capacidades registradas."

Por ejemplo:

```json
{
  "name": "consultar_ventas_dia",
  "description": "Obtiene el monto total vendido para una fecha determinada.",
  "domain": "ventas",
  "capabilities": [
    "ventas",
    "resumen",
    "fecha"
  ],
  "input_schema": {
    "fecha": "YYYY-MM-DD"
  },
  "output": {
    "type": "financial_summary"
  }
}
```

Pero además agregaría metadata específicamente orientada al discovery:

```json
{
  "name": "consultar_ventas_dia",

  "domain": "ventas",

  "intent": [
    "consultar ventas",
    "total vendido",
    "ventas de un día",
    "venta diaria",
    "facturación diaria"
  ],

  "keywords": [
    "ventas",
    "vendí",
    "vendido",
    "total",
    "día",
    "fecha"
  ],

  "examples": [
    "Cuánto vendí ayer",
    "Cuánto vendimos el 30 de septiembre",
    "Cuál fue la venta del día",
    "Total vendido en una fecha"
  ]
}
```

Eso constituye tu **índice de capacidades**.

---

# 3. Ahí sí aparece RAG

Podrías generar embeddings de esa metadata.

Por ejemplo:

```text
consultar_ventas_dia
        ↓
embedding
        ↓
Vector DB
```

Cuando llega:

> "Cuánto vendí el día 30-09-2026"

haces:

```text
embedding(pregunta)
        ↓
vector search
        ↓
top K
```

Y obtienes:

```text
1. consultar_ventas_dia       0.94
2. consultar_ventas_periodo   0.78
3. consultar_ventas_sucursal  0.71
4. consultar_devoluciones     0.42
```

Entonces **recién ahí** construyes el catálogo que verá el LLM:

```text
Tools disponibles para esta consulta:

consultar_ventas_dia
consultar_ventas_periodo
consultar_ventas_sucursal
```

No 200.

---

# 4. Pero hay una arquitectura todavía más sólida

Yo no me quedaría únicamente con vector search.

Para 200 tools, incluso puedes hacerlo bastante más robusto:

```text
                    ┌─────────────────────┐
                    │    Tool Registry    │
                    │                     │
                    │  200 capacidades    │
                    └──────────┬──────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Tool Discovery   │
                     │                   │
                     │ Semantic Search   │
                     │ Metadata Filter   │
                     │ Keyword Search    │
                     └─────────┬─────────┘
                               │
                         Top 5 / Top 10
                               │
                     ┌─────────▼─────────┐
                     │       LLM         │
                     │                   │
                     │ Tool Selection    │
                     └─────────┬─────────┘
                               │
                         selected tool
                               │
                     ┌─────────▼─────────┐
                     │   MCP Server      │
                     └───────────────────┘
```

Esto es un **retrieval + tool selection pipeline**.

Y aquí hay una distinción muy importante:

> **RAG no sería para recuperar la respuesta. Sería para recuperar capacidades.**

---

# 5. Yo usaría Hybrid Retrieval

No confiaría exclusivamente en embeddings.

Tienes tres señales muy útiles:

### A. Semantic search

```text
"Cuánto vendí..."
```

encuentra:

```text
consultar_ventas_dia
```

aunque las palabras no coincidan exactamente.

### B. Keyword/BM25

Puede detectar directamente:

```text
vendí
ventas
día
```

### C. Metadata

Puedes restringir:

```text
domain = ventas
```

si el router detecta que la pregunta pertenece a ventas.

Entonces:

```text
                    Pregunta
                       │
              ┌────────┴────────┐
              ↓                 ↓
         Vector Search       BM25
              │                 │
              └────────┬────────┘
                       ↓
                 Fusion / Rank
                       ↓
                   Top K
                       ↓
                      LLM
```

Esto es bastante más resistente que:

```text
pregunta → embedding → top 5
```

---

# 6. Y aquí aparece algo que creo que te va a interesar mucho

**No necesariamente necesitas enviar siquiera las definiciones completas de las tools al primer LLM.**

Puedes hacer dos etapas.

### Etapa 1 — Discovery

El LLM recibe solamente:

```text
Pregunta:
¿Cuánto vendí el 30-09-2026?

Capacidades candidatas:

1. consultar_ventas_dia
   Obtiene ventas totales para una fecha.

2. consultar_ventas_periodo
   Obtiene ventas entre fecha inicial y fecha final.

3. consultar_ventas_sucursal
   Obtiene ventas de una sucursal.
```

El LLM decide:

```json
{
  "tool": "consultar_ventas_dia",
  "arguments": {
    "fecha": "2026-09-30"
  }
}
```

### Etapa 2 — Execution

Ahora Python recupera la **definición completa** de esa tool:

```text
consultar_ventas_dia
+ schema
+ parámetros
+ restricciones
```

y la ejecuta mediante MCP.

Esto reduce todavía más el contexto.

---

# 7. Incluso puedes separar "capacidad" de "tool"

Esta es una evolución que personalmente considero muy interesante para tu arquitectura.

No hagas que el catálogo sea simplemente:

```text
200 MCP tools
```

Haz:

```text
                 CAPACIDAD
                    │
          ┌─────────┴─────────┐
          │                   │
      REST Adapter        MCP Adapter
          │                   │
      HTTP/API              Tool
```

Esto coincide exactamente con la idea que hemos venido trabajando:

> **la capacidad es canónica; el protocolo es una representación.**

Entonces tu Tool Registry podría registrar:

```text
Capability
──────────────
consultar_ventas_dia

Description
Domain
Intent
Examples
Parameters
Permissions
Risk
REST endpoint
MCP tool
```

Y MCP sería simplemente una de las formas de exponerla.

---

# 8. Con 200 tools, yo no me preocuparía todavía demasiado

Hay algo importante en tu escenario.

**200 tools no es una cantidad monstruosa desde el punto de vista de infraestructura.**

El problema es principalmente:

* contexto
* latencia
* costo
* precisión del tool selection
* confusión entre herramientas similares

Y esos problemas aparecen progresivamente.

Por ejemplo:

### 20 tools

Puedes enviar todas.

### 50 tools

Probablemente todavía sea manejable dependiendo del modelo y schemas.

### 200 tools

Ya conviene discovery.

### 1.000+

Ya necesitas una arquitectura explícita de:

```text
Registry
+
Discovery
+
Routing
+
Ranking
+
Execution
```

Por eso **no diseñaría tu arquitectura actual pensando solamente en "200"**.

Diseñaría el mecanismo para que 200, 500 o 2.000 sean simplemente un cambio de tamaño del registry.

---

# 9. Hay otra estrategia: jerarquía de dominios

Y esta puede ser incluso mejor que hacer una búsqueda vectorial plana.

Imagina:

```text
                  Tool Registry
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
     Ventas          Finanzas        Pacientes
       │               │                │
   35 tools          28 tools         46 tools
       │
       ├── consultas
       ├── análisis
       ├── proyecciones
       └── operaciones
```

Pregunta:

> "¿Cuánto vendí ayer?"

Primero:

```text
Pregunta
   ↓
Domain Router
   ↓
VENTAS
```

Después:

```text
VENTAS
   ↓
Tool Discovery
   ↓
consultar_ventas_dia
```

Entonces nunca haces:

```text
pregunta → buscar entre 200
```

sino:

```text
pregunta
   ↓
dominio
   ↓
subdominio
   ↓
capacidad
   ↓
tool
```

Eso escala muchísimo mejor.

---

# 10. Y puedes agregar un "Tool Router" especializado

Esto es particularmente interesante para tu enfoque con agentes.

Podrías tener:

```text
Fernando-orquestador
        │
        ▼
   Tool Router
        │
        ▼
 Tool Discovery
        │
        ▼
  candidatos
        │
        ▼
    LLM
        │
        ▼
 herramienta
```

Incluso puedes hacer que el router sea barato:

```text
DeepSeek / modelo pequeño
        ↓
identifica dominio + intención
```

y reservar el modelo más potente para:

```text
razonamiento
+
tool selection compleja
+
análisis del resultado
```

Eso también reduce costos.

---

# 11. Hay una arquitectura todavía más interesante para tu caso

Dado que tú estás construyendo MCP **para capacidades de negocio**, yo mantendría un registro como:

```text
┌──────────────────────────────────────────────┐
│              TOOL REGISTRY                   │
├──────────────────────────────────────────────┤
│ Capability                                   │
│ Description                                  │
│ Domain                                       │
│ Subdomain                                    │
│ Intent                                       │
│ Examples                                     │
│ Keywords                                     │
│ Input schema                                 │
│ Output schema                                │
│ Risk level                                   │
│ Read / Analyze / Act                         │
│ Permissions                                  │
│ MCP tool                                     │
│ REST capability                              │
│ Version                                      │
│ Status                                       │
└──────────────────────────────────────────────┘
```

Y sobre ese registry:

```text
                 TOOL DISCOVERY
                       │
       ┌───────────────┼────────────────┐
       │               │                │
    Metadata          BM25          Embeddings
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                   Ranking
                       ↓
                    Top K
                       ↓
                     LLM
```

Esto ya es una arquitectura seria de **Tool Discovery**.

---

# 12. ¿Y dónde entra MCP exactamente?

Aquí hay una distinción conceptual que te recomiendo mantener:

**MCP no debería ser quien resuelva el problema de descubrir entre 2.000 capacidades.**

MCP resuelve principalmente la **interfaz estandarizada entre el agente y las herramientas/contextos**.

Tu aplicación puede tener:

```text
                 AI Orchestrator
                       │
                Tool Discovery
                       │
                 Tool Registry
                       │
                 MCP Client
                       │
              ┌────────┴────────┐
              ↓                 ↓
          MCP Server A       MCP Server B
              │                 │
           tools...          tools...
```

Incluso podrías tener varios servidores MCP:

```text
mcp-ventas
mcp-finanzas
mcp-pacientes
mcp-produccion
mcp-stock
```

Y el discovery decide **qué servidor MCP consultar**.

Eso escala aún mejor.

---

# 13. Para tu laboratorio, yo evolucionaría tu implementación así

Tu implementación actual:

```text
Python
   │
   ├── obtiene tools MCP
   │
   ├── pregunta + catálogo
   │
   ├── DeepSeek
   │
   ├── tool call
   │
   └── resultado → DeepSeek
```

La siguiente versión:

```text
Python Orchestrator
       │
       ├── User Question
       │
       ▼
Tool Discovery
       │
       ├── BM25
       ├── Vector Search
       └── Metadata
       │
       ▼
Top 5-10 capabilities
       │
       ▼
DeepSeek
       │
       ▼
Tool Call
       │
       ▼
MCP
       │
       ▼
Result
       │
       ▼
DeepSeek
       │
       ▼
Final Answer
```

Y después una tercera evolución:

```text
                  ORCHESTRATOR
                       │
                 Intent Router
                       │
          ┌────────────┼─────────────┐
          ↓            ↓             ↓
       Ventas       Finanzas      Clínica
          │            │             │
          ↓            ↓             ↓
     Tool Registry Tool Registry Tool Registry
          │
          ↓
     Tool Discovery
          │
          ↓
       Top K
          │
          ↓
         LLM
          │
          ↓
        MCP
```

---

## Mi conclusión para tu caso

**Sí: RAG es una pieza válida, pero no llamaría a toda la solución "RAG".**

El concepto arquitectónico que estás buscando es:

> **Dynamic Tool Discovery / Tool Retrieval + Tool Routing**

Y la implementación que veo más sólida para tu escenario es:

```text
             TOOL REGISTRY
                   │
        ┌──────────┼──────────┐
        │          │          │
     Metadata     BM25     Embeddings
        │          │          │
        └──────────┼──────────┘
                   ↓
              Hybrid Ranker
                   ↓
                Top-K
                   ↓
              LLM Tool Call
                   ↓
                  MCP
                   ↓
               Resultado
                   ↓
                  LLM
```

**Y hay una decisión arquitectónica que tomaría desde ahora:** no acoples tu orquestador a `list_tools()` como mecanismo permanente de discovery. Úsalo en tu laboratorio actual porque es excelente para probar el patrón, pero cuando tu catálogo crezca, introduce un **Tool Registry independiente del MCP server**.

Eso además calza casi perfectamente con tu idea anterior de **Tool Contract + Tool Registry + capacidad canónica única**. El MCP pasa a ser el mecanismo de ejecución, mientras que el Registry se convierte en el mecanismo de **descubrimiento y gobierno de capacidades**.

Y para tu futuro escenario de **200 servicios**, yo empezaría a experimentar ya con **20–30 tools simuladas**, porque ahí vas a poder medir algo mucho más interesante que simplemente "funciona": **recall@K del discovery, precisión del routing, tokens enviados al LLM y latencia total**.


