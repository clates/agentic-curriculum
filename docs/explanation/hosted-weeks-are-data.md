# Why hosted weeks are data

On the hosted app, a model writes every week. The server then turns that week into printable
pages. Rendering it must never run code the model wrote, read arbitrary files, or fetch anything
over the network. So a hosted week is data, not a program: a structured document the server checks
against a schema (`src/weekdoc/models.py`) before rendering it with its own code.

## Why pictures are the hard part

Text is easy to keep safe. Pictures aren't. If a worksheet could name an image, by path, URL or
`data:` URI, a model could point the renderer at a file on the server, at a remote address, or at
bytes nobody has looked at. So a hosted worksheet names no image at all.

Instead, the renderer draws the pictures it understands from small, bounded data: a shape named
from a fixed list, a clock from an hour and a minute, a dot array from a row and column count.
Emoji count as text, so they are allowed too. Colours are limited to `#rrggbb` because they're
written straight into SVG attributes, and a looser format could break out of them.

Some kinds lose something as a result. A labeled diagram prints an empty, numbered frame for the
child to draw in, and raster art can't be hosted at all. Exactly which kinds are hosted, and how,
is in [Hosted images](../reference/hosted-images.md).

## A way to add drawn diagrams later

If pre-drawn diagrams are wanted, one shape keeps the rule intact: a reviewed library of SVG files
committed to the repo, each with an id such as `diagram_id: "plant-parts"`. The model could only
pick an id. It could never supply the bytes or a path. This isn't built. It needs someone to
commission and review the drawings.

## Why answers are kept apart

Answer-only fields (`show_answers`, a story map's `value`, an error audit's `bug_location`,
`diagnosis` and `fix_text`) aren't part of the child's data. Answers live in the worksheet's
`answers`, keyed by item, so the student packet and the teacher guide are built from separate
data. The child's pages can't print an answer by accident.

Related: [Why a week is a script](why-a-week-is-a-script.md) covers the offline path, where the
trade-off goes the other way.
