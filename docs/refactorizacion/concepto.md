# Ajuste de 000_MiEstrategiaV1.md según Claude

**Session ID:** ses_f26644cd7ffe0eo8iIh0DmT8kR
**Created:** 9/25/2026, 2:27:34 PM
**Updated:** 9/25/2026, 5:38:08 PM

---

## User

quiero que entiendas @000_MiEstrategiaV1.md, entiendas las observaciones de declaude del apartado "Claude Dice — Revisión enfocada en exposición API/MCP y contratos". Ajusta el documento segun esas observaciones, si quedan bien aplicadas da como hecha en el listado de claude y si por el contrario no puedes marcala como pendiente.

---

## Assistant (Build · Gemini 2.5 Flash Lite (Bajo Consumo) · 3.0s)

---

## User

quiero que entiendas @000_MiEstrategiaV1.md, entiendas las observaciones de declaude del apartado "Claude Dice — Revisión enfocada en exposición API/MCP y contratos". Ajusta el documento segun esas observaciones, si quedan bien aplicadas da como hecha en el listado de claude y si por el contrario no puedes marcala como pendiente.

---

## Assistant (Build · Big Pickle · 17.8s)

_Thinking:_

Let me plan the edits. I need to apply the 7 observations from Claude's review into the document body, plus the Django note. Then mark each as "hecha" or "pendiente" in the Claude review list.

Let me think about each observation and how to apply it:

1. **Tool annotations** → add `mcp.annotations` block in §9.1 (contract schema), derived from `operation.mode`. Add a new rule or subsection. Apply: YES.

2. **Description as contract** → add `usage_notes` / `disambiguation` field to contract in §9.1, and enrich the §9.3 example description. Apply: YES.

3. **Scaling catalog** → P2, add to §16.3 (or §16.2 pendientes) — namespacing by domain or multiple MCP servers. Apply: YES (annotate as pending P2).

4. **Versioning vs MCP** → modify R10 to state MCP exposes only current version; coexistence resolved in REST. Apply: YES.

5. **Error taxonomy → LLM view** → add serialization of each error type into tool result content (isError: true). Apply: YES.

6. **MCP transport → P0** → move "transporte MCP" from §16.3 open decisions to P0 in §16.1, and update §3 priority table. Apply: YES.

7. **Rate/concurrency limit per tool** → add `max_calls_per_session` informal field to contract. Apply: YES.

Plus the Django note → add explicit note in document (e.g., a new subsection in §15 or §16.3 clarifying that Django is a consumer, not the enablement layer). Apply: YES — as an explicit statement. Mark it as "hecha" in the sense the note is now explicit... but is it a decision that needs confirmation? I should mark it as partially pending: the ambiguity of "was Django meant to be the enablement layer" is a business decision that needs confirming. I'll add the note in the doc and mark as "✅ aplicada la aclaración / ⚠️ pendiente confirmar la intención original". Let me be careful with the marking.

Let me now do the edits. Also need to update §3 priority table with the new P0 (transporte MCP) and maybe P2 catalog scaling.

Let me write the edits.

Edit 1: R4 — tie annotations to READ→ANALYZE→ACT. Actually observation 1 says "esa jerarquía de riesgo ya diseñada debería ser las annotations, no vivir aparte." So add to R4 a mapping to annotations.

Edit 2: R10 — add MCP versioning constraint.

Edit 3: R6 or new section — description as contract. Maybe extend R6 (MCP adapter contract). Good spot: R6 mentions name/description/schema. Add rule that description is a contract in prose: must include when NOT to use + examples.

Edit 4: New rule R17? The document is R1–R16. Adding new rules could be cleaner: R17 (protocolo MCP: annotations + description), R18 (errores hacia el LLM), R19 (tráfico de agente / rate), R20 (escalado del catálogo). Hmm, but maybe better to keep them where relevant. But the doc's "En síntesis" from Claude refers to "la capa protocolo MCP real". I think adding a dedicated section in §9 or a new group of rules is cleanest. Let me add rules R17–R20 in section 2, since section 2 is "Reglas que dicta el documento". That keeps the "no information lost" and gives a home for the new decisions.

Actually, careful: adding R17-R20 plus edits to §9 creates duplication. But rules are the durable statement; §9 is the concrete contract. Duplication is acceptable in this doc's style (R2/R9 also get repeated in §9). I'll do:

- R17 — El protocolo MCP es parte del contrato (annotations + description como contrato).
- R18 — Errores: traducción explícita al content del tool result.
- R19 — Tráfico de agente: límite de llamadas por sesión (no R11 asumía tráfico humano).
- R20 — Escalado del catálogo: namespacing / servidores MCP por dominio.
- R21? — Django/Vault es consumidor, no la capa. Maybe better as a note in §15 (decisiones congeladas) rather than a rule. Yes, add to §15 as a bullet + a note in §16.3.

Let me do the edits now, one at a time.

Edit A: R4 addition.

Current:
```
- **Frontera explícita de Fase 1:** las Action Tools **quedan fuera de la milla cero**. La arquitectura no necesita demostrar escritura autónoma todavía, lo cual elimina temporalmente preguntas de transacciones, rollback, idempotencia, concurrencia, autorización fina, compensación, auditoría, doble ejecución y aprobación humana.

### R5 — Separar "Tool" de "Service"
```

New: add bullet about annotations derivation + a table mapping mode → annotations. Then R17? Hmm, if I put the mapping in R4, then R17 would be redundant. Let me instead make R17 focused on: "El contrato MCP es parte del contrato de la capability" with the annotations mapping table. And in R4 just add one line pointing to R17.

Let me plan the annotation mapping table:

| `operation.mode` | readOnlyHint | destructiveHint | idempotentHint | openWorldHint |
| READ | true | false | true | false |
| ANALYZE | true | false | true | true |
| ACT (write) | false | según caso | a definir | true |

Good.

Now let's write edits.

For §9.1 contract schema, add fields:

```yaml
id:
version:

name:
description:          # contrato en prosa: qué hace + cuándo usarla
usage_notes:          # cuándo NO usarla / cómo diferenciarla de otras similares
purpose:

operation:
  mode: READ

mcp:                   # proyección al protocolo MCP
  enabled: true
  tool: consultar_disponibilidad
  annotations:         # derivadas de operation.mode, no escritas a mano
    readOnlyHint: true
    destructiveHint: false
    idempotentHint: true
    openWorldHint: false
...
errors:
  ValidationError:
    is_error: true
    message: ...
  NotFoundError: ...

agent_traffic:
  max_calls_per_session: 10   # límite blando, declarado desde el día 1
```

Hmm the errors section in §9.1 is a list; I'll make it a mapping with serialization. Let me keep it simple.

Let me write all edits now.

Also §9.3 ficha: add usage_notes, mcp.annotations, errors mapping, agent_traffic. And enrich description.

Also §7.3: add MCP serialization table.

Also §3 priority table: add P0 "Transporte MCP" and P2 "Escalado de catálogo de tools".

Also §16.1: add P0 items. §16.2: add P2 catalog scaling. §16.3: remove "Framework/transporte del server MCP" and replace with a note that it's P0 with criteria, plus add Django clarification.

Also §5.3 security: add note that transport determines auth per request; decision criteria.

Also §15: add Django/Vault bullet.

Then update the Claude review list with ✅/⚠️ status per point.

Let's go. I'll use the edit tool.

Voy a aplicar las 7 observaciones de Claude al cuerpo del documento y luego marcar cada punto en su listado.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "oldString": "- Ser **conservador** con las Action Tools.\n- Primero exponer lecturas, después análisis, y recién al final acciones.\n- Esto permite demostrar valor rápido con bajo riesgo operacional.\n- **Frontera explícita de Fase 1:** las Action Tools **quedan fuera de la milla cero**. La arquitectura no necesita demostrar escritura autónoma todavía, lo cual elimina temporalmente preguntas de transacciones, rollback, idempotencia, concurrencia, autorización fina, compensación, auditoría, doble ejecución y aprobación humana.\n\n### R5 — Separar \"Tool\" de \"Service\"",
  "newString": "- Ser **conservador** con las Action Tools.\n- Primero exponer lecturas, después análisis, y recién al final acciones.\n- Esto permite demostrar valor rápido con bajo riesgo operacional.\n- **Frontera explícita de Fase 1:** las Action Tools **quedan fuera de la milla cero**. La arquitectura no necesita demostrar escritura autónoma todavía, lo cual elimina temporalmente preguntas de transacciones, rollback, idempotencia, concurrencia, autorización fina, compensación, auditoría, doble ejecución y aprobación humana.\n- **Esta jerarquía de riesgo no puede vivir solo en la capa interna:** se proyecta al protocolo MCP como `annotations` nativas (ver R17), para que el agente reciba la señal sin necesidad de ejecutar la tool.\n\n### R5 — Separar \"Tool\" de \"Service\""
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.0s)

_Thinking:_

Now R6 — description as contract.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### R6 — El MCP Adapter no implementa lógica\n\n- El MCP Adapter conoce: `Tool name`, `Description`, `Input schema`, `Output schema`.\n- Pero **no implementa la lógica**: delega en el service.\n- El nombre MCP no debería ser una copia automática del nombre Python: MCP tiene un **contrato semántico propio**.\n- **La `description` es contrato, no documentación.** Es lo único que el LLM lee para decidir *cuándo* usar la tool y con qué argumentos: es tan vinculante como el JSON Schema, solo que en prosa (ver R17).\n\n### R7 — Todo delegate poder de negocio: exponer conocimiento, no tablas\n",
  "oldString": "### R6 — El MCP Adapter no implementa lógica\n\n- El MCP Adapter conoce: `Tool name`, `Description`, `Input schema`, `Output schema`.\n- Pero **no implementa la lógica**: delega en el service.\n- El nombre MCP no debería ser una copia automática del nombre Python: MCP tiene un **contrato semántico propio**.\n\n### R7 — Todo delegate poder de negocio: exponer conocimiento, no tablas\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.1s)

Ahora R10 (versionado vs MCP):

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- Durante el Strangler, `consultar_disponibilidad.v1` y `.v2` **pueden coexistir temporalmente**. Mucho más limpio que `consultar_disponibilidad_v1`.\n- **Restricción específica de MCP:** la coexistencia de versiones **no se proyecta al tool list**. En MCP cada versión sería una entrada más de la lista de tools que ve el agente, y dos tools casi idénticas sin señal de cuál偏好 degradan la calidad de la respuesta.\n  - **MCP expone siempre una sola versión: la vigente del contrato.** El nombre de la tool no lleva sufijo de versión.\n  - **La coexistencia v1/v2 durante el Strangler se resuelve en REST**, que tolera bien rutas versionadas (`/api/v1/...`, `/api/v2/...`).\n  - La deprecación se comunica por `description` / `usage_notes` de la versión vigente (\"esta tool reemplaza a la anterior; no la busques por otro nombre\"), no por duplicar entradas.\n\n### R11 — Medir antes de optimizar (Measure before optimize)\n",
  "oldString": "- Durante el Strangler, `consultar_disponibilidad.v1` y `.v2` **pueden coexistir temporalmente**. Mucho más limpio que `consultar_disponibilidad_v1`.\n\n### R11 — Medir antes de optimizar (Measure before optimize)\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.5s)

_Thinking:_

Oops, I accidentally included a Chinese character "偏好" — that was a mistake (I meant "cuál preferir"). Let me fix that.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "  - **MCP expone siempre una sola versión: la vigente del contrato.** El nombre de la tool no lleva sufijo de versión.\n  - **La coexistencia v1/v2 durante el Strangler se resuelve en REST**, que tolera bien rutas versionadas (`/api/v1/...`, `/api/v2/...`).\n  - La deprecación se comunica por `description` / `usage_notes` de la versión vigente (\"esta tool reemplaza a la anterior\"), no por duplicar entradas.",
  "oldString": "  - **MCP expone siempre una sola versión: la vigente del contrato.** El nombre de la tool no lleva sufijo de versión.\n  - **La coexistencia v1/v2 durante el Strangler se resuelve en REST**, que tolera bien rutas versionadas (`/api/v1/...`, `/api/v2/...`).\n  - La deprecación se comunica por `description` / `usage_notes` de la versión vigente (\"esta tool reemplaza a la anterior; no la busques por otro nombre\"), no por duplicar entradas."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.6s)

_Thinking:_

Also fix R11 — mention that measure before optimize assumes human traffic, not agent loops. Let me add a bullet to R11 pointing to R19.

Let me read the R11 section as it currently is.

R11:
```
### R11 — Medir antes de optimizar (Measure before optimize)

- **No construir cache ni infraestructura de performance speculativa.**
- Primero observar la operación real:

```text
query duration
rows
frequency
CPU
connection pool
```

- Si se descubre por ejemplo ...
- Si se descubre `calcular_produccion ...`
```

Add a bullet: "- **Límite del supuesto:** R11 asume tráfico humano. El tráfico de agente en loop (un mismo agente llamando 20 veces a la misma tool en una sesión) es carga real sobre Oracle aunque sea solo lectura → ver R19."

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### R11 — Medir antes de optimizar (Measure before optimize)\n\n- **No construir cache ni infraestructura de performance speculativa.**\n- **Límite del supuesto:** R11 modela tráfico humano. El tráfico de agente en loop (un mismo agente invocando muchas veces la misma tool dentro de una sesión) es carga real contra Oracle productivo aunque la tool sea de solo lectura. Se cubre aparte en R19.\n- Primero observar la operación real:",
  "oldString": "### R11 — Medir antes de optimizar (Measure before optimize)\n\n- **No construir cache ni infraestructura de performance speculativa.**\n- Primero observar la operación real:"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 1.5s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "offset": 183,
  "limit": 30
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
183: - **No construir cache ni infraestructura de performance especulativa.**
184: - Primero observar la operación real:
185: 
186: ```text
187: query duration
188: rows
189: frequency
190: CPU
191: connection pool
192: ```
193: 
194: - Si se descubre por ejemplo `consultar_disponibilidad · 183ms · 42 rows · 50 calls/día`, no se necesita cache.
195: - Si se descubre `calcular_produccion · 7.8s · 500k rows · 1000 calls/día`, recién ahí se analizan opciones:
196: 
197: ```text
198: cache
199: materialized view
200: precalculation
201: read replica
202: Oracle tuning
203: warehouse
204: ```
205: 
206: ### R12 — Gobernanza de datos clínicos (qué cruza hacia la IA)
207: 
208: El sistema es clínico. Una cadena `Oracle → Python → MCP → LLM` exige responder:
209: 
210: > **¿Qué datos pueden cruzar realmente el límite hacia una IA?**
211: 
212: - Debe formar parte del Tool Contract:

(Showing lines 183-212 of 1330. Use offset=213 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **No construir cache ni infraestructura de performance speculativa.**\n- **Límite del supuesto:** R11 modela tráfico humano. El tráfico de agente en loop (un mismo agente invocando muchas veces la misma tool dentro de una sesión) es carga real contra Oracle productivo aunque la tool sea de solo lectura. Se cubre aparte en R19.\n- Primero observar la operación real:",
  "oldString": "- **No construir cache ni infraestructura de performance speculativa.**\n- Primero observar la operación real:"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 1.8s)

_Thinking:_

Odd. Maybe there are non-breaking characters or the file uses different line endings. Let me check the raw bytes around there.

Actually, maybe the issue is the em dash or something. Let's check with grep.

**Tool: bash**

**Input:**
```json
{
  "command": "sed -n '182,185p' /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md | od -c | head -20"
}
```

**Output:**
```
0000000   \n   -       *   *   N   o       c   o   n   s   t   r   u   i
0000020    r       c   a   c   h   e       n   i       i   n   f   r   a
0000040    e   s   t   r   u   c   t   u   r   a       d   e       p   e
0000060    r   f   o   r   m   a   n   c   e       e   s   p   e   c   u
0000100    l   a   t   i   v   a   .   *   *  \n   -       P   r   i   m
0000120    e   r   o       o   b   s   e   r   v   a   r       l   a    
0000140    o   p   e   r   a   c   i   ó  **   n       r   e   a   l   :
0000160   \n  \n                                                        
0000162

```

---

## Assistant (Build · Big Pickle · 2.6s)

_Thinking:_

The text looks normal. So why did edit fail? Perhaps because the `oldString` appears... no, it said "could not find". Hmm, maybe the issue is the em-dash? No, there's no em dash. Let me try a smaller unique string.

Wait — maybe my previous edit (R10) already... no. Let me just try again with exact text "### R11 — Medir antes de optimizar" to see if em dash matches.

Actually the first attempt included the header line with an em dash "—". The second attempt didn't include the header. Hmm, both failed. Let me retry.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **No construir cache ni infraestructura de performance speculativa.**\n- **Límite del supuesto:** R11 modela tráfico humano, no tráfico de agente en loop (ver R19).\n- Primero observar la operación real:",
  "oldString": "- **No construir cache ni infraestructura de performance speculativa.**\n- Primero observar la operación real:"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 2.7s)

_Thinking:_

Strange. Maybe the file has a BOM or the read tool showed a cached version? Let me check whether the file content is different from what read shows — maybe there are trailing spaces. od showed "- Primero observar la operación real:" followed by \n. And the line before: "- **No construir cache ni infraestructura de performance especulativa.**\n". That's exactly what I have.

Unless... the tool compares against something else. Let me try grep to confirm the exact text.

Actually maybe the issue: the `oldString` I pass contains a non-breaking space in "cache"? od shows regular spaces.

Hmm, wait. Maybe my newString/oldString gets transformed. Let me try using a distinctive single line as oldString.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **Límite del supuesto:** R11 modela tráfico humano, no tráfico de agente en loop (ver R19).\n- Primero observar la operación real:",
  "oldString": "- Primero observar la operación real:"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 1.9s)

_Thinking:_

It worked with a single line. So multi-line oldString matching is flaky here (maybe due to how I typed it). I'll use single-line anchors going forward where possible.

