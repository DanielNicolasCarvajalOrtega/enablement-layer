# DREAMS Explorer — Revisión estratégica y apertura de alternativas

> **Documento revisado:** `dreams_explorer.md`  
> **Sistema:** DentWeb12  
> **Fecha de revisión:** 2026-09-21  
> **Propósito:** evaluar la madurez de la estrategia de transformación, identificar brechas entre lo documentado y una estrategia ejecutable, y abrir alternativas de inicio considerando una posible evolución hacia **Django + ORM + MCP/JSON-RPC**, manteniendo Oracle inicialmente si resulta conveniente.

---

# 1. Resumen ejecutivo

Después de leer el documento completo, mi impresión es bastante clara:

> **Vas por buen camino y, más importante todavía, ya dejaste atrás la etapa de “¿cómo modernizamos esta aplicación?” y estás entrando en la etapa correcta: “¿cómo transformamos el sistema sin destruir el conocimiento que contiene?”**

El documento ya no es simplemente un assessment técnico. Está evolucionando hacia una **estrategia de transformación**.

La diferencia es importante.

Al principio el problema aparecía como:

```text
Java/JSP/Payara + Oracle
        ↓
“Hay que modernizar”
```

Después aparece:

```text
Legacy tecnológico
+ modelo de datos implícito
+ reglas de negocio distribuidas
+ dificultad para integrar
        ↓
Modernización progresiva
```

Y finalmente aparece algo mucho más potente:

```text
                    NEGOCIO
                       │
          ┌────────────┴────────────┐
          │                         │
      OPERACIÓN                INTELIGENCIA
          │                         │
    DentWeb12 actual          Analytics / IA
          │                         │
          └──────────┬──────────────┘
                     │
                   DATOS
                     │
        ┌────────────┴────────────┐
        │                         │
    Oracle actual          Capa semántica
        │                         │
        └────────────┬────────────┘
                     │
              nueva arquitectura
```

Ese último modelo es, en mi opinión, mucho más cercano a la realidad estratégica del proyecto.

## Mi diagnóstico en una frase

**El documento está suficientemente maduro para comenzar un proyecto de transformación, pero todavía no está suficientemente maduro para comprometer una arquitectura final, una migración de BD o una reescritura masiva.**

Y eso no es una debilidad.

Es exactamente donde debería estar un proyecto de esta naturaleza antes de comenzar.

La principal brecha que veo no es “faltan más tecnologías”. La brecha es:

> **convertir el conocimiento recuperado en una arquitectura de transición ejecutable, con contratos, boundaries, pruebas de caracterización, observabilidad, criterios de corte y una estrategia explícita de datos.**

---

# 2. Lo primero que cambiaría en mi forma de mirar el problema

Hay una idea del documento que considero especialmente importante:

> “El legacy no es el enemigo.”

El documento reconoce que DentWeb12 es estable, que soporta los flujos de la clínica y que el verdadero problema no es simplemente que Java/JSP/Oracle sean antiguos.

Eso cambia completamente el punto de partida.

La pregunta ya no debería ser:

> ¿Por dónde empiezo: BD, aplicación o datos?

Yo la reformularía así:

> **¿Cuál es la primera capacidad que puedo aislar del sistema actual para comenzar a crear una nueva arquitectura sin necesitar transformar todo el sistema?**

Ese cambio de pregunta es enorme.

Porque “BD vs aplicación vs datos” obliga a elegir un componente.

En cambio:

> **capacidad → boundary → contrato → implementación → evidencia**

obliga a elegir una **unidad de transformación**.

Y esa unidad puede ser:

- una capacidad de negocio;
- un workflow;
- una consulta crítica;
- una tool MCP;
- un caso de uso;
- un módulo;
- una vista semántica;
- un servicio de aplicación;
- una funcionalidad completa de usuario.

Eso abre muchas más posibilidades.

---

# 3. Lo que considero que ya tienes resuelto

El documento tiene varios elementos que normalmente aparecen mucho más tarde en un proyecto de modernización.

## 3.1 Ya tienes una radiografía importante

Documentas:

- aplicación;
- Java;
- JSP;
- helpers;
- SQL;
- Oracle;
- relaciones implícitas;
- PL/SQL;
- configuración;
- reportes;
- dependencias;
- reglas;
- riesgos;
- flujos;
- código fuente incrustado en los RICH.

El documento indica que existen **689 archivos RICH con código fuente completo**, 239 helpers, 94 tablas y documentación extensa de Java/JSP.

Eso es un activo extraordinariamente importante.

No estás empezando desde cero.

---

## 3.2 Descubriste que las relaciones de BD no son el problema completo

El documento identifica correctamente que las relaciones funcionales existen aunque no estén formalizadas como FK.

Eso lleva a una conclusión más interesante:

> **El modelo físico de Oracle no necesariamente representa el modelo conceptual del negocio.**

Esto es fundamental.

Por ejemplo:

```text
Oracle físico

PACIENTES
   PAC_CODIGO
   ...

FICHAS
   NUM_FICHA
   COD_PERSONA
   ...

TELEFONOS
   COD_PERSONA
   ...
```

puede esconder conceptualmente:

```text
Paciente
   │
   ├── Ficha
   │
   └── Teléfonos
```

La ausencia de FK no significa ausencia de relación.

Significa que la relación está siendo expresada en otro lugar:

- SQL;
- Java;
- JSP;
- convenciones;
- código;
- datos;
- comportamiento.

Y eso justamente es lo que tu assessment está recuperando.

---

# 4. La gran decisión que todavía NO debes cerrar

Aquí veo la mayor tentación del proyecto:

> “Probablemente voy a partir con Django.”

Puede ser una excelente decisión.

Pero yo evitaría convertir esa intuición inmediatamente en:

```text
Django
    ↓
ORM
    ↓
PostgreSQL
```

Porque entonces habrías decidido tres cosas simultáneamente:

1. framework;
2. modelo de persistencia;
3. motor de BD.

Y todavía no necesitas decidir las tres.

Yo separaría esas decisiones.

## Decisión A

**¿Cuál será el lenguaje/framework del nuevo núcleo?**

Probablemente:

```text
Python + Django
```

o una combinación:

```text
Django
+
servicios específicos / ASGI
```

## Decisión B

**¿Cuál será el modelo de dominio?**

Esto todavía debe descubrirse.

## Decisión C

**¿Cuál será el modelo de persistencia?**

Puede inicialmente ser:

```text
Oracle
```

y posteriormente:

```text
PostgreSQL
```

## Decisión D

**¿Cuál será la interfaz de integración?**

Aquí sí puedes experimentar temprano con:

```text
MCP
JSON-RPC
Tools
Resources
```

sin haber decidido todavía PostgreSQL.

---

# 5. Mi propuesta conceptual: desacoplar cinco decisiones

Yo introduciría explícitamente en tu documento una matriz como esta:

| Decisión | Puede decidirse ahora | Puede esperar |
|---|---:|---:|
| Python | Sí, como hipótesis/piloto | Sí |
| Django | Sí, como framework candidato | Sí |
| ORM | Sí, para experimentar | Sí |
| Oracle inicialmente | Sí | — |
| PostgreSQL | No necesariamente | Sí |
| Modelo relacional definitivo | No | Sí |
| FK físicas | No | Sí |
| MCP | Sí, como canal de AI/integración | — |
| Arquitectura de dominio | Parcialmente | Sí |
| Microservicios | No | Mucho después |

Esto te permite comenzar a construir sin fingir que ya conoces la arquitectura final.

---

# 6. Una idea que cambiaría del documento: MCP no debería reemplazar el dominio

