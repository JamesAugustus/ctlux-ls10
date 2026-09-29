#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""METHOD.md, bölüm 9 içindeki sentetik örneği kurar.

Her bayt burada elle kurulur. Hiçbir bayt gerçek bir proje dosyasından gelmez.
Tür kimliği bir yer tutucudur (16 x 0x11), gerçek bir kimlik değildir.

Kullanım:
    python3 make_example.py            konum tablosunu ve SHA-256 özetini yazdırır
    python3 make_example.py out.bin    ayrıca baytları out.bin dosyasına yazar

License: MIT OR Apache-2.0
Copyright (C) 2026 James Augustus

You may choose either the MIT License or the Apache License, Version 2.0.
See ../../LICENSE-MIT and ../../LICENSE-APACHE for the full terms.
Follow the conditions of your chosen licence. Both are not required.
The Apache option uses ../../NOTICE. MIT does not require that NOTICE.
Both licences contain warranty and liability disclaimers.

"""
import hashlib
import struct
import sys

EXPECTED_SHA256 = "5182482876d8004c734360c8b6d196e5ddef7265f56fcb3393b5fc722145465b"


def chunk(tag, payload):
    """4 baytlık etiket + 32 bitlik little-endian uzunluk + veri."""
    assert len(tag) == 4
    return tag + struct.pack("<I", len(payload)) + payload


def u32(value):
    return struct.pack("<I", value)


def f32(*values):
    return struct.pack("<%df" % len(values), *values)


def text(value):
    return value.encode("utf-16le")


TYPE_ID = bytes([0x11]) * 16

# Tek üçgen: konumlar, normaller (işaretli 16 bit), iki UV kümesi, indisler
positions = f32(0, 0, 0, 1, 0, 0, 0, 1, 0)
normals = struct.pack("<9h", 0, 0, 32767, 0, 0, 32767, 0, 0, 32767)
uv0 = f32(0, 0, 1, 0, 0, 1)
uv1 = f32(0, 0, 1, 0, 0, 1)
indices = struct.pack("<3I", 0, 1, 2)

channel = [
    ("CHIT", chunk(b"CHIT", u32(1))),
    ("CHNW", chunk(b"CHNW", text("Vertex Data"))),
    ("CHIT", chunk(b"CHIT", u32(1))),
    ("CHLC", chunk(b"CHLC", u32(1))),
    ("CHLI", chunk(b"CHLI", u32(0))),
    ("CHUL", chunk(b"CHUL", u32(0))),
    ("VRCO", chunk(b"VRCO", u32(3))),
    ("VPPI", chunk(b"VPPI", positions)),
    ("VNNI", chunk(b"VNNI", normals)),
    ("VTD0", chunk(b"VTD0", uv0)),
    ("VTD1", chunk(b"VTD1", uv1)),
    ("PO32", chunk(b"PO32", indices)),
]

parts = [
    ("ICUD", chunk(b"ICUD", bytes(32))),
    ("ICIC", chunk(b"ICIC", u32(1))),
    ("ICTD", chunk(b"ICTD", TYPE_ID)),
    ("ICSI", b"ICSI"),                      # kontrol sözcüğü: ardından uzunluk gelmez
    ("INIC", chunk(b"INIC", u32(2))),
    ("INIT", b"INIT"),                      # alan tanımı 1: "a"
    ("IINW", chunk(b"IINW", text("a"))),
    ("IIIS", b"IIIS"),
    ("IIOM", chunk(b"IIOM", b"")),
    ("INIT", b"INIT"),                      # alan tanımı 2: "g"
    ("IINW", chunk(b"IINW", text("g"))),
    ("IIIS", b"IIIS"),
    ("IIOM", chunk(b"IIOM", b"")),
    ("ICIF", b"ICIF"),
    ("IFSI", b"IFSI"),                      # önce bütün alanların değerleri
    ("IIOM", chunk(b"IIOM", b"")),
    ("IIV1", chunk(b"IIV1", f32(0.5, 0.25, 0.125, 1.0))),
    ("ENDL", b"ENDL"),
    ("IFNS", b"IFNS"),
    ("IFNS", b"IFNS"),                      # sonra çocuklar, aynı alan sırasıyla
    ("IFSI", b"IFSI"),
    ("CHAC", b"CHAC"),
] + channel + [
    ("ENDI", b"ENDI"),
    ("^EN^", b"^EN^"),
]


def main(argv):
    raw = b"".join(data for _, data in parts)
    offset = 0
    print("%6s  %-5s %5s" % ("konum", "öğe", "bayt"))
    for name, data in parts:
        print("%6d  %-5s %5d" % (offset, name, len(data)))
        offset += len(data)
    digest = hashlib.sha256(raw).hexdigest()
    print("toplam %d bayt, SHA-256 %s" % (len(raw), digest))
    if digest != EXPECTED_SHA256:
        print("EŞLEŞMİYOR: beklenen %s" % EXPECTED_SHA256)
        return 1
    if len(argv) > 1:
        with open(argv[1], "wb") as handle:
            handle.write(raw)
        print("yazıldı: %s" % argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
