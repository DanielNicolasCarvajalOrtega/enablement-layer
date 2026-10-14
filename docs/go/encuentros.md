# Reportes por correo: qué programa los genera y con qué SQL

Fecha de análisis: 2026-09-25
Fuentes: corpus `vault/dosier/docs/**/*RICH.md` + código físico en
`/Users/fernandosalvo/Desktop/ino/assesstment/app/DentWeb12_Java21`

## Resumen ejecutivo

| Correo (asunto) | Programa | Estado de la evidencia | MCP |
|---|---|---|---|
| `Resumen Procesos` | Ninguno en Java/JSP. Solo se escribe en `MAIL_AVISO`; el lector no está en el corpus | **Inferido** | Fuera de alcance (por ahora) |
| `Resumen Control (Agenda)` | `ConsultaControl` + `ResumenControl` | Confirmado (contenido) / Inferido (asunto) | **Pendiente MCP correo (Agenda)** |
| `Resumen Control (Contable)` | `ConsultaControl` + `ResumenControl` | Confirmado (contenido) / Inferido (asunto) | MCP implementado |
| `Resumen Control (Funcionarios)` | `ConsultaControl` + `ResumenControl` | Confirmado (contenido) / Inferido (asunto) | **Pendiente MCP correo (Funcionarios)** |
| `Resumen Control (Notas)` | `ConsultaControl` + `ResumenControl` | Confirmado (contenido) / Inferido (asunto) | **Pendiente MCP correo (Notas)** |
| `Resumen Control (becas y convenios)` | `rptBecas.jsp` + `rptConvenios.jsp` + `rptConveniosMensual.jsp` | Confirmado (contenido) / Inferido (asunto) | **Pendiente MCP correo (Becas y convenios)** |

> **Leyenda de marcas MCP** (este archivo es input para implementar MCP + plantilla):
> - **Pendiente MCP correo (X)** → las queries de esa sección aún no están implementadas como capability MCP.
> - **MCP implementado** → ya existen capabilities (ver `docs/refactorizacion/capacidades/CATALOGO.md`).
> - **Fuera de alcance (por ahora)** → no se implementará en esta tanda.

**Hallazgo central:** ninguno de los seis correos se envía desde este código. El
código solo *construye* el contenido (HTML) y, en el caso de procesos, *deja
registro* en una tabla (`MAIL_AVISO`). El proceso que arma y despacha los correos
no está en el corpus Java/JSP: es un job externo (scheduler, cron o agente
propio). Ver "Ausencias" al final.

---

## Pendientes para implementar como MCP

Queries a portar (marca `Pendiente MCP correo (...)` en los títulos). Una
capability por query salvo que se indique lo contrario.

**Correo (Agenda)** — 3 queries
- [ ] Estado de citas día — `ResumenControl.setTablaAgendaHoy` (`ResumenControl.java:320`)
- [ ] Pacientes agendados mañana — `setTablaAgendaManana` (`:229`)
- [ ] Citas por tipo previsión — `getCitasPorTipoPrevision` (`:716`)

**Correo (Funcionarios)** — 4 queries (+1 condicional)
- [ ] Rendimiento asistentes — `setTablaRendimientoAst` (`:381`)
- [ ] Informes impresos por doctor — `getImpresoInformePorDoc` (`:779`)
- [ ] Productos usados por doctor — `getUsoProductoPorDoc` (`:817`)
- [ ] Detalle de acciones — `getAccionesPorTipoAccion` (`:452`)
- [ ] *(condicional, `chk_det=ON`)* Detalle de acciones por asistente — `getAccionesPorTipoAccionAsistentes` (`:480`)

**Correo (Notas)** — 1 query (2 invocaciones)
- [ ] Notas administrativas y de doctores — `getNotas` (`:752`), con `OBS_TIPO` `ADMINISTRADOR` y `DOCTOR`

**Correo (Becas y convenios)** — 3 queries (una por tabla del correo)
- [ ] Reporte Becas (detalle) — `rptBecas.jsp` (`:346`, `idUnidad=3`)
- [ ] Reporte Convenios (detalle) — `rptConvenios.jsp` (`:300`)
- [ ] Reporte Convenios Últimos 6 Meses — `rptConveniosMensual.jsp` (`:62` cabecera, `:80` datos)

> Procesos: fuera de alcance por ahora (lector externo, no en el corpus).

---

## 1. `Resumen Procesos`

### 1.1 Lo que sí existe

`MaestroProceso.logResumen()` escribe el detalle de ejecución en `MAIL_AVISO`.

`src/cl/llm/dent/MaestroProceso.java:154-167`
```java
public void logResumen(int idProceso, String descrip, int cantidad){
    //query oracle
    String query ="insert into MAIL_AVISO values("+idProceso
        +",to_date(to_char(sysdate,'YYYY-MM-DD'),'YYYY-MM-DD')"
        +",to_char(sysdate,'HH24:MI:SS')"
        +",'"+descrip+"',"+cantidad+")";
    String strRsp = cns1.insDelUpdQuery(query);
}
```