Now add the new rules R17–R20 after R16. Let me read the R16 section.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "offset": 278,
  "limit": 28
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
278:     SL[SERVICE LAYER] --> AP[API] --> APP[Aplicación / Dashboard]
279:     SL --> MC[MCP] --> AG[IA / Agentes]
280:     SL --> JB[Jobs] --> AU[Automatización / Alertas]
281: ```
282: 
283: Ejemplo: `calcular_stock_proyectado()` puede ser a la vez una API para dashboard, una MCP Tool para un agente y un job nocturno de alertas.
284: 
285: ---
286: 
287: ## 3. Priorización de decisiones: ahora vs pendiente
288: 
289: **Las brechas no son 10 problemas equivalentes.** Algunas son decisiones de la milla cero, otras se preparan sin implementarse, y otras son transversales.
290: 
291: | Prioridad | Tema                             | ¿Resolver ahora?        |
292: | --------- | -------------------------------- | ----------------------- |
293: | 🔴 P0     | Caso de negocio #1 (capability patrón) | Sí                  |
294: | 🔴 P0     | Seguridad / identidad            | Sí                      |
295: | 🔴 P0     | Observabilidad                   | Sí                      |
296: | 🔴 P0     | Contratos Pydantic / JSON Schema | Sí                      |
297: | 🔴 P0     | Testing mínimo                   | Sí                      |
298: | 🔴 P0     | Gobernanza de datos (qué cruza a IA) | Sí, por capability  |
299: | 🟠 P1     | Calidad / confiabilidad de datos | Sí, pero por capability |
300: | 🟠 P1     | Versionado                       | Definir convención      |
301: | 🟢 P2     | Action Tools / transacciones     | Diseñar, no implementar |
302: | 🟢 P2     | Cache / performance avanzada     | Medir antes             |
303: | 🟢 P2     | PostgreSQL / Strangler           | Mantener como evolución |
304: 
305: > **No se necesita resolver toda la arquitectura futura para comenzar la milla cero.**

(Showing lines 278-305 of 1331. Use offset=306 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 12.1s)

Ahora inserto las reglas nuevas R17–R20 al final de §2:

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "Ejemplo: `calcular_stock_proyectado()` puede ser a la vez una API para dashboard, una MCP Tool para un agente y un job nocturno de alertas.\n\n### R17 — El contrato MCP es parte del contrato de la capability (protocolo, no solo negocio)\n\nEl Tool Contract no es solo metadata de negocio: es también **metadata de protocolo MCP**. Un agente decide *si* y *cómo* llamar una tool leyendo el schema publicado, antes de ejecutarla. Si esa señal no se proyecta al schema, el cliente MCP la pierde aunque exista en la capa interna.\n\n**a) Annotations nativas, derivadas — nunca escritas a mano de `operation.mode`:**\n\n| `operation.mode` | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` |\n| ----------------- | -------------- | ----------------- | ---------------- | --------------- |\n| `READ`            | `true`         | `false`           | `true`           | `false`         |\n| `ANALYZE`         | `true`         | `false`           | `true`           | `true`          |\n| `ACT`             | `false`        | según caso        | a definir        | `true`          |\n\n- `readOnlyHint: true` permite que los clientes MCP pidan menos confirmación en tools de solo lectura — es la proyección nativa de R4.\n- `openWorldHint` distingue si la tool interactúa con sistemas externos (notificaciones, Agenda externa) más allá de la base de datos.\n- La derivación es **automática en el registry**: si alguien declara `mode: ACT` y el `readOnlyHint` queda en `true`, el contract test (§12, Nivel 3) falla.\n\n**b) La `description` es el contrato de facto, en prosa:**\n\nLa descripción en lenguaje natural es lo único que el LLM ve para decidir *cuándo* usar la tool y con qué argumentos. Con 10-30 capabilities activas, cada una debe declarar explícitamente:\n\n- **qué hace** (una línea, sin jerga legacy),\n- **cuándo usarla**,\n- **cuándo NO usarla** — para diferenciarla de la tool parecida (`usage_notes` / `disambiguation`),\n- **1-2 ejemplos de input/output correcto** (`examples`).\n\n> Una tool sin `usage_notes` y sin ejemplos es un contrato incompleto aunque el JSON Schema sea perfecto.\n\n### R18 — Todo error se traduce al `content` del tool result\n\n- La taxonomía de errores (R7 §7.3) está escrita para código Python; el agente la consume como **texto dentro del tool result**.\n- En MCP el error no debe perderse en la capa de transporte: se devuelve `isError: true` con un mensaje legible en el mismo turno, para que el LLM pueda razonar y reintentar.\n- Cada tipo de error declara su serialización en el contrato: `error_code` estable + mensaje accionable, nunca el traceback.\n\n```yaml\nerrors:\n  ValidationError:\n    is_error: true\n    error_code: INVALID_ARGUMENT\n    message: \"Argumentos inválidos: revisa fecha (YYYY-MM-DD) y unidad.\"\n  NotFoundError:\n    is_error: true\n    error_code: NO_DATA\n    message: \"No hay disponibilidad para esa fecha/unidad. Es un resultado válido, no un fallo.\"\n  InfrastructureError:\n    is_error: true\n    error_code: UNAVAILABLE\n    message: \"No pude consultar los datos. Reintenta; si persiste, escala a TI.\"\n```\n\n- **Contrato clave para el LLM:** `NO_DATA` es un resultado válido; `UNAVAILABLE` es un fallo. Nunca deben verse iguales.\n\n### R19 — El tráfico de agente es tráfico real: límites por tool\n\n- R11 asume tráfico humano. Un agente investigando (§8.2) puede **iterar y repetir** llamadas a la misma tool dentro de una sola sesión. Contra Oracle productivo eso es carga, aunque todo sea lectura.\n- El contrato declara un límite **informal desde el día 1** (aunque la Fase 1 no lo aplique todavía):\n\n```yaml\nagent_traffic:\n  max_calls_per_session: 10   # límite blando, declarado y observable\n  expected_cost: low          # low | medium | high — define si la tool necesita cache (R11)\n```\n\n- El enforcement real (rate limit por sesión, por usuario, por tool) es **P1**: en la milla cero basta con medir y alertar.\n- Este campo también ordena la lista: una tool con `expected_cost: high` es candidata natural a cacheado, y eso se decide con dato, no por intuición.\n\n### R20 — El catálogo de tools tiene que escalar\n\n- Con 2-5 tools, un único servidor MCP con lista plana funciona. **Con 20-50 satura el contexto del agente y degrada la precisión de selección de tool.**\n- Criterio de escalado (a decidir antes de llegar a ~15 tools registradas, no antes):\n  - **Namespacing por dominio:** `agenda.consultar_disponibilidad` como **nombre real de la tool** (no solo el `id` interno), manteniendo `consultar_disponibilidad` como nombre canónico de la capability (R1).\n  - **Varios servidores MCP por área de negocio** en vez de uno monolítico, manteniendo un mismo service layer detrás.\n- En Fase 1 se registra el dominio (`id: agenda.disponibilidad`) y se construye el registry de forma que el namespacing sea un cambio de proyección, no de lógica de negocio.\n- **P2 en la práctica:** no bloquea la milla cero, pero condiciona el diseño del registry desde el inicio.\n",
  "oldString": "Ejemplo: `calcular_stock_proyectado()` puede ser a la vez una API para dashboard, una MCP Tool para un agente y un job nocturno de alertas."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.6s)

Ahora actualizo la tabla de priorización (§3):

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "| Prioridad | Tema                             | ¿Resolver ahora?        |\n| --------- | -------------------------------- | ----------------------- |\n| 🔴 P0     | Caso de negocio #1 (capability patrón) | Sí                  |\n| 🔴 P0     | Seguridad / identidad            | Sí                      |\n| 🔴 P0     | **Transporte MCP** (condiciona auth y enforcement point) | **Sí**          |\n| 🔴 P0     | Observabilidad                   | Sí                      |\n| 🔴 P0     | Contratos Pydantic / JSON Schema | Sí                      |\n| 🔴 P0     | **Proyección al protocolo MCP** (annotations + `description` como contrato) | **Sí** |\n| 🔴 P0     | Testing mínimo                   | Sí                      |\n| 🔴 P0     | Gobernanza de datos (qué cruza a IA) | Sí, por capability  |\n| 🟠 P1     | Calidad / confiabilidad de datos | Sí, pero por capability |\n| 🟠 P1     | Versionado (REST versioning en Strangler) | Definir convención      |\n| 🟠 P1     | Límites de tráfico de agente (rate/concurrencia por tool) | Declarar, medir      |\n| 🟢 P2     | Action Tools / transacciones     | Diseñar, no implementar |\n| 🟢 P2     | Cache / performance avanzada     | Medir antes             |\n| 🟢 P2     | Escalado del catálogo de tools (namespacing / split por dominio) | Diseñar, no implementar |\n| 🟢 P2     | PostgreSQL / Strangler           | Mantener como evolución |",
  "oldString": "| Prioridad | Tema                             | ¿Resolver ahora?        |\n| --------- | -------------------------------- | ----------------------- |\n| 🔴 P0     | Caso de negocio #1 (capability patrón) | Sí                  |\n| 🔴 P0     | Seguridad / identidad            | Sí                      |\n| 🔴 P0     | Observabilidad                   | Sí                      |\n| 🔴 P0     | Contratos Pydantic / JSON Schema | Sí                      |\n| 🔴 P0     | Testing mínimo                   | Sí                      |\n| 🔴 P0     | Gobernanza de datos (qué cruza a IA) | Sí, por capability  |\n| 🟠 P1     | Calidad / confiabilidad de datos | Sí, pero por capability |\n| 🟠 P1     | Versionado                       | Definir convención      |\n| 🟢 P2     | Action Tools / transacciones     | Diseñar, no implementar |\n| 🟢 P2     | Cache / performance avanzada     | Medir antes             |\n| 🟢 P2     | PostgreSQL / Strangler           | Mantener como evolución |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.8s)

Ahora §5.3 (transporte MCP como decisión P0) y §5.4:

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "offset": 528,
  "limit": 30
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
528:     AG[AI Client / Agent] --> AUTH[Authentication] --> FM[FastMCP] --> AZ[Authorization] --> SVC[Service]
529: ```
530: 
531: ### 5.4 Regla de enforcement
532: 
533: > **La autorización debe ocurrir antes de ejecutar la capability, no dentro de la query Oracle.**
534: 
535: Requiere un **enforcement point único** (middleware/decorator), no lógica dispersa en cada service.
536: 
537: ---
538: 
539: ## 6. Observabilidad (obligatoria desde el día 1)
540: 
541: ### 6.1 Por qué
542: 
543: La cadena `CEO → LLM → Agent → Tool → Service → Oracle` es nueva. Si el CEO pregunta "¿dónde estamos perdiendo ocupación?" y la IA responde algo incorrecto, debe poder reconstruirse la investigación completa:
544: 
545: ```mermaid
546: graph TD
547:     CEO[CEO] --> P[Pregunta] --> LLM[LLM] --> PLAN[Plan del agente]
548:     PLAN --> T1[Tool 1 · argumentos → resultado]
549:     T1 --> T2[Tool 2 · argumentos → resultado]
550:     T2 --> FIN[Respuesta final]
551: ```
552: 
553: Eso es **trazabilidad de investigación**.
554: 
555: ### 6.2 Dos niveles
556: 
557: **A. Observabilidad técnica:**

(Showing lines 528-557 of 1410. Use offset=558 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 5.8s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "    AG[AI Client / Agent] --> AUTH[Authentication] --> FM[FastMCP] --> AZ[Authorization] --> SVC[Service]\n```\n\n### 5.4 Regla de enforcement\n\n> **La autorización debe ocurrir antes de ejecutar la capability, no dentro de la query Oracle.**\n\nRequiere un **enforcement point único** (middleware/decorator), no lógica dispersa en cada service.\n\n### 5.5 El transporte MCP es decisión P0, no infraestructura diferible\n\nEl diagrama anterior **assume transporte remoto con autenticación por request**. Eso no es un detalle de infraestructura: condiciona directamente el enforcement point único.\n\n- Si el transporte es **local/in-process** (el agente corre junto al server), no hay identidad de request que evaluar: el modelo de autorización hay que redefinirlo (identidad de proceso/sesión).\n- Si el transporte es **remoto** (HTTP / SSE / streamable HTTP), la identidad viaja por request y el enforcement point puede ser middleware único para REST y MCP.\n\n**Criterio de decisión (a cerrar antes de codificar la capability #1):**\n\n| Criterio | Pregunta que decide |\n| -------- | ------------------- |\n| Autenticación | ¿Cómo viaja la identidad del agente en cada request? (token, API key, mTLS) |\n| Enforcement | ¿Puede un único punto de enforcement cubrir REST y MCP? |\n| Red | ¿El agente corre en la misma red que Oracle / Payara? |\n| Streaming | ¿Se necesita respuesta incremental o basta respuesta por llamada? |\n| Framework | FastMCP ya resuelve el transporte; lo que hay que fijar es **cuál** y **con qué auth** |\n\n- **Restricción:** si el transporte elegido no soporta identidad por request, **el enforcement point único de R8 no es implementable tal como estáRule** → hay que revisarlo antes de escribir código de seguridad.\n\n---",
  "oldString": "    AG[AI Client / Agent] --> AUTH[Authentication] --> FM[FastMCP] --> AZ[Authorization] --> SVC[Service]\n```\n\n### 5.4 Regla de enforcement\n\n> **La autorización debe ocurrir antes de ejecutar la capability, no dentro de la query Oracle.**\n\nRequiere un **enforcement point único** (middleware/decorator), no lógica dispersa en cada service.\n\n---"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.5s)

_Thinking:_

I made a typo: "no es implementable tal como estáRule" — fix.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **Restricción:** si el transporte elegido no soporta identidad por request, **el enforcement point único de R8 no es implementable tal como está definido** → hay que revisarlo antes de escribir código de seguridad.",
  "oldString": "- **Restricción:** si el transporte elegido no soporta identidad por request, **el enforcement point único de R8 no es implementable tal como estáRule** → hay que revisarlo antes de escribir código de seguridad."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.0s)

Ahora §7.3 (erreros vistos por el LLM):

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 30,
  "offset": 645
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
645: ### 7.2 Convergencia de contratos
646: 
647: ```mermaid
648: graph TD
649:     PC[Pydantic Contract] --> FA[FastAPI · OpenAPI]
650:     PC --> FM[FastMCP · Tool Schema]
651: ```
652: 
653: Es exactamente el tipo de convergencia que se busca entre las interfaces.
654: 
655: ### 7.3 Taxonomía de errores común
656: 
657: No dejar que cada service invente sus errores. Taxonomía única:
658: 
659: ```text
660: DomainError
661: ├── ValidationError
662: ├── NotFoundError
663: ├── BusinessRuleError
664: ├── AuthorizationError
665: └── InfrastructureError
666: ```
667: 
668: - `ValidationError`: por ejemplo `fecha = "banana"`.
669: - `NotFoundError`: "no existen datos".
670: - `InfrastructureError`: `Oracle unavailable`, `timeout`, `connection pool exhausted`.
671: 
672: **Crítico para agentes:** el LLM debe distinguir *"no existen datos"* (resultado válido) de *"no pude consultar los datos"* (fallo de infraestructura). Son cosas radicalmente diferentes.
673: 
674: ---