Esta es probablemente la observación más importante respecto de tu nueva dirección.

En el documento aparece una idea equivalente a:

```text
239 helpers
      ↓
239 MCP tools
```

Yo **no haría eso**.

Al menos no como arquitectura final.

Puede ser excelente como experimento de descubrimiento.

Pero conceptualmente es peligroso.

## ¿Por qué?

Porque un helper legacy no necesariamente es una capacidad de negocio.

Un helper puede ser:

```text
getPaciente()
```

pero también:

```text
getPaciente2()
```

o:

```text
getDatos()
```

o:

```text
calcularAlgo()
```

o:

```text
ejecutarQueryX()
```

Eso no constituye una API de dominio.

Si conviertes cada helper en una tool MCP, estarías haciendo:

```text
Legacy API
      ↓
MCP
```

en vez de:

```text
Legacy
   ↓
Business capability
   ↓
Application service
   ↓
MCP tool
```

La segunda arquitectura es muchísimo más sana.

---

# 7. Cómo utilizaría MCP en tu transformación

Yo mantendría tu apuesta por MCP, pero cambiaría su posición arquitectónica.

No:

```text
Frontend
   ↓
MCP
   ↓
Oracle
```

Sino:

```text
                    ┌───────────────┐
                    │   MCP Host    │
                    │   / AI Agent  │
                    └───────┬───────┘
                            │
                         MCP/JSON-RPC
                            │
                    ┌───────▼────────┐
                    │   MCP Adapter  │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Application    │
                    │ Services       │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Domain         │
                    │ / Business     │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Repository     │
                    │ / Persistence  │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Oracle         │
                    └────────────────┘
```

Así MCP se convierte en una **puerta de entrada especializada para IA**, no en el lugar donde vive el negocio.

---

# 8. Y aquí aparece una distinción crítica: API vs MCP

Tu intuición de evitar una REST API tradicional tiene sentido si tu objetivo inmediato es habilitar capacidades para agentes.

Pero yo no convertiría:

> “No quiero REST”

en:

> “MCP reemplaza conceptualmente toda API.”

Son problemas diferentes.

## REST

Es principalmente un mecanismo de exposición de recursos/capacidades HTTP para consumidores de software.

## MCP

Es un protocolo orientado a que clientes/hosts de IA descubran y utilicen capacidades, tools, resources y prompts.

MCP está construido sobre JSON-RPC, pero **MCP no es simplemente “una REST API hecha con JSON-RPC”.**

Por eso yo usaría esta distinción:

```text
Application layer
       │
       ├── MCP adapter
       │      └── AI consumers
       │
       ├── HTTP/API adapter
       │      └── Web/mobile/integrations
       │
       └── Internal application calls
```

Y podrías perfectamente decidir que durante la primera etapa:

```text
MCP = principal interfaz de experimentación
```

sin comprometerte a que:

```text
MCP = única interfaz para siempre
```

---

# 9. La idea más potente que veo para tu proyecto: “Capability First”

Creo que este concepto puede convertirse en el eje de la estrategia.

En vez de:

```text
Tabla
→ ORM
→ endpoint
→ pantalla
```

pensaría:

```text
CAPACIDAD DE NEGOCIO
        ↓
CONTRATO
        ↓
CASO DE USO
        ↓
REGLAS
        ↓
DATOS
        ↓
PERSISTENCIA
        ↓
INTERFACES
        ├── MCP
        ├── Web
        ├── Mobile
        └── Integraciones
```

Por ejemplo:

```text
Disponibilidad de agenda
```

no debería ser:

```text
SELECT ...
```

ni:

```text
helper.disponibilidad()
```

ni:

```text
GET /agenda
```

Primero debería existir conceptualmente:

```text
Capability:
    disponibilidad_dia

Input:
    fecha
    unidad opcional

Output:
    disponibilidad por unidad/estación/bloque

Business rules:
    estados válidos
    tipos válidos
    rangos de fechas
    exclusiones
```

Después decides cómo se implementa.

Esto conecta directamente con el trabajo que ya estás haciendo con `disponibilidad_dia`.

---

# 10. Tu servicio `disponibilidad_dia` es más importante de lo que parece

La dirección que has comenzado a explorar con servicios MCP parametrizados es, en realidad, una excelente semilla para la nueva arquitectura.

Porque estás haciendo:

```text
Pregunta de negocio
        ↓
Contrato
        ↓
Parámetros
        ↓
Query controlada
        ↓
Resultado estructurado
```

Eso ya es bastante distinto de:

```text
LLM
 ↓
SQL libre
 ↓
Oracle
```

Y esto es bueno.

Yo mantendría una regla:

> **Los agentes no deberían tener acceso directo e irrestricto al esquema operacional de Oracle.**

El agente debería conocer:

```text
disponibilidad_dia
historial_paciente
estado_cuenta
stock_producto
laboratorio_pendiente
agenda_profesional
```

y no:

```text
SELECT * FROM ...
```

Esto coincide con una de las mejores intuiciones de tu documento: la **Semantic Data Layer**.

---

# 11. Tu verdadera arquitectura podría ser una “Semantic Application Layer”

Hasta ahora la llamas:

> Semantic Data Layer

Yo exploraría una evolución del concepto.

Porque si solo limpias datos, estás construyendo una capa analítica.

Pero si empiezas a encapsular:

- reglas;
- capacidades;
- consultas;
- validaciones;
- agregaciones;
- operaciones;
- estados;
- permisos;
- semántica;

entonces estás construyendo algo más potente:

> **Semantic Application Layer**

Por ejemplo:

```text
                 AI / Agents
                      │
                    MCP
                      │
        ┌─────────────▼─────────────┐
        │ Semantic Application      │
        │ Layer                     │
        │                           │
        │ disponibilidad_dia        │
        │ historial_paciente       │
        │ estado_cuenta             │
        │ stock_proyectado          │
        │ laboratorio_pendiente     │
        │ compromisos_vencidos      │
        └─────────────┬─────────────┘
                      │
              Application Services
                      │
             ┌────────┴────────┐
             │                 │
          Oracle            Future PG
```

Esta capa puede convertirse posteriormente en la frontera natural de la nueva aplicación.

---

# 12. La decisión de Oracle sin FK: sí, es una estrategia viable

Aquí tu nueva hipótesis me parece técnicamente razonable.

Puedes mantener:

```text
Oracle
0 FK
```

y construir encima:

```text
Python
Django / SQLAlchemy
        ↓
Domain relationships
        ↓
Oracle
```

Eso es viable.

SQLAlchemy, de hecho, permite definir relaciones ORM mediante condiciones explícitas incluso cuando la tabla no contiene `ForeignKey` metadata; la documentación contempla `relationship()`, `foreign_keys`, `primaryjoin` y anotaciones `foreign()` para estos casos. citeturn0search1turn0search9

Eso significa que tu situación de “Oracle sin FK” **no bloquea un ORM**.

Pero hay una distinción fundamental:

> **Que el ORM pueda representar una relación no significa que Oracle tenga integridad referencial.**

Son dos cosas diferentes.

---

# 13. ORM lógico ≠ integridad física

Podrías tener:

```python
class Paciente:
    fichas = relationship(...)
```

y que la aplicación entienda:

```text
Paciente 123
    ↓
Ficha 456
```

pero Oracle seguirá permitiendo potencialmente:

```text
Ficha 456
    ↓
Paciente inexistente
```

Por eso yo establecería tres niveles:

```text
Nivel 1 — Relación descubierta
```

La relación existe según código/datos.

```text
Nivel 2 — Relación declarada en el modelo
```

El ORM conoce la relación.

```text
Nivel 3 — Integridad referencial física
```

