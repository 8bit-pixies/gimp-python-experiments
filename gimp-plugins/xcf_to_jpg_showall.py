#!/usr/bin/env python
import os


def xcf_to_jpg_showall(fname, out_fname=""):
    """
    makes all layers visible, flattens the image and then exports as jpg
    """
    img = pdb.gimp_file_load(fname, fname)

    # do show all layers
    pdb.gimp_image_undo_group_start(img)

    # iterate layer groups
    for group in [group for group in img.layers if pdb.gimp_item_is_group(group)]:
        # you want a group.name check here to pick a specific group
        for layer in group.layers:
            layer.visible = True

    # iterate non-group layers
    for layer in img.layers:
        layer.visible = True

    pdb.gimp_image_undo_group_end(img)
    # end do show all layers

    img.flatten()
    if out_fname == "":
        out_fname = os.path.splitext(fname)[0] + ".jpg"
    pdb.gimp_file_save(img, img.layers[0], out_fname, "?")
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
    shcode = 'gimp-console -idf --batch-interpreter python-fu-eval -b "{}" -b "pdb.gimp_quit(1)"'.format(
        shcode_template
    )
    print("Running command:\n{}\n".format(shcode))
    sys.exit(subprocess.call(shcode, shell=True))
else:
    from gimpfu import *
