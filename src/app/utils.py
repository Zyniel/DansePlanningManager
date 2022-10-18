#!/usr/bin/python
# coding: utf-8

import numpy as np
import cv2
import csv
import os
import shutil
import shutil
import logging

def to_image_string(image_filepath):
    return open(image_filepath, "rb").read().encode("base64")


def from_base64(base64_data):
    nparr = np.fromstring(base64_data.decode("base64"), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)


# clean all non-alphanumberic characters
def strip(string):
    words = string.split()
    words = [word for word in words if "#" not in word]
    string = " ".join(words)
    clean = ""
    for c in string:
        if str.isalnum(c) or (c in [" ", ".", ","]):
            clean += c
    return clean


# creating CSV header
def create_csv(filename):
    with open(filename, "w+", newline="", encoding="utf-8") as save_file:
        writer = csv.writer(save_file)
        writer.writerow(["Author", "uTime", "Text"])


def write_to_csv(filename, data):
    with open(filename, "a+", newline="", encoding="utf-8") as save_file:
        writer = csv.writer(save_file)
        writer.writerow(data)


def empty_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                empty_folder(file_path)
        except Exception as e:
            logging.info("Failed to delete %s. Reason: %s" % (file_path, e))


def move_file(source, dest):
    shutil.move(source, dest)