(Showing lines 645-674 of 1429. Use offset=675 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 5.3s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Crítico para agentes:** el LLM debe distinguir *\"no existen datos\"* (resultado válido) de *\"no pude consultar los datos\"* (fallo de infraestructura). Son cosas radicalmente diferentes.\n\n### 7.4 Cómo ve el LLM cada error (traducción al protocolo)\n\nLa taxonomía de arriba está escrita en términos de excepciones Python. El agente nunca la lee así: la consume como **texto dentro del `content` del tool result**.\n\n- **Regla de transporte:** el error **no se propaga como excepción de protocolo**; se devuelve `isError: true` con el mensaje en el resultado, para que el LLM lo lea en el mismo turno y pueda corregir o reintentar. Perderlo a nivel de transporte es perder la información.\n- **Regla de contenido:** nunca traceback. Un `error_code` estable + un mensaje accionable.\n\n| Error Python         | `error_code` REST/HTTP | Traducción MCP                            | Lectura del agente                |\n| -------------------- | --------------------- | ------------------------------------------ | --------------------------------- |\n| `ValidationError`    | `400 INVALID_ARGUMENT` | `isError: true` + código + mensaje        | \"mis argumentos están mal, corrijo\" |\n| `NotFoundError`      | `404 NO_DATA`          | `isError: true` + código + mensaje        | \"no hay datos\" (resultado válido) |\n| `BusinessRuleError`  | `422 BUSINESS_RULE`    | `isError: true` + código + regla violada  | \"la regla X no se cumple\"          |\n| `AuthorizationError` | `403 FORBIDDEN`        | `isError: true` + código (sin detalle)    | \"no puedo, no reintento\"           |\n| `InfrastructureError`| `503 UNAVAILABLE`      | `isError: true` + código + \"reintenta\"     | \"falla la fuente, reintento\"       |\n\n- El mapeo vive en **un solo lugar** (el translator de errores del adapter MCP), no en cada service.\n- `AuthorizationError` **nunca** revela qué regla de autorización falló: el agente solo necesita saber que debe detenerse.\n\n---\n",
  "oldString": "**Crítico para agentes:** el LLM debe distinguir *\"no existen datos\"* (resultado válido) de *\"no pude consultar los datos\"* (fallo de infraestructura). Son cosas radicalmente diferentes.\n\n---\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.1s)

Ahora §9.1 (contrato evolucionado) y §9.3 (ficha YAML):

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 55,
  "offset": 712
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
712: 
713: ### 8.2 Investigación guiada por IA (caso CEO)
714: 
715: Un agente **investiga**, en lugar de solo responder sobre un dataset prearmado.
716: 
717: > Pregunta del CEO: *"¿Dónde estamos teniendo problemas con las horas agendadas?"*
718: 
719: ```mermaid
720: graph LR
721:     A[consultar_ocupacion_agenda] --> B[comparar_ocupacion_historica] --> C[identificar_unidades_con_caida] --> D[analizar_causas_probables]
722: ```
723: 
724: ### 8.3 La nueva arquitectura crea capacidades nuevas
725: 
726: Una capability puede no tener equivalente directo en el legacy (`identificar_pacientes_con_riesgo_de_inasistencia`). **No importa**: la nueva arquitectura puede crear capacidades que antes no existían — punto fundamental para la estrategia **AI First**.
727: 
728: ---
729: 
730: ## 9. Tool Contract interno
731: 
732: ### 9.1 Contrato evolucionado
733: 
734: El contrato de cada tool define los siguientes campos:
735: 
736: ```yaml
737: id:
738: version:
739: 
740: name:
741: description:
742: purpose:
743: 
744: operation:
745:   mode: READ
746: 
747: input:
748:   schema:
749: 
750: output:
751:   schema:
752: 
753: business_rules:
754: 
755: data:
756:   sources:
757:   classification:
758:   pii:
759:   ai_allowed:
760:   allowed_fields:
761:   forbidden_fields:
762: 
763: security:
764:   roles:
765:   authorization:
766: 

(Showing lines 712-766 of 1447. Use offset=767 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "```yaml\nid:\nversion:\n\nname:                      # nombre canónico de la capability (R1)\ndescription:                # contrato en prosa: qué hace + cuándo usarla\nusage_notes:               # cuándo NO usarla / cómo se diferencia de las parecidas\npurpose:\n\noperation:\n  mode: READ               # READ | ANALYZE | ACT  → fuente de las annotations\n\nmcp:                       # proyección al protocolo MCP\n  enabled: true\n  tool: consultar_disponibilidad\n  annotations:             # DERIVADAS de operation.mode, no escritas a mano (R17)\n    readOnlyHint: true\n    destructiveHint: false\n    idempotentHint: true\n    openWorldHint: false\n\ninput:\n  schema:\n\noutput:\n  schema:\n\nbusiness_rules:\n\ndata:\n  sources:\n  classification:\n  pii:\n  ai_allowed:\n  allowed_fields:\n  forbidden_fields:\n\nsecurity:\n  roles:\n  authorization:\n",
  "oldString": "```yaml\nid:\nversion:\n\nname:\ndescription:\npurpose:\n\noperation:\n  mode: READ\n\ninput:\n  schema:\n\noutput:\n  schema:\n\nbusiness_rules:\n\ndata:\n  sources:\n  classification:\n  pii:\n  ai_allowed:\n  allowed_fields:\n  forbidden_fields:\n\nsecurity:\n  roles:\n  authorization:\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.5s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 30,
  "offset": 776
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
776: 
777: errors:
778: 
779: observability:
780: 
781: performance:
782:   expected_duration:
783:   cacheable:
784: 
785: legacy:
786:   helper:
787: 
788: examples:
789: ```
790: 
791: No es necesario implementar todos los campos el primer día, pero el **contrato conceptual queda definido desde el inicio**.
792: 
793: ### 9.2 Ejemplo clásico de contrato (verbo/lectura)
794: 
795: ```text
796: disponibilidad_dia
797: 
798: Purpose:
799: Consultar disponibilidad de agenda clínica para una fecha.
800: 
801: Input:
802:     fecha: YYYY-MM-DD
803:     unidad: optional
804: 
805: Output:

(Showing lines 776-805 of 1457. Use offset=806 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.6s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "errors:                     # cada tipo declara su traducción al content MCP (R18)\n  ValidationError:\n    error_code: INVALID_ARGUMENT\n    message:\n  NotFoundError:\n    error_code: NO_DATA\n    message:\n  InfrastructureError:\n    error_code: UNAVAILABLE\n    message:\n\nobservability:\n\nperformance:\n  expected_duration:\n  cacheable:\n\nagent_traffic:              # tráfico de agente, no humano (R19)\n  max_calls_per_session: 10\n  expected_cost: low\n\nlegacy:\n  helper:\n\nexamples:\n```\n\nNo es necesario implementar todos los campos el primer día, pero el **contrato conceptual queda definido desde el inicio**. Los que sí son obligatorios desde la capability #1, porque el contrato incompleto rompe al agente: `description`, `usage_notes`, `operation.mode`, `mcp.annotations`, `errors` y `examples`.\n",
  "oldString": "errors:\n\nobservability:\n\nperformance:\n  expected_duration:\n  cacheable:\n\nlegacy:\n  helper:\n\nexamples:\n```\n\nNo es necesario implementar todos los campos el primer día, pero el **contrato conceptual queda definido desde el inicio**."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.0s)

Ahora la ficha completa del §9.3:

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 70,
  "offset": 820
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
820:     unidad
821:     estación
822:     profesional
823:     hora
824:     estado
825: 
826: Data:
827:     CALENDAR_DOC
828:     UNIDAD
829:     ...
830: 
831: Operation:
832:     READ ONLY
833: 
834: AI suitability:
835:     HIGH
836: ```
837: 
838: ### 9.3 Ficha YAML completa (ejemplo: `agenda.disponibilidad`)
839: 
840: ```yaml
841: id: agenda.disponibilidad
842: version: 1
843: 
844: name: consultar_disponibilidad
845: 
846: description: >
847:   Consulta las horas disponibles de agenda
848:   para una fecha y opcionalmente una unidad.
849: 
850: purpose: >
851:   Permitir al CEO / agente conocer la oferta
852:   horaria disponible de la clínica.
853: 
854: operation:
855:   mode: READ
856: 
857: service:
858:   python: agenda.services.consultar_disponibilidad
859: 
860: mcp:
861:   enabled: true
862:   tool: consultar_disponibilidad
863: 
864: rest:
865:   enabled: true
866:   method: GET
867:   path: /api/agenda/disponibilidad
868: 
869: legacy:
870:   helper: getAgenda
871: 
872: input:
873:   schema:
874:     fecha: date
875:     unidad: str | None
876: 
877: output:
878:   schema:
879:     fecha: date
880:     items: list[DisponibilidadItem]
881: 
882: business_rules:
883:   - unidad_debe_existir
884:   - no_incluir_horas_canceladas
885: 
886: data:
887:   sources:
888:     oracle:
889:       - CALENDAR_DOC

(Showing lines 820-889 of 1471. Use offset=890 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 4.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "id: agenda.disponibilidad\nversion: 1\n\nname: consultar_disponibilidad\n\ndescription: >\n  Consulta las horas disponibles de agenda clínica\n  para una fecha y opcionalmente una unidad.\n  Úsala cuando el usuario pregunte qué horas se pueden\n  agendar, qué cupos hay libres o por un rango de fechas\n  específico. Solo lectura: no crea, no modifica y no reserva nada.\n\nusage_notes: >\n  NO usar para: (1) ver horas ya reservadas u ocupadas —\n  eso es consultar_ocupacion; (2) comparar varios días o\n  detectar caída de ocupación — eso es una tool analítica;\n  (3) crear o cancelar una reserva — eso es una Action Tool,\n  fuera de la milla cero. Si la unidad no se indica, devuelve\n  todas las unidades de la fecha.\n\npurpose: >\n  Permitir al CEO / agente conocer la oferta\n  horaria disponible de la clínica.\n\noperation:\n  mode: READ\n\nservice:\n  python: agenda.services.consultar_disponibilidad\n\nmcp:\n  enabled: true\n  tool: consultar_disponibilidad        # sin sufijo de versión (R10)\n  annotations:                          # derivadas de operation.mode (R17)\n    readOnlyHint: true\n    destructiveHint: false\n    idempotentHint: true\n    openWorldHint: false\n",
  "oldString": "id: agenda.disponibilidad\nversion: 1\n\nname: consultar_disponibilidad\n\ndescription: >\n  Consulta las horas disponibles de agenda\n  para una fecha y opcionalmente una unidad.\n\npurpose: >\n  Permitir al CEO / agente conocer la oferta\n  horaria disponible de la clínica.\n\noperation:\n  mode: READ\n\nservice:\n  python: agenda.services.consultar_disponibilidad\n\nmcp:\n  enabled: true\n  tool: consultar_disponibilidad\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.3s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 60,
  "offset": 898
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
898: business_rules:
899:   - unidad_debe_existir
900:   - no_incluir_horas_canceladas
901: 
902: data:
903:   sources:
904:     oracle:
905:       - CALENDAR_DOC
906:       - UNIDAD
907:   classification: confidential
908:   pii: false
909:   clinical_data: false
910:   ai_allowed: yes
911:   allowed_fields:
912:     - fecha
913:     - hora
914:     - unidad
915:     - estacion
916:     - profesional
917:     - estado
918:   forbidden_fields:
919:     - rut
920:     - diagnostico
921: 
922: security:
923:   classification: internal
924:   access: read
925:   roles:
926:     - business_analyst
927:     - ai_agent
928: 
929: errors:
930:   - ValidationError
931:   - NotFoundError
932: 
933: observability:
934:   level: tech + ai
935: 
936: performance:
937:   expected_duration: <250ms
938:   cacheable: true
939: 
940: ai_suitability: HIGH
941: 
942: examples:
943:   - fecha: 2026-09-23
944:     unidad: "03"
945: ```
946: 
947: Esto crea un **catálogo de capacidades**, no simplemente un catálogo de endpoints.
948: 
949: ### 9.4 Identity Map de capacidades
950: 
951: | Concepto       | Nombre                       |
952: | -------------- | ---------------------------- |
953: | Legacy helper  | `getAgenda()`                |
954: | Capability     | `consultar_disponibilidad`   |
955: | Python service | `consultar_disponibilidad()` |
956: | MCP Tool       | `consultar_disponibilidad`   |
957: | REST resource  | `/agenda/disponibilidad`     |

(Showing lines 898-957 of 1487. Use offset=958 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "errors:\n  ValidationError:\n    is_error: true\n    error_code: INVALID_ARGUMENT\n    message: \"Argumentos inválidos. fecha debe ser YYYY-MM-DD; unidad, si viene, debe existir.\"\n  NotFoundError:\n    is_error: true\n    error_code: NO_DATA\n    message: \"No hay horas disponibles para esa fecha/unidad. Resultado válido, no es un fallo.\"\n\nobservability:\n  level: tech + ai\n\nperformance:\n  expected_duration: <250ms\n  cacheable: true\n\nagent_traffic:\n  max_calls_per_session: 10\n  expected_cost: low\n\nai_suitability: HIGH\n\nexamples:\n  - in:  { fecha: 2026-09-23, unidad: \"03\" }\n    out: { fecha: 2026-09-23, items: 42 }\n  - in:  { fecha: 2026-09-23 }\n    out: { fecha: 2026-09-23, items: 310 }   # todas las unidades\n```",
  "oldString": "errors:\n  - ValidationError\n  - NotFoundError\n\nobservability:\n  level: tech + ai\n\nperformance:\n  expected_duration: <250ms\n  cacheable: true\n\nai_suitability: HIGH\n\nexamples:\n  - fecha: 2026-09-23\n    unidad: \"03\"\n```"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.2s)

_Thinking:_

Now §9.4 Identity Map: add "Dominio MCP" row and note about namespacing. Let me read the rest.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 20,
  "offset": 965
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
965: | Legacy helper  | `getAgenda()`                |
966: | Capability     | `consultar_disponibilidad`   |
967: | Python service | `consultar_disponibilidad()` |
968: | MCP Tool       | `consultar_disponibilidad`   |
969: | REST resource  | `/agenda/disponibilidad`     |
970: | HTTP           | `GET`                        |
971: 
972: ---
973: 
974: ## 10. Tool / Service Registry → Catálogo de capacidades empresariales
975: 
976: ### 10.1 Estructura inicial (documentación estructurada)
977: 
978: ```text
979: tools/
980: ├── agenda/
981: │   ├── disponibilidad_dia.md
982: │   ├── ocupacion.md
983: │   └── horas_libres.md
984: │

(Showing lines 965-984 of 1499. Use offset=985 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.9s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "| Legacy helper  | `getAgenda()`                |\n| Capability     | `consultar_disponibilidad`   |\n| Python service | `consultar_disponibilidad()` |\n| MCP Tool       | `consultar_disponibilidad`   |\n| Dominio (id)   | `agenda`                     |\n| REST resource  | `/agenda/disponibilidad`     |\n| HTTP           | `GET`                        |\n\nEl **dominio** (`agenda`) no es un cuarto nombre de la capability: es el namespace que usará el nombre real de la tool cuando el catálogo crezca (`agenda.consultar_disponibilidad`, ver R20). El nombre canónico sigue siendo `consultar_disponibilidad`.",
  "oldString": "| Legacy helper  | `getAgenda()`                |\n| Capability     | `consultar_disponibilidad`   |\n| Python service | `consultar_disponibilidad()` |\n| MCP Tool       | `consultar_disponibilidad`   |\n| REST resource  | `/agenda/disponibilidad`     |\n| HTTP           | `GET`                        |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 1.8s)

Ahora §10.2 (registry) y §11.3 (puente MCP → Service):

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 40,
  "offset": 1005
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1005: 
1006: ```text
1007: qué hace
1008: qué datos utiliza
1009: qué reglas aplica
1010: quién puede utilizarla
1011: si puede ir a IA
1012: si es read/write
1013: qué legacy reemplaza
1014: qué API expone
1015: qué MCP expone
1016: cómo se prueba
1017: cómo se observa
1018: ```
1019: 
1020: Es un **catálogo de capacidades empresariales**, más valioso que un simple catálogo de MCP.
1021: 
1022: ### 10.3 Generación automática posterior
1023: 
1024: ```mermaid
1025: graph TD
1026:     REG[Capability Registry] --> MCP[MCP schema]
1027:     REG --> API[API schema]
1028:     REG --> DOC[Documentación]
1029:     REG --> TEST[Tests]
1030:     REG --> CAT[Catálogo para IA]
1031: ```
1032: 
1033: ---
1034: 
1035: ## 11. Estructura de código
1036: 
1037: ### 11.1 Layout del proyecto
1038: 
1039: ```text
1040: application/
1041:     agenda/
1042:         service.py
1043:         models.py
1044:         ports.py

(Showing lines 1005-1044 of 1502. Use offset=1045 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 4.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "```text\nqué hace\nqué datos utiliza\nqué reglas aplica\nquién puede utilizarla\nsi puede ir a IA\nsi es read/write\nqué legacy reemplaza\nqué API expone\nqué MCP expone\ncómo se prueba\ncómo se observa\ncuánto puede gastar un agente en esta capability\n```\n\nEs un **catálogo de capacidades empresariales**, más valioso que un simple catálogo de MCP.\n\n### 10.3 Generación automática posterior\n\n```mermaid\ngraph TD\n    REG[Capability Registry] --> MCP[MCP schema<br/>incluye annotations]\n    REG --> API[API schema]\n    REG --> DOC[Documentación]\n    REG --> TEST[Tests]\n    REG --> CAT[Catálogo para IA]\n```\n\nEl registry es la **única fuente** de la proyección MCP: de ahí salen el nombre de la tool, las annotations derivadas de `operation.mode` y la descripción. Un developer no escribe el schema MCP a mano.",
  "oldString": "```text\nqué hace\nqué datos utiliza\nqué reglas aplica\nquién puede utilizarla\nsi puede ir a IA\nsi es read/write\nqué legacy reemplaza\nqué API expone\nqué MCP expone\ncómo se prueba\ncómo se observa\n```\n\nEs un **catálogo de capacidades empresariales**, más valioso que un simple catálogo de MCP.\n\n### 10.3 Generación automática posterior\n\n```mermaid\ngraph TD\n    REG[Capability Registry] --> MCP[MCP schema]\n    REG --> API[API schema]\n    REG --> DOC[Documentación]\n    REG --> TEST[Tests]\n    REG --> CAT[Catálogo para IA]\n```"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 1.9s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 30,
  "offset": 1068
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1068: 
1069: Ambos llaman exactamente al mismo service.
1070: 
1071: ### 11.3 Puente MCP → Service (ejemplo)
1072: 
1073: ```python
1074: @mcp.tool(
1075:     name="consultar_disponibilidad",
1076:     description="""
1077:     Consulta la disponibilidad de agenda clínica
1078:     para una fecha y opcionalmente una unidad.
1079:     """
1080: )
1081: ```
1082: 
1083: ```python
1084: resultado = agenda_service.consultar_disponibilidad(
1085:     fecha=fecha,
1086:     unidad=unidad
1087: )
1088: ```
1089: 
1090: ---
1091: 
1092: ## 12. Testing (cuatro niveles)
1093: 
1094: No se necesita una batería gigantesca, pero desde el primer service se establecen los cuatro niveles:
1095: 
1096: ### Nivel 1 — Unit
1097: 

(Showing lines 1068-1097 of 1505. Use offset=1098 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 5.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### 11.3 Puente MCP → Service (ejemplo)\n\nEl adapter MCP **no inventa el contrato**: lo lee del registry y proyecta el schema MCP. En la práctica eso se ve así:\n\n```python\ncontrato = registry.get(\"agenda.disponibilidad\")\n\n@mcp.tool(\n    name=contrato.mcp.tool,                    # sin versión, sin namespace todavía\n    description=contrato.description,           # contrato en prosa, no documentación\n    annotations=contrato.mcp.annotations,       # derivadas de operation.mode\n)\n```\n\nLa descripción que ve el modelo **incluye el `usage_notes`**, porque es lo que permite diferenciar `consultar_disponibilidad` de `consultar_ocupacion` cuando ambas están registradas:\n\n```python\n@mcp.tool(\n    name=\"consultar_disponibilidad\",\n    description=\"\"\"\n    Consulta las horas disponibles de agenda clínica para una fecha\n    y opcionalmente una unidad. Úsala cuando pregunten qué horas se\n    pueden agendar o qué cupos hay libres. Solo lectura.\n\n    NO usar para: ver horas ya reservadas (usar consultar_ocupacion),\n    comparar varios días (usar una tool analítica), ni crear o cancelar\n    reservas (Action Tools, fuera de la milla cero).\n    \"\"\",\n    annotations={\n        \"readOnlyHint\": True,\n        \"destructiveHint\": False,\n        \"idempotentHint\": True,\n        \"openWorldHint\": False,\n    },\n)\n```\n\nEl cuerpo delega, sin lógica:\n\n```python\nresultado = agenda_service.consultar_disponibilidad(\n    fecha=fecha,\n    unidad=unidad\n)\n```\n\nSi la capability lanza un error, el adapter lo traduce según la tabla de §7.4 y devuelve `isError: true` con el mensaje en el `content` — nunca propaga la excepción cruda al transporte.\n",
  "oldString": "### 11.3 Puente MCP → Service (ejemplo)\n\n```python\n@mcp.tool(\n    name=\"consultar_disponibilidad\",\n    description=\"\"\"\n    Consulta la disponibilidad de agenda clínica\n    para una fecha y opcionalmente una unidad.\n    \"\"\"\n)\n```\n\n```python\nresultado = agenda_service.consultar_disponibilidad(\n    fecha=fecha,\n    unidad=unidad\n)\n```\n"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.6s)

Ahora §12 Nivel 3 (contract test con annotations) y §13/§15/§16:

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 40,
  "offset": 1140
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1140: Oracle test/snapshot
1141: ```
1142: 
1143: Prueba que la consulta funciona.
1144: 
1145: ### Nivel 3 — Contract
1146: 
1147: ```text
1148: FastAPI ──────┐
1149:               ├── Pydantic Contract
1150: FastMCP ──────┘
1151: ```
1152: 
1153: Prueba que ambos adaptadores respetan el mismo contrato.
1154: 
1155: ### Nivel 4 — AI / tool
1156: 
1157: ```text
1158: Agent
1159:  ↓
1160: Tool
1161:  ↓
1162: Service
1163: ```
1164: 
1165: No se prueba que el LLM "responda bonito", sino algo más determinista:
1166: 
1167: > Ante esta intención, ¿el agente tiene disponible la tool correcta y puede ejecutarla con los argumentos correctos?
1168: 
1169: ---
1170: 
1171: ## 13. Roadmap en fases
1172: 
1173: ### Fase 1 — Enablement
1174: 
1175: ```mermaid
1176: graph LR
1177:     O[Oracle] --> P[Python] --> S[Services] --> A[API + MCP]
1178: ```
1179: 

(Showing lines 1140-1179 of 1534. Use offset=1180 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 4.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### Nivel 3 — Contract\n\n```text\nFastAPI ──────┐\n              ├── Pydantic Contract\nFastMCP ──────┘\n```\n\nPrueba que ambos adaptadores respetan el mismo contrato. Además, en la milla cero el contract test verifica **tres invariantes del protocolo MCP** (R17, R18):\n\n1. **Annotations coherentes:** el `readOnlyHint` publicado coincide con `operation.mode`; una capability `ACT` no puede publicarse como solo lectura.\n2. **Descripción utilizable:** `description` y `usage_notes` no están vacíos, y el nombre de la tool **no lleva versión** (R10).\n3. **Errores serializados:** cada tipo de error declarado produce `isError: true` con su `error_code`, y `NO_DATA` ≠ `UNAVAILABLE` en el `content` (R18).\n\n### Nivel 4 — AI / tool\n\n```text\nAgent\n ↓\nTool\n ↓\nService\n```\n\nNo se prueba que el LLM \"responda bonito\", sino algo más determinista:\n\n> Ante esta intención, ¿el agente tiene disponible la tool correcta y puede ejecutarla con los argumentos correctos?\n\nCasos mínimos derivables del `usage_notes` de cada capability: una intención que **debe** elegir la tool y una intención parecida que **no debe** elegirla.",
  "oldString": "### Nivel 3 — Contract\n\n```text\nFastAPI ──────┐\n              ├── Pydantic Contract\nFastMCP ──────┘\n```\n\nPrueba que ambos adaptadores respetan el mismo contrato.\n\n### Nivel 4 — AI / tool\n\n```text\nAgent\n ↓\nTool\n ↓\nService\n```\n\nNo se prueba que el LLM \"responda bonito\", sino algo más determinista:\n\n> Ante esta intención, ¿el agente tiene disponible la tool correcta y puede ejecutarla con los argumentos correctos?"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.3s)

Ahora §15 (decisiones congeladas, nota Django) y §16:

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 55,
  "offset": 1288
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1288: - **Refactorización en sí:** pospuesta; la primera etapa es **Enablement**.
1289: - **Action Tools:** fuera de la milla cero (diseñar, no implementar).
1290: - **Cache / performance avanzada:** no construir nada especulativo; medir antes de decidir (R11).
1291: 
1292: ---
1293: 
1294: ## 16. Tareas: definidas ahora vs pendientes
1295: 
1296: ### 16.1 Ahora (milla cero / P0)
1297: 
1298: - **Capability patrón:** construir `agenda.disponibilidad` end-to-end (R14 → §4.2).
1299: - **Seguridad base:** abstracción `Identity → Authorization → Capability` + enforcement point único (R8, §5).
1300: - **Observabilidad mínima:** request_id/tracing + trazabilidad AI sin guardar datos completos (§6).
1301: - **Contratos formales:** Pydantic/JSON Schema + taxonomía de errores (§7).
1302: - **Testing mínimo:** los cuatro niveles aplicados a `agenda.disponibilidad` (§12).
1303: - **Data Quality Rules:** primeras reglas por capability (R9).
1304: - **Gobernanza de datos:** `classification / pii / ai_allowed / allowed_fields / forbidden_fields` en la primera capability (R12).
1305: 
1306: ### 16.2 Pendientes (preparados pero no implementados)
1307: 
1308: - **P1 · Versionado:** definir y documentar la convención (contrato con `version`); ejercitar cuando algo rompa el contrato (R10).
1309: - **P1 · Calidad de datos ampliada:** reglas complejas a medida que lleguen capabilities analíticas (R9).
1310: - **P2 · Action Tools / transacciones:** diseñar modelo transaccional (commit/rollback) e idempotencia; no implementar en Fase 1 (R4).
1311: - **P2 · Cache / performance:** esperar métricas reales; aplicar "measure before optimize" (R11).
1312: - **P2 · PostgreSQL / Strangler Fig:** mantener como evolución futura, sin construir ahora (R15, Fase 3).
1313: - **P2 · Estrategia de seguridad avanzada:** IAM/SSO, autorización fina por campo — recién cuando existan más consumidores y Action Tools.
1314: 
1315: ### 16.3 Decisiones técnicas abiertas (resolver antes de codificar)
1316: 
1317: - ORM concreto (con `models`, `ports`, `repository` — candidate list: SQLAlchemy / SQLModel).
1318: - Framework/transporte del server MCP.
1319: - Proveedor de identidad/autenticación (token, API key, integración existente).
1320: - Despliegue (proceso, contenedor, entorno).
1321: 
1322: ---
1323: 
1324: ## 17. Ventajas estratégicas de este enfoque
1325: 
1326: - La refactorización **deja de ser un proyecto puramente técnico** que pide meses de inversión antes de mostrar resultados.
1327: - La primera etapa empieza a producir **capacidades visibles** mientras, al mismo tiempo, se construyen los cimientos de la segunda.
1328: - La IA puede **investigar** y responder preguntas del CEO con conocimiento operativo real, no con datasets prearmados.
1329: - Las **business rules quedan explicitadas** en la capa de servicios (Data Quality Rules), convirtiendo la plataforma en **fuente de conocimiento arquitectónico** para la futura refactorización.
1330: - El **golden path** (`agenda.disponibilidad`) hace que cada capability nueva sea incrementalmente más barata y consistente.
1331: 
1332: ---
1333: 
1334: ## 18. Milla cero (resumen ejecutivo)
1335: 
1336: > **Python Service Layer → FastAPI + FastMCP → ORM → Oracle → Capability Registry → `agenda.disponibilidad` como capability patrón + casos de negocio/IA.**
1337: 
1338: La estrategia está decidida. El siguiente paso no es seguir discutiendo arquitectura abstracta: es **construir CAPABILITY #001** y hacerla pasar por todo el circuito (Oracle → Repository → Service → Pydantic → FastAPI → FastMCP → Security → Observability → Tests → Registry).
1339: 
1340: ---
1341: 
1342: ## Claude Dice — Revisión enfocada en exposición API/MCP y contratos

(Showing lines 1288-1342 of 1540. Use offset=1343 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **Refactorización en sí:** pospuesta; la primera etapa es **Enablement**.\n- **Action Tools:** fuera de la milla cero (diseñar, no implementar).\n- **Cache / performance avanzada:** no construir nada especulativo; medir antes de decidir (R11).\n- **Versiones en MCP:** MCP expone solo la versión vigente del contrato; el versionado por ruta queda en REST (R10).\n- **Django no es la capa de habilitación.** En una conversación previa (DREAMS) la inclinación era partir con Django + MCP en vez de una API tradicional. **Decisión: el enablement layer es el servidor Python (FastAPI + FastMCP) sobre Oracle.** Django / Vault — si existe — queda como **consumidor**: cliente REST o MCP client, no dueña de la capa. Esto no contradice nada; es una capa distinta. *Pendiente de confirmar con el negocio:* si la intención original era que Django *fuera* el enablement layer, este es un cambio de rumbo que hay que validar explícitamente antes de la maqueta.\n\n---",
  "oldString": "- **Refactorización en sí:** pospuesta; la primera etapa es **Enablement**.\n- **Action Tools:** fuera de la milla cero (diseñar, no implementar).\n- **Cache / performance avanzada:** no construir nada especulativo; medir antes de decidir (R11).\n\n---"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 6.9s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### 16.1 Ahora (milla cero / P0)\n\n- **Capability patrón:** construir `agenda.disponibilidad` end-to-end (R14 → §4.2).\n- **Seguridad base:** abstracción `Identity → Authorization → Capability` + enforcement point único (R8, §5).\n- **Transporte MCP:** decidir transporte y autenticación **antes** de codificar la capability #1, porque condiciona el enforcement point único (§5.5).\n- **Proyección al protocolo MCP:** `mcp.annotations` derivadas de `operation.mode`, `description` como contrato con `usage_notes` y ejemplos, y traducción de errores al `content` del tool result (R17, R18, §7.4, §11.3).\n- **Observabilidad mínima:** request_id/tracing + trazabilidad AI sin guardar datos completos (§6).\n- **Contratos formales:** Pydantic/JSON Schema + taxonomía de errores (§7).\n- **Testing mínimo:** los cuatro niveles aplicados a `agenda.disponibilidad`, incluidos los tres invariantes MCP del Nivel 3 (§12).\n- **Data Quality Rules:** primeras reglas por capability (R9).\n- **Gobernanza de datos:** `classification / pii / ai_allowed / allowed_fields / forbidden_fields` en la primera capability (R12).\n\n### 16.2 Pendientes (preparados pero no implementados)\n\n- **P1 · Versionado:** definir y documentar la convención (contrato con `version`); se ejercita en REST, nunca duplicando tools en MCP (R10).\n- **P1 · Calidad de datos ampliada:** reglas complejas a medida que lleguen capabilities analíticas (R9).\n- **P1 · Límites de tráfico de agente:** campo `agent_traffic` declarado y medido; enforcement real (rate limit por sesión/tool) cuando el catálogo tenga varias capabilities (R19).\n- **P2 · Action Tools / transacciones:** diseñar modelo transaccional (commit/rollback) e idempotencia; no implementar en Fase 1 (R4).\n- **P2 · Cache / performance:** esperar métricas reales; aplicar \"measure before optimize\" (R11).\n- **P2 · Escalado del catálogo de tools:** namespacing por dominio o split de servidores MCP por área, a decidir antes de ~15 tools registradas (R20).\n- **P2 · PostgreSQL / Strangler Fig:** mantener como evolución futura, sin construir ahora (R15, Fase 3).\n- **P2 · Estrategia de seguridad avanzada:** IAM/SSO, autorización fina por campo — recién cuando existan más consumidores y Action Tools.\n\n### 16.3 Decisiones técnicas abiertas (resolver antes de codificar)\n\n- **Transporte MCP + autenticación** (subido a P0, §5.5): remoto con identidad por request, o local/in-process. Determina si el enforcement point único de R8 es viable.\n- ORM concreto (con `models`, `ports`, `repository` — candidate list: SQLAlchemy / SQLModel).\n- Proveedor de identidad/autenticación (token, API key, integración existente).\n- Despliegue (proceso, contenedor, entorno).\n- **Escalado del catálogo de tools** (P2, R20): namespacing por dominio vs. servidores MCP separados — se decide por conteo de tools, no antes.",
  "oldString": "### 16.1 Ahora (milla cero / P0)\n\n- **Capability patrón:** construir `agenda.disponibilidad` end-to-end (R14 → §4.2).\n- **Seguridad base:** abstracción `Identity → Authorization → Capability` + enforcement point único (R8, §5).\n- **Observabilidad mínima:** request_id/tracing + trazabilidad AI sin guardar datos completos (§6).\n- **Contratos formales:** Pydantic/JSON Schema + taxonomía de errores (§7).\n- **Testing mínimo:** los cuatro niveles aplicados a `agenda.disponibilidad` (§12).\n- **Data Quality Rules:** primeras reglas por capability (R9).\n- **Gobernanza de datos:** `classification / pii / ai_allowed / allowed_fields / forbidden_fields` en la primera capability (R12).\n\n### 16.2 Pendientes (preparados pero no implementados)\n\n- **P1 · Versionado:** definir y documentar la convención (contrato con `version`); ejercitar cuando algo rompa el contrato (R10).\n- **P1 · Calidad de datos ampliada:** reglas complejas a medida que lleguen capabilities analíticas (R9).\n- **P2 · Action Tools / transacciones:** diseñar modelo transaccional (commit/rollback) e idempotencia; no implementar en Fase 1 (R4).\n- **P2 · Cache / performance:** esperar métricas reales; aplicar \"measure before optimize\" (R11).\n- **P2 · PostgreSQL / Strangler Fig:** mantener como evolución futura, sin construir ahora (R15, Fase 3).\n- **P2 · Estrategia de seguridad avanzada:** IAM/SSO, autorización fina por campo — recién cuando existan más consumidores y Action Tools.\n\n### 16.3 Decisiones técnicas abiertas (resolver antes de codificar)\n\n- ORM concreto (con `models`, `ports`, `repository` — candidate list: SQLAlchemy / SQLModel).\n- Framework/transporte del server MCP.\n- Proveedor de identidad/autenticación (token, API key, integración existente).\n- Despliegue (proceso, contenedor, entorno)."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 1.9s)

_Thinking:_

Now update the Claude review list at the end with status markers. Let me read the current state of that section.

Ahora marco el listado de Claude con el estado de cada punto:

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 65,
  "offset": 1355
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1355: El YAML de `agenda.disponibilidad` (§9.3) es completo para gobernanza y trazabilidad, pero le falta el campo que el protocolo MCP usa para que un agente decida *si* y *cómo* llamar la tool sin ejecutarla primero: las **tool annotations** (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). El campo `operation.mode: READ` es información equivalente, pero vive en la capa interna — si no se proyecta al `readOnlyHint` real del schema MCP, se pierde la señal nativa que los clientes MCP usan para, por ejemplo, pedir menos confirmación en tools de solo lectura. Esto conecta directo con R4 (READ→ANALYZE→ACT): esa jerarquía de riesgo ya diseñada debería *ser* las annotations, no vivir aparte.
1356: 
1357: **Acción sugerida:** agregar a §9.1 un bloque `mcp.annotations` que se derive automáticamente de `operation.mode`.
1358: 
1359: ### 2. La descripción de la tool es el contrato más importante y casi no está tratada
1360: 
1361: R6 dice bien que "el nombre MCP no es copia del nombre Python", pero el `description` en lenguaje natural es lo único que el LLM ve para decidir *cuándo* usar la tool y con qué argumentos — es tan contrato como el JSON schema, solo que en prosa. El ejemplo de §9.3 tiene una descripción de una línea. Con 10-30 capabilities activas (agenda, pacientes, facturación, inventario), cada `description` va a necesitar explícitamente: cuándo NO usar esta tool (para diferenciarla de otra parecida), y 1-2 ejemplos de input/output correcto.
1362: 
1363: **Acción sugerida:** agregar al contrato un campo `usage_notes` / `disambiguation`, además del ya existente `examples`.
1364: 
1365: ### 3. Escalado del catálogo de tools (no está cubierto)
1366: 
1367: R16 y el catálogo (§10) asumen todas las capabilities conviviendo en un único servidor MCP con una lista de tools plana. Eso funciona con 2-5 tools; con 20-50 empieza a saturar el contexto del agente y a degradar la precisión de selección de tool.
1368: 
1369: **Acción sugerida (P2, anotar junto a §16.3):** namespacing por dominio (`agenda.consultar_disponibilidad` como nombre real de tool, no solo como `id` interno), o varios servidores MCP montados por área de negocio en vez de uno monolítico.
1370: 
1371: ### 4. Versionado (R10) choca con cómo funciona MCP en la práctica
1372: 
1373: La regla "v1 y v2 pueden coexistir temporalmente" es sana a nivel de contrato/servicio, pero en MCP cada tool es una entrada en la lista de tools que ve el agente. Si se registran `consultar_disponibilidad.v1` y `.v2` como dos tools MCP simultáneas, el agente ve dos tools casi idénticas sin señal de cuál preferir.
1374: 
1375: **Acción sugerida:** que MCP exponga siempre solo la versión vigente del contrato; la coexistencia de versiones (Strangler) se resuelve en REST, que sí tolera bien rutas versionadas.
1376: 
1377: ### 5. Taxonomía de errores (§7.3) necesita traducción explícita a "cómo lo ve el LLM"
1378: 
1379: La distinción `NotFoundError` vs `InfrastructureError` es correcta para que el agente razone bien, pero en MCP el error no siempre llega como excepción de protocolo — la práctica común es devolver `isError: true` con el mensaje dentro del *content* del tool result, para que el LLM lo lea en el mismo turno en vez de que se pierda a nivel de transporte.
1380: 
1381: **Acción sugerida:** agregar al contrato cómo se serializa cada tipo de error hacia el content del tool result, no solo el nombre de la excepción Python.
1382: 
1383: ### 6. El transporte MCP no es una decisión neutral (§16.3 lo trata como tal)
1384: 
1385: §5.3 y §16.3 dejan el transporte MCP como detalle de infraestructura a resolver después. Pero el diagrama de seguridad (Identity → Authorization antes de la capability) asume implícitamente transporte remoto (HTTP/SSE) con autenticación por request. Esto condiciona directamente el enforcement point único (ya identificado como el segundo cabo a amarrar antes de codificar).
1386: 
1387: **Acción sugerida:** subir "transporte MCP" a P0, junto a seguridad, en vez de dejarlo en §16.3 como decisión abierta de igual peso que el ORM.
1388: 
1389: ### 7. Falta límite de concurrencia/rate por tool para loops de agente
1390: 
1391: Un agente investigando (ejemplo §8.2: `consultar_ocupacion_agenda → comparar_ocupacion_historica → identificar_unidades_con_caida → analizar_causas_probables`) puede iterar y repetir llamadas a la misma tool dentro de una sola sesión. Contra Oracle productivo, aunque sea solo lectura, eso es carga real que R11 ("medir antes de optimizar") no cubre porque asume tráfico humano, no tráfico de agente en loop.
1392: 
1393: **Acción sugerida:** agregar un campo informal `max_calls_per_session` (o equivalente) al contrato desde el día 1, aunque no se implemente todavía.
1394: 
1395: ### Nota aparte: tensión con la dirección Django + MCP
1396: 
1397: En una conversación previa (DREAMS) la inclinación era partir la nueva arquitectura con Django + MCP en vez de una API tradicional. Esta estrategia usa FastAPI + FastMCP como servidor Python independiente, sin mencionar Django. Si Vault (Django) va a consumir esta capa como cliente vía REST o como MCP client, no hay contradicción — son capas distintas. Pero si la idea original era que Django *fuera* el enablement layer, este es un cambio de rumbo que conviene dejar explícito en el documento en vez de que se lea como decisión ya resuelta.
1398: 
1399: ### En síntesis
1400: 
1401: La parte de negocio/gobernanza del contrato (R1–R16, §9, §12) está sólida. Lo que falta es la capa "protocolo MCP real": annotations, la descripción como contrato de facto, escalado de catálogo, y cómo versión/error se ven específicamente desde el lado del agente y no solo desde el lado del servicio Python.
1402: 
1403: ---
1404: 
1405: ## BigPickle Dice:
1406: 
1407: ### Fortalezas
1408: 
1409: 1. **Pragmatismo estratégico de alto valor.** Separar el *Problema A* (modernizar) del *Problema B* (consumir los datos) es la decisión más potente del documento: produce valor visible para el negocio sin tocar el sistema productivo.
1410: 2. **La identidad canónica de capacidad es la columna vertebral.** La regla "una capacidad, identidad única, protocolos como representaciones" evita la inflación de nombres, mantiene limpias las tres interfaces y evita que el legacy contamine la semántica nueva.
1411: 3. **Riesgo controlado con READ → ANALYZE → ACT.** Estrategia de despliegue sensata que demuestra valor primero y habilita escrituras solo cuando hay confianza; ahora con frontera explícita para la Fase 1.
1412: 4. **Empoderamiento del equipo.** Tool Contract + Registry a catálogo de capacidades: el equipo agrega capabilities sin depender de una sola persona (resuelve el cuello de botella de conocimiento).
1413: 5. **El ORM como capa semántica.** Declarar relaciones en el modelo aunque Oracle no tenga FK es a la vez documentación viva y puente hacia una base relacional sana en el futuro.
1414: 6. **Golden path definido.** `agenda.disponibilidad` como capability patrón le da a la arquitectura un punto de partida concreto, medible y replicable — el verdadero indicador de éxito es que la capability #2 cueste menos que la #1.
1415: 7. **La revisión convirtió brechas en decisiones, no en inflación de alcance.** Se priorizó (P0/P1/P2) y se separó "resolver ahora" de "preparar sin implementar"; el documento ahora distingue claramente la milla cero de la evolución futura.
1416: 
1417: ### Debilidades / brechas que permanecen abiertas
1418: 
1419: *Se eliminaron de esta lista los puntos que quedaron cubiertos como decisiones de diseño en el cuerpo del documento (seguridad, observabilidad, calidad de datos, priorización, contratos, versionado, testing, Action Tools, performance).*

(Showing lines 1355-1419 of 1547. Use offset=1420 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.8s)

_Thinking:_

Now add status markers. I'll add a "Estado" line after each "Acción sugerida" and a status table right after the intro of that section. Let me do targeted edits.

First, add a status summary table right after the intro blockquote of the Claude section. Let me read the section start.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 12,
  "offset": 1344
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
1344: 
1345: La estrategia está decidida. El siguiente paso no es seguir discutiendo arquitectura abstracta: es **construir CAPABILITY #001** y hacerla pasar por todo el circuito (Oracle → Repository → Service → Pydantic → FastAPI → FastMCP → Security → Observability → Tests → Registry).
1346: 
1347: ---
1348: 
1349: ## Claude Dice — Revisión enfocada en exposición API/MCP y contratos
1350: 
1351: > Foco de esta revisión: la declaración de cómo se expone la capa hacia REST y MCP, y en particular el Tool Contract (§9), porque es la pieza que decide si un agente usa bien o mal el catálogo de capabilities. Las reglas de negocio/gobernanza (R1–R16, §12) están sólidas; lo que falta es la capa "protocolo MCP real".
1352: 
1353: ### 1. El Tool Contract describe metadata de negocio, no metadata de protocolo MCP
1354: 
1355: El YAML de `agenda.disponibilidad` (§9.3) es completo para gobernanza y trazabilidad, pero le falta el campo que el protocolo MCP usa para que un agente decida *si* y *cómo* llamar la tool sin ejecutarla primero: las **tool annotations** (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). El campo `operation.mode: READ` es información equivalente, pero vive en la capa interna — si no se proyecta al `readOnlyHint` real del schema MCP, se pierde la señal nativa que los clientes MCP usan para, por ejemplo, pedir menos confirmación en tools de solo lectura. Esto conecta directo con R4 (READ→ANALYZE→ACT): esa jerarquía de riesgo ya diseñada debería *ser* las annotations, no vivir aparte.

(Showing lines 1344-1355 of 1547. Use offset=1356 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 4.3s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "> Foco de esta revisión: la declaración de cómo se expone la capa hacia REST y MCP, y en particular el Tool Contract (§9), porque es la pieza que decide si un agente usa bien o mal el catálogo de capabilities. Las reglas de negocio/gobernanza (R1–R16, §12) están sólidas; lo que falta es la capa \"protocolo MCP real\".\n\n### Estado de aplicación de esta revisión\n\n| # | Observación | Estado | Dónde quedó |\n| - | ----------- | ------ | ----------- |\n| 1 | Tool annotations ausentes | ✅ **Hecha** | R17, R4, §9.1, §9.3, §11.3, §12 Nivel 3 |\n| 2 | `description` como contrato de facto | ✅ **Hecha** | R6, R17, §9.1, §9.3, §11.3 |\n| 3 | Escalado del catálogo de tools | ✅ **Hecha** (como P2) | R20, §9.4, §3, §16.2, §16.3 |\n| 4 | Versionado R10 vs MCP | ✅ **Hecha** | R10, §9.3, §12 Nivel 3, §16.2 |\n| 5 | Errores: traducción al `content` MCP | ✅ **Hecha** | R18, §7.4, §9.1, §9.3, §11.3 |\n| 6 | Transporte MCP no es decisión neutral | ✅ **Hecha** (subido a P0) | §5.5, §3, §16.1, §16.3 |\n| 7 | Límite de tráfico de agente | ✅ **Hecha** (declarado, enforcement P1) | R19, R11, §9.1, §9.3, §16.2 |\n| N | Tensión Django + MCP | ⚠️ **Parcial** | §15: la decisión quedó escrita, pero falta confirmarla con el negocio |\n\n",
  "oldString": "> Foco de esta revisión: la declaración de cómo se expone la capa hacia REST y MCP, y en particular el Tool Contract (§9), porque es la pieza que decide si un agente usa bien o mal el catálogo de capabilities. Las reglas de negocio/governanza (R1–R16, §12) están sólidas; lo que falta es la capa \"protocolo MCP real\".\n\n"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 3.9s)

_Thinking:_

Multi-line again failing. The pattern: multi-line oldString with blockquote `> ` lines fails. Maybe due to invisible characters? Let me check od of line 1351.

Actually earlier multi-line edits worked (e.g., R16 → R17 insert, §15 edit, §16.1 edit). So multi-line generally works. The failure might be because of some specific char. Let me just use a single-line anchor.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### Estado de aplicación de esta revisión\n\n| # | Observación | Estado | Dónde quedó |\n| - | ----------- | ------ | ----------- |\n| 1 | Tool annotations ausentes | ✅ **Hecha** | R17, R4, §9.1, §9.3, §11.3, §12 Nivel 3 |\n| 2 | `description` como contrato de facto | ✅ **Hecha** | R6, R17, §9.1, §9.3, §11.3 |\n| 3 | Escalado del catálogo de tools | ✅ **Hecha** (como P2) | R20, §9.4, §3, §16.2, §16.3 |\n| 4 | Versionado R10 vs MCP | ✅ **Hecha** | R10, §9.3, §12 Nivel 3, §16.2 |\n| 5 | Errores: traducción al `content` MCP | ✅ **Hecha** | R18, §7.4, §9.1, §9.3, §11.3 |\n| 6 | Transporte MCP no es decisión neutral | ✅ **Hecha** (subido a P0) | §5.5, §3, §16.1, §16.3 |\n| 7 | Límite de tráfico de agente | ✅ **Hecha** (declarado; enforcement en P1) | R19, R11, §9.1, §9.3, §16.2 |\n| N | Tensión Django + MCP | ⚠️ **Parcial** | §15: la decisión quedó escrita, falta confirmarla con el negocio |\n\n### 1. El Tool Contract describe metadata de negocio, no metadata de protocolo MCP",
  "oldString": "### 1. El Tool Contract describe metadata de negocio, no metadata de protocolo MCP"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.8s)

Ahora añado el estado individual al final de cada observación:

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** agregar a §9.1 un bloque `mcp.annotations` que se derive automáticamente de `operation.mode`.\n\n> **✅ Aplicado.** Nueva regla **R17** con la tabla de derivación `operation.mode → annotations`; bloque `mcp.annotations` en §9.1 y en la ficha §9.3; R4 ahora declara que la jerarquía de riesgo **se proyecta** a las annotations; el adapter de §11.3 las toma del registry en vez de escribirlas a mano; y el contract test de §12 Nivel 3 falla si `mode: ACT` se publica con `readOnlyHint: true`.",
  "oldString": "**Acción sugerida:** agregar a §9.1 un bloque `mcp.annotations` que se derive automáticamente de `operation.mode`."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.4s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** agregar al contrato un campo `usage_notes` / `disambiguation`, además del ya existente `examples`.\n\n> **✅ Aplicado.** R6 establece que la `description` es contrato y no documentación; R17b define el contenido obligatorio (qué hace, cuándo usarla, **cuándo NO usarla**, 1-2 ejemplos). El contrato de §9.1 incorpora `usage_notes`, la ficha §9.3 pasa de una línea a descripción con criterio de uso + `usage_notes` explícito + ejemplos con `in`/`out`, y §11.3 muestra la descripción real que ve el modelo. El Nivel 4 de testing ahora deriva sus casos de los `usage_notes` (una intención que debe elegir la tool, una parecida que no).",
  "oldString": "**Acción sugerida:** agregar al contrato un campo `usage_notes` / `disambiguation`, además del ya existente `examples`."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.4s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida (P2, anotar junto a §16.3):** namespacing por dominio (`agenda.consultar_disponibilidad` como nombre real de tool, no solo como `id` interno), o varios servidores MCP montados por área de negocio en vez de uno monolítico.\n\n> **✅ Aplicado como P2** (coherente con la sugerencia de Claude, que ya la calificaba de P2). Nueva regla **R20** con el criterio de escalado y el umbral (~15 tools registradas): namespacing por dominio o split de servidores MCP por área, siempre detrás del mismo service layer. El registry se construye para que el namespace sea un cambio de proyección y no de lógica. Registrado en §3 (P2), §16.2, §16.3, y §9.4 agrega la fila `Dominio` al Identity Map aclarando que el nombre canónico no cambia.",
  "oldString": "**Acción sugerida (P2, anotar junto a §16.3):** namespacing por dominio (`agenda.consultar_disponibilidad` como nombre real de tool, no solo como `id` interno), o varios servidores MCP montados por área de negocio en vez de uno monolítico."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** que MCP exponga siempre solo la versión vigente del contrato; la coexistencia de versiones (Strangler) se resuelve en REST, que sí tolera bien rutas versionadas.\n\n> **✅ Aplicado.** R10 ahora tiene una restricción explícita de MCP: el tool list expone **una sola versión, la vigente**; el nombre de la tool no lleva sufijo; la coexistencia v1/v2 del Strangler se resuelve en REST; y la deprecación se comunica en la `description`/`usage_notes` en vez de duplicar entradas. Reflejado en la ficha §9.3 (`tool: consultar_disponibilidad  # sin sufijo de versión`), en §15 (frontera congelada) y en el contract test (§12 Nivel 3, invariante 2). §16.2 reescribe el P1 de versionado con esta restricción.",
  "oldString": "**Acción sugerida:** que MCP exponga siempre solo la versión vigente del contrato; la coexistencia de versiones (Strangler) se resuelve en REST, que sí tolera bien rutas versionadas."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.4s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** agregar al contrato cómo se serializa cada tipo de error hacia el content del tool result, no solo el nombre de la excepción Python.\n\n> **✅ Aplicado.** Nueva regla **R18** y nueva sección **§7.4 \"Cómo ve el LLM cada error\"**, con la tabla de traducción por tipo de error (Python → `error_code` REST/HTTP → `content` MCP → lectura del agente). Reglas fijadas: el error no se propaga como excepción de protocolo, se devuelve `isError: true` con mensaje accionable en el mismo turno; nunca traceback; el mapeo vive en un único translator del adapter MCP; `AuthorizationError` no revela la regla que falló. El contrato de §9.1 y la ficha §9.3 declaran `error_code` + `message` por tipo de error, §11.3 dice que el adapter traduce según §7.4, y §12 Nivel 3 verifica que `NO_DATA ≠ UNAVAILABLE`.",
  "oldString": "**Acción sugerida:** agregar al contrato cómo se serializa cada tipo de error hacia el content del tool result, no solo el nombre de la excepción Python."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** subir \"transporte MCP\" a P0, junto a seguridad, en vez de dejarlo en §16.3 como decisión abierta de igual peso que el ORM.\n\n> **✅ Aplicado.** Nueva sección **§5.5 \"El transporte MCP es decisión P0, no infraestructura diferible\"**: contrasta transporte local/in-process vs remoto, aclara que el diagrama de seguridad asumía remoto con identidad por request, y da la tabla de criterios de decisión (auth, enforcement, red, streaming, framework). Restricción dura: sin identidad por request, el enforcement point único de R8 no es implementable tal como está definido. Reflejado en §3 (nueva fila P0), §16.1 (P0 antes de codificar la capability #1) y §16.3 (sube de \"decisión abierta de igual peso\" a primera línea, con el criterio de viabilidad).",
  "oldString": "**Acción sugerida:** subir \"transporte MCP\" a P0, junto a seguridad, en vez de dejarlo en §16.3 como decisión abierta de igual peso que el ORM."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "**Acción sugerida:** agregar un campo informal `max_calls_per_session` (o equivalente) al contrato desde el día 1, aunque no se implemente todavía.\n\n> **✅ Aplicado como declaración, enforcement en P1** (que es exactamente lo que pedía la observación: declararlo desde el día 1 sin implementarlo todavía). Nueva regla **R19** con el bloque `agent_traffic` (`max_calls_per_session`, `expected_cost`); R11 declara su propio límite de supuesto (modela tráfico humano, no de agente); el contrato §9.1 y la ficha §9.3 incluyen el campo; §3 lo registra como P1; y §16.2 lo lista como pendiente de implementación, indicando que en la milla cero basta con medir y alertar. El campo `expected_cost` además conecta con R11: una tool cara es candidata a cache y eso se decide con dato.",
  "oldString": "**Acción sugerida:** agregar un campo informal `max_calls_per_session` (o equivalente) al contrato desde el día 1, aunque no se implemente todavía."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.5s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "En una conversación previa (DREAMS) la inclinación era partir la nueva arquitectura con Django + MCP en vez de una API tradicional. Esta estrategia usa FastAPI + FastMCP como servidor Python independiente, sin mencionar Django. Si Vault (Django) va a consumir esta capa como cliente vía REST o como MCP client, no hay contradicción — son capas distintas. Pero si la idea original era que Django *fuera* el enablement layer, este es un cambio de rumbo que conviene dejar explícito en el documento en vez de que se lea como decisión ya resuelta.\n\n> **⚠️ Parcialmente aplicado.** La ambigüedad ya no está implícita: §15 (Decisiones congeladas) declara explícitamente que **el enablement layer es el servidor Python (FastAPI + FastMCP) sobre Oracle** y que Django / Vault queda como **consumidor** (cliente REST o MCP client), no como dueño de la capa.\n>\n> **Lo que queda pendiente** es una decisión de negocio, no de documento: confirmar con el negocio si la intención original era que Django *fuera* el enablement layer. Si la respuesta es sí, este documento está desactualizado en su premisa y hay que rehacer §4 y §11; si es no, se cierra el punto. Marcado en §15 y en §16.3 como pendiente de validación antes de la maqueta.",
  "oldString": "En una conversación previa (DREAMS) la inclinación era partir la nueva arquitectura con Django + MCP en vez de una API tradicional. Esta estrategia usa FastAPI + FastMCP como servidor Python independiente, sin mencionar Django. Si Vault (Django) va a consumir esta capa como cliente vía REST o como MCP client, no hay contradicción — son capas distintas. Pero si la idea original era que Django *fuera* el enablement layer, este es un cambio de rumbo que conviene dejar explícito en el documento en vez de que se lea como decisión ya resuelta."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.4s)

_Thinking:_

Now update the "En síntesis" of the Claude section to reflect application, and add Django pending to §16.3 (I mentioned it there but let me verify I added it — I said in §16.3 in the status note "Marcado en §15 y en §16.3 como pendiente". Let me check §16.3 content. I added transporte MCP, ORM, identity provider, deployment, escalado. I did not add Django. Let me add it to be consistent.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **Escalado del catálogo de tools** (P2, R20): namespacing por dominio vs. servidores MCP separados — se decide por conteo de tools, no antes.\n- **Validar con el negocio la premisa de Django** (§15): confirmar que el enablement layer es el servidor Python y que Django / Vault queda como consumidor. Si no se confirma antes de la maqueta, la premisa del documento queda en riesgo.",
  "oldString": "- **Escalado del catálogo de tools** (P2, R20): namespacing por dominio vs. servidores MCP separados — se decide por conteo de tools, no antes."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.8s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "La parte de negocio/gobernanza del contrato (R1–R16, §9, §12) está sólida. Lo que falta es la capa \"protocolo MCP real\": annotations, la descripción como contrato de facto, escalado de catálogo, y cómo versión/error se ven específicamente desde el lado del agente y no solo desde el lado del servicio Python.\n\n### En síntesis — tras aplicar la revisión\n\nLos 7 puntos quedaron absorbidos como decisiones de diseño en el cuerpo del documento, no como tareas sueltas: **R17** (annotations + descripción como contrato), **R18** (errores traducidos al `content` MCP), **R19** (tráfico de agente) y **R20** (escalado del catálogo) se suman a R1–R16; **§5.5** saca el transporte MCP de la caja de Pandora; **§7.4** traduce la taxonomía de errores a la vista del LLM; y §9.1/§9.3/§11.3/§12 muestran el contrato completo con la proyección MCP incluida. El único punto que no se puede cerrar desde el documento es la premisa de Django, que requiere una confirmación del negocio.",
  "oldString": "La parte de negocio/governanza del contrato (R1–R16, §9, §12) está sólida. Lo que falta es la capa \"protocolo MCP real\": annotations, la descripción como contrato de facto, escalado de catálogo, y cómo versión/error se ven específicamente desde el lado del agente y no solo desde el lado del servicio Python."
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 130.7s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "### En síntesis — tras aplicar la revisión\n\nLos 7 puntos quedaron absorbidos como decisiones de diseño en el cuerpo del documento, no como tareas sueltas: **R17** (annotations + descripción como contrato), **R18** (errores traducidos al `content` MCP), **R19** (tráfico de agente) y **R20** (escalado del catálogo) se suman a R1–R16; **§5.5** saca el transporte MCP de la caja de Pandora; **§7.4** traduce la taxonomía de errores a la vista del LLM; y §9.1/§9.3/§11.3/§12 muestran el contrato completo con la proyección MCP incluida. El único punto que no se puede cerrar desde el documento es la premisa de Django, que requiere una confirmación del negocio.",
  "oldString": "### En síntesis"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.9s)

_Thinking:_

Now let's verify the document renders reasonably and there are no leftover issues. Let me check the mermaid blocks aren't broken, and check for the §14 reference "R14 → §4.2" which is pre-existing wrong (R14 is about FK). Not my concern.

Let me do a final sanity check: grep for R17-R20, §5.5, §7.4, and verify no typos like "estáRule".

Also I should double check the R17 heading numbering and that §2 ends properly with the `---`.

Let me view relevant regions.

**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"^### R1[7-9]\\|^### R20\\|^### 5\\.5\\|^### 7\\.4\\|✅\\|⚠️\" /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md | head -40; echo \"---\"; grep -c \"estáRule\\|偏好\" /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md"
}
```

**Output:**
```
285:### R17 — El contrato MCP es parte del contrato de la capability (protocolo, no solo negocio)
312:### R18 — Todo error se traduce al `content` del tool result
336:### R19 — El tráfico de agente es tráfico real: límites por tool
350:### R20 — El catálogo de tools tiene que escalar
537:### 5.5 El transporte MCP es decisión P0, no infraestructura diferible
674:### 7.4 Cómo ve el LLM cada error (traducción al protocolo)
1203:    READ[READ · Fase 1 ✅] --> ANALYZE[ANALYZE · Fase 1 ✅]
1358:| 1 | Tool annotations ausentes | ✅ **Hecha** | R17, R4, §9.1, §9.3, §11.3, §12 Nivel 3 |
1359:| 2 | `description` como contrato de facto | ✅ **Hecha** | R6, R17, §9.1, §9.3, §11.3 |
1360:| 3 | Escalado del catálogo de tools | ✅ **Hecha** (como P2) | R20, §9.4, §3, §16.2, §16.3 |
1361:| 4 | Versionado R10 vs MCP | ✅ **Hecha** | R10, §9.3, §12 Nivel 3, §16.2 |
1362:| 5 | Errores: traducción al `content` MCP | ✅ **Hecha** | R18, §7.4, §9.1, §9.3, §11.3 |
1363:| 6 | Transporte MCP no es decisión neutral | ✅ **Hecha** (subido a P0) | §5.5, §3, §16.1, §16.3 |
1364:| 7 | Límite de tráfico de agente | ✅ **Hecha** (declarado; enforcement en P1) | R19, R11, §9.1, §9.3, §16.2 |
1365:| N | Tensión Django + MCP | ⚠️ **Parcial** | §15: la decisión quedó escrita, falta confirmarla con el negocio |
1373:> **✅ Aplicado.** Nueva regla **R17** con la tabla de derivación `operation.mode → annotations`; bloque `mcp.annotations` en §9.1 y en la ficha §9.3; R4 ahora declara que la jerarquía de riesgo **se proyecta** a las annotations; el adapter de §11.3 las toma del registry en vez de escribirlas a mano; y el contract test de §12 Nivel 3 falla si `mode: ACT` se publica con `readOnlyHint: true`.
1381:> **✅ Aplicado.** R6 establece que la `description` es contrato y no documentación; R17b define el contenido obligatorio (qué hace, cuándo usarla, **cuándo NO usarla**, 1-2 ejemplos). El contrato de §9.1 incorpora `usage_notes`, la ficha §9.3 pasa de una línea a descripción con criterio de uso + `usage_notes` explícito + ejemplos con `in`/`out`, y §11.3 muestra la descripción real que ve el modelo. El Nivel 4 de testing ahora deriva sus casos de los `usage_notes` (una intención que debe elegir la tool, una parecida que no).
1389:> **✅ Aplicado como P2** (coherente con la sugerencia de Claude, que ya la calificaba de P2). Nueva regla **R20** con el criterio de escalado y el umbral (~15 tools registradas): namespacing por dominio o split de servidores MCP por área, siempre detrás del mismo service layer. El registry se construye para que el namespace sea un cambio de proyección y no de lógica. Registrado en §3 (P2), §16.2, §16.3, y §9.4 agrega la fila `Dominio` al Identity Map aclarando que el nombre canónico no cambia.
1397:> **✅ Aplicado.** R10 ahora tiene una restricción explícita de MCP: el tool list expone **una sola versión, la vigente**; el nombre de la tool no lleva sufijo; la coexistencia v1/v2 del Strangler se resuelve en REST; y la deprecación se comunica en la `description`/`usage_notes` en vez de duplicar entradas. Reflejado en la ficha §9.3 (`tool: consultar_disponibilidad  # sin sufijo de versión`), en §15 (frontera congelada) y en el contract test (§12 Nivel 3, invariante 2). §16.2 reescribe el P1 de versionado con esta restricción.
1405:> **✅ Aplicado.** Nueva regla **R18** y nueva sección **§7.4 "Cómo ve el LLM cada error"**, con la tabla de traducción por tipo de error (Python → `error_code` REST/HTTP → `content` MCP → lectura del agente). Reglas fijadas: el error no se propaga como excepción de protocolo, se devuelve `isError: true` con mensaje accionable en el mismo turno; nunca traceback; el mapeo vive en un único translator del adapter MCP; `AuthorizationError` no revela la regla que falló. El contrato de §9.1 y la ficha §9.3 declaran `error_code` + `message` por tipo de error, §11.3 dice que el adapter traduce según §7.4, y §12 Nivel 3 verifica que `NO_DATA ≠ UNAVAILABLE`.
1413:> **✅ Aplicado.** Nueva sección **§5.5 "El transporte MCP es decisión P0, no infraestructura diferible"**: contrasta transporte local/in-process vs remoto, aclara que el diagrama de seguridad asumía remoto con identidad por request, y da la tabla de criterios de decisión (auth, enforcement, red, streaming, framework). Restricción dura: sin identidad por request, el enforcement point único de R8 no es implementable tal como está definido. Reflejado en §3 (nueva fila P0), §16.1 (P0 antes de codificar la capability #1) y §16.3 (sube de "decisión abierta de igual peso" a primera línea, con el criterio de viabilidad).
1421:> **✅ Aplicado como declaración, enforcement en P1** (que es exactamente lo que pedía la observación: declararlo desde el día 1 sin implementarlo todavía). Nueva regla **R19** con el bloque `agent_traffic` (`max_calls_per_session`, `expected_cost`); R11 declara su propio límite de supuesto (modela tráfico humano, no de agente); el contrato §9.1 y la ficha §9.3 incluyen el campo; §3 lo registra como P1; y §16.2 lo lista como pendiente de implementación, indicando que en la milla cero basta con medir y alertar. El campo `expected_cost` además conecta con R11: una tool cara es candidata a cache y eso se decide con dato.
1427:> **⚠️ Parcialmente aplicado.** La ambigüedad ya no está implícita: §15 (Decisiones congeladas) declara explícitamente que **el enablement layer es el servidor Python (FastAPI + FastMCP) sobre Oracle** y que Django / Vault queda como **consumidor** (cliente REST o MCP client), no como dueño de la capa.
1533:    READ[READ · lecturas ✅] --> AN[ANALYZE · análisis ✅] --> ACT[ACT · acciones ⏳ fuera de la milla cero]
---
1

```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

The grep -c returned 1 — meaning one line matches "estáRule\|偏好". Let me check which.

**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"estáRule\\|偏好\" /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md"
}
```

**Output:**
```
176:- **Restricción específica de MCP:** la coexistencia de versiones **no se proyecta al tool list**. En MCP cada versión sería una entrada más de la lista de tools que ve el agente, y dos tools casi idénticas sin señal de cuál偏好 degradan la calidad de la respuesta.

```

---

## Assistant (Build · Big Pickle · 2.2s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "newString": "- **Restricción específica de MCP:** la coexistencia de versiones **no se proyecta al tool list**. En MCP cada versión sería una entrada más de la lista de tools que ve el agente, y dos tools casi idénticas sin señal de cuál preferir degradan la calidad de la respuesta.",
  "oldString": "- **Restricción específica de MCP:** la coexistencia de versiones **no se proyecta al tool list**. En MCP cada versión sería una entrada más de la lista de tools que ve el agente, y dos tools casi idénticas sin señal de cuál偏好 degradan la calidad de la respuesta."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.3s)

