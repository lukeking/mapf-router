# Spike 001 — Space-Time A* 吞吐量比較

支撐 `docs/decisions/001-tech-stack-evaluation.md` 的 G1 效能可達性判定。
依憲章原則 IV（Benchmark 可重現），程式碼與來源資訊一併留存。

## 這個 spike 測什麼

把求解延遲拆成兩個因子：

```
求解延遲  ≈  每次求解的節點展開數  ×  每次展開的成本
             └─ 演算法決定，與語言無關 ─┘   └─ 語言決定 ─┘
```

本 spike 只測**右因子**。左因子（CBS 高階節點數）需實作 CBS 後另行量測，尚未取得。

## 有效性設計

四個實作必須展開**完全相同的節點、且順序相同**，否則比較的就不只是語言差異。
為此節點優先權打包成單一 int64，跨語言排序一致：

```
key = f<<42 | g<<30 | x<<21 | y<<12 | t     (12/12/9/9/12 bits)
```

執行後 MUST 檢查四者的 `expansions` 與 `cost_sum` 完全一致。不一致即代表實作有差異，
時間數據無效。

## 執行

```bash
python3 gen_problem.py .                      # 產生 spike.map / spike.queries（種子固定）
g++ -std=c++20 -O2 -march=native -o astar astar.cpp
./astar spike.map spike.queries               # cpp-hash 與 cpp-flat 兩種 closed set
python3 astar_py.py spike.map spike.queries   # 純 CPython
python3 astar_nb.py spike.map spike.queries   # 需 numba + numpy
```

## 來源資訊（2026-07-20 該次執行）

| 項目 | 值 |
|---|---|
| 測資 | 合成 octile 地圖，128×128，20% 障礙，**seed 42**（非真實 movingai 資料集） |
| 查詢 | 100 組單代理人查詢，Manhattan 距離 ≥ 128 |
| 硬體 | AMD Ryzen 7 3700X 8-Core |
| 編譯 | g++ 13.3.0，`-std=c++20 -O2 -march=native` |
| Python | CPython 3.12.3 |
| Numba | 0.66.0 / NumPy 2.4.6 |
| 有效性 | 四實作皆 `expansions=353985`、`cost_sum=15395` ✓ |

展開數與成本完全可重現；**吞吐量有 5–8% 的執行間變異**，數字請讀作量級與比率。

## 測資為合成而非真實 benchmark

movingai 的正式資料集未使用。本 spike 測的是**每次展開的成本**，這是 per-node 常數，
對障礙物版面不敏感；換成真實 benchmark 會改變絕對數字，但不會改變候選之間的比率——
而比率才是技術選型需要的。M1 接上真正的 map loader 後，應以真實資料集重跑一次確認。

## 結果與解讀

見 `docs/decisions/001-tech-stack-evaluation.md` §7.5。摘要：

| 實作 | expansions/sec | 對 python |
|---|---:|---:|
| `cpp-flat` | 6,020,774 | 23.4× |
| `numba` | 5,234,545 | 20.4× |
| `cpp-hash` | 3,982,712 | 15.5× |
| `python` | 256,761 | 1.0× |
