# Author: Jonathan Zwiebel
# Version: 12 January 2018
# This file contains a basic version of a discrete cosine transformation for compression of time series data

import math


MIN_VALUE = 30
MAX_VALUE = 130
RESOLUTION = 7
K_SIZE = 16
QUANTIZATION_VECTOR = [1, 2, 3, 5, 8, 10, 20, 40, 40, 40, 40, 80, 80, 80, 80, 20]


def split(data):
    if len(data) % K_SIZE != 0:
        last = data[len(data) - 1]
        for i in range(K_SIZE - len(data) % K_SIZE):
            data.append(last)

    segments = []
    curr = 0
    while curr < len(data):
        segment = []
        for i in range(K_SIZE):
            segment.append(data[curr])
            curr += 1
        segments.append(segment)
    return segments


def transform_data(data):
    for i in range(len(data)):
        value = data[i]
        offset = value - MIN_VALUE
        scaled = offset / (MAX_VALUE - MIN_VALUE)
        if scaled < 0:
            scaled = 0
        if scaled > 1:
            scaled = 1
        data[i] = round((2 ** RESOLUTION * scaled - 2 ** (RESOLUTION - 1)))

# Assumes values are already transformed


def dct_transform_segment(segment):
    new_segment = []
    for k in range(K_SIZE):
        total = 0
        for n in range(K_SIZE):
            total += segment[n] * math.cos(math.pi / K_SIZE * (n + 0.5) * k)
        new_segment.append(round(total))
    return new_segment


def quantize_segment(segment):
    assert len(QUANTIZATION_VECTOR) == K_SIZE
    new_segment = []
    for i in range(K_SIZE):
        new_segment.append(round(segment[i] / QUANTIZATION_VECTOR[i]))
    return new_segment


loc = "C:/users/jonathan/desktop/exchange_data.csv"
f = open(loc, "r")
lines = f.read().splitlines()

data = []
for i in range(1, len(lines)):
    cells = lines[i].split(",")
    if cells[1] != "":
        data.append(float(cells[1]))

transform_data(data)
segments = split(data)

dct_segments = []
for segment in segments:
    dct_segments.append(dct_transform_segment(segment))

quant_segments = []
for dct_segment in dct_segments:
    quant_segments.append(quantize_segment(dct_segment))
print(quant_segments)
