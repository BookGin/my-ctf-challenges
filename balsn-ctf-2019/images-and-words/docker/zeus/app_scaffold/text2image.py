#!/usr/bin/env python3

# Script to render text as a PNG image
# Modified from https://github.com/drj11/pypng/blob/main/code/texttopng.py

'''
LICENCE (MIT)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from binascii import unhexlify
import png

unknown = 'FFFFFFFFFFFFFFFF'
font = {
    ' ': '0000000000000000',
    '!': '0010101010001000',
    '"': '0028280000000000',
    '#': '0000287c287c2800',
    '$': '00103c5038147810',
    '%': '0000644810244c00',
    '&': '0020502054483400',
    '\'': '0010100000000000',
    '(': '0008101010101008',
    ')': '0020101010101020',
    '*': '0010543838541000',
    '+': '000010107c101000',
    ',': '0000000000301020',
    '-': '000000007c000000',
    '.': '0000000000303000',
    '/': '0000040810204000',
    '0': '0038445454443800',
    '1': '0008180808080800',
    '2': '0038043840407c00',
    '3': '003c041804043800',
    '4': '00081828487c0800',
    '5': '0078407804047800',
    '6': '0038407844443800',
    '7': '007c040810101000',
    '8': '0038443844443800',
    '9': '0038443c04040400',
    ':': '0000303000303000',
    ';': '0000303000301020',
    '<': '0004081020100804',
    '=': '0000007c007c0000',
    '>': '0040201008102040',
    '?': '0038440810001000',
    '@': '00384c545c403800',
    'A': '0038447c44444400',
    'B': '0078447844447800',
    'C': '0038444040443800',
    'D': '0070484444487000',
    'E': '007c407840407c00',
    'F': '007c407840404000',
    'G': '003844405c443c00',
    'H': '0044447c44444400',
    'I': '0038101010103800',
    'J': '003c040404443800',
    'K': '0044487048444400',
    'L': '0040404040407c00',
    'M': '006c545444444400',
    'N': '004464544c444400',
    'O': '0038444444443800',
    'P': '0078447840404000',
    'Q': '0038444444443c02',
    'R': '0078447844444400',
    'S': '0038403804047800',
    'T': '007c101010101000',
    'U': '0044444444443c00',
    'V': '0044444444281000',
    'W': '0044445454543800',
    'X': '0042241818244200',
    'Y': '0044443810101000',
    'Z': '007c081020407c00',
    '[': '0038202020202038',
    '\\': '0000402010080400',
    ']': '0038080808080838',
    '^': '0010284400000000',
    '_': '000000000000fe00',
    '`': '0040200000000000',
    'a': '000038043c443c00',
    'b': '0040784444447800',
    'c': '0000384040403800',
    'd': '00043c4444443c00',
    'e': '000038447c403c00',
    'f': '0018203820202000',
    'g': '00003c44443c0438',
    'h': '0040784444444400',
    'i': '0010003010101000',
    'j': '0010003010101020',
    'k': '0040404870484400',
    'l': '0030101010101000',
    'm': '0000385454444400',
    'n': '0000784444444400',
    'o': '0000384444443800',
    'p': '0000784444784040',
    'q': '00003c44443c0406',
    'r': '00001c2020202000',
    's': '00003c4038047800',
    't': '0020203820201800',
    'u': '0000444444443c00',
    'v': '0000444444281000',
    'w': '0000444454543800',
    'x': '0000442810284400',
    'y': '00004444443c0438',
    'z': '00007c0810207c00',
    '{': '0018202060202018',
    '|': '0010101000101010',
    '}': '003008080c080830',
    '~': '0020540800000000',
}

def int2bin(n):
    return bin(n)[2:].zfill(8)

def draw_line(line):
    rows = ['' for _ in range(8)]
    for char in line:
        c = unhexlify(font.get(char, unknown))
        for i, row in enumerate(c):
            rows[i] += int2bin(row)
    return rows

def pad(rows):
    w = max(len(row) for row in rows)
    h = len(rows)
    pixels = [[int(row[i]) if i < len(row) else 0 for i in range(w)] for row in rows]
    return w, h, pixels

def render(text, outfile):
    rows = []
    for line in text.splitlines():
        rows += draw_line(line)
    w, h, pixels = pad(rows)
    png.Writer(w, h, greyscale=True, bitdepth=1).write(outfile, pixels)