**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"estáRule\\|偏好\" /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md; echo \"exit=$?\"; wc -l /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md"
}
```

**Output:**
```
exit=1
    1580 /Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md

```

---

## Assistant (Build · Big Pickle · 2.7s)

_Thinking:_

Clean. Let me also verify the "## 2. Reglas..." section transition after R20 — check the end of R20 and the `---` before ## 3.

Also verify §7.4 placement — it was inserted after 7.3 and before `---` + `## 8`. Let me verify.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 30,
  "offset": 348
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
348: - Este campo también ordena la lista: una tool con `expected_cost: high` es candidata natural a cacheado, y eso se decide con dato, no por intuición.
349: 
350: ### R20 — El catálogo de tools tiene que escalar
351: 
352: - Con 2-5 tools, un único servidor MCP con lista plana funciona. **Con 20-50 satura el contexto del agente y degrada la precisión de selección de tool.**
353: - Criterio de escalado (a decidir antes de llegar a ~15 tools registradas, no antes):
354:   - **Namespacing por dominio:** `agenda.consultar_disponibilidad` como **nombre real de la tool** (no solo el `id` interno), manteniendo `consultar_disponibilidad` como nombre canónico de la capability (R1).
355:   - **Varios servidores MCP por área de negocio** en vez de uno monolítico, manteniendo un mismo service layer detrás.
356: - En Fase 1 se registra el dominio (`id: agenda.disponibilidad`) y se construye el registry de forma que el namespacing sea un cambio de proyección, no de lógica de negocio.
357: - **P2 en la práctica:** no bloquea la milla cero, pero condiciona el diseño del registry desde el inicio.
358: 
359: 
360: ---
361: 
362: ## 3. Priorización de decisiones: ahora vs pendiente
363: 
364: **Las brechas no son 10 problemas equivalentes.** Algunas son decisiones de la milla cero, otras se preparan sin implementarse, y otras son transversales.
365: 
366: | Prioridad | Tema                             | ¿Resolver ahora?        |
367: | --------- | -------------------------------- | ----------------------- |
368: | 🔴 P0     | Caso de negocio #1 (capability patrón) | Sí                  |
369: | 🔴 P0     | Seguridad / identidad            | Sí                      |
370: | 🔴 P0     | **Transporte MCP** (condiciona auth y enforcement point) | **Sí**          |
371: | 🔴 P0     | Observabilidad                   | Sí                      |
372: | 🔴 P0     | Contratos Pydantic / JSON Schema | Sí                      |
373: | 🔴 P0     | **Proyección al protocolo MCP** (annotations + `description` como contrato) | **Sí** |
374: | 🔴 P0     | Testing mínimo                   | Sí                      |
375: | 🔴 P0     | Gobernanza de datos (qué cruza a IA) | Sí, por capability  |
376: | 🟠 P1     | Calidad / confiabilidad de datos | Sí, pero por capability |
377: | 🟠 P1     | Versionado (REST versioning en Strangler) | Definir convención      |