El comentario del método (línea 149) lo dice explícitamente:
> `Registra detalle de la ejecucion que sera enviado x mail y visible web`

Los 4 datos del INSERT corresponden 1:1 con las columnas de la tabla y con las
columnas del correo (`Fecha | Hora | Proceso | Cantidad`):

| Correo | `MAIL_AVISO` | Origen del valor |
|---|---|---|
| Fecha | `AVI_FECHA` | `to_char(sysdate,'YYYY-MM-DD')` |
| Hora | `AVI_HORA` | `to_char(sysdate,'HH24:MI:SS')` |
| Proceso | `AVI_DESCRIP` | parámetro `descrip` |
| Cantidad | `AVI_CANTIDAD` | parámetro `cantidad` |

Nota: el primer valor del INSERT es `idProceso`, no la descripción. La columna
`AVI_ID` es la PK. Para que la columna "Proceso" del correo muestre el nombre
del proceso (ej. "Actualiza Injustificados") el lector externo debe resolver
`MAIL_AVISO.AVI_ID` contra `PROCESOS.PRC_NOMBRE`/`PRC_DSC`.

Esquema de `MAIL_AVISO` (`vault/dosier/docs/raw_db_metadata/columns.json:10894-10949`):
`AVI_ID`, `AVI_FECHA`, `AVI_HORA`, `AVI_DESCRIP`, `AVI_CANTIDAD`. PK `PK_MAIL_AVISO`.

### 1.2 Lo que NO existe

- No hay ningún `SELECT ... FROM MAIL_AVISO` en Java ni JSP. Verificado con grep
  sobre `*.java` y `*.jsp` de todo el proyecto.
- La búsqueda literal de `Resumen Procesos` (como asunto) en los 1.101
  documentos del corpus y en el código fuente no arroja resultados.
- `docs/llm/dent/maestroprocesoRICH.md:476` ya lo decía:
  > "No se documenta en el código qué proceso consume/envía los registros de MAIL_AVISO.
  > Se asume que existe un batch o scheduler externo que procesa esta tabla."

**Conclusión:** `Resumen Procesos` es el correo que arma un componente externo a
partir de `MAIL_AVISO`. El productor de los datos está identificado
(`MaestroProceso.logResumen`, y el equivalente PL/SQL
`PACK_PROCESOS_BATCH.PROC_REGISTRA_DET_EJECUCION`); el consumidor del correo no
está en el corpus.

### 1.3 Otros escritores de `MAIL_AVISO`

| Productor | Ubicación | Qué escribe |
|---|---|---|
| Java | `MaestroProceso.logResumen` — `src/cl/llm/dent/MaestroProceso.java:160` | INSERT directo |
| PL/SQL | `PACK_PROCESOS_BATCH.PROC_REGISTRA_DET_EJECUCION` — `source_code.json`, líneas 35-39 | INSERT (cuerpo no capturado, solo la firma) |

Firma PL/SQL (`vault/dosier/docs/raw_db_metadata/source_code.json`):
```sql
PROCEDURE PROC_REGISTRA_DET_EJECUCION(
    v_id_proceso  IN mail_aviso.avi_id%TYPE,
    v_descripcion IN mail_aviso.avi_descrip%TYPE,
    v_cantidad    IN mail_aviso.avi_cantidad%TYPE
);
```
Comentario en el paquete: *"Registra detalle de la ejecucion que sera enviado x
mail y visible web"*.

El paquete se confirma como dependencia de la tabla en
`raw_db_metadata/dependencies.json:2018-2024`.

---

## 2. `Resumen Control (Agenda)` / `(Contable)` / `(Funcionarios)` / `(Notas)`

### 2.1 El despachador

Un solo programa atende los cuatro: `ConsultaControl.verApp()` lee el parámetro
`TIPO_CONSULTA` y dibuja el grupo de tablas correspondiente.

`src/cl/llm/dent/ConsultaControl.java:67-72` — el combo define los 4 reportes:
```java
String[] strArr1 = {"Seleccionar...",
                    "1.Agenda",
                    "2.Contable",
                    "3.Funcionarios",
                    "4.Notas Internas"
                    };
```

| `TIPO_CONSULTA` | Etiqueta en código | Bloque del correo |
|---|---|---|
| `1` | `1.Agenda` | `Resumen Control (Agenda)` |
| `2` | `2.Contable` | `Resumen Control (Contable)` |
| `3` | `3.Funcionarios` | `Resumen Control (Funcionarios)` |
| `4` | `4.Notas Internas` | `Resumen Control (Notas)` |

