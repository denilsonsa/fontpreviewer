# fontpreviewer

`fontpreviewer` is a nice little tool that generates PNG thumbnails of fonts,
and also generates a HTML file with all generated thumbnails.

It receives a list of font files as parameters, and writes a PNG image for each
font at the same directory. It requires write-permission to the directory with
the fonts.

It supports TTF, OTF (OpenType), and [any fonts supported by `pygame.freetype`](https://www.pygame.org/docs/ref/freetype.html).

## Requirements

* Python 3
* [pygame](https://www.pygame.org/)
    * pygame requires `SDL` and `FreeType`.
* [fonttools](https://github.com/fonttools/fonttools)
    * Optional, but recommended.
