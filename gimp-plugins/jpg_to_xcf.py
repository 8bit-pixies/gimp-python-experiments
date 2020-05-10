#!/usr/bin/env python
import os


def jpg_to_xcf(fname, out_fname=""):
    """
    Converts a jpg file to xcf and saves it.
    Note that in this mode, the function name and the name of this file must match.
    See here: https://ntcore.com/?p=509

    Usage
    ./jpg_to_xcf.py poster.jpg
    """
    img = pdb.gimp_file_load(fname, fname)
    drawable = img.active_drawable
    if out_fname == "":
        out_fname = os.path.splitext(fname)[0] + ".xcf"
    pdb.gimp_xcf_save(0, img, drawable, out_fname, out_fname)
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
