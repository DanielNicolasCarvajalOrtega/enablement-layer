#!/usr/bin/env python3
"""Convierte una respuesta gmail format=raw a un JSON con la misma forma
de payload.parts que devuelve gmail format=full, para que extract_mime.py
pueda consumirla sin cambios.

Uso: raw_to_parts.py <entrada_json_raw> <salida_json_parts>
"""
import base64
import json
import pathlib
import re
import sys
from email import policy
from email.parser import BytesParser

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])

data = json.loads(src.read_text())

raw_b64 = None
if isinstance(data, dict) and data.get("raw"):
    raw_b64 = data["raw"]
elif isinstance(data, dict) and "head" in data:
    # envoltorio truncado: el campo 'raw' puede quedar cortado en 'head'
    m = re.search(r'"raw"\s*:\s*"([A-Za-z0-9+/=_-]*)', data["head"])
    if m:
        raw_b64 = m.group(1)
if not raw_b64:
    print("ERROR: no hay campo 'raw' recuperable en la entrada")
    sys.exit(1)

msg_bytes = base64.urlsafe_b64decode(raw_b64 + "=" * (-len(raw_b64) % 4))
msg = BytesParser(policy=policy.compat32).parsebytes(msg_bytes)


def b64u(data_bytes):
    return base64.urlsafe_b64encode(data_bytes).decode("ascii").rstrip("=")


def keep_headers(part):
    out = []
    for name in ("Content-Type", "Content-Transfer-Encoding"):
        val = part.get(name)
        if val is not None:
            out.append({"name": name, "value": str(val)})
    return out


def convert(part):
    ctype = part.get_content_type()
    node = {"mimeType": ctype, "filename": part.get_filename() or ""}

    if part.is_multipart():
        node["body"] = {"size": 0}
        node["headers"] = keep_headers(part)
        node["parts"] = [convert(p) for p in part.get_payload()]
        return node

    raw_payload = part.get_payload(decode=False)
    if isinstance(raw_payload, list):
        raw_payload = "".join(str(x) for x in raw_payload)
    if raw_payload is None:
        raw_payload = ""
    enc = raw_payload.encode("utf-8", "surrogateescape")
    decoded = part.get_payload(decode=True) or b""
    node["body"] = {"size": len(decoded), "data": b64u(enc)}
    node["headers"] = keep_headers(part)
    return node


out = {"payload": convert(msg)}
dst.write_text(json.dumps(out, ensure_ascii=False))
print(f"CONVERTED -> {dst.name} root={out['payload']['mimeType']}")
