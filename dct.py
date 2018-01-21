# Author: Jonathan Zwiebel
# Version: 12 January 2018
# This file contains a basic version of a discrete cosine transformation for compression of time series data

import math
import sys


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


class MinHeap:
    def __init__(self):
        self.nodes = []

    def swap(self, index_a, index_b):
        temp = self.nodes[index_a]
        self.nodes[index_a] = self.nodes[index_b]
        self.nodes[index_b] = temp

    def left_child_index(self, parent_index):
        return 2 * parent_index + 1

    def right_child_index(self, parent_index):
        return 2 * parent_index + 2

    def parent_index(self, child_index):
        return (int)((child_index - 1) / 2)

    def add(self, new_node):
        self.nodes.append(new_node)
        self.fix_heap(len(self.nodes) - 1)

    def pop(self):
        value = self.nodes[0]
        if len(self.nodes) == 1:
            del self.nodes[0]
            return value

        self.swap(0, len(self.nodes) - 1)
        del self.nodes[-1]
        self.fix_heap_down(0)
        return value

    def fix_heap(self, index):
        if index == 0:
            return
        parent_index = self.parent_index(index)
        if self.nodes[index].value < self.nodes[parent_index].value:
            self.swap(index, parent_index)
            self.fix_heap(parent_index)

    def fix_heap_down(self, index):
        lc_index = self.left_child_index(index)
        rc_index = self.right_child_index(index)

        value = self.nodes[index].value
        if lc_index > len(self.nodes) - 1:
            return
        lc_value = self.nodes[lc_index].value
        if rc_index > len(self.nodes) - 1:
            if lc_value < value:
                self.swap(index, lc_index)
        else:
            rc_value = self.nodes[rc_index].value
            if lc_value <= rc_value and lc_value < value:
                self.swap(index, lc_index)
                self.fix_heap_down(lc_index)
            elif rc_value < lc_value and rc_value < value:
                self.swap(index, rc_index)
                self.fix_heap_down(rc_index)


class HeapNode:
    def __init__(self, value, data=None, right=None, left=None):
        self.value = value
        self.data = data
        self.right = right
        self.left = left


def traverse_huffman(node, dictionary, prefix):
    if node.left is None and node.right is None:
        dictionary[node.data] = prefix
    else:
        if node.left is not None:
            traverse_huffman(node.left, dictionary, prefix + "1")
        if node.right is not None:
            traverse_huffman(node.right, dictionary, prefix + "0")


def huffman(data):
    f_dict = {}
    for value in data:
        if value in f_dict:
            f_dict[value] += 1
        else:
            f_dict[value] = 1

    heap = MinHeap()
    for key in f_dict:
        new_node = HeapNode(f_dict[key], data=key)
        heap.add(new_node)

    while len(heap.nodes) > 1:
        smallest = heap.pop()
        second_smallest = heap.pop()
        new_node = HeapNode(smallest.value + second_smallest.value, left=smallest, right=second_smallest)
        heap.add(new_node)

    h_dict = {}
    traverse_huffman(heap.nodes[0], h_dict, "")

    out_sequence = ""
    for value in data:
        out_sequence += h_dict[value]
    print(out_sequence)
    return h_dict, out_sequence


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
print(len(data) * sys.getsizeof(data[0]))

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

huffman_tree, encoded_data = huffman(transformed_data)
print(len(encoded_data))

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

out_file.write("IN, SCALE, DCT, QUANT, UN-QUANT, UN_DCT, OUT\n")
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
