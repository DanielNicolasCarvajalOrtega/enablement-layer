#!/usr/bin/env python3
"""Extrae el cuerpo text/plain de la respuesta JSON de gmail.users.messages.get.

Uso: extract_mime.py <salida_json> <nombre_destino> [etiquetas_json]

Guarda:
  _build/raw/<nombre>.txt      cuerpo de texto verbatim
  _build/raw/<nombre>.meta.json  metadatos de la parte (para trazabilidad)
"""
import base64
import json
import quopri
import sys
import pathlib

src = pathlib.Path(sys.argv[1])
name = sys.argv[2]
labels = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

raw_dir = pathlib.Path(__file__).resolve().parent / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

data = json.loads(src.read_text())
payload = data.get("payload", data)

found = {"plain": None, "html": None}
tree = []


def walk(part):
    mime = part.get("mimeType", "")
    body = part.get("body", {})
    tree.append(
        {
            "mimeType": mime,
            "filename": part.get("filename", ""),
            "size": body.get("size"),
            "hasData": bool(body.get("data")),
            "headers": [
                {"name": h.get("name"), "value": h.get("value")}
                for h in part.get("headers", [])
                if h.get("name", "").lower() in ("content-type", "content-transfer-encoding")
            ],
        }
    )
    if mime == "text/plain" and body.get("data"):
        found["plain"] = body["data"]
    if mime == "text/html" and body.get("data"):
        found["html"] = body["data"]
    for sub in part.get("parts", []) or []:
        walk(sub)


walk(payload)

if not found["plain"]:
    print(f"ERROR {name}: no se encontro text/plain")
    print(json.dumps(tree, indent=2))
    sys.exit(1)

b64 = found["plain"]
decoded = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
text = quopri.decodestring(decoded)

out = raw_dir / f"{name}.txt"
out.write_bytes(text)

meta = {
    "name": name,
    "mimeTree": tree,
    "plainBytes": len(text),
    "plainCrlf": text.count(b"\r\n"),
    "plainLf": text.count(b"\n"),
    "htmlBytes": len(found["html"] or ""),
    **labels,
}
(raw_dir / f"{name}.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

print(f"OK {name}: {len(text)} bytes | CRLF={text.count(chr(13).encode()) + text.count(chr(10).encode()) - text.count(chr(10).encode())} LF={text.count(chr(10).encode())} | html_b64={len(found['html'] or '')}")