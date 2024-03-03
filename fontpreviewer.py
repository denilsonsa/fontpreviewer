#!/usr/bin/env python
# -*- coding: us-ascii -*-

import getopt
import os.path
import sys

import pygame
from pygame.font import Font

try:
    from fontTools import ttLib
    from ttfquery import describe
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False


def render_font_to_file(fontfile, text, fontsize, antialias=True, background=None):
    font = Font(fontfile, fontsize)

    # Despite what the documentation implies, Font.render() does not support
    # None as the "background" parameter. You must either omit it, or pass a
    # RGBA tuple.
    if background == None:
        surf = font.render(text, antialias, (0,0,0))
    else:
        surf = font.render(text, antialias, (0,0,0), background)

    pngfile = os.path.splitext(fontfile)[0] + '.png'
    pygame.image.save(surf, pngfile)


class FontMetadata(object):
    def __init__(self,fontfile):
        if not HAS_FONTTOOLS:
            return
        # describe.shortName(font)
        #   This will return (font_name, font_family), like this:
        #   ("MyFont Bold Italic","MyFont")
        #   ("MyFont","MyFont")
        # describe.family(font)
        #   This will return the font families based on some internal integer.
        #   For "Arial Unicode MS", it returns ("SANS","GOTHIC-NEO-GROTESQUE").
        #   For many thirdy-party fonts, it returns ("ANY","ANY").
        # describe.modifiers(font)
        #   This returns two integers (weight,italic).
        #   The first one is font weight [100..900]. The second one is 0 or 1.
        # describe.weightName(number)
        #   This converts the font weight number into a name (like normal, bold).

        font = ttLib.TTFont(fontfile)
        short_name = describe.shortName(font)
        family = describe.family(font)
        modifiers = describe.modifiers(font)

        self.filename = fontfile
        self.name = short_name[0]
        self.name_family = short_name[1]
        self.family = '/'.join(family)
        self.weight = modifiers[0]
        self.weight_name = describe.weightName(modifiers[0])
        if modifiers[1]:
            self.italic = True
        else:
            self.italic = False


def print_html(metadata, html_file, text=''):
    def html(s):
        s = (s
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )
        if isinstance(s, str):
            s = s.encode('utf-8', 'replace')
        elif isinstance(s, str):
            pass
        else:
            raise ValueError(
                'What kind of type is this? type(s)={0} repr(s)={1}'
                .format(type(s), repr(s))
            )
        return s

    text = html(text)

    html_file.write('''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="Generator" content="fontpreviewer https://github.com/denilsonsa/fontpreviewer">
<title>Font list</title>
<style type="text/css">
html, body {
    background: white;
    color: black;
}
table {
    border: 3px solid black;
    margin: 0;
    padding: 0;
    border-collapse: collapse;
}
td, th {
    border: 1px solid black;
    margin: 0;
    padding: 0 2px;
    white-space: pre;
}
td[rowspan="2"] {
    padding: 0;
}
th {
    font-weight: normal;
    text-align: left;
}
td {
    text-align: left;
}
tr.first {
    border-top: 3px solid black;
}
tr.second {
    border-bottom: 3px solid black;
}
</style>
</head><body>
''')

    html_file.write('<table>\n\n'
        '<!--<thead>\n'
        '<tr class="first"><th colspan="3">Font name</th><th rowspan="2">{text}</th></tr>\n'
        '<tr class="second"><th>filename</th><th>weight</th><th>italic</th></tr>\n'
        '</thead>-->\n\n'
        '<tbody>\n\n'.format(
            text=text
        )
    )

    for e in metadata:
        pngfilename = os.path.splitext(e.filename)[0] + '.png'
        italic = 'Italic' if e.italic else ''

        html_file.write(
            '<tr class="first">'
            '<td colspan="3">{name}</td>'
            '<td rowspan="2"><img src="{pngfilename}" alt="" title="{filename} - {name}"></td>'
            '</tr>\n'
            '<tr class="second">'
            '<td>{filename}</td><td>{weight}</td><td>{italic}</td>'
            '</tr>\n\n'.format(
                name=html(e.name),
                filename=html(e.filename),
                pngfilename=html(pngfilename),
                weight=str(e.weight),
                italic=italic,
                text=text
            )
        )

    html_file.write('</tbody>\n\n</table>\n\n</body>\n</html>\n')


