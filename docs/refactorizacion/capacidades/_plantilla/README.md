# `_plantilla/` · esqueleto de una capability READ

Archivos con marcadores `TODO` para copiar, renombrar y llenar. Van con sufijo
`.example` a propósito: pytest colecta desde el rootdir y no hay `pytest.ini` con
`testpaths`, así que un `.py` con TODOs dentro de `docs/` rompería la suite en cuanto
alguien corriera `pytest` desde el directorio madre.

**Se usa con la plantilla, no en su lugar:**
[`../PLANTILLA_CAPACIDAD.md`](../PLANTILLA_CAPACIDAD.md).

---

## Cómo

### 1. Llenar el encargo

Sección 2 de la plantilla. El `nombre_snake` y el `dominio` deciden los nombres de
todos los archivos de abajo.

### 2. Determinar si es dominio existente o nuevo

| | Dominio existente | Dominio nuevo |
|---|---|---|
| Carpeta | se agrega al directorio ya existente | se crea `application/<dominio>/` con `__init__.py` |
| Repository | ya existe | se crea |
| `composition.py` | no se toca | hay que instanciar repo + service |
| `app.py` | no se toca | `include_router` + `import` por efecto del adapter MCP |
| Suite de service | se extiende `test_service.py` o la del dominio | se crea `test_service_<dominio>.py` |
| `test_contracts.py` | sí, siempre | sí, siempre |
| `test_repository_sql.py` | sí, siempre | sí, siempre |

### 3. Copiar y renombrar

```sh
D=application/<dominio>
N=consultar_<nombre_snake>
mkdir -p $D

cp _plantilla/models.py.example     $D/models.py
cp _plantilla/ports.py.example      $D/ports.py
cp _plantilla/service.py.example    $D/service.py
cp _plantilla/repository.py.example infrastructure/oracle/<dominio>_repository.py
cp _plantilla/rest.py.example       adapters/rest/<dominio>.py
cp _plantilla/mcp.py.example        adapters/mcp/<dominio>.py
cp _plantilla/test_service.py.example tests/test_service_<dominio>.py

open _plantilla/registry_entry.py.example   # pegar en application/registry.py
open _plantilla/FICHA.md.example            # escribir la ficha
```

### 4. Reemplazar los marcadores

Todos los `TODO` están en mayúsculas. Al final del recorrido no debe quedar ninguno:

```sh
grep -rn "TODO" application/<dominio> infrastructure/oracle/<dominio>_repository.py \
     adapters/rest/<dominio>.py adapters/mcp/<dominio>.py tests/
```

### 5. Ejecutar los pasos 1 a 12 de la plantilla

El orden importa: **registro primero**, antes de nada, porque `_validate()` falla al
importar y es tu primer test gratis.

---

## Qué tapa cada archivo

| Archivo | Paso | A dónde va |
|---|---|---|
| `registry_entry.py.example` | 1 | bloque pegado en `application/registry.py` |
| `models.py.example` | 2 | `application/<dominio>/models.py` |
| `ports.py.example` | 3 | `application/<dominio>/ports.py` |
| `repository.py.example` | 4 | `infrastructure/oracle/<dominio>_repository.py` |
| `service.py.example` | 5 | `application/<dominio>/service.py` |
| `rest.py.example` | 6 | `adapters/rest/<dominio>.py` |
| `mcp.py.example` | 7 | `adapters/mcp/<dominio>.py` |
| `test_service.py.example` | 8 | `tests/test_service_<dominio>.py` |
| `FICHA.md.example` | 10 | `docs/refactorizacion/capacidades/<nombre_snake>.md` |

Los pasos 8–9 (tests de contracts, repository y paridad) **no** tienen esqueleto: se
extienden archivos que ya existen y las guardas concretas dependen de la query.

---

## Reglas que no están en los esqueleto pero que la suite te va a exigir

- El id tiene que entrar en `CON_FECHA` o en `SIN_ARGUMENTOS` de
  `tests/test_registry.py`.
- La `name` del contrato tiene que aparecer en `CATALOGO.md`, o
  `test_catalogo_documenta_todas_las_capabilities` falla.
- La ruta REST tiene que ir en `ENDPOINTS` y su prefijo en `REPO_POR_PATH` de
  `tests/test_contracts.py`.
- Si el dominio es nuevo, el import del adapter MCP va en `app.py` con
  `# noqa: F401`: no hay que confiar en que alguien lo recuerde a mano.
