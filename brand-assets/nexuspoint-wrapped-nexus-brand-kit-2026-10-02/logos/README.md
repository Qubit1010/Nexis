# Wrapped Nexus logo assets

Approved reference: `reference/approved-wrapped-nexus-original.png`, preserved untouched.

The master is a faithful, editable contour reconstruction of the approved raster. Four original emblem contours are fitted to cubic Bézier paths. The original lettering is traced with its counters intact and labelled a custom outlined wordmark. No exact font identity is claimed for the generated logo.

The central point is a true SVG circle in the verified portfolio blue, `#02A1E1`. All whites are flat `#FFFFFF`. The alternate logo navy is `#02040A`. Slight irregularities from the generated source are retained; this is not a claim that an original designer vector was recovered.

## Choosing a file

- `nexuspoint-primary-black.svg`: primary horizontal lockup on portfolio black.
- `nexuspoint-primary-dark.svg`: horizontal lockup on the retained navy.
- `nexuspoint-outline-master.svg`: complete horizontal logo, outlined and transparent, with white ribbons and lettering.
- `nexuspoint-symbol-transparent-white.svg`: symbol only for dark backgrounds.
- `nexuspoint-symbol-transparent-navy.svg`: symbol only for light backgrounds.
- `nexuspoint-wordmark-white.svg` / `nexuspoint-wordmark-navy.svg`: original outlined lettering alone.
- `nexuspoint-stacked-*.svg`: centred vertical lockups.
- `nexuspoint-favicon.svg`: symbol centred on a square navy canvas with a small inset.

For each of the primary, stacked and symbol layouts, the suffixes are:

| Suffix | Artwork | Canvas |
|---|---|---|
| `black` | White + blue | Black `#000000` |
| `dark` | White + blue | Navy `#02040A` |
| `light` | Navy + blue | White |
| `transparent-white` | White + blue | Transparent |
| `transparent-navy` | Navy + blue | Transparent |
| `mono-white` | White including centre point | Transparent |
| `mono-navy` | Navy including centre point | Transparent |
| `mono-black` | Black including centre point | Transparent |

`png/` contains raster exports from these new SVGs, not edited source images. Primary exports are 2400px wide, stacked exports 1600px wide, and symbols 1200px wide. Transparent variants keep their alpha channel.

`favicons/` contains 16, 32, 48, 64, 128, 180, 192, 256 and 512px square PNGs plus a multi-resolution `favicon.ico`. The 16px version is recognisable but loses fold detail. Use at least 32px for the full-detail symbol, ideally 48px or larger. A primary logo width of 240px or larger is recommended. Preserve at least one centre-dot diameter of clear space, approximately 0.28 times symbol height, in the surrounding layout. SVG export canvases are tight artwork bounds and do not themselves provide the full recommended placement clear space.

## Rebuild

From the kit directory, with Python packages `numpy`, `opencv-python`, `Pillow` and `scikit-image`, and a Node.js installation with `sharp`:

```powershell
python scripts/build-logo-assets.py
node scripts/build-logo-assets.cjs
python scripts/build-logo-assets.py --verify
```

If `sharp` is outside the normal package search path, set `NODE_PATH` to its parent `node_modules` directory before the Node command.

## Validation

`validation-report.json` records measured silhouette fidelity, native SVG checks, exact blue verification, PNG decoding, ICO sizes, source SHA-256 and visual small-size review. At original raster scale, the reconstructed outline boundaries differ by no more than 1px for the symbol and 1.4px for the wordmark under the recorded threshold comparison. The original raster colour shading is intentionally not reproduced in flat vector assets.

`png/nexuspoint-*-native-scale-qa.png` and `png/favicon-size-review.png` are diagnostic exports, not recommended placement assets.
