# Method

Notation: all integers and floats are little-endian. `u32` is an unsigned 32-bit
integer, `f32` a 32-bit IEEE float, `i16` a signed 16-bit integer. A *tag* is four
ASCII bytes. `p` is the offset of the next unread byte and `N` the file size.
Text is UTF-16LE.

## 1. Container

The basic unit is a chunk:

```
offset p      p+4          p+8                 p+8+n
| tag (4 B)  | n (u32)    | payload (n bytes)  | next item
```

- Bounds rule: first require `0 <= p <= N`. Then accept a chunk only if
  `N - p >= 8` and `n <= N - p - 8`. In
  fixed-width integer code, compare in this order before computing `p + 8 + n`,
  so that the sum is never formed out of range
- The payload offset is `p + 8`, not `p`. Keep the two apart when recording
  offsets
- The file is not a flat list of chunks. What follows a chunk depends on the
  grammar position (sections 2 to 4), so the file has to be read by grammar, not
  by walking tag after tag
- Type identifiers are raw 16-byte values. This method compares them as bytes
  (hex) and does not reorder them into a UUID text form

The tag + length + payload pattern itself is well known (IFF, RIFF) and was used
by the earlier Quest3D channel-group format. See RELATED_WORK.md.

## 2. Control words without a length

Some tags are *control words*: four bytes and nothing else. At their grammar
position they are consumed as four bytes. No length follows.

| Control word | Role |
| --- | --- |
| `ICSI`, `ICIF` | start and end of a schema |
| `INIT`, `IIIS` | start and end of the name part of a field descriptor |
| `IFSI`, `IFNS` | "present" / "absent" marker for a value or a child |
| `ENDL` | end of one value |
| `ENDI` | end of one class section |
| `^EN^` | end of a terminated instance |
| `CHAC`, `OCHA` | child channel follows / no child channel |
| `SKDA` | empty channel |
| `ISP2` | start of a single-instance channel body |
| `NOIS` | no instance in that body |

**Why this matters.** A reader that reads a length after every tag falls out of
step at the earliest control word: it takes the next tag's four bytes as a length
and jumps to a wrong place. In the synthetic example (section 9) such a reader
stops at offset 76 (`ICSI`) after reading the bytes of the following tag `INIC`
as the length 1128877641.

## 3. Instance grammar

```
Instance
  ICUD   chunk (metadata)
  ICIC   chunk, u32 = number of class sections (S)
  Section x S
    ICTD   chunk, 16-byte type identifier
    Schema
      ICSI
      INIC   chunk, u32 = number of fields (F)
      FieldDescriptor x F
        INIT
        chunks ... including IINW (field name, UTF-16LE)
        IIIS
        IIOM   chunk
        IIIT   chunk, optional
      ICIF
    Value x F            (all values)
      IFNS                                  no value
      IFSI  IIOM-chunk  <value>  ENDL
    Child x F            (then all children, same field order)
      IFNS                                  no child
      IFSI  OCHA                            no channel
      IFSI  CHAC  <channel>                 section 4
    ENDI
  ^EN^                   (only for a terminated instance)
```

Rules:

- **All values come before all children**, in the same field order. Reading
  a field's child right after its value misreads the section. A wrong order is
  not always detected: in the synthetic example (section 9) both orders even give
  the same bytes, because the two markers involved are both `IFNS`. The order has
  to come from the grammar, not from trial parsing
- Value forms: `IIVE` (4 bytes, one f32), `IIV1` (16 bytes, four f32), `IIM1`
  (64 bytes, sixteen f32), a `Text` channel introduced by `CHIT`, or an opaque
  16-byte type reference. Non-finite numbers are rejected
- A type reference is 16 raw bytes with no tag or length. It is read when the next
  four bytes are none of `IIVE`, `IIV1`, `IIM1` or `CHIT`. `ENDL` must follow it as
  a guard against a wrong reading
- The reference converter reads the field name in `IINW` up to the first NUL character,
  or to the end of the payload if there is no NUL. In the project examined, `IINW`
  had a fixed payload size with padding after the name
