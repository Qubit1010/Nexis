# NexusPoint business-card variations

All three directions retain the approved Soft Fold logo, exact #02A1E1 centre, Conthrax display lettering and Inter contact copy. No Portfolio caption appears beneath the QR. Every QR encodes https://nexus-point.co/work.

## Compare

Open comparison.html for a responsive front-and-back viewer, or comparison.png for the complete sheet.

- 01 Ribbon Flow: curved ribbons and a quiet black field. Preview: 01-ribbon-flow-proof.png.
- 02 Orbital Field: an enlarged symbol, circular paths and an asymmetric blue reverse. Preview: 02-orbital-field-proof.png. Recommended balance of visual character and readable contact details.
- 03 Folded Edge: architectural folds with a bright white reverse. Preview: 03-folded-edge-proof-spacing-fixed.png.

These are earlier exploration options. The current master card is the approved 3C Diagonal Wrap refinement.

## Files

Each direction supplies native front/back SVGs, 1125 x 675 PNGs at 300 ppi and a two-page print PDF, front then back. Media size is 3.75 x 2.25 inches, trim is 3.5 x 2 inches, and bleed is 0.125 inch. Text is outlined. No private font binary is embedded. Colours are sRGB; the existing kit print guidance applies.

The QR was decoded from all three back PNGs and all three rendered back PDF pages. Text bounds were checked against the card safe area. SVGs contain paths and real QR modules, with no raster images or live font dependence.

Rebuild with scripts/build-card-variations.py, scripts/render-card-variations.cjs and scripts/validate-card-variations.py. The Python validation accepts --qr-python for an OpenCV-enabled interpreter. These scripts resolve from the kit root and use its existing logo and local font files.

## Preferred family and refinements

Aleem preferred Folded Edge. Its divider now has a visible gap above the service caption. Three refinements are in ../folded-edge-variations/. 3C Diagonal Wrap is the approved final refinement.
