#!/usr/bin/python
# coding: utf-8
from PIL import Image
import cv2
import numpy as np
import logging


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def get_color_presence(image, lower_hsv, upper_hsv):
    presence = 0

    resized = image_resize(image, width=2000)

    # prepare image for better analysis
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

    # here we are defining range of color to isolate
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # the bitwise and of the frame and mask is done so
    # that only the blue coloured objects are highlighted
    result = cv2.bitwise_and(resized, resized, mask=mask)

    # debug result in separate windows
    # cv2.imshow('Original',image)
    # cv2.imshow('Mask',mask)
    # cv2.imshow('Result',result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # if mask.size > 0:
    presence = round(np.count_nonzero(mask) / np.size(mask) * 100, 1)

    return round(presence, 2)


def load_image(path):
    # Open Image
    image = cv2.imread(path)
    return image


def to_np_array(h, s, v):
    return np.array([h, s, v])