- The sections of one instance are merged into one field set. Two sections
  giving the same field name is an error. Section boundaries are kept
- The reader's acceptance quotas were: 1 to 16 sections, at most 128 fields, at
  most 12 chunks in a field descriptor, metadata chunks up to 4096 bytes, at most
  64 `CHLC` link pairs in a channel and at most 64 `ICLL` list items. These
  are limits of the reader, not known limits of the format

## 4. Channels

`SKDA` appears alone where a channel is expected after `CHAC`. It replaces the
entire channel header and body.

A channel header is `CHIT` (u32), `CHNW` (channel kind name, UTF-16LE),
a second `CHIT` (u32), `CHLC` (u32 = link count L), then L pairs of
`CHLI` (u32) and `CHUL` (u32). The link pairs are stored as read. Their meaning
across the whole file was not resolved. The two `CHIT` values are not
interpreted.

| Channel kind | Body |
| --- | --- |
| `Text` | `STWA` (UTF-16LE text), `STLR` |
| `OO Class Instances List` | `ICSD`, `ICLL` (u32 count), then that many terminated instances |
| `OO ClassInstance`, `ClassInstance->...` | `ISP2`, `ICSD`, then `NOIS` or one unterminated instance |
| `Vertex Data` | vertex attribute and index chunks (below) |
| `3D ObjectData` | `VRCO` = 0, then `MBCT`, `POCO`, `POTY`, `PONM`, `POTT`, `POSO`, `PUAV`, `PSRV` in that fixed order. Each chunk is at most 4096 bytes and its contents are not interpreted. A non-zero count (geometry held elsewhere) is not resolved and stops the reader |
| `Texture` | `TEXW`, `TEXH` (u32 width, height), `TEXS` (u32 size), `TEXT` (payload) and optional fields. `TEXS` must equal the `TEXT` length |

Any other channel kind stops the reader with an error. Channels and instances
share one nesting depth counter that grows by one at each nested level. A channel
at a depth above 12 or an instance at a depth above 16 stops the reader.

**Vertex Data.** With `V` = vertex count:

| Tag | Content | Payload length |
| --- | --- | --- |
| `VRCO` | vertex count V | u32 |
| `VPPI` | positions, 3 x f32 per vertex | 12 V |
| `VNNI` | normals, 3 x i16 per vertex (signed normalised. The direction is the normalised vector) | 6 V |
| `VTD0` | UV set 0, 2 x f32 | 8 V |
| `VTD1` | UV set 1, 2 x f32 | 8 V |
| `PO32` | triangles, 3 x u32 indices | multiple of 12 |
| `VTO0`, `VTO1` | UV transform, 6 x f32 per set (identity `0 0 0 0 1 1`) | 24 |

The parser checks that each tag occurs at most once, requires `VRCO`, `VPPI`,
`VNNI`, `VTD0`, `VTD1` and `PO32`, and validates attribute lengths against V.
The structured exporter checks each index is below V and rejects non-finite
positions, UV0, UV1 and UV transform values. It preserves UV1 as raw bytes after
validation. `VTO0` and `VTO1` are optional for the parser, while the structured
OBJ exporter requires both. A `PO32` length that is a multiple of 12 only shows
that the data splits into triangles. It does not prove that indices are in range.

Other tags seen in the same position (`VTTB`, `MBCT`, `POCO`, `POTY`, `PONM`,
`POTT`, `POSO`, `PUAV`, `PSRV`) are accepted and kept but not interpreted here.

**End of the body.** A `Vertex Data` body has no count and no terminator of its
own. The reader keeps reading chunks while the next four bytes are one of the
vertex tags named in this section (the interpreted and the uninterpreted ones).
The body ends at the first four bytes outside that set. The tags may come in any
order.

**Texture body.** It is read the same way, with the tag set `TEXM`, `TEXW`,
`TEXH`, `TEPU`, `TEXS`, `TEXT`, `TENT`, `TECM`, `TEGC`, `TEOW`, `TELM`, `RWEN`,
each at most once. `TEXW`, `TEXH`, `TEXS` and `TEXT` are required. The others are
optional and are kept without interpretation.