Construcción del helper: `ConsultaControl.java:91`
```java
ResumenControl rc = new ResumenControl(fecha.fechaBD(fechaConsulta));
```

### 2.2 El título interno

`src/cl/llm/batch/ResumenControl.java:96-106`
```java
public void setTitulo() {
    Fechas fec = new Fechas();
    String fecha=fec.fechaActual();
    this.titulo = "Resumen Control "+fecha;
}

public void setTitulo(String subTipo) {
    Fechas fec = new Fechas();
    String fecha=fec.fechaActual();
    this.titulo = "Resumen Control ("+subTipo+") "+fecha;
}
```

**Importante:** el constructor (`ResumenControl.java:45-67`) solo invoca
`setTitulo()` sin subtipo, y `setTitulo(String)` **no tiene ningún llamador en
todo el código Java**. El campo `titulo` no se lee en ningún lado
(`getTitulo()` no tiene consumidores). Por lo tanto la cadena
`"Resumen Control (...)"` existe en el código como plantilla, pero el valor
concreto entre paréntesis lo inyecta el componente externo. El mapeo
`1→Agenda`, `2→Contable`... de la tabla anterior es coherente con la nomenclatura
del combo, pero es **inferencia**, no hecho.

---

### 2.3 SQL por reporte

Todas las consultas viven en `src/cl/llm/batch/ResumenControl.java`.

#### `(Agenda)` — `TIPO_CONSULTA=1` — **Pendiente MCP correo (Agenda)**

Consumidas en `ConsultaControl.java:117-176` (listas `rc.listAgendaHoy`,
`rc.listAgendaManana`) y `rc.getCitasPorTipoPrevision(...)` en la línea 155.

**a) Estado de citas del día** — `ResumenControl.setTablaAgendaHoy()` (`:320-324`)
```sql
select ind_estado, count(id_agenda) cantidad
from DENT.agenda
where fec_cita=to_date('<agno>-<mes>-<dia>','YYYY-MM-DD')
and cita_secuencia=1
group by ind_estado
```
Los estados se traducen con `ConstantesDent.EstadoCita` (`ResumenControl.java:341-349`):
`TERMINADA`→Terminada, `RESERVADA|INGRESADA`→Reservada, `RECEPCIONADA`→Recepcionada,
`INJUSTIFICADA`→Injustificada, `TEMPORAL`→Paciente Temporal, `ASIGNADA`→Asignado,
`SUSPENDIDA`→Suspendida, `DERIVADA`→Derivada.

**b) Pacientes agendados mañana** — `ResumenControl.setTablaAgendaManana()` (`:229-231`)
```sql
select count(id_agenda) cantidad
from DENT.agenda
where fec_cita=to_date(to_char(sysdate+1,'YYYY-MM-DD'),'YYYY-MM-DD')
and cita_secuencia=1
and ind_estado='RSV'
```

**c) Citas por tipo previsión** — `ResumenControl.getCitasPorTipoPrevision()` (`:716-724`)
```sql
select do.DOMIDESCRI, count(1)
from DENT.agenda ag, DENT.fichas fi, DENT.dominio do
where ag.FEC_CITA=to_date(<fechaCns>,'YYYY-MM-DD')
and ag.cita_secuencia=1
and ag.COD_PACIENTE = fi.NUM_FICHA
and fi.TIP_PREVISION = do.DOMICODIGO
and do.DOMINOMBRE = 'TIPO_PREVISION'
group by do.DOMIDESCRI
order by DOMIDESCRI
```

#### `(Contable)` — `TIPO_CONSULTA=2` — MCP implementado

Consumidas en `ConsultaControl.java:204-494`.

**a) Resumen deuda (4 meses)** — `ResumenControl.setTablaDeuda()` (`:284-287`)
```sql
select to_char(bat_fecha,'MM'), round(avg(bat_deuda),0) deuda
from DENT.bat_deuda
where to_char(bat_fecha,'YYYY-MM') = '<agno>-<mes>'
group by to_char(bat_fecha,'MM')
```
Se ejecuta en bucle 4 veces, retrocediendo mes (y año al cruzar diciembre).

