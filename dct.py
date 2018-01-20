# Author: Jonathan Zwiebel
# Version: 12 January 2018
# This file contains a basic version of a discrete cosine transformation for compression of time series data

import math


MIN_VALUE = 30
MAX_VALUE = 130
RESOLUTION = 7
K_SIZE = 16
QUANTIZATION_VECTOR = [1, 2, 3, 5, 8, 10, 20, 40, 40, 40, 40, 80, 80, 80, 80, 20]
# QUANTIZATION_VECTOR = [1, 2, 3, 5, 8, 10, 20, 40]
FILE = "data.csv"


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


def scale_data(segment):
    new_data = []
    for i in range(len(segment)):
        value = segment[i]
        offset = value - MIN_VALUE
        scaled = offset / (MAX_VALUE - MIN_VALUE)
        if scaled < 0:
            scaled = 0
        if scaled > 1:
            scaled = 1
        new_data.append(round((2 ** RESOLUTION * scaled - 2 ** (RESOLUTION - 1))))
    return new_data


def dct_data(segment):
    new_segment = []
    for k in range(K_SIZE):
        total = 0
        for n in range(K_SIZE):
            total += segment[n] * math.cos(math.pi / K_SIZE * (n + 0.5) * k)
        new_segment.append(round(total))
    return new_segment


def quantize_data(segment):
    assert len(QUANTIZATION_VECTOR) == K_SIZE
    new_segment = []
    for i in range(K_SIZE):
        new_segment.append(round(segment[i] / QUANTIZATION_VECTOR[i]))
    return new_segment


def unquantize_data(segment):
    assert len(QUANTIZATION_VECTOR) == K_SIZE
    new_segment = []
    for i in range(K_SIZE):
        new_segment.append(segment[i] * QUANTIZATION_VECTOR[i])
    return new_segment


def inverse_dct_data(segment):
    new_segment = []
    for k in range(K_SIZE):
        total = 0.5 * segment[0]
        for n in range(1, K_SIZE):
            total += segment[n] * math.cos(math.pi / K_SIZE * n * (0.5 + k))
        total *= 2 / K_SIZE
        new_segment.append(total)
    return new_segment


def unscale_data(segment):
    new_data = []
    for i in range(len(segment)):
        value = segment[i]
        offset = value + 2 ** (RESOLUTION - 1)
        scaled = offset / (2 ** RESOLUTION)
        if scaled < 0:
            print("At zero extreme")
            scaled = 0
        if scaled > 1:
            print("At one extreme")
            scaled = 1
        new_data.append(MAX_VALUE * scaled + MIN_VALUE * (1 - scaled))
    return new_data


out = "C:/users/jonathan/desktop/" + FILE
out_file = open(out, "w")

loc = "C:/users/jonathan/desktop/exchange_data.csv"
f = open(loc, "r")
lines = f.read().splitlines()

data = []
for i in range(1, len(lines)):
    cells = lines[i].split(",")
    if cells[1] != "":
        data.append(float(cells[1]))

# BEGIN TRANSOFMRATION
segments = split(data)

scaled_segments = []
for segment in segments:
    scaled_segments.append(scale_data(segment))

dct_segments = []
for scaled_segment in scaled_segments:
    dct_segments.append(dct_data(scaled_segment))

quant_segments = []
for dct_segment in dct_segments:
    quant_segments.append(quantize_data(dct_segment))

transformed_data = []
for quant_segment in quant_segments:
    for value in quant_segment:
        transformed_data.append(value)

# END TRANSFORMATION

# BEGIN REVERSE TRANSFORMATION
transformed_segments = split(transformed_data)

unquantized_segments = []
for transformed_segment in transformed_segments:
    unquantized_segments.append(unquantize_data(transformed_segment))

inverse_dct_segments = []
for unquantized_segment in unquantized_segments:
    inverse_dct_segments.append(inverse_dct_data(unquantized_segment))

unscaled_segments = []
for inverse_dct_segment in inverse_dct_segments:
    unscaled_segments.append(unscale_data(inverse_dct_segment))

out_file.write("Raw, SCALE, DCT, QUANT, UN-QUANT\n")
for i in range(len(data)):
    segment_index = (int)(i / K_SIZE)
    value_index = i - segment_index * K_SIZE
    out_file.write(str(segments[segment_index][value_index]) + ",")
    out_file.write(str(scaled_segments[segment_index][value_index]) + ",")
    out_file.write(str(dct_segments[segment_index][value_index]) + ",")
    out_file.write(str(quant_segments[segment_index][value_index]) + ",")
    out_file.write(str(unquantized_segments[segment_index][value_index]) + ",")
    out_file.write(str(inverse_dct_segments[segment_index][value_index]) + ",")
    out_file.write(str(unscaled_segments[segment_index][value_index]) + "\n")

f.close()
out_file.close()
