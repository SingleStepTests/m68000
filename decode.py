#!/usr/bin/python3
import os
import glob
import json
from struct import unpack_from
from typing import Dict, Any

PRINTED_YET = 0
M68K_JSON_PATH = os.getcwd() + '/v1'
REG_ORDER = ['d0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7',
             'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'usp',
             'ssp', 'sr', 'pc'
             ]

def read_name(content, ptr):
    numbytes, magic_num = unpack_from('<II', content, ptr)
    ptr += 8
    assert magic_num == 0x89ABCDEF

    strlen = unpack_from('<I', content, ptr)[0]
    ptr += 4

    bs = unpack_from(str(strlen) + 's', content, ptr)[0]
    ptr += strlen
    nstr = bs.decode('utf-8')

    return ptr, nstr

def read_transactions(content, ptr):
    numbytes, magic_num = unpack_from("<II", content, ptr)
    assert magic_num == 0x456789AB
    ptr += 8
    transactions = []
    num_cycles, num_transactions = unpack_from("<II", content, ptr)
    if num_cycles == 0:
        global PRINTED_YET
        PRINTED_YET += 1
    ptr += 8
    for i in range(0, num_transactions):
        tw, cycles = unpack_from("<BI", content, ptr)
        ptr += 5
        if tw == 0:
            transactions.append(['n', cycles])
            continue
        fc, addr_bus, data_bus, UDS, LDS = unpack_from("<IIIII", content, ptr)
        bw = UDS + LDS
        ptr += 20
        if tw == 1:
            tws = 'w'
        elif tw == 2:
            tws = 'r'
        else:
            tws = 't'
        transactions.append([tws, cycles, fc, addr_bus, '.w' if bw == 2 else '.b', data_bus, UDS, LDS])

    return ptr, transactions, num_cycles

def read_state(content, ptr):
    st = {}
    numbytes, magic_num = unpack_from('<II', content, ptr)
    ptr += 8
    assert magic_num == 0x01234567

    for a in REG_ORDER:
        st[a] = unpack_from("<I", content, ptr)[0]
        ptr += 4

    pf0, pf1 = unpack_from("<II", content, ptr)
    ptr += 8
    st['prefetch'] = [pf0, pf1]

    # RAM 6-byte values
    num_rams = unpack_from("<I", content, ptr)[0]
    ptr += 4

    st['ram'] = []

    for i in range(0, num_rams):
        addr, data = unpack_from("<IH", content, ptr)
        ptr += 6
        assert addr < 0x1000000
        st['ram'].append([addr, (data >> 8)])
        st['ram'].append([addr | 1, data & 0xFF])

    return ptr, st

def decode_test(content, ptr):
    test = {}
    numbytes, magic_num = unpack_from('<II', content, ptr)
    assert magic_num == 0xABC12367
    ptr += 8

    ptr, test['name'] = read_name(content, ptr)

    ptr, test['initial'] = read_state(content, ptr)
    ptr, test['final'] = read_state(content, ptr)

    ptr, test['transactions'], test['length'] = read_transactions(content, ptr)

    return ptr, test

def decode_file(infilename, outfilename):
    print('DECODE', infilename)
    global PRINTED_YET
    with open(infilename, 'rb') as infile:
        content = infile.read()
    ptr = 0
    magic_num, num_tests = unpack_from('<II', content, ptr)
    assert magic_num == 0x1A3F5D71
    ptr += 8
    tests = []

    PRINTED_YET = 0
    for i in range(0, num_tests):
        ptr, test = decode_test(content, ptr)
        tests.append(test)
    if PRINTED_YET > 0:
        print('NUM WITH NO CYCLES: ', PRINTED_YET)
    if os.path.exists(outfilename):
        os.unlink(outfilename)
    with open(outfilename, 'w') as outfile:
        outfile.write(json.dumps(tests, indent=2))


def do_path(where):
    print("Doing path...", where + '/**.json.bin')
    fs = glob.glob(where + '/**.json.bin')
    for fname in fs:
        decode_file(fname, fname[:-4])


def main():
    do_path(M68K_JSON_PATH)

if __name__ == '__main__':
    main()
