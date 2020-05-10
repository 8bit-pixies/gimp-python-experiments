#!/usr/bin/env python
"""
This is being used to form quicktile approximation to text location with 
the goal of having another markup language as input (TODO)

Usage:

./add_text.py poster.xcf "hello world" 12 100 200 100 100
"""


def add_text(fname, text, font_height, x, y, x_size, y_size):
    """
    Adds some text based on quicktile approximation
    """
    text = text.strip()
    img = pdb.gimp_file_load(fname, fname)
    min_font_size = 18.

    width = pdb.gimp_image_width(img)
    height = pdb.gimp_image_height(img)

    # rescale font - just to ensure it looks a bit more sane
    fontsize = max(min_font_size, float(font_height) * 0.8)
    drawable = pdb.gimp_text_fontname(
        img, None, x, y, "", 0, True, min_font_size, 1, "Intuitive Semi-Bold"
    )

    # now really add in information
    pdb.gimp_text_layer_resize(drawable, x_size, y_size)
    pdb.gimp_text_layer_set_justification(drawable, 2)
    pdb.gimp_text_layer_set_font_size(drawable, fontsize, 0)
    pdb.gimp_text_layer_set_text(drawable, text)

    # now check for intersection using binary search like algorithm
    # so that we know it fits in the selection box perfectly.
    w_, h_, _, _ = pdb.gimp_text_get_extents_fontname(
        text, fontsize, 0, "Intuitive Semi-Bold"
    )
    text_area_approx = w_ * h_*0.5
    current_area = int(x_size) * int(y_size)

    while text_area_approx < current_area and fontsize > min_font_size:
        fontsize = fontsize - 1
        pdb.gimp_text_layer_set_font_size(drawable, fontsize, 0)
        w_, h_, _, _ = pdb.gimp_text_get_extents_fontname(
            text, fontsize, 0, "Intuitive Semi-Bold"
        )
        text_area_approx = w_ * h_ * 0.5

    # add a background layer to improve readability
    shadow_layer = pdb.gimp_layer_new_from_drawable(drawable, img)
    pdb.gimp_image_insert_layer(img, shadow_layer, None, 1)
    pdb.gimp_edit_fill(shadow_layer, BACKGROUND_FILL)
    shadow_layer.opacity = 70.0

    pdb.gimp_image_raise_item_to_top(img, shadow_layer)
    pdb.gimp_image_raise_item_to_top(img, drawable)

    pdb.gimp_xcf_save(0, img, drawable, fname, fname)
    pdb.gimp_image_delete(img)


# GIMP auto-execution stub
if __name__ == "__main__":
    import os, sys, subprocess

    scrdir = os.path.dirname(os.path.realpath(__file__))
    scrname = os.path.splitext(os.path.basename(__file__))[0]
    args = str(tuple(sys.argv[1:]))
    shcode_template = "import sys;sys.path.insert(0, '{scrdir}'); import {scrname}; {scrname}.{scrname}{args}".format(
        scrdir=scrdir, scrname=scrname, args=args
    )
    shcode = 'gimp-console -i --batch-interpreter python-fu-eval -b "{}" -b "pdb.gimp_quit(1)"'.format(
        shcode_template
    )
    print("Running command:\n{}\n".format(shcode))
    sys.exit(subprocess.call(shcode, shell=True))
else:
    from gimpfu import *