(Showing lines 348-377 of 1581. Use offset=378 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.6s)

_Thinking:_

Good. One extra blank line at 358-359, harmless.

Now let me also make sure §18 (milla cero) and the Presentation mention the MCP protocol layer? Not strictly needed. The user asked to adjust per Claude's observations. Done.

One more thing: Claude's review mentions "§12" as reglas de negocio — fine.

Let me quickly double check §7.4 and §5.5 render.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md",
  "limit": 32,
  "offset": 672
}
```

**Output:**
```
<path>/Users/fernandosalvo/Desktop/humbold/docs/refactorizacion/000_MiEstrategiaV1.md</path>
<type>file</type>
<content>
672: **Crítico para agentes:** el LLM debe distinguir *"no existen datos"* (resultado válido) de *"no pude consultar los datos"* (fallo de infraestructura). Son cosas radicalmente diferentes.
673: 
674: ### 7.4 Cómo ve el LLM cada error (traducción al protocolo)
675: 
676: La taxonomía de arriba está escrita en términos de excepciones Python. El agente nunca la lee así: la consume como **texto dentro del `content` del tool result**.
677: 
678: - **Regla de transporte:** el error **no se propaga como excepción de protocolo**; se devuelve `isError: true` con el mensaje en el resultado, para que el LLM lo lea en el mismo turno y pueda corregir o reintentar. Perderlo a nivel de transporte es perder la información.
679: - **Regla de contenido:** nunca traceback. Un `error_code` estable + un mensaje accionable.
680: 
681: | Error Python         | `error_code` REST/HTTP | Traducción MCP                            | Lectura del agente                |
682: | -------------------- | --------------------- | ------------------------------------------ | --------------------------------- |
683: | `ValidationError`    | `400 INVALID_ARGUMENT` | `isError: true` + código + mensaje        | "mis argumentos están mal, corrijo" |
684: | `NotFoundError`      | `404 NO_DATA`          | `isError: true` + código + mensaje        | "no hay datos" (resultado válido) |
685: | `BusinessRuleError`  | `422 BUSINESS_RULE`    | `isError: true` + código + regla violada  | "la regla X no se cumple"          |
686: | `AuthorizationError` | `403 FORBIDDEN`        | `isError: true` + código (sin detalle)    | "no puedo, no reintento"           |
687: | `InfrastructureError`| `503 UNAVAILABLE`      | `isError: true` + código + "reintenta"     | "falla la fuente, reintento"       |
688: 
689: - El mapeo vive en **un solo lugar** (el translator de errores del adapter MCP), no en cada service.
690: - `AuthorizationError` **nunca** revela qué regla de autorización falló: el agente solo necesita saber que debe detenerse.
691: 
692: ---
693: 
694: ## 8. Catálogo de capacidades de negocio
695: 
696: ### 8.1 Ejemplos de capabilities (conocimiento operativo)
697: 
698: En lugar de `get_agendas()`, `get_pacientes()`, `get_pagos()`, `get_facturas()`:
699: 
700: ```
701: consultar_disponibilidad
702: detectar_horas_sin_ocupacion
703: pacientes_con_deuda_vencida

(Showing lines 672-703 of 1581. Use offset=704 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 6.2s)

Listo. Apliqué las 7 observaciones de Claude al cuerpo del documento y las marqué con estado en su propio apartado.

**Cambios en el cuerpo:**

| Obs | Dónde quedó |
|---|---|
| 1. Annotations MCP | Nueva **R17** con tabla `operation.mode → annotations`; bloque `mcp.annotations` en §9.1/§9.3; R4 amended; adapter §11.3 las toma del registry; contract test §12 Nivel 3 |
| 2. `description` como contrato | R6 amended + R17b; campo `usage_notes` en §9.1; descripción y ejemplos `in`/`out` reales en §9.3 y §11.3; Nivel 4 deriva casos de `usage_notes` |
| 3. Escalado del catálogo | Nueva **R20** (namespacing vs split por dominio, umbral ~15 tools) + filas en §3, §16.2, §16.3, §9.4 |
| 4. Versionado vs MCP | R10 con restricción explícita: MCP expone solo la versión vigente, coexistencia v1/v2 en REST; ficha §9.3 sin sufijo; invariante en §12 |
| 5. Errores hacia el LLM | Nueva **R18** + **§7.4** con tabla de traducción por tipo de error; `errors` como mapa con `error_code`/`message` en §9.1 y §9.3 |
| 6. Transporte MCP | Nueva **§5.5** con criterios de decisión y restricción dura (sin identidad por request, R8 no es viable); subido a P0 en §3, §16.1, §16.3 |
| 7. Rate de agente | Nueva **R19** con `agent_traffic` (`max_calls_per_session`, `expected_cost`); R11 declara su límite de supuesto; P1 en §16.2 |
| N. Django | **§15**: queda escrito que el enablement layer es FastAPI+FastMCP y Django/Vault es consumidor |

**Estado marcado en el listado de Claude:** los 7 puntos como ✅ Hecha (el 3 y el 7 explícitamente como P2 / declaración-sin-enforcement, que es lo que pedía la propia observación). El punto de Django quedó ⚠️ **Parcial**: la ambigüedad ya no es implícita, pero confirmar con el negocio si Django *debía* ser el enablement layer es una decisión que no puedo tomar desde el documento — lo dejé anotado en §15 y §16.3.

---

## User

Este es un ejemplo de un prompt function calling a modo de plantilla. Eres un asistente virtual avanzado con acceso a un conjunto de herramientas (tools) específicas. Tu objetivo es ayudar al usuario resolviendo su solicitud. 

Para hacerlo, debes analizar la petición del usuario y determinar si necesitas usar una o más de las herramientas disponibles.

### HERRAMIENTAS DISPONIBLES:
[
  {
    "name": "obtener_clima",
    "description": "Obtiene el clima actual para una ubicación geográfica específica.",
    "parameters": {
      "type": "object",
      "properties": {
        "ciudad": {
          "type": "string",
          "description": "El nombre de la ciudad y el país, ej. 'Madrid, España'"
        },
        "unidad": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "La unidad de temperatura a devolver."
        }
      },
      "required": ["ciudad"]
    }
  },
  {
    "name": "enviar_correo",
    "description": "Envía un correo electrónico a un destinatario específico.",
    "parameters": {
      "type": "object",
      "properties": {
        "destinatario": {
          "type": "string",
          "description": "Dirección de correo electrónico del receptor."
        },
        "asunto": {
          "type": "string",
          "description": "El tema del correo."
        },
        "cuerpo": {
          "type": "string",
          "description": "El mensaje principal del correo."
        }
      },
      "required": ["destinatario", "asunto", "cuerpo"]
    }
  }
]

### INSTRUCCIONES DE RESPUESTA:
1. Si la solicitud del usuario requiere una herramienta, DEBES responder EXCLUSIVAMENTE con un objeto JSON que indique la herramienta a llamar y sus argumentos. No agregues texto antes ni después del JSON.
   
   Ejemplo de formato de salida si se requiere una herramienta:
   {
     "tool_call": {
       "name": "nombre_de_la_herramienta",
       "arguments": {
         "parametro1": "valor1"
       }
     }
   }

2. Si la solicitud no requiere ninguna herramienta, responde normalmente con texto amigable. Entenderia que esta bien descrito las herramientas disponibles para satisfacer las preguntas del usaurio. Ahora suponte que le responde el json con los datos. Mi pregunta es si ademas de enviar un correo con los resultados, puedo solicitar que los datos del json se representen como graficas tipo kpi en el correo. Suponte tu que la tools del clima da la temperatura de 10 ciudades. Aparte de ejecutar el tools, puedo pedir en el mismo prompt que genere un dashboard adecuado, por ejemplo en un pdf, con los datos obtenidos? Esto es ejecutandolo desde una llamada por api del tipo openai o antrhopics

---

## Assistant (Build · Big Pickle · 30.0s)

_Thinking:_

The user is asking a technical question about function calling / MCP tools: can they, in addition to executing the tool and sending results by email, request in the same prompt that the JSON data be rendered as KPI-style charts in the email, or generate a dashboard/PDF?

This is a conceptual/architecture question, not a coding task. They're asking whether it's possible when calling via OpenAI/Anthropic APIs.

Answer: Yes, technically, but with important caveats:

1. The LLM does NOT render charts. It only emits tool_call JSON. Rendering requires deterministic code.
2. The pattern: tool returns JSON → your orchestrator (your code, not the LLM) takes the result and feeds it into a rendering pipeline (matplotlib/plotly → PNG/SVG → embedded into HTML email via MIME attachments or base64, or PDF via weasyprint/reportlab/fpdf2).
3. Two architectural options:
   - **Option A (recommended)**: the LLM's job ends at tool_call. Your deterministic code decides the presentation based on the data shape (or based on a "presentation" field the user requested, which the LLM emits as a second tool call).
   - **Option B**: add a second tool like `generar_dashboard_kpi` that takes the dataset + chart spec and returns a file (PDF/PNG). Then `enviar_correo` takes an `adjuntos` param with the file id/URL.
4. Important: the LLM shouldn't be trusted to produce chart specs blindly. Better: capability contract declares `chart_recommendation` / `supported_visualizations` per capability — this ties DIRECTLY to the document they have (R17, R20, the Tool Contract, `usage_notes`, decision-support tools). The contract should declare whether the output is tabular/aggregatable and what visualization it supports.
5. Direct answer on "same prompt": yes, in one user message the LLM can be instructed to do tool_call → then you return the tool result → then LLM calls a second tool (`generar_dashboard`, then `enviar_correo` con adjunto). That's multi-step agentic loop, totally standard with OpenAI/Anthropic. But note: the LLM's request for charts should be captured as structured intent, not free text.
6. Caveats: token cost of passing large JSON back to the LLM (better to pass aggregates); PDF generation determinism; email clients blocking; size limits; and data governance (their doc: forbidden_fields, PII — the PDF/email is a NEW egress channel, the governance R12 currently only covers MCP/LLM boundary, not the rendered artifact).
7. Also: for their doc, this means the "email sending" is an Action Tool (ACT mode → `readOnlyHint: false`, `destructiveHint: true`, requires human approval per R4). Sending a PDF with clinical data over email is exactly the kind of thing that should be gated.

Also relevant: their doc's R7 "exponer conocimiento, no tablas" — a chart request is really a dashboard/BI need, which suggests a capability that returns aggregates (KPI-ready), not raw rows. And the golden path for that.

Let me also mention the concrete implementation sketch briefly, and MCP-specific: MCP tool can return image content, and the client can render; but for the deterministic business case they want, do it server-side.

Should I write code? They didn't ask to write code in the repo. It's a question. I'll answer concisely but with enough substance. The system prompt says be concise (<4 lines) unless detail is asked. But this is a substantive technical question that requires explanation. The user asked a multi-part conceptual question. I'll give a moderately detailed answer but keep it tight — the guidance says be concise unless the user asks for detail. This question inherently requires detail. I'll use a structured but compact answer.

Let me write it in Spanish (user writes in Spanish).

Key structure:
- Sí, se puede — pero el LLM no dibuja nada.
- El bucle: user msg → tool_call clima → tu código ejecuta → JSON → (a) render determinista → (b) LLM 2º tool_call generar_dashboard → 3er tool_call enviar_correo con adjunto.
- Los 3 patrones (dónde decide el formato).
- Lo importante para su documento: declarar en el contrato; nueva tool = ACT; governance del artefacto.
- Límites / trampas.

I'll keep it compact with a code sketch of the loop.

Let me mention specific libs briefly: matplotlib/plotly → PNG; weasyprint/reportlab/fpdf2 para PDF; email con `MIMEApplication` / `add_attachment`; en Anthropic hay `document` content blocks; en OpenAI hay `image_url`. And MCP clients can render image content blocks.

Let me be careful to be accurate about APIs:
- OpenAI: tools/function calling, `tool_calls`, then `role: "tool"` message. Images: `image_url` data URL in user content. PDF: can use `input_file`/`file` in newer models.
- Anthropic: `tools`, `tool_use` blocks, then `tool_result` in a `user` message. Images: base64 `image` block. Documents: `document` block with base64 PDF.
- MCP: `tools/call` result can include `content` of type `text` or `image`.

Good. Also mention: better to send the PDF/attachment to the model as document so it can summarize, but for KPI rendering the code does it.

Now, tie-in to their doc (they're building the contract). This is the valuable part:
- `consultar_clima` would need to declare in its contract: `output.visualization` (supported: kpi_bar, table, gauge) — so the agent doesn't guess.
- The `enviar_correo` tool becomes an Action Tool: `mode: ACT` → `readOnlyHint: false`, `destructiveHint: true` + `openWorldHint: true` (email is an external system). Their R17 table already handles this — good example to cite.
- R12 governance: the rendered PDF is a new egress; `forbidden_fields` must apply to the artifact, not just the MCP response. Their current R12 only covers the LLM boundary.
- Also R19 (agent traffic) and the "dashboard" need: a KPI capability should be ANALYZE mode returning aggregates, not 10 raw rows rendered client-side.

I'll write it.

Length: this deserves detail. I'll aim for a compact but complete answer.

Sí, se puede — pero conviene separar dos cosas que el prompt de ejemplo mezcla: **quién decide el formato** y **quién dibuja**.

## Lo que el LLM nunca hace

El LLM solo emite `tool_call` JSON. No ejecuta la tool, no tiene matplotlib, no genera un PDF. Cualquier cosa que se vea como gráfico tiene que salir de **código determinístico tuyo**, entre el `tool_result` y el `enviar_correo`.

## El bucle real (una sola petición del usuario)

```
user: "dame el clima de 10 ciudades, mándame un correo y quiero un PDF con KPIs"
  ↓
