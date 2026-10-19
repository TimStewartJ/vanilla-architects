# Vanilla Architects

A small Minecraft **26.3 Fabric** client pack for vanilla survival, assisted
building and distant landscapes, with small enchanting/XP conveniences.
No new biomes, dimensions or ores.

Mighty Architectury **2.1.1** includes the 26.x shader-compatibility fix. The pack
uses the official published jar, not a private patched build.

## Install in Prism or the Modrinth App

Download `Vanilla-Architects-0.3.0.mrpack` from this private repository's
[Releases](https://github.com/TimStewartJ/vanilla-architects/releases).
Sign in to GitHub to access the private release.

- **Prism Launcher:** Add Instance -> Import -> select the `.mrpack`.
- **Modrinth App:** import the `.mrpack` as a new instance.
- Use **Java 25** and allocate **at least 4 GB**, preferably **6 GB** maximum
  memory before the first launch. Large builds or distant terrain can need more.
- Import into a **new instance**, not an existing world or another modpack.

The archive contains pinned download links and hashes, not redistributed mod
or shader binaries. The launcher downloads the files from Modrinth's CDN.
No account, token, world, test agent or personal launcher settings are included.
This is not a publicly listed Modrinth project.

## Included mods

All entries are the Fabric build for Minecraft 26.3.

| Mod | Version | Purpose |
| --- | --- | --- |
| The Mighty Architectury | 2.1.1 | Design buildings and export schematics |
| BuildPrint | 0.1.20 | Schematic previews, material lists and survival printing |
| Sorted | 0.1.27 | Sorting, quick stack and BuildPrint chest-stock integration |
| Jade | 26.3.5 | Block information |
| AppleSkin | 3.0.10 | Hunger and saturation information |
| Mouse Tweaks | 2.31 | Easier stack movement |
| Shulker Box Tooltip | 5.4.2 | Preview building supplies |
| Continuity | 3.0.1 | Connected textures for glass and other building materials |
| Presence Footsteps | 1.14.0 | Material-specific walking sounds |
| Spyglass Improvements | 1.6 | Adjustable spyglass zoom and quick access |
| Falling Leaves | 2.0.8 | Configurable falling-leaf particles |
| LambDynamicLights | 4.13.0 | Dynamic lighting from carried items and other light sources |
| Tax Free Levels | 1.5.4 | Predictable XP costs and no default "Too Expensive!" anvil limit |
| Grind Enchantments | 4.2.2 | Extract enchantments to books and split enchanted books |
| Sodium | 0.9.2 | Rendering performance |
| Lithium | 0.26.2 | Game-logic optimization |
| FerriteCore | 9.0.0 | Lower memory usage |
| Distant Horizons | 3.3.4 | Distant terrain LODs; official upstream release |
| Iris | 1.11.7 | Shader support; pinned to its required Sodium release |
| Fabric API | 0.163.0 | Shared Fabric APIs |
| YetAnotherConfigLib (YACL) | 3.9.7 | BuildPrint and Sorted configuration |
| Mod Menu | 21.0.0 | Access mod configuration |
| Text Placeholder API | 3.2.0 | Mod Menu dependency |
| Cloth Config API | 26.3.159 | Settings support for AppleSkin, Falling Leaves and Tax Free Levels |

Fabric Loader is pinned to **0.19.5**. REI, JEI, EMI and Architectury API are not
included. Neither are Create, AutoBuild or Litematica. Cloth Config stays only
because AppleSkin's actual Mod Menu integration and other selected mods need it.

**0.3.0 adds Tax Free Levels and Grind Enchantments.** All previous mod and
shader versions from 0.2.0 are retained. Both use their upstream defaults.

- **Tax Free Levels:** XP costs no longer increase merely because the player
  has a high XP level. Its defaults remove the anvil's "Too Expensive!" limit
  and make renaming cost one level; this does not make every action free.
- **Grind Enchantments:** place an enchanted item and a book in the grindstone
  to move its enchantments onto the book and keep the unenchanted item. You can
  also transfer enchantments between books.
- These are gameplay changes, not just client interfaces. They work in
  single-player and in a world opened to LAN by someone running this pack.
  A separate server needs the gameplay mods installed too; joining a vanilla
  server does not enable these mechanics there.

The Tax Free Levels jar is named `TaxFreeLevels-1.5.4-fabric-26.1.jar`; its
published version explicitly supports 26.3 despite that filename.

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

Continuity includes connected-texture and glass-pane resource packs, available
under Resource Packs. LambDynamicLights provides lighting without a shader
pack; if a shader already supplies hand lighting, avoid enabling duplicate
hand-light effects.

Sodium's **Use No Error GL Context** optimization is disabled. This avoids the
documented Iris/Sodium/Mesa shader-startup crash
([IrisShaders/Iris#3367](https://github.com/IrisShaders/Iris/issues/3367)).
Do not re-enable it while using this pinned rendering stack.

DH's optional garbage-collector advice popup is off: DH 3.3.4 can try to bake
its text inside an active Iris render pass. The same advice remains enabled in
the log, and real rendering exceptions still fail CI. Its built-in updater is
also off so it cannot replace the pack's pinned jar. If changing JVM options,
ZGC is DH's recommended collector on Java 25.

Other mod settings are left at their upstream defaults. Start with a normal
render distance around 12 chunks, then adjust Distant Horizons and shader
quality to your hardware. LOD generation uses background CPU and disk space;
terrain does not appear everywhere instantly.

## Survival building

BuildPrint opens a walkthrough on the first world join. Complete it or press
Esc; `/buildprint onboarding` opens it again later.

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

The output is `dist\Vanilla-Architects-0.3.0.mrpack` plus a SHA-512 file.
`--download` verifies every referenced binary, upstream version compatibility,
required dependencies, Fabric metadata and the shader archives.

CI also reuses Mighty Architectury's pinned production-client harness on
26.3 only, once for each included shader. It loads the exact pack jars into a
real client, joins a disposable test server, exercises the existing builder
checks and confirms the selected shader is active. The test companion is never
included in the pack. Screenshots and logs are kept in the per-shader
`runtime-evidence-*` CI artifacts. These are compatibility checks, not FPS
benchmarks.
The existing Fabric dedicated-server harness also runs with the two gameplay
mods and their dependencies loaded. This checks server loading and the
harness's existing world operations, not every enchanting interaction.
Only the test fixture skips BuildPrint's first-run tour; the exported pack
keeps it.

To verify an unmerged Mighty Architectury fix, manually run **Build modpack**
and set `mightyarchitect_ref` to its exact commit. That run tests the renderer
regressions and substitutes the newly built mod in the disposable runtime
fixture only. It records the source commit and jar hash, does not upload an
installable pack, and cannot publish a release. Normal builds and tags always
test the actual Modrinth-pinned jar. The compatibility fix was merged in
[TimStewartJ/TheMightyArchitectury#58](https://github.com/TimStewartJ/TheMightyArchitectury/pull/58).

To stage a clean installation for inspection, append
`--install-dir build\instance`. The destination must be empty; the script
never overwrites an existing instance.

For an intentional update, use packwiz's update command, review every changed
version, retain `side = "both"` for Tax Free Levels, Grind Enchantments, Fabric
API and Cloth Config, and `side = "client"` for the other entries. Run
`packwiz refresh` and the checks again. Do not hand-edit the generated
`index.toml` hashes. CI rejects
stale indexes, wrong targets, missing dependencies and mismatched downloads.

The `.mrpack` is reproducible from the committed files: archive order,
timestamps and permissions are normalized. CI artifacts are available for
branch builds. Version tags publish a private GitHub Release after validation.

## Multiplayer

This is primarily a **player instance**, not a complete managed server
distribution. Do not copy its complete mods folder onto a server. For the
enchanting changes on a dedicated Fabric 26.3 server, install the matching
**Tax Free Levels, Grind Enchantments, Fabric API and Cloth Config** files.
Those four are marked as required on the server in the `.mrpack`; rendering
and other client-only mods are not.

Both players should use the same pack version. Server rules still govern
building automation. Nothing here grants creative mode, operator permission
or free building materials. The prior 0.2.0 release remains available for
players who want the original vanilla enchanting rules.
