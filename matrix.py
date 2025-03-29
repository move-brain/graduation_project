# matrix.py
from typing import List
from config import SIZE
from bitset import Bitset


def get_matrix() -> List[Bitset]:
    raw = [
        # 0x814c,
        # 0x4962,
        # 0x2431,
        # 0x1298,
        # 0x18c4,
        # 0x9426,
        # 0x4213,
        # 0x2189,
        # 0x4c81,
        # 0x6249,
        # 0x3124,
        # 0x9812,
        # 0xc418,
        # 0x2694,
        # 0x1342,
        # 0x8921
        0x01818080,
        0x81c14040,
        0x40602020,
        0x21311010,
        0x11190808,
        0x080c0404,
        0x04060202,
        0x02030101,
        0x80018180,
        0x4081c140,
        0x20406020,
        0x10213110,
        0x08111908,
        0x04080c04,
        0x02040602,
        0x01020301,
        0x80800181,
        0x404081c1,
        0x20204060,
        0x10102131,
        0x08081119,
        0x0404080c,
        0x02020406,
        0x01010203,
        0x81808001,
        0xc1404081,
        0x60202040,
        0x31101021,
        0x19080811,
        0x0c040408,
        0x06020204,
        0x03010102
    ]
    return [Bitset(SIZE, row) for row in raw]


FILENAME = 'FSE_SKOP15_4x4_4.txt'