**b) Ingresos por tipo pago** — `ResumenControl.setTablaIngresoPago()` (`:132-189`)
```sql
select NUM_DOCTO tipo_doc, sum(mto_bol) mto
from (
  select NUM_DOCTO, mto_bol from dent.boleta
  where fec_bol between <fecha> 00:00:00 and <fecha> 23:59:59
    and ind_estado in ('ACT') and id_impresora like 'IBM%'
  union all
  select NUM_DOCTO, mto_bol from dent_ciclo.boleta
  where ... and ind_estado in ('ACT') and id_impresora like 'IBM%'
  union all
  select 'WEBPAY' NUM_DOCTO, mto_bol from dent.boleta            where ... id_impresora='WPTN'
  union all
  select 'WEBPAY' NUM_DOCTO, mto_bol from dent_ciclo.boleta      where ... id_impresora='WPTN'
  union all
  select 'CAJA VECINA BCO.EST.' NUM_DOCTO, mto_bol from dent.boleta       where ... id_impresora='BESTA'
  union all
  select 'CAJA VECINA BCO.EST.' NUM_DOCTO, mto_bol from dent_ciclo.boleta where ... id_impresora='BESTA'
  union all
  select 'TOTEM' NUM_DOCTO, mto_bol from dent.boleta              where ... id_impresora like 'TOT%'
  union all
  select 'TOTEM' NUM_DOCTO, mto_bol from dent_ciclo.boleta        where ... id_impresora like 'TOT%'
) group by NUM_DOCTO
```
Mapeo de `NUM_DOCTO` a etiqueta (`:197-199`): `EFE`→CAJA-EFECTIVO,
`TRJ`→CAJA-TARJETA, `CHQ`→CAJA-CHEQUE.

**c) Ingresos por tipo de tarjeta** — `ResumenControl.getDetIngresPorTipoTarjeta()` (`:603-639`)
Se llama 3 veces con `origen` = `CAJA`, `TOTEM`, `WEBPAY`
(`ConsultaControl.java:269, 310, 350`). El sufijo del origen se inyecta en
`qryOrigen` (`:595-599`): `CAJA`→`id_impresora like 'IBM%'`,
`TOTEM`→`like 'TOT%'`, `WEBPAY`→`= 'WPTN'`.

Variante `CAJA` (`:603-621`):
```sql
select TIP_TARJETA, count(1), sum(MTO_BOL) from (
  select bo.TIP_TARJETA, bo.MTO_BOL from DENT.boleta bo
  where bo.FEC_BOL = to_date(<fechaCns>,'YYYY-MM-DD')
    and bo.NUM_DOCTO='TRJ' and bo.ind_estado='ACT'
    and bo.id_impresora like 'IBM%' and <qryOrigen>
  union all
  select bo.TIP_TARJETA, bo.MTO_BOL from dent_ciclo.boleta bo
  where ... mismos filtros ...
) group by TIP_TARJETA
```

Variante `TOTEM`/`WEBPAY` (`:623-639`): en vez de agrupar por `TIP_TARJETA`
crudo, decodifica los códigos de tarjeta a texto:
```sql
select decode(bo.TIP_TARJETA,'CRD1','CREDITO','DEB1','DEBITO',bo.TIP_TARJETA) tipo, ...
...
group by tipo
```

**d) Ingresos por tipo previsión** — `ResumenControl.getIngresoPorPrevision()` (`:668-688`)
```sql
select DOMIDESCRI, count(1), sum(MTO_BOL) from (
  select do.DOMIDESCRI, bo.MTO_BOL
  from boleta bo, fichas fi, dominio do
  where bo.fec_bol between <fecha> 00:00:00 and <fecha> 23:59:59
    and bo.NUM_FICHA=fi.NUM_FICHA and bo.ind_estado='ACT'
    and fi.TIP_PREVISION=do.DOMICODIGO and do.DOMINOMBRE='TIPO_PREVISION'
  union all
  select ... from dent_ciclo.boleta bo, fichas fi, dominio do where ...
) group by DOMIDESCRI order by DOMIDESCRI
```

**e) Boletas emitidas por usuario** — `ResumenControl.getBoletasPorUsuario()` (`:511-526`)
```sql
select USUAPEP, USUNOMC, count(1), sum(mto_bol) from (
  select us.USUAPEP, us.USUNOMC, mto_bol
  from boleta bo, usuarios us
  where bo.fec_bol between <fecha> 00:00:00 and <fecha> 23:59:59
    and bo.ind_estado='ACT' and bo.COD_USUARIO=us.USULOGIN
  union all
  select us.USUAPEP, us.USUNOMC, mto_bol
  from dent_ciclo.boleta bo, usuarios us where ...
) group by USUAPEP, USUNOMC
```

**f) Boletas anuladas por usuario** — `ResumenControl.getBoletasAnuladasPorUsuario()` (`:552-565`)
```sql
select USUAPEP, USUNOMC, count(1), sum(mto_bol) from (
  select us.USUAPEP, us.USUNOMC, mto_bol from DENT.boleta bo, DENT.usuarios us
  where bo.FEC_BOL = to_date(<fechaCns>,'YYYY-MM-DD')
    and bo.ind_estado in ('ANU','DEV','NCI') and bo.COD_USUARIO=us.USULOGIN
  union all
  select ... from dent_ciclo.boleta bo, DENT.usuarios us where ...
) group by USUAPEP, USUNOMC
```

#### `(Funcionarios)` — `TIPO_CONSULTA=3` — **Pendiente MCP correo (Funcionarios)**

Consumidas en `ConsultaControl.java:524-727`.

