# Hosted image rule

Hosted weeks are data. Rendering must not run model-written code, read arbitrary files, or fetch
anything over the network (product design; see `src/weekdoc/kinds_visual.py`).

**Rule: a hosted worksheet carries no image reference.** No `image_path`, URL, or `data:` URI in
`Worksheet.data`. A picture on a hosted page is one of:

1. Procedural inline SVG or HTML drawn by the renderer from structured, bounded data: shapes by
   enum name (`circle|square|rectangle|triangle`), clocks (`hour`, `minute`), dot arrays
   (`rows`, `cols`), fraction wedges (`parts`), Venn circles from labels, the decimal-stack grid.
2. Text, including emoji characters (glyphs, not files).

Colours are `#rrggbb` only, because the renderer writes them into SVG attributes unescaped.

Kinds that need a picture the renderer cannot draw are either hosted without it or not hosted:

| Kind | Hosted as |
|------|-----------|
| `shapeIdWorksheet` | all five modes; shapes from the enum |
| `errorAuditWorksheet` | clock, dots, partitions art; decimal scaffold |
| `pictureSequenceWorksheet` | emoji glyph cards |
| `vennDiagramWorksheet`, `storyMapWorksheet` | text only |
| `labeledDiagramWorksheet` | without `image_path`: the page prints the numbered, framed diagram box and the child draws or glues the picture |
| any PIL/raster art (photos, logos, `image_path` on handwriting/labeled) | not hosted: cannot be produced deterministically from structured data |

Extension point if pre-drawn diagrams are wanted: a vetted bundled library of SVGs, referenced by
id (`diagram_id: "plant-parts"`), resolved to inline SVG inside the weekdoc render step from files
committed to the repo and reviewed. The model could then only pick an id, never supply bytes or a
path. Not built; it needs someone to commission and review the library.

Answer-only fields (`show_answers`, story-map `value`, error-audit `bug_location`, `diagnosis`,
`fix_text`) are not hosted data; answers live in the worksheet's `answers` by `item_ref`.
