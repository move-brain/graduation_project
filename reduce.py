import copy
from typing import List
from config import xpair, SIZE
from strategy import build_table, strgy3, exchange_set, exchange
from bitset import Bitset
import threading

THREAD_NUM = 4
PTHREAD_CREATE_JOINABLE = 0


def get_reduced_matrix(seq: List[xpair], m: List[Bitset]) -> List[Bitset]:
    tmp_m = [copy.deepcopy(row) for row in m]
    for pair in seq:
        tmp_m[pair.dst] ^= tmp_m[pair.src]
    return tmp_m


def exchange(a, b):
    if a.dst == b.dst:
        return True
    if a.src == b.src:
        return True
    if a.src != b.dst and a.dst != b.src:
        return True
    return False


# a = 0


def get_table(seq, table, osize, nsize):
    # global a
    # 创建一个 nsize x nsize 的二维列表，初始化为 0
    table = [[0 for _ in range(nsize)] for _ in range(nsize)]
    # 获取序列长度
    s = len(seq)
    # if a == 0:
    #     print("table", table)
    #     print("s", s)
    #     a = a + 1
    # 对于每个索引 i
    for i in range(s):
        # 设置对角线元素为 1
        table[i][i] = 1

        # 从 i+1 到 s-1 检查右侧元素
        for j in range(i + 1, s):
            if exchange(seq[i], seq[j]):
                table[i][j] = 1
            else:
                # 后续元素保持 0（已初始化），直接跳出
                break

        # 从 i-1 到 0 检查左侧元素
        for j in range(i - 1, -1, -1):
            if exchange(seq[i], seq[j]):
                table[i][j] = 1
            else:
                # 后续元素保持 0（已初始化），直接跳出
                break

    # 返回新构建的表
    return table


def reduce0(seq, table):
    """
    对序列 seq 进行一次 reduce 操作，返回是否成功。
    """
    s = len(seq)
    for i in range(s):
        for j in range(i + 1, s):
            if table[i][j - 1] == 0 and table[j][i + 1] == 0:
                break
            if seq[i].src != seq[j].src:
                continue
            for k in range(j + 1, s):
                if table[k][j + 1] == 0 and table[j][k - 1] == 0:
                    break
                if seq[k].dst != seq[i].dst:
                    if seq[k].dst != seq[j].dst:
                        continue
                    elif seq[k].src != seq[i].dst:
                        continue
                elif seq[k].src != seq[j].dst:
                    continue
                index = -1
                if table[i][j - 1] and table[k][j + 1]:
                    index = j - 1
                elif table[j][i + 1] and table[k][j + 1] and exchange_set(seq, j - 1, i + 1, seq[k]):
                    index = i
                elif table[i][j - 1] and table[j][k - 1] and exchange_set(seq, j + 1, k - 1, seq[i]):
                    index = k - 2
                else:
                    continue
                tmp1 = seq[k]
                tmp2 = xpair(seq[i].src, seq[k].src)
                del seq[k]
                del seq[j]
                del seq[i]
                seq.insert(index, tmp1)
                seq.insert(index + 1, tmp2)
                return True
    return False


def reduce1(seq: List[xpair], table: List[List[int]]) -> bool:
    s = len(seq)
    for i in range(s):
        for j in range(i + 1, s):
            if table[i][j - 1] == 0 and table[j][i + 1] == 0:
                break
            if seq[i].src != seq[j].dst and seq[i].dst != seq[j].dst:
                continue
            for k in range(j + 1, s):
                if table[k][j + 1] == 0 and table[j][k - 1] == 0:
                    break
                if seq[k].src != seq[j].src:
                    continue
                else:
                    if seq[j].dst == seq[i].dst:
                        if seq[k].dst != seq[i].src:
                            continue
                    if seq[j].dst == seq[i].src:
                        if seq[k].dst != seq[i].dst:
                            continue
                index = -1
                if table[i][j - 1] and table[k][j + 1]:
                    index = j - 1
                elif table[j][i + 1] and table[k][j + 1] and exchange_set(seq, j - 1, i + 1, seq[k]):
                    index = i
                elif table[i][j - 1] and table[j][k - 1] and exchange_set(seq, j + 1, k - 1, seq[i]):
                    index = k - 2
                else:
                    continue
                # 创建新元素
                tmp1 = xpair(src=seq[j].src, dst=seq[i].src)
                tmp2 = seq[i]

                # 计算在 index 之前被删除的元素数量
                # m = sum(1 for x in [i, j, k] if x < index)

                # 从大到小删除，防止索引偏移
                del seq[k]  # 先删 k，不影响 j 和 i
                del seq[j]  # 再删 j，不影响 i
                del seq[i]  # 最后删 i

                # 插入新元素，位置调整为 index - m
                seq.insert(index, tmp1)
                seq.insert(index + 1, tmp2)
                return True
    return False


