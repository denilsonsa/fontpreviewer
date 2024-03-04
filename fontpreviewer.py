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


def process_font(filename, text, fontsize, antialias=True):
    font = Font(filename, fontsize)
    font.antialiased=antialias
    surf, rect = font.render(text)

    if rect.width == 0 or rect.height == 0:
        png_filename = ''
        sys.stderr.write("Font '{0}' rendered to a zero-sized image.\n".format(filename))
    else:
        png_filename = os.path.splitext(filename)[0] + '.png'
        pygame.image.save(surf, png_filename)

    family_name = None
    subfamily_name = None
    full_name = None
    weight = None
    italic = None
    num_glyphs = None
    if HAS_FONTTOOLS:
        ttfont = ttLib.TTFont(filename)
        num_glyphs = ttfont['maxp'].numGlyphs
        family_name = ttfont['name'].getBestFamilyName()
        subfamily_name = ttfont['name'].getBestSubFamilyName()
        full_name = ttfont['name'].getBestFullName()
        # This logic is based on TTFQuery:
        # https://pypi.org/project/TTFQuery/#files
        # https://ttfquery.sourceforge.net/
        # https://sourceforge.net/projects/ttfquery/files/ttfquery/
        weight = ttfont['OS/2'].usWeightClass  # Integer.
        italic = ttfont['OS/2'].fsSelection & 1 or ttfont['head'].macStyle & 2  # Boolean.
        # Weight numbers:
        # 100 thin
        # 200 extralight, ultralight
        # 300 light
        # 400 normal, regular, plain
        # 500 medium
        # 600 semibold, demibold
        # 700 bold
        # 800 extrabold, ultrabold
        # 900 black, heavy

    return {
        'filename': filename,
        'path': font.path,  # Should be equivalent to filename.
        'name': font.name,  # ← This is actually the family name.
        'family_name': family_name,  # Str or None.
        'subfamily_name': subfamily_name,  # Str or None.
        'full_name': full_name,  # Str or None.
        'num_glyphs': num_glyphs,  # Integer or None.
        'monospace': 'monospace' if font.fixed_width else '',  # Boolean.
        'scalable': 'scalable' if font.scalable else 'bitmap',  # Boolean. Most modern fonts are.
        'weight': weight,  # Integer or None.
        'italic': 'Italic' if italic else '',  # Boolean or None.
        'img_filename': png_filename,
        'img_width': rect.width,
        'img_height': rect.height,
    }


def print_html(metadata, html_file, text=''):
    escape = lambda text: html.escape(str(text), quote=True) if text is not None else ''

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
        '<tbody>\n\n'.format(
            text=text
        )
    )

    for item in metadata:
        escaped_item = { k: escape(v) for (k, v) in item.items() }
        if HAS_FONTTOOLS:
            escaped_item['num_glyphs'] = '{num_glyphs}<br>glyphs'.format(**escaped_item)
            name_as_html = '<th><b>{family_name}</b></th> <td>{subfamily_name}</td>'.format(**escaped_item)
        else:
            name_as_html = '<th><b>{name}</b><th> <td></td>'.format(**escaped_item)
        html_file.write(
            '<tr class="first">'
            '  {name_as_html}'
            '  <td rowspan="2">{num_glyphs}</td>'
            #'  <td rowspan="2">{scalable}</td>'
            '  <td rowspan="2">{monospace}</td>'
            '  <td rowspan="2">{weight}</td>'
            '  <td rowspan="2">{italic}</td>'
            '  <td rowspan="2"><img src="{img_filename}" alt="" title="{filename} - {name}" width="{img_width}" height="{img_height}"></td>'
            '</tr>\n'
            '<tr class="second">'
            '  <td colspan="2"><a href="{filename}">{filename}</a></td>'
            '</tr>\n\n'.format(
                text=text,
                name_as_html=name_as_html,
                **escaped_item
            )
        )

    html_file.write('</tbody>\n</table>\n\n</body>\n</html>\n')


def print_help():
    print("Usage: {0} [opts] <font files>".format(os.path.basename(sys.argv[0])))
    print("Options:")
    print("  -s 48    Sets the font size (height). (default=48)")
    print("  -a       Enables anti-aliasing. (default)")
    print("  -A       Disables anti-aliasing.")
    print("  -t text  Defines the text to be used when rendering the font.")
    print("           (default=The Quick Brown Fox Jumped Over The Lazy Dog.)")
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
            opt.text = v
        elif o in ('-o', '--output'):
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
            metadata.append(process_font(f, opt.text, opt.fontsize, opt.antialias))
        except Exception as e:
            sys.stderr.write("Exception while processing '{0}': {1}\n".format(f, repr(e)))

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
