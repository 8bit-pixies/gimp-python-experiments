#!/usr/bin/env python

# Custom Font On Path Rel 1
# idea from http://bakon.ca/gimplearn/custom-fonts-script-291
# Created by Tin Tran http://bakon.ca/gimplearn/
# Comments directed to http://gimplearn.com or http://gimp-forum.net or http://gimpchat.com or http://gimpscripts.com
#
# License: GPLv3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# To view a copy of the GNU General Public License
# visit: http://www.gnu.org/licenses/gpl.html
#
#
# ------------
# | Change Log |
# ------------
# Rel 1: Initial release.
import math
import string

# import Image
from gimpfu import *
from array import array
import sys

# ========================================
# Copied this below function from ofnuts text-along-path-0.4.py
def computeThetaWithSlope(fromPoint, toPoint, slope):
    dX = toPoint[0] - fromPoint[0]
    dY = toPoint[1] - fromPoint[1]

    if math.fabs(dX) < 0.001:
        theta = math.copysign(math.pi / 2, dY)
    else:
        theta = math.atan(slope)
        if dX < 0:
            theta = theta + math.pi
    return theta


# ========================================
# copied from http://stackoverflow.com/questions/31735499/calculate-angle-clockwise-between-two-points
def python_custom_font_on_path(image, layer, xcffilename, text, position, spacing):
    pdb.gimp_image_undo_group_start(image)
    pdb.gimp_context_push()

    # loads file
    dummy = 0
    fontimg = pdb.gimp_xcf_load(dummy, xcffilename, xcffilename)

    # calculate width of our custom text to scale it to fit path later.
    width = 0
    for i in range(0, len(text)):
        char = text[i]
        if i < len(text) - 1:  # check next character for kerning
            nextchar = text[i + 1]
        else:
            nextchar = "N/A"  # if it's last character just give it a long string so it won't match with anything
        layer_name = char + ".png"
        width_vector_name = layer_name  # same name as layer_name
        kerning_vector_name = char + nextchar + ".png"
        char_layer = pdb.gimp_image_get_layer_by_name(fontimg, layer_name)
        if char_layer < 0:  # layer not found
            pdb.gimp_message("Layer not found: '" + layer_name + "'")  # message user.
        else:
            char_width = char_layer.width
            add_width = char_width
            # look at kerning
            found_vector = pdb.gimp_image_get_vectors_by_name(
                fontimg, kerning_vector_name
            )
            if (
                found_vector < 0
            ):  # if we don't find kerning we look for width_vector_name
                found_vector = pdb.gimp_image_get_vectors_by_name(
                    fontimg, width_vector_name
                )
            if found_vector >= 0:  # either found a kerning or a width vector
                numstrokes, strokeids = pdb.gimp_vectors_get_strokes(found_vector)
                stroke = strokeids[0]
                type, numpoints, points, closed = pdb.gimp_vectors_stroke_get_points(
                    found_vector, stroke
                )
                firstX = points[2]
                secondX = points[len(points) - 4]
                minX = min(firstX, secondX)
                maxX = max(firstX, secondX)
                add_width = (
                    maxX - minX
                )  # overwrite add_width to be added to total width
            width += add_width

            if i < len(text) - 1:  # if there is next character, add spacing
                width += spacing

    # get active vectors to work with
    active_vectors = pdb.gimp_image_get_active_vectors(image)
    numstrokes, src_strokeids = pdb.gimp_vectors_get_strokes(active_vectors)
    src_stroke = src_strokeids[
        0
    ]  # just work with first stroke, not sure about multiple strokes
    path_length = pdb.gimp_vectors_stroke_get_length(active_vectors, src_stroke, 0.01)

    # now that we have path_length we'll calculate the scale in order to fit all our letters on to the path
    scale = float(path_length) / width

    # actual work of putting layers on the path
    width = 0
    for i in range(0, len(text)):
        char = text[i]
        if i < len(text) - 1:  # check next character for kerning
            nextchar = text[i + 1]
        else:
            nextchar = "N/A"  # if it's last character just give it a long string so it won't match with anything
        layer_name = char + ".png"
        width_vector_name = layer_name  # same name as layer_name
        kerning_vector_name = char + nextchar + ".png"
        char_layer = pdb.gimp_image_get_layer_by_name(fontimg, layer_name)
        if char_layer < 0:  # layer not found
            pdb.gimp_message("Layer not found: '" + layer_name + "'")  # message user.
        else:
            # CREATE COPY OF LAYER, SCALE IT TOO AT ONCE TO FIT ON PATH
            copy = pdb.gimp_layer_new_from_drawable(char_layer, image)
            pdb.gimp_image_insert_layer(image, copy, None, 0)
            pdb.gimp_item_set_visible(copy, True)
            new_width = copy.width * scale
            new_height = copy.height * scale
            pdb.gimp_layer_scale(copy, new_width, new_height, False)

            char_width = char_layer.width
            add_width = char_width
            # look at kerning
            found_vector = pdb.gimp_image_get_vectors_by_name(
                fontimg, kerning_vector_name
            )
            if (
                found_vector < 0
            ):  # if we don't find kerning we look for width_vector_name
                found_vector = pdb.gimp_image_get_vectors_by_name(
                    fontimg, width_vector_name
                )
            if found_vector >= 0:  # either found a kerning or a width vector
                numstrokes, strokeids = pdb.gimp_vectors_get_strokes(found_vector)
                stroke = strokeids[0]
                type, numpoints, points, closed = pdb.gimp_vectors_stroke_get_points(
                    found_vector, stroke
                )
                firstX = points[2]
                secondX = points[len(points) - 4]
                minX = min(firstX, secondX)
                maxX = max(firstX, secondX)
                add_width = (
                    maxX - minX
                )  # overwrite add_width to be added to total width
            width += add_width

            # CALCULATE WHERE TO MOVE IT
            dist = width - (float(add_width) / 2)  # to get center of character.
            dist = dist * scale
            x_point, y_point, slope, valid = pdb.gimp_vectors_stroke_get_point_at_dist(
                active_vectors, src_stroke, dist, 0.01
            )
            (
                x_point1,
                y_point1,
                slope1,
                valid,
            ) = pdb.gimp_vectors_stroke_get_point_at_dist(
                active_vectors, src_stroke, dist - 5, 0.01
            )
            (
                x_point2,
                y_point2,
                slope2,
                valid,
            ) = pdb.gimp_vectors_stroke_get_point_at_dist(
                active_vectors, src_stroke, dist + 5, 0.01
            )

            translate_x = x_point - float(copy.width / 2)
            if position == 0:  # PUT IT ABOVE PATH
                translate_y = y_point - float(copy.height)
            elif position == 1:  # PUT IT ON PATH
                translate_y = y_point - float(copy.height) / 2
            elif position == 2:  # PUT IT BELOW PATH
                translate_y = y_point - 0
            pdb.gimp_layer_translate(copy, translate_x, translate_y)

            # ROTATE IT ACCORDING TO SLOPE OF PATH
            angle = computeThetaWithSlope(
                [x_point1, y_point1], [x_point2, y_point2], slope
            )

            x, y = pdb.gimp_drawable_offsets(copy)
            if position == 0:  # ON PATH ROTATE AT BASE
                pdb.gimp_drawable_transform_rotate(
                    copy,
                    angle,
                    False,
                    x + copy.width / 2,
                    y + copy.height,
                    TRANSFORM_FORWARD,
                    INTERPOLATION_CUBIC,
                    True,
                    3,
                    TRANSFORM_RESIZE_ADJUST,
                )
            elif position == 1:  # PUT IT ON PATH ROTATE AT CENTER
                pdb.gimp_drawable_transform_rotate(
                    copy,
                    angle,
                    True,
                    x + copy.width / 2,
                    y + copy.height,
                    TRANSFORM_FORWARD,
                    INTERPOLATION_CUBIC,
                    True,
                    3,
                    TRANSFORM_RESIZE_ADJUST,
                )
            elif position == 2:  # PUT IT BELOW PATH ROTATE AT TOP
                pdb.gimp_drawable_transform_rotate(
                    copy,
                    angle,
                    False,
                    x + copy.width / 2,
                    y + 0,
                    TRANSFORM_FORWARD,
                    INTERPOLATION_CUBIC,
                    True,
                    3,
                    TRANSFORM_RESIZE_ADJUST,
                )

            if i < len(text) - 1:  # if there is next character, add spacing
                width += spacing

    pdb.gimp_context_pop()
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_displays_flush()
    # return


register(
    "python_fu_custom_font_on_path",
    "Places Custom Font on Path",
    "Places Custom Font on Path",
    "Tin Tran",
    "Tin Tran",
    "2017",
    "<Image>/Python-Fu/Custom Font on Path...",  # Menu path
    "RGB*, GRAY*",
    [
        (PF_FILENAME, "xcffilename", ".xcf font file:", 0),
        (PF_TEXT, "text", "Custom Text:", "GIMP LEARN CUSTOM FONT"),
        (
            PF_OPTION,
            "position",
            "Text Positioning:",
            0,
            ["Above Path", "On Path", "Below Path"],
        ),  # initially 0th is choice
        (
            PF_SPINNER,
            "spacing",
            "Letter Spacing (before scaling text to fit on path):",
            0,
            (-1000, 1000, 1),
        ),
    ],
    [],
    python_custom_font_on_path,
)

main()