Oracle/PostgreSQL garantiza la relación mediante FK/constraints.

No necesitas saltar inmediatamente del nivel 1 al nivel 3.

Puedes pasar:

```text
1 → 2
```

mucho antes.

Y ese puede ser uno de los mejores movimientos iniciales del proyecto.

---

# 14. Esto cambia mi opinión sobre “¿debo agregar FK ahora?”

No.

Yo **no comenzaría agregando FK al Oracle productivo**.

Haría:

```text
Oracle actual
     │
     ▼
Data profiling
     │
     ▼
Relaciones inferidas
     │
     ▼
Modelo lógico
     │
     ▼
ORM/domain relationships
     │
     ▼
Tests de integridad
     │
     ▼
FK candidata
     │
     ▼
Validación
     │
     ▼
FK física
```

Y algunas FK quizá nunca deban existir porque la relación puede ser:

- histórica;
- opcional;
- polimórfica;
- derivada;
- basada en códigos;
- temporal;
- con excepciones de negocio.

Tu documento ya apunta en esa dirección cuando advierte que agregar FK no es simplemente ejecutar `ALTER TABLE`.

Yo llevaría esa idea todavía más lejos.

---

# 15. Una posibilidad que el documento todavía no explora suficientemente: ORM “legacy-aware”

Aquí veo una línea de experimentación muy interesante.

En vez de:

```text
Oracle legacy
        ↓
ORM
        ↓
“modelo bonito”
```

puedes construir:

```text
Oracle legacy
        ↓
Legacy Persistence Model
        ↓
Domain Model
```

Es decir:

## Capa 1 — Persistence Model

Representa Oracle casi como es.

Ejemplo:

```text
Oracle PACIENTES
Oracle FICHAS
Oracle TELEFONOS
```

## Capa 2 — Domain Model

Representa:

```text
Paciente
Ficha
Contacto
```

## Capa 3 — Application Services

Representa:

```text
obtener_paciente()
buscar_historial()
obtener_disponibilidad()
```

Así no obligas al dominio a pensar como Oracle.

Esta separación puede ser muchísimo más valiosa que migrar inmediatamente a PostgreSQL.

---

# 16. Django podría encajar muy bien aquí, pero con una condición

Django tiene una ventaja importante para tu escenario:

> te permite construir rápidamente una aplicación empresarial alrededor del dominio mientras mantiene una infraestructura madura.

Pero yo evitaría convertir Django en:

```text
“el nuevo framework que reemplaza Java”
```

Ese enfoque es demasiado pequeño.

Yo lo usaría como:

```text
Python
│
├── Django
│   ├── configuración
│   ├── administración
│   ├── seguridad
│   ├── modelos
│   └── aplicación web
│
├── Application Services
│
├── Domain
│
├── Persistence
│
├── MCP
│
└── Analytics / AI
```

Es decir:

> **Django es infraestructura de la nueva plataforma, no la arquitectura completa.**

---

# 17. ¿Django ORM o SQLAlchemy?

Aquí tampoco cerraría todavía.

Hay dos caminos razonables.

## Camino A — Django ORM

```text
Django
  ↓
Django ORM
  ↓
Oracle
```

Ventajas:

- integración natural con Django;
- administración;
- convenciones;
- rapidez;
- modelos;
- migraciones;
- ecosystema.

Riesgo:

> que el ORM termine convirtiéndose en una representación demasiado directa del Oracle legacy.

---

## Camino B — Django + SQLAlchemy

```text
Django
   │
Application
   │
Domain
   │
SQLAlchemy
   │
Oracle
```

Es más complejo.

Pero te da un control explícito de persistencia que puede ser interesante si el proyecto tiene que convivir mucho tiempo con Oracle y posteriormente con PostgreSQL.

SQLAlchemy mantiene soporte para Oracle y `python-oracledb`; su documentación actual también contempla relaciones ORM con joins explícitos cuando no existen FK físicas. citeturn0search0turn0search1

---

# 18. Mi hipótesis técnica para el piloto

No decidiría ahora cuál de los dos gana.

Construiría **el mismo pequeño caso de negocio dos veces**.

Por ejemplo:

```text
Caso:
    disponibilidad_dia
```

Implementación:

```text
A) Django ORM + Oracle
B) SQLAlchemy + Oracle
```

Y mediría:

- complejidad;
- cantidad de código;
- facilidad para representar relaciones;
- consultas;
- performance;
- manejo de transacciones;
- testing;
- trazabilidad;
- facilidad para MCP;
- facilidad para migrar posteriormente a PostgreSQL;
- facilidad de comprensión por agentes IA.

Entonces la arquitectura se decide con evidencia.

---

# 19. La migración PostgreSQL puede dejar de ser una prioridad inmediata

Tu documento ya llega a esta conclusión parcialmente.

Yo la reforzaría.

Actualmente puedes tener:

```text
Nueva aplicación
        ↓
Oracle
```

y posteriormente:

```text
Nueva aplicación
        ↓
Persistence abstraction
        ├── Oracle
        └── PostgreSQL
```

Y hacer:

```text
Oracle
   │
   ├── ejecución real
   │
   └── PostgreSQL
          ↓
       shadow/read validation
```

hasta alcanzar equivalencia.

Entonces PostgreSQL deja de ser una “apuesta arquitectónica” y pasa a ser una **hipótesis comprobable**.

---

# 20. La arquitectura que yo empezaría a dibujar ahora

Esta sería mi arquitectura de transición preferida:

```text
                         ┌──────────────────────┐
                         │      AI Agents       │
                         └──────────┬───────────┘
                                    │
                                  MCP
                             JSON-RPC / MCP
                                    │
                         ┌──────────▼───────────┐
                         │     MCP Adapter      │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────▼──────────────────┐
                 │       Application Services          │
                 │                                     │
                 │ disponibilidad_dia                  │
                 │ historial_paciente                  │
                 │ estado_cuenta                       │
                 │ stock                                │
                 │ laboratorio                          │
                 └──────────────────┬──────────────────┘
                                    │
                           ┌────────▼────────┐
                           │ Domain / Rules  │
                           └────────┬────────┘
                                    │
                       ┌────────────▼────────────┐
                       │ Persistence / Repos      │
                       └────────────┬────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │       Oracle        │
                         │      legacy DB      │
                         └─────────────────────┘


 Legacy DentWeb12
       │
       └─────────────── Oracle
```

Y posteriormente:

```text
Persistence
     │
     ├── Oracle Adapter
     │
     └── PostgreSQL Adapter
```

---

# 21. Y aquí aparece algo todavía más interesante: no necesitas empezar por la UI

Tu documento originalmente contempla:

```text
Vue
   ↓
API
   ↓
Backend
```

Yo ahora probaría otra ruta:

```text
Capability
   ↓
Application Service
   ↓
MCP
```

antes de construir Vue.

¿Por qué?

Porque si el primer caso de uso funciona:

```text
LLM
 ↓
MCP
 ↓
Application Service
 ↓
Oracle
```

ya has demostrado:

- desacoplamiento;
- nueva lógica;
- nueva integración;
- acceso moderno a datos;
- contrato;
- observabilidad;
- posibilidad de IA;
- independencia del JSP.

Y todavía no has tocado el frontend.

Eso es extremadamente poderoso.

---

# 22. Esto podría convertirse en tu “vertical slice”

En lugar de modernizar:

```text
backend completo
frontend completo
BD completa
```

haría un **vertical slice**.

Por ejemplo:

```text
                    disponibilidad
                           │
            ┌──────────────┼──────────────┐
            │              │              │
          MCP        Application       Tests
            │          Service           │
            │              │              │
            └──────────────┼──────────────┘
                           │
                        Domain
                           │
                       Repository
                           │
                         Oracle
```

