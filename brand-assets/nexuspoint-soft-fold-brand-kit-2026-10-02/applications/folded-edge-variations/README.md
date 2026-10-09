# Folded Edge refinements

Aleem preferred 03 Folded Edge and requested more variations, with space between the divider and AI SYSTEMS & AUTOMATION. The divider is now 25 artwork pixels higher, leaving approximately 25.8 pixels, 2.18 mm at print scale, between its stroke and the caption ink.

## Directions

- 3A Soft Edge: a gently curved edge that echoes the Soft Fold logo.
- 3B Layered Fold: sharper overlapping facets, closest to the preferred original. Retained as an earlier option.
- 3C Diagonal Wrap: a stronger diagonal sweep and a bolder silhouette.

comparison.html is the responsive viewer. comparison.png is the full sheet. Each direction also has a paired proof PNG, native front/back SVGs, 300 ppi PNGs, and a two-page print PDF. Front is page 1, back is page 2.

The corrected original preview is ../card-variations/03-folded-edge-proof-spacing-fixed.png. The earlier proof remains historical and is excluded from the current shared ZIP.

## Production

Trim 3.5 x 2 inches, with 0.125 inch bleed. Media size 3.75 x 2.25 inches. Native foreground logo, lettering and QR groups are unchanged from Folded Edge. QR opens https://nexus-point.co/work, with no Portfolio caption. All contacts are preserved.

QR codes were decoded from every back PNG and every 300 ppi print-PDF page rendering. All six native card sides and print layouts were visually reviewed. The existing kit colour-proof guidance applies.

Rebuild:

1. Python scripts/build-card-variations.py
2. Python scripts/build-folded-edge-variations.py
3. Node scripts/render-card-variations.cjs --directory=folded-edge-variations
4. Python scripts/validate-card-variations.py --directory folded-edge-variations --qr-python <OpenCV interpreter>

The refinement builder uses the supplied native source SVGs and does not require the private display-font binaries. **3C Diagonal Wrap is the final approved card, locked by Aleem on 2 October 2026.** The application master files contain this artwork; 3A and 3B remain references.
