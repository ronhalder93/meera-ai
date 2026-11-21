# MEERA outfit controls — free and persistent

## Product behavior

Outfit controls are a standard, free character-customization feature. They must not be premium-gated, paywalled, or disabled based on subscription tier.

The user can independently show/hide each clothing/accessory layer:
- Saree
- Blouse
- Bra / innerwear (only if present as a separate mesh)
- Jewellery
- Hair accessories

Provide a master **Outfit / Nude Mode** toggle. Turning it on hides all clothing and accessories, revealing the adult anatomical base mesh. Turning it off restores the user's previously selected outfit state; it must not silently re-equip items the user had individually disabled.

## State and persistence

Use an explicit per-character outfit state, for example:

```json
{
  "characterId": "meera",
  "outfit": {
    "saree": true,
    "blouse": true,
    "innerwear": true,
    "jewellery": true,
    "hairAccessories": true
  },
  "mode": "outfit"
}
```

- Persist changes automatically; no separate save button.
- Restore the last selected state when the character/viewer is reopened.
- Persist per user and per character when accounts are available; use local storage only as a temporary guest fallback.
- Animation playback must never reset outfit state. Idle, dance, and turn clips all use the same selected visibility state.
- Switching modes must change mesh visibility only; it must not replace the character, reset the rig, or interrupt the current animation.
- If a garment is absent from the GLB, its control should be disabled/hidden rather than pretending it can be removed.

## 3D asset requirements

Each removable garment/accessory must be a separately named mesh or node in the GLB (stable names such as `Clothing_Saree`, `Clothing_Blouse`, `Clothing_Innerwear`, `Accessory_Jewellery`). The anatomical base remains the same rigged character underneath. Export and validate the node names in the GLB.

## Acceptance tests

- [ ] All controls are available without a paid plan.
- [ ] Hiding/showing each layer affects only that layer.
- [ ] Master mode hides/restores layers without losing the prior per-item selections.
- [ ] A reload restores the saved selection.
- [ ] Idle, dance_gentle, dance_full, and turn_360 preserve the chosen outfit state.
- [ ] The same base identity and armature remain active in every mode.
- [ ] No garment controls claim to work unless the corresponding separate GLB node exists.

## Implementation status

This document defines the required behavior. The current generated GLB is a first-pass character asset; separate removable garment-node validation and viewer UI/persistence wiring have not yet been completed. Do not claim the toggle is live until those checks pass.