**a) Rendimiento asistentes (citas)** — `ResumenControl.setTablaRendimientoAst()` (`:381-389`)
```sql
select ac.cod_asistente, u.usunomc||' '||u.usuapep nombre, count(distinct(ac.id_agenda)) cantidad
from DENT.agenda a, DENT.acciones ac, DENT.usuarios u
where a.FEC_CITA = to_date(<fechaCns>,'YYYY-MM-DD')
and a.cita_secuencia=1
and a.id_agenda = ac.id_agenda
and ac.ind_estado = 'EJE'
and ac.cod_asistente = u.usurut
group by ac.cod_asistente, u.usunomc||' '||u.usuapep
order by cantidad desc
```

**b) Informes impresos por doctor** — `ResumenControl.getImpresoInformePorDoc()` (`:779-788`)
```sql
select u.USUAPEP||' '||u.USUNOMC doc, u2.USUAPEP||' '||u2.USUNOMC ast, count(1)
from DENT.accion d, DENT.acciones a, DENT.usuarios u, DENT.usuarios u2
where d.acc_cod like 'IMP%' and d.acc_cod != 'IMPH'
and d.acc_cod = A.COD_ACCION
and A.IND_ESTADO = 'EJE'
and A.FEC_ACCION between to_date(<fechaCns>,'YYYY-MM-DD') and to_date(<fechaCns>,'YYYY-MM-DD')+.99999
and A.COD_MEDICO = U.USURUT
and A.COD_ASISTENTE = U2.USURUT
group by u.USUAPEP||' '||u.USUNOMC, u2.USUAPEP||' '||u2.USUNOMC
order by ...
```

**c) Productos usados por doctor** — `ResumenControl.getUsoProductoPorDoc()` (`:817-823`)
```sql
select U.USUAPEP||' '||U.USUNOMC NOMBRE_DOC, U2.USUAPEP||' '||U2.USUNOMC NOMBRE_AST,
       count(p.cod_accion)
from DENT.PROD_OUT_ENC p, DENT.usuarios u, DENT.usuarios u2
where P.OUT_FEC_CRE = to_date(<fechaCns>,'YYYY-MM-DD')
and P.OUT_DOC = U.USURUT
and P.OUT_AST = U2.USURUT
group by U.USUAPEP||' '||U.USUNOMC, U2.USUAPEP||' '||U2.USUNOMC
order by ...
```

**d) Detalle de acciones** — `ResumenControl.getAccionesPorTipoAccion()` (`:452-458`)
```sql
select do.acc_dsc, count(1)
from DENT.acciones ac, DENT.accion do
where ac.FEC_ACCION between to_date(<fechaCns>,'YYYY-MM-DD') and to_date(<fechaCns>,'YYYY-MM-DD')+.99999
and ac.IND_ESTADO = 'EJE'
and ac.COD_ACCION = do.ACC_COD
group by do.acc_dsc
order by do.acc_dsc
```

**e) Detalle de acciones por asistente** (condicional, `chk_det=ON`) —
`ResumenControl.getAccionesPorTipoAccionAsistentes()` (`:480-487`)
```sql
select us.USUAPEP, us.USUNOMC, do.acc_dsc, count(1)
from DENT.acciones ac, DENT.accion do, DENT.usuarios us
where ac.FEC_ACCION between to_date(<fechaCns>,'YYYY-MM-DD') and to_date(<fechaCns>,'YYYY-MM-DD')+.99999
and ac.IND_ESTADO = 'EJE'
and ac.COD_ACCION = do.acc_cod
and ac.COD_ASISTENTE = us.USURUT
group by us.USUAPEP, us.USUNOMC, do.acc_dsc
order by us.USUAPEP, us.USUNOMC
```

#### `(Notas)` — `TIPO_CONSULTA=4` — **Pendiente MCP correo (Notas)**

Una sola consulta, invocada dos veces con distinto `OBS_TIPO`.
`ConsultaControl.java:753` (tipo `ADMINISTRADOR`) y `:807` (tipo `DOCTOR`).
Definición: `ResumenControl.getNotas()` (`:752-756`).
```sql
select us.USUAPEP, us.USUNOMC, ob.obs_ficha, ob.obs_descrip
from DENT.obs ob, DENT.usuarios us
where to_char(ob.OBS_FECHA,'YYYY-MM-DD') = <fechaCns>
and ob.OBS_TIPO = '<ADMINISTRADOR|DOCTOR>'
and ob.OBS_USER = us.USULOGIN
```

---

## 3. `Resumen Control (becas y convenio)` — **Pendiente MCP correo (Becas y convenios)**

### 3.1 Por qué es un caso aparte

