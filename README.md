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

## TODO

* [ ] Rewrite the argument parsing routine to use the modern `argparse` module instead of `getopt`.
* [ ] Add argument to write the PNG files to a specific directory, avoiding the need for write-permission on the fonts directory.
* [ ] [Support multi-line `--text`](https://stackoverflow.com/q/42014195), consider [migrating from pygame to pygame-ce](https://github.com/pygame-community/pygame-ce/issues/2735).
