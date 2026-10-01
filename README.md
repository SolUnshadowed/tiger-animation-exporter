# <DO_NOT_FORGET_NAME>

A utility for parsing `s_animation_clip` tags binaries of Tiger engine (Destiny/Destiny 2/Marathon).

Supports animated codecs 0, 1, 2, 3 and static codec 3.

## Requirements

- Python 3.13+
- Install dependencies:

```bash
python -m pip install .
````

## Running

```bash
python3 main.py \
    -v <game_version> \
    --packages <path/to/game/packages>
    [-t <export_target>] \
    [--name-convention <name_convention>] \
    [--animation-space <space>] \
    [-i <json_indent>] \
```

### Arguments

- `-v`, `--version <game_version>` – game version the tags were extracted from. Supported values:
  - `d1_devalpha` - Destiny Internal Alpha
  - `d1_roi` – Destiny latest version (Rise of Iron)
  - `d2_eof` – Destiny 2 (Edge of Fate)
  - `marathon` – Marathon

- `-t`, `--target <export_target>` – export format. Supported targets:
  - `json_raw` – extracts data from the tag and writes it to a JSON file. Uses Z-up, X-forward coordinate order for translations and quaternions.
  - `json_retarget` – extracts animation data and retargets it according to provided skeleton and runtime rig constraints. Uses a Y-up, Z-forward coordinate system. Output is a JSON file.
  - `gltf_retarget` – same as `json_retarget`, but exports a GLTF file containing the armature and animation. Uses a Y-up, Z-forward coordinate system.
  - `glb_retarget` - same as `gltf_retarget`, but exports a GLB file. **Default option**

- `--name-convention <name_convention>` – naming convention for exported bones:
  - `fnv1le` – FNV-1 32-bit little-endian hash.
  - `fnv1le_no_zeroes` – FNV-1 32-bit little-endian hash with leading zeroes stripped.
  - `fnv1be` – FNV-1 32-bit big-endian hash. **Default**.
  - `fnv1be_no_zeroes` – FNV-1 32-bit big-endian hash with leading zeroes stripped.
  - `bungie` – attempts reverse hash lookup using known Bungie bone names, falling back to `fnv1be` if no match is found.
  - `blender` – uses Blender exporter addon names for skeletons when possible, falling back to `fnv1be` for unknown bones.

- `--animation-space <space>` - animation space:
  - `local` – bones' transforms are in parent local space. If `gltf_retarget` or `glb_retarget` is selected, hierarchical skeleton will be created. **Default**.
  - `object` - bones' transforms are in character's object space. If `gltf_retarget` or `glb_retarget` is selected, skeleton bones will be children of the same root.

- `-i`, `--json-indent <json_indent>` – number of spaces to use for JSON indentation. If omitted, the JSON will be output in a single line without indentation.

## References

This project was developed with reference to the following projects, articles,
and technical presentations:

- [3D Content Documentation](https://github.com/Bungie-net/api/wiki/3D-Content-Documentation) — Bungie-net
  - Render stages and LODs 

- [alkahest](https://github.com/cohaereo/alkahest) — cohaereo
  - Render stages mechanism

- [Creating Content to Drive Destiny's Investment Game](https://advances.realtimerendering.com/destiny/siggraph2014/bungie_gear_production_siggraph_2014_web_ready.pdf) — Natalya Tatarchuk (SIGGRAPH 2014)
  - Player gear geometry parts and textures

- [Destiny: From Mythic Science Fiction to Rendering in Real-Time](https://advances.realtimerendering.com/s2013/Tatarchuk-Destiny-SIGGRAPH2013.pdf) — Natalya Tatarchuk (SIGGRAPH 2013)
  - Destiny 1 shading and lighting systems

- [Destiny Character-Animation System and Lessons Learned](https://advances.realtimerendering.com/destiny/siggraph2014/animation/index.html) (SIGGRAPH 2014):
  - [Design and Animation in Destiny](https://advances.realtimerendering.com/destiny/siggraph2014/animation/destiny_animation_and_design_siggraph_2014_public.pptx) - Joe Spataro
  - [Destiny's Runtime Animation Rig](https://advances.realtimerendering.com/destiny/siggraph2014/animation/bungie_runtime_rig_siggraph_2014_web_ready.pptx) - Tam Armstrong
  - [Animation Layers](https://advances.realtimerendering.com/destiny/siggraph2014/animation/animation_layers_in_destiny_siggraph_2014_public.pptx) - Joe Spataro

- [Character Heads Creation Pipeline and Rendering in Destiny course](https://advances.realtimerendering.com/destiny/siggraph2014/heads/index.html) (SIGGRAPH 2014):
  - [FACE ANIMATION RETARGETING IN DESTINY](https://advances.realtimerendering.com/destiny/siggraph2014/heads/siggraph_2014_destiny_face_pipeline.pptx) - Jason G. Jones, and Tom Sanocki
