# DREAMS Explorer — Estrategia de Modernización DentWeb12

> **Documento base:** DREAMS_02 · Agosto 2026
> **Sistema:** DentWeb12 — Java 21, Payara 7, JSP (Model 1), Oracle 11g XE
> **Estado:** Estrategia en definición · Fase A (Understand) completada

---

## Índice

### PARTE I — Los 39 Pasos Estratégicos

**Fase: Contexto y Diagnóstico**
- [1. Contexto: El Ferrari del 89](#1-contexto-el-ferrari-del-89)
- [2. Los 3 frentes de transformación y el costo de la inacción](#2-los-3-frentes-de-transformación-y-el-costo-de-la-inacción)
- [3. Frente 1: Hacer explícito el modelo relacional](#3-frente-1-hacer-explícito-el-modelo-relacional)
- [4. Frente 2: Oracle → PostgreSQL](#4-frente-2-oracle--postgresql)
- [5. Frente 3: Modernización profunda de la aplicación](#5-frente-3-modernización-profunda-de-la-aplicación)
- [6. Arquitectura actual vs. arquitectura objetivo](#6-arquitectura-actual-vs-arquitectura-objetivo)

**Fase: Evaluación Tecnológica**
- [7. Escenarios tecnológicos considerados](#7-escenarios-tecnológicos-considerados)
- [8. Frontend: alternativas y simpatía por Vue](#8-frontend-alternativas-y-simpatía-por-vue)

**Fase: Riesgos y Conocimiento**
- [9. El riesgo principal: conocimiento de reglas de negocio disperso](#9-el-riesgo-principal-conocimiento-de-reglas-de-negocio-disperso)
- [10. Hidden Logic Inventory](#10-hidden-logic-inventory)
- [11. Limitación del assessment actual](#11-limitación-del-assessment-actual)

**Fase: Validación y Metodología**
- [12. Validación por comportamiento y Characterization Testing](#12-validación-por-comportamiento-y-characterization-testing)
- [13. El rol de la IA en la modernización](#13-el-rol-de-la-ia-en-la-modernización)
- [14. Crítica a las estimaciones tradicionales y nuevo modelo](#14-crítica-a-las-estimaciones-tradicionales-y-nuevo-modelo)
- [15. Estrategias de migración discutidas](#15-estrategias-de-migración-discutidas)

**Fase: Arquitectura de Persistencia**
- [16. Escenario estratégico alternativo: no migrar Oracle primero](#16-escenario-estratégico-alternativo-no-migrar-oracle-primero)
- [17. Ventajas y riesgos de modernizar la aplicación antes que la BD](#17-ventajas-y-riesgos-de-modernizar-la-aplicación-antes-que-la-bd)
- [18. Punto arquitectónico clave: separar modelo de dominio del modelo físico](#18-punto-arquitectónico-clave-separar-modelo-de-dominio-del-modelo-físico)
- [19. Comparación de estrategias de orden](#19-comparación-de-estrategias-de-orden)
- [20. Arquitectura futura propuesta](#20-arquitectura-futura-propuesta)

**Fase: Metodología de Ejecución**
- [21. Principio: una dimensión por vez](#21-principio-una-dimensión-por-vez)
- [22. Los 6 Migration Control Points / Gates](#22-los-6-migration-control-points--gates)
- [23. Frente transversal: Business Knowledge Recovery](#23-frente-transversal-business-knowledge-recovery)
- [24. Modernization Readiness](#24-modernization-readiness)
- [25. Lo que NO se debe hacer vs. lo que SÍ parece estar decantando](#25-lo-que-no-se-debe-hacer-vs-lo-que-sí-parece-estar-decantando)
- [26. El rol de la IA y la pregunta estratégica principal](#26-el-rol-de-la-ia-y-la-pregunta-estratégica-principal)
- [27. Estado actual de las decisiones](#27-estado-actual-de-las-decisiones)
- [28. Roadmap: próximos pasos](#28-roadmap-próximos-pasos)
- [29. Conclusión provisional y frase de trabajo](#29-conclusión-provisional-y-frase-de-trabajo)

**⭐ HALLAZGOS CLAVE — Reencuadre Estratégico**
- [30. El legacy no es el enemigo](#30-el-legacy-no-es-el-enemigo)
- [31. Los tres problemas distintos](#31-los-tres-problemas-distintos)
- [32. Esto cambia la prioridad](#32-esto-cambia-la-prioridad)
- [33. El dossier como Knowledge Graph](#33-el-dossier-como-knowledge-graph)
- [34. Arquitectura híbrida: inteligencia sin tocar la app](#34-arquitectura-híbrida-inteligencia-sin-tocar-la-app)
- [35. Ejemplos de IA con valor de negocio concreto](#35-ejemplos-de-ia-con-valor-de-negocio-concreto)
- [36. Dos líneas paralelas de transformación](#36-dos-líneas-paralelas-de-transformación)
- [37. La secuencia de 6 fases](#37-la-secuencia-de-6-fases)
- [38. Cómo cambia la conversación con el CEO](#38-cómo-cambia-la-conversación-con-el-ceo)
- [39. Resuelve PostgreSQL + las 7 preguntas que reencuadran todo](#39-resuelve-postgresql--las-7-preguntas-que-reencuadran-todo)

### PARTE II — Estado Actual del Assessment
- [Situación de partida](#parte-ii--estado-actual-del-assessment)
- [Verificación de archivos RICH](#verificación-de-archivos-rich)
- [Lo que falta](#lo-que-falta-para-una-refactorización-efectiva)

### PARTE III — Sugerencias y Tormenta de Ideas
- [5 Estrategias de Refactorización Comparadas](#5-estrategias-de-refactorización-comparadas)
- [Tormenta de Ideas: 10 Estrategias Alternativas](#tormenta-de-ideas-10-estrategias-alternativas)
- [Matriz de Decisión: Impacto vs Esfuerzo](#matriz-de-decisión-impacto-vs-esfuerzo)
- [Recomendación Personalizada](#recomendación-personalizada)

---

# PARTE I — Los 39 Pasos Estratégicos

---

## 1. Contexto: El Ferrari del 89

### Stack actual

| Componente | Estado |
|------------|--------|
| **Lenguaje** | Java 21 |
| **Servidor** | Payara (Jakarta EE) |
| **Presentación** | JSP (Model 1) |
| **Base de datos** | Oracle 11g XE |
| **Arquitectura** | Estilo legacy — responsabilidades mezcladas |

El assessment técnico ya fue completado. El resultado es un dossier amplio que representa el principal conocimiento reconstruido de la aplicación hasta hoy.

En la superficie, los componentes individuales del stack (Java 21, Payara, Oracle) son **técnicamente potentes**. Pero la forma en que están ensamblados —presentación, lógica de negocio, acceso a datos y SQL frecuentemente entremezclados en los mismos archivos— responde a prácticas de otra época.

> «Tenemos un Ferrari... pero del 89.»

La metáfora captura la esencia: el motor no es malo ni incapaz. El problema es que la arquitectura, la separación de responsabilidades, el modelo de datos y la forma de evolución **no aprovechan las capacidades tecnológicas actuales**. JSP puede contener lógica de aplicación; Java puede generar HTML; SQL puede alojar reglas de negocio; y las relaciones entre tablas deben inferirse desde el código o los datos porque no existen constraints explícitos.

> **Punto clave:** No se trata de que el sistema «no funcione». Funciona y es estable. El desafío es lo que **no permite hacer** hacia adelante: integrar con herramientas modernas, exponer APIs limpias, aplicar IA sobre los datos, o evolucionar con velocidad competitiva.

```mermaid
flowchart TD
    subgraph actual["Situacion actual: responsabilidades mezcladas"]
        JSP["JSP<br/>Presentacion - Logica<br/>Validacion - Flujo<br/>Acceso a datos"]
        JAVA["Java<br/>Negocio - Persistencia<br/>Generacion de HTML<br/>Controladores"]
        ORACLE["Oracle / SQL<br/>Datos - Reglas<br/>Procedures - tramites<br/>Triggers"]
    end
    actual --- JSP
    actual --- JAVA
    actual --- ORACLE
    style JSP fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style JAVA fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style ORACLE fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
```

---

## 2. Los 3 frentes de transformación y el costo de la inacción

Después del assessment se identificaron **tres grandes frentes iniciales** de transformación. No son proyectos independientes: se afectan mutuamente y comparten el mismo objetivo de fondo.

| Frente | Descripción |
|--------|-------------|
| **Frente 1** | **Modelo de datos** — Hacer explícito el modelo relacional: claves foráneas, integridad referencial, cardinalidades. |
| **Frente 2** | **Plataforma de datos** — Oracle → PostgreSQL. Evaluar viabilidad técnica de migración de SQL, PL/SQL, procedures, triggers, etc. |
| **Frente 3** | **Modernización de la aplicación** — Reemplazar frontend, backend, arquitectura y mecanismos de integración. |

### El costo de la inacción

No decidir es también una decisión, con consecuencias concretas para la aplicación, el negocio y el equipo:

> **1. La deuda técnica no se mantiene estable: se compone.** Cada nueva funcionalidad se construye **sobre** la ambigüedad existente. Cada desarrollador nuevo tarda más en entender el sistema. Cada corrección de bug tiene más probabilidad de generar efectos secundarios no previstos. El costo de no actuar hoy no es fijo, es **creciente**.

> **2. Conocimiento que solo existe en la cabeza de las personas.** Las reglas de negocio viven distribuidas en JSP, Java, SQL, triggers y procedures. Si esas personas dejan la organización, el conocimiento se va con ellas. No hay un modelo de dominio explícito del cual aprender.

> **3. Riesgo de continuidad operativa.** Dependencia de licenciamiento Oracle (costo recurrente). Payara requiere conocimiento especializado cada vez más escaso. Superficie de ataque difícil de asegurar cuando las capas están mezcladas.

> **4. Costo de oportunidad frente al negocio.** Cada funcionalidad nueva tarda más. No existe una capa de API limpia para integrar IA, apps móviles o terceros. La velocidad de respuesta se degrada mientras la competencia acelera.

> **No modernizar no significa «quedarse quieto». Significa seguir acumulando deuda técnica, riesgo de conocimiento, riesgo operativo y costo de oportunidad, con una base cada vez más grande y más cara de corregir.**

---

## 3. Frente 1: Hacer explícito el modelo relacional

La situación actual tiene relaciones que **existen funcionalmente** pero no están representadas mediante constraints relacionales explícitos. La intención es avanzar hacia relaciones explícitas, integridad referencial, claves foráneas, cardinalidades conocidas y reducción de datos huérfanos.

> **Importante:** Agregar FK no es una simple tarea de `ALTER TABLE`. La ausencia de FK puede estar ocultando registros huérfanos, relaciones implícitas, excepciones históricas, reglas de negocio y dependencias de procesos antiguos. Por lo tanto, construir el modelo relacional es también una actividad de **descubrimiento del negocio**.

```mermaid
flowchart LR
    A["Descubrimiento"] --> B["Data<br/>Profiling"]
    B --> C["Deteccion de<br/>inconsistencias"]
    C --> D["Validacion<br/>con negocio"]
    D --> E["Correccion /<br/>saneamiento"]
    E --> F["FK"]
    style F fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style C fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

### ¿Por qué debemos hacer esto?

- **Los datos pueden estar mintiendo sin que nadie lo note.** Sin integridad referencial, nada impide pedidos sin cliente o despachos sin pedido. Cada reporte, dashboard y decisión de negocio hereda esa incertidumbre.

- **Cualquier modernización construida sobre este modelo hereda su ambigüedad.** Si frontend y backend se modernizan pero el modelo sigue implícito, el nuevo sistema tendrá que adivinar las mismas relaciones.

- **Migrar a PostgreSQL sin este trabajo previo simplemente traslada el problema.** Migrar una base ambigua produce una base ambigua nueva, solo que en otro motor.

- **El costo de descubrir esto crece con el tiempo.** Cada mes se generan más registros con los mismos patrones ambiguos.

---

## 4. Frente 2: Oracle → PostgreSQL

Se realizó un primer análisis exploratorio. La conclusión inicial es que la migración parece **técnicamente viable**, pero requiere analizar en detalle: SQL, PL/SQL, procedures, functions, packages, triggers, views, secuencias, tipos de datos, transacciones, funciones específicas de Oracle, jobs, dependencias desde Java y JSP, y comportamiento implícito.

> **Advertencia importante:** No se debe convertir *Oracle legacy → PostgreSQL legacy* como objetivo final. La intención debe ser: *Oracle actual → Modelo real descubierto → Modelo lógico corregido → Modelo relacional objetivo → PostgreSQL*.

### ¿Por qué migrar a PostgreSQL es la jugada maestra?

- **Costo de licenciamiento.** Oracle cobra de forma recurrente y escala con el uso. PostgreSQL es open source: libera presupuesto que puede redirigirse a desarrollo.

- **Salir del vendor lock-in.** PostgreSQL es un estándar abierto ampliamente adoptado. Reduce la dependencia de un único proveedor.

- **Ecosistema y talento.** Es el motor de referencia para la mayoría de frameworks modernos (Spring Data, Django ORM, Prisma, SQLAlchemy). Encontrar talento es más simple y económico.

- **Compatibilidad cloud-native.** AWS, GCP y Azure ofrecen PostgreSQL como servicio administrado nativo con backups, réplicas, escalamiento y observabilidad.

- **Alineación con el resto de la modernización.** Spring Boot, Django o NestJS: en los tres, PostgreSQL es opción de primera clase. Esta decisión no compite con las otras, las potencia.

---

## 5. Frente 3: Modernización profunda de la aplicación

Este es el frente más complejo. No se trata de actualizar versiones. Se evalúa una modernización que podría llegar a reemplazar completamente frontend, backend, arquitectura, mecanismos de integración, forma de acceso a datos y eventualmente la base de datos.

```mermaid
flowchart TD
    A["Frontend desacoplado"] --> B["JSON / REST / API"]
    B --> C["Backend + Domain"]
    C --> D["Persistence Layer"]
    D --> E["Database"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style C fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

### ¿Por qué es urgente?

- **JSP con lógica mezclada frena la velocidad de desarrollo** y esa frenada empeora con el tiempo. Tareas que tomarían días en una arquitectura desacoplada toman semanas aquí.

- **No existe una API real.** Mientras la lógica esté acoplada al HTML, es imposible construir una app móvil, integrar con terceros, o conectar capacidades de IA.

- **El talento disponible para mantener JSP + Java/HTML se reduce.** Son patrones de una época anterior; el talento para stacks modernos es mucho más abundante.

- **La seguridad es más difícil de garantizar** cuando las capas están mezcladas. Separar capas permite aplicar controles consistentes en un solo lugar.

- **Cada año que pasa el «salto» necesario es más grande.** El ecosistema sigue avanzando. Postergar solo hace que crezca la distancia entre lo que tenemos y lo que el mercado necesita.

---

## 6. Arquitectura actual vs. arquitectura objetivo

### Situación actual: responsabilidades mezcladas

```mermaid
flowchart TD
    subgraph actual["Situacion actual"]
        J1["JSP"] --- J1P["Presentacion"]
        J1 --- J1L["Logica / Validacion"]
        J1 --- J1F["Flujo / Acceso a datos"]
        J2["Java"] --- J2N["Negocio / Persistencia"]
        J2 --- J2H["Generacion de HTML"]
        J2 --- J2P["Presentacion"]
        O1["Oracle / SQL"] --- O1D["Datos"]
        O1 --- O1R["Reglas de negocio"]
        O1 --- O1T["tramites / Procedures"]
    end
    style J1 fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style J2 fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style O1 fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
```

### Arquitectura objetivo

```mermaid
flowchart TD
    A["Frontend (Vue)"] --> B["API / JSON"]
    B --> C["Application Layer"]
    C --> D["Domain Layer"]
    D --> E["Repository / Persistence"]
    E --> F["Database"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style C fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style E fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style F fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

La transformación apunta a **responsabilidades claramente delimitadas** en cada capa, donde cada una depende solo de la capa inmediatamente inferior, y ninguna capa conoce detalles de implementación de las demás.

---

## 7. Escenarios tecnológicos considerados

Se evaluaron tres escenarios principales, dejando fuera .NET. Cada uno tiene ventajas, desventajas y un razonamiento específico de «¿por qué consideraríamos esto?».

### Escenario A — Java / Spring Boot

> **Stack:** Java 21+ · Spring Boot · Spring Security · Spring Data · REST · OpenAPI · PostgreSQL

| Ventajas | Riesgos |
|----------|---------|
| Mantiene Java como lenguaje | Riesgo de trasladar legacy sin modernizar |
| Reduce el salto tecnológico | JPA puede introducir malas decisiones |
| Ruta natural desde Java legacy | El equipo puede reproducir patrones antiguos |
| Transición progresiva posible | |
| Convivencia legacy/nuevo factible | |

> **¿Por qué considerarlo?** Reduce el número de variables desconocidas en un proceso que ya tiene suficiente incertidumbre. La prioridad es reducir riesgo, no maximizar productividad.

### Escenario B — Python / Django

> **Stack:** Django · DRF · FastAPI · SQLAlchemy · PostgreSQL

| Ventajas | Riesgos |
|----------|---------|
| Alta productividad | Mayor salto desde Java actual |
| Excelente ecosistema para IA y data | Cambiar lenguaje y ecosistema |
| Desarrollo rápido | La ventaja de productividad puede no compensar el riesgo |
| Framework maduro con convenciones | |

> **¿Por qué considerarlo?** Si se prioriza productividad e integración con IA por sobre continuidad. Django acelera la reconstrucción una vez que el dominio esté bien entendido.

### Escenario C — Node.js / NestJS

> **Stack:** Node.js · TypeScript · NestJS · REST/OpenAPI · PostgreSQL

| Ventajas | Riesgos |
|----------|---------|
| TypeScript con tipado fuerte | Mayor distancia de Java |
| Ecosistema moderno | Requiere consolidar prácticas empresariales |
| Compartir tipos frontend/backend | Puede convertirse en reescritura en vez de modernización |
| Buen encaje para APIs | |

> **¿Por qué considerarlo?** Si la prioridad es unificar lenguaje entre frontend y backend (TypeScript en ambos extremos) para reducir fricción entre equipos.

### Hipótesis emergente

> Existe una simpatía inicial por **Spring Boot + Vue**. No es una decisión definitiva. La simpatía se debe a que permite una evolución gradual: *Java legacy → Java moderno → Spring Boot → Domain limpio → PostgreSQL*, en lugar de cambiar simultáneamente lenguaje, arquitectura, frontend y base de datos.

---

## 8. Frontend: alternativas y simpatía por Vue

Se consideraron Vue, Angular, React, HTML/JS moderno con framework ligero, Bootstrap y Tailwind. La pregunta correcta no es «¿qué framework es mejor?» sino **«¿qué necesita realmente esta aplicación?»**

### Criterios relevantes para la decisión

Complejidad de UI · Formularios · Tablas · Workflows · Dashboards · Validaciones · Accesibilidad · Mantenimiento · Talento disponible · Integración APIs · Seguridad

### Simpatía inicial: Vue

> Principalmente por su **equilibrio entre capacidad, complejidad y facilidad para evolucionar** desde una aplicación web tradicional. Todavía no es una decisión definitiva.

---

## 9. El riesgo principal: conocimiento de reglas de negocio disperso

> **Conclusión clave:** La tecnología probablemente no sea el principal riesgo. El principal riesgo es **no saber exactamente dónde están todas las reglas de negocio**.

Las reglas pueden estar distribuidas entre:

`JSP` · `Java` · `SQL` · `Oracle` · `Procedures` · `Functions` · `Packages` · `Triggers` · `Views` · `Configuraciones` · `JavaScript` · `Sesiones` · `Validaciones` · `Estados` · `Códigos` · `Constantes` · `Integraciones`

```mermaid
flowchart LR
    A["Reglas distribuidas<br/>JSP + Java + SQL + Oracle"] -->|Recuperacion| B["Business Rules<br/>- Domain Model"]
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

---

## 10. Hidden Logic Inventory

Se considera **obligatorio** buscar sistemáticamente lógica oculta en todos los artefactos del sistema. El objetivo es construir un **Hidden Logic Inventory** clasificando cada hallazgo por severidad.

| Artefacto a inspeccionar | Qué buscar |
|--------------------------|------------|
| JSP | Lógica de negocio, validaciones, flujo, acceso a datos |
| Java | Responsabilidades múltiples, generación de HTML, lógica mezclada |
| SQL / Oracle | Reglas en queries, procedures, functions, packages, triggers |
| Jobs / Listeners | Comportamiento programado, side effects |
| Filtros / Interceptores | Lógica transversal no documentada |
| Endpoints no documentados | URLs con funcionalidad no mapeada |
| Configuración externa | Variables globales, valores hardcoded, códigos mágicos |
| Dependencias | Acoplamiento a Payara, funciones propietarias de Oracle |

### Clasificación por severidad

| Severidad | Descripción |
|-----------|-------------|
| 🟢 **Bajo** | Impacto localizado. |
| 🟡 **Medio** | Puede causar inconsistencias. |
| 🟠 **Alto** | Afecta integridad de datos o flujos críticos. |
| 🔴 **Crítico** | Pérdida o corrupción de datos. Riesgo operacional. |

---

## 11. Limitación del assessment actual

> **Advertencia explícita:** El análisis actual se realizó principalmente sobre el dossier técnico y no sobre el código fuente completo.

| Assessment documental | Assessment directo del código |
|----------------------|------------------------------|
| Lo que **creemos** que hace la aplicación, basado en el dossier reconstruido. Valioso como mapa, pero puede tener zonas grises. | Lo que el código **realmente** implementa, verificado línea por línea. Es la fuente de verdad última. |

### Implicancia práctica

Hasta que no se realice el análisis directo de fuentes, toda estimación de esfuerzo, elección de stack y plan de migración debe considerarse como **hipótesis de trabajo**, no como plan definitivo.

---

## 12. Validación por comportamiento y Characterization Testing

El nivel de confianza más alto se obtiene triangulando documentación, código y comportamiento real.

```mermaid
flowchart TD
    A["Documentacion<br/>(Dossier)"] --> C["Maxima confianza"]
    B["Codigo<br/>(Source)"] --> C
    D["Comportamiento<br/>(Runtime)"] --> C
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style C fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
```

### Characterization Testing

Capturar el comportamiento actual antes de reemplazar componentes. La meta es **demostrar equivalencia funcional**, no asumirla.

```mermaid
flowchart LR
    A["Legacy Input"] -->|Legacy Output| B["Legacy Output"]
    C["New Input"] -->|New Output| D["New Output"]
    B --- E["VS"]
    E --- D
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style C fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

---

## 13. El rol de la IA en la modernización

La transformación se pretende realizar con **fuerte asistencia de IA**: Codex, Claude, Gemini, OpenCode, modelos locales, agentes especializados.

```mermaid
flowchart LR
    A["AI Analysis"] -->|Human Review| B["Human Review"]
    B -->|AI Implementation| C["AI Implementation"]
    C --> D["Auto Tests"]
    D --> E["Human Validation"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style C fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

La mayor oportunidad está en recuperar conocimiento, encontrar reglas ocultas, analizar cientos de archivos, detectar dependencias y generar documentación y tests. Pero la **validación funcional y la responsabilidad sobre el negocio siguen siendo humanas**.

---

## 14. Crítica a las estimaciones tradicionales y nuevo modelo

La primera evaluación incluyó estimaciones poco atractivas, basadas en desarrollo tradicional. **Todavía NO se consideran estimaciones válidas.**

> «¿Cuánto trabajo es realmente humano y cuánto puede automatizarse o acelerarse mediante IA?»

| Actividad | Automatización IA | Esfuerzo humano | Riesgo |
|-----------|-------------------|-----------------|--------|
| Inventario de código | 🟢 Muy alta | Bajo | 🟢 Bajo |
| Documentación | 🟢 Muy alta | Bajo | 🟢 Bajo |
| Dependencias | 🟡 Alta | Medio | 🟡 Medio |
| Extracción de reglas | 🟡 Alta | 🔴 Alto | 🔴 Alto |
| Refactoring mecánico | 🟢 Muy alta | Medio | 🟡 Medio |
| DTO/API | 🟢 Muy alta | Bajo | 🟢 Bajo |
| Tests | 🟢 Muy alta | Medio | 🟡 Medio |
| Java → Spring | 🟡 Alta | 🔴 Alto | 🟠 Medio/Alto |
| JSP → Vue | 🟡 Alta | 🔴 Alto | 🟡 Medio |
| Validación funcional | 🔴 Baja | 🔴 Muy alto | 🔴 Crítico |

> **Piloto propuesto:** Tomar un módulo representativo y medir horas humanas, iteraciones de IA, tokens, errores, cobertura y equivalencia funcional. El resultado permite **extrapolar con evidencia**.

---

## 15. Estrategias de migración discutidas

| Estrategia | Descripción | Ventaja | Desventaja |
|-----------|-------------|---------|------------|
| **Big Bang** | Todo se reemplaza en una sola operación. | Arquitectura nueva completa. | 🔴 Riesgo extremadamente alto. **No preferida.** |
| **Strangler Fig** | El sistema nuevo reemplaza progresivamente al legacy. | Reduce riesgo. Permite aprender. | Mantiene dos mundos temporalmente. |
| **Por módulos** | Cada módulo se moderniza independientemente. | Permite priorizar. Facilita pilotos. | El acoplamiento puede dificultar la separación. |
| **Por capas** | Separar frontend, backend, dominio y persistencia. | Útil conceptualmente. | Las capas actuales están muy mezcladas. |
| **API-First** | Construir contratos claros entre frontend y backend. | Desacopla evolución. | Requiere definir contrato temprano. |
| **Reimplementación progresiva** | Construir funcionalidad nueva y retirar la antigua. | Convivencia. Validación continua. | Puede extenderse sin gates claros. |

> **Preferencia:** Combinación de **Strangler Fig + por módulos + API-First**, aplicando «una dimensión por vez» con characterization testing en cada etapa.

---

## 16. Escenario estratégico alternativo: no migrar Oracle primero

```mermaid
flowchart LR
    A["FASE 0<br/>Data Baseline<br/>no modificar<br/>Oracle"] --> B["FASE 1<br/>Modernizar<br/>Front + Back<br/>Vue + Spring"]
    B --> C["FASE 2<br/>Formalizar<br/>modelo<br/>relacional"]
    C --> D["FASE 3<br/>Oracle -<br/>PostgreSQL"]
    D --- E["Oracle permanece estable durante fases 0-2"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style C fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

> **La lógica:** Si se cambia simultáneamente Oracle→PostgreSQL, JSP→Vue, Java→Spring, Modelo→nuevo y API→nueva, y aparece un error, es muy difícil identificar la causa. Mantener Oracle estable durante las primeras fases provee un punto de comparación confiable.

---

## 17. Ventajas y riesgos de modernizar la aplicación antes que la BD

```mermaid
flowchart TD
    A["Legacy<br/>(JSP + Java)"] -->|Modernizacion| B["Spring Boot + Vue"]
    A -->|Comparte| C["Oracle"]
    B -->|Comparte| C
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style C fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

Se dispone temporalmente de un punto estable de comparación.

> **Riesgo:** Construir un backend moderno sobre un modelo de datos legacy puede provocar que el nuevo backend reproduzca estructuras históricas y relaciones implícitas. **Por eso el nuevo backend NO debe acoplarse directamente al esquema físico de Oracle.**

---

## 18. Punto arquitectónico clave: separar modelo de dominio del modelo físico

```mermaid
flowchart TD
    A["Domain"] --> B["Repository (interface)"]
    B --> C["Oracle Adapter"]
    B --> D["PostgreSQL Adapter"]
    C --> E["Oracle"]
    D --> F["PostgreSQL"]
    style A fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style C fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style F fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

Esto permite **intercambiar el motor de base de datos sin que el dominio se entere del cambio**. El dominio solo conoce interfaces de repositorio; los adaptadores implementan esas interfaces para cada motor concreto.

---

## 19. Comparación de estrategias de orden

| Estrategia | Riesgo | Complejidad | Comentario |
|-----------|--------|-------------|------------|
| Oracle → PostgreSQL → Front/Backend | 🟠 Medio/Alto | Alta | Resuelve datos primero, pero deja la app desactualizada. |
| **Front/Backend → Modelo → PostgreSQL** | 🟡 Medio/Bajo | Media | **Aísla cambios. Permite validar contra Oracle estable.** |
| Todo simultáneo | 🔴 Muy alto | Muy alta | Difícil de controlar. Demasiadas variables. |

> **Estado:** No se ha tomado decisión definitiva. *Front/Backend → Modelo → PostgreSQL* es la hipótesis más atractiva en este momento.

---

## 20. Arquitectura futura propuesta

```mermaid
flowchart TD
    A["VUE"] --> B["JSON / API"]
    B --> C["SPRING BOOT"]
    C --> D["Application"]
    C --> E["Domain"]
    D --> F["Repository"]
    E --> F
    F --> G["Oracle Adapter"]
    F --> H["PostgreSQL Adapter"]
    G --> I["Oracle"]
    H --> J["PostgreSQL"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style C fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style D fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style E fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style F fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style G fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style H fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style I fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style J fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

---

## 21. Principio: una dimensión por vez

La estrategia propone abordar 5 dimensiones de transformación, evitando cambiar demasiadas variables críticas al mismo tiempo.

| Dimensión | Transformación |
|-----------|---------------|
| **Dimensión 1 — Datos** | Oracle → PostgreSQL |
| **Dimensión 2 — Modelo** | Implícito → Explícito |
| **Dimensión 3 — Backend** | Java legacy → Spring Boot |
| **Dimensión 4 — Frontend** | JSP → Vue |
| **Dimensión 5 — Arquitectura** | Acoplada → Separada |

> «Una dimensión crítica a la vez, con evidencia y gates de validación.»

---

## 22. Los 6 Migration Control Points / Gates

Gates de control que actúan como puntos de validación obligatorios antes de avanzar a la siguiente etapa.

```mermaid
flowchart LR
    G1["Gate 1<br/>App moderna<br/>sobre Oracle"] --> G2["Gate 2<br/>Modelo<br/>relacional"]
    G2 --> G3["Gate 3<br/>Backend"]
    G3 --> G4["Gate 4<br/>Frontend"]
    G4 --> G5["Gate 5<br/>Base de<br/>datos"]
    G5 --> G6["Gate 6<br/>Cutover"]
    style G1 fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style G2 fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style G3 fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style G4 fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style G5 fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style G6 fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

| Gate | Nombre | Criterio de validación |
|------|--------|----------------------|
| **1** | App moderna sobre Oracle | Nueva app funciona correctamente sobre Oracle. |
| **2** | Modelo relacional | Relaciones e integridad referencial validadas. |
| **3** | Backend | Nuevo backend reproduce los casos de negocio. |
| **4** | Frontend | Nuevo frontend reproduce funcionalidad validada. |
| **5** | Base de datos | PostgreSQL reproduce comportamiento esperado. |
| **6** | Cutover | El legacy puede retirarse. |

> **Regla de operación:** Ningún gate se considera superado sin **evidencia concreta y reproducible**. No se avanza por opinión: se avanza porque se demostró.

---

## 23. Frente transversal: Business Knowledge Recovery

```mermaid
flowchart TD
    A["JSP"] --> F["Reglas de negocio"]
    B["Java"] --> F
    C["SQL"] --> F
    D["Oracle"] --> F
    E["Config"] --> F
    F --> G["Modelo de dominio"]
    G --> H["Nueva arquitectura"]
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style C fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style D fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style E fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style F fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style G fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style H fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

Este conocimiento es **probablemente el activo más importante** para que una modernización sea segura. Sin entender qué reglas gobiernan el negocio, cualquier reimplementación corre el riesgo de romper comportamientos que el negocio da por sentados.

---

## 24. Modernization Readiness

El assessment exploratorio pidió un score de 0 a 100 para medir el nivel de comprensión actual en múltiples dimensiones: arquitectura, negocio, código, BD, dependencias, reglas, testabilidad, acoplamiento, riesgo de migración y preparación general.

> **Nota:** La puntuación debe interpretarse considerando que el análisis actual carece del código fuente completo. El score subirá significativamente después del análisis directo de fuentes.

---

## 25. Lo que NO se debe hacer vs. lo que SÍ parece estar decantando

| Lo que NO (todavía) | Lo que SÍ |
|---------------------|-----------|
| Elegir definitivamente Spring Boot | Modernizar progresivamente |
| Elegir definitivamente Vue | Desacoplar primero la aplicación |
| Definir microservicios | Data Baseline como primer paso |
| Fijar duración definitiva | Modernización Front/Backend sobre Oracle |
| Comenzar migración masiva | Validación con characterization testing |
| Agregar FK sin profiling | Modelo relacional después del dominio |
| Migrar Oracle sin conocer dependencias | PostgreSQL como destino posterior |
| Hacer Big Bang | |

---

## 26. El rol de la IA y la pregunta estratégica principal

> **«¿Tenemos suficiente conocimiento y control sobre la aplicación como para comenzar una modernización profunda sin poner en riesgo el negocio?»**

Y si la respuesta todavía es NO:

> **«¿Qué debemos descubrir primero para llegar a ese punto?»**

---

## 27. Estado actual de las decisiones

### ✅ Confirmado / muy avanzado
- Assessment técnico terminado
- Dossier técnico amplio disponible
- Necesidad de modernización profunda
- Modelo de datos necesita formalización
- PostgreSQL es candidato serio
- Reglas de negocio ocultas son riesgo
- IA debe formar parte de la estrategia

### 🟡 Hipótesis
- Spring Boot como backend
- Vue como frontend
- Modernización progresiva
- Strangler / por módulos
- Characterization testing
- Mantener Oracle inicialmente
- PostgreSQL como destino posterior

### ⚪ Aún no decidido
- Stack definitivo
- Frontend definitivo
- Orden definitivo de migración
- Monolito vs. microservicios
- Momento Oracle → PostgreSQL
- Costos y duración

---

## 28. Roadmap: próximos pasos

Se sugieren 10 pasos secuenciales. El orden refleja dependencias: cada paso entrega información necesaria para los siguientes.

```mermaid
flowchart TD
    N1["#1 Mineria de datos,<br/>analytics e inteligencia<br/>de negocio"] --> N2["#2 Entregar fuentes<br/>reales a agentes"]
    N2 --> N3["#3 Source-Based<br/>Modernization Assessment"]
    N3 --> N4["#4 Construir inventario<br/>completo"]
    N4 --> N5["#5 Data Baseline<br/>de Oracle"]
    N5 --> N6["#6 Seleccionar modulo<br/>representativo"]
    N6 --> N7["#7 Piloto con IA"]
    N7 --> N8["#8 Medir esfuerzo real<br/>y comparar stacks"]
    N8 --> N9["#9 Definir arquitectura<br/>objetivo"]
    N9 --> N10["#10 Definir roadmap<br/>basado en evidencia"]
    style N1 fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style N7 fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style N10 fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
```

| # | Paso | Descripción |
|---|------|-------------|
| **1** | **MINERÍA DE DATOS** | Explotar los datos del sistema actual con analytics, BI, RAG y agentes de IA **sin tocar la aplicación operacional**. Construir una capa de inteligencia que demuestre valor de negocio concreto en semanas, no en meses. |
| **2** | Entregar fuentes reales | Java, JSP, SQL, configuración, scripts, archivos de despliegue. |
| **3** | Source-Based Assessment | Análisis directo del código para validar y extender el dossier actual. |
| **4** | Inventario completo | Clases, JSP, SQL, procedures, triggers, endpoints, reglas y dependencias. |
| **5** | Data Baseline de Oracle | Snapshot del estado actual sin modificar la BD. |
| **6** | Módulo representativo | Que concentre complejidad de negocio. |
| **7** | Piloto con IA | Legacy → Characterization Tests → Spring Boot → Vue → Validation. |
| **8** | Medir esfuerzo real | Java/Spring, Python/Django, Node/TypeScript con datos del piloto. |
| **9** | Arquitectura objetivo | Basada en evidencia del piloto. |
| **10** | Roadmap basado en evidencia | Con estimaciones calibradas por el piloto real. |

---

## 29. Conclusión provisional y frase de trabajo

> **«¿Cómo podemos transformar esta aplicación reduciendo progresivamente el riesgo, preservando las reglas de negocio y utilizando IA para disminuir radicalmente el esfuerzo tradicional de modernización?»**

> «No queremos reescribir la aplicación. Queremos recuperar su conocimiento, separar sus responsabilidades, preservar su comportamiento y reemplazar progresivamente su tecnología.»

> «Una dimensión crítica a la vez, con evidencia y gates de validación.»

---

# ⭐ HALLAZGOS CLAVE — Reencuadre Estratégico

> **Este bloque de pasos (30-39) es distinto del resto del documento.** No contiene «una idea más»: contiene el **reencuadre estratégico** que cambió la prioridad de todo el análisis anterior. Lo que sigue no es una continuación lineal del punto 29, sino una relectura del problema completo que abre una segunda línea de transformación paralela, con lógica y cronograma propios.

---

## 30. El legacy no es el enemigo

La aplicación actual **es estable, no se cae, soporta los flujos de la clínica y es eficiente**. Lleva años acumulando reglas y tiene buena cobertura funcional. No deberíamos destruir esto por entusiasmo tecnológico.

> «No modernicemos porque sea viejo. Modernicemos donde lo viejo impida evolucionar.»

Si el sistema hace perfectamente *Doctor → Paciente → Atención → Tratamiento → Caja*, no existe urgencia de reemplazarlo. El problema aparece cuando queremos hacer *Paciente → histórico → comportamiento → predicción → alerta → decisión*, y ahí el sistema empieza a quedarse corto.

> **El verdadero dolor del negocio:** No es la aplicación: es que **el conocimiento que contiene no está siendo explotado**. El sistema genera datos valiosos todos los días, pero esos datos no se convierten en inteligencia operacional. Eso cambia muchísimo la estrategia.

---

## 31. Los tres problemas distintos

Hasta ahora los habíamos mezclado bajo un solo paraguas de «modernización». Pero son tres problemas de naturaleza distinta, y cada uno requiere un abordaje diferente.

| Problema | Descripción | Urgencia |
|----------|-------------|----------|
| **Problema A — Legacy tecnológico** | JSP, Java, Payara, Oracle, arquitectura acoplada. Es real pero no es el dolor más urgente. La aplicación funciona. | Media |
| **Problema B — Modelo de información** | Sin relaciones explícitas, EAV, relaciones implícitas, SQL complejo. Obstaculiza analytics pero no detiene la operación. | Media |
| **Problema C — Explotación del conocimiento** | Datos → reportes cuando el negocio quiere Datos → contexto → análisis → predicción → alerta → decisión. **Este es hoy el dolor real.** | 🔴 Alta |

> **El cambio de enfoque:** El Problema C puede atacarse **sin resolver primero A y B**. Eso cambia completamente la ecuación de prioridades y de inversión. No necesitamos esperar a tener el modelo relacional perfecto ni la app modernizada para empezar a generar valor de negocio con IA.

---

## 32. Esto cambia la prioridad

Antes del hallazgo, la prioridad era: BD → Backend → Frontend. Ahora probablemente sería:

```mermaid
flowchart TD
    N["NEGOCIO"] --> O["OPERACION<br/>Aplicacion actual (estable)"]
    N --> I["INTELIGENCIA<br/>Analytics / IA (nuevo valor)"]
    I --> D["Data Platform"]
    O --> D2["DATOS"]
    I --> D2
    style N fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style O fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style I fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D2 fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

> **Idea clave:** **No necesitamos esperar a modernizar toda la aplicación para empezar a generar valor con IA.** Podemos construir una capa de inteligencia sobre el sistema existente mientras la aplicación operacional permanece intacta sobre Oracle. Esto separa el problema tecnológico del problema de negocio y genera el apoyo ejecutivo necesario para financiar después la modernización profunda.

---

## 33. El dossier como Knowledge Graph

El dossier que se construyó no es solamente documentación. Es una especie de **Knowledge Graph humano de la aplicación**, aunque esté materializado como Markdown.

```mermaid
flowchart LR
    A["Capa actual (dossier)<br/>Programa - Java - JSP - SQL<br/>- Tabla - Campo - Relacion - Regla"] -->|Evolucion| B["Capa a agregar<br/>Campo - Significado de negocio<br/>- KPI - Regla analitica - Alerta - Prediccion"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

Esta es una evolución natural del trabajo ya hecho: tomar el conocimiento técnico capturado en el dossier y extenderlo hacia el dominio del negocio. Eso permite que los datos no solo se «documenten» sino que se **semanticen** para ser consumidos por herramientas de analytics e IA.

> **Conexión con LangChain / Text-to-SQL:** El modelo no relacional dificulta que un LLM entienda directamente el esquema operacional. Pero no necesitamos que el LLM entienda Oracle: podemos crear una **Semantic Data Layer** con un modelo analítico amigable (paciente, atención, tratamiento, pago, laboratorio, stock, comisión, agenda) y que el LLM consulte ese modelo, no el esquema físico con 100 columnas y EAV.

---

## 34. Arquitectura híbrida: inteligencia sin tocar la app

```mermaid
flowchart TD
    A["APLICACION (sin tocar)"] --> B["ORACLE"]
    B --> C["Aplicacion Operacional"]
    B --> D["Data Platform"]
    D --> E["Semantic Data Layer"]
    E --> F["BI - RAG - Text-to-SQL - AI Agents"]
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style C fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style F fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
```

El LLM consulta el modelo analítico, no el modelo operacional. No tiene que entender EAV, DECODE, JOINs históricos, relaciones implícitas ni 100 columnas. La transformación de datos ocurre en una capa intermedia que resuelve esa complejidad una sola vez, y el resto del ecosistema de inteligencia consume una representación limpia del negocio.

> **Consecuencia clave:** No necesariamente hay que decir «arreglar Oracle antes de hacer IA». Podemos decir: **«necesitamos construir una representación analítica del negocio que sea mucho más amigable para IA»**. Eso cambia la naturaleza del problema: de un prerrequisito bloqueante a una tarea paralelizable.

---

## 35. Ejemplos de IA con valor de negocio concreto

No se trata de «dame el reporte de laboratorio». Se trata de **«¿qué está pasando?»** y mejor aún: **«¿qué debería preocuparme?»**

### Laboratorio
No 100 columnas y 500 filas, sino: ⚠️ 12 trabajos con retraso > SLA · ⚠️ Laboratorio X concentra 38% de retrasos · ⚠️ Retraso aumentó 17% en 4 semanas · ⚠️ 6 compromisos de entrega probablemente no se cumplirán.

### Stock
Stock actual + consumo histórico + agenda futura + tiempo reposición + estacionalidad = **«El stock de X probablemente será insuficiente en 11 días»**. Ya no es reporting: es **Predictive Analytics**.

### Pagos
$X de cartera vencida · 72% concentrado en 8 clientes · Cliente Y presenta deterioro progresivo · Patrón histórico indica alta probabilidad de atraso adicional → **Risk Score** por cliente.

### Comisiones
Grupo X creció 22% · Crecimiento explicado por prestación Y · Desviación del patrón histórico · **«El comportamiento requiere revisión»**. La IA deja de ser chatbot y pasa a ser **Business Intelligence aumentado**.

> **Patrón común:** Reporte tradicional = datos crudos en tabla. Analytics aumentado = detección de anomalías, predicción, comparación con historia, alertas proactivas, recomendaciones accionables.

---

## 36. Dos líneas paralelas de transformación

```mermaid
flowchart TD
    T["TRANSFORMACION"] --> M["MODERNIZACION TECNOLOGICA<br/>Spring/Vue - APIs - PostgreSQL"]
    T --> I["INTELIGENCIA DEL NEGOCIO<br/>Analytics - IA - Prediccion - Agentes"]
    M --> D["DATOS"]
    I --> D
    D --- E["No necesariamente a la misma velocidad"]
    style T fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style M fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style I fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style E fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
```

La modernización tecnológica y la inteligencia del negocio pueden avanzar en paralelo, pero no necesariamente a la misma velocidad. La línea de inteligencia puede entregar valor en semanas (dashboards, alertas, predicciones sobre datos existentes), mientras que la línea de modernización del core requiere meses de análisis y migración controlada. **Ambas se refuerzan:** el valor demostrado por inteligencia genera el apoyo para financiar la modernización; la modernización mejora la calidad de los datos que alimentan la inteligencia.

---

## 37. La secuencia de 6 fases

El hallazgo sugiere una secuencia que prioriza la entrega de valor de negocio temprano, sin abandonar la modernización del core.

```mermaid
flowchart LR
    A["Fase A<br/>Understand<br/>✅ Ya realizada"] --> B["Fase B<br/>Expose<br/>Oracle - Semantic<br/>Data Layer"]
    B --> C["Fase C<br/>Intelligence<br/>BI, Dashboards,<br/>AI, Alerts"]
    C --> D["Fase D<br/>Modernize<br/>Core - Spring<br/>Boot + Vue"]
    D --> E["Fase E<br/>Transform Data<br/>Modelo relacional<br/>- PostgreSQL"]
    E --> F["Fase F<br/>Retire<br/>Legacy desaparece<br/>progresivamente"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style C fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style F fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
```

| Fase | Nombre | Descripción |
|------|--------|-------------|
| **A** | Understand | Assessment, Dossier, Data model. **✅ Ya realizada.** |
| **B** | Expose | Oracle → Semantic Data Layer. Acceso estructurado a datos. |
| **C** | Intelligence | **VALOR RÁPIDO.** BI, Dashboards, AI, Alerts. |
| **D** | Modernize | Core → Spring Boot + Vue. |
| **E** | Transform Data | Modelo relacional → PostgreSQL. |
| **F** | Retire | Legacy desaparece progresivamente. |

> **Propiedad clave de esta secuencia:** **Se demuestra valor antes de tocar el sistema operacional.** CEO quiere IA → Data Intelligence → Primeros casos reales → Valor demostrado → Apoyo para modernización. TI avanza la modernización progresivamente en paralelo. Son dos agendas que se refuerzan mutuamente.

---

## 38. Cómo cambia la conversación con el CEO

El argumento para el CEO se transforma completamente. De una conversación defensiva sobre tecnología antigua a una propuesta de creación de capacidad de negocio.

### Antes (mensaje débil)
> «Necesitamos modernizar porque Java, JSP y Payara son antiguos y Oracle es caro.»

Suena a proyecto de TI, a gasto, a riesgo sin beneficio claro.

### Ahora (mensaje fuerte)
> **«La aplicación actual funciona bien y no necesitamos reemplazarla por deporte tecnológico. Lo que necesitamos es convertir los datos que genera en inteligencia operacional. En paralelo, iremos modernizando progresivamente las partes que realmente aporten valor.»**

Esto es crear capacidad de negocio.

> **El ciclo virtuoso:** La minería de datos e inteligencia sobre el sistema actual **no compite con la modernización: la financia**. Al demostrar valor de negocio concreto en semanas —alertas de stock, predicción de pagos, analytics de laboratorio— se construye el caso para invertir en la modernización del core. Y cuando el core se moderniza, la calidad y accesibilidad de los datos mejora, potenciando aún más la capa de inteligencia.

---

## 39. Resuelve PostgreSQL + las 7 preguntas que reencuadran todo

### Cómo esto resuelve la discusión de PostgreSQL

PostgreSQL deja de ser «tenemos que migrar porque Oracle es viejo» y se convierte en **«necesitamos una plataforma de datos que soporte nuestra siguiente generación de analytics, integración e IA»**. Es un argumento de negocio, no tecnológico. Y abre posibilidades que antes no se consideraban: réplica, warehouse, arquitectura híbrida, modelo analítico separado.

### Las 7 preguntas que reencuadran todo el problema

1. ¿Cómo extraemos conocimiento del sistema actual?
2. ¿Cómo hacemos que los datos sean entendibles para máquinas y personas?
3. ¿Cómo entregamos inteligencia de negocio rápidamente?
4. ¿Qué parte de la aplicación realmente merece ser modernizada?
5. ¿Qué parte simplemente podemos dejar tranquila?
6. ¿Cuál es el momento correcto para cambiar Oracle?
7. ¿Qué puede hacer la IA para acelerar cada transformación?

> **«No migramos la aplicación completa. Construimos primero una capa de inteligencia sobre el sistema existente, modernizamos después el core que realmente importa y dejamos que el resto del legacy muera lentamente por falta de necesidad.»**

> Y, paradójicamente, eso podría ser mucho más transformador para la clínica que una reescritura completa de Java/JSP.

---

---

# PARTE II — Estado Actual del Assessment

---

## Situación de partida

### Lo que ya existe (cobertura documental completa)

El dossier técnico de DentWeb12 es **excepcionalmente completo** para un sistema legacy. La siguiente tabla resume la cobertura:

| Directorio | Contenido | Archivos | Calidad |
|-----------|-----------|----------|---------|
| `assessment/app/` | Assessment de aplicación: inventario, arquitectura, capa datos, flujos E2E, algoritmos, riesgos, build/deploy | 7 docs | Exhaustivo — mega-clases de 5K-13K líneas documentadas |
| `assessment/db/` | Assessment de BD: esquemas, tablas, PL/SQL, conectividad, cruce Java↔BD, anomalías, contingencia | 7 docs | Oracle XE identificado, 0 FKs cuantificados |
| `assessment/relaciones-implicitas/` | Relaciones implícitas: 35 relaciones, cardinalidad, EAV, triggers, riesgos de integridad | 9 docs | 0% completitud relacional — dato crítico |
| `bd_diccionario/` | Diccionario de datos Oracle | 94 tablas | Cada tabla con campos, PKs, relaciones |
| `helper/` | Métodos helper con SQL embebido | 239 métodos | Cada uno con riesgo SQL injection y prioridad refactor |
| `llm/` | Clases Java documentadas (service, vo, pool, dent, util, etc.) | 250 RICH + 255 non-RICH | Diagramas Mermaid + metadata YAML |
| `jsp/dent/` | Páginas JSP documentadas | 439 RICH + 224 non-RICH | Flowcharts + class diagrams |
| `jasper/` | Templates de reportes JasperReports | 51 docs | 102 templates en el sistema |
| `raw_db_metadata/` | Metadata cruda de Oracle en JSON | 26 archivos | Columnas, constraints, índices, secuencias |

### Verificación de archivos RICH — Código fuente incrustado

**Confirmación verificada:** Los archivos RICH **SÍ contienen código fuente completo** incrustado bajo la sección `## Codigo Fuente`.

| Directorio | Archivos RICH | Con código | Sin código |
|-----------|--------------|-----------|-----------|
| `llm/` (todas las subcarpetas) | **250** | **250 (100%)** | 0 |
| `jsp/dent/` | **439** | **439 (100%)** | 0 |
| **Total** | **689** | **689 (100%)** | **0** |

#### Estructura de cada archivo RICH

```markdown
## 0. Resumen Ejecutivo y Metadatos     ← metadata YAML + ficha
## 1. Contexto Funcional y Arquitectura  ← flowcharts Mermaid
## 2. Definicion de Datos e Interfaces   ← class diagrams
## 3. Logica de Negocio                  ← sequence diagrams
## 4. Analisis Tecnico Detallado         ← state diagrams
## 5. Mantenibilidad, Errores y Seguridad
## 6. Integraciones y Servicios
## 7. Pruebas y Cobertura
## 8. Trazabilidad RAG y Matriz de Control
## Codigo Fuente                         ← ⬅ CÓDIGO COMPLETO
```java   // o ```jsp
[...código fuente completo sin truncar...]
```
```

#### Verificación de completitud del código

| Archivo | Líneas en metadata | Líneas reales | Coincide |
|---------|-------------------|---------------|----------|
| `ContableService.java` | 192 | 193 | ✅ |
| `ConexionDS.java` | 174 | 174 | ✅ |
| `BoletaVO.java` | 63 | 64 | ✅ |
| `agenda.jsp` | 988 | 989 | ✅ |
| `main.jsp` | — | 914 | ✅ |

### Lo que FALTA para una refactorización más efectiva

| Prioridad | Item | Impacto |
|-----------|------|---------|
| **1 (Alta)** | **Código fuente original del repositorio SVN** — Los RICH tienen el código pero no puedes ejecutar builds, hacer git diff, ni verificar compilation | Sin esto no ejecutas CI/CD |
| **2 (Alta)** | **Configuración Payara real** — `payara-web.xml`, `web.xml`, `domain.xml` del servidor | No sabes qué JNDI, pools, o configs están activas |
| **3 (Media)** | **Métricas de uso en producción** — Qué JSPs se usan, qué endpoints son calientes, qué tablas tienen más tráfico | No focalizas esfuerzo |
| **4 (Media)** | **Historial de SVN** — Commits recientes, quién toca qué, qué está vivo vs muerto | No distingues código activo de legacy |
| **5 (Baja)** | **Composición del equipo** — ¿Quién ejecuta? ¿Un solo dev + IA? ¿Equipo? | Impacta estimaciones y cronograma |

### Conclusión de situación

> **¿Es suficiente para iniciar una refactorización?** **SÍ.** El dossier es más completo que el 90% de proyectos legacy que existen. Los 689 archivos RICH con código fuente incrustado son un activo sin precedentes. La Fase A (Understand) está completada. El siguiente paso lógico es la **Fase A' (Source-Based Validation)**: usar los RICH files como insumo para que la IA valide y extienda el assessment directamente sobre el código, antes de construir el Semantic Layer.

---

---

# PARTE III — Sugerencias y Tormenta de Ideas

---

## 5 Estrategias de Refactorización Comparadas

### Estrategia 1: Intelligence-First (la que propone DREAMS)

> Construir una capa de inteligencia sobre el sistema existente sin tocar la aplicación operacional. Separar los problemas: (A) legacy tecnológico, (B) modelo de información, (C) explotación del conocimiento. Atacar C primero.

```mermaid
flowchart LR
    A["Oracle<br/>(sin tocar)"] --> B["Semantic<br/>Data Layer"]
    B --> C["BI / IA<br/>(valor rapido)"]
    B --> D["Data<br/>Platform"]
    D --> E["Modernizacion<br/>del core"]
    style A fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style B fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style C fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style E fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
```

| Aspecto | Evaluación |
|---------|------------|
| **Riesgo** | 🟢 Bajo — no toca el sistema operacional |
| **Valor temprano** | 🟢 Alto — analytics e IA en semanas |
| **Complejidad técnica** | 🟡 Media — requiere Semantic Data Layer |
| **Costo** | 🟢 Bajo-Medio — infraestructura analítica separada |
| **Recomendada para** | Organizaciones que necesitan demostrar ROI antes de invertir en modernización profunda |

---

### Estrategia 2: Strangler Fig Clásico

> Construir funcionalidad nueva fuera del legacy, y retirar gradualmente la funcionalidad antigua. El sistema nuevo crece alrededor del legacy como la hiedra que estrangula un árbol.

```mermaid
flowchart TD
    A["Legacy System<br/>(JSP + Java + Oracle)"] -->|Nuevo modulo| B["API + Spring Boot"]
    B --> C["Vue Frontend"]
    C -->|Validacion| D["Characterization Tests"]
    D -->|Retiro| E["Legacy module removed"]
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style C fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style E fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

| Aspecto | Evaluación |
|---------|------------|
| **Riesgo** | 🟡 Medio — requiere convivencia temporal |
| **Valor temprano** | 🟡 Medio — funcionalidad nueva es moderna, legacy sigue activo |
| **Complejidad técnica** | 🟠 Alta — dos mundos coexisten, routing complejo |
| **Costo** | 🟡 Medio — mantenimiento doble temporal |
| **Recomendada para** | Sistemas donde se puede identificar claramente la frontera entre legacy y nuevo |

---

### Estrategia 3: Domain-Driven Displacement

> Extraer el dominio de negocio del código legacy, construir un Domain Model limpio, y reimplementar sobre esa base. Enfoque en el conocimiento, no en la tecnología.

```mermaid
flowchart TD
    A["Hidden Logic<br/>Inventory"] --> B["Business Rules<br/>Extractor (IA)"]
    B --> C["Domain Model<br/>(Limpio)"]
    C --> D["Repository<br/>Interface"]
    D --> E["Oracle<br/>Adapter"]
    D --> F["PostgreSQL<br/>Adapter"]
    style A fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style B fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style C fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style D fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style F fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

| Aspecto | Evaluación |
|---------|------------|
| **Riesgo** | 🟡 Medio — el Domain Model puede no capturar todo |
| **Valor temprano** | 🟡 Medio — requiere extracción completa de reglas primero |
| **Complejidad técnica** | 🟠 Alta — DDD es conceptualmente simple pero difícil de implementar bien |
| **Costo** | 🟠 Alto — inversión inicial significativa en modelado |
| **Recomendada para** | Sistemas donde el dominio de negocio es complejo y el conocimiento está bien distribuido |

---

### Estrategia 4: API-First + Backend-for-Frontend

> Definir contratos API primero, construir el backend nuevo que satisfaga esos contratos, y reemplazar el frontend consumiendo las APIs. El legacy puede seguir sirviendo como backend mientras el nuevo backend crece.

```mermaid
flowchart TD
    A["OpenAPI Spec<br/>(Contrato)"] --> B["Backend<br/>Spring Boot"]
    A --> C["Frontend<br/>Vue"]
    B --> D["Legacy<br/>API Adapter"]
    D --> E["Oracle<br/>(sin tocar)"]
    style A fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style C fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style E fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
```

| Aspecto | Evaluación |
|---------|------------|
| **Riesgo** | 🟢 Bajo — contratos claros, separación por diseño |
| **Valor temprano** | 🟢 Alto — API usable desde el primer día |
| **Complejidad técnica** | 🟡 Media — definir buenos contratos requiere experiencia |
| **Costo** | 🟡 Medio — diseño de API + implementación backend |
| **Recomendada para** | Equipos que quieren habilitar integración con terceros / apps móviles rápidamente |

---

### Estrategia 5: Strangling por Capas

> Separar las capas de la arquitectura una por una: primero extraer lógica de negocio de JSP, luego separar persistencia, luego reemplazar frontend, finalmente migrar BD.

```mermaid
flowchart TD
    A["Paso 1: Extraer logica<br/>de JSP - Java classes"] --> B["Paso 2: Separar<br/>Persistencia - DAO/Repo"]
    B --> C["Paso 3: Construir<br/>API REST"]
    C --> D["Paso 4: Reemplazar<br/>Frontend JSP - Vue"]
    D --> E["Paso 5: Migrar<br/>Oracle - PostgreSQL"]
    style A fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style B fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style C fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style D fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style E fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
```

| Aspecto | Evaluación |
|---------|------------|
| **Riesgo** | 🟡 Medio — cada paso es validable pero el acumulado puede ser alto |
| **Valor temprano** | 🟡 Medio — mejoras incrementales, no rupturas |
| **Complejidad técnica** | 🟡 Media — requiere entender bien las capas actuales |
| **Costo** | 🟡 Medio — esfuerzo distribuido |
| **Recomendada para** | Equipos pequeños que prefieren avance incremental sin grandes inversiones |

---

### Matriz de Comparación

| Criterio | Intelligence-First | Strangler Fig | DDD | API-First | Capas |
|----------|-------------------|---------------|-----|-----------|-------|
| Riesgo | 🟢 Bajo | 🟡 Medio | 🟡 Medio | 🟢 Bajo | 🟡 Medio |
| Valor temprano | 🟢 Alto | 🟡 Medio | 🟡 Medio | 🟢 Alto | 🟡 Medio |
| Complejidad | 🟡 Media | 🟠 Alta | 🟠 Alta | 🟡 Media | 🟡 Media |
| Costo | 🟢 Bajo-Medio | 🟡 Medio | 🟠 Alto | 🟡 Medio | 🟡 Medio |
| IA como acelerador | 🟢 Muy alto | 🟡 Medio | 🟡 Medio | 🟢 Alto | 🟡 Medio |
| Conviene con poco equipo | 🟢 Sí | 🟡 Parcial | 🟡 Parcial | 🟢 Sí | 🟡 Parcial |

---

## Tormenta de Ideas: 10 Estrategias Alternativas

### Idea 1: Data Mesh Ligero sobre el sistema existente

> En lugar de construir un Data Warehouse centralizado, crear **Data Products** autónomos por dominio: Pacientes, Agenda, Cobros, Laboratorio, Presupuesto. Cada Data Product es una vista materializada o una API que expone datos limpios de un subconjunto de tablas Oracle. Los Data Products se consumen desde dashboards, RAG y agentes de IA.

**¿Por qué?** Reduce la complejidad de construir un Semantic Layer monolítico. Permite empezar por el dominio más valioso (ej: Cobros) y expandir gradualmente.

---

### Idea 2: Feature Flags + strangling incremental

> No reemplazar módulos completos, sino **envolver funcionalidad existente** con Feature Flags. Ej: un botón "nueva versión" en agenda que muestre Vue+API cuando el flag está activo, y el JSP original cuando no. Medir uso, errores y satisfacción antes de decidir el retiro.

**¿Por qué?** Minimiza el riesgo de "big bang" a nivel de módulo. Permite A/B testing real con usuarios.

---

### Idea 3: AI-Augmented Refactoring (refactoring con IA en loop)

> En lugar de hacer assessment → plan → ejecución, usar un ciclo continuo: **IA lee código → sugiere refactor → humano valida → IA ejecuta → tests verifican → humano aprueba**. El dossier RICH alimenta el contexto del LLM, que puede generar código refactorizado con comprensión del dominio.

**¿Por qué?** Los RICH files ya tienen el código fuente. La IA puede operar directamente sobre ellos para generar versiones refactorizadas (ej: convertir Statement a PreparedStatement, extraer SQL a Repository, etc.)

---

### Idea 4: Modular Monolith antes que Microservicios

> No separar en microservicios (premature optimization para este tamaño de aplicación). En cambio, **modularizar el monolito**: crear módulos internos (Pacientes, Agenda, Cobros, Laboratorio, Presupuesto) con boundaries claros y APIs internas. Cuando un módulo necesite escalar independientemente, ahí sí se extrae como servicio.

**¿Por qué?** El sistema actual tiene 268 clases Java. Microservicios serían over-engineering. Modularización es el sweet spot.

---

### Idea 5: Strangler por usuario, no por funcionalidad

> En lugar de estrangular por módulo funcional, hacerlo **por tipo de usuario**: primero migrar la vista de Recepción (login, agenda, citas), luego la de Doctor (odontograma, prescripciones), luego la de Administración (cobros, reportes). Cada tipo de usuario tiene un flujo acotado.

**¿Por qué?** Reduce el scope de cada iteración. Un tipo de usuario es más acotado que un módulo completo.

---

### Idea 6: Documentation-Driven Development (DDD inverso)

> Usar los 239 helpers como **contratos vivos**: cada helper define exactamente qué SQL ejecuta, qué tablas toca, qué retorna. Refactorizar convirtiendo cada helper en un Repository method con contrato tipado. La documentación EXISTE; solo necesita ser transformada en código.

**¿Por qué?** Los helpers ya son la API no documentada del sistema. Formalizarlos como Repository methods es bajo riesgo y alto valor.

---

### Idea 7: Shadow Mode — Backend nuevo opera en paralelo

> Construir el nuevo backend Spring Boot que lee de Oracle simultáneamente al legacy. Ejecutar ambos en paralelo, comparar outputs. Cuando los outputs coincidan al 100%, switch de tráfico. Esto es characterization testing continuo, no puntual.

**¿Por qué?** La validación más segura: si ambos sistemas producen el mismo resultado para las mismas entradas, el reemplazo es seguro.

---

### Idea 8: AI Knowledge Agent como primer deliverable

> Construir un agente de IA (RAG sobre el dossier) que responda preguntas sobre el sistema: "¿Qué hace agenda.jsp?", "¿Qué tablas toca ContableService?", "¿Cuál es el flujo de cobro?". Este agente se convierte en la herramienta de onboarding para cualquier desarrollador nuevo y en el basis para las decisiones de refactor.

**¿Por qué?** El dossier ya tiene 689 archivos RICH con código. Un RAG sobre esto es construible en días y tiene valor inmediato para el equipo.

---

### Idea 9: Progressive Service Exposure via MCP Server

> En lugar de construir REST APIs tradicionales, exponer los helpers como **tools en un MCP Server**. Cada helper documentado se convierte en una tool que LLMs pueden consumir directamente. Ej: `Agenda.getCitas` → tool `getCitas(fecha, odontologo_id)`. 239 helpers = 239 tools MCP.

**¿Por qué?** Los MCP servers son servidores HTTP que exponen herramientas mediante JSON-RPC 2.0. Son consumidos nativamente por LLMs, pero también por cualquier aplicación tradicional via HTTP. Un solo código, múltiples consumidores.

---

### Idea 10: Contract-First con MCP Schema + code generation

> Definir el schema MCP de las tools primero (basado en los 239 helpers y los 689 RICH files), luego usar code generation para crear el MCP Server. El schema es la fuente de verdad, no el código.

**¿Por qué?** El schema MCP define automáticamente parámetros, tipos y retorno. La generación de código reduce errores manuales y garantiza consistencia.

---

## Matriz de Decisión: Impacto vs Esfuerzo

```mermaid
quadrantChart
    title Impacto vs Esfuerzo de Estrategias
    x-axis "Bajo Esfuerzo" --> "Alto Esfuerzo"
    y-axis "Bajo Impacto" --> "Alto Impacto"
    quadrant-1 "Hacer primero"
    quadrant-2 "Planificar"
    quadrant-3 "Considerar"
    quadrant-4 "Evaluar cuidadosamente"
    "Intelligence-First": [0.25, 0.85]
    "AI Knowledge Agent": [0.15, 0.70]
    "Progressive MCP": [0.30, 0.65]
    "Documentation-Driven": [0.35, 0.60]
    "Strangler Fig": [0.60, 0.75]
    "API-First": [0.50, 0.70]
    "Feature Flags": [0.45, 0.55]
    "Modular Monolith": [0.55, 0.65]
    "DDD Displacement": [0.75, 0.80]
    "Shadow Mode": [0.70, 0.85]
```

| Posición | Estrategia | Acción sugerida |
|----------|-----------|----------------|
| **Quadrant 1 (Hacer primero)** | Intelligence-First, AI Knowledge Agent, Progressive MCP | Ejecutar inmediatamente, bajo riesgo, alto valor |
| **Quadrant 2 (Planificar)** | Strangler Fig, API-First, Shadow Mode | Planificar después del piloto, requieren más preparación |
| **Quadrant 3 (Considerar)** | Documentation-Driven, Feature Flags, Modular Monolith | Buenas ideas pero menor prioridad relativa |
| **Quadrant 4 (Evaluar cuidadosamente)** | DDD Displacement | Alto potencial pero alto esfuerzo, requiere equipo experto |

---

## Recomendación Personalizada

Basándome en el assessment completo, la estrategia DREAMS, y las alternativas exploradas, esta es mi recomendación para tu situación específica:

### Secuencia recomendada (híbrida optimizada)

```mermaid
flowchart TD
    A["Fase A': Source-Based Validation<br/>(RICH files - OpenCode)"] --> B["Fase B: AI Knowledge Agent<br/>(RAG sobre dossier)"]
    B --> C["Fase C: Progressive Service Exposure<br/>(239 helpers - MCP Server)"]
    C --> D["Fase D: Intelligence Layer<br/>(Semantic Data Layer - BI/IA)"]
    D --> E["Fase E: Strangler Fig<br/>(modulo piloto - Spring Boot + Vue)"]
    E --> F["Fase F: Modular Monolith<br/>(boundary interno entre modulos)"]
    F --> G["Fase G: Oracle - PostgreSQL<br/>(validado por el piloto)"]
    style A fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#1e1e1e
    style B fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
    style C fill:#a5b4fc,stroke:#4f46e5,stroke-width:2px,color:#1e1e1e
    style D fill:#fde68a,stroke:#d97706,stroke-width:2px,color:#1e1e1e
    style E fill:#fca5a5,stroke:#dc2626,stroke-width:2px,color:#1e1e1e
    style F fill:#c4b5fd,stroke:#7c3aed,stroke-width:2px,color:#1e1e1e
    style G fill:#86efac,stroke:#16a34a,stroke-width:2px,color:#1e1e1e
```

### ¿Por qué esta secuencia?

1. **Fase A'** (1-2 semanas): Los RICH files ya tienen código fuente. OpenCode puede validar el assessment directamente sobre el código, encontrar gaps, y generar un inventory completo. Bajo esfuerzo, alto valor.

2. **Fase B** (2-4 semanas): Un RAG sobre los 689 archivos RICH es construible rápido y tiene valor inmediato. El equipo puede hacer preguntas al sistema y obtener respuestas del dominio.

3. **Fase C** (4-6 semanas): Los 239 helpers documentados ya definen las herramientas del MCP Server. Cada helper = una tool MCP. La IA puede generar el 80% del código. Los MCP servers son servidores HTTP que sirven tanto para LLMs como para aplicaciones tradicionales.

4. **Fase D** (6-8 semanas): Con las tools MCP expuestas, construir el Semantic Layer para analytics. Valor de negocio demostrable.

5. **Fase E** (12-24 semanas): Con MCP Server funcionando y IA validando, estrangular un módulo completo con characterization testing.

6. **Fase F** (8-12 semanas): Modularizar el monolito restante con boundaries internos.

7. **Fase G** (cuando esté validado): Migrar Oracle → PostgreSQL con el dominio bien entendido.

### Lo que NO haría

- ❌ **No haría Big Bang** — demasiado riesgo para un sistema de producción
- ❌ **No migraría Oracle primero** — necesitas un punto de comparación estable
- ❌ **No empezaría por DDD Displacement** — requiere más experiencia de equipo de la que típicamente se tiene al inicio
- ❌ **No construiría microservicios** — 268 clases no justifican microservicios

### Lo que SÍ haría (próximos 30 días)

1. **Semana 1-2:** Entregar los RICH files a OpenCode para validación del assessment
2. **Semana 2-3:** Construir un prototipo RAG básico sobre el dossier
3. **Semana 3-4:** Implementar 5-10 helpers críticos como tools en el MCP Server como prueba de concepto
4. **Semana 4:** Presentar resultados al CEO con datos concretos

---

## Comparación: REST API vs MCP Server

### ¿Por qué MCP Server en lugar de REST API?

| Aspecto | REST API tradicional | MCP Server |
|---------|---------------------|------------|
| **Definición de herramientas** | Manual (OpenAPI/Swagger) | Automática (schema del tool) |
| **Integración con LLMs** | Requiere function calling custom | Nativo (tools se auto-descubren) |
| **Validación de parámetros** | Manual en cada endpoint | Automática por el protocolo |
| **Descubrimiento** | El LLM necesita el spec completo | El LLM obtiene las tools disponibles |
| **Complejidad de implementación** | Más código boilerplate | Más directo para el caso AI |
| **Consumo por apps tradicionales** | HTTP nativo | HTTP nativo (JSON-RPC 2.0) |
| **Múltiples consumidores** | Requiere CORS, versionado | Un solo endpoint, múltiples clientes |

### Arquitectura MCP Server

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Server                              │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Tools (239 helpers → 239 tools)                        │ │
│  │  ├── getCitas(fecha, odontologo_id) → Lista<Cita>       │ │
│  │  ├── getDatosPaciente(ficha_o_rut) → Paciente           │ │
│  │  ├── getStockProducto(producto_id) → Stock              │ │
│  │  ├── getHistorialPaciente(paciente_id) → Historial      │ │
│  │  └── ... (235 tools más)                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Resources (lectura de datos estáticos)                 │ │
│  │  ├── /pacientes/{id}                                     │ │
│  │  ├── /agenda/{fecha}                                     │ │
│  │  └── ...                                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Service Layer (lógica de negocio)                      │ │
│  │  └── Helpers existentes (239 métodos Java)              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  Puerto: 3000 (HTTP)                                        │
│  Protocolo: JSON-RPC 2.0 sobre HTTP                         │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
         │ AI Agent│  │ App Web│  │ Móvil  │
         │ (MCP)   │  │ (HTTP) │  │ (HTTP) │
         └─────────┘  └────────┘  └────────┘
```

---

## Ejemplo Real: DatosPaciente.getDatosPaciente

### Contexto del helper original

El helper `DatosPaciente.getDatosPaciente` obtiene datos completos de un paciente por ficha o RUT. Consulta 3 tablas (FICHAS, PACIENTES, TELEFONOS) y usa funciones Oracle (`get_edad`, `get_comuna_pcte`).

**SQL original:**
```sql
SELECT NUM_FICHA FROM FICHAS WHERE COD_PERSONA = '<rut>'
SELECT PAC_NOMBRES, PAC_SOCIAL, PAC_APELLIDO_PATERNO, PAC_APELLIDO_MATERNO,
       get_edad(PAC_FEC_NACIMIENTO) EDAD, PAC_EMAIL, get_comuna_pcte(<ficha>) COMUNA
FROM PACIENTES WHERE PAC_CODIGO = '<ficha>'
SELECT COD_AREA||NUM_TELEFONO FROM TELEFONOS
WHERE COD_PERSONA='<ficha>' AND IND_ESTADO='VIG' AND IND_PRIORIDAD='S'
```

---

### db.py — Pool de conexiones compartido

Ambos enfoques (REST API y MCP Server) comparten la misma capa de persistencia. El pool se crea una vez y se reutiliza en todas las peticiones:

```python
# db.py — Pool de conexiones Oracle (compartido por API y MCP)
import oracledb
from contextlib import contextmanager

# Pool global — se crea UNA vez al iniciar el servidor
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user="dent",
            password="***",
            dsn="localhost:1521/XE",
            min=2,          # conexiones mínimas en el pool
            max=10,         # conexiones máximas simultáneas
            increment=1     # incremento cuando se necesitan más
        )
    return _pool

@contextmanager
def get_connection():
    """Obtiene una conexión del pool y la devuelve automáticamente."""
    pool = get_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)
```

> **Nota:** El pool maneja la reapertura automática de conexiones caídas y limita el número de conexiones simultáneas a Oracle. Tanto la API como el MCP Server usan el mismo pool.

---

### Versión REST API (alternativa tradicional)

```python
# app.py — REST API tradicional con FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection

app = FastAPI(title="DentWeb12 API")

class PacienteResponse(BaseModel):
    num_ficha: str
    nombres: str
    nombre_social: str | None
    apellido_paterno: str
    apellido_materno: str
    edad: int
    email: str
    comuna: str
    telefono: str

@app.get("/api/pacientes/{ficha_o_rut}", response_model=PacienteResponse)
async def get_paciente(ficha_o_rut: str):
    """Obtiene datos del paciente por ficha o RUT."""

    with get_connection() as connection:
        cursor = connection.cursor()

        try:
            # Determinar si es RUT o ficha
            if '-' in ficha_o_rut:
                cursor.execute("SELECT NUM_FICHA FROM FICHAS WHERE COD_PERSONA = :1", [ficha_o_rut])
            else:
                cursor.execute("SELECT COD_PERSONA FROM FICHAS WHERE NUM_FICHA = :1", [ficha_o_rut])

            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Paciente no encontrado")

            ficha = row[0]

            # Datos del paciente
            cursor.execute("""
                SELECT PAC_NOMBRES, PAC_SOCIAL, PAC_APELLIDO_PATERNO, PAC_APELLIDO_MATERNO,
                       get_edad(PAC_FEC_NACIMIENTO), PAC_EMAIL, get_comuna_pcte(:1)
                FROM PACIENTES WHERE PAC_CODIGO = :1
            """, [ficha, ficha])

            datos = cursor.fetchone()
            if not datos:
                raise HTTPException(status_code=404, detail="Datos del paciente no encontrados")

            # Teléfono
            cursor.execute("""
                SELECT COD_AREA||NUM_TELEFONO FROM TELEFONOS
                WHERE COD_PERSONA=:1 AND IND_ESTADO='VIG' AND IND_PRIORIDAD='S'
            """, [ficha])

            tel_row = cursor.fetchone()
            telefono = tel_row[0] if tel_row else ""

            return PacienteResponse(
                num_ficha=ficha,
                nombres=datos[0],
                nombre_social=datos[1],
                apellido_paterno=datos[2],
                apellido_materno=datos[3],
                edad=datos[4],
                email=datos[5],
                comuna=datos[6],
                telefono=telefono
            )

        finally:
            cursor.close()
```

**Consumo:**
```bash
curl http://localhost:8000/api/pacientes/12345
```

---

### Versión REST API con ORM (SQLAlchemy)

Mismo ejemplo pero usando SQLAlchemy como ORM, que mapea tablas a clases Python:

```python
# models.py — Modelos ORM (SQLAlchemy)
from sqlalchemy import Column, String, Integer, Date, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Ficha(Base):
    __tablename__ = "FICHAS"
    num_ficha = Column("NUM_FICHA", String, primary_key=True)
    cod_persona = Column("COD_PERSONA", String)

class Paciente(Base):
    __tablename__ = "PACIENTES"
    pac_codigo = Column("PAC_CODIGO", String, primary_key=True)
    pac_nombres = Column("PAC_NOMBRES", String)
    pac_social = Column("PAC_SOCIAL", String)
    pac_apellido_paterno = Column("PAC_APELLIDO_PATERNO", String)
    pac_apellido_materno = Column("PAC_APELLIDO_MATERNO", String)
    pac_fec_nacimiento = Column("PAC_FEC_NACIMIENTO", Date)
    pac_email = Column("PAC_EMAIL", String)

class Telefono(Base):
    __tablename__ = "TELEFONOS"
    cod_persona = Column("COD_PERSONA", String, primary_key=True)
    cod_area = Column("COD_AREA", String)
    num_telefono = Column("NUM_TELEFONO", String)
    ind_estado = Column("IND_ESTADO", String)
    ind_prioridad = Column("IND_PRIORIDAD", String)
```

```python
# app_orm.py — REST API con FastAPI + SQLAlchemy ORM
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, Ficha, Paciente, Telefono

app = FastAPI(title="DentWeb12 API (ORM)")

# Pool de conexiones via SQLAlchemy
engine = create_engine(
    "oracle+oracledb://dent:***@localhost:1521/XE",
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(bind=engine)

class PacienteResponse(BaseModel):
    num_ficha: str
    nombres: str
    nombre_social: str | None
    apellido_paterno: str
    apellido_materno: str
    edad: int
    email: str
    comuna: str
    telefono: str

@app.get("/api/pacientes/{ficha_o_rut}", response_model=PacienteResponse)
async def get_paciente(ficha_o_rut: str):
    """Obtiene datos del paciente por ficha o RUT."""

    db = SessionLocal()
    try:
        # Determinar si es RUT o ficha
        if '-' in ficha_o_rut:
            ficha_obj = db.query(Ficha).filter(Ficha.cod_persona == ficha_o_rut).first()
        else:
            ficha_obj = db.query(Ficha).filter(Ficha.num_ficha == ficha_o_rut).first()

        if not ficha_obj:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        ficha = ficha_obj.num_ficha

        # Datos del paciente
        paciente = db.query(Paciente).filter(Paciente.pac_codigo == ficha).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Datos del paciente no encontrados")

        # Edad (función Oracle via SQLAlchemy)
        edad = db.query(func.get_edad(paciente.pac_fec_nacimiento)).scalar() or 0

        # Comuna (función Oracle via SQLAlchemy)
        comuna = db.query(func.get_comuna_pcte(ficha)).scalar() or ""

        # Teléfono
        tel = db.query(Telefono).filter(
            Telefono.cod_persona == ficha,
            Telefono.ind_estado == 'VIG',
            Telefono.ind_prioridad == 'S'
        ).first()
        telefono = (tel.cod_area + tel.num_telefono) if tel else ""

        return PacienteResponse(
            num_ficha=ficha,
            nombres=paciente.pac_nombres,
            nombre_social=paciente.pac_social,
            apellido_paterno=paciente.pac_apellido_paterno,
            apellido_materno=paciente.pac_apellido_materno,
            edad=edad,
            email=paciente.pac_email or "",
            comuna=comuna,
            telefono=telefono
        )

    finally:
        db.close()
```

**Ventajas del ORM:**
- Mapeo tablas → clases Python (autocompletado, tipado)
- No SQL crudo en el código de negocio
- Cambiar de Oracle a PostgreSQL = cambiar la URL de conexión
- Relaciones declarativas (cuando existan FK)

**Desventajas:**
- Curva de aprendizaje mayor
- Overhead para queries simples
- Funciones Oracle específicas requieren `func.`

---

### Versión MCP Server (dirección recomendada)

```python
# mcp_server.py — MCP Server con FastMCP
from fastmcp import FastMCP
from pydantic import BaseModel
from db import get_connection

mcp = FastMCP(
    name="dentweb12-mcp",
    version="1.0.0"
)

class PacienteResult(BaseModel):
    ficha: str
    nombres: str
    nombre_social: str | None
    apellido_paterno: str
    apellido_materno: str
    edad: int
    email: str
    comuna: str
    telefono: str

@mcp.tool()
def get_datos_paciente(ficha_o_rut: str) -> PacienteResult:
    """
    Obtiene datos completos de un paciente por ficha o RUT.

    Args:
        ficha_o_rut: Número de ficha (ej: "12345") o RUT con guión (ej: "12345678-9")

    Returns:
        PacienteResult con nombres, edad, comuna, email y teléfono vigente.
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        try:
            # Determinar si es RUT o ficha
            if '-' in ficha_o_rut:
                cursor.execute("SELECT NUM_FICHA FROM FICHAS WHERE COD_PERSONA = :1", [ficha_o_rut])
            else:
                cursor.execute("SELECT COD_PERSONA FROM FICHAS WHERE NUM_FICHA = :1", [ficha_o_rut])

            row = cursor.fetchone()
            if not row:
                return PacienteResult(
                    ficha="ERROR",
                    nombres="Paciente no encontrado",
                    nombre_social=None,
                    apellido_paterno="",
                    apellido_materno="",
                    edad=0,
                    email="",
                    comuna="",
                    telefono=""
                )

            ficha = row[0]

            # Datos del paciente
            cursor.execute("""
                SELECT PAC_NOMBRES, PAC_SOCIAL, PAC_APELLIDO_PATERNO, PAC_APELLIDO_MATERNO,
                       get_edad(PAC_FEC_NACIMIENTO), PAC_EMAIL, get_comuna_pcte(:1)
                FROM PACIENTES WHERE PAC_CODIGO = :1
            """, [ficha, ficha])

            datos = cursor.fetchone()
            if not datos:
                return PacienteResult(
                    ficha=ficha,
                    nombres="Sin datos",
                    nombre_social=None,
                    apellido_paterno="",
                    apellido_materno="",
                    edad=0,
                    email="",
                    comuna="",
                    telefono=""
                )

            # Teléfono
            cursor.execute("""
                SELECT COD_AREA||NUM_TELEFONO FROM TELEFONOS
                WHERE COD_PERSONA=:1 AND IND_ESTADO='VIG' AND IND_PRIORIDAD='S'
            """, [ficha])

            tel_row = cursor.fetchone()
            telefono = tel_row[0] if tel_row else ""

            return PacienteResult(
                ficha=ficha,
                nombres=datos[0],
                nombre_social=datos[1],
                apellido_paterno=datos[2],
                apellido_materno=datos[3],
                edad=datos[4],
                email=datos[5],
                comuna=datos[6],
                telefono=telefono
            )

        finally:
            cursor.close()

@mcp.tool()
def get_edad_paciente(ficha: str) -> int:
    """
    Obtiene la edad actual de un paciente.

    Args:
        ficha: Número de ficha del paciente

    Returns:
        Edad en años
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT get_edad(PAC_FEC_NACIMIENTO) FROM PACIENTES WHERE PAC_CODIGO = :1", [ficha])
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            cursor.close()

@mcp.tool()
def get_historial_citas(ficha: str, meses: int = 6) -> list[dict]:
    """
    Obtiene las citas recientes de un paciente.

    Args:
        ficha: Número de ficha del paciente
        meses: Cuántos meses hacia atrás buscar (default: 6)

    Returns:
        Lista de citas con fecha, tipo y estado
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT fec_cita, tip_cita, ind_estado
                FROM agenda
                WHERE cod_paciente = :1
                AND fec_cita >= ADD_MONTHS(SYSDATE, - :2)
                ORDER BY fec_cita DESC
            """, [ficha, meses])

            citas = []
            for row in cursor.fetchall():
                citas.append({
                    "fecha": str(row[0]),
                    "tipo": row[1],
                    "estado": row[2]
                })
            return citas
        finally:
            cursor.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")  # Para LLMs
    # mcp.run(transport="http", port=3000)  # Para apps tradicionales
```

**Consumo por LLM (nativo MCP):**
```python
# El LLM descubre automáticamente las tools disponibles
# y las llama cuando el usuario hace preguntas como:
# "¿Cuántos años tiene el paciente 12345?"
# → El LLM llama a get_datos_paciente("12345") y responde: "El paciente tiene 34 años"
```

**Consumo por app tradicional (HTTP):**
```bash
# Cualquier app puede consumir el MCP Server via HTTP
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_datos_paciente",
      "arguments": {"ficha_o_rut": "12345"}
    },
    "id": 1
  }'
```

---

### Comparación CURL: API vs MCP

Misma operación (obtener paciente 12345) ejecutada de forma diferente:

| CURL API REST | CURL MCP Server |
|---------------|-----------------|
| `curl http://localhost:8000/api/pacientes/12345` | `curl -X POST http://localhost:3000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_datos_paciente","arguments":{"ficha_o_rut":"12345"}},"id":1}'` |
| **Transporte:** HTTP GET | **Transporte:** HTTP POST (JSON-RPC 2.0) |
| **Resultado:** `{"num_ficha":"12345","nombres":"Juan",...}` | **Resultado:** `{"jsonrpc":"2.0","result":{"content":[{"type":"text","text":"{\"ficha\":\"12345\",\"nombres\":\"Juan\",...}"}]},"id":1}` |

> **Nota:** El CURL es idéntico tanto para la versión con SQL directo como con ORM. La diferencia está solo en el código del servidor.

---

### Comparación de los dos enfoques

| Aspecto | REST API | MCP Server |
|---------|----------|------------|
| **Código** | ~80 líneas | ~120 líneas |
| **Endpoints** | 1 endpoint por operación | Tools auto-registradas |
| **Documentación** | Swagger manual | Auto-generada del docstring |
| **Validación** | Pydantic manual | Automática por el schema |
| **Consumo LLM** | Requiere adaptador | Nativo |
| **Consumo tradicional** | HTTP nativo | HTTP nativo (JSON-RPC) |
| **Escalabilidad** | Fácil de entender | Más potente, menos código |
| **Futuro** | Estándar establecido | Estándar emergente para AI |

### Conclusión

**El MCP Server es la dirección correcta porque:**
1. Los LLMs lo consumen nativamente sin adaptadores
2. Las apps tradicionales lo consumen via HTTP (JSON-RPC 2.0)
3. Un solo código sirve para múltiples consumidores
4. La documentación de las tools se auto-genera del docstring
5. Está alineado con la estrategia "Intelligence First"

---

> **Frase final:** «El dossier que construiste no es documentación: es el activo más valioso para la modernización. Úsalo como base para la IA, como schema para el MCP Server, y como conocimiento para el Domain Model. No lo dejes dormir.»