def reduce2(seq: List[xpair], table: List[List[int]]) -> bool:
    s = len(seq)
    for i in range(s):
        for j in range(i + 1, s):
            if table[i][j - 1] == 0 and table[j][i + 1] == 0:
                break
            if seq[j].src != seq[i].dst and seq[j].dst != seq[i].dst:
                continue
            for k in range(j + 1, s):
                if table[k][j + 1] == 0 and table[j][k - 1] == 0:
                    break
                if seq[k].src != seq[i].src:
                    continue

                if seq[j].src == seq[i].dst:
                    if seq[k].dst != seq[j].dst:
                        continue
                elif seq[j].dst == seq[i].dst:
                    if seq[k].dst != seq[j].src:
                        continue
                else:
                    continue

                index = -1
                if table[i][j - 1] and table[k][j + 1]:
                    index = j - 1
                elif table[j][i + 1] and table[k][j + 1]:
                    if exchange_set(seq, j - 1, i + 1, seq[k]):
                        index = i
                elif table[i][j - 1] and table[j][k - 1]:
                    if exchange_set(seq, j + 1, k - 1, seq[i]):
                        index = k - 2
                else:
                    continue

                if index == -1:
                    continue

                tmp1 = xpair(src=0, dst=seq[k].dst)
                tmp2 = xpair(src=0, dst=seq[i].dst)
                if seq[j].src == seq[i].dst:
                    tmp1 = xpair(src=seq[j].src, dst=tmp1.dst)
                    tmp2 = xpair(src=seq[i].src, dst=tmp2.dst)
                else:
                    tmp1 = xpair(src=seq[i].src, dst=tmp1.dst)
                    tmp2 = xpair(src=seq[j].src, dst=tmp2.dst)

                del seq[k]
                del seq[j]
                del seq[i]

                seq.insert(index, tmp1)
                seq.insert(index + 1, tmp2)
                return True
    return False


def reduce3(seq: List[xpair], table: List[List[int]]) -> bool:
    s = len(seq)
    for i in range(s):
        for j in range(i + 1, s):
            if table[i][j - 1] == 0 and table[j][i + 1] == 0:
                break
            if seq[j].dst != seq[i].src or seq[j].src != seq[i].dst:
                continue

            index = j - 1 if table[i][j - 1] else i

            tmp = seq[j]

            # 删除 seq[j] 和 seq[i]（从后向前删除）
            del seq[j]
            del seq[i]

            # 插入 tmp 到 index 位置
            seq.insert(index, tmp)

            # 计算掩码
            mask = seq[index].dst ^ seq[index].src

            # 更新后续元素
            for k in range(index + 1, len(seq)):
                if seq[k].dst == seq[index].dst or seq[k].dst == seq[index].src:
                    seq[k].dst ^= mask
                if seq[k].src == seq[index].dst or seq[k].src == seq[index].src:
                    seq[k].src ^= mask
            return True
    return False


def binary_array_to_hex(binary_array):
    # 将二进制数组转换为字符串（例如 [1,0,1] → "101"）
    binary_str = ''.join(map(str, binary_array))

    # 计算需要补零的位数，使总长度为8的倍数（用于按字节分组）
    pad_length = (-len(binary_str)) % 8
    padded_str = '0' * pad_length + binary_str  # 左侧补零

    # 分割为每8位一组，每组转换为两位十六进制字符
    hex_bytes = []
    for i in range(0, len(padded_str), 8):
        byte_str = padded_str[i:i + 8]  # 提取8位（一个字节）
        hex_byte = format(int(byte_str, 2), '02x')  # 转为两位十六进制（小写）
        hex_bytes.append(hex_byte)

    # 合并所有十六进制字符并添加前缀
    return '0x' + ''.join(hex_bytes)


