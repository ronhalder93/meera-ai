# MEERA 3D Character — Visual and Rig Specification

This specification records the user's approved visual reference for the MEERA character. The reference photo is kept in the conversation and is **not** copied to this public repository.

## Visual target

Create a realistic, adult Indian woman character with a natural, warm expression. Match the overall visible appearance of the approved reference without claiming an exact biometric reconstruction.

- **Saree:** white/light translucent saree with broad vivid hot-pink and lime-green panels/borders; soft fabric folds and a natural drape.
- **Blouse:** short-sleeved lime-green blouse.
- **Hair:** black hair, neatly pulled back into a bun; centre-parted front.
- **Face details:** small dark bindi, subtle natural makeup, expressive dark eyes, warm neutral smile.
- **Jewellery:** small silver-toned earrings, long ornate silver-toned necklace with a prominent pendant, and a simple bangle.
- **Body / pose:** anatomically natural adult proportions; full-body asset including feet. The reference photo crops the feet, so lower-leg/foot details must be completed plausibly rather than copied from the photo.
- **Style:** realistic 3D character, detailed but mobile-friendly materials and textures. Avoid a cartoon or anime look.

## Required deliverable

- One rigged humanoid character exported as **GLB**.
- Full-body mesh with clean topology and sensible deformation around shoulders, elbows, hips, knees, and ankles.
- Face and hair should remain stable during animation.
- Saree must be separate or suitably weighted cloth geometry so it moves naturally without clipping excessively.
- Include a neutral standing/rest pose and a basic preview thumbnail.
- Keep the model optimized for mobile browser viewing.

## Animation requirements

The GLB should contain named animation clips, at minimum:
- `idle` — relaxed breathing and subtle natural movement.
- `dance_gentle` — gentle standing dance with coordinated arms and torso.
- `dance_full` — fuller dance movement with safe foot placement and saree motion.
- `turn_360` — slow full-body turn for inspection.

Animations must be authored for the rig and embedded in the GLB; a static model or video is not a substitute.

## Viewer integration

The MEERA 3D Studio at `/static/3d-studio.html` is a viewer/tester only. Once a real rigged GLB with embedded clips exists, load it locally in the viewer to validate:
1. full-body framing and mobile performance;
2. clip names and playback;
3. skinning at joints;
4. saree clipping and material appearance.

## Honest status

This file is a production specification, **not** the 3D model itself. The photo-matched rigged GLB and dance clips still need to be generated/created and tested.