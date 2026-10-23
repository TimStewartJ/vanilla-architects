# Vanilla Architects

A small Minecraft **26.3 Fabric** client pack for vanilla survival, assisted
building and distant landscapes, with small enchanting/XP conveniences.
No new biomes, dimensions or ores.

Mighty Architectury **3.0.0** adds no blocks or items, so a server or LAN host
running it no longer turns away players who don't have it. The pack uses the
official published jar, not a private patched build.

## Install in Prism or the Modrinth App

Download `Vanilla-Architects-0.4.0.mrpack` from this private repository's
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
| The Mighty Architectury | 3.0.0 | Design buildings and export schematics |
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
| Entity Model Features | 3.3.12 | Animated mob models from resource packs (Fresh Animations) |
| Entity Texture Features | 7.2.6 | Entity texture features used by Fresh Animations |
| 3D Skin Layers | 1.11.4 | Renders skin overlay layers in 3D |
| Not Enough Animations | 1.12.6 | Extra player animations such as eating, maps and ladders |
| Sound Physics Remastered | 1.5.2 | Cave reverb and sound muffled by walls (upstream beta) |
| ImmediatelyFast | 1.17.1 | Faster entity, text and GUI rendering |
| EntityCulling | 1.11.3 | Skips rendering hidden entities and block entities |
| Double Doors | 7.5 | Both halves of a double door open together |
| Collective | 8.64 | Double Doors dependency |

Fabric Loader is pinned to **0.19.5**. REI, JEI, EMI and Architectury API are not
included. Neither are Create, AutoBuild or Litematica. Cloth Config stays only
because AppleSkin's actual Mod Menu integration and other selected mods need it.

### Resource packs

| Pack | Version | Notes |
| --- | --- | --- |
| [Fresh Animations](https://modrinth.com/resourcepack/fresh-animations) | 1.11.1 | Vanilla-style animated mobs |
| [Fresh Animations: Details](https://modrinth.com/resourcepack/fresh-animations-details) | 2.3.0 | Official extra mob details; place above Fresh Animations |
| [Fresh Animations: Player Extension](https://modrinth.com/resourcepack/fa-player-extension) | 1.1.0 | Official player animations; place above Fresh Animations |
| [CoffeePBR](https://modrinth.com/resourcepack/coffeepbr) | 1.0 (beta) | Vanilla-style PBR materials for Complementary or Bliss |

**Resource packs are not enabled automatically.** A modpack can only force them
on by overwriting each player's `options.txt` on every update, so the pack
leaves that choice to the player. In Options -> Resource Packs, move **Fresh
Animations** to the right, then **Details** and **Player Extension** above it.
Enable CoffeePBR only with Complementary or Bliss: it adds little without a
PBR shader and is a 45 MB upstream beta.

**0.4.0 updates The Mighty Architectury to 3.0.0** and adds the entity
animation, sound and rendering-performance mods above, Double Doors and four
optional resource packs. Existing pins are unchanged.
Its theme tools are now a blaze rod, lodestones and glazed terracotta; any old
Mighty Architect marker blocks in a world turn into air.
Double Doors is a gameplay mod: it works in single-player and on a LAN host
running the pack, and a dedicated server needs it plus Collective.

**0.3.0 added Tax Free Levels and Grind Enchantments,** both with their upstream defaults.

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

The output is `dist\Vanilla-Architects-0.4.0.mrpack` plus a SHA-512 file.
`--download` verifies every referenced binary, upstream version compatibility,
required dependencies, Fabric metadata and the shader archives.

CI also reuses Mighty Architectury's pinned production-client harness on
26.3 only, once for each included shader. It loads the exact pack jars into a
real client, joins a disposable test server, exercises the existing builder
checks and confirms the selected shader is active. The test companion is never
included in the pack. Screenshots and logs are kept in the per-shader
`runtime-evidence-*` CI artifacts. These are compatibility checks, not FPS
benchmarks.
The existing Fabric dedicated-server harness also runs with the dedicated-server
subset described below. The harness supplies Mighty Architectury itself; the
other ten pinned mods are added to its server runtime. This checks server
loading and the harness's existing world operations, not every enchanting interaction.
Only the test fixture skips BuildPrint's first-run tour and enables the three
Fresh Animations packs, so CI confirms they load with each shader; the exported
pack keeps the tour and leaves resource packs off. CoffeePBR is download- and
format-checked but not rendered in CI.

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
version, retain `side = "both"` for Tax Free Levels, Grind Enchantments, Double
Doors, Collective, Fabric API and Cloth Config, and `side = "client"` for the
other entries, including Sound Physics Remastered and the resource packs (packwiz
marks those `both` because of their Modrinth metadata). Run
`packwiz refresh` and the checks again. Do not hand-edit the generated
`index.toml` hashes. CI rejects
stale indexes, wrong targets, missing dependencies and mismatched downloads.

The `.mrpack` is reproducible from the committed files: archive order,
timestamps and permissions are normalized. CI artifacts are available for
branch builds. Version tags publish a private GitHub Release after validation.

## Multiplayer

The `.mrpack` is a **player instance**. Do not copy its complete mods folder
onto a server. For the gameplay changes on a dedicated Fabric 26.3 server, the
matching **Tax Free Levels, Grind Enchantments, Double Doors, Collective, Fabric
API and Cloth Config** files are required. Those six remain marked as required on
the server in the client `.mrpack`; its other entries are not automatically
installed there.

### Dedicated-server subset

To prepare the companion server installation from the same exact pack pins:

```powershell
python -m unittest discover -s tests -v
python scripts\build_server.py --install-dir build\server
```

The destination must be empty. The command verifies upstream Minecraft/loader
compatibility, dependency closure, download hashes and Fabric metadata before
installing these eleven mods:

| Component | Why it is on the server |
| --- | --- |
| Fabric API and Cloth Config | Gameplay-mod dependencies |
| Tax Free Levels and Grind Enchantments | The pack's enchanting/XP rules |
| Double Doors and Collective | Paired door opening (Collective is its library) |
| The Mighty Architectury | Faster printing (optional; players without it can still join) |
| Jade | Additional information for clients using Jade |
| Lithium and FerriteCore | Server game-logic and memory optimizations |
| Distant Horizons | Multiplayer LOD support using the client's pinned release |

These are the existing versions in the table above, not independently resolved
latest versions. BuildPrint and Sorted remain client-side; survival printing
still consumes the player's materials. Shader packs, Iris, Sodium, resource packs
and other client interfaces are not installed on the server.

The command also writes `dist\Vanilla-Architects-0.4.0-server.json` and its SHA-512
file. This manifest records the exact official download URLs, hashes, versions
and Fabric Loader/Minecraft requirements; it does not redistribute mod binaries.
CI includes it in the pack artifact and future release uploads.

Run the installed `mods` folder with **Minecraft 26.3, Fabric Loader 0.19.5 and
Java 25**. The export does not include Java, the Minecraft server, an accepted
EULA, a world, operator/whitelist entries, credentials or a managed backup
schedule. Preserve those deployment-specific settings separately.

For an existing world, first make and verify a save-consistent **off-host
backup**, test the conversion on a copy, and retain the original installation
for rollback. Do not open a world converted to 26.3 in an older server; restore
the pre-upgrade backup instead.

Both players should use the same pack version. Server rules still govern
building automation. Nothing here grants creative mode, operator permission
or free building materials. The prior 0.2.0 release remains available for
players who want the original vanilla enchanting rules.
