#!/usr/bin/env python3

import getopt
import html
import os
import os.path
import sys

# https://github.com/pygame/pygame/issues/1468
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame.freetype import Font

try:
    from fontTools import ttLib
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False

if HAS_FONTTOOLS:
    # TTFQuery project is abandoned and doesn't run/install anymore on recent
    # Python versions. Thankfully, I only need one file from that project, so
    # I've copied that file from that project into this project.
    # from ttfquery import describe
    import ttfquery_describe as describe


def render_font_to_file(fontfile, text, fontsize, antialias=True):
    font = Font(fontfile, fontsize)
    font.antialiased=antialias
    surf, rect = font.render(text)

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
    escape = lambda text: html.escape(text, quote=True)

    text = escape(text)

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
    --border-color: #a0a0a0;
    --thick-border: 2px solid var(--border-color);
    --thin-border: 1px solid var(--border-color);
    border: var(--thick-border);
    margin: 0;
    padding: 0;
    border-collapse: collapse;
}
td, th {
    border: var(--thin-border);
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
    border-top: var(--thick-border);
}
tr.second {
    border-bottom: var(--thick-border);
}
table a {
    text-decoration: none;
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
            '<td><a href="{filename}">{filename}</a></td><td title="{weight_name}">{weight}</td><td>{italic}</td>'
            '</tr>\n\n'.format(
                name=escape(e.name),
                filename=escape(e.filename),
                pngfilename=escape(pngfilename),
                weight=str(e.weight),
                weight_name=escape(', '.join(e.weight_name)),
                italic=italic,
                text=text
            )
        )

    html_file.write('</tbody>\n\n</table>\n\n</body>\n</html>\n')


def print_help():
    print("Usage: {0} [opts] <font files>".format(os.path.basename(sys.argv[0])))
    print("Options:")
    print("  -s 48    Sets the font size (height). (default=48)")
    print("  -a       Enables anti-aliasing. (default)")
    print("  -A       Disables anti-aliasing.")
    print("  -t text  Defines the text to be used when rendering the font.")
    print("           (default=The Quick Brown Fox Jumped Over The Lazy Dog.)")
    if HAS_FONTTOOLS:
        print("  -o file  Writes a HTML page linking to all PNG images and including actual")
        print("           font names. (use '-' to output to stdout)")
    print("  -h       Prints this help.")
    print("")
    print("This program will render each font file into a PNG file (in the same directory")
    print("of the font file).")
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

    if not (pygame.freetype and pygame.freetype.get_init()):
        sys.stderr.write('ERROR: pygame.freetype has not been initialized.\n')
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
                output_html_file = open(opt.output_html_filename, "w", encoding="utf-8", errors="replace")

            print_html(metadata, output_html_file, opt.text)

            if opt.output_html_filename != '-':
                output_html_file.close()
        except IOError as e:
            sys.stderr.write("IOError while writing '{0}': {1}\n".format(opt.output_html_filename, str(e)))


if __name__ == '__main__':
    main()
