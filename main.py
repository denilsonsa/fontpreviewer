#!/usr/bin/env python
# -*- coding: us-ascii -*-

# Requirements:
# - Python (d'oh!)
#   - Tested with python-2.4.4
# - SDL and SDL_ttf
#   - Tested with libsdl-1.2.11 and sdl-ttf-2.0.8
# - pygame compiled with font support (SDL_ttf)
#   - Tested with pygame-1.7.1
# - ImageMagick 'convert' tool available on system PATH
#
# Optional requirements:
#  - FontTools (http://fonttools.sourceforge.net/)
#    - Tested with fonttools-2.0_beta1

# This program comes with "describe.py" file from TTFQuery-1.0.0 package.
# http://ttfquery.sourceforge.net/


import sys, getopt, os, os.path, subprocess, pygame
from pygame.font import Font

try:
    from fontTools import ttLib
    HAS_FONTTOOLS = True
    import describe
except ImportError:
    HAS_FONTTOOLS = False



def render_font_to_file(fontfile, text, fontsize, antialias, background=None):
    """From Font.render() documentation:
  If antialiasing is not used, the return image will always be an 8bit image with a two color palette. If the background is transparent a colorkey will be set. Antialiased images are rendered to 24-bit RGB images. If the background is transparent a pixel alpha will be included.

Note that current implementation is broken. The "background" parameter does not support None. You must either omit it, or pass a RGBA tuple.

Note also that PNG support was (?) added in pygame-1.8 (but, as of 2007-08-08, 1.7.1 is the latest version, being released on 2005-08-16)."""

    font = Font(fontfile, fontsize)
    if background == None:
        surf = font.render(text, antialias, (0,0,0))
    else:
        surf = font.render(text, antialias, (0,0,0), background)
    tgafile = os.path.splitext(fontfile)[0] + ".tga"
    pngfile = os.path.splitext(fontfile)[0] + ".png"
    pygame.image.save(surf, tgafile)
    subprocess.call(["convert",tgafile,pngfile])
    # Note: os.unlink() is exactly the same as os.remove()
    os.unlink(tgafile)



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
        self.family = "/".join(family)
        self.weight = modifiers[0]
        self.weight_name = describe.weightName(modifiers[0])
        if modifiers[1]:
            self.italic = True
        else:
            self.italic = False


def print_html(metadata, html_file, text=""):
    html_file.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=US-ASCII">
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

<table>

<!--<thead>
<tr class="first"><th colspan="3">Font name</th><th rowspan="2">"""+text+"""</th></tr>
<tr class="second"><th>filename</th><th>weight</th><th>italic</th></tr>
</thead>-->

<tbody>

""")
    for e in metadata:
        pngfile = os.path.splitext(e.filename)[0] + ".png"
        if e.italic:
            italic = "Italic"
        else:
            italic = ""
        html_file.write(
            '<tr class="first"><td colspan="3">%s</td><td rowspan="2"><img src="%s" alt="" title="%s"></td></tr>\n' %
            (e.name, pngfile, "%s - %s" % (e.filename, e.name))
        )
        html_file.write(
            '<tr class="second"><td>%s</td><td>%d</td><td>%s</td></tr>\n\n' %
            (e.filename, e.weight, italic)
        )

    html_file.write("</tbody>\n\n</table>\n\n</body></html>\n")


def print_help():
    print "Usage: %s [opts] <ttf font files>" % os.path.basename(sys.argv[0])
    print "Options:"
    print "  -s 48    Sets the font size (height) in pixels. (default=48)"
    print "  -a       Enables anti-aliasing. (default)"
    print "  -A       Disables anti-aliasing."
    print "  -t text  Defines the text to be used when rendering the font."
    print "           (default=The Quick Brown Fox Jumped Over The Lazy Dog.)"
    if HAS_FONTTOOLS:
        print "  -o file  Writes a HTML page linking to all PNG images and including actual"
        print "           font names. (use '-' to save to stdout)"
    print "  -h       Prints this help."
    print ""
    print "This program will render each TTF file into a TGA file (in the same directory"
    print "of the TTF file), then will convert TGA to PNG using ImageMagick 'convert'"
    print "tool, and finally remove the TGA file."
    print ""
    print "This program will ignore (skip) any invalid file (but will report any errors"
    print "encountered)."


class ProgramOptions(object):
    """Holds the program options, after they are parsed by parse_options()"""

    def __init__(self):
        self.text = "The Quick Brown Fox Jumped Over The Lazy Dog."
        self.fontsize = 48
        self.antialias = True
        self.output_html = False
        self.output_html_filename = ""
        self.args = []


def parse_options(argv, opt):
    """argv should be sys.argv[1:]
    opt should be an instance of ProgramOptions()"""

    try:
        opts, args = getopt.getopt(
            argv,
            "s:t:aAho:",
            ["size=", "text=", "help", "output="]
        )
    except getopt.GetoptError as e:
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("Use --help for usage instructions.\n")
        sys.exit(2)

    for o, v in opts:
        if o in ("-s", "--size"):
            opt.fontsize = int(v)
        elif o == "-a":
            opt.antialias = True
        elif o == "-A":
            opt.antialias = False
        elif o in ("-t", "--text"):
            opt.text = v
        elif o in ("-o", "--output") and HAS_FONTTOOLS:
            opt.output_html = True
            opt.output_html_filename = v
        elif o in ("-h", "--help"):
            print_help()
            sys.exit(0)
        else:
            print "Invalid parameter: {0}".format(o)
            print "Use --help for usage instructions."
            sys.exit(2)

    opt.args = args
    if len(args) == 0:
        sys.stderr.write("No files. Use --help for usage instructions.\n")
        sys.exit(2)


def main():
    pygame.init()

    if not (pygame.font and pygame.font.get_init()):
        sys.stderr.write("pygame.font has not been initialized. Do you have SDL_ttf?\n")
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
                    sys.stderr.write("Exception while getting metadata for '%s': %s\n" % (f, repr(e)))
        except Exception as e:
            sys.stderr.write("Exception while rendering '%s': %s\n" % (f, repr(e)))

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
            sys.stderr.write("IOError while writing '%s': %s\n" % (opt.output_html_filename, e))


if __name__ == '__main__':
    main()