## 5. Surfaces and materials

The reference converter does not parse the file from its first byte. It finds surface
instances by searching for the instance-start pattern: `ICUD` with a 32-byte
payload, then `ICIC` with a 4-byte payload, then `ICTD` with a 16-byte payload
containing the surface type identifier.

A surface is an instance whose class section has a specific 16-byte type
identifier and whose child `ObjectData` is a `Vertex Data` channel. Its fields
include `surfaceNr`, `surfaceName` and `Diffuse` (four f32. Components 1 to 3 are
used as the base colour). Surface numbers must be unique.

Material filter instances (another type identifier) carry a `materialname` field
that matches a surface name and a `materialInfo` child whose `color` field (four
f32) is used as the display colour when present. The fourth component of that
colour is **not** treated as opacity. Its meaning was not established. Glass
settings and other shader parameters are kept as read and not interpreted.

The observed surface type identifier is
`fd1c729ffb00b74ea24200c2ba2db89b`. The observed material filter type
identifier is `daf0495380ebbe4497e19680ea2238d9`. The working reader
uses them in `ctlux-core/core/tools/ls10_surface.py`.

## 6. World matrix and axes

**Matrix.** `IIM1` holds 16 f32 values `M[0..15]`. A point `v = (x, y, z)` maps to

```
w_j = v.x * M[j] + v.y * M[j+4] + v.z * M[j+8] + M[j+12]        j = 0, 1, 2
```

This is a row vector times a row-major matrix with the translation in the last row
(`M[12]`, `M[13]`, `M[14]`). Reading the same 16 numbers as column-major gives its
transpose, used with a column vector. Both readings give the same result. The
implementation accepts only finite values, deviations of `M[3]`, `M[7]`,
`M[11]` from 0 and `M[15]` from 1 no greater than `1e-6`, and a finite
3 x 3 determinant with absolute value at least `1e-20`.

**Which matrix.** The world matrix of an imported model was taken from the
64-byte `IIM1` in the `ClassType->cCustomObject` section (from that UTF-16LE text
to the next `ClassType->` text), and only if that section also contains the
UTF-16LE text `world`. This was done only when the file holds exactly one such
section and exactly one `ClassInstance->cImportObject`. With several models the
link between vertex buffers and model instances was not resolved, and no matrix
is guessed.

**Normals** are transformed by the inverse transpose of the 3 x 3 part and then
normalised. Applying the position matrix to normals is wrong under non-uniform
scale or shear.

**Mirroring.** If the determinant of the 3 x 3 part is negative, the second and
third index of every triangle are swapped so that faces keep their orientation.

**Axes.** Lumion® space is Y-up. To a Z-up target (for example Radiance) points,
normals and directions map as `(x, y, z) -> (x, -z, y)`, applied after the world
matrix. In the project examined, units were metres and the stored normals agreed
with right-handed, counter-clockwise triangle winding.

**Precision.** Only exactly equal vertices are merged, separately for position,
UV and normal, so UV seams and hard edges survive. No distance threshold is used.
A coarse grid can delete thin faces. Coordinates are written with 17 significant
digits.

**Simpler path.** When the conditions above are not met, a narrower scan was used:
find `VPPI`, then the next `PO32`, skip the pair if another `VPPI` lies between
them, and check that the lengths are multiples of 12, that every index is below
the vertex count and that positions are finite. This path does not read normals,
UVs or names.

## 7. Light records

A light block starts at the UTF-16LE text `cLightObject` and runs to the next one.
Values are collected in order by searching inside the block for `IIVE` (4 bytes),
`IIV1` (16 bytes) and `IIM1` (64 bytes), not by the section 3 grammar. Wrong-length
chunks and matches inside an accepted payload are skipped. Random bytes resembling
value chunks may also be collected. Blocks with fewer than 37 values are skipped.

The block's schema part also contains values, so counting from the block start is
not stable. The earliest `IIM1` is field 3. With `n` collected values and its
zero-based index `j`, field `k` is at `j + (k - 3)` and exists only if `j + (k - 3)
< n`. A total of 37 values does not guarantee this.

