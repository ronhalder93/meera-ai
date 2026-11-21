# MEERA 3D Character — Visual, Build Order, Rig and Delivery Specification

This is the source-of-truth production brief for the MEERA character. The approved reference photo remains in the user's conversation and is **not** copied into this public repository.

## Non-negotiable build order

Build one character identity in this order. Do not create a separate replacement character for the clothed stage.

1. **Adult anatomical base first.** Create a clearly adult woman (age 25+), full-body, realistic non-erotic anatomical base in a neutral A-pose. Include head, face, ears, neck, torso, arms, hands, fingers, legs, feet and toes. The base is an anatomy/rigging asset, not a sexualized render.
2. **Indian appearance second.** Preserve the same base mesh, face identity, body proportions and rig. Add the approved Indian styling, hair, clothing and jewellery as layers/accessories. Do not regenerate a different face or body.
3. **Rig and deformation.** Build and test the humanoid skeleton, facial controls where feasible, skin weights and cloth setup.
4. **Animation.** Author the named clips on this same rig and export them embedded in the final GLB.
5. **Viewer validation.** Test the exported asset in `/static/3d-studio.html` on desktop and mobile.

## Stage 1 — Adult anatomical base

- Clearly adult female anatomy and proportions; realistic, non-exaggerated anatomy.
- Neutral A-pose, feet planted, symmetrical alignment, consistent scale and forward-facing orientation.
- Full body including hands, individual fingers, feet and toes; no cropped or missing geometry.
- Clean, deformation-friendly topology with sensible edge flow around shoulders, elbows, wrists, hips, knees, ankles, mouth and eyes.
- Separate or clearly organized eye, teeth, tongue, scalp/hairline and body materials as appropriate.
- UVs and PBR material slots; realistic skin detail without excessive texture resolution.
- No pose-dependent mesh intersections; no hidden holes or non-manifold geometry.
- Keep this base identity as the canonical source for every later stage.

## Stage 2 — Approved Indian styling

Apply styling to the Stage 1 character while preserving identity and rig:

- **Saree:** white/light translucent saree with broad vivid hot-pink and lime-green panels/borders; soft fabric folds and a natural drape.
- **Blouse:** short-sleeved lime-green blouse.
- **Hair:** black hair, neatly pulled back into a bun; centre-parted front.
- **Face details:** small dark bindi, subtle natural makeup, expressive dark eyes, warm neutral smile.
- **Jewellery:** small silver-toned earrings, long ornate silver-toned necklace with a prominent pendant, and a simple bangle.
- **Body / pose:** retain the anatomically natural adult body; full-body asset including feet. The reference photo crops the feet, so lower-leg/foot details must be completed plausibly.
- **Style:** realistic 3D character, detailed but mobile-friendly materials and textures. Avoid cartoon/anime styling.

Clothing must be separate or suitably layered geometry. Ensure blouse/saree fit the same base body and do not replace or reshape the underlying identity.

## Stage 3 — Rig and deformation

- Humanoid skeleton with root, pelvis, spine, chest, neck, head, clavicles, arms, hands/fingers, legs and feet.
- Clean skin weights with smooth transitions at shoulders, elbows, wrists, hips, knees and ankles.
- Test a range of joint bends before approving the rig.
- Keep face and hair stable during movement.
- Saree should use suitable cloth simulation/baked motion or carefully weighted geometry, with practical clipping control.
- Preserve a neutral rest pose and consistent axis/scale for export.

## Stage 4 — Required animation clips

Embed these named clips in the final GLB:
- `idle` — relaxed breathing and subtle natural movement.
- `dance_gentle` — gentle standing dance with coordinated arms and torso.
- `dance_full` — fuller dance movement with safe foot placement and saree motion.
- `turn_360` — slow full-body turn for inspection.

Animations must be authored for this rig and embedded in the GLB; a static model, video, or separate animation preview is not a substitute.

## Deliverables and repository layout

Expected outputs (do not mark complete until actual files exist and have been tested):

- `assets/character/meera_base.blend` — editable adult anatomical base scene.
- `assets/character/meera_base.glb` — optional base-stage interchange export.
- `assets/character/meera_final.blend` — dressed, rigged source scene.
- `assets/character/meera_final.glb` — final mobile-ready rigged character with embedded clips.
- `assets/character/meera_preview.png` — full-body preview of the final clothed look.
- `assets/character/validation.md` — export details and test results.

If binary assets are stored outside Git (for example, via Git LFS or object storage), document their exact stable location and verify that the viewer can fetch them.

## Acceptance checklist

- [ ] Base model is clearly adult and full-body, with complete hands and feet.
- [ ] Base model has clean topology, UVs and usable material slots.
- [ ] Final Indian look uses the same base identity and proportions.
- [ ] Saree, blouse, hair and jewellery are present and fit correctly.
- [ ] Humanoid rig deforms correctly at all major joints.
- [ ] All four named animation clips are embedded and play correctly.
- [ ] GLB opens in the MEERA 3D Studio viewer.
- [ ] Desktop and mobile framing/performance are checked.
- [ ] No missing textures, broken materials, severe clipping or broken skinning.

## Current status — do not overstate

The repository currently contains the viewer/tester and this production specification. The viewer is **not** a model generator. No actual base mesh, dressed character, rigged GLB, animation clips or preview image should be considered delivered until the corresponding asset files are present and validated.
