# Evidence scope

The documented grammar was inferred from one saved Lumion 10 project file. It covers the observed schemas and records described in [METHOD.md](METHOD.md). Other versions and unsupported schemas were not validated.

The synthetic example in [example/make_example.py](example/make_example.py) is constructed by hand. It exercises the documented reader rules without including bytes from an original project file. Passing that example does not establish compatibility with every real project.

Only saved project files were inspected using general tools and the reading tool written for this work. The examined files were not encrypted and were read directly without decompression. The application was not decompiled or disassembled, and no protection measure was bypassed.

Public sources and overlapping work are credited in [RELATED_WORK.md](RELATED_WORK.md). This account does not claim independent proof of priority.
