"""Generate a deterministic movingai-format map + query set for the Space-Time A* spike.

The real movingai benchmark is not used here: this is a synthetic stand-in with the same
structural characteristics (octile grid, ~20% random obstacles). Expansions/sec is a
per-node cost and is not very sensitive to the exact obstacle layout, so a stand-in is
adequate for the LANGUAGE comparison this spike is measuring. Swapping in the real
benchmark later changes absolute numbers, not the ratios between candidates.
"""
import collections
import sys

W = H = 128
OBSTACLE_RATE = 0.20
N_QUERIES = 100
SEED = 42


def lcg(seed):
    """Tiny deterministic PRNG so the map is reproducible without numpy."""
    state = seed
    while True:
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        yield (state >> 33) / float(1 << 31)


def main(outdir):
    rng = lcg(SEED)
    grid = [[1 if next(rng) < OBSTACLE_RATE else 0 for _ in range(W)] for _ in range(H)]

    # Largest connected component, so every query is guaranteed solvable.
    seen = [[False] * W for _ in range(H)]
    best = []
    for sy in range(H):
        for sx in range(W):
            if grid[sy][sx] or seen[sy][sx]:
                continue
            comp, q = [], collections.deque([(sx, sy)])
            seen[sy][sx] = True
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not grid[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            if len(comp) > len(best):
                best = comp

    # Queries: sample far-apart pairs so paths are long and expansion counts are meaningful.
    queries = []
    n = len(best)
    while len(queries) < N_QUERIES:
        a = best[int(next(rng) * n) % n]
        b = best[int(next(rng) * n) % n]
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) >= (W + H) // 2:
            queries.append((a[0], a[1], b[0], b[1]))

    with open(f"{outdir}/spike.map", "w") as f:
        f.write(f"type octile\nheight {H}\nwidth {W}\nmap\n")
        for y in range(H):
            f.write("".join("@" if grid[y][x] else "." for x in range(W)) + "\n")

    with open(f"{outdir}/spike.queries", "w") as f:
        f.write(f"{len(queries)}\n")
        for sx, sy, gx, gy in queries:
            f.write(f"{sx} {sy} {gx} {gy}\n")

    print(f"map {W}x{H}, largest component {n} cells, {len(queries)} queries")


if __name__ == "__main__":
    main(sys.argv[1])
