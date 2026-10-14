#!/usr/bin/env python3
"""Extrae cuerpo text/plain de un mensaje Gmail format=raw aunque el JSON
guardado por la herramienta esté truncado.

Uso: pluck_raw_plain.py <salida_herramienta_json> <nombre_destino>
"""
import base64
import json
import pathlib
import re
import sys
from email import policy
from email.parser import BytesParser

src = pathlib.Path(sys.argv[1])
name = sys.argv[2]
raw_dir = pathlib.Path(__file__).resolve().parent / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

data = json.load(open(src))
s = data.get("head", "") if isinstance(data, dict) else ""
if not s:
    s = src.read_text()
# Busca el campo raw en el JSON completo o en head
raw_b64 = None
if isinstance(data, dict) and data.get("raw"):
    raw_b64 = data["raw"]
else:
    # buscar en head o en todo el texto
    m = re.search(r'"raw"\s*:\s*"([A-Za-z0-9+/=_-]*)', s)
    if m:
        raw_b64 = m.group(1)

if not raw_b64:
    print("ERROR: no se encontro raw")
    sys.exit(1)

# Decodificar con padding correcto
def b64u_decode(b):
    pad = "=" * (-len(b) % 4)
    return base64.urlsafe_b64decode(b + pad)

try:
    msg_bytes = b64u_decode(raw_b64)
except Exception as e:
    print(f"ERROR base64: {e}")
    sys.exit(1)

msg = BytesParser(policy=policy.compat32).parsebytes(msg_bytes)

def extract_plain(part):
    if part.is_multipart():
        for p in part.get_payload():
            r = extract_plain(p)
            if r: return r
        return None
    ctype = part.get_content_type()
    if ctype == "text/plain":
        dec = part.get_payload(decode=True)
        return dec
    return None

body = extract_plain(msg) or b""
out = raw_dir / f"{name}.txt"
out.write_bytes(body)
print(f"OK {name}: {len(body)} bytes | CRLF={body.count(b'\r\n')} LF={body.count(b'\n')}")
