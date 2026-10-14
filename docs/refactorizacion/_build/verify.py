#!/usr/bin/env python3
"""Verifica la cuadre aritmetica de cada reporte y calcula los KPI
que alimentaran el dashboard de corporativo.html."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
D = lambda n: json.load(open(os.path.join(BASE, "data", f"{n}.json"), encoding="utf-8"))


def f(v):
    return float(v or 0)


def head(t):
    print("\n" + "=" * 66)
    print(t)
    print("=" * 66)


# ---------------------------------------------------------------- CONTABLE
c = D("contable")
head("CONTABLE")
pago = {r["tipo"]: r["monto"] for r in c["ingresos_pago"] if not r["es_total"]}
total_pago = next(r["monto"] for r in c["ingresos_pago"] if r["es_total"])
print(f"total declarado (Ingresos por tipo pago) = {total_pago:>15,.0f}")
print(f"suma de filas no-TOTAL                    = {sum(pago.values()):>15,.0f}")

tar = {k.replace("Ingresos por Tipo Tarjeta", "").strip(" ()"): v
       for k, v in c["tarjetas"].items()}
suma_tar = sum(f(x["monto"]) for v in tar.values() for x in v["rows"] if x["tarjeta"].upper() != "TOTAL")
print(f"suma tarjetas (CAJA+TOTEM+WEBPAY)          = {suma_tar:>15,.0f}")
print(f"  + CAJA-EFECTIVO {pago.get('CAJA - EFECTIVO',0):,.0f}                  = {suma_tar + pago.get('CAJA - EFECTIVO', 0):>15,.0f}")

prev = [r for r in c["ingresos_prevision"] if r["prevision"].upper() != "TOTAL"]
suma_prev = sum(f(r["monto"]) for r in prev)
decl_prev = next(r["monto"] for r in c["ingresos_prevision"] if r["prevision"].upper() == "TOTAL")
qprev = sum(f(r["cantidad"]) for r in prev)
decl_qprev = next(r["cantidad"] for r in c["ingresos_prevision"] if r["prevision"].upper() == "TOTAL")
print(f"ingresos por prevision: suma={suma_prev:,.0f} declarado={decl_prev:,.0f} dif={suma_prev - decl_prev:,.0f}")
print(f"                         trx={qprev:,.0f} declarado={decl_qprev:,.0f} dif={qprev - decl_qprev:,.0f}")

bol = [r for r in c["boletas_usuario"] if r["usuario"].upper() != "TOTAL"]
suma_bol = sum(f(r["monto"]) for r in bol)
qbol = sum(f(r["cantidad"]) for r in bol)
decl_bol = next((r["monto"] for r in c["boletas_usuario"] if r["usuario"].upper() == "TOTAL"), None)
decl_qbol = next((r["cantidad"] for r in c["boletas_usuario"] if r["usuario"].upper() == "TOTAL"), None)
print(f"boletas por usuario:      suma={suma_bol:,.0f} declarado={decl_bol:,.0f} dif={suma_bol - f(decl_bol):,.0f}")
print(f"                         trx={qbol:,.0f} declarado={decl_qbol:,.0f} dif={qbol - f(decl_qbol):,.0f}")

deuda = c["deuda"]
for i in range(1, len(deuda)):
    a, b = deuda[i - 1], deuda[i]
    print(f"deuda {a['mes']}->{b['mes']}: {f(a['deuda']):,.0f} -> {f(b['deuda']):,.0f} "
          f"(+{f(b['deuda']) - f(a['deuda']):,.0f}, {(f(b['deuda']) / f(a['deuda']) - 1) * 100:.2f}%)")

# ---------------------------------------------------------------- AGENDA
a = D("agenda")
head("AGENDA")
est = [r for r in a["estado_hoy"] if r["estado"].upper() != "TOTAL"]
decl_est = next(r["cantidad"] for r in a["estado_hoy"] if r["estado"].upper() == "TOTAL")
print(f"citas hoy: suma={sum(f(r['cantidad']) for r in est):,.0f} declarado={decl_est:,.0f}")
for r in est:
    print(f"   {r['estado']:12} {f(r['cantidad']):>10,.0f}  {f(r['cantidad'])/f(decl_est)*100:5.2f}%")
man = a["manana"][0]
print(f"mañana: {man['estado']} = {man['cantidad']}")
cp = [r for r in a["citas_prevision"] if r["prevision"].upper() != "TOTAL"]
decl_cp = next(r["cantidad"] for r in a["citas_prevision"] if r["prevision"].upper() == "TOTAL")
print(f"citas prevision: suma={sum(f(r['cantidad']) for r in cp):,.0f} declarado={decl_cp:,.0f}")

# ---------------------------------------------------------------- BECAS
b = D("becas")
head("BECAS / CONVENIOS")
print(f"becas declaradas={b['total_becas']} filas={len(b['becas'])}  mensaje='{b['secciones'][0]['vacio']}'")
conv = [r for r in b["convenios"] if r["convenio"] != "Total Descontado"]
suma_conv = sum(f(r["monto"]) for r in conv)
print(f"convenios declarados={b['total_convenios']} filas={len(conv)} suma={suma_conv:,.0f}")
por_pac = defaultdict(lambda: [0, 0.0])
for r in conv:
    por_pac[r["paciente"]][0] += 1
    por_pac[r["paciente"]][1] += f(r["monto"])
for k, v in sorted(por_pac.items(), key=lambda x: -x[1][1]):
    flag = "  <-- REPETICIONES" if v[0] > 1 else ""
    print(f"   {k:20} {v[0]} desc.  {v[1]:>10,.0f}{flag}")
print("\nConvenios por mes (declarado):")
for r in b["mensual"]:
    print(f"   {r['tipo']:10} " + " ".join(f"{x:>11,.0f}" for x in r["valores"]))

# ---------------------------------------------------------------- PROCESOS
p = D("procesos")
head("PROCESOS")
tot = 0
for r in p["procesos"]:
    tot += f(r["cantidad"])
    print(f"   {r['hora']}  {r['proceso']:45} {f(r['cantidad']):>8,.0f}")
print(f"   {'TOTAL':53} {tot:>8,.0f}")

# ---------------------------------------------------------------- FUNCIONARIOS
fn = D("funcionarios")
head("FUNCIONARIOS")
ren = fn["rendimiento"]
suma_citas = sum(f(r["citas"]) for r in ren)
print(f"asistentes={len(ren)} suma_citas={suma_citas:,.0f} (declarado en correo = 1.781)")
for r in ren[:5]:
    print(f"   {r['nombre']:28} {f(r['citas']):>4,.0f}")
print("   ...")
for r in ren[-3:]:
    print(f"   {r['nombre']:28} {f(r['citas']):>4,.0f}")

for key, label in [("informes", "Informes Impresos"), ("productos", "Productos Usados")]:
    blocks = fn[key]
    sub = sum(b["subtotal_calculado"] for b in blocks)
    dec = sum(f(b["total_declarado"]) for b in blocks)
    print(f"\n{label}: {len(blocks)} doctores | suma subtotales={sub:,.0f} | suma totales={dec:,.0f} | dif={sub-dec:,.0f}")
    for b in sorted(blocks, key=lambda x: -x["subtotal_calculado"])[:5]:
        print(f"   {b['doctor']:26} {b['subtotal_calculado']:>5,.0f} "
              f"(declarado {f(b['total_declarado']):>5,.0f})")

acc = fn["acciones"]
suma_acc = sum(f(r["cantidad"]) for r in acc)
print(f"\nAcciones: {len(acc)} tipos | suma={suma_acc:,.0f} (declarado 7.996)")

# ---------------------------------------------------------------- NOTAS
n = D("notas")
head("NOTAS")
tot = n["totales_declarados"]
por_tipo = defaultdict(int)
por_func = defaultdict(int)
por_tabla = defaultdict(int)
borra = defaultdict(int)
for x in n["notas"]:
    por_tipo[x["tipo"]] += 1
    por_func[x["funcionario"]] += 1
    por_tabla[x["tabla"]] += 1
    if "borra_fecha" in x:
        borra[x["borra_fecha"]] += 1
print(f"total notas={len(n['notas'])}  declarados={tot}  cuadra={len(n['notas']) == sum(tot.values())}")
print(f"por tabla: {dict(por_tabla)}")
print("\npor tipo:")
for k, v in sorted(por_tipo.items(), key=lambda x: -x[1]):
    print(f"   {k:28} {v:>5}  {v/len(n['notas'])*100:5.2f}%")
print("\ntop 12 funcionarios:")
for k, v in sorted(por_func.items(), key=lambda x: -x[1])[:12]:
    print(f"   {k:32} {v:>4}")
print(f"\nBORRA CITA por fecha: {dict(sorted(borra.items()))}  total={sum(borra.values())}")