Todo funciona.

Pero solamente para una capacidad.

Eso es mucho más informativo que construir 30% de cada capa.

---

# 23. El primer experimento que yo haría

No empezaría con:

> “vamos a refactorizar DentWeb12”.

Empezaría con:

> **“vamos a demostrar una nueva capacidad de negocio completa sobre Oracle sin modificar DentWeb12.”**

Por ejemplo:

```text
disponibilidad_dia
```

### Entrada

```json
{
  "fecha": "2026-09-22",
  "unidad": null
}
```

### Proceso

```text
MCP
 ↓
Application Service
 ↓
Domain rule
 ↓
Repository
 ↓
Oracle
```

### Salida

```json
{
  "fecha": "2026-09-22",
  "unidades": [...]
}
```

### Después

Agregar:

```text
Characterization Test
```

y comparar:

```text
Legacy
    ↓
resultado A

Nueva capability
    ↓
resultado B

A == B
```

Eso es una semilla de arquitectura.

---

# 24. Segundo experimento: relación sin FK

Después elegiría un caso que obligue a navegar relaciones.

Por ejemplo:

```text
Paciente
   ↓
Ficha
   ↓
Atenciones
   ↓
Tratamientos
   ↓
Pagos
```

Sin agregar ninguna FK a Oracle.

El objetivo sería demostrar:

```text
Oracle físico
       ↓
ORM/Persistence
       ↓
Domain relationship
       ↓
Application service
       ↓
MCP
```

Si eso funciona elegantemente, habrás respondido una de las preguntas arquitectónicas más importantes del proyecto:

> **¿Podemos modernizar el modelo lógico sin tener que modernizar inmediatamente el modelo físico?**

Mi hipótesis es que sí.

---

# 25. Tercer experimento: PostgreSQL como sombra

No migraría todavía.

Haría algo mucho más pequeño:

```text
Oracle
   │
   ├── query
   │
   └── PostgreSQL
          │
          └── query equivalente
```

Y compararía:

- cardinalidad;
- valores;
- nulls;
- fechas;
- cálculos;
- funciones;
- agregaciones.

Esto permitiría crear un:

> **Migration Compatibility Matrix**

por capacidad.

Ejemplo:

| Capacidad | Oracle | PostgreSQL | Diferencias |
|---|---|---|---|
| disponibilidad_dia | OK | OK | fechas |
| paciente | OK | OK | función edad |
| historial | OK | — | pendiente |
| stock | OK | — | PL/SQL |

La migración deja de ser un “gran proyecto futuro” y empieza a ser una acumulación de evidencia.

---

# 26. La brecha más importante que veo hoy

Si tuviera que condensarla en una sola frase:

> **Tu documento tiene mucha comprensión del “qué tenemos” y bastante comprensión del “hacia dónde queremos ir”, pero todavía necesita formalizar con mucha mayor precisión el “cómo atravesamos el espacio entre ambos”.**

Eso es exactamente la **arquitectura de transición**.

---

# 27. La arquitectura de transición es lo que falta

Tu documento tiene muy bien:

```text
AS-IS
```

y bastante bien:

```text
TO-BE
```

Pero necesitas un tercer modelo:

```text
TRANSITIONAL ARCHITECTURE
```

Yo agregaría una sección explícita:

# Arquitectura de transición

Y tendría algo como:

```text
                  LEGACY
                     │
                     │
              ┌──────▼──────┐
              │    Oracle   │
              └──────┬──────┘
                     │
          ┌──────────┴──────────┐
          │                     │
     DentWeb12             New Platform
       legacy                   │
                                │
                       ┌────────▼────────┐
                       │ Persistence     │
                       │ Oracle Adapter  │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │ Domain          │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │ Application     │
                       │ Services        │
                       └──────┬─┬────────┘
                              │ │
                         MCP  │ │ Web
                              │ │
                              ▼ ▼
```

Esta arquitectura puede existir durante años.

Y eso no es malo.

---

# 28. Segunda gran brecha: todavía falta un “Capability Map”

Tienes inventario técnico.

Ahora necesitas un inventario de capacidades.

Por ejemplo:

```text
AGENDA
 ├── buscar disponibilidad
 ├── reservar hora
 ├── cancelar hora
 ├── modificar hora
 ├── consultar agenda
 └── bloquear agenda

PACIENTE
 ├── buscar paciente
 ├── consultar ficha
 ├── consultar historial
 ├── consultar contacto
 └── consultar tratamientos

CAJA
 ├── consultar saldo
 ├── registrar pago
 ├── consultar deuda
 └── emitir documento
```

Y luego:

```text
Capability
   ↓
Legacy implementation
   ↓
Tables
   ↓
Rules
   ↓
Risk
   ↓
New implementation
   ↓
MCP tool
   ↓
Test
```

Ese mapa sería uno de los activos más importantes del proyecto.

---

# 29. Tercera gran brecha: falta un “Rule Catalog”

Tu Hidden Logic Inventory es excelente.

Pero hay que dar el siguiente paso.

Actualmente:

```text
Encontramos lógica.
```

Después:

```text
¿qué significa esa lógica?
```

Yo crearía:

```text
Business Rule Catalog
```

Ejemplo:

```yaml
id: RULE-AGENDA-017
domain: agenda
name: disponibilidad_unidad
source:
  - disponibilidad_dia.sql
  - CalendarHelper.java
  - agenda.jsp

description: >
  Una unidad puede ser considerada disponible
  cuando...

inputs:
  - fecha
  - unidad

conditions:
  - estado = A
  - tipo IN (...)

output:
  type: availability

confidence: high

validated_by:
  - technical_analysis
  - runtime_test
  - business_owner

implemented_in:
  - legacy
  - new_application
```

Esto es oro para IA.

---

# 30. Cuarta brecha: falta un “Decision Record System”

Estás tomando decisiones importantes:

- Django;
- SQLAlchemy;
- ORM;
- Oracle inicialmente;
- MCP;
- PostgreSQL después;
- modular monolith;
- no microservicios;
- Vue;
- semantic layer.

Pero algunas aparecen como conversación y no como decisiones arquitectónicas formalizadas.

Yo incorporaría:

```text
ADR/
```

Architecture Decision Records.

Por ejemplo:

```text
ADR-001 — Oracle permanece inicialmente
ADR-002 — PostgreSQL no es prerequisite
ADR-003 — MCP como AI integration surface
ADR-004 — No microservices initially
ADR-005 — Domain model independiente del físico
ADR-006 — No FK físicas inicialmente
ADR-007 — Django como candidato
ADR-008 — ORM relationships pueden ser lógicas
```

Cada ADR debería tener:

```text
Context
Decision
Alternatives
Consequences
Status
Date
Evidence
```

Esto evitará que dentro de seis meses vuelvas a discutir las mismas decisiones.

---

# 31. Quinta brecha: falta un modelo de observabilidad

Tu documento habla mucho de tests, pero yo agregaría:

```text
Observability by design
```

Cada capability nueva debería registrar:

```text
request_id
capability
input
actor
source
duration
database_time
rows_returned
result_status
error
correlation_id
```

Y para MCP:

```text
mcp_request
tool_name
arguments
authorization
execution
result
latency
error
```

Esto será especialmente importante cuando agentes IA empiecen a ejecutar herramientas.

---

# 32. Sexta brecha: seguridad de tools MCP

Esta es una zona que considero que el documento todavía no desarrolla suficientemente.

No todas las tools deberían ser iguales.

Yo las clasificaría:

```text
READ
ANALYTICAL
ACTION
MUTATING
DESTRUCTIVE
```

Ejemplo:

```text
get_datos_paciente
    READ

disponibilidad_dia
    READ

analizar_cartera
    ANALYTICAL

reservar_hora
    ACTION

registrar_pago
    MUTATING

eliminar_reserva
    DESTRUCTIVE
```

Y agregaría políticas:

```text
READ
    bajo riesgo

ANALYTICAL
    acceso controlado

ACTION
    autorización

MUTATING
    autorización + auditoría

DESTRUCTIVE
    autorización fuerte + confirmación
```

Esto debería ser parte de la arquitectura MCP desde el principio.

---

# 33. Séptima brecha: separar “AI read” de “AI write”

Yo comenzaría con:

```text
AI → READ
```

y bastante después:

```text
AI → WRITE
```

Primero:

```text
LLM
 ↓
consulta
 ↓
Oracle
 ↓
resultado
```

Después:

```text
LLM
 ↓
propuesta
 ↓
validación humana
 ↓
acción
```

Y finalmente:

```text
LLM
 ↓
acción autónoma
```

No saltaría directamente al último nivel.

---

# 34. El MCP debería comenzar como “read-only intelligence plane”

Esto encaja perfectamente con tu estrategia.

Primera etapa:

```text
Oracle
   ↓
MCP
   ↓
AI
```

solo lectura.

Después:

```text
Oracle
   ↓
MCP
   ↓
Analytics
   ↓
AI
```

Después:

```text
MCP
   ↓
Application Services
   ↓
Actions
```

Eso crea una progresión de riesgo.

---

# 35. Otro cambio importante: no hagas 239 tools

Utilizaría los 239 helpers como:

> **materia prima para descubrir capacidades**

no como catálogo final.

Podrías terminar con algo como:

```text
239 helpers
      ↓
82 funciones técnicas
      ↓
37 reglas de negocio
      ↓
18 application services
      ↓
12 MCP tools
```

Es solamente un ejemplo.

Pero conceptualmente es mucho más sano.

---

# 36. El helper debería convertirse primero en evidencia

Ejemplo:

```text
DatosPaciente.getDatosPaciente
```

No:

```text
helper → MCP tool
```

sino:

```text
helper
  ↓
SQL
  ↓
tablas
  ↓
relaciones
  ↓
reglas
  ↓
resultado
  ↓
capacidad
  ↓
application service
  ↓
MCP
```

Ese proceso transforma legacy en arquitectura.

---

# 37. Una nueva taxonomía que incorporaría al documento

Yo agregaría cuatro capas de conocimiento:

```text
LEVEL 0 — Physical

Oracle
tables
columns
indexes
procedures
triggers


LEVEL 1 — Technical

Java
JSP
helpers
queries
dependencies


LEVEL 2 — Business

entities
relationships
rules
workflows
states
capabilities


LEVEL 3 — Intelligence

KPIs
signals
anomalies
predictions
alerts
agents
```

Tu dossier ya cubre muy bien:

```text
0 + 1
```

Ahora debes hacer crecer:

```text
2
```

y después:

```text
3
```

---

# 38. Esta puede ser la evolución natural de tu Knowledge Graph

Tu idea del dossier como Knowledge Graph me parece muy buena.

Yo lo extendería:

```text
                    BUSINESS
                       │
              ┌────────┴────────┐
              │                 │
          Capability           Rule
              │                 │
              └────────┬────────┘
                       │
                    Domain
                       │
                 Application
                       │
             ┌─────────┴─────────┐
             │                   │
          Technical            Data
             │                   │
       Java/JSP/Helper        Tables
             │                   │
             └─────────┬─────────┘
                       │
                    Oracle
```

Y encima:

```text
Business
   ↓
KPI
   ↓
Signal
   ↓
Prediction
   ↓
Alert
   ↓
Agent
```

Entonces el mismo conocimiento alimenta:

- refactoring;
- RAG;
- MCP;
- analytics;
- IA;
- documentación;
- onboarding;
- arquitectura.

Eso es muchísimo más poderoso que un simple repositorio de Markdown.

---

# 39. ¿Dónde empezaría realmente?

Si mañana tuviera que tomar el proyecto, **no empezaría migrando Oracle**.

Tampoco empezaría reconstruyendo todo el frontend.

Y tampoco empezaría creando un nuevo backend gigantesco.

Comenzaría así:

```text
FASE 0
────────────
Source Validation
+
Capability Discovery
+
Data Baseline
+
Rule Catalog
```

Después:

```text
FASE 1
────────────
Vertical Slice
```

Con una sola capability:

```text
disponibilidad_dia
```

Después:

```text
FASE 2
────────────
MCP Read-Only
```

Después:

```text
FASE 3
────────────
Semantic Application Layer
```

Después:

```text
FASE 4
────────────
AI / Analytics
```

Después:

```text
FASE 5
────────────
Nuevo módulo operacional
```

Después:

```text
FASE 6
────────────
Migración de datos
```

---

# 40. Mi roadmap revisado

Propongo reemplazar la secuencia lineal del documento por una secuencia de **ondas**.

## Onda 0 — Understand

Ya realizada en gran parte.

```text
Dossier
RICH
Oracle metadata
Relations
Java
JSP
Helpers
```

Estado:

> 🟢 Muy avanzado

---

## Onda 1 — Validate

Objetivo:

> convertir documentación en conocimiento verificable.

```text
RICH
 ↓
Source analysis
 ↓
Compile
 ↓
Runtime
 ↓
Characterization
```

Entregables:

- inventory;
- dependencies;
- rules;
- capabilities;
- tests;
- confidence.

---

## Onda 2 — Expose

Crear:

```text
Application Services
```

sobre Oracle.

No migrar BD.

No modificar DentWeb12.

Ejemplo:

```text
disponibilidad_dia
```

---

## Onda 3 — MCP

Exponer las capacidades seleccionadas:

```text
MCP tools
```

pero no todos los helpers.

Objetivo:

> demostrar integración real con agentes.

---

## Onda 4 — Intelligence

Crear:

```text
Semantic Data Layer
+
Analytics
+
AI
```

Aquí entra el valor para negocio.

---

## Onda 5 — Modernize

Elegir un módulo.

```text
Legacy
 ↓
Characterization
 ↓
Application Service
 ↓
Domain
 ↓
New UI
```

Aquí Django puede convertirse en el nuevo núcleo.

---

## Onda 6 — Data Transformation

Ahora sí:

```text
Oracle
 ↓
Modelo validado
 ↓
PostgreSQL
```

---

## Onda 7 — Retire

Finalmente:

```text
Legacy
 ↓
retirement
```

No antes.

---

# 41. La diferencia con tu roadmap actual

Tu roadmap actual todavía tiene una tendencia:

```text
Understand
→ Expose
→ Intelligence
→ Modernize
→ Transform Data
→ Retire
```

Es bueno.

Pero yo introduciría un concepto transversal:

```text
             VALIDATION
                  │
                  ▼
Understand ── Expose ── Intelligence ── Modernize ── Data ── Retire
                  │          │             │
                  └──────────┴─────────────┴── Evidence
```

La transformación no avanza simplemente por tiempo.

Avanza por:

> **evidencia.**

---

# 42. Gates que agregaría

Tu documento ya tiene seis gates.

Yo los convertiría en gates más arquitectónicos:

## Gate 0 — Knowledge Confidence

¿Sabemos qué hace realmente?

---

## Gate 1 — Capability Contract

¿Podemos describir la capacidad sin hablar de tablas?

---

## Gate 2 — Characterization

¿Podemos demostrar que el nuevo comportamiento coincide?

---

