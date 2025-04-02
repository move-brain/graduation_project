import copy
import random
from typing import List
from config import xpair, SIZE
from bitset import Bitset
import time

random.seed(int(time.time()))


def get_ones(m: List[Bitset]) -> int:
    return sum(row.count() for row in m)


def get_trans_matrix(trans_m: List[Bitset], m: List[Bitset]) -> None:
    # 清空传入的 trans_m，相当于 C++ 中 trans_m.clear()
    trans_m.clear()
    n = len(m)
    for i in range(n):
        # 初始化一个全0的 Bitset，大小为 SIZE
        tmp = Bitset(SIZE, 0)
        for j in range(n):
            # 赋值逻辑与 C++ 版本完全一致：
            # tmp[m[0].size() - 1 - j] = m[j][m[0].size() - i - 1];
            tmp[len(m) - 1 - j] = m[j][len(m) - i - 1]
        trans_m.append(tmp)


def build_table(m, tab):
    ind = 0  # 在循环外部初始化 ind
    for i in range(len(m)):  # 遍历每一行
        for j in range(len(m)):  # 检查每一列
            if m[i].test(j):  # 检查第 j 位是否为 true
                ind = len(m) - 1 - j  # 更新 ind
                break
        tab[ind] = i  # 将行号 i 存储到 tab[ind]


def exchange(a: xpair, b: xpair) -> bool:
    if a.dst == b.dst:
        return True
    if a.src == b.src:
        return True
    if (a.src != b.dst) and (a.dst != b.src):
        return True
    return False


def exchange_set(seq: List[xpair], start: int, end: int, p: xpair) -> bool:
    if start <= end:
        # Forward traversal from start to end (inclusive)
        for i in range(start, end + 1):
            if not exchange(p, seq[i]):
                return False
    else:
        # Backward traversal from start to end (inclusive)
        for i in range(start, end - 1, -1):
            if not exchange(p, seq[i]):
                return False
    return True


def update_seq_str(seq: List[xpair], tab: List[int]) -> List[xpair]:
    tmp_seq = []
    # 处理 flag 为 False 的元素
    for op in seq:
        if not op.flag:
            tmp_seq.append(op)
    # 处理 flag 为 True 的元素
    for op in reversed(seq):
        if op.flag:
            new_op = xpair(src=tab[op.dst], dst=tab[op.src], flag=False)
            tmp_seq.append(new_op)
    return tmp_seq


def select_oper(m: List[Bitset], max_seq: List[xpair], no_reduced: int, opr_type: int) -> int:
    size = len(m)
    for i in range(size):
        tmp_m = [copy.deepcopy(row) for row in m]
        for j in range(size):
            if i != j:
                no_before = tmp_m[j].count()
                # 执行 XOR 操作： tmp_m[j] ^= tmp_m[i]
                tmp_m[j] ^= tmp_m[i]
                no_after = tmp_m[j].count()
                if (no_before - no_after) > 0:
                    # 如果当前减少值比已有的最大减少值大，则更新
                    if no_reduced < (no_before - no_after):
                        no_reduced = no_before - no_after
                        max_seq.clear()
                        new_ele = xpair(src=i, dst=j, flag=False if opr_type == 0 else True)
                        max_seq.append(new_ele)
                    # 如果减少值等于当前最大减少值，则追加该操作
                    elif no_reduced == (no_before - no_after):
                        new_ele = xpair(src=i, dst=j, flag=False if opr_type == 0 else True)
                        max_seq.append(new_ele)
    return no_reduced


def strgy1(m):
    seq = []
    row_size = len(m)
    col_size = len(m[0]) if row_size > 0 else 0

    mark = [0] * row_size

    for col in range(1, col_size + 1):
        r = 0
        while r < row_size and (m[r][col_size - col] == 0 or mark[r] == 1):
            r += 1
        if r >= row_size:
            continue
        else:
            mark[r] = 1

        for i in range(row_size):
            if m[i][col_size - col] != 0 and i != r:
                # 异或操作
                for j in range(len(m[i])):
                    m[i][j] ^= m[r][j]
                p = xpair(src=r, dst=i, flag=False)
                seq.append(p)
    return seq


def strgy2(m: List[Bitset]) -> List[xpair]:
    trans_m = []
    get_trans_matrix(trans_m, m)
    seq = strgy1(trans_m)
    for op in seq:
        op.flag = True
    get_trans_matrix(m, trans_m)
    tab = [0] * SIZE
    build_table(m, tab)
    final_seq = update_seq_str(seq, tab)
    return final_seq


def strgy3(m: List[Bitset]) -> List[xpair]:
    tmp_seq: List[xpair] = []
    while get_ones(m) != len(m):
        base_oper: List[xpair] = []
        value = 0
        Reduced_Row = select_oper(m, base_oper, value, 0)
        trans_m: List[Bitset] = []
        get_trans_matrix(trans_m, m)

        select_oper(trans_m, base_oper, Reduced_Row, 1)

        if len(base_oper) >= 1:
            rand_num = random.randrange(len(base_oper))
            # rand_num = 0
            op = base_oper[rand_num]
            if not op.flag:
                m[op.dst] ^= m[op.src]
                tmp_seq.append(op)
            else:
                trans_tmp_m: List[Bitset] = []
                get_trans_matrix(trans_tmp_m, m)
                trans_tmp_m[op.dst] ^= trans_tmp_m[op.src]
                get_trans_matrix(m, trans_tmp_m)
                tmp_seq.append(op)
        else:
            break

    if get_ones(m) != len(m):
        rnd = random.randrange(2)
        if rnd == 0:
            seq_2 = strgy1(m)  # 生成一个新的列表
            tmp_seq.extend(copy.deepcopy(seq_2))
        elif rnd == 1:
            seq_2 = strgy2(m)
            tmp_seq.extend(copy.deepcopy(seq_2))  # 或者直接：tmp_seq.extend(seq_2)

    tab = [0] * SIZE
    build_table(m, tab)
    final_seq = update_seq_str(tmp_seq, tab)
    return final_seq
