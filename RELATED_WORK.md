# Related work

Addresses and published content were checked on 2026-09-27.

## Established patterns and method context

- **EA IFF 85** (Electronic Arts, 1985) describes chunks with a four-character
  identifier, a big-endian length and data. A copy of the original document:
  <https://1fish2.github.io/IFF/IFF%20docs%20with%20Commodore%20revisions/EA%20IFF%2085.pdf>
- **RIFF** (Microsoft documentation) describes FOURCC identifiers, little-endian
  chunk lengths and data, including alignment rules
  <https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff->
- **Conti et al. (2008), Visual Reverse Engineering of Binary and Data Files**
  discusses inspection of unfamiliar binary files as a general research method.
  It is cited for context, not as evidence for any `.ls10` record or as a tool
  used in this work. <https://doi.org/10.1007/978-3-540-85933-8_1>

The examined `.ls10` files use a four-byte tag and, for many records, a
little-endian length followed by a payload. This resembles the chunk framing
described for IFF and RIFF. The resemblance does not establish direct lineage
or identical grammar.

## Earlier public work on the Quest3D format

Quest3D was an earlier engine by Act-3D B.V., the company behind Lumion.

- **GingerLib** (GitHub organisation AudiosurfResearch), repository created
  2024-01-06, MIT licence.
  <https://github.com/AudiosurfResearch/GingerLib>
  A Rust crate for Quest3D channel-group (`.cgr`) files. Its source describes a
  file as a sequence of tags, each "a 4 character name and the data", with a
  4-byte little-endian length after the name. It notes one tag with no data,
  `A3DG`, used as the magic number and preceded by a tag holding the engine
  version. It also reads zlib-compressed and "protected" files. Its published code
  (read on 2026-09-27) reads and writes the tags as a container

- **"My Audiosurf/Quest3D reverse engineering journey"**, KC Forums, user m1nt_,
  2023-09-14, with replies up to 2026.
  <https://forum.mattkc.com/viewtopic.php?t=319>
  Describes the Quest3D engine (made by Act-3D B.V.), the `.cgr` files that store
  its channels, and the observation that uncompressed `.cgr` files look like
  RIFF

## Lumion support pages

- "Can you export 3D models from Lumion?"
  <https://support.lumion.com/hc/en-us/articles/360003475333-Can-you-export-3D-models-from-Lumion>
  States that Lumion projects and scenes, imported models, materials and textures
  cannot be exported to other 2D or 3D applications. These notes were written with
  this interoperability question in mind
- "How do you migrate Projects and Files to Lumion 2025 and newer?"
  <https://support.lumion.com/knowledge-base/api/v2/help_center/en-us/articles/19339275362332.json>
  States that project files of Lumion 12.5 and older use the extension
  `LS[major version]`, Lumion 2023 and later use `LSF`, and Lumion 2026/2025.0
  introduces "a completely new file structure for all data/file types". These
  notes cover `.ls10` only

## Context and credit

IFF and RIFF describe general chunk framing. GingerLib and the KC Forums post
describe related tag structures in Quest3D `.cgr` files. These sources are
credited for the patterns they actually discuss. None establishes the meaning
of the `.ls10` records in this note.

These notes document the positions of selected control words and the instance,
channel, vertex-buffer, world-transform and light records observed in the
examined `.ls10` project. The byte-level evidence and unresolved fields are
given in METHOD.md, sections 2 to 7. This is a record of observations, not a
claim of first discovery or completeness.

## Search scope and limits

The public materials listed here were reviewed on 2026-09-27. The search
included general web sources and GitHub but did not directly search every
forum, Reddit or format registry. Closed work may also exist. Absence from
this list is not evidence that a structure was previously undocumented.
An archived Quest3D SDK page cited in an earlier draft could not be verified
on 2026-09-28 and is not used for a technical claim.

## Code

No source code from these works is included. The short quotations above are
attributed to their sources.
