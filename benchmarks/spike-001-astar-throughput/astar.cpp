// Candidates A / D-core: C++20 Space-Time A*.
//
// Two closed-set variants are measured:
//   "cpp-hash" uses unordered_set, mirroring CPython's set so the comparison is
//              apples-to-apples on data structures (same algorithm, different language).
//   "cpp-flat" uses a flat visited array, which is what one would actually write in C++.
//              The gap between the two is the headroom the language additionally unlocks.
//
// Node ordering is identical to the Python and Numba implementations: a single packed
// int64 key, f<<42 | g<<30 | x<<21 | y<<12 | t.

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

static constexpr int DX[5] = {1, -1, 0, 0, 0};
static constexpr int DY[5] = {0, 0, 1, -1, 0};

struct Problem {
    std::vector<uint8_t> grid;
    int w = 0, h = 0;
    std::vector<std::array<int, 4>> queries;
};

static Problem load(const std::string& mappath, const std::string& qpath) {
    Problem p;
    std::ifstream mf(mappath);
    std::string line, tok;
    std::getline(mf, line);                       // type octile
    std::getline(mf, line); { std::istringstream s(line); s >> tok >> p.h; }
    std::getline(mf, line); { std::istringstream s(line); s >> tok >> p.w; }
    std::getline(mf, line);                       // map
    p.grid.assign(static_cast<size_t>(p.w) * p.h, 0);
    for (int y = 0; y < p.h; ++y) {
        std::getline(mf, line);
        for (int x = 0; x < p.w; ++x)
            p.grid[static_cast<size_t>(y) * p.w + x] = (line[x] != '.') ? 1 : 0;
    }
    std::ifstream qf(qpath);
    int n; qf >> n;
    p.queries.resize(n);
    for (int i = 0; i < n; ++i)
        qf >> p.queries[i][0] >> p.queries[i][1] >> p.queries[i][2] >> p.queries[i][3];
    return p;
}

template <bool FlatClosed>
static int64_t astar(const Problem& p, int sx, int sy, int gx, int gy, int max_t,
                     int64_t& expansions, std::vector<uint16_t>& flat, uint16_t gen) {
    const int w = p.w, h = p.h;
    std::priority_queue<int64_t, std::vector<int64_t>, std::greater<int64_t>> open;
    std::unordered_set<int64_t> closed;
    // Generation stamping avoids clearing a 16M-entry array per query, which would
    // otherwise dominate the measurement.

    const int64_t h0 = std::abs(sx - gx) + std::abs(sy - gy);
    open.push((h0 << 42) | (int64_t(sx) << 21) | (int64_t(sy) << 12));

    while (!open.empty()) {
        const int64_t key = open.top(); open.pop();
        const int t = int(key & 0xFFF);
        const int y = int((key >> 12) & 0x1FF);
        const int x = int((key >> 21) & 0x1FF);
        const int g = int((key >> 30) & 0xFFF);

        const int64_t state = (int64_t(t) * h + y) * w + x;
        if constexpr (FlatClosed) {
            if (flat[state] == gen) continue;
            flat[state] = gen;
        } else {
            if (!closed.insert(state).second) continue;
        }
        ++expansions;

        if (x == gx && y == gy) return g;
        if (t >= max_t) continue;

        const int ng = g + 1, nt = t + 1;
        for (int i = 0; i < 5; ++i) {
            const int nx = x + DX[i], ny = y + DY[i];
            if (nx < 0 || nx >= w || ny < 0 || ny >= h) continue;
            if (p.grid[static_cast<size_t>(ny) * w + nx]) continue;
            const int64_t nstate = (int64_t(nt) * h + ny) * w + nx;
            if constexpr (FlatClosed) {
                if (flat[nstate] == gen) continue;
            } else {
                if (closed.count(nstate)) continue;
            }
            const int64_t nf = ng + std::abs(nx - gx) + std::abs(ny - gy);
            open.push((nf << 42) | (int64_t(ng) << 30) | (int64_t(nx) << 21) |
                      (int64_t(ny) << 12) | nt);
        }
    }
    return -1;
}

template <bool FlatClosed>
static void run(const Problem& p, const char* label) {
    const int max_t = 4 * (p.w + p.h);
    std::vector<uint16_t> flat;
    if constexpr (FlatClosed)
        flat.assign(static_cast<size_t>(max_t + 1) * p.h * p.w, 0);

    int64_t total_exp = 0, total_cost = 0;
    uint16_t gen = 0;
    const auto t0 = std::chrono::steady_clock::now();
    for (const auto& q : p.queries)
        total_cost += astar<FlatClosed>(p, q[0], q[1], q[2], q[3], max_t, total_exp, flat,
                                        ++gen);
    const double elapsed =
        std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();

    std::printf("impl=%s queries=%zu expansions=%lld cost_sum=%lld seconds=%.4f "
                "expansions_per_sec=%.0f\n",
                label, p.queries.size(), (long long)total_exp, (long long)total_cost,
                elapsed, total_exp / elapsed);
}

int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: astar <map> <queries>\n"); return 1; }
    const Problem p = load(argv[1], argv[2]);
    run<false>(p, "cpp-hash");
    run<true>(p, "cpp-flat");
    return 0;
}