| Field | Tag | Use in this method |
| --- | --- | --- |
| 3 | `IIM1` | world matrix: position `M[12..14]`, direction `M[8..10]` (image of the local z axis) |
| 26 | `IIVE` | cone value, treated as radians when below 6.3, else as degrees. Whether it is a full or half angle was not validated |
| 28 | `IIV1` | vector: the length of components 1 to 3 is used as a **relative** intensity |
| 35, 36 | `IIVE` | width and height of an area light |
| 37 | `IIVE` | light type: values 0, 1 and 3 were seen and are read as spot, omni (point) and area |

Stated plainly:

- The reference converter does not stop at an unreadable light field. If a value is
  missing at the expected position or has another tag, it uses defaults: type 0,
  cone 1.0, size 1.0 x 1.0, and white `(1, 1, 1)` in place of the vector. A
  warning identifies each missing or wrong-tag field and the default used
- **Intensity is relative.** It is divided by a calibration constant, 200 by default
  in the reference converter and not settable from the command line. It is not a
  photometric quantity. **No photometric claim is made**
- **Colour is not validated.** The field 28 vector may encode colour, but this
  was not confirmed. A neutral white is used by default
- The type values were interpreted from the other fields of the records (cone,
  size, shadow settings), not confirmed against the program
- The reference converter treats type values other than 0, 1 and 3 as spot
- After the radians-or-degrees rule the reference converter clamps the cone angle
  to the range 10 to 160 degrees
- Two nearby lights are never merged by default. Nearby records can be
  independent lights

## 8. Embedded textures

In the structured path, `Texture` channels give width, height and the raw payload,
which is kept with its hash. The role of a texture (for example base colour) was
not resolved and is not guessed. Payload signatures select a file extension
in the structured exporter. The simpler geometry scanning path does not extract
textures.

## 9. Synthetic example

The bytes below were built by hand with a short script. **No byte comes from a
real project file.** The type identifier is a placeholder (`0x11` x 16), not a
real Lumion identifier. Field names `a` and `g` are made up. The example is one
terminated instance with two fields: `a` has a four-float value and no child.
`g` has no value and a `Vertex Data` child with one triangle.

| Offset | Item | Bytes | Hex |
| ---: | --- | ---: | --- |
| 0 | ICUD | 40 | `49 43 55 44 20 00 00 00` + 32 x `00` |
| 40 | ICIC | 12 | `49 43 49 43 04 00 00 00 01 00 00 00` |
| 52 | ICTD | 24 | `49 43 54 44 10 00 00 00` + 16 x `11` |
| 76 | ICSI | 4 | `49 43 53 49` |
| 80 | INIC | 12 | `49 4e 49 43 04 00 00 00 02 00 00 00` |
| 92 | INIT | 4 | `49 4e 49 54` |
| 96 | IINW | 10 | `49 49 4e 57 02 00 00 00 61 00` |
| 106 | IIIS | 4 | `49 49 49 53` |
| 110 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 118 | INIT | 4 | `49 4e 49 54` |
| 122 | IINW | 10 | `49 49 4e 57 02 00 00 00 67 00` |
| 132 | IIIS | 4 | `49 49 49 53` |
| 136 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 144 | ICIF | 4 | `49 43 49 46` |
| 148 | IFSI | 4 | `49 46 53 49` |
| 152 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 160 | IIV1 | 24 | `49 49 56 31 10 00 00 00 00 00 00 3f 00 00 80 3e 00 00 00 3e 00 00 80 3f` |
| 184 | ENDL | 4 | `45 4e 44 4c` |
| 188 | IFNS | 4 | `49 46 4e 53` |
| 192 | IFNS | 4 | `49 46 4e 53` |
| 196 | IFSI | 4 | `49 46 53 49` |
| 200 | CHAC | 4 | `43 48 41 43` |
| 204 | CHIT | 12 | `43 48 49 54 04 00 00 00 01 00 00 00` |
| 216 | CHNW | 30 | `43 48 4e 57 16 00 00 00` + `Vertex Data` in UTF-16LE |
| 246 | CHIT | 12 | `43 48 49 54 04 00 00 00 01 00 00 00` |
| 258 | CHLC | 12 | `43 48 4c 43 04 00 00 00 01 00 00 00` |
| 270 | CHLI | 12 | `43 48 4c 49 04 00 00 00 00 00 00 00` |
| 282 | CHUL | 12 | `43 48 55 4c 04 00 00 00 00 00 00 00` |
| 294 | VRCO | 12 | `56 52 43 4f 04 00 00 00 03 00 00 00` |
| 306 | VPPI | 44 | `56 50 50 49 24 00 00 00` + f32 `0 0 0  1 0 0  0 1 0` |
| 350 | VNNI | 26 | `56 4e 4e 49 12 00 00 00` + i16 `0 0 32767` x 3 |
| 376 | VTD0 | 32 | `56 54 44 30 18 00 00 00` + f32 `0 0  1 0  0 1` |
| 408 | VTD1 | 32 | `56 54 44 31 18 00 00 00` + f32 `0 0  1 0  0 1` |
| 440 | PO32 | 20 | `50 4f 33 32 0c 00 00 00 00 00 00 00 01 00 00 00 02 00 00 00` |
| 460 | ENDI | 4 | `45 4e 44 49` |
| 464 | ^EN^ | 4 | `5e 45 4e 5e` |

