import time
import copy
from matrix import FILENAME, get_matrix
from reduce import reduce_matrix, get_reduced_matrix
from typing import List
# 假设 xpair 类已经在你的代码中定义

# 引入 Qiskit 模块
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


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


def build_quantum_circuit(seq, num_qubits):
    """
    根据优化后的 XOR 操作序列构造量子电路。
    每个操作 (src, dst) 对应于一条 CNOT 门（控制比特为 src，目标比特为 dst）。
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    for op in seq:
        qc.cx(op.src, op.dst)
    # 添加测量，将所有量子比特测量到经典寄存器
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def simulate_circuit(qc):
    backend = Aer.get_backend('qasm_simulator')
    # 使用 transpile 对电路进行编译优化，适应目标后端
    transpiled_qc = transpile(qc, backend=backend)
    job = backend.run(transpiled_qc, shots=1024)
    result = job.result()
    counts = result.get_counts(qc)
    print("量子电路测量结果：", counts)
    plot_histogram(counts)
    plt.show()


def main():
    counter = 100000
    start_time = time.time()
    print("文件名：", FILENAME)
    try:
        while True:
            # 取得原始矩阵（这里返回的是 Bitset 对象列表）
            m_orig = get_matrix()
            # 计算优化后的 XOR 操作序列（这里深拷贝确保原始数据不被修改）
            seq = reduce_matrix(copy.deepcopy(m_orig))
            # 根据 seq 得到最终的矩阵（仅用于打印展示对比）
            tmp_m = get_reduced_matrix(seq, copy.deepcopy(m_orig))

            print("当前 seq 序列：", seq)
            print(f"当前操作数 = {len(seq)}, 最小记录 = {counter}\n")

            if len(seq) < counter:
                counter = len(seq)
                # 输出当前结果到文件
                print_seq(m_orig, tmp_m, seq)

                # 集成量子编程部分
                # 假设量子比特数等于矩阵的列数（或行数）
                num_qubits = len(seq)
                qc = build_quantum_circuit(seq, num_qubits)
                print("生成的量子电路：")
                print(qc.draw())

                # 仿真并展示量子电路的测量结果
                simulate_circuit(qc)

    except KeyboardInterrupt:
        end_time = time.time()
        time_used = end_time - start_time
        print(f"\n总耗时 = {time_used:.2f} 秒")


if __name__ == "__main__":
    main()