LLM → tool_call obtener_clima(ciudades=[...])
  ↓
TU CÓDIGO ejecuta el tool → JSON (10 filas)
  ↓
LLM → tool_call generar_dashboard(dataset_id, tipo="kpi", enviar_como="pdf")
  ↓
TU CÓDIGO: plotly/matplotlib → PNG/SVG → weasyprint o fpdf2 → dashboard.pdf
  ↓
LLM → tool_call enviar_correo(destinatario, asunto, cuerpo, adjuntos=[dashboard.pdf])
```

Esto es un loop multi-turn normal en ambas APIs: en OpenAI respondes con `role:"tool"`, en Anthropic con un bloque `tool_result` en un mensaje `user`. El PDF lo generas y lo sirves tú (base64, S3, o el filesystem de tu backend); al modelo solo le pasas el resultado como `document`/`input_file` si quieres que lo lea o resuma.

## Las tres decisiones de diseño (esto es lo importante)

| Patrón | Quién decide el formato | Cuándo |
|---|---|---|
| **A. Declarativo** | El **contrato** de la capability declara qué visualizaciones soporta | Recommended: `consultar_clima` dice `output.visualization: [kpi_bar, table]`, no dejas que el agente invente |
| **B. Intención del LLM** | El LLM traduce "quiero KPIs" en un argumento estructurado (`tipo="kpi"`, `formato="pdf"`) | Funciona, pero solo si el schema limita el enum |
| **C. Implícito** | Tu pipeline decide por heurística según la forma del JSON |.Simple, pero frágil y no auditable |

## Lo que esto significa en tu documento

Esto calza exacto con lo que acabas de absorber de la revisión de Claude:

1. **`generar_dashboard` es una capability nueva**, no un parámetro de `enviar_correo`. Y `enviar_correo` deja de ser READ: es **Action Tool** → `mode: ACT`, `readOnlyHint: false`, `destructiveHint: true`, y `openWorldHint: true` (el correo es un sistema externo). Tu tabla de R17 ya cubre eso, pero conviene，把它 como el **primer caso real de ACT** para ejercitar el frontier que hoy está fuera de la milla cero.

2. **Tu R12 tiene un agujero que esto destapa.** Hoy gobernas `classification / forbidden_fields` para el cruce `Oracle → MCP → LLM`. Un PDF con datos clínicos enviado por correo es **un segundo egreso, no cubierto**. El `forbidden_fields` tiene que aplicarse **al artefacto renderizado**, no solo a la respuesta MCP. Si no, la regla se cumple para el LLM y se rompe dos metros después.

3. **Los KPIs son ANALYZE, no READ.** Si el dashboard necesita agregados, la capability correcta devuelve agregados (`ocupacion_promedio_por_unidad`), no 500 filas que el pipeline agrupa. Raw rows + agregación client-side es exactamente el anti-patrón de R7 ("exponer conocimiento, no tablas").

4. **Trampa de tokens**: si le devuelves las 10 filas al LLM para que "decida el chart", estás pagando la serialización dos veces y el LLM nunca dibuja. Que el `tool_result` sea compacto y que el dataset grande viva en tu backend referenciado por id.

---

## User

Dejame aclarar mi escenario para que no nos perdamos. PRimero generamos una estrategia y diriamos que ya esta bastabte avanzada. Tengo un patron claro para armar un servidor mcp y de api. Incluso el documento habla de capacidades ya acordadas para implementar. PEro el dia lunes actualizare el documento, el concepto es el mismo, pero cambiaremos los servicios, inicialmente son todos READ. Hoy a un gerente le llegan 6 correos de la actualidad operacional, de diferentes ambitos. Mi mill cero la redefiniere con uno de esos correos que se llama Control Contable, tecnicamente son 5 querys de diferentes informaciones, deuda, ingresos, boletas, creditos, promociones. El correo del tipo contable es un mail con formato html que representa la informacion en tablas. Toda la informacion deben ser unas 50 lineas. Quiero que mi primer mcp retorne la data contable. La tools devolvera imagino un json de 5 nodos con esa informacion. Hasta aqui dime si estamos claros para continuar con mi relato.

---

## Assistant (Plan · Big Pickle · 38.0s)

_Thinking:_

The user is clarifying their scenario. They want me to confirm I'm clear before they continue. Let me be careful — they asked "Hasta aquí dime si estamos claros para continuar con mi relato."

So they want a confirmation of understanding, and possibly flagging issues. I'm in plan mode, read-only. I should NOT edit files.

Let me reflect back what I understood, and flag the important observations that will matter. But they said "dime si estamos claros para continuar" — so they want me to confirm and let them continue. I should be concise but also raise the 2-3 things that matter so they can incorporate as they narrate.

Key things to reflect:
1. Strategy document is done and mature (the one I just edited). Monday they'll update it — same concept, but the capability changes.
2. Zero mile redefined: instead of `agenda.disponibilidad`, the first capability is **Control Contable** — driven by a real recurring email a manager receives.
3. The source is an HTML email with tables, ~50 rows total of operational/accounting info.
4. It decomposes into 5 queries: deuda, ingresos, boletas, creditos, promociones.
5. The first MCP tool should return this accounting data — imagined as a JSON with 5 nodes.

Now the important flags — I should be honest and useful, not just say "yes we're clear":

**Flag 1: This is a much better golden path than `agenda.disponibilidad`.** It's an ANALYZE-capable... well, actually it's 5 READ aggregations. It validates multiple sub-queries, real business value, verifiable by humans (the manager compares against the email he gets today), and it's already in production as a manual process. That's a stronger criterion-#1 fit than the old candidate. Worth noting.

**Flag 2: The key design decision — is this ONE capability with 5 sections, or FIVE capabilities?** This is the thing I most need from them. Their doc's rules (R1, R7, R16, R20 namespacing) push toward: 5 capabilities, each READ, each with its own contract, joined by an orchestrator. OR one capability `control_contable` that returns 5 typed nodes. Their own R16 ("una implementación, múltiples consumidores") and R7 ("exponer conocimiento, no tablas") suggest 5. But the consumer (the manager's email) wants all 5 together. This is exactly a "composite capability" / "report capability" design question. Big impact on the document.

**Flag 3: Verification source.** The email is the golden fixture. That means you have a **known-good expected output** — that's a gift for testing (Nivel 2/3 contract tests) and for data quality rules. They should think of it as a regression fixture. Their doc's R9 (data quality rules) has a perfect anchor here.

**Flag 4: The "json de 5 nodos" and the earlier dashboard question.** Their previous turn was about KPIs/PDF/email. So the trajectory is: Oracle → Python → MCP tool returns the 5 nodes → the agent renders the HTML table email (or a PDF) that replicates today's manual email. That's a coherent story and it's a strong candidate for the first ANALYZE-ish/decision-support demo. Worth confirming that's the arc.

**Flag 5: Risk / scope.** 5 queries means 5 Oracle queries. If each has different sources and different "rules" (e.g., what counts as a credit, what counts as a promotion), the scope is bigger than the old single-query golden path. Their doc explicitly warns against over-engineering the golden path. So: is this still "thin"? Recommendation: build the plumbing with ONE of the 5 (the simplest, e.g. boletas) as the true golden path, then replicate 4x — that proves the replication claim within the same capability family. But if they build all 5 at once, they lose the "capability #2 costs less than #1" proof. Actually — a good middle: the 5 are the same domain (contabilidad), so capability #2..#5 within the same domain is exactly the replication proof they want. But they'd be building the family in one go rather than proving it incrementally. Trade-off to raise.

**Flag 6: "¿50 líneas" matters** — that sets the output size / whether to paginate / whether the MCP result fits comfortably in context. Small = good, no pagination needed, no R19 rate concerns beyond trivial. But: is 50 lines the *email* (already aggregated by SQL) or the *raw data*? If the email is already the aggregation, then the Oracle queries are producing the same aggregation — meaning the 5 queries are already "cooked" and READ. Confirm.

Let me be careful not to overload. They asked a yes/no plus they want to continue narrating. I should:
- Confirm clear on the narrative so far
- Give the 2-3 things that matter (the composition question is the big one)
- Invite them to continue

I should keep it reasonably concise. Let me use a short confirmation + the key flags. I shouldn't ask a huge list of questions since they want to continue narrating — but I should flag the one bifurcation (1 vs 5 capabilities) because if they continue narrating without knowing that fork exists, they'll produce a narrative that has to be reworked.

Let me also note: in plan mode, I should not edit. I could offer to record the change but not do it.

Let me write it. Spanish, technical, direct.

I want to be careful about the "50 líneas" — the user said "Toda la informacion deben ser unas 50 lineas." Probably means the email has ~50 table rows total. That's per what? Per query or total? Ambiguous. Worth flagging lightly.

Let me draft:

Confirmación: sí, claro. 3-4 lines restating.

Then: "Antes de que sigas, hay una bifurcación que conviene que tengas presente" — the 1 vs 5 capabilities fork, with the 3 options and the doc's rules pointing to one.

Then: 3 observations that strengthen the proposal (email as golden fixture; verification; 5 queries = 5 Oracle sources).

Then: one scope caution.

Then: "sigue con tu relato".

Keep it tight. Maybe ~40 lines. Let me aim for that.

Actually the system prompt says be very concise. But this is a plan-mode planning conversation where the user explicitly asks for a comprehension check and there are genuine design forks. Detail is warranted here. I'll be structured and tight but complete.

Let me reconsider the composition question more carefully to give a real recommendation.

Their contract rules:
- R7: expose knowledge, not tables. "deuda" is knowledge, not a table.
- R1: one capability = one canonical business identity.
- R2: MCP name = semantic intent.

Option 1: ONE capability `control_contable` with output `{deuda: [...], ingresos: [...], boletas: [...], creditos: [...], promociones: [...]}`
- Pro: exactly mirrors the email = the business unit of work; one tool call per manager question; matches the consumer's mental model.
- Con: violates "one intention per tool" from the doc's own R17/description guidance — a single tool that does 5 things is hard for the LLM to select correctly and hard to test. And §12 Nivel 4 (agent picks the right tool) becomes mushy. Also any future need for just "deuda" forces you to decompose later.
- Also: the 5 sections have different data sources, different freshness, different rules → one contract with 5 data blocks is heavy.

Option 2: FIVE capabilities, each READ, namespaced `contabilidad.*` (R20), plus a composite/aggregate capability `control_contable` that composes them for the email.
- Pro: clean per R1/R7; each independently testable; scales (add `conciliacion` later); the aggregate is a thin orchestrator (SVC layer, not new logic).
- Con: 5 contracts to write; the agent may need 5 tool calls to answer the manager's question (or 1 via the composite).

Recommendation: Option 2, because the doc they just spent effort hardening (R1, R17 annotations, §12 Nivel 4, R20) all assume fine-grained tools. And crucially: option 2 gives them the *replication proof* for free — capability #2, #3, #4, #5 are all in the same family, so "the second capability costs less than the first" is demonstrated within the same milestone.

But there's a nuance: if they want ONE MCP call to reproduce the email, the composite tool is the answer. So the answer is: 5 leaf capabilities + 1 composite. That's 6 contracts though. Might be overkill for milla cero. Middle ground: 5 leaf capabilities and let the *agent* orchestrate the 5 calls (that's literally their §8.2 "investigación guiada por IA" / the CEO case). No composite needed for the milla cero. The composite can come later when the email reproduction is automated.

That's a clean, honest recommendation. Let me present it as: the fork is 1 vs 5; their own rules point to 5 leaves; the composite is optional/later; and the agent naturally does the 5 calls (which is the demo they want anyway).

Also worth noting: the HTML email is the **human-comparable acceptance criterion**. That's gold: it gives them a deterministic diff target. Their doc should say "the MCP output, rendered as the same HTML table, must match the email the manager receives today." That is a *verifiable by humans* criterion (§14.1 criterion 5) and it nails it.

And the scope caution: 5 queries = 5 legacy helpers potentially. Should ask whether the SQL already exists (does the legacy system already run these 5 queries to build the email? — if the email is generated BY the legacy system, then the queries exist and you just have to locate/copy them. If the email is manually assembled by an analyst, then the queries may not exist and you're designing 5 new aggregations = much bigger scope.)

That is actually a really important question. Let me flag it. The doc says legacy has hundreds of helpers — so likely the queries exist somewhere, or an analyst writes SQL manually in the BI tool. I should ask.

Let me write the response now. Concise, structured, with the fork and 2 questions.

Sí, estamos claros. Confirmo lo que entendí:

1. La estrategia está madura (el documento que acabamos de revisar).
2. El lunes cambian las capacidades del golden path — **mismo patrón, misma arquitectura, otro caso de negocio**.
3. Milla cero redefinida: en vez de `agenda.disponibilidad`, la primera capability es **Control Contable**, motivada por un proceso real en curso (el gerente recibe hoy ese mail a mano).
4. El caso se descompone en **5 consultas**: deuda, ingresos, boletas, créditos, promociones.
5. La fuente es un **mail HTML con tablas, ~50 líneas**; la tool devolverá un JSON con 5 nodos, uno por consulta.

Antes de que sigas, hay **una bifurcación de diseño** que conviene que tengas presente, porque cambia cómo se ve todo lo demás:

## ¿Una capability o cinco?

| | 1 capability `control_contable` (5 nodos) | 5 capabilities `contabilidad.*` (hojas) |
|---|---|---|
| Encaja con | el mail, que es una sola pieza | R1, R7, R2, R20, R17 |
| Tool selection (LLM) | una tool que hace 5 cosas → difuso | una intención → una tool |
| Testing §12 Nivel 3 | 1 contrato pesado con 5 bloques de datos | 5 contratos chicos, independientes |
| Riesgo | cada bloque tiene fuentes y reglas distintas → contrato inflado | 5 contratos que escribir |

**Mi lectura, dado el documento que acabamos de endurecer:** tus propias reglas (R7 "conocimiento, no tablas", R1 identidad por capacidad, R20 namespacing, y el Nivel 4 de testing que exige "una intención → una tool correcta") apuntan a **5 capacidades hoja READ**, con el agente orquestrando las 5 llamadas — que es literalmente el caso de §8.2 que ya tienes documentado.

El beneficio extra: `deuda → ingresos → boletas → créditos → promociones` **es la prueba de replicación que tu §14.4 exige** ("la #2 debe costar menos que la #1"), y la obtienes dentro de la misma milla cero en vez de dejarla para después.

La alternativa (1 tool compuesta que devuelve los 5 nodos) la dejaría para una **capacidad de reporte** posterior, cuando quieras automatizar el mail sin depender del agente.

## Dos preguntas que necesito antes de seguir

**a) ¿Quién arma ese mail hoy?** Si lo genera el sistema legacy (o una herramienta BI interna), **las 5 queries ya existen** y tu trabajo es localizarlas y portarlas al patrón Repository/Service. Si lo arma un analista con SQL a mano en una planilla, entonces no existen y estás diseñando 5 agregaciones nuevas — eso multiplica el alcance de la milla cero por 5.

**b) ¿El JSON de 5 nodos es la forma que quieres para el LLM, o es la forma "para el humano"?** Si el agente va a elegir tools, darle los 5 bloques juntos en un solo resultado es exactamente lo contrario de lo queRecommendamos arriba. Puedes tener ambas salidas si el contrato declara `compositions`, pero conviene que lo sepas antes.

## Lo que esto aporta y vale la pena que anotes el lunes

El mail actual es tu **fixture de aceptación**. Tienes un golden output conocido y comparable por un humano (§14.1, criterio 5: "resultado verificable por humanos"). Eso es oro para tres cosas a la vez: los contract tests de §12, las Data Quality Rules de R9 (hoy implícitas en un mail que nadie audita) y el criterio de éxito de la capability. Vale la pena que el documento lo diga explícitamente: *la salida de la tool, renderizada como las mismas tablas, debe coincidir con el mail que el gerente recibe hoy* — esa es la prueba de que la capa funciona.

Sigue con tu relato.

---

## User

El correo actual es generado por el legacy. Se ejecuta a ciera hora. Los programas del legacy generan el correo con mime type html. Literalmente dibujan el html con los datos de la query y lo adjuntan al body. Tengo todas las querys identificadas y documentdas (de hecho lo hiciste en la mañana). Lo del json con cinco nodos es solo una idea, de hecho me parece que quey deberia ser una tools. Y creo que aqui me pierdo en la comprension. Imagina que expones las 5 o las tools que sean necesarias, incluida una que envie mail. Mi prompt para el api declarara las tools disponibles y la pregunta del usuario sera algo asi como "envia un mail juan perez con el resultado contable." Lo mas probable que le llegue un correo a juna perez con la misma informacion con algun formato. Pero de fondo quiero que a juan perez le llegue un mail con un formato adecuado, moderno. Y quiero que el prompt ademas contenga instrucciones para generar una interpretacion de "Analista de datos" representada por una especie de dashboard con algunas kpi declaras. Ayudame a dar vida a esta idea. 

---

## Assistant (Plan · Big Pickle · 60.8s)

_Thinking:_

The user is clarifying. Let me re-read carefully.

Key facts:
1. The email is generated by the legacy. It runs at a fixed hour. The legacy programs generate the HTML email with mime type html, literally drawing the HTML with query data and attaching it to the body.
2. They have all the queries identified and documented ("de hecho lo hiciste en la mañana" — referring to earlier conversation, the doc mentions CALENDAR_DOC etc. Actually they say I did it in the morning. I should not falsely claim credit. I can note that the queries are already documented, but I should be honest — I don't have memory of that session. Careful: don't fabricate. I should just accept that they have them documented. Actually, it's fine to note that the doc they have references them. Hmm — better to not assert I did it. Just proceed.)
3. The 5-node JSON is just an idea, and actually they think it SHOULD be a tool each. "me parece que deberia ser una tool" each.
4. They feel they're losing understanding. Let me clarify their actual ask:
   - Expose the necessary tools (5 accounting queries + a send-email tool).
   - The API prompt declares available tools; user question: "envía un mail a Juan Pérez con el resultado contable."
   - Most likely Juan Pérez receives an email with the same information, in some format.
   - Underneath, they want Juan Pérez to get an email with an appropriate, modern format.
   - And the prompt should also contain instructions to generate a "data analyst" interpretation, represented by a kind of dashboard with some declared KPIs.
   - "Ayúdame a dar vida a esta idea."

So they want help fleshing out this design. They're in plan mode. So I should produce a plan/design, and ask clarifying questions.

This is a substantial architecture question. Let me think carefully about what's really being asked and what the right design is.

The user is conflating two things and wants help "giving life" to the idea. Let me decompose:

**The desired end-to-end flow:**
1. User (manager) asks an LLM/agent: "envía un mail a Juan Pérez con el resultado contable"
2. Agent calls the 5 accounting tools (READ, already exist as queries)
3. Agent then needs to produce: (a) a modern formatted email for Juan Pérez, (b) a "data analyst interpretation" as a dashboard with declared KPIs
4. Agent sends the email with attachments

**The critical architectural insight I need to give them:**

There are two fundamentally different things being conflated:
- **The email to Juan Pérez** = a *reproduction/replacement* of what the legacy does. This is the "kill a legacy feature" case.
- **The data analyst interpretation + dashboard KPIs** = a *new* capability. The legacy does NOT do this today. The legacy just draws tables.

This distinction matters enormously because:
- The 5 queries reproduce existing behavior → low risk, verifiable, golden path.
- The "analyst interpretation" + KPI dashboard is NEW business logic that no one has specified. The KPIs must be *declared* — by whom? That's a business decision, not a technical one. This is the actual risk in this plan.

**Second critical insight: the rendering must be deterministic.**

The user says "el prompt además contenga instrucciones para generar una interpretación de Analista de datos representada por una especie de dashboard con algunas KPIs declaradas."

This is the trap. If you put "generate a dashboard" in the prompt as an instruction, the LLM will:
- hallucinate the KPIs (invent metrics that aren't in the data)
- produce inconsistent formatting
- you cannot test it
- it violates the doc's own R7/R17 (contract-first, not prompt-first)

Their document is a monument to "the contract is the design, the LLM is a consumer." So the consistent answer is: **KPIs are declared in the capability contracts, not in the prompt.** The prompt only selects which tool to call.

This is the single most important thing to tell them. Their instinct ("el prompt contenga instrucciones para generar un dashboard") contradicts the architecture they spent a day building. I must flag it clearly but constructively.

Let me think about the right design.

**Proposed capability set:**

READ leaves (5):
- `consultar_deuda` (deuda)
- `consultar_ingresos` (ingresos)
- `consultar_boletas` (boletas)
- `consultar_creditos` (creditos)
- `consultar_promociones` (promociones)

Wait — I should be careful about naming. Their doc's R2/R3 rules: verb + business language, no getXxx. But also I don't know the actual business semantics precisely. "boletas" = receipts/tickets, "creditos" = credits (tax credits? store credits?), "promociones" = promotions/discounts. The business meaning of each is ambiguous and the rules differ. I should flag that the *rule definitions* need to be pinned down (R9 data quality).

ANALYZE / presentation capabilities:
- `renderizar_reporte_contable` — takes the 5 datasets, returns an HTML/markdown report using a template. Deterministic, no LLM.
- `calcular_kpis_contables` — takes the datasets, returns declared KPIs with values. Deterministic. This is where the KPI math lives.
- `generar_analisis` — takes datasets + KPIs, produces the narrative interpretation. **This is the only place the LLM is legitimately involved** — turning real numbers into prose. And even here, the LLM must not invent numbers; it gets the KPI payload as input and can only narrate.

ACT capabilities:
- `enviar_correo` — sends. This is where the ACT boundary gets exercised.

So the flow is: 5 READ → 1 ANALYZE (KPIs) → 1 ANALYZE (analysis) → 1 compose (render) → 1 ACT (send).

**Key: the email body is a rendering of a template + data, not something the LLM writes freely.** Modern format = an HTML email template (responsive, table layout, inline CSS because email clients). The LLM contributes: a subject line suggestion, a short summary paragraph, and the "analyst interpretation" block. Everything else is deterministic.

**Now, an important question: is this still a "milla cero" for the doc?**

The user's document defines Fase 1 as READ + ANALYZE, with ACT explicitly OUT of the milla cero. `enviar_correo` is ACT. So this scenario crosses the boundary the document froze.

This is a real tension I must raise. Options:
- (A) Milla cero = the 5 READ + KPIs + render. The email sending stays manual (human copies the rendered report into their mail client, or the legacy cron still sends). This keeps the frozen boundary intact.
- (B) Milla cero includes `enviar_correo` as the first ACT tool. Requires opening the ACT design questions: idempotencia, aprobación humana, autorización, rollback, doble ejecución. The document says those were *eliminated* by keeping ACT out.
- (C) Two-stage: milla cero = READ+ANALYZE producing an HTML report artifact (a file, viewable in a browser). Then milla cero + 1 week = add `enviar_correo` as the first, carefully-gated ACT tool.

I'd recommend (C) or (A). Actually, thinking about it more: the business value is "Juan Pérez receives a modern email." Without the send, the demo is "a browser shows a nice report." That's still valuable but it doesn't kill the legacy cron. The real "strangle" happens when the send is automated.

So I should be honest: **this scenario deliberately crosses the ACT boundary your document froze.** That's not a problem — it's an evolution — but it must be an explicit, conscious decision on Monday, and the doc's §15/§16.1 should be updated to say "primer ACT: enviar_correo (reemplaza el cron del legacy)".

And here's a nice insight: the legacy already does this send (the cron job at a fixed hour). So `enviar_correo` is NOT a new capability with unknown risk — it's a **replacement of a known, scheduled, single-recipient operation**. The risk profile is completely different from "create_reserva". That's a huge de-risking argument. I should make it: this is the cheapest possible first ACT tool, because the semantics are already frozen by the legacy (fixed hour, fixed recipient list, fixed format).

**Another key point: idempotency / double-send.** The legacy runs at a fixed hour. If the agent sends on demand, you can double-send. So `enviar_correo` needs: a `periodo` (e.g., "2026-09-25" or "CierreAgosto"), and the system must check whether that period was already sent. This is the concrete form of the R4/R10 concern. I should mention it — it's the one real engineering problem in the whole scenario.

**Security/governance concern:** the accounting data going into an email. Their R12 (data governance). Accounting data = confidential. `allowed_fields` / `forbidden_fields` must be declared for the email artifact specifically. Also: is Juan Pérez authorized to receive this? `enviar_correo` is an ACT tool that exfiltrates data to an external system (email). That needs authorization: the agent shouldn't be able to send clinical/accounting data to an arbitrary address. This is a real security hole in the naive design — the LLM could be prompt-injected into emailing data elsewhere. I should flag this prominently. This is the "external system + sensitive data + autonomous action" combination.

**Now about MCP vs REST here.** Their doc: REST for dashboards/apps, MCP for agents. The email flow is agent-driven → MCP. Fine.

**Let me also address their "me pierdo en la comprensión".** I should restate their idea back to them crisply in one diagram, because they said they're lost. That's a direct request.

**Format of my response:** This is plan mode. I should:
1. Reflect back their flow in one clear picture (they asked for this implicitly)
2. Flag the one thing that contradicts their own architecture (KPIs in the prompt)
3. Give the capability decomposition
4. Flag the ACT boundary issue + the double-send problem + the exfiltration/security issue
5. Ask the clarifying questions that matter

Let me think about what the real open questions are:
- Who declares the KPIs and what are they exactly? (business decision, blocking)
- Does the send replace the legacy cron (decommission) or coexist?
- Is `enviar_correo` allowed to take an arbitrary address, or a validated recipient from a directory?
- What's the acceptance criterion — does it have to match the legacy email's numbers, or is the new format free to show different things?

Let me not overload with questions. Pick the 3-4 that actually change the design.

Actually, let me reconsider the KPI-in-prompt point once more, because it's the crux and I want to be precise and useful rather than preachy.

The user said: "el prompt además contenga instrucciones para generar una interpretación de 'Analista de datos' representada por una especie de dashboard con algunas kpis declaradas."

Note "kpis declaradas" — they say *declared*. So they may already be sensing that KPIs should be declared somewhere. The question is: declared *in the prompt* or *in the contract*? I should give them the crisp reason why it must be the contract:

- The prompt is per-session and per-user. If Juan asks for it one way and María another, they get different numbers. Non-reproducible.
- You can't unit-test a prompt instruction.
- The LLM will do arithmetic inconsistently — that's the failure mode that kills trust in a demo in front of a manager.
- Their R9/R12 already say: rules are declared per capability, in the contract. KPIs are rules.
- §12 Nivel 4 exists precisely to test "given this intent, is the right tool available with the right args" — a prompt instruction can't be tested that way.

So: the prompt *selects*; the contract *declares*. And the "analyst interpretation" is the one legitimate LLM job, because it's prose over known numbers, not the numbers themselves.

I think that's a strong, honest, useful framing. Let me also give them the "the numbers must be computed twice by two independent paths and compared" test — that's a nice concrete acceptance test for the demo. Actually, better: the legacy email is the fixture. The new system's KPIs must tie out to the legacy email's numbers. That's the acceptance criterion.

Let me also handle: "Lo del json con cinco nodos es solo una idea, de hecho me parece que debería ser una tool." — They're saying each of the 5 should be a tool. I agree, that matches my earlier recommendation. Good, I should confirm that quickly and move on.

One more consideration: should the 5 tools each return their own shape? Yes. And a `periodo` param is probably shared. And the render step needs a way to reference already-fetched data — you don't want to re-query 5 times and pass 5 JSONs through the LLM context twice (their previous turn's concern). Options: a server-side `reporte` artifact (the ANALYZE tool composes and stores, returns a `reporte_id`), and then `enviar_correo(reporte_id, destinatario)`. That's much better than passing data through the LLM multiple times. This is the `dataset_id` idea from my previous answer. I should make it concrete.

Actually this is important and elegant: 
- The 5 READ tools return data to the agent (for the agent's understanding) — that's the LLM's view.
- But the actual bytes that get rendered/emailed should be produced server-side deterministically. So the ANALYZE tool re-derives from the repository (same queries), not from what the LLM passed back. This avoids passing 5 payloads through context twice AND avoids the LLM being able to tamper with numbers.

So: `generar_reporte_contable(periodo, formato)` → server-side: runs the 5 queries, computes KPIs, renders HTML, stores artifact, returns `{reporte_id, resumen_kpis, artefacto_url}`. Then the LLM can either just send it, or write a short commentary, then `enviar_correo(reporte_id, destinatario, comentario)`.

This is clean. The 5 individual READ tools still exist and are still valuable (the manager can ask "¿cuánto debo?" without generating a full report), and they prove the replication pattern. But the *email* path doesn't route all the data through the LLM.

Hmm, but there's a duplication concern: now there's `consultar_deuda` AND `generar_reporte_contable` which internally calls the same. That's fine — same rule as R16: one implementation, multiple consumers. The service layer has `calcular_deuda()`, and both the leaf tool and the report tool consume it. No logic duplication. Good, that's consistent with their doc.

Let me make sure I present this clearly and not over-long. This is a meaty design question so some length is justified, but I should be disciplined.

Structure:
1. "Sí, ahora te lo devolvoy claro" — one flow diagram of their idea
2. The one thing I'd change: KPIs out of the prompt, into the contract. With the reason.
3. The capability decomposition (table) + the artifact/reference pattern
4. What the LLM does vs what the code does
5. Three things to be careful about (ACT boundary, double-send, exfiltration)
6. Questions I need answered

Let me write it. Spanish. Direct. Use their own vocabulary (capability, milla cero, ACT, R-numbers) so it feels like a continuation of the doc.

I need to be careful about length. Let me be tight but complete. I'll aim for something scannable.

Let me draft the flow diagram in mermaid (they use mermaid).

Actually for the "reflect back", a simple numbered flow is clearer than mermaid. But they like mermaid. Let me use a compact mermaid for the target architecture and prose for the rest.

Let me write.

On the "me pierdo en la comprensión" — I should be explicit: "tu idea es esta, confirmame". And clarify the one ambiguity: when they say "que le llegue un correo con la misma información con algún formato" — the information is the same, the format is modern. And separately there's the analyst interpretation. Are those the same email or two emails? That's a real question. One email with tables + a KPI dashboard + a short analyst note? Or the dashboard is an attachment? I should ask. Actually I'll propose the default (one email, with a KPI header block + the 5 tables + a short analyst note) and flag it as a question.

Let me finalize. I'll keep headers, use tables, and end with 3-4 sharp questions.

One more thought on the security issue — this is worth being emphatic about because it's the one that could actually cause a real incident: an agent that can email confidential accounting data to any address it decides is a prompt-injection exfiltration primitive. The recipient must be validated against a directory/allowlist, and the agent must not be able to invent the address. In their contract terms: `enviar_correo` has `security.roles`, and the recipient resolution must be a separate step (`resolver_destinatario`) or a constraint on the input. I'll mention it as a design requirement, not a lecture.

Length check: I'll keep it disciplined. Let's go.

Ahora sí te lo devuelvo limpio, porque tu descripción mezcla dos capas distintas y ahí está la confusión.

## Tu idea, reformulada

```
Manager: "envía el resultado contable a Juan Pérez"
  ↓
