# LS10 project file grammar: method notes

[Turkish](Turkish/README.md)

These notes describe a grammar inferred from one `.ls10` project file
saved by Lumion® 10: how the tagged binary is structured beyond its generic
tag + length + payload container, and how geometry, surfaces, world transforms
and light records can be read from it. The work is interoperability-oriented file
format analysis: only saved project files were inspected, and the program itself
was not examined.
The notes state what could be read, what could not, and how this relates to other
public work.

Independent work, not affiliated with, endorsed by or supported by Act-3D B.V.
Lumion® is a trademark of Act-3D B.V. The name identifies the application
that saved the source files.

## Scope

- Input: a Lumion `.ls10` project file
- Output: triangle geometry (positions, normals, two UV sets), surface names and
  base colours, the world transform of a single imported model, and light records
  (position, direction, type, cone value, area size, relative intensity)
- Not covered: `.lsf` files (Lumion 2023 and later), the file structure introduced
  with Lumion 2025, cameras, animation, terrain and physically calibrated light
  or material values

## Summary

| Topic | Status |
| --- | --- |
| Container: 4-byte tag + 32-bit little-endian length + payload | A known pattern (IFF, RIFF. Earlier described for Quest3D, see RELATED_WORK.md). Described here only as used in `.ls10` |
| Control words without a length | Described for the grammar positions listed |
| Instance grammar (sections, schema, values, children) | Described for the supported schemas. Entry scan and limits in METHOD.md, sections 5 and 10. Unknown channel kinds stop the reader |
| Channel header and link pairs | Header described. Link pairs stored, their meaning across the file not resolved |
| Vertex buffer (positions, normals, UV0, UV1, triangles) with length checks | Described |
| Surface names and base colours | Described. Shader, glass and UV transforms partial |
| World matrix, axis conversion, mirrored matrices | Described for a single imported model. Buffer-to-instance mapping with several models not resolved |
| Light records | Partial: intensity is relative only, colour not validated, no photometry |
| Embedded textures | Structured payload kept, roles not resolved. Simpler geometry scan does not extract textures |
| `.lsf` and Lumion 2025 files | Not tried |

## Documents

- [METHOD.md](METHOD.md): the grammar, the rules, a byte-level synthetic example
  and the limits
- [example/make_example.py](example/make_example.py): builds the synthetic
  example by hand and checks its hash
- [RELATED_WORK.md](RELATED_WORK.md): the known container pattern, earlier public
  work on the Quest3D format, and how these notes differ
- [PROVENANCE.md](PROVENANCE.md): method scope and evidence limits
- [LICENSE](LICENSE): MIT OR Apache-2.0, for the
  original notes and example script
- [CITATION.md](CITATION.md): how to cite these notes

## Status

Method notes only. The working Python converter is in
[ctlux-core](https://github.com/JamesAugustus/ctlux-core) (MIT OR Apache-2.0).
From the core repository root, its LS10 command is
`python3 -B -m core input.ls10 output`. No sample project files, textures,
models, screenshots or Lumion application files are included here.

## Development note

The analysis and the findings are the author's. AI tools helped with wording and
with keeping the text organised.
The grammar was inferred from one real project. The synthetic example
exercises the documented reader rules (see METHOD.md, sections 9 and 10).

## Licence scope

Copyright (C) 2026 James Augustus

All original content in this repository, including method notes, documentation and any example code, is offered under **MIT OR Apache-2.0**. You may choose either [MIT](LICENSE-MIT) or [Apache 2.0](LICENSE-APACHE). The conditions of your chosen licence apply. Compliance with both is not required

Both options permit commercial use and distribution in closed products. Neither requires publication of source code or private modifications

- Under MIT, include the copyright and permission notice in all copies or substantial portions of the Software
- Under Apache 2.0, give recipients the licence, mark modified files with prominent change notices and preserve the relevant source notices as required by section 4
- Under Apache 2.0, include the relevant [NOTICE](NOTICE) attribution in a location allowed by section 4(d), such as a distributed NOTICE file or documentation
- Apache NOTICE requirements do not apply when MIT is chosen

Both options preserve applicable copyright notices. Neither requires advertising credit, a dedicated user interface credit or academic citation

Third party quotations, code and trademarks retain their own terms and are not relicensed by this notice. Only rights held in the original material are granted. Ideas, methods and file format facts do not become exclusive copyright under these licences. For independent implementations using only those ideas or facts, scholarly citation is voluntary and requested in [CITATION.md](CITATION.md)
