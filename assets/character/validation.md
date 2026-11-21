# MEERA character build validation

Build workflow: [successful run #44920767816](https://github.com/ronhalder93/meera-ai/actions/runs/44920767816) · [workflow](https://github.com/ronhalder93/meera-ai/actions/workflows/meera-character-build.yml)

## Generated outputs

The workflow produces these files as the `meera-adult-base` artifact:

- `meera_base.blend` — editable adult anatomical base scene.
- `meera_base.glb` — base character export.
- `meera_final.blend` — editable dressed character scene.
- `meera_final.glb` — dressed character with the humanoid armature and named animation actions.
- `meera_preview.png` — front preview render.

## Automated checks

- Blender background build completes.
- MPFB2 creates the adult human mesh and humanoid game-engine rig.
- Base and final GLB exports are written.
- The final scene includes the saree wrap and pallu, lime blouse, hair bun, bindi, necklace, pendant and bangles.
- The final GLB embeds four named animation clips: `idle`, `dance_gentle`, `dance_full`, and `turn_360` (confirmed in the GLB animation metadata).
- The workflow verifies that the expected binary deliverables exist and uploads them as a downloadable artifact.

## Known limitations

- The costume is a procedural first pass, not a photo-matched couture garment. Saree folds, blouse fit, face details, hair styling and jewellery need a visual-art refinement pass.
- The animation actions are procedural blocking motions; they have not been professionally motion-captured or fully reviewed for natural biomechanics.
- The workflow validates successful export and file presence. It does not replace manual playback/deformation QA in the MEERA 3D Studio viewer on desktop and mobile.
- The reference photo itself is not stored in this repository; the build follows the written reference notes.

Do not describe the asset as production-final until the visual and animation review checklist in `meera-character-spec.md` is completed.
