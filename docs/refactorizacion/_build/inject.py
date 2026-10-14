#!/usr/bin/env python3
"""Ensambla corporativo.html: template + datos + correos originales.

El HTML final es un unico archivo autonome, sin dependencias externas.
Uso:  python3 inject.py
"""
import hashlib
import json
import pathlib
import re
import sys

BUILD = pathlib.Path(__file__).resolve().parent
OUT = BUILD.parent / "corporativo.html"

# Orden de las pestañas = orden de los correos (§2.2)
FILES = [
    ("contable", "Contable"),
    ("agenda", "Agenda"),
    ("becas", "Becas"),
    ("procesos", "Procesos"),
    ("funcionarios", "Funcionarios"),
    ("notas", "Notas"),
]


def count_rows(d):
    """Filas de tabla visibles por panel (para el chip de integridad)."""
    n = 0
    n += len(d.get("secciones", []))
    for sec in d.get("secciones", []):
        n += len(sec.get("rows", []))
    n += sum(len(v) for k, v in d.items()
             if isinstance(v, list) and k not in ("secciones", "meta", "notas"))
    if d.get("notas"):
        n += len(d["notas"])
    return n


def encabezado(text, campo="de"):
    """Campo del bloque de reenviado: 'de' (remitente) o 'para' (destinatarios)."""
    clave = r"De" if campo == "de" else r"Para"
    for line in text.splitlines():
        m = re.match(rf"^\s*>?\s*{clave}:\s*(.+?)\s*$", line, re.I)
        if m:
            return m.group(1)
    return ""


def primer_email(texto):
    hit = re.search(r"[\w.+-]+@[\w.-]+", texto or "")
    return hit.group(0) if hit else ""


def main():
    template = (BUILD / "template.html").read_text(encoding="utf-8")
    if "/*__DATA__*/" not in template:
        sys.exit("template.html no contiene el marcador /*__DATA__*/")

    data, raw, raw_ids, raw_meta = {}, {}, [], []
    for name, label in FILES:
        data[name] = json.loads((BUILD / "data" / f"{name}.json").read_text(encoding="utf-8"))
        # newline='' desactiva la traducción universal de saltos de línea: los
        # correos originales vienen en CRLF y deben llegar intactos al apéndice.
        with open(BUILD / "raw" / f"{name}.txt", encoding="utf-8", newline="") as fh:
            text = fh.read()
        # §2.2: la clave de raw es el sha1 del cuerpo verbatim.
        sid = hashlib.sha1(text.encode("utf-8")).hexdigest()
        raw[sid] = text
        raw_ids.append(sid)
        raw_meta.append({
            "label": label,
            "chars": len(text),
            "lines": text.count("\n"),
        })

    filas = sum(count_rows(d) for d in data.values())
    # §5.4: remitente y cuenta se derivan del primer correo del lote.
    primero = raw[raw_ids[0]] if raw_ids else ""
    remitente = primer_email(encabezado(primero, "de"))
    # La cuenta corporativa es el dominio propio del remitente del reporte.
    dominio = remitente.split("@")[-1].lower() if "@" in remitente else ""
    propios = [e for e in re.findall(r"[\w.+-]+@[\w.-]+",
                                     encabezado(primero, "para"))
               if e.lower().endswith("@" + dominio)]
    cuenta = propios[0] if propios else remitente
    data["raw"] = raw
    data["meta"] = {
        "filas_totales": filas,
        "correos": len(raw_ids),
        "remitente": remitente,
        "cuenta": cuenta,
        "raw_ids": raw_ids,
        "raw_meta": raw_meta,
        "raw_chars": sum(m["chars"] for m in raw_meta),
        "raw_lines": sum(m["lines"] for m in raw_meta),
    }

    payload = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    # Evita que un "</script>" dentro del texto cierre el bloque del payload.
    payload = payload.replace("<", "\\u003c")

    html = template.replace("/*__DATA__*/", payload)
    OUT.write_text(html, encoding="utf-8")
    print(f"OK  {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    print(f"    {len(raw_ids)} correos · {filas} filas de tabla · "
          f"{data['meta']['raw_chars']:,} caracteres originales")


if __name__ == "__main__":
    main()
