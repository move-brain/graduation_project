# config.py
from dataclasses import dataclass

SIZE = 16  # 矩阵大小


@dataclass
class xpair:
    src: int
    dst: int
    flag: bool = False

    def __repr__(self):
        return f"xpair(src={self.src}, dst={self.dst}, flag={self.flag})"
