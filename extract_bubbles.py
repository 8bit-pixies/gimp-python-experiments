"""
Based on https://github.com/dalelyunas/manga-translator https://github.com/Kocarus/Manga-Translator-TesseractOCR

We'll create objects, that is based on the blurb object
In this sense, we'll use jsonlines as the exchange data
format. 

The goal of this is to extract the bubbles in image
and we'll use GIMP to take it out etc...
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
import nltk
import re

import glob
import subprocess

from googletrans import Translator

translator = Translator()

words = set(nltk.corpus.words.words())
# from googletrans import Translator

template = {
    "jpg_to_xcf": """gimp-console -idf --batch-interpreter python-fu-eval -b "import sys;sys.path.insert(0, '/home/chapman/Github/opensandwich/gimp-plugins'); import jpg_to_xcf; jpg_to_xcf.jpg_to_xcf('{}','{}',)" -b "pdb.gimp_quit(1)" """,
    "xcf_to_jpg": """gimp-console -idf --batch-interpreter python-fu-eval -b "import sys;sys.path.insert(0, '/home/chapman/Github/opensandwich/gimp-plugins'); import xcf_to_jpg; xcf_to_jpg.xcf_to_jpg('{}','{}',)" -b "pdb.gimp_quit(1)" """,
    "add_text": """gimp-console -i   --batch-interpreter python-fu-eval -b "import sys;sys.path.insert(0, '/home/chapman/Github/opensandwich/gimp-plugins'); import add_text; add_text.add_text('{}', '{}', '{}', '{}', '{}', '{}', '{}',)" -b "pdb.gimp_quit(1)" """,
}


lang = "jpn_vert"
lang = "chi_sim"
lang = "eng"


def get_params():
    params = ""
    params += "--psm 12"

    configParams = []

    def configParam(param, val):
        return "-c " + param + "=" + val

    configParams.append(("chop_enable", "T"))
    configParams.append(("use_new_state_cost", "F"))
    configParams.append(("segment_segcost_rating", "F"))
    configParams.append(("enable_new_segsearch", "0"))
    configParams.append(("textord_force_make_prop_words", "F"))
    configParams.append(("tessedit_char_blacklist", "}><L"))
    configParams.append(("textord_debug_tabfind", "0"))
    params += " ".join([configParam(p[0], p[1]) for p in configParams])
    return params


def extract_bubbles(img, lang):
    """
    This does some destructive changes!
    """
    # with open(blurb_out, 'w') as f:
    # pass

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.bitwise_not(
        cv2.adaptiveThreshold(
            img_gray, 255, cv2.THRESH_BINARY, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 75, 10
        )
    )

    kernel = np.ones((2, 2), np.uint8)
    img_gray = cv2.erode(img_gray, kernel, iterations=2)
    img_gray = cv2.bitwise_not(img_gray)
    contours, hierarchy = cv2.findContours(
        img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    pruned_contours = []
    mask = np.zeros_like(img)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    height, width, channel = img.shape

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100 and area < ((height / 3) * (width / 3)):
            pruned_contours.append(cnt)

    # find contours for the mask for a second pass after pruning the large and small contours
    cv2.drawContours(mask, pruned_contours, -1, (255, 255, 255), 1)
    contours2, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    final_mask = cv2.cvtColor(np.zeros_like(img), cv2.COLOR_BGR2GRAY)

    blurbs = []
    for idx, cnt in enumerate(contours2):
        area = cv2.contourArea(cnt)
        if area > 1000 and area < ((height / 3) * (width / 3)):
            draw_mask = cv2.cvtColor(np.zeros_like(img), cv2.COLOR_BGR2GRAY)
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            # pickle.dump(approx, open("approx.pkl", mode="w"))
            cv2.fillPoly(draw_mask, [approx], (255, 0, 0))
            cv2.fillPoly(final_mask, [approx], (255, 0, 0))
            image = cv2.bitwise_and(draw_mask, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            # draw_mask_inverted = cv2.bitwise_not(draw_mask)
            # image = cv2.bitwise_or(image, draw_mask_inverted)
            y = approx[:, 0, 1].min()
            h = approx[:, 0, 1].max() - y
            x = approx[:, 0, 0].min()
            w = approx[:, 0, 0].max() - x

            h, w = image.shape[:2]
            img_rgb = np.zeros_like(img)
            img_rgb[y : y + h, x : x + w, :] = np.stack(
                [
                    image[y : y + h, x : x + w],
                    image[y : y + h, x : x + w],
                    image[y : y + h, x : x + w],
                ],
                -1,
            )

            # add additional layer with transparency
            img_rgb = np.dstack((img_rgb, np.zeros((h, w), dtype=np.uint8)))
            # img_rgb[y:y+h, x:x+w, 3] = 255
            # img_rgb[:, :, 3] = (1-draw_mask) * 255
            x, y, w, h = cv2.boundingRect(draw_mask)
            img_rgb[y : y + h, x : x + w, 3] = 255

            # dump image...if you want to see what is being pulled
            pil_image = Image.fromarray(img_rgb[y : y + h, x : x + w, :3])
            text_df = pytesseract.image_to_data(
                pil_image, lang=lang, config=get_params(), output_type="data.frame"
            )
            # text = pytesseract.image_to_string(
            #     pil_image, lang=lang, config=get_params()
            # )
            text_df = text_df[text_df.conf != -1]
            lines = text_df.groupby("block_num")["text"].apply(list)
            conf = text_df.groupby(["block_num"])["conf"].max().reset_index()
            conf = conf[conf["conf"] >= 70]  # filter if it is greater than...

            # keep all blocks in conf
            text_df = text_df[text_df["block_num"].isin(conf["block_num"])]

            # dump image, to-do add to gimp via shcode
            if text_df.shape[0] > 0:
                Image.fromarray(img_rgb).save(f"tmp{idx}.png")
                text = " ".join(list(text_df["text"]))

                # calculate offset for boxes...
                text_df["right"] = text_df["left"] + text_df["width"]
                text_df["bottom"] = text_df["top"] + text_df["height"]

                # interpolate font size
                font_px = 0.5 * text_df["height"].mean() + 0.5 * text_df["height"].max()
                font_px = int(font_px)

                # these are the offset...
                x_min = text_df["left"].min()
                x_max = text_df["right"].max()

                y_min = text_df["top"].min()
                y_max = text_df["bottom"].max()

                if text.strip() != "":
                    # x, y, w, h
                    text_out = {
                        "x": x + x_min,
                        "y": y + y_min,
                        "w": x_max - x_min,
                        "h": y_max - y_min,
                        "text": text,
                        "font_size": font_px,
                    }
                    blurbs.append(text_out)
    return blurbs


def process_image(img_fname, img_xcf, img_out, text_fname, lang, target_lang=""):
    # try to combine this with gimp to determine whats the best way to do everything!
    shcode = template["jpg_to_xcf"].format(img_fname, img_xcf)
    subprocess.call(shcode, shell=True)
    text_info = extract_bubbles(cv2.imread(img_fname), lang)

    # now do stuff here for textbox
    # template
    with open(text_fname, "w") as f:
        for args in text_info:
            # print([args['x'], args['y'], args['w'], args['h'], args['font_size'], args['text']])
            f.write(
                "\t".join(
                    [
                        str(int(args["x"])),
                        str(int(args["y"])),
                        str(int(args["w"])),
                        str(int(args["h"])),
                        str(int(args["font_size"])),
                        args["text"],
                    ]
                )
            )
            f.write("\n")

    # this is split so that we can process translation separately
    # purely for refactoring reasons down the  line
    for line in open(text_fname, "r").readlines():
        x, y, w, h, font_size, text = line.split("\t")
        text = re.sub(r"\s+", " ", text).strip()
        if target_lang != "":
            translatedText = translator.translate(text, dest=target_lang)
            text = translatedText.text.encode("utf-8").decode("unicode_escape")
        shcode = template["add_text"].format(img_xcf, text, font_size, x, y, w, h)
        subprocess.call(shcode, shell=True)

    shcode = template["xcf_to_jpg"].format(img_xcf, img_out)
    subprocess.call(shcode, shell=True)


process_image(
    "img/001.jpg", "img/001.xcf", "img/001-eng.jpg", "img/001.tsv", "eng", ""
)

process_image(
    "img/001.jpg", "img/001-es.xcf", "img/001-es.jpg", "img/001-es.tsv", "eng", "es"
)