def print_help():
    print("Usage: {0} [opts] <ttf font files>".format(os.path.basename(sys.argv[0])))
    print("Options:")
    print("  -s 48    Sets the font size (height) in pixels. (default=48)")
    print("  -a       Enables anti-aliasing. (default)")
    print("  -A       Disables anti-aliasing.")
    print("  -t text  Defines the text to be used when rendering the font.")
    print("           (default=The Quick Brown Fox Jumped Over The Lazy Dog.)")
    if HAS_FONTTOOLS:
        print("  -o file  Writes a HTML page linking to all PNG images and including actual")
        print("           font names. (use '-' to output to stdout)")
    print("  -h       Prints this help.")
    print("")
    print("This program will render each TTF file into a PNG file (in the same directory")
    print("of the TTF file).")
    print("")
    print("This program will ignore (skip) invalid files (but will report all errors")
    print("encountered).")


class ProgramOptions(object):
    """Holds the program options, after they are parsed by parse_options()"""

    def __init__(self):
        self.text = 'The Quick Brown Fox Jumped Over The Lazy Dog.'
        self.fontsize = 48
        self.antialias = True
        self.output_html = False
        self.output_html_filename = ''
        self.args = []


def parse_options(argv, opt):
    """argv should be sys.argv[1:]
    opt should be an instance of ProgramOptions()"""

    try:
        opts, args = getopt.getopt(
            argv,
            's:t:aAho:',
            ['size=', 'text=', 'help', 'output=']
        )
    except getopt.GetoptError as e:
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write('Use --help for usage instructions.\n')
        sys.exit(2)

    for o, v in opts:
        if o in ('-s', '--size'):
            opt.fontsize = int(v)
        elif o == '-a':
            opt.antialias = True
        elif o == '-A':
            opt.antialias = False
        elif o in ('-t', '--text'):
            opt.text = v.decode('utf-8')
        elif o in ('-o', '--output') and HAS_FONTTOOLS:
            opt.output_html = True
            opt.output_html_filename = v
        elif o in ('-h', '--help'):
            print_help()
            sys.exit(0)
        else:
            print('Invalid parameter: {0}'.format(o))
            print('Use --help for usage instructions.')
            sys.exit(2)

    opt.args = args
    if len(args) == 0:
        sys.stderr.write('No files. Use --help for usage instructions.\n')
        sys.exit(2)


def main():
    pygame.init()

    if not (pygame.font and pygame.font.get_init()):
        sys.stderr.write('pygame.font has not been initialized. Do you have SDL_ttf?\n')
        sys.exit(1)

    opt = ProgramOptions()
    parse_options(sys.argv[1:], opt)

    metadata = []

    for f in opt.args:
        try:
            render_font_to_file(f, opt.text, opt.fontsize, opt.antialias)
            if opt.output_html:
                try:
                    metadata.append(FontMetadata(f))
                except Exception as e:
                    sys.stderr.write("Exception while getting metadata for '{0}': {1}\n".format(f, repr(e)))
        except Exception as e:
            sys.stderr.write("Exception while rendering '{0}': {1}\n".format(f, repr(e)))

    if opt.output_html:
        try:
            if opt.output_html_filename == '-':
                output_html_file = sys.stdout
            else:
                output_html_file = open(opt.output_html_filename, "w")

            print_html(metadata, output_html_file, opt.text)

            if opt.output_html_filename != '-':
                output_html_file.close()
        except IOError as e:
            sys.stderr.write("IOError while writing '{0}': {1}\n".format(opt.output_html_filename, str(e)))


if __name__ == '__main__':
    main()