a = 0


def reduce_step(seq):
    # print(len(seq))
    # global a
    tab = get_table(seq, None, 0, len(seq))
    # if a == 0:
    #     print("len", len(seq))
    #     print("tab[0]", tab[1])
    #     a = a + 1
    # print([
    #     format(int(''.join(map(str, sublist)), 2), 'x')
    #     for sublist in tab
    # ])
    # print("tab[0]", binary_array_to_hex(tab[0]))

    i = 0
    NUM = 4
    counter = 0
    # a = a + 1
    while counter != NUM:
        if i == 0:
            if reduce0(seq, tab):
                # if a == 1:
                #     # print("i", i, "counter", counter)
                #     print("reduce0")
                tab = get_table(seq, tab, len(seq) + 1, len(seq))
                counter = 0
            else:
                i = (i + 1) % NUM
                counter += 1
        elif i == 1:
            if reduce1(seq, tab):
                # if a == 1:
                #     # print("i", i, "counter", counter)
                #     print("reduce1")
                tab = get_table(seq, tab, len(seq) + 1, len(seq))
                counter = 0
            else:
                i = (i + 1) % NUM
                counter += 1
        elif i == 2:
            if reduce2(seq, tab):
                # if a == 1:
                #     # print("i", i, "counter", counter)
                #     print("reduce2")
                tab = get_table(seq, tab, len(seq) + 1, len(seq))
                counter = 0
            else:
                i = (i + 1) % NUM
                counter += 1
        elif i == 3:
            if reduce3(seq, tab):
                # if a == 1:
                #     # print("i", i, "counter", counter)
                #     print("reduce3")
                tab = get_table(seq, tab, len(seq) + 1, len(seq))
                counter = 0
            else:
                i = (i + 1) % NUM
                counter += 1

    return len(seq)


def get_equivalent_seq(seq: List[xpair], gap: int, start: int) -> None:
    m = []
    for i in range(SIZE):
        tmp = Bitset(SIZE, 0)
        tmp[SIZE - 1 - i] = True  # 设置唯一的 1
        m.append(tmp)

    for i in range(start + gap - 1, start - 1, -1):
        m[seq[i].dst] ^= m[seq[i].src]
    seq_here = strgy3(m)
    del seq[start:start + gap]
    seq[start:start] = seq_here
    tab = [0] * SIZE
    build_table(m, tab)
    update_seq(seq, tab, start + len(seq_here))


def update_seq(seq: List[xpair], tab: List[int], start: int) -> None:
    for i in range(start, len(seq)):
        seq[i].src = tab[seq[i].src]
        seq[i].dst = tab[seq[i].dst]


class ThreadData:
    def __init__(self, seq, gap, start, length):
        self.seq = seq
        self.gap = gap
        self.start = start
        self.len = length


def reduce_thread(data):
    """
    参数:
        data (ThreadData): 包含 seq, gap, start 和 len 的对象
    返回:
        ThreadData: 更新后的 data 对象
    """
    get_equivalent_seq(data.seq, data.gap, data.start)
    data.len = reduce_step(data.seq)
    return data


def reduce_matrix(m: List[Bitset]) -> List[xpair]:
    seq = strgy3(m)
    l = reduce_step(seq)
    gap = l
    start = 0
    flag = True
    # thread_datas = []
    while flag:
        thread_datas = []
        for j in range(THREAD_NUM):
            # print("gap", gap, "start", start)
            td = ThreadData(copy.deepcopy(seq), gap, start, l)
            thread_datas.append(td)
            if gap != 3 or start != l - gap:
                if start == l - gap:
                    gap -= 1
                    start = 0
                else:
                    start += 1
            else:
                flag = False

        threads = []
        for td in thread_datas:
            t = threading.Thread(target=reduce_thread, args=(td,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        for td in thread_datas:
            if td.len < l:
                seq = td.seq
                l = td.len
                gap = l
                start = 0

    return seq
