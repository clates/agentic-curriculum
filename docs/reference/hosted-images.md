# Hosted images

What a worksheet in a hosted week may contain in place of an image. Why the rule exists:
[Why hosted weeks are data](../explanation/hosted-weeks-are-data.md). Code:
`src/weekdoc/kinds_visual.py`.

## Rule

A hosted worksheet carries no image reference. `Worksheet.data` must not contain an `image_path`,
a URL or a `data:` URI.

## Allowed pictures

| Source | Data it is drawn from |
|---|---|
| Shapes | `circle`, `square`, `rectangle` or `triangle`, by name |
| Clocks | `hour`, `minute` |
| Dot arrays | `rows`, `cols` |
| Fraction wedges | `parts` |
| Venn circles | labels |
| Decimal grid | the decimal-stack scaffold |
| Emoji | text characters, not files |

Colours: `#rrggbb` only.

## Kinds

| Kind | Hosted as |
|------|-----------|
| `shapeIdWorksheet` | all five modes; shapes from the list above |
| `errorAuditWorksheet` | clock, dots and partitions art; decimal scaffold |
| `pictureSequenceWorksheet` | emoji cards |
| `vennDiagramWorksheet`, `storyMapWorksheet` | text only |
| `labeledDiagramWorksheet` | without `image_path`: a numbered, framed diagram box the child draws in or glues a picture into |
| PIL or raster art (photos, logos, `image_path` on handwriting or labeled diagrams) | not hosted |

## Answer fields

`show_answers`, story-map `value`, and error-audit `bug_location`, `diagnosis` and `fix_text` are
not hosted data. Answers go in the worksheet's `answers`, keyed by `item_ref`.
