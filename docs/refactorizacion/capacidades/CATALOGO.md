# Catálogo de capacidades · Control Contable + Pacientes

> Índice de las **7 capabilities READ** publicadas: 6 del bloque Control Contable, extraídas de `Resumen Control (Contable)`, y 1 del bloque Pacientes, extraída de `docs/go/encuentros.md`. Todas implementadas, verificadas contra Oracle QA y con paridad Nivel 0.

**Estado:** ✅ 7/7 implementadas · 240 tests en verde · paridad viva ejecutada 2026-10-05.

> **Para agregar la siguiente:** [`PLANTILLA_CAPACIDAD.md`](./PLANTILLA_CAPACIDAD.md) —
> 12 pasos, rutas de archivo, y las trampas ya conocidas de este repo. El esqueleto
> copiable está en [`_plantilla/`](./_plantilla/).

---

## Tabla resumen

### Bloque Control Contable (6)

| # | Capability | Tool / REST | SQL | Ficha | Fecha |
| --- | --- | --- | --- | --- | --- |
| 1 | Ingresos por tipo pago | `consultar_ingresos_por_tipo_pago` | `Q1` | [consultar_ingresos_por_tipo_pago.md](./consultar_ingresos_por_tipo_pago.md) | obligatoria |
| 2 | Resumen de deuda | `consultar_resumen_deuda` | `Q3` | [consultar_resumen_deuda.md](./consultar_resumen_deuda.md) | obligatoria |
| 3 | Ingresos por tipo tarjeta | `consultar_ingresos_por_tipo_tarjeta` | `Q10` | [consultar_ingresos_por_tipo_tarjeta.md](./consultar_ingresos_por_tipo_tarjeta.md) | obligatoria · `origen` opcional |
| 4 | Ingresos por tipo previsión | `consultar_ingresos_por_tipo_prevision` | `Q11` | [consultar_ingresos_por_tipo_prevision.md](./consultar_ingresos_por_tipo_prevision.md) | obligatoria |
| 5 | Boletas emitidas por usuario | `consultar_boletas_emitidas_por_usuario` | `Q8` | [consultar_boletas_emitidas_por_usuario.md](./consultar_boletas_emitidas_por_usuario.md) | obligatoria |
| 6 | Boletas anuladas por usuario | `consultar_boletas_anuladas_por_usuario` | `Q9` | [consultar_boletas_anuladas_por_usuario.md](./consultar_boletas_anuladas_por_usuario.md) | obligatoria |

### Bloque Pacientes (1)

| # | Capability | Tool / REST | SQL | Ficha | Fecha |
| --- | --- | --- | --- | --- | --- |
| 7 | Pacientes por ciudad (Chile) | `consultar_pacientes_por_ciudad_chile` | `ENC.PACIENTES_POR_CIUDAD` | [consultar_pacientes_por_ciudad_chile.md](./consultar_pacientes_por_ciudad_chile.md) | **no aplica** (sin parámetros) |

---

## Contrato transversal

Reglas comunes a las 7, declaradas **una sola vez** en el Capability Registry (`application/registry.py`):