## Gate 3 — Persistence Independence

¿El dominio depende de Oracle?

---

## Gate 4 — MCP Safety

¿La capability puede exponerse de forma segura a agentes?

---

## Gate 5 — Operational Equivalence

¿Puede convivir con el legacy?

---

## Gate 6 — Cutover

¿Podemos apagar la implementación antigua?

---

# 43. Lo que considero que NO necesitas todavía

No necesitas todavía:

- microservicios;
- Kubernetes;
- service mesh;
- Kafka;
- event sourcing;
- CQRS completo;
- DDD táctico exhaustivo;
- PostgreSQL productivo;
- migración masiva;
- Vue completo;
- API completa;
- IA autónoma escribiendo datos.

Todo eso puede ser válido en algún momento.

Pero ninguno debería ser prerequisite del primer vertical slice.

---

# 44. Lo que sí necesitas ahora

Necesitas:

```text
1. Código real
2. Runtime
3. Data baseline
4. Capability map
5. Rule catalog
6. Characterization tests
7. Application service
8. Persistence abstraction
9. MCP tool
10. Observability
```

Eso es suficiente para comenzar.

---

# 45. Una arquitectura Django que sí me gustaría ver

No haría simplemente:

```text
Django
├── models.py
├── views.py
└── urls.py
```

Para este proyecto iría hacia algo parecido a:

```text
dentweb/
│
├── apps/
│   │
│   ├── agenda/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   │
│   ├── pacientes/
│   ├── caja/
│   ├── laboratorio/
│   └── stock/
│
├── shared/
│
├── mcp/
│   ├── tools/
│   ├── schemas/
│   ├── policies/
│   └── server.py
│
├── persistence/
│   ├── oracle/
│   └── postgres/
│
├── analytics/
│
├── tests/
│   ├── characterization/
│   ├── contract/
│   ├── integration/
│   └── domain/
│
└── docs/
    ├── adr/
    ├── capabilities/
    ├── rules/
    └── data/
```

No porque esta estructura sea “la correcta”.

Sino porque obliga a separar:

```text
Domain
Application
Infrastructure
Interfaces
```

---

# 46. Django no debería conocer el Oracle legacy

Una regla que yo escribiría literalmente:

> **El dominio no debe saber que Oracle existe.**

Idealmente:

```text
Domain
   X Oracle
   X SQL
   X Django
   X MCP
```

El dominio conoce:

```text
Paciente
Ficha
Agenda
Pago
Disponibilidad
```

Infrastructure conoce:

```text
Oracle
SQLAlchemy
Django ORM
python-oracledb
```

MCP conoce:

```text
tools
schemas
authorization
transport
```

---

# 47. ¿Y si al final PostgreSQL nunca fuera necesario?

También está bien.

Esta es una de las ventajas de separar:

```text
Domain
   ↓
Repository
   ↓
Oracle
```

de:

```text
Domain
   ↓
Repository
   ↓
PostgreSQL
```

La migración deja de ser una religión arquitectónica.

Se convierte en una decisión basada en:

- costo;
- performance;
- operación;
- disponibilidad;
- seguridad;
- capacidades;
- analytics;
- soporte;
- evolución.

Eso es mucho más sano.

---

# 48. Una observación sobre una afirmación de tu documento

Hay una frase que conviene corregir:

> “Cambiar de Oracle a PostgreSQL = cambiar la URL de conexión.”

Eso **no debe quedar como conclusión arquitectónica**.

SQLAlchemy sí tiene soporte para Oracle y PostgreSQL, y abstrae una parte importante del acceso mediante dialectos. citeturn0search0turn0search2

Pero una aplicación real no queda portable entre ambos motores simplemente cambiando:

```text
oracle+oracledb://...
```

por:

```text
postgresql://...
```

Tu propio sistema contiene:

- funciones Oracle;
- SQL específico;
- PL/SQL;
- `SYSDATE`;
- `ADD_MONTHS`;
- funciones propias;
- packages;
- triggers;
- tipos;
- secuencias;
- comportamiento transaccional.

Por eso la abstracción debe estar **por encima de la semántica específica de Oracle**, no solamente en el driver.

---

# 49. Otra observación importante: el ORM no debe convertirse en la arquitectura

Existe un riesgo:

```text
Oracle
 ↓
ORM
 ↓
Django
```

y creer que ya desacoplaste.

No.

Eso sería:

```text
Oracle
 ↓
ORM
 ↓
Application
```

pero probablemente seguirías teniendo:

```text
Oracle schema
     ↓
domain model
```

muy acoplado.

El verdadero desacoplamiento es:

```text
Business capability
        ↓
Domain
        ↓
Repository
        ↓
Persistence
```

El ORM es una herramienta dentro de Persistence.

No es el Domain.

---

# 50. La arquitectura de datos también debería tener dos modelos

Yo definiría explícitamente:

## Operational Model

```text
Oracle legacy
```

## Semantic Model

```text
Paciente
Atención
Tratamiento
Pago
Agenda
Laboratorio
Stock
Comisión
```

Y eventualmente:

## Analytical Model

```text
fact_atencion
fact_pago
fact_laboratorio
fact_stock
dim_paciente
dim_unidad
dim_profesional
dim_tiempo
```

No necesitas construir el tercer modelo ahora.

Pero debes evitar que:

```text
AI
```

tenga que aprender:

```text
100 columnas
EAV
códigos históricos
joins implícitos
```

para responder:

> “¿Qué pacientes tienen compromisos atrasados?”

---

# 51. El mayor potencial de IA está precisamente aquí

Tu proyecto puede terminar siendo algo mucho más interesante que:

> “reescribir una aplicación Java en Python”.

Puede convertirse en:

```text
Legacy
   ↓
Knowledge Recovery
   ↓
Semantic Model
   ↓
Capabilities
   ↓
MCP
   ↓
AI
   ↓
Modern Application
```

La IA no solamente genera código.

La IA participa en:

```text
reconocimiento
extracción
clasificación
trazabilidad
generación
testing
validación
observabilidad
operación
```

Eso sí constituye una transformación verdaderamente AI-assisted.

---

# 52. El dossier puede convertirse en una “fuente de verdad”

Pero yo agregaría una advertencia.

El dossier no debería ser la única fuente de verdad.

Yo tendría:

```text
SOURCE OF TRUTH STACK
```

### Nivel 1

Código fuente real.

### Nivel 2

Runtime.

### Nivel 3

Datos.

### Nivel 4

Tests.

### Nivel 5

Dossier.

### Nivel 6

LLM/RAG.

El LLM nunca debería ser la autoridad.

Debe ser un intérprete.

---

# 53. El concepto de “confidence” debería entrar al Knowledge Graph

Cada regla/capacidad debería tener:

```text
confidence:
    low
    medium
    high
    verified
```

Ejemplo:

```yaml
capability: disponibilidad_dia

confidence:
  source_analysis: high
  data_analysis: high
  runtime: medium
  business_validation: pending
```

Eso sería extraordinariamente útil para controlar el proyecto.

---

# 54. Una idea que agregaría: “Transformation Ledger”

Mantendría un registro de cada transformación.

```text
TL-0001
Capability: disponibilidad_dia

Legacy:
    JavaHelperX

New:
    Python ApplicationService

MCP:
    disponibilidad_dia

Oracle:
    unchanged

Tests:
    27

Equivalent:
    100%

Runtime:
    14 ms legacy
    11 ms new

Status:
    Shadow validated
```

Cuando tengas 100 capabilities así documentadas, tendrás una evidencia brutal del avance.

---

# 55. El proyecto debería medir “capabilities migrated”, no “líneas de código”

No mediría:

```text
Java eliminados
JSP eliminados
clases convertidas
```

como principal KPI.

Mediría:

```text
Capabilities discovered
Capabilities verified
Capabilities modernized
Capabilities exposed
Capabilities migrated
Capabilities retired
```

Y también:

```text
Rules recovered
Rules verified
Characterization tests
Legacy dependencies removed
Oracle dependencies removed
```

Eso refleja transformación real.

---

# 56. El piloto perfecto para ti

Yo buscaría una capability que cumpla:

```text
Alta relevancia
+
Complejidad media
+
Lectura principalmente
+
Reglas claras
+
Varias tablas
+
Valor para negocio
+
Potencial MCP
```

`disponibilidad_dia` tiene varias de esas propiedades.

Por eso me parece un candidato excelente.

No necesariamente porque sea “el módulo más importante”, sino porque puede demostrar:

```text
SQL
Oracle
reglas
parámetros
relaciones
MCP
JSON-RPC
IA
tests
```

en una sola pieza.

---

# 57. La prueba que realmente importa

La prueba no debería ser:

> “Miren, el MCP responde.”

Eso es demasiado poco.

La prueba debería ser:

```text
Usuario:
“¿Qué disponibilidad existe para mañana en la unidad X?”

        ↓

LLM

        ↓

MCP

        ↓

disponibilidad_dia

        ↓

Application Service

        ↓

Oracle

        ↓

resultado estructurado

        ↓

LLM

        ↓

respuesta comprensible
```

Y simultáneamente:

```text
Legacy
        ↓
mismo escenario
        ↓
resultado

Nuevo
        ↓
mismo escenario
        ↓
resultado

COMPARE
```

Eso es una demostración de transformación.

---

# 58. La verdadera arquitectura “ideal vs real”

Aquí está la brecha que me parece más útil documentar.

## Arquitectura ideal

```text
Domain
  ↓
Application
  ↓
Repository
  ↓
PostgreSQL
  ↓
Semantic Data Platform
  ↓
AI
```

## Arquitectura real de transición

```text
Legacy Oracle
      │
      ├──────── DentWeb12
      │
      └──────── New Application
                    │
                Application
                    │
                  Domain
                    │
                Repository
                    │
                  Oracle
                    │
                  MCP
                    │
                    AI
```

## Arquitectura futura posible

```text
                Web
                 │
                MCP
                 │
                AI
                 │
        ┌────────▼────────┐
        │ Application     │
        │ Services        │
        └────────┬────────┘
                 │
              Domain
                 │
          Repository
          /           \
      Oracle         PostgreSQL
                         │
                  Analytics/Data
                         │
                         AI
```

Y lo hermoso es que:

> **no necesitas construir la tercera arquitectura para comenzar a recorrer el camino.**

---

# 59. Mi evaluación de madurez del documento

No como “score político” ni como nota absoluta, sino como diagnóstico cualitativo:

| Área | Estado |
|---|---|
| Comprensión del legacy | **Muy avanzada** |
| Comprensión técnica | **Muy avanzada** |
| Recuperación de conocimiento | **Muy avanzada** |
| Identificación del riesgo | **Muy avanzada** |
| Estrategia de modernización | **Avanzada** |
| Estrategia de transición | **Intermedia** |
| Modelo de dominio | **En construcción** |
| Capability map | **Falta formalizar** |
| Rule catalog | **Falta formalizar** |
| MCP architecture | **Idea fuerte, necesita maduración** |
| Data architecture | **Hipótesis, no decisión** |
| ORM strategy | **Exploración** |
| Django architecture | **Exploración inicial** |
| Testing strategy | **Buena base** |
| Operational observability | **Debe crecer** |
| Security model para AI/tools | **Debe crecer** |
| PostgreSQL migration | **Correctamente no cerrada** |
| Roadmap | **Bueno, pero puede evolucionar a ondas/vertical slices** |

---

# 60. La brecha real

Yo la resumiría así:

```text
                 LO QUE TIENES
                       │
                       ▼
             ┌───────────────────┐
             │  Knowledge        │
             │  Recovery         │
             │                   │
             │  Technical map    │
             │  Data map         │
             │  RICH             │
             │  Relations        │
             └─────────┬─────────┘
                       │
                 BRECHA ACTUAL
                       │
                       ▼
             ┌───────────────────┐
             │ Transition        │
             │ Architecture      │
             │                   │
             │ Capabilities      │
             │ Rules             │
             │ Contracts         │
             │ Domain            │
             │ Tests             │
             │ MCP policy        │
             └─────────┬─────────┘
                       │
                       ▼
               FUTURA ARQUITECTURA
                       │
                       ▼
             Django / Domain / MCP
             PostgreSQL / AI
```

---

# 61. Entonces, ¿estás cerca?

Sí.

Pero no estás cerca de:

> “ya podemos reescribir”.

Estás cerca de algo más importante:

> **“ya podemos comenzar a experimentar la nueva arquitectura con riesgo controlado.”**

Y esa es una diferencia enorme.

---

# 62. Lo que yo incorporaría inmediatamente al documento

Crearía estas nuevas secciones:

```text
40. Arquitectura de transición
41. Capability Map
42. Business Rule Catalog
43. Application Service Contract
44. MCP Architecture
45. MCP Security Model
46. ORM Strategy
47. Oracle Legacy Persistence Strategy
48. Semantic Application Layer
49. Characterization Test Strategy
50. Transformation Ledger
51. Architecture Decision Records
52. Vertical Slice Pilot
53. Migration Compatibility Matrix
54. Observability Model
55. Definition of Done por capability
```

Eso llevaría el documento desde:

```text
estrategia de modernización
```

hacia:

```text
blueprint de transformación
```

---

# 63. Definition of Done para una capability

Esto también me parece importante.

Una capability no debería considerarse modernizada porque “funciona”.

Debe cumplir:

```text
[ ] Capability definida
[ ] Regla documentada
[ ] Fuentes legacy identificadas
[ ] Datos involucrados identificados
[ ] Contrato definido
[ ] Application Service implementado
[ ] Repository implementado
[ ] Oracle validado
[ ] Characterization test
[ ] Integration test
[ ] MCP tool
[ ] Autorización
[ ] Observabilidad
[ ] Resultado equivalente
[ ] Documentación actualizada
[ ] Legacy dependency registrada
```

Eso convierte la modernización en un proceso industrializable.

---

# 64. Una consecuencia muy interesante: la IA puede ayudar a construir el sistema que luego la IA consumirá

Este proyecto tiene una especie de círculo virtuoso:

```text
IA
 ↓
analiza legacy
 ↓
recupera conocimiento
 ↓
genera capabilities
 ↓
genera tests
 ↓
genera Application Services
 ↓
genera MCP tools
 ↓
MCP alimenta agentes
 ↓
agentes utilizan capabilities
 ↓
nueva arquitectura genera más conocimiento
```

Esto es bastante más interesante que “usar IA para programar más rápido”.

Es una:

> **AI-assisted transformation architecture.**

---

# 65. Mi recomendación concreta para los próximos 30 días

## Semana 1

### Source-Based Validation

No construiría todavía la nueva aplicación completa.

Usaría los RICH y el código real para validar:

- dependencias;
- SQL;
- reglas;
- clases;
- llamadas;
- flujos;
- configuración.

Resultado:

```text
Validated Knowledge Base
```

---

## Semana 2

### Capability Discovery

Elegiría 5–10 capacidades.

Por ejemplo:

```text
disponibilidad_dia
get_datos_paciente
historial_citas
estado_cuenta
stock_producto
```

No necesariamente estas cinco exactamente.

El criterio sería:

