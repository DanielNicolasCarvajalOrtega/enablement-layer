#!/usr/bin/env python3
"""Parsea los 6 correos de Resumen Control (INO) a JSON estructurado.
Fuente: raw/*.txt (cuerpos text/plain completos extraidos de Gmail).
Regla: NO se descarta ninguna fila de datos.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "data")

SKIP_PREFIX = (
    "Atte", "Rodrigo Mansilla", "￼", ">", "De:", "Asunto:",
    "Fecha:", "Para:", "--", "Este correo electrónico contiene",
    "privilegiada. Si Usted", "mensaje, tendrá prohibido",
    "reproducirlo o copiarlo", "notificarlo al remitente",
)

# cabeceras del bloque de reenvío: no son contenido del reporte (§3.2)
FWD_HEADERS = re.compile(
    r"^(Inicio del mensaje reenviado\s*:?|De\s*:|Asunto\s*:|Fecha\s*:|Para\s*:|CC\s*:)\s*\S?")

FIX = {"\ufffdltimos": "\u00daltimos", "�ltimos": "\u00daltimos"}

# caracteres de control / invisibles que ensucian los valores
CTRL = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\ufeff]+")
WS = re.compile(r"[\s\u00a0]+")


def norm(s):
    if s is None:
        return ""
    t = CTRL.sub("", str(s))
    return WS.sub(" ", t).strip()


def load(name):
    t = open(os.path.join(RAW, f"{name}.txt"), encoding="utf-8", newline="").read()
    for k, v in FIX.items():
        t = t.replace(k, v)
    return t


def content_lines(name):
    """Lineas reales del reporte: sin '> ' de reenvio, sin firma,
    sin aviso legal, sin vacias. Mantiene el orden."""
    out = []
    for ln in load(name).splitlines():
        s = ln.rstrip()
        if not s.strip():
            continue
        s = re.sub(r"^>\s?", "", s)          # prefijo de reenvio
        t = norm(s)
        if not t:
            continue
        if t in ("Atte", "Rodrigo Mansilla") or t.startswith("Informe de confidencialidad"):
            continue
        if t in ("￼", "‑‑") or t.startswith("Inicio del mensaje reenviado"):
            continue
        if FWD_HEADERS.match(t):
            continue
        if "correo electrónico contiene información legal" in t:
            break                              # fin del reporte
        out.append(s)
    return out


def num(s):
    """Convierte a float. Entiende formato chileno de miles ('2.739.900',
    '1,234') y decimales con coma ('0,5'). Devuelve None si no es numerico."""
    if s is None:
        return None
    t = str(s).strip().replace("−", "-")
    neg = t.startswith("-")
    t = re.sub(r"[^0-9.,]", "", t.lstrip("-"))
    if not t or not re.search(r"\d", t):
        return None
    if "," in t and "." in t:
        # el separador de miles es el que aparece antes del ultimo separador
        t = t.replace(",", "") if t.rfind(".") > t.rfind(",") else t.replace(".", "").replace(",", ".")
    elif "," in t:
        if re.fullmatch(r"\d{1,3}(,\d{3})+", t):
            t = t.replace(",", "")            # 1,234,567 -> miles
        elif re.fullmatch(r"\d+,\d{1,2}", t):
            t = t.replace(",", ".")            # 0,5 -> decimal
        else:
            t = t.replace(",", "")
    elif t.count(".") > 1:
        t = t.replace(".", "")          # 2.739.900 -> 2739900
    elif "." in t:
        head_, tail = t.split(".", 1)
        if len(tail) == 3 and len(head_) <= 3 and len(head_) >= 1 and head_ != "0":
            t = t.replace(".", "")      # 1.338 -> 1338 (miles)
        else:
            pass                        # decimal real (0.5)
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def money(v):
    if v is None:
        return ""
    v = float(v)
    return "$" + f"{v:,.0f}".replace(",", ".")
def n0(v):
    return "" if v is None else f"{v:,.0f}".replace(",", ".")


def split_tabs(line):
    return [norm(c) for c in line.split("\t")]


def is_total(cells):
    return bool(cells) and norm(cells[0]).upper() in ("TOTAL", "TOTAL (TODOS)")


def grand_total(cells):
    for c in reversed(cells[1:]):
        v = num(c)
        if v is not None:
            return v
    return None


# ----------------------------------------------------------------通用的
def simple_table(lines):
    """Divide en secciones (titulo, header, rows).
    Un texto es TITULO de seccion si le sigue (lineas vacias de por medio)
    una linea con tabs. Si no, es mensaje de tabla vacia.
    """
    has_tab = [("\t" in s) for s in lines]
    # §5.3: un texto es TITULO solo si la línea INMEDIATAMENTE siguiente tiene
    # tabulador. Mirar "cualquier tabulador posterior" convertía el mensaje de
    # tabla vacía ("No hay registros") en un título falso.
    nxt_tab = [False] * len(lines)
    for i in range(len(lines) - 1):
        nxt_tab[i] = has_tab[i + 1]

    sections, cur = [], None
    for i, s in enumerate(lines):
        if "\t" in s:
            cells = split_tabs(s)
            if cur is None:
                cur = {"titulo": None, "header": None, "rows": []}
                sections.append(cur)
            if cur["header"] is None:
                cur["header"] = cells
            else:
                cur["rows"].append(cells)
        else:
            t = norm(s)
            if not t or t == "--":
                continue
            if i + 1 < len(lines) and nxt_tab[i]:
                cur = {"titulo": t, "header": None, "rows": []}
                sections.append(cur)
            elif cur is not None and cur["header"] is not None:
                cur["vacio"] = t       # "No hay registros" / "No hay datos..."
    out = []
    for s in sections:
        if not s["header"]:
            continue
        w = max([len(s["header"])] + [len(r) for r in s["rows"]])
        s["header"] = (s["header"] + [""] * w)[:w]
        s["rows"] = [(r + [""] * w)[:w] for r in s["rows"]]
        s.setdefault("vacio", "")
        s["total"] = next((grand_total(r) for r in s["rows"]
                           if r[0].upper() == "TOTAL (TODOS)"), None)
        out.append(s)
    return out


def find(secs, *needles):
    for s in secs:
        t = (s.get("titulo") or "").lower()
        if all(n.lower() in t for n in needles):
            return s
    return None


# ---------------------------------------------------------------- contable
def parse_contable():
    secs = simple_table(content_lines("contable"))
    d = {"secciones": secs, "deuda": [], "ingresos_pago": [], "tarjetas": {},
         "ingresos_prevision": [], "boletas_usuario": [], "boletas_anuladas": []}
    for s in secs:
        t = (s.get("titulo") or "").lower()
        r = s["rows"]
        if "deuda" in t:
            d["deuda"] = [{"mes": c[0], "deuda": num(c[1])} for c in r]
        elif "tipo pago" in t:
            d["ingresos_pago"] = [
                {"tipo": c[0], "monto": num(c[1]), "es_total": c[0].upper() == "TOTAL"}
                for c in r]
        elif "tipo tarjeta" in t:
            d["tarjetas"][(s.get("titulo") or "")] = {
                "rows": [{"tarjeta": c[0], "cantidad": num(c[1]), "monto": num(c[2])} for c in r]}
        elif "prevision" in t:
            d["ingresos_prevision"] = [
                {"prevision": c[0], "cantidad": num(c[1]), "monto": num(c[2])} for c in r]
        elif "emitidas" in t:
            d["boletas_usuario"] = [
                {"usuario": c[0], "cantidad": num(c[1]), "monto": num(c[2])} for c in r]
        elif "anuladas" in t:
            d["boletas_anuladas"] = r
    return d


# ---------------------------------------------------------------- agenda
def parse_agenda():
    secs = simple_table(content_lines("agenda"))
    d = {"secciones": secs, "estado_hoy": [], "manana": [], "citas_prevision": []}
    for s in secs:
        t = (s.get("titulo") or "").lower()
        r = s["rows"]
        if "hoy" in t:
            d["estado_hoy"] = [{"estado": c[0], "cantidad": num(c[1])} for c in r]
        elif "mañana" in t or "mañana" in t:
            d["manana"] = [{"estado": c[0], "cantidad": num(c[1])} for c in r]
        elif "prevision" in t:
            d["citas_prevision"] = [{"prevision": c[0], "cantidad": num(c[1])} for c in r]
    return d


# ---------------------------------------------------------------- becas
def parse_becas():
    secs = simple_table(content_lines("becas"))
    d = {"secciones": secs, "becas": [], "convenios": [], "meses": [], "mensual": [],
         "total_becas": 0, "total_convenios": 0}
    for s in secs:
        t = (s.get("titulo") or "").lower()
        r = s["rows"]
        m = re.search(r"total:\s*(\d+)", t)
        if "becas" in t and m:
            d["total_becas"] = int(m.group(1))
            d["becas"] = r
        elif "últimos" in t or "ultimos" in t:
            d["meses"] = s["header"][1:]
            for c in r:
                d["mensual"].append({"tipo": c[0], "valores": [num(x) for x in c[1:]]})
        elif "convenios" in t:
            if m:
                d["total_convenios"] = int(m.group(1))
            d["convenios"] = [{
                "ficha": num(c[0]), "paciente": c[1], "funcionario": c[2],
                "monto": num(c[3]), "convenio": c[4], "unidad": c[5],
                "fecha": c[6], "referido": c[7],
            } for c in r if norm(c[0]).lower() != "total descontado" and c[1]]
            d["convenios_total_declarado"] = next(
                (num(c[1]) for c in r if norm(c[0]).lower() == "total descontado"), None)
    return d


# ---------------------------------------------------------------- procesos
def parse_procesos():
    secs = simple_table(content_lines("procesos"))
    rows = []
    for s in secs:
        for c in s["rows"]:
            if is_total(c):          # §12.6: el TOTAL viene como fila de datos
                continue
            rows.append({"fecha": c[0], "hora": c[1], "proceso": c[2],
                         "cantidad": num(c[3])})
    # §4: el título se deriva de las filas, nunca escrito a mano.
    fechas = [r["fecha"] for r in rows if r["fecha"]]
    horas = sorted(r["hora"] for r in rows if r["hora"])
    if fechas and horas:
        titulo = (f"Procesos automaticos ejecutados "
                  f"({fechas[0]} {horas[0]}-{horas[-1]})")
    else:
        titulo = "Procesos automaticos ejecutados"
    for s in secs:
        if not s.get("titulo"):
            s["titulo"] = titulo
    return {"secciones": secs, "procesos": rows,
            "total": sum(r["cantidad"] or 0 for r in rows)}


# ---------------------------------------------------------------- funcionarios
def build_pairs(rows):
    """Bloques: 'Doctor | Asistente | Cantidad ... TOTAL n'."""
    out, doctor, buf = [], None, []
    for c in rows:
        if is_total(c):
            if doctor is not None:
                sub = sum((num(x[-1]) or 0) for x in buf)
                out.append({
                    "doctor": doctor,
                    "registros": [{"asistente": x[0], "cantidad": num(x[-1])} for x in buf],
                    "subtotal_calculado": sub,
                    "total_declarado": grand_total(c),
                })
            doctor, buf = None, []
            continue
        if doctor is None:
            doctor, buf = c[0], []
        if len(c) > 1:
            buf.append(c[1:])
    return out


def parse_funcionarios():
    secs = simple_table(content_lines("funcionarios"))
    d = {"secciones": secs, "rendimiento": [], "informes": [], "productos": [], "acciones": []}
    for s in secs:
        t = (s.get("titulo") or "").lower()
        r = s["rows"]
        if "rendimiento" in t:
            d["rendimiento"] = [{"nombre": c[0], "citas": num(c[1])} for c in r
                                if not is_total(c)]
        elif "informes" in t:
            d["informes"] = build_pairs(r)
        elif "productos" in t:
            d["productos"] = build_pairs(r)
        elif "acciones" in t:
            d["acciones"] = [{"accion": c[0], "cantidad": num(c[1])} for c in r
                             if not is_total(c)]
    return d


# ---------------------------------------------------------------- notas
NOTA_TYPES = [
    ("borra cita", "Borra cita"),
    ("paciente atrasado", "Paciente atrasado"),
    ("presupuestos eliminados", "Presupuestos eliminados"),
    ("edita datos ficha", "Edita datos ficha"),
    ("formulario reembolso", "Reembolso asegurado"),
    ("cambio estado", "Cambio estado paciente"),
    ("crea ficha", "Crea ficha"),
    ("cambio de tel", "Cambio telefono"),
    ("cambio de ciclo", "Cambio ciclo"),
    ("mensualidades", "Informa mensualidades"),
    ("suspende cita", "Suspende cita"),
    ("cambio de cuotas", "Cambio cuotas"),
    ("promo", "Promo / campana"),
    ("webpay", "Boleta webpay"),
    ("mueve boleta", "Mueve boleta"),
    ("devolucion", "Devolucion"),
    ("cierre sesion medica", "Cierre sesion medica"),
    ("scanner", "Scanner / imagenologia"),
]


def clasificar(txt):
    t = txt.lower()
    for needle, label in NOTA_TYPES:
        if needle in t:
            return label
    return "Nota libre"


BORRA_RE = re.compile(r"BORRA CITA:\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2})\s*\(([^)]*)\)")


def parse_notas():
    """Tabla continua Funcionario|Ficha|Nota con subtotales TOTAL por grupo y
    notas multilinea. Se parte en dos tablas: Administrativas y Doctores."""
    lines = content_lines("notas")
    notas, tabla = [], "administrativas"
    totales, subtotales = {}, []
    ultima = None

    for s in lines:
        t = norm(s)
        low = t.lower()
        if "notas doctores" in low and "\t" not in s:
            tabla = "doctores"
            continue
        if "\t" not in s:
            # continuacion de una nota multilinea
            if ultima is not None:
                if not ultima["nota"].endswith(" "):
                    ultima["nota"] += " "
                ultima["nota"] += t
                ultima["tipo"] = clasificar(ultima["nota"])
            continue

        cells = split_tabs(s)
        h0 = cells[0].upper()
        if h0 == "FUNCIONARIO" and len(cells) > 1 and cells[1].lower() == "ficha":
            continue                                   # fila de encabezado
        if h0 == "TOTAL (TODOS)":
            totales[tabla] = grand_total(cells)
            continue
        if h0 == "TOTAL":
            subtotales.append({"tabla": tabla, "valor": grand_total(cells),
                               "n_filas": len([n for n in notas
                                               if n["tabla"] == tabla
                                               and n.get("_grupo") == len(subtotales) + 1])})
            continue

        fila = {
            "tabla": tabla,
            "funcionario": cells[0],
            "ficha": num(cells[1]) if len(cells) > 1 else None,
            "nota": cells[2] if len(cells) > 2 else "",
        }
        fila["tipo"] = clasificar(fila["nota"])
        fila["es_sistema"] = fila["funcionario"].strip().upper() in (
            ". SISTEMA", "SISTEMA", "SISTEMAINO")
        m = BORRA_RE.search(fila["nota"])
        if m:
            fila["borra_fecha"] = m.group(1)
            fila["borra_hora"] = m.group(2)
            fila["borra_sala"] = m.group(3)
        notas.append(fila)
        ultima = fila

    secs = [
        {"titulo": "Notas Administrativas (funcionarios)",
         "header": ["Funcionario", "Ficha", "Nota"], "rows": [], "vacio": "",
         "total": totales.get("administrativas")},
        {"titulo": "Notas Doctores",
         "header": ["Funcionario", "Ficha", "Nota"], "rows": [], "vacio": "",
         "total": totales.get("doctores")},
    ]
    return {"secciones": secs, "notas": notas,
            "totales_declarados": totales,
            "subtotales": len(subtotales)}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("contable", parse_contable), ("agenda", parse_agenda),
                     ("becas", parse_becas), ("procesos", parse_procesos),
                     ("funcionarios", parse_funcionarios), ("notas", parse_notas)]:
        d = fn()
        p = os.path.join(OUT, f"{name}.json")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"== {name}  ({os.path.getsize(p):,} bytes)")
        for s in d.get("secciones", []):
            print(f"   {str(s.get('titulo'))[:50]:52} filas={len(s.get('rows', []))}")
        for k, v in d.items():
            if isinstance(v, list) and k != "secciones":
                print(f"   · {k}: {len(v)} elementos")
        if "totales_declarados" in d:
            print(f"   · totales declarados: {d['totales_declarados']}")


if __name__ == "__main__":
    main()
