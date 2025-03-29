import time
from matrix import FILENAME, get_matrix
from reduce import reduce_matrix, get_reduced_matrix
from typing import List


def print_seq(m: List, tmp_m: List, seq: List) -> None:
    with open(FILENAME, "w") as f:
        f.write("Original Matrix:\n")
        for row in m:
            f.write(str(row) + "\n")
        f.write("\n\n")
        f.write("Reduced Matrix:\n")
        for row in tmp_m:
            f.write(str(row) + "\n")
        f.write("\n\n")
        f.write(f"Xor Count = {len(seq)}\n")
        tab = [0] * len(tmp_m)
        for i in range(len(tmp_m)):
            for j in range(len(tmp_m)):
                if tmp_m[i][len(tmp_m) - 1 - j]:
                    tab[i] = j
                    break
        for i in reversed(range(len(seq))):
            current = seq[i]
            line = f"x[{tab[current.dst]}] = x[{tab[current.dst]}] ^ x[{tab[current.src]}]"
            tmp_m[current.dst] ^= tmp_m[current.src]
            found = False
            for j in range(len(m)):
                if str(tmp_m[current.dst]) == str(m[j]):
                    line += f"    y[{j}]\n"
                    found = True
                    break
            if not found:
                line += "\n"
            f.write(line)


def main():
    counter = 100000
    start_time = time.time()
    print(FILENAME)
    try:
        while True:
            m_orig = get_matrix()
            seq = reduce_matrix(m_orig)
            tmp_m = get_reduced_matrix(seq, m_orig)
            print(f"minimal = {counter}   current = {len(seq)}\n")
            if len(seq) < counter:
                counter = len(seq)
                print_seq(m_orig, tmp_m, seq)
    except KeyboardInterrupt:
        end_time = time.time()
        time_used = end_time - start_time
        print(f"\nTime used = {time_used:.2f} seconds")


if __name__ == "__main__":
    main()