Total 468 bytes, SHA-256
`5182482876d8004c734360c8b6d196e5ddef7265f56fcb3393b5fc722145465b`.
The script [example/make_example.py](example/make_example.py) builds these bytes
and checks the hash, so the example can be reproduced.
`61 00` and `67 00` are `a` and `g` in UTF-16LE. `00 00 00 3f` is f32 0.5.
The example names have no NUL character and end at the payload boundary.

Reading it with the grammar above consumes all 468 bytes and gives fields
`a = (0.5, 0.25, 0.125, 1.0)` and `g` = none, children `a` = none and
`g` = a `Vertex Data` channel with 3 vertices, one link pair `(0, 0)` and buffer
lengths 36, 18, 24, 24 and 12. The simpler `VPPI` -> `PO32` scan reads the same
triangle. Three altered copies must be rejected, and were:

- `ICUD` length set to 468: "chunk length outside source"
- final `^EN^` removed: "expected `^EN^`" at offset 464
- `VPPI` shortened to two vertices: "vertex attribute count mismatch"

A reader should pass the valid example and reject all three altered copies before
it is used on real files.

## 10. Limits

- These notes are not a complete file specification. A reader should stop at any
  case not described here
- Only `.ls10` project files (Lumion 10) were examined, and the derivation used
  one real project. `.lsf` files (Lumion 2023 and later) and the new file
  structure announced for Lumion 2025 were not tried
- The grammar covers the supported schemas and channel kinds. Others stop the
  reader. Reaching the end of the input does not mean every meaning is resolved
- The mapping between vertex buffers and model instances in files with several
  models is not fully resolved. The world matrix is used only in the single-model
  case
- Channel link pairs are stored but not resolved across the file
- Missing or wrong-tag light fields use defaults in the reference converter (section 7)
  and report each assumption rather than stopping conversion
- Lights: intensity is relative, colour is not validated, cone angle convention is
  not validated, and no photometry is claimed. The radians-or-degrees rule for the
  cone value misreads a cone stored in degrees below 6.3: a 5 degree spot would be
  taken as 5 radians (about 286 degrees) and then clamped to 160 degrees
- The reference converter accepts `.ls10` as its only Lumion project extension.
  Other versions and extensions were not validated
- UV transforms other than identity are reported, not applied. Texture roles,
  glass and shader parameters are not interpreted
- The simpler geometry scanning path does not extract embedded textures
- Field positions and quotas were established on the observed version. Other
  versions may differ. Unexpected data should stop a reader rather than be
  guessed

## Independence and trademarks

Independent work, not affiliated with, endorsed by or supported by Act-3D B.V.
Lumion® is a trademark of Act-3D B.V. Product names identify only the
formats and programs discussed.
