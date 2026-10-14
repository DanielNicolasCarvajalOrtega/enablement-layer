# PLANTILLA · Implementar una capability de tipo «consulta» (READ)

> **Para quién es:** para la persona que va a agregar **una** capacidad de consulta a
> la capa de habilitación sin entender el proyecto entero. Se le siguen los 12 pasos
> en orden; ninguno es opcional.
>
> **Cómo usar:** leé el documento completo una vez antes de escribir código, llená el
> **encargo** (§3) con el dueño, y después seguí los pasos. El esqueleto de archivos
> para copiar está en [`_plantilla/`](./_plantilla/).
>
> **Referencias vivas:** la capacidad #7 `consultar_pacientes_por_ciudad_chile` es la
> implementación más reciente y la que se aparta más del bloque original (sin `fecha`,
> dominio nuevo, roles propios). La ficha modelo con `fecha` es
> [`consultar_ingresos_por_tipo_pago.md`](./consultar_ingresos_por_tipo_pago.md).
>
> **Estado de la base:** 7 capabilities · **240 tests en verde** · paridad viva
> ejecutada 2026-10-05.

---

## 0 · La ruta completa

```
enablement-layer/
│
├── application/registry.py                     PASO 1 · contrato (fuente única)
├── application/<dominio>/models.py             PASO 2 · Pydantic in/item/out
├── application/<dominio>/ports.py              PASO 3 · puerto + NamedTuple
├── infrastructure/oracle/<dominio>_repository.py  PASO 4 · SQL + binds
├── application/<dominio>/service.py            PASO 5 · lógica de negocio
├── adapters/rest/<dominio>.py                  PASO 6 · endpoint
├── adapters/mcp/<dominio>.py                   PASO 7 · tool MCP
│
│   ··· si el dominio es NUEVO, además: ···
├── composition.py                              PASO 6b · repo + service
├── app.py                                      PASO 6b · include_router + import MCP
│
├── tests/test_registry.py                      PASO 8 · declaración de la forma de entrada
├── tests/test_contracts.py                     PASO 8 · endpoint + auth + errores
├── tests/test_service_<dominio>.py             PASO 8 · suite nueva si el dominio es nuevo
├── tests/test_repository_sql.py                PASO 8 · guardas de fidelidad SQL
├── tests/test_paridad_oracle.py                PASO 9 · Nivel 0
│
└── docs/refactorizacion/capacidades/
    ├── <nombre_snake>.md                       PASO 10 · ficha (16 secciones)
    └── CATALOGO.md                             PASO 11 · catálogo
```

**Orden, no gusto:** el registro (paso 1) va primero aunque todavía no haya nada que
importar. `_validate()` corre al importar el módulo y falla rápido: si el contrato está
mal lo sabés en el paso 1, no en el paso 7.

**Si la consulta no es de Control Contable**, casi con seguridad estás creando un
dominio nuevo. Los candidatos de [`docs/go/encuentros.md`](../../go/encuentros.md) —
agenda, funcionarios, notas, becas, convenios — son bloques que no son contables y
toca el rama de PASO 6b.

---

## 1 · Diez reglas que no se negocian

| # | Regla | Por qué |
|---|---|---|
| R1 | **Identidad canónica.** El nombre de la capacidad es independiente del protocolo. El nombre MCP no lleva versión (`consultar_x`, nunca `consultar_x_v1`). | V2 R10 |
| R2 | **Nada de `getXxx()`.** El nombre expresa intención de negocio: `consultar_...`. `getBoletasPorUsuario()` dice cómo está implementado. | V2 R3 |
| R3 | **`READ` y punto.** `mode` es el único dato de entrada; las 4 annotations MCP se **derivan** de `ANNOTATIONS_BY_MODE`. Jamás se escriben a mano. | V2 R17 |
| R4 | **La descripción es contrato, no documentación.** Qué hace, cuándo usarla y **cuándo NO usarla**, remitiendo a las capabilities vecinas. Sin `usage_notes` el contrato está incompleto aunque el JSON Schema esté perfecto. | V2 R6, R17b |
| R5 | **El adapter no tiene lógica.** REST y MCP delegan en el service. Los dos llaman a la **misma instancia**, la que sale de `composition.py`. | V2 R5, R6 |
| R6 | **El SQL vive solo en el repository.** El service no sabe qué tabla existe; mapea conceptos de negocio, no columnas. | V2 R7, R15 |
| R7 | **La autorización ocurre antes de ejecutar**, en un único enforcement point. Nunca una condición de autorización dentro de la query ni dentro del service. | V2 R8 |
| R8 | **`NO_DATA` ≠ `UNAVAILABLE`.** Tabla vacía con query exitosa → `NO_DATA` (404). Oracle caído → `UNAVAILABLE` (503). El legacy silencia los errores; vos **no** lo replicás. | V2 R18 |
| R9 | **El total se calcula en la capa**, nunca le pedís la suma al LLM. | V2 §8.4 |
| R10 | **No inventás filtros.** Replicás la query de la fuente normativa tal cual. Un `WHERE`, un `HAVING` o un filtro de estado de más ya es **otra capacidad**. | V2 §0.1 |