`becas y convenios` **no** es un valor de `TIPO_CONSULTA` (`ConsultaControl.java:67-72`
solo define 1-4). No viene de `ResumenControl`. Son tres reportes JSP
independientes en `WebContent/dent/graph/`, vinculados juntos desde el menú
`WebContent/dent/graph/index.jsp:248-251` y `:279-282`:
```html
<a href="rptConvenios.jsp"       ...>Convenios</a>
<a href="rptConveniosMensual.jsp"...>Convenios - Resumen Mensual</a>
<a href="rptBecas.jsp"          ...>Becas</a>
```
El agrupamiento en un solo correo es, por tanto, una decisión del componente
externo que arma los correos; el código solo ofrece los tres reportes por separado.

Correspondencia con las **3 tablas del correo** (confirmada contra
`docs/refactorizacion/_build/data/becas.json`):

| Tabla del correo | Reporte JSP | Query (sección) |
|---|---|---|
| `Reporte Becas` | `rptBecas.jsp` (`accion=det`, `idUnidad=3`) | §3.2 |
| `Reporte Convenios` | `rptConvenios.jsp` (`accion=det`) | §3.3 |
| `Reporte Convenios Últimos 6 Meses` | `rptConveniosMensual.jsp` | §3.4 |

**Nota de exactitud:** las tablas `Reporte Becas` y `Reporte Convenios` del correo
incluyen una columna `Funcionario crea` (`USER_CREA`) que **ninguna query de los
JSP devuelve**: el `det` de `rptBecas.jsp:346` no selecciona `USER_CREA`, y el
`det` de `rptConvenios.jsp:300` tampoco (y además filtra por `USER_CREA = '<usuario>'`).
El armador externo usa variantes propias (agrega `USER_CREA` y quita el filtro por
usuario). Las queries de §3.2/§3.3 son el origen lógico, no byte-a-byte las del correo.

### 3.2 Becas — `WebContent/dent/graph/rptBecas.jsp`

Control de acceso: `vistaDirectorio` o rol `CNT`/`ADM`/`SRE`/`DRJEF`/`vistaDirClinico`
(`rptBecas.jsp:19-22`). Parámetros: `accion` (`bs`/`det`/`detRef`), `fecha1`, `fecha2`,
`idUnidad` (1 = Ortodoncia hasta Sep 2022, 2 = Especialidad hasta Sep 2022, 3 = Ortodoncia).

**Resumen por ejecutivo, `idUnidad=1`** (`:214-220`) — fichas becadas:
```sql
select o.OBS_USER USER_CREA,
       NVL(DENT.GET_USER_NOMBRE2(o.OBS_USER,6),'Otros') NOMBRE_FUNC,
       count(o.OBS_FICHA) cantidad
from dent.obs o, dent.fichas f
where f.BECADO = 'S' AND f.NUM_FICHA = o.OBS_FICHA
AND o.OBS_TIPO = 'ADMINISTRADOR'
AND o.OBS_DESCRIP like 'Paciente becado: %'
AND o.OBS_FECHA between to_date('<fechaInicio>','DD/MM/YYYY') and to_date('<fechaFin>','DD/MM/YYYY')
GROUP BY o.OBS_USER
```

**Resumen por ejecutivo, `idUnidad=2` o `4`** (`:222-227`, `:249-254`) — descuentos:
```sql
select SUBSTR(TO_CHAR(p.PRE_OBS_TRA),13-1) USER_CREA,
       NVL(DENT.GET_USER_NOMBRE2(SUBSTR(TO_CHAR(p.PRE_OBS_TRA),13-1),6),'Otros') NOMBRE_FUNC,
       count(p.PRE_DESCUENTO) CANTIDAD, sum(p.PRE_DESCUENTO) DESCUENTO
from DENT.PRESUPUESTO p
where p.PRE_DESCUENTO > 0
AND p.PRE_ESTADO = 'TRM'
AND p.FEC_TRM between to_date('<fechaInicio>','DD/MM/YYYY') and to_date('<fechaFin>','DD/MM/YYYY')+.99999
group by TO_CHAR(p.PRE_OBS_TRA)
```

**Resumen por referred, `idUnidad=3`** (`:229-245`) — pagos registrados:
```sql
SELECT USUA_CREA AS USER_CREA,
       NVL(DENT.GET_USER_NOMBRE2(USUA_CREA,6),'Otros') AS NOMBRE_FUNC,
       COUNT(*) CANTIDAD
FROM PAGOS_LOG
WHERE COD_MOTIVO IN('BEC') AND TIP_PAGO = 'ORT'
AND FEC_CREA BETWEEN TO_DATE('<fechaInicio>','DD/MM/YYYY') AND TO_DATE('<fechaFin>','DD/MM/YYYY')
AND FEC_CREA > '14-09-2022'
GROUP BY USUA_CREA, GET_USER_NOMBRE(USUA_CREA)
```
Segunda consulta idéntica agrupada por `USER_REF` (`:238-245`) para la tabla
"Referido". La fecha `14-09-2022` está hardcodeada (`:158`).

