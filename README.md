# Vanilla Architects

A small Minecraft **26.3 Fabric** client pack for vanilla survival, assisted
building and distant landscapes. No new biomes, dimensions, ores or progression.

## Install in Prism or the Modrinth App

Download `Vanilla-Architects-0.1.0.mrpack` from this private repository's
[Releases](https://github.com/TimStewartJ/vanilla-architects/releases).
Sign in to GitHub to access the private release.

- **Prism Launcher:** Add Instance -> Import -> select the `.mrpack`.
- **Modrinth App:** import the `.mrpack` as a new instance.
- Use **Java 25**. Start with **6 GB** maximum memory; 4 GB is a lower-end
  starting point, and large builds or distant terrain can need more.
- Import into a **new instance**, not an existing world or another modpack.

The archive contains pinned download links and hashes, not redistributed mod
or shader binaries. The launcher downloads the files from Modrinth's CDN.
No account, token, world, test agent or personal launcher settings are included.
This is not a publicly listed Modrinth project.

## Included mods

All entries are the Fabric build for Minecraft 26.3.

| Mod | Version | Purpose |
| --- | --- | --- |
| The Mighty Architectury | 2.1.0 | Design buildings and export schematics |
| BuildPrint | 0.1.20 | Schematic previews, material lists and survival printing |
| Sorted | 0.1.27 | Sorting, quick stack and BuildPrint chest-stock integration |
| Jade | 26.3.5 | Block information |
| AppleSkin | 3.0.10 | Hunger and saturation information |
| Mouse Tweaks | 2.31 | Easier stack movement |
| Shulker Box Tooltip | 5.4.2 | Preview building supplies |
| Sodium | 0.9.2 | Rendering performance |
| Lithium | 0.26.2 | Game-logic optimization |
| FerriteCore | 9.0.0 | Lower memory usage |
| Distant Horizons | 3.3.4 | Distant terrain LODs; official upstream release |
| Iris | 1.11.7 | Shader support; pinned to its required Sodium release |
| Fabric API | 0.163.0 | Shared Fabric APIs |
| YetAnotherConfigLib (YACL) | 3.9.7 | BuildPrint and Sorted configuration |
| Mod Menu | 21.0.0 | Access mod configuration |
| Text Placeholder API | 3.2.0 | Mod Menu dependency |

Fabric Loader is pinned to **0.19.5**. REI, JEI, EMI, Cloth Config and
Architectury API are not included. Neither are Create, AutoBuild or Litematica.

### Shader choices

All three are included as selectable shader packs, with Distant Horizons
programs:

| Shader | Version | Why it is here |
| --- | --- | --- |
| [I Like Vanilla](https://modrinth.com/shader/i-like-vanilla) | 1.5.0b | The vanilla-focused first choice |
| [Complementary Reimagined](https://modrinth.com/shader/complementary-reimagined) | r5.9.3 | A reworked Minecraft look with quality presets |
| [Bliss](https://modrinth.com/shader/bliss-shader) | 2.1.2 | A different landscape and atmosphere option |

**Shaders are off on first launch.** In Video Settings -> Shader Packs, enable
them and choose one pack. Only one shader runs at a time. The vanilla-focused
choice is preselected, but is not enabled automatically.

Other mod settings are left at their upstream defaults. Start with a normal
render distance around 12 chunks, then adjust Distant Horizons and shader
quality to your hardware. LOD generation uses background CPU and disk space;
terrain does not appear everywhere instantly.

## Survival building

1. Press **G** to design with Mighty Architectury and choose vanilla materials.
2. Save the design as a schematic in the shared `schematics` folder.
3. Open BuildPrint with **M**, load the `.nbt`, and position the preview.
4. Check the material list and gather supplies. Sorted adds remembered chest
   counts; on multiplayer these can become stale.
5. Use BuildPrint's easy placement or enable its printer. The printer consumes
   blocks you carry and only works within normal reach: walk and scaffold
   through the building.

This is not a chest-fed, unattended Schematicannon. Creative paste is not the
survival building method. Printer features are off by default; on a server,
check whether automated placement is allowed.

The pack uses Mighty Architectury's existing `.nbt` export. Separate export
format development is not required by, or bundled into, this repository.

## Rebuild and update

Source format: [packwiz](https://packwiz.infra.link/). Each `.pw.toml` pins the
exact Modrinth project, version, URL and SHA-512.

Use Python **3.11+** and packwiz built from commit
`170b22d785959dda5876b54b7f16e1b807a57fb6`:

```powershell
python -m unittest discover -s tests -v
python scripts\build_pack.py --packwiz C:\path\to\packwiz.exe --download
```

The output is `dist\Vanilla-Architects-0.1.0.mrpack` plus a SHA-512 file.
`--download` verifies every referenced binary, upstream version compatibility,
required dependencies, Fabric metadata and the shader archives.

CI also reuses Mighty Architectury's pinned production-client harness on
26.3 only. It loads the exact released pack jars into a real client, joins a
disposable test server, exercises the existing builder checks and enables
I Like Vanilla for the run. The test companion is never included in the pack.
Screenshots and logs are kept in the `runtime-evidence` CI artifact. The other
two shaders are integrity-checked, not visually benchmarked.

To stage a clean installation for inspection, append
`--install-dir build\instance`. The destination must be empty; the script
never overwrites an existing instance.

For an intentional update, use packwiz's update command, review every changed
version, retain `side = "client"` on each entry, run `packwiz refresh`, and run
the checks again. Do not hand-edit the generated `index.toml` hashes. CI rejects
stale indexes, wrong targets, missing dependencies and mismatched downloads.

The `.mrpack` is reproducible from the committed files: archive order,
timestamps and permissions are normalized. CI artifacts are available for
branch builds. Version tags publish a private GitHub Release after validation.

## Multiplayer

This is a **client pack**, not a server distribution. Do not copy its complete
mods folder onto a server. Players can join a compatible vanilla/Fabric server;
server rules still govern building automation. Nothing here grants creative
mode, operator permission or free building materials.