---

## 2 · Antes de tocar código: el encargo

Llená esto con el dueño y tenlo a la mano.

```yaml
nombre_funcion:          # en lenguaje de negocio: "agenda del día"
nombre_snake:            # agenda_del_dia
nombre_tool:             # consultar_agenda_del_dia   (sin versión, R10)
dominio:                 # contabilidad | agenda | pacientes | <nuevo>
id_capability:           # <dominio>.<nombre_snake>
rest_path:               # /api/<dominio>/<kebab-case>
sql_id:                  # Q<n> | ENC.<NOMBRE> | el tuyo
fuente_normativa:        # archivo:líneas — de dónde SE COPIÓ la query
metodo_legacy:           # ResumenControl.setTablaAgendaHoy | rptBecas.jsp:214-220
data_profile:            # operational | financial | financial_pii | clinical
roles:                   # ⊆ KNOWN_ROLES
acepta_fecha:            # sí | no
acepta_otros_filtros:    # ninguno | <lista>
expone_pii:              # sí | no
es_censo_variable:       # sí → paridad por comparación · no → golden file
```

### Las 6 preguntas que hay que responder antes de empezar

1. ¿Cuál es la **fuente normativa** de la query? (Java `:líneas`, JSP `:líneas`, o
   la sección de `docs/go/encuentros.md`)