```text
valor + complejidad + riesgo + datos
```

---

## Semana 3

### Persistence Experiment

Construiría:

```text
Oracle
 ↓
Django ORM
```

y:

```text
Oracle
 ↓
SQLAlchemy
```

sobre **una sola capability**.

No dos aplicaciones completas.

---

## Semana 4

### MCP Vertical Slice

Implementaría:

```text
LLM
 ↓
MCP
 ↓
Application Service
 ↓
ORM/Persistence
 ↓
Oracle
```

y además:

```text
Characterization Test
```

El resultado debería ser una demostración reproducible.

---

# 66. Si tuviera que tomar una sola decisión hoy

Sería esta:

> **No decidir todavía PostgreSQL. No decidir todavía la arquitectura final del frontend. No decidir todavía REST vs MCP como decisión excluyente. Sí decidir comenzar un vertical slice sobre Oracle, con dominio desacoplado, persistence abstraction y MCP como primera interfaz de experimentación.**

Eso reduce enormemente el riesgo.

---

# 67. Y si tuviera que dibujar tu “milla cero”

La dibujaría así:

```text
                         ┌─────────────┐
                         │   LLM       │
                         └──────┬──────┘
                                │
                               MCP
                                │
                    ┌───────────▼───────────┐
                    │ MCP Tool              │
                    │ disponibilidad_dia    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Application Service   │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Domain / Rules        │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Repository            │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Oracle 11g XE         │
                    │ SIN MODIFICAR         │
                    └───────────────────────┘

                 + Characterization Tests
                 + Observability
                 + Rule Catalog
                 + ADR
```

Y solamente cuando esto funcione:

```text
Oracle
```

se convierte en:

```text
Oracle Adapter
```

y aparece:

```text
PostgreSQL Adapter
```

---

# 68. Conclusión

Después de leer el documento completo, mi conclusión es bastante distinta de “todavía te falta mucho”.

**No. Ya tienes muchísimo.**

Lo que tienes no es todavía el plano constructivo completo, pero sí tienes algo que normalmente cuesta muchísimo más conseguir:

> **una comprensión razonablemente profunda del sistema que estás intentando transformar.**

El siguiente salto no consiste en investigar más frameworks.

Consiste en transformar el conocimiento recuperado en **unidades ejecutables de arquitectura**.

Y ahí creo que tu nueva intuición de:

```text
Django
+
ORM
+
Oracle inicialmente
+
MCP
+
JSON-RPC
+
IA
```

puede ser una dirección muy interesante.

Pero con una condición:

> **Django no debe ser la estrategia. MCP no debe ser la estrategia. PostgreSQL tampoco debe ser la estrategia.**

La estrategia es:

```text
RECUPERAR CONOCIMIENTO
        ↓
EXPLICITAR CAPACIDADES
        ↓
EXPLICITAR REGLAS
        ↓
SEPARAR DOMINIO
        ↓
AISLAR PERSISTENCIA
        ↓
EXPONER CAPACIDADES
        ↓
VALIDAR COMPORTAMIENTO
        ↓
MODERNIZAR PROGRESIVAMENTE
        ↓
TRANSFORMAR DATOS
        ↓
RETIRAR LEGACY
```

Y las tecnologías son herramientas dentro de ese proceso.

---

# 69. La idea que yo pondría ahora al frente del documento

Tu frase actual:

> “No queremos reescribir la aplicación. Queremos recuperar su conocimiento, separar sus responsabilidades, preservar su comportamiento y reemplazar progresivamente su tecnología.”

me parece muy buena.

Pero después de esta nueva etapa agregaría:

> **“No vamos a transformar una aplicación completa. Vamos a transformar capacidades de negocio, una por una, preservando evidencia, desacoplando su dominio, exponiéndolas mediante contratos y reemplazando progresivamente sus implementaciones.”**

Y todavía agregaría una segunda:

> **“Oracle no tiene que desaparecer para que la nueva arquitectura exista.”**

Y una tercera:

> **“MCP no será el dominio de la aplicación; será una de las puertas de entrada a sus capacidades.”**

Para mí, esas tres frases describen mucho mejor hacia dónde está evolucionando el proyecto.

---

# 70. Mi lectura final del momento en que estás

Creo que estás pasando de:

```text
ASSESSMENT
```

a:

```text
TRANSFORMATION ENGINEERING
```

El assessment respondió:

> **¿Qué tenemos?**

La siguiente etapa debe responder:

> **¿Qué capacidades tenemos?**

Después:

> **¿Qué reglas las gobiernan?**

Después:

> **¿Cómo las aislamos?**

Después:

> **¿Cómo las exponemos?**

Después:

> **¿Cómo demostramos que la nueva implementación es equivalente?**

Y solamente después:

> **¿Qué partes de Oracle, JSP y Java podemos retirar?**

Ese orden, en mi opinión, es el que convierte este proyecto desde una posible “reescritura gigantesca” en una **transformación incremental, medible y reversible**.

Y ahí está, probablemente, la diferencia entre pasar años “modernizando DentWeb12” y realmente construir una nueva plataforma alrededor del conocimiento que DentWeb12 ya contiene.

---

## Apéndice — Fuentes técnicas externas consultadas

La revisión arquitectónica anterior se apoya principalmente en el documento proporcionado. Para la parte específica de ORM/Oracle se contrastó además la documentación actual de SQLAlchemy:

- SQLAlchemy ORM — relaciones y `relationship()`.
- SQLAlchemy — configuración de relaciones mediante `primaryjoin`, `foreign_keys` y `foreign()`.
- SQLAlchemy — dialecto Oracle y soporte de `python-oracledb`.

La documentación actual de SQLAlchemy confirma que es posible modelar relaciones ORM con condiciones explícitas cuando no existe metadata de FK en la tabla, aunque esto no equivale a disponer de integridad referencial física en Oracle.

---

# Anexo — Resumen de decisión propuesto

```text
┌──────────────────────────────────────────────────────┐
│                 DENTWEB12 TRANSFORM                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  LEGACY                                             │
│    │                                                 │
│    ├── Java/JSP                                      │
│    └── Oracle 11g                                   │
│                                                      │
│                 ↓                                    │
│                                                      │
│  KNOWLEDGE RECOVERY                                  │
│    ├── RICH                                          │
│    ├── Rules                                         │
│    ├── Capabilities                                  │
│    └── Data model                                    │
│                                                      │
│                 ↓                                    │
│                                                      │
│  NEW PLATFORM                                       │
│    ├── Python / Django                              │
│    ├── Domain                                       │
│    ├── Application Services                         │
│    ├── Persistence abstraction                      │
│    └── Oracle                                       │
│                                                      │
│                 ↓                                    │
│                                                      │
│  MCP                                                │
│    ├── Tools                                        │
│    ├── Policies                                     │
│    ├── Audit                                        │
│    └── AI Agents                                    │
│                                                      │
│                 ↓                                    │
│                                                      │
│  INTELLIGENCE                                       │
│    ├── Semantic Layer                               │
│    ├── Analytics                                    │
│    ├── Prediction                                   │
│    └── Alerts                                       │
│                                                      │
│                 ↓                                    │
│                                                      │
│  MODERNIZATION                                      │
│    ├── Vertical slices                              │
│    ├── Characterization tests                       │
│    ├── Modular monolith                             │
│    └── Progressive retirement                       │
│                                                      │
│                 ↓                                    │
│                                                      │
│  DATA TRANSFORMATION                                │
│    ├── Oracle                                       │
│    └── PostgreSQL                                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Estado recomendado:** comenzar por un vertical slice sobre Oracle, no por una migración de BD ni por una reescritura de frontend.

