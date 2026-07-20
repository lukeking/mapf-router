"""Candidate C: Numba nopython Space-Time A*.

NOTE ON EXPRESSIVENESS (this is itself a spike finding):
Numba's nopython mode has no usable hash-set, so the CPython `set` used for the closed
list cannot be carried over — a flat generation-stamped array is forced instead. The heap
must also be hand-rolled on a preallocated array because `heapq` is unsupported. The
implementation is therefore structurally comparable to `cpp-flat`, NOT to `python`.
That constraint is the concrete form of the "algorithm expressiveness" penalty the
evaluation framework assigned to candidate C.
"""
import sys
import time

import numpy as np
from numba import njit

DX = np.array([1, -1, 0, 0, 0], dtype=np.int64)
DY = np.array([0, 0, 1, -1, 0], dtype=np.int64)


@njit(cache=True)
def _push(heap, size, key):
    heap[size] = key
    i = size
    while i > 0:
        parent = (i - 1) >> 1
        if heap[parent] <= heap[i]:
            break
        heap[parent], heap[i] = heap[i], heap[parent]
        i = parent
    return size + 1


@njit(cache=True)
def _pop(heap, size):
    top = heap[0]
    size -= 1
    heap[0] = heap[size]
    i = 0
    while True:
        l, r, best = 2 * i + 1, 2 * i + 2, i
        if l < size and heap[l] < heap[best]:
            best = l
        if r < size and heap[r] < heap[best]:
            best = r
        if best == i:
            break
        heap[best], heap[i] = heap[i], heap[best]
        i = best
    return top, size


@njit(cache=True)
def _astar(grid, w, h, sx, sy, gx, gy, max_t, heap, flat, gen):
    h0 = abs(sx - gx) + abs(sy - gy)
    size = _push(heap, 0, (h0 << 42) | (sx << 21) | (sy << 12))
    expansions = 0

    while size > 0:
        key, size = _pop(heap, size)
        t = key & 0xFFF
        y = (key >> 12) & 0x1FF
        x = (key >> 21) & 0x1FF
        g = (key >> 30) & 0xFFF

        state = (t * h + y) * w + x
        if flat[state] == gen:
            continue
        flat[state] = gen
        expansions += 1

        if x == gx and y == gy:
            return g, expansions, size
        if t >= max_t:
            continue

        ng = g + 1
        nt = t + 1
        for i in range(5):
            nx = x + DX[i]
            ny = y + DY[i]
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if grid[ny * w + nx]:
                continue
            nstate = (nt * h + ny) * w + nx
            if flat[nstate] == gen:
                continue
            nf = ng + abs(nx - gx) + abs(ny - gy)
            size = _push(heap, size,
                         (nf << 42) | (ng << 30) | (nx << 21) | (ny << 12) | nt)

    return -1, expansions, size


@njit(cache=True)
def _run_all(grid, w, h, queries, max_t, heap, flat):
    total_exp = 0
    total_cost = 0
    for i in range(queries.shape[0]):
        cost, exp, _ = _astar(grid, w, h, queries[i, 0], queries[i, 1],
                              queries[i, 2], queries[i, 3], max_t, heap, flat, i + 1)
        total_exp += exp
        total_cost += cost
    return total_exp, total_cost


def main(mappath, qpath):
    with open(mappath) as f:
        lines = f.read().split("\n")
    h = int(lines[1].split()[1])
    w = int(lines[2].split()[1])
    grid = np.zeros(w * h, dtype=np.uint8)
    for y in range(h):
        row = lines[4 + y]
        for x in range(w):
            if row[x] != ".":
                grid[y * w + x] = 1

    with open(qpath) as f:
        n = int(f.readline())
        queries = np.array([[int(v) for v in f.readline().split()] for _ in range(n)],
                           dtype=np.int64)

    max_t = 4 * (w + h)
    heap = np.zeros(8_000_000, dtype=np.int64)
    flat = np.zeros((max_t + 1) * h * w, dtype=np.uint16)

    # Warm-up run triggers JIT compilation; excluded from the measurement.
    warm = queries[:1].copy()
    _run_all(grid, w, h, warm, max_t, heap, flat)
    flat[:] = 0

    t0 = time.perf_counter()
    total_exp, total_cost = _run_all(grid, w, h, queries, max_t, heap, flat)
    elapsed = time.perf_counter() - t0

    print(f"impl=numba queries={n} expansions={total_exp} cost_sum={total_cost} "
          f"seconds={elapsed:.4f} expansions_per_sec={total_exp / elapsed:.0f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
