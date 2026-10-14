#!/usr/bin/env python3
"""Decodifica un cuerpo Gmail: base64url -> quoted-printable -> bytes crudos."""
import base64
import quopri
import sys
import pathlib

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])

b64 = b"".join(src.read_bytes().split())
raw = base64.urlsafe_b64decode(b64 + b"=" * (-len(b64) % 4))
out = quopri.decodestring(raw)

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(out)

crlf = out.count(b"\r\n")
lf = out.count(b"\n")
print(f"{dst.name}: {len(out)} bytes | CRLF={crlf} LF={lf} | CR={out.count(chr(13).encode())}")