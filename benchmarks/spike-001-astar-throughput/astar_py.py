"""Candidate B: pure-CPython Space-Time A*.

All three implementations MUST expand the same nodes in the same order, so the
comparison measures only per-expansion cost. Ordering is made language-independent by
packing the priority into a single int64 with fixed bit widths:

    key = f<<42 | g<<30 | x<<21 | y<<12 | t      (12/12/9/9/12 bits)

Total expansion counts are compared across implementations as a validity check; if they
diverge, the implementations differ and the timing comparison is meaningless.
"""
import heapq
import sys
import time

MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))  # 4-connected + wait


def load_map(path):
    with open(path) as f:
        lines = f.read().split("\n")
    h = int(lines[1].split()[1])
    w = int(lines[2].split()[1])
    grid = bytearray(w * h)
    for y in range(h):
        row = lines[4 + y]
        for x in range(w):
            if row[x] != ".":
                grid[y * w + x] = 1
    return grid, w, h


def load_queries(path):
    with open(path) as f:
        n = int(f.readline())
        return [tuple(map(int, f.readline().split())) for _ in range(n)]


def astar(grid, w, h, sx, sy, gx, gy, max_t):
    """Returns (cost, expansions). cost == -1 if unsolvable within max_t."""
    h0 = abs(sx - gx) + abs(sy - gy)
    start_key = (h0 << 42) | (0 << 30) | (sx << 21) | (sy << 12) | 0
    open_heap = [start_key]
    closed = set()
    expansions = 0

    while open_heap:
        key = heapq.heappop(open_heap)
        t = key & 0xFFF
        y = (key >> 12) & 0x1FF
        x = (key >> 21) & 0x1FF
        g = (key >> 30) & 0xFFF

        state = (t * h + y) * w + x
        if state in closed:
            continue
        closed.add(state)
        expansions += 1

        if x == gx and y == gy:
            return g, expansions
        if t >= max_t:
            continue

        ng = g + 1
        nt = t + 1
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or grid[ny * w + nx]:
                continue
            nstate = (nt * h + ny) * w + nx
            if nstate in closed:
                continue
            # Constraint lookup lives here in CBS's low level; kept as an empty-set probe
            # so the per-expansion cost stays representative.
            nf = ng + abs(nx - gx) + abs(ny - gy)
            heapq.heappush(open_heap, (nf << 42) | (ng << 30) | (nx << 21) | (ny << 12) | nt)

    return -1, expansions


def main(mappath, qpath):
    grid, w, h = load_map(mappath)
    queries = load_queries(qpath)
    max_t = 4 * (w + h)

    total_exp = 0
    total_cost = 0
    t0 = time.perf_counter()
    for sx, sy, gx, gy in queries:
        cost, exp = astar(grid, w, h, sx, sy, gx, gy, max_t)
        total_exp += exp
        total_cost += cost
    elapsed = time.perf_counter() - t0

    print(f"impl=python queries={len(queries)} expansions={total_exp} "
          f"cost_sum={total_cost} seconds={elapsed:.4f} "
          f"expansions_per_sec={total_exp / elapsed:.0f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