Detalle por ficha (`:323-356`) y por referido (`:397-408`): devuelven
`NUM_FICHA`, `GET_PACIENTE_NOMBRE(...)`, fecha y, según el caso, unidad/descuento
o referido.

### 3.3 Convenios — `WebContent/dent/graph/rptConvenios.jsp`

Parámetros: `accion`, `fecha1`, `fecha2`, `idUnidad`, `idConvenio`.
Tabla base: `DENT.CONVENIO_LOG_FICHA` (`lf`).

**Resumen por ejecutivo** (`:188-200`):
```sql
select lf.USER_CREA, GET_USER_NOMBRE2(lf.USER_CREA,6) NOMBRE_FUNC,
       count(lf.NUM_FICHA) cantidad_fichas,
       sum(lf.MTO_INI-lf.MTO_FIN) total_descontado
FROM DENT.CONVENIO_LOG_FICHA lf
WHERE lf.FEC_CREA between to_date('<fechaInicio> 00:00:00','dd-mm-yyyy HH24:MI:SS')
                    and to_date('<fechaFin> 23:59:59','dd-mm-yyyy HH24:MI:SS')
AND lf.IND_ESTADO = 'ACT'
[AND lf.UNIDAD = <idUnidad>]
[AND lf.ID_CONVENIO = <idConvenio>]
GROUP BY lf.USER_CREA
```

**Resumen por referido** (`:236-248`): idéntico, con `lf.USER_REF` y
`GROUP BY lf.USER_REF`.

**Detalle** (`:300-310` y `:351-361`): `NUM_FICHA`, nombre del paciente,
`UNIDAD` vía subconsulta, y montos.

### 3.4 Convenios últimos 6 meses — `WebContent/dent/graph/rptConveniosMensual.jsp`

Este es el reporte que genera la **3ª tabla** del correo (`Reporte Convenios
Últimos 6 Meses`); no estaba documentado antes de este análisis.

Control de acceso: `vistaDirectorio` o rol `ADM`/`SRE`/`CNT`/`DRJEF`/`PROMAN`/`pjeldres`
(`:19-22`). **No recibe parámetros**: opera siempre sobre `SYSDATE`. Alimenta un
gráfico Highcharts "Convenios últimos 6 meses" (`:152`).

**a) Cabecera de meses (los 6 últimos)** (`:62-69`)
```sql
SELECT * FROM (
  SELECT TO_CHAR(ADD_MONTHS(SYSDATE,-5),'MON_YYYY') CAB, TO_CHAR(ADD_MONTHS(SYSDATE,-5),'YYYY/MM') ORDEN FROM DUAL
  UNION SELECT ... ADD_MONTHS(SYSDATE,-4) ...
  UNION SELECT ... ADD_MONTHS(SYSDATE,-3) ...
  UNION SELECT ... ADD_MONTHS(SYSDATE,-2) ...
  UNION SELECT ... ADD_MONTHS(SYSDATE,-1) ...
  UNION SELECT TO_CHAR(SYSDATE,'MON_YYYY') CAB, TO_CHAR(SYSDATE,'YYYY/MM') ORDEN FROM DUAL
) A ORDER BY A.ORDEN ASC
```
Devuelve las 6 etiquetas `MON_YYYY` (ej. `ABR_2026` … `SEP_2026`) que titulan las
columnas de la tabla.

**b) Descuentos por tipo de convenio y mes** (`:80-110`)
```sql
SELECT * FROM (
  SELECT A.TIPO_CONVENIO, A.MES, SUM(A.MTO_INI - A.MTO_FIN) TOTAL_DESCONTADO, A.ORDEN
  FROM (
    SELECT
      CASE
        WHEN ID_CONVENIO IN (29,37,4,24,3) THEN 'REFERIDO'
        WHEN ID_CONVENIO IN (30,34,31,32,33) THEN 'RECLAMO'
        WHEN ID_CONVENIO IN (26,39,28,25,2) THEN 'GARANTIA'
        WHEN ID_CONVENIO NOT IN (29,37,4,24,3,30,34,31,32,33,26,39,28,25,27) THEN 'OTROS'
      END TIPO_CONVENIO,
      TO_CHAR(FEC_CREA,'MON_YYYY') MES,
      TO_CHAR(FEC_CREA,'YYYY/MM') ORDEN,
      MTO_INI, MTO_FIN
    FROM DENT.CONVENIO_LOG_FICHA
    WHERE FEC_CREA >= TRUNC(ADD_MONTHS(SYSDATE,-5),'MM')
      AND FEC_CREA <  LAST_DAY(TRUNC(SYSDATE)) + .99999
  ) A
  GROUP BY A.TIPO_CONVENIO, A.MES, A.ORDEN
  UNION ALL
  SELECT A.TIPO_CONVENIO, A.MES, SUM(A.MTO_INI - A.MTO_FIN) TOTAL_DESCONTADO, A.ORDEN
  FROM (
    SELECT 'TODOS' AS TIPO_CONVENIO,
           TO_CHAR(FEC_CREA,'MON_YYYY') MES, TO_CHAR(FEC_CREA,'YYYY/MM') ORDEN,
           MTO_INI, MTO_FIN
    FROM DENT.CONVENIO_LOG_FICHA
    WHERE FEC_CREA >= TRUNC(ADD_MONTHS(SYSDATE,-5),'MM')
      AND FEC_CREA <  LAST_DAY(TRUNC(SYSDATE)) + .99999
  ) A
  GROUP BY A.TIPO_CONVENIO, A.MES, A.ORDEN
) B ORDER BY B.TIPO_CONVENIO ASC, B.ORDEN ASC
```

