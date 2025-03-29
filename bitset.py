class Bitset:
    def __init__(self, size: int, value: int = 0):
        self.size = size
        self.value = value & ((1 << size) - 1)

    def __getitem__(self, index: int) -> bool:
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of range [0, {self.size})")
        return (self.value >> index) & 1 == 1

    def __setitem__(self, index: int, value: bool):
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of range")
        if value:
            self.value |= (1 << index)  # 将指定位置1
        else:
            self.value &= ~(1 << index)  # 将指定位置0

    def set(self, index: int):
        if 0 <= index < self.size:
            self.value |= (1 << index)
        else:
            raise IndexError

    def clear(self, index: int):
        if 0 <= index < self.size:
            self.value &= ~(1 << index)
        else:
            raise IndexError

    def __len__(self) -> int:
        return self.size  # 直接返回初始化时的位数

    def flip(self, index: int = None):
        if index is None:
            self.value ^= ((1 << self.size) - 1)
        elif 0 <= index < self.size:
            self.value ^= (1 << index)
        else:
            raise IndexError

    def count(self) -> int:
        return bin(self.value).count('1')

    def any(self) -> bool:
        return self.value != 0

    def all(self) -> bool:
        return self.value == ((1 << self.size) - 1)

    def __ixor__(self, other: 'Bitset') -> 'Bitset':
        if not isinstance(other, Bitset):
            raise TypeError("Operand must be a Bitset")
        if self.size != other.size:
            raise ValueError("Bitsets must be of the same size for in-place XOR")
        self.value ^= other.value
        self.value &= (1 << self.size) - 1  # 确保不超出当前size
        return self

    def __and__(self, other: 'Bitset') -> 'Bitset':
        return Bitset(max(self.size, other.size), self.value & other.value)

    def __or__(self, other: 'Bitset') -> 'Bitset':
        return Bitset(max(self.size, other.size), self.value | other.value)

    def __repr__(self):
        return bin(self.value)[2:].zfill(self.size)[::-1]

    def __xor__(self, other: 'Bitset') -> 'Bitset':
        if not isinstance(other, Bitset):
            raise TypeError("Operand must be a Bitset")
        new_size = max(self.size, other.size)
        new_value = (self.value ^ other.value) & ((1 << new_size) - 1)
        return Bitset(new_size, new_value)

    def test(self, index: int) -> bool:
        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} out of range [0, {self.size - 1}]")
        mask = 1 << index
        return (self.value & mask) != 0