| Atributo | Valor |
| --- | --- |
| `operation.mode` | `READ` en las 7 |
| Annotations MCP | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false` — **derivadas** del modo, no escritas a mano |
| Autenticación | `Authorization: Bearer <token>` |
| `NO_DATA` | Tabla vacía con query exitosa → `404`. **Nunca** se disfraza de `UNAVAILABLE` |

Y las que **no** son comunes, para no asumir que el bloque contable describe el服务器 entero:

| Atributo | Control Contable (#1–#6) | Pacientes (#7) |
| --- | --- | --- |
| Roles | `contador`, `analista_financiero`, `gerente_finanzas`, `ai_agent` | `analista_financiero`, `gerente_finanzas`, `ai_agent` — **sin `contador`** |
| Parámetros | `fecha` obligatoria `YYYY-MM-DD` | Ninguno; el schema MCP va vacío |
| Fuente | Oracle `DENT` + réplica `DENT_CICLO` (`union all`) | Solo `DENT` (`PACIENTES`, `DIRECCIONES`, `CIUDADES`) |
| `data_profile` | `financial_pii` | `operational` |

---

## Cómo elegir una capability

| Si la pregunta es… | Usar |
| --- | --- |
| ¿Cuánto se recaudó hoy por forma de pago? | #1 `consultar_ingresos_por_tipo_pago` |
| ¿Cómo viene la deuda mes a mes? | #2 `consultar_resumen_deuda` |
| ¿Cuánto entró por tarjeta, por tipo y canal? | #3 `consultar_ingresos_por_tipo_tarjeta` |
| ¿Cuánto se facturó por previsión? | #4 `consultar_ingresos_por_tipo_prevision` |
| ¿Quién emitió más boletas? | #5 `consultar_boletas_emitidas_por_usuario` |
| ¿Quién generó más anulaciones? | #6 `consultar_boletas_anuladas_por_usuario` |
| ¿Cómo se reparten los pacientes entre ciudades? | #7 `consultar_pacientes_por_ciudad_chile` |

---

## Advertencias de interpretación

Las cuatro primeras hacen que dos consultas "razonables" den números que parecen contradicción. La quinta es la más fácil de malinterpretar de todo el catálogo.

### 1. El filtro de fecha no es uniforme

| Capability | Filtro | Efecto |
| --- | --- | --- |
| #1, #2, #4, #5 | `00:00:00` a `23:59:59` | Día completo |
| #3 CAJA | **Igualdad exacta** | Solo boletas a medianoche |
| #3 TOTEM, #3 WEBPAY | `trunc(FEC_BOL)` | Día completo |
| #6 | **Igualdad exacta** | Solo boletas a medianoche |

Es un comportamiento del legacy, replicado a propósito (V2 §19 h2). En Oracle QA, `FEC_BOL` tiene 163.369 filas a medianoche, 8.553 con hora y el resto con hora real: las diferencias son materiales.

### 2. Los canales de #3 no son comparables entre sí por filtro

Un canal CAJA vacío puede deberse al filtro por igualdad exacta, no a ausencia de datos.

### 3. El total de #4 puede no cuadrar con el total de #1

#4 excluye las boletas sin ficha, sin `TIP_PREVISION`, o con previsión ausente en `DENT.dominio`. La diferencia es esperable.

### 4. `deuda` de #2 es un promedio diario

`round(avg(bat_deuda), 0)` **no** es el saldo de cierre del mes. Además, los meses sin filas se **omiten**: pueden venir menos de 4 ítems, y eso no es `NO_DATA`.

### 5. #7 no cuenta pacientes activos, ni pacientes totales

Tres cosas se suelen leer mal en un mismo número:

| Lectura equivocada | Realidad |
| --- | --- |
| "2.307 pacientes en Santiago" (pacientes activos) | La consulta **no** filtra por estado. De los 2.530 contados, solo 340 están `ACT` |
| "2.530 pacientes en total" | `DENT.PACIENTES` tiene 505.304 fichas; 502.774 no tienen ninguna dirección vigente y no aparecen en ninguna ciudad |
| "Las ciudades con 1 paciente son ruido" | No hay umbral mínimo. 35 ciudades tienen 1 paciente y están en el resultado a propósito |

De ahí que el payload lleve `base: "pacientes_con_direccion_vigente"` e `incluye_pacientes_no_activos: true`: la semántica viaja en el dato, no en la memoria del agente.

---

## PII

Solo #5 y #6 exponen datos personales (**nombres y apellidos de empleados**). #7 expone conteos agregados sin ningún identificador, pero 35 ciudades tienen un solo paciente, así que un consumidor con acceso al detalle podría inferir quién es. Por eso #7 excluye el rol `contador`.

| Campo | Estado |
| --- | --- |
| `USULOGIN` / `cod_usuario` | Nunca se expone (llave de join) |
| `password` de `DENT.usuarios` | Nunca se proyecta |
| Nombres en logs | No se registran; los logs llevan conteos |
| `NUM_FICHA` en #4 | Solo como llave de join, nunca se proyecta |
| `USURUT` | **Nunca** se selecciona en ninguna query |

Para restringir el detalle por operador, el lugar correcto es `roles` en el registry, no una condición en el service.

---

## Casos límite conocidos

| Caso | Comportamiento | Nota |
| --- | --- | --- |
| `DENT.bat_deuda` termina en 2023-03-30 | #2 devuelve `NO_DATA` para fechas recientes | Correcto; cubierto por `test_q3_sin_datos_recientes_es_nodata` |
| `DENT_CICLO.boleta` tiene 0 filas | El `union all` se conserva por fidelidad | Ninguna de las 6 se rompe por eso |
| Fecha muy antigua sin boletas | `NO_DATA` en las 6 | V2 §12 |
| Canal sin datos en #3 | Se omite de `items`; su total queda en 0 | `NO_DATA` solo si **todos** los canales consultados están vacíos |

---

## Tests

| Suite | Cubre | Tests |
| --- | --- | --- |
| `tests/test_registry.py` | Invariantes del registry, derivación de annotations, tools MCP, schema vacío de #7 | 60 |
| `tests/test_service.py` | Lógica de negocio de #1–#6, errores, totales | 34 |
| `tests/test_service_pacientes.py` | Lógica de #7: mapeo, orden, `NO_DATA`, contrato sin argumentos | 9 |
| `tests/test_repository_sql.py` | Guardas de fidelidad SQL (filtros, owner, binds) de las 7 | 67 |
| `tests/test_contracts.py` | Auth, OpenAPI, códigos de error REST de las 7 | 45 |
| `tests/test_paridad_oracle.py` | Paridad contra Oracle QA | 25 |
| **Total** | | **240** |

```bash
.venv/bin/python -m pytest -q
# 240 passed
```

`tests/test_paridad_oracle.py` **se salta solo** si no hay pool configurado, así que la suite es verde sin base de datos; con DSN configurado exige conexión real.

---

## Orden de construcción (V2 §14.3)

| Orden | Capability | Por qué en esa posición |
| --- | --- | --- |
| 1 | `consultar_ingresos_por_tipo_pago` (Q1) | Arma el repository, el mapeo de canales y la unión con la réplica |
| 2 | `consultar_resumen_deuda` (Q3) | Período armado en el service, sin literal de fecha en el SQL |
| 3 | `consultar_ingresos_por_tipo_tarjeta` (Q10) | Tres SQL bajo una llamada; primer input opcional |
| 4 | `consultar_ingresos_por_tipo_prevision` (Q11) | Joins extra (`fichas`, `dominio`) |
| 5 | `consultar_boletas_emitidas_por_usuario` (Q8) | Primera capability con PII |
| 6 | `consultar_boletas_anuladas_por_usuario` (Q9) | Replica Q8 con estados y filtro distintos |
| 7 | `consultar_pacientes_por_ciudad_chile` | Primer dominio sin `fecha`; abre el bloque Pacientes |

El orden 7 no viene de `V2 §14.3`, que solo cubre el bloque Control Contable: es la primera capacidad que se implementa siguiendo el mismo patrón pero fuera de esa lista.

---

## Fuera de alcance

Confirmado en el levantamento, **no** implementado:

| Capability legacy | Motivo |
| --- | --- |
| Agenda de citas | Bloque Agenda (odontología), no Control Contable |
| Funcionarios / resumen de Turning | Módulo de RRHH |
| Notas del día | Datos clínicos |
| Becas / alignment | Módulo de admisión |

---

## Referencias

- `000_MiEstrategiaV2.md` — estrategia autoritativa (§8.1 catálogo, §12 Nivel 0, §14.3 orden, §19 hallazgos).
- `arquitectura.md` — pool Oracle, Bearer, `.env`, puerto, composición.
- `ResumenControl.java` / `ConsultaControl.java` — fuente Java autoritativa de #1–#6.
- `docs/go/encuentros.md` — fuente autoritativa de #7.
- `estado_de_sesion_2026-10-02.md` — bitácora de la sesión del bloque Control Contable.