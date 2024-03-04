# fontpreviewer

`fontpreviewer` is a nice little tool that generates PNG thumbnails of TTF
fonts, and also generates a HTML file with all generated thumbnails.

It receives a list of TTF files as parameters, and writes a PNG image for
each file at the same directory. It requires write-permission to the
directory with the fonts.

## Requirements

* Python 3
* [pygame](https://www.pygame.org/)
    * pygame requires `SDL` and `SDL_ttf`.
* [fonttools](https://github.com/fonttools/fonttools)
    * Optional, but recommended.