Notas de implementación:
- La fila `TODOS` es un `UNION ALL` (no un `ROLLUP`): es una fila de datos más,
  no un total calculado sobre las otras categorías. En el correo aparece como
  última fila de la tabla.
- Las categorías salen de listas **hardcodeadas** de `ID_CONVENIO`; la rama
  `TODOS` no aplica el `CASE`/exclusión, por lo que suma todo el rango.
- Ventana temporal: desde `TRUNC(ADD_MONTHS(SYSDATE,-5),'MM')` (inicio de mes
  hace 5 meses) hasta `LAST_DAY(TRUNC(SYSDATE))+.99999` (fin del mes actual).


## Cantidad de pacientes por ciudad — MCP implementado (`consultar_pacientes_por_ciudad_chile`)

-- Cantidad de pacientes por CIUDAD

```sql
SELECT ci.NOM_CIU AS ciudad,
       COUNT(DISTINCT p.PAC_CODIGO) AS cantidad_pacientes
FROM DENT.PACIENTES p
JOIN DENT.DIRECCIONES d ON d.COD_PERSONA = p.PAC_CODIGO
JOIN DENT.CIUDADES ci ON ci.COD_CIU = d.COD_CIUDAD
WHERE d.IND_ESTADO = 'VIG'
GROUP BY ci.NOM_CIU
ORDER BY cantidad_pacientes DESC, ci.NOM_CIU
```



---

## 4. Ausencias (lo que no está en el corpus)

Estas ausencias son la conclusión más relevante del análisis:

1. **Ningún programa envía los seis correos.** En todo el proyecto Java/JSP
   existen 5 llamadas a `setEmailTitulo` (`EnviarMail.java:213,286`,
   `MailForo.java:133`, `LeeMailRadio.java:134,269`) y ninguna corresponde a
   estos reportes. `LeeMailRadio` está además marcado `@Deprecated` y su envío
   está comentado (`:131-140`).

2. **`MAIL_AVISO` solo se escribe, nunca se lee** desde Java/JSP.

3. **`ResumenControl.getTitulo()` no tiene consumidores**, y
   `setTitulo(String)` no tiene llamadores. La cadena
   `"Resumen Control ("+subTipo+") "` existe pero nunca se instancia con un
   subtipo real en el código.

4. **El lector de `MAIL_AVISO` es un componente ausente.** La metadata lo
   anticipa: `docs/assessment/relaciones-implicitas/01-joins-manuales-en-codigo.md:498`
   > "No se encontraron jobs programados en la metadata de BD. El archivo
   > `scheduler_jobs.json` está vacío. Los procesos batch en esta aplicación
   > probablemente se ejecutan externamente".

5. **El asunto literal `Resumen Procesos` no existe** en ningún archivo del
   corpus ni en el código fuente.

### Consecuencia práctica

Para cerrar el círculo hay que revisar fuera de este repositorio:
- El job/agente que lee `MAIL_AVISO` y compone el correo de procesos.
- El job que instancia `ResumenControl` con subtipo y despacha los cuatro
  reportes de control.
- El job que combina `rptBecas.jsp` y `rptConvenios.jsp`.

## 5. Nota de calidad de datos

Todas las consultas de `ResumenControl` concatenan la fecha directamente en el
SQL sin `PreparedStatement` (`ResumenControl.java:111,135-136,268-269,286,322,
378,381,450,454,478,482,510,514,550,593,667,671,714,750,777,815,819`). El patrón
`to_date(to_char(sysdate,'YYYY-MM-DD'),'YYYY-MM-DD')` con concatenación es
vulnerable a inyección si algún llamador pasara un valor no controlado, aunque
en el flujo actual la fecha proviene de un input de calendario de la propia UI.
`MaestroProceso.logResumen` tiene el mismo problema con `descrip`
(`MaestroProceso.java:160`), señalado en
`docs/llm/dent/maestroprocesoRICH.md:452`.