Agente selecciona las capabilities de contabilidad (READ)
  ↓
Agente obtiene los datos
  ↓
Algo produce: (1) un email moderno con la misma información de hoy
              (2) una lectura de "analista de datos" con KPIs
  ↓
Agente envía el mail
```

Eso es coherente y es un caso de negocio **excelente** — probablemente mejor que `agenda.disponibilidad`. Tres razones: (a) las 5 queries **ya existen y están probadas en producción**; (b) el mail actual es un **fixture de aceptación** — un humano puede comparar número por número; (c) la replicación del patrón se demuestra con las 4 capabilities siguientes, dentro de la misma milla cero.

Y coincido contigo: **5 tools, no un JSON de 5 nodos.** Eso es lo correcto y encaja con tus reglas.

## Lo que yo cambiaría: las KPIs no van en el prompt

Dijiste "el prompt además contenga instrucciones para generar una interpretación de analista de datos con algunas KPIs declaradas". Entiendo la intuición, pero **las KPIs declaradas van en el contrato de la capability, no en el prompt**. Es la única razón:

> Un LLM no es confiable haciendo aritmética sobre datos de negocio. En la demo frente al gerente, si el mismo set de datos produce dos números distintos según quién preguntó, se acaba la credibilidad del proyecto — y no hay forma de testearlo ni de auditar por qué pasó.

Esto no es una preferencia mía, es literalmente tu propia arquitectura:

- **R9**: las reglas se declaran por capability, no se dejan implícitas en el código legacy.
- **R12**: la gobernanza es definición de diseño, no opcional.
- **§12 Nivel 4**: el test es "ante esta intención, ¿hay la tool correcta con los argumentos correctos?" — una instrucción en el prompt no es testeable así.

O sea: **el prompt selecciona, el contrato declara.** La parte de "interpretación de analista" sí es trabajo legítimo del LLM, porque es *prosa sobre números ya conocidos* — no es calcular los números.

## La descomposición que propongo

| # | Capability | Modo | Qué hace | Dónde vive la lógica |
|---|---|---|---|---|
| 1 | `consultar_deuda` | READ | Deuda |
| 2 | `consultar_ingresos` | READ | Ingresos |
| 3 | `consultar_boletas` | READ | Boletas |
| 4 | `consultar_creditos` | READ | Créditos |
| 5 | `consultar_promociones` | READ | Promociones |
| 6 | `calcular_kpis_contables` | ANALYZE | Aplica las reglas KPI declaradas y devuelve `{kpi: valor}` |
| 7 | `generar_reporte_contable` | ANALYZE | Renderiza HTML/PDF desde plantilla, corre en el server, devuelve `reporte_id` |
| 8 | `generar_analisis` | ANALYZE | LLM: redacta la lectura sobre los KPIs ya calculados |
| 9 | `enviar_correo` | **ACT** | Envía el `reporte_id` a un destinatario validado |

Sobre esto, tres notas importantes:

**a) Las 5 hojas siguen valiendo aunque el email no las use.** El gerente puede preguntar "¿cuánto debo?" sin generar un reporte completo. Y son las que prueban tu §14.4.

**b) El dato no debería pasar dos veces por el contexto del LLM.** Si el agente pide las 5, las renderiza, las manda por email y las pasa de vuelta al modelo para que escriba la interpretación, estás pagango la serialización dos veces y abriendo la puerta a que el LLM altere un número en el camino. La capacidad #7 re-deriva desde el repositorio y produce un artefacto con `reporte_id`. El LLM nunca carga con los 50 registros; carga con el resumen de KPIs. Esto es tu R16 aplicado: una implementación, varios consumidores — el service `calcular_deuda()` lo usan tanto la hoja #1 como el reporte #7. Cero lógica duplicada.

**c) El reparto LLM / código queda así:**

| Lo hace **código determinístico** | Lo hace el **LLM** |
|---|---|
| Consultar Oracle | Elegir qué tools llamar |
| Calcular los KPIs | Redactar el asunto |
| Filtrar campos permitidos / prohibidos (R12) | Escribir el párrafo de lectura |
| Renderizar HTML, KPI blocks, tablas | |
| Enviar | |

## Tres cosas de las que me ocuparía antes de escribir código

**1. `enviar_correo` es un ACT, y tu documentorozen esa frontera.** §15 dice que las Action Tools están fuera de la milla cero. Pero hay unaGOOD news: **este es el ACT más barato que podrías elegir**, porque la semántica ya está congelada por el legacy — hora fija, destinatarios fijos, formato fijo. No es `crear_reserva` con riesgo desconocido. Aun así hay que cruzar la frontera *a propósito*, no de rebote. Sugiero: milla cero = 1-7, y `enviar_correo` como hito siguiente y explícito ("reemplaza el cron del legacy"). La sección "Decisiones técnicas abiertas" del lunes debería reconocer esto.

**2. El doble envío es el problema de ingeniería real de este caso.** El legacy corre a hora fija; el agente envía bajo demanda. Si le piden dos veces, Juan Pérez recibe dos correos. Necesita un `periodo` (tipo `cierre-2026-08`) y verificación de si ese período ya se envió. Es la forma concreta del `idempotentHint` de tus R17.

**3. El agente no debe poder inventar el destinatario.** Una tool que envía datos contables confidenciales a cualquier dirección que el modelo decida es un vector de exfiltración por prompt injection. El destinatario debería resolverse contra un directorio/allowlist, y si no existe, fallar — no adivinar.

## Lo que necesito de ti para seguir

1. **¿Quién declara las KPIs y cuáles son?** Es decisión de negocio y bloquea el diseño de la #6. ¿"Deuda total" significa saldo insoluto, incluye provisiones, aging? Esto es exactamente las Data Quality Rules de R9, y hoy viven implícitas en el código del cron.
2. **¿Reemplazamos el cron del legacy?** Si sí, esto es StranglerFig fase 3 desde el primer día y hay que decirlo. Si no, conviven.
3. **¿Un solo mail o dos entregables?** Mi supuesto: un mail con bloque de KPIs arriba, las 5 tablas debajo, y el párrafo de lectura al final. El "dashboard" como HTML inline (no PDF), porque en un correo un PDF adjunto no se mira.
4. **La comparación de aceptación:** ¿las cifras nuevas tienen que cuadrar exactamente con el mail del legacy, o el formato nuevo puede mostrar cosas distintas? Esto define si es un reemplazo verificable o un producto nuevo.

---