2. ¿El legacy tiene un reporte **más parecido** que no es la fuente? Documentá la
   diferencia (§6.2 de la ficha #7 es el modelo).
3. ¿Qué **decisiones del legacy se replican** aunque parezcan bugs? (banda horaria vs
   igualdad exacta, estados incluidos, umbral mínimo, agrupación)
4. ¿Quién aprueba `allowed_fields` / `forbidden_fields`? Para `financial`, gerencia de
   finanzas; para `clinical`, el dueño del dato.
5. ¿Los **roles** son los del dominio? Un dominio nuevo casi nunca es trabajo
   contable: analizá si `contador` entra.
6. Si expone **PII**, ¿quién es el destinatario autorizado y cómo se mitiga?

---

## 3 · Hallazgos conocidos de este repo

Son cinco desviaciones entre lo que la documentación promete y lo que el código hace.
No se arreglan acá: se documentan para que el programador no tropiece.

### H1 · El 400 de FastAPI ya no manda a arreglar `fecha`, pero los services sí

`app.py::validation_error_handler` derivaba `"fecha debe ser YYYY-MM-DD"` para
cualquier error de validación. Ya se corrigió: el mensaje se arma con los campos que
fallaron y hay dos tests que lo fijan (`test_fecha_invalida_es_400_invalid_argument`
y `test_el_handler_de_validacion_deriva_el_mensaje_del_error`).

**Queda pendiente el mismo patrón en el service.** Por ejemplo
`application/contabilidad/service.py:157`:

```python
raise ValidationError(
    "fecha es obligatoria y debe ser YYYY-MM-DD; origen debe ser CAJA, TOTEM o WEBPAY."
) from exc
```

Se dispara cuando el error es **solo de `origen`** y la fecha llegaba válida: el
mensaje le pide al agente que corrija un campo que no falló. Si la capability que
creás usa `_dec(...)`, armá el mensaje con el campo real, no con la lista completa.

### H2 · La clasificación de argumentos es por id, no por dominio

`tests/test_registry.py` declaraba las capacidades `CON_FECHA` / `SIN_ARGUMENTOS` con
una comprensión sobre el prefijo del dominio, mientras el comentario afirmaba que
"la clasificación es explícita para que un tercer dominio no se cuelgue en silencio del
grupo equivocado". **El código no hacía eso**: cualquier dominio no-contable caía por
defecto en `SIN_ARGUMENTOS`. Una capability nueva con `fecha` habría fallado en
`test_input_schema_de_las_sin_argumentos_esta_vacio` con un mensaje que apunta al
schema cuando el problema estaba en el clasificador.

Hoy las dos listas son literales de id y
`test_toda_capability_declara_si_toma_argumentos` exige que su unión sea exactamente
`set(CAPABILITIES)`.

**Lo que hay que hacer al agregar una capability:** agregar su id a `CON_FECHA` o a
`SIN_ARGUMENTOS`. Si no lo hacés, ese test falla con la lista de "sin declarar".

### H3 · Los conteos del catálogo son tripwires, no mágicos

`test_registro_tiene_las_7_capabilities` decía `assert len(CAPABILITIES) == 7`. El
número existía para forzar a actualizar el catálogo, pero no verificaba que el
catálogo se hubiera actualizado y había que subirlo a mano. Ahora
`test_catalogo_documenta_todas_las_capabilities` lee `CATALOGO.md` y exige que el
`name` de cada contrato aparezca en él.

**No hay ningún número que subir a mano.** Lo que hay que hacer es agregar la fila y
la ficha en `CATALOGO.md`, y si el test falla es porque esas filas no están.

`test_list_tools_expone_todas_las_capabilities` compara contra `len(CAPABILITIES)`,
no contra una constante.

### H4 · Un rol nuevo son 5 archivos, y ninguna ficha lo dice

1. `application/registry.py` → agregar el rol a `KNOWN_ROLES` (sin eso, `_validate()` falla).
2. `config.py` → `AUTH_TOKEN_<ROL>: str = ""` en `Settings` **y** su entrada en `token_roles`.
3. `.env` → `AUTH_TOKEN_<ROL>=...` (**nunca** al repo).
4. `.env.example` → la variable vacía.
5. `tests/conftest.py` → `os.environ["AUTH_TOKEN_<ROL>"] = "tok-<rol>-test"`.
   **Asignación, no `setdefault`**: ver el comentario de ese archivo.

`test_rollos_del_registry_cuadran_con_los_tokens_de_env` falla si se saltea alguno.

### H5 · El `CapabilityContract` no tiene todos los campos de gobernanza

V2 §9.3 define `errors`, `business_rules`, `data.allowed_fields`,
`data.forbidden_fields`, `observability`, `performance` y `agent_traffic`. **Ninguno
existe** en el dataclass (`application/registry.py:69`), que tiene 15 campos.

Eso significa que "el registry es la fuente única" vale para **rol, nombre, modo,
descripción, ruta y anotaciones**, y **no** para errores, reglas de negocio ni frontera
de privacidad: esos viven solo en la ficha y no los testea nada.

**Consecuencia práctica:** escribí igual las secciones 7, 9, 11 y 12 de la ficha, con
las listas explícitas. Son la frontera documentada; el día que se agreguen al registry
hay que poder compararlas. Y no afirmes en la ficha que algo está "enforced by test"
si solo está escrito en prosa.

---

## 4 · Tampoco son bugs, pero conviene saberlo

- **Los cuatro `test_ollama_*.py` y `test_mcp.py` de la raíz son scripts manuales.**
  Están con `if __name__ == "__main__"` y no definen funciones `test_*`, pero pytest
  los **importa** al colectar: `import ollama` tiene que funcionar o la suite rompe en
  importación.
- **No hay `pytest.ini` ni `pyproject.toml` con `testpaths`**, así que pytest colecta
  desde el rootdir. Corré siempre desde `enablement-layer/`.
- **No hay `ruff`, `mypy` ni ningún lint configurado en el venv.** El único control de
  calidad es la suite.
- **Si `uvicorn` sigue corriendo desde antes del cambio**, los clientes MCP siguen
  viendo la lista de tools vieja. Reiniciá siempre.

---

# PASO 1 · Contrato en el registry

**Archivo:** `application/registry.py`

Agregar la entrada a `CAPABILITIES`. Los campos son exactos: el dataclass es
`frozen=True`.

```python
"<dominio>.<nombre_snake>": CapabilityContract(
    id="<dominio>.<nombre_snake>",
    name="consultar_<nombre_snake>",      # SIN versión (R10). Es el nombre MCP:
                                          # mcp_name lo devuelve tal cual.
    title="<título corto legible>",       # lo que se ve en la annotation de la tool
    mode=OperationMode.READ,              # de acá salen las 4 annotations
    description=(
        "<Qué hace, en una línea, sin jerga de infraestructura.> ÚSALA cuando "
        "<pregunta típica del negocio>. <parámetros y si son obligatorios>. "
        "Solo lectura."
    ),
    usage_notes=(
        "NO la uses para <capacidad vecina A> (<su name>), ni para <vecina B>. "
        "<Advertencia semántica: lo que el número NO es.> <Si hay un sesgo del "
        "legacy replicado a propósito, decilo.>"
    ),
    rest_method="GET",
    rest_path="/api/<dominio>/<kebab-case>",
    roles=<DOMINIO>_ROLES,                # o la tupla literal
    oracle_sql_id="<Q<n> | ENC.<NOMBRE>>",
    legacy_method="<Clase.método | archivo.jsp>",
    legacy_lines="<a-b>",
    data_profile="<operational | financial | financial_pii | clinical>",
    examples=({"fecha": "<YYYY-MM-DD>"},),  # o ({},) si no acepta fecha
),
```

**Lo que `_validate()` te asegura gratis** (falla al importar):

- `id` igual a la key del dict · el `name` sin sufijo `_vN`
- `description` y `usage_notes` no vacíos · `examples` no vacío
- nombre MCP único · ruta `(method, path)` única
- `roles` no vacíos y ⊆ `KNOWN_ROLES`

**Lo que NO valida:** que `rest_path` esté montada en `app.py`, ni que la tool exista.
Eso lo cubren `test_registro_y_openapi_coinciden` y `test_list_tools_*`.

> **Si el dominio es nuevo**, conviene declarar una constante de roles al lado de las
> existentes (`CONTABILIDAD_ROLES`, `PACIENTES_ROLES`) con el comentario de por qué
> esos roles y no otros. Ese comentario es lo único que explica la decisión.

---

# PASO 2 · Contratos Pydantic

**Archivo:** `application/<dominio>/models.py`

Tres modelos: entrada, item de fila, salida. **Todas las descripciones de campo son
obligatorias**: son lo que lee el agente.

```python
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class Consultar<Nombre>Input(BaseModel):
    fecha: date = Field(
        ...,
        description="Fecha obligatoria (YYYY-MM-DD). <Por qué la exige el legacy.>",
    )
```

```python
class <Nombre>Item(BaseModel):
    <campo>: str = Field(..., description="<Qué es y de qué columna/macro sale.>")
    cantidad: int
    monto: Decimal
```

```python
class Consultar<Nombre>Output(BaseModel):
    fecha: date
    items: list[<Nombre>Item] = Field(
        ..., description="<Qué filas trae, en qué orden, y qué NO aparecen.>"
    )
    total_cantidad: int
    total_monto: Decimal
```

### Tipos

| Dato | Tipo | Por qué |
|---|---|---|
| Montos | `Decimal` | `float` introduce error de redondeo en plata. En el payload MCP salen como `str(...)` |
| Fechas | `date` | Pydantic valida formato y serializa a ISO |
| Conteos | `int` | — |
| Categorías del maestro | `str` crudo | `prevision` son literales de `TIPO_PREVISION`: no los consolides ni los interpretes |
| Semántica que se puede leer mal | `Literal[...]` | Ver el campo `base` de la ficha #7 |

### Si la consulta no tiene filtros

El input existe **aunque esté vacío**, con `extra="forbid"`:

```python
from pydantic import BaseModel, ConfigDict


class Consultar<Nombre>Input(BaseModel):
    """Contrato de entrada vacío: la consulta no admite ningún parámetro."""

    model_config = ConfigDict(extra="forbid")
```

`extra="forbid"` es lo que hace que cualquier argumento futuro sea un **error
explícito** y no un parámetro ignorado en silencio.

### Semántica hecha dato

Si el payload admite una lectura equivocada, agregá el campo que la cierra. El
ejemplo canónico: `base: Literal["pacientes_con_direccion_vigente"]` e
`incluye_pacientes_no_activos: True`, para que el agente no reporte 2.307 pacientes
activos cuando son 340.

---

# PASO 3 · Puerto de persistencia

**Archivo:** `application/<dominio>/ports.py`

Un `NamedTuple` por forma de fila y **un método abstracto por consulta**. El docstring
del `NamedTuple` explica qué es crudo y qué lo arma.

```python
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import NamedTuple


class <Nombre>Row(NamedTuple):
    """Fila de <Q<n>>. ``x`` es lo que entrega el SQL tal cual; ``y`` lo arma el service."""

    x: str
    cantidad: int
    monto: Decimal


class <Dominio>Port(ABC):
    """Puerto de persistencia del bloque <Dominio> (V2 R15)."""

    @abstractmethod
    def <nombre_snake>(self, fecha: date) -> list[<Nombre>Row]:
        """<Qué agrupa el SQL, con qué filtro de fecha y qué estados incluye.>"""
```

- **Sin filtro:** el método no lleva parámetro — `def pacientes_por_ciudad_chile(self)`.
- **Una fila o cero** (como `deuda_del_mes`): el retorno es `<Row> | None` y el `None`
  significa «el legacy omite la fila», **no** «cero».

---

# PASO 4 · SQL y repository · el paso donde más se falla

**Archivo:** `infrastructure/oracle/<dominio>_repository.py`

## 4.1 La constante y su comentario

El comentario es parte del contrato. Es lo único que explica por qué esa query y no
una "mejorada".

```python
# <Q<n>> · <Clase.método>  ·  fuente: <ruta:líneas>
#
# <POR QUÉ esta query es esta y no una "mejorada"> — V2 §0.1: no innovar.
#
# Decisiones del legacy que se replican tal cual:
#   1. <filtro de fecha: banda horaria 00:00:00–23:59:59, igualdad exacta, o trunc>
#   2. <estados incluidos: ACT, o ANU/DEV/NCI, o ninguno>
#   3. <unión con la réplica DENT_CICLO, o por qué no aplica>
#   4. <agrupación por columna real>
#   5. <lo que el legacy NO filtra y esta query tampoco>
<QXN>_SQL = """
select ...
from DENT.<tabla> bo
where bo.FEC_BOL >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
  and bo.FEC_BOL <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
  and bo.ind_estado = 'ACT'
group by <columna real>
"""
```

## 4.2 Checklist del SQL

- [ ] **Bind parameters**, nunca concatenación: `:fecha`, `:periodo`, `:origen`.
      El legacy concatena y es vulnerable (V2 `encuentros.md` §5). Parametrizar.
- [ ] **Owner explícito siempre**: `DENT.boleta`, `DENT_CICLO.boleta`.
- [ ] **Nunca** `USURUT`, `USULOGIN`, `password` en el `select`. `USULOGIN` es llave
      de join y no viaja.
- [ ] **`group by` por la columna real, no por el alias del `select`** → `ORA-00904`.
- [ ] **Banda horaria o igualdad exacta, según el legacy.** No "normalizar" a
      `trunc()` ni a `between`. En QA hay 163.369 boletas a medianoche y 8.553 con
      hora: la diferencia es material, no cosmética.
- [ ] **Réplica `DENT_CICLO`:** si la query original la une, se conserva el
      `union all` completo. Hoy tiene 0 filas, pero quitarlo rompe la paridad mañana.
- [ ] **`count(distinct ...)`** si un join puede duplicar filas.
- [ ] **Nada de cláusulas de escritura.** `test_todas_las_consultas_son_select_y_no_modifican`
      lo exige de todas las queries.

## 4.3 El repository

```python
class <Dominio>Repository(<Dominio>Port):
    """Adapter Oracle del bloque <Dominio>."""

    <QXN>_SQL = <QXN>_SQL   # atributo de clase: lo lee test_repository_sql.py

    def __init__(self, pool: oracledb.ConnectionPool | None = None):
        self._pool = pool

    @property
    def pool(self) -> oracledb.ConnectionPool:
        return self._pool or get_pool()   # lazy: la suite corre sin DSN

    def _fetchall(self, sql: str, **binds):
        """Traduce cualquier fallo a UNAVAILABLE: una caída de Oracle no puede
        disfrazarse de 'tabla vacía' (V2 R18)."""
        try:
            with self.pool.acquire() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, **binds)
                    return cur.fetchall()
        except Exception as exc:
            raise InfrastructureError() from exc

    def <nombre_snake>(self, fecha: date) -> list[<Nombre>Row]:
        filas = self._fetchall(self.<QXN>_SQL, fecha=fecha.isoformat())
        return [
            <Nombre>Row(
                x="" if r[0] is None else str(r[0]),   # un None se serializa como "None"
                cantidad=int(r[1]),
                monto=Decimal(r[2]),
            )
            for r in filas
        ]
```

**El `_fetchall` se copia tal cual.** Es el único lugar donde un fallo de infra se
convierte en `UNAVAILABLE`. Reimplementarlo distinto rompe R8.

Reglas del repository:

- **`pool.acquire()`, nunca crear/conexión por request.** El pool lo crea el lifespan
  (`database.create_pool()` en `app.py`).
- El property con fallback a `get_pool()` es lo que permite que la suite corra sin
  `.env`: los tests de unitario tocan el atributo `pool` con un `property` falso.
- Exponé la constante SQL **también como atributo de clase**, porque
  `tests/test_repository_sql.py` la levanta por ese nombre.

---

# PASO 5 · Service · acá vive el negocio, no el SQL

**Archivo:** `application/<dominio>/service.py`

```python
from datetime import date
from decimal import Decimal

from pydantic import ValidationError as PydanticValidationError

from application.errors import NotFoundError, ValidationError


class <Dominio>Service:
    def __init__(self, repo: <Dominio>Port):
        self.repo = repo

    def consultar_<nombre_snake>(self, fecha) -> Consultar<Nombre>Output:
        try:
            entrada = Consultar<Nombre>Input(fecha=fecha)
        except PydanticValidationError as exc:
            raise ValidationError("fecha es obligatoria y debe ser YYYY-MM-DD.") from exc

        rows = self.repo.<nombre_snake>(entrada.fecha)

        if not rows:
            raise NotFoundError(
                "No hay <qué> para <fecha>. Resultado válido, no es un fallo."
            )

        # Orden: ver la lista de decisiones abajo.
        items = [<Nombre>Item(x=r.x, cantidad=r.cantidad, monto=r.monto) for r in rows]

        return Consultar<Nombre>Output(
            fecha=entrada.fecha,
            items=items,
            total_cantidad=sum(i.cantidad for i in items),
            total_monto=sum((i.monto for i in items), Decimal("0.00")),
        )
```

### Decisiones que hay que justificar en un comentario

1. **Ordenar o no.** Si el SQL no garantiza orden, fijá uno estable y documentalo.
   Pero **si el SQL ya trae un orden total, no reordenes en Python**: el contrato
   quedaría dependiendo del `NLS_SORT` de Oracle en vez del texto original. La
   ficha #7 tiene el test `test_no_reordena_una_entrada_desordenada` que fija ese
   criterio.
2. **Filas ausentes ≠ cero.** Si el legacy omite un mes/ficha sin datos, se omite.
   Ponerlo en cero es inventar un dato.
3. **No repliques bugs de presentación**: el `resp.size()` de Java, el
   `round(avg(...),0)` que después formatea el `DecimalFormat` del HTML. La paridad es
   sobre el **valor numérico**, no sobre el texto formateado.
4. **Mapeos de código a etiqueta.** Si el legacy los hace en SQL para un canal y no
   para otro, aplicá el mapeo **para los tres** en la capa y exponé el valor crudo en
   un campo aparte (`codigo_tarjeta` + `etiqueta_correo`).
5. **Bucles, no queries mágicas.** Si el legacy hace 4 ejecuciones, la capa hace 4
   viajes. No se colapsa a un `RANGE` (V2 §0.3).
6. **El orden total que sí conviene preservar** es el que el `ORDER BY` ya resuelve:
   en ese caso el `sorted()` de Python no aporta nada y solo agrega una dependencia.

---

# PASO 6 · Adapter REST

**Archivo:** `adapters/rest/<dominio>.py`

```python
from datetime import date

from fastapi import APIRouter, Depends, Query

from application.<dominio>.models import Consultar<Nombre>Output
from composition import <dominio>_service
from security import require_contract

router = APIRouter(prefix="/api/<dominio>", tags=["<dominio>"])


@router.get(
    "/<kebab-case>",
    response_model=Consultar<Nombre>Output,
    summary="<mismo title que el registry>",
)
def consultar_<nombre_snake>(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    identity: dict = Depends(require_contract("<dominio>.<nombre_snake>")),
):
    """<Qué reproduce + la advertencia semántica clave.>"""
    return <dominio>_service.consultar_<nombre_snake>(fecha)
```

- **Sin parámetros** (variante #7): no hay ningún `Query`, solo el `Depends` y el
  `return` sin argumentos.
- `require_contract("<id>")` toma los roles **del registry**. No copies la lista de
  roles a mano: se desincroniza.
- El `summary` y el `title` del registry son el mismo string.
- `identity` no se usa en el cuerpo. Está por la dependencia; no lo borres.

## PASO 6b · Montaje (solo si el dominio es NUEVO)

`composition.py` — el único lugar donde se instancian adapters concretos:

```python
<dominio>_repository = <Dominio>Repository()
<dominio>_service = <Dominio>Service(<dominio>_repository)
```

`app.py`:

```python
from adapters.rest.<dominio> import router as <dominio>_router
from adapters.mcp import <dominio>          # noqa: F401 · importa por efecto
...
app.include_router(<dominio>_router)
```

> **Nunca** construir el service dentro del router o de la tool. REST y MCP resuelven
> el **mismo objeto**: si construyeran dos, la lógica podría divergir sin que nada lo
> detecte, y el pool sería doble.

---

# PASO 7 · Adapter MCP

**Archivo:** `adapters/mcp/<dominio>.py`

```python
from mcp.server.fastmcp import Context

from adapters.mcp.server import FechaArg, _json, _run, _tool, mcp
from composition import <dominio>_service

T = "<dominio>.<nombre_snake>"


@mcp.tool(**_tool(T, "<mismo title que el registry>"))
def consultar_<nombre_snake>(fecha: FechaArg, ctx: Context) -> str:
    """<Una línea. La descripción que ve el agente la publica el registry.>"""
    out = _run(T, ctx, <dominio>_service.consultar_<nombre_snake>, fecha)
    return _json(
        {
            "fecha": out.fecha.isoformat(),
            "items": [
                {"x": i.x, "cantidad": i.cantidad, "monto": str(i.monto)}
                for i in out.items
            ],
            "total_cantidad": out.total_cantidad,
            "total_monto": str(out.total_monto),
        }
    )
```

**Sin argumentos** (variante #7): la firma es `(ctx: Context)` y `_run(...)` se llama
sin extras.

### Lo que hay que saber

- **`from mcp.server.fastmcp import Context`, jamás `from fastmcp import ...`.** No
  instales el paquete standalone `fastmcp`: es incompatible con `mcp` 1.30.
- **`_tool(id, title)`** arma `annotations` + `description` desde el registry. No los
  escribas a mano: quedarían mintiendo cuando cambie el modo.
- **`_run(id, ctx, fn, *args)`** autoriza, ejecuta y traduce `DomainError` a
  `RuntimeError("[CODE] mensaje")` → FastMCP lo publica como `isError: true`. No
  reimplementes ese `try/except`.
- **`_json(payload)`** es `json.dumps(..., ensure_ascii=False, default=str)`: los
  `Decimal` salen sin más.
- **El schema MCP sale de la firma de la función**, no del modelo Pydantic. Para que
  el agente sepa el formato de un parámetro, usá un `Annotated` tipado. Ya existen
  `FechaArg` y `OrigenArg` en `adapters/mcp/server.py`; **para un filtro nuevo,
  agregá el tuyo ahí**, al lado de ellos, y usalo como tipo en la firma. Un
  `fecha: str` pelado no le dice nada al agente.
- **Las tools se registran sobre el `FastMCP` compartido** de `adapters/mcp/server.py`.
  Nunca crear un `FastMCP` por dominio.

---

# PASO 8 · Tests

## 8.1 Lo que hay que declarar al agregar la capability

`tests/test_registry.py`:

```python
# En CON_FECHA o en SIN_ARGUMENTOS, no en los dos.
CON_FECHA = (
    ...,
    "<dominio>.<nombre_snake>",
)
```

Si no lo hacés, `test_toda_capability_declara_si_toma_argumentos` falla con la lista de
«sin declarar». **No** pongas el id en `SIN_ARGUMENTOS` si toma `fecha`: caerías en el
mismo problema de la sección H2.

## 8.2 Qué agrega cada suite

| Suite | Qué agregar | Obligatorio |
|---|---|---|
| `tests/test_registry.py` | Id declarado en la forma de entrada · el resto de tests están parametrizados sobre `CAPABILITIES` y no requieren nada | Sí |
| `tests/test_contracts.py` | Tupla `(ruta, params)` en `ENDPOINTS` · prefijo en `REPO_POR_PATH` (para el test de Oracle caído) | Sí |
| `tests/test_repository_sql.py` | Guardas de fidelidad, ver 8.3 | Sí |
| `tests/test_service_<dominio>.py` | Suite propia si el dominio es nuevo; si es contabilidad, extendé `test_service.py` | Sí |
| `tests/test_paridad_oracle.py` | Nivel 0, ver paso 9 | Sí |

**Si la capability excluye a `contador`**, los tests que usan `TOKEN` (contador) te van
a dar **403, no 503**. Usá `TOKEN_COMUN` (gerente) para esos casos.

**La trampa del `!= 403`:** `test_los_tres_roles_de_pacientes_pueden_acceder` afirma
`!= 401` **y** `!= 403`. Un `!= 403` solo pasa con un `401` y no prueba nada.

## 8.3 Guardas de fidelidad SQL (tests/test_repository_sql.py)

- Usa bind: el parámetro está y el conteo de ocurrencias coincide con los usos.
- Owner explícito en toda tabla.
- **No** selecciona `USURUT` / `USULOGIN`.
- No concatena la entrada (ningún `|| :param` ni f-string en el SQL).
- Los filtros clave del legacy están: banda horaria / igualdad exacta / estados.
- `group by` por columna real, no por alias.
- `select` sin cláusula de escritura.

## 8.4 Suite de service (tests/test_service_<dominio>.py)

Con un `FakeRepo` que implemente el puerto:

- Mapeo de `Row` a item de contrato.
- Orden canónico; y si el SQL ya ordena, que **no** reordene.
- Totales calculados por el service.
- `NO_DATA` (`NotFoundError`) con repo vacío.
- `INVALID_ARGUMENT` (`ValidationError`) con entrada mal formada.
- **Una sola** llamada al repo.
- El service no acepta argumentos no declarados.
- Se preservan los literales crudos del maestro (no se "corrige" `SAN JOSE DE MA`).

---

# PASO 9 · Paridad Nivel 0

**Archivo:** `tests/test_paridad_oracle.py`

El test se salta solo si no hay pool, así que la suite sigue verde sin BD; con DSN
configurado **exige conexión real**.

### Dos variantes

| Variante | Cuándo | Qué se verifica |
|---|---|---|
| **Golden file** | Corte del día (los datos de una fecha no cambian) | Los números igualan los de la fuente para **una fecha con datos** y **una sin actividad** |
| **Comparación** | Censo que cambia con cada registro | El service iguala fila por fila el mismo SQL corrido a mano + invariantes |

### Reglas del diff (V2 §12)

1. **Números crudos**, no el texto formateado con `DecimalFormat` del HTML.
2. **Contra la fuente real** (el correo que ve la gerencia), no contra la query
   re-ejecutada.
3. `NO_DATA` es válido; `UNAVAILABLE` no.
4. **Fecha siempre explícita.** Nunca vacía.

Invariantes útiles para la variante por comparación:

```python
def test_coincide_con_el_sql_de_la_fuente(oracle): ...
def test_rest_devuelve_los_mismos_numeros(client, oracle): ...
def test_suma_coherente_con_las_filas(client, oracle): ...
def test_orden_estable(client, oracle): ...
def test_incluye_los_estados_que_el_legacy_no_excluye(client, oracle): ...
```

**Nunca fijes números de un censo como golden file**: se rompen con el próximo registro
y alguien va a "arreglar" el código.

---

# PASO 10 · Ficha de la capacidad (16 secciones)

**Archivo:** `docs/refactorizacion/capacidades/<nombre_snake>.md`

| # | Sección | Qué no puede faltar |
|---|---|---|
| 1 | Identidad del contrato | `id`, `version`, `name`, `mode` |
| 2 | Propósito | Qué hace + **cuándo NO usarla** |
| 3 | Proyección MCP | Annotations derivadas, tabla de input/output, y los campos que cierran lecturas equivocadas |
| 4 | Proyección REST | Método, path, tabla de códigos HTTP, y por qué **no** hay 400 si no hay args |
| 5 | Modo de ejecución | Diagrama de secuencia + las 4 reglas de la capa |
| 6 | Query incluida | El SQL + **tabla de decisiones replicadas (h1, h2, …)** + diferencias deliberadas vs el legacy más cercano |
| 7 | Reglas de negocio | Lista YAML de las reglas que la capa impone |
| 8 | Contrato Pydantic | Los tres modelos + por qué existen |
| 9 | Datos y gobernanza | `profile`, `sources`, `classification`, `pii`, `allowed_fields`, `forbidden_fields` + la mitigación si agregás rareza |
| 10 | Seguridad | `roles` + **por qué** esos y no otros |
| 11 | Errores | Tabla error → `error_code` → HTTP → mensaje. Y por qué `NO_DATA` ≠ `UNAVAILABLE` |
| 12 | Observabilidad | Qué metadatos se registran y **qué no** (minimización) |
| 13 | Paridad | Qué se verificó, con qué criterio de aceptación |
| 14 | Ejemplos | Input y output real (recortado) |
| 15 | Trazabilidad técnica | Fuente normativa · `oracle_sql_id` · archivos tocados · tests |
| 16 | Referencias | V2, CATALOGO, arquitectura, fuente legacy |

> **Sobre `allowed_fields` / `forbidden_fields` (sección 9):** ver H5. Se escriben igual,
> sabiendo que hoy no los testea nada.

---

# PASO 11 · Catálogo y documentación

- [ ] `capacidades/CATALOGO.md`: fila en la tabla del bloque, entrada en "Cómo elegir
      una capability", advertencia de interpretación si tiene una lectura engañosa, y
      actualización del conteo de tests y de capabilities del encabezado.
      **`test_catalogo_documenta_todas_las_capabilities` falla si falta la fila.**
- [ ] `arquitectura.md` §10 — solo si agregaste un dominio o un rol.
- [ ] `README.md` y `arquitectura.md` — si anuncian un número de tools.
- [ ] `analsismcp.html` — si es de cara a gerencia.

---

# PASO 12 · Definition of Done

- [ ] `pytest -q` verde, **240 o más**. Anotá el número nuevo en `CATALOGO.md`.
- [ ] Paridad viva contra Oracle para la fecha elegida, o por comparación si es censo.
- [ ] Reiniciá el server y verificá que la tool aparece.
- [ ] Probá la tool desde el cliente MCP real, no sólo por REST. El contrato es para
      el agente.
- [ ] Ficha de 16 secciones + `CATALOGO.md` actualizados.
- [ ] Si publica datos sensibles: nota de PII en la ficha **y** en el `usage_notes` que
      ve el agente.
- [ ] `arquitectura.md` §10.1 sin pendientes nuevos.

---

# Errores que ya pagamos una vez

### Oracle / SQL

- **Alias del `select` en el `group by` → `ORA-00904`.** Agrupá por la columna real.
- **`=` vs `trunc()` vs banda horaria.** Respetá la semántica del legacy por capability.
- **`None` de una columna nullable** se serializa como `"None"` en el payload del
  agente. Defendete en el repository: `"" if r[0] is None else str(r[0])`.
- **`create_pool()` no traduce `ORA-12154` de arranque**, sólo los fallos de consulta
  → 503. Y el DSN sale de `tnsnames.ora` del Instant Client: si el alias no está,
  falla todo el Nivel 0 con `ORA-12154`.

### Python / framework

- **No instalar `fastmcp`.** El server usa `mcp.server.fastmcp`.
- **`FastMCP(..., streamable_http_path="/")`** + lifespan del sub-app dentro del de
  FastAPI + fixture `client` **session-scoped** (el session manager solo admite un
  lifespan por proceso).
- **`os.environ.setdefault` en `conftest.py` no alcanza para los tokens**: si el shell
  tiene exportado un `AUTH_TOKEN_*` real, `setdefault` no sobreescribe y la suite queda
  autenticada con el token de producción. **Asigná**.
- **El `pool` del repository tiene que ser lazy** (`self._pool or get_pool()`) para que
  la suite corra sin DSN.

### Proceso

- **Reiniciar el server** después de cambiar código.
- **Ver H1**: los mensajes de 400 armados a mano en el service pueden nombrar campos
  que no fallaron.

---

# Referencias

| Documento | Qué da |
|---|---|
| [`consultar_pacientes_por_ciudad_chile.md`](./consultar_pacientes_por_ciudad_chile.md) | Implementación más reciente, sin `fecha`, dominio nuevo, rol propio. **Leerla primero.** |
| [`consultar_ingresos_por_tipo_pago.md`](./consultar_ingresos_por_tipo_pago.md) | Ficha de 16 secciones con `fecha` |
| [`CATALOGO.md`](./CATALOGO.md) | Las 7 existentes + errores de interpretación conocidos |
| [`../000_MiEstrategiaV2.md`](../000_MiEstrategiaV2.md) | R1–R20, §7 errores, §12 testing, §19 hallazgos |
| [`../arquitectura.md`](../arquitectura.md) | Pool, Bearer, composition root, config de clientes |
| [`../../go/encuentros.md`](../../go/encuentros.md) | **Las queries normativas** de Agenda, Funcionarios, Notas, Becas y Convenios |
| [`../estado_de_sesion_2026-10-02-B.md`](../estado_de_sesion_2026-10-02-B.md) §9 | Receta histórica de 10 pasos con la que se construyó el bloque contable |
| [`_plantilla/`](./_plantilla/) | Esqueleto de archivos con marcadores TODO |
