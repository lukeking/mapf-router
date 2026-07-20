# 專案一：時空多代理人路徑規劃器 (Spatiotemporal MAPF Router)

## 專案目標
實作一個基於 **Time-Expanded Graph** 的多代理人路徑規劃器，展示圖論演算法設計、4D（3D 空間 + 時間軸）搜尋空間建模，以及在毫秒級延遲內求解多代理人最優/次優路徑的能力。

## 問題定義
給定 N 個代理人（模擬無人機）的起點、終點與共享的網格/圖狀空間，求出一組使所有代理人皆能無碰撞（無節點衝突、無邊衝突/交換衝突）抵達終點的路徑集合，並在合理時間內完成計算。

## 驗證方式（無需硬體）
- 使用公開 MAPF benchmark 資料集（如 movingai.com 的 grid map + scenario 檔）作為標準測資，可直接比對已知最優解或其他求解器的結果。
- 自建隨機網格生成器，用於壓力測試與邊界案例（高密度代理人、窄通道死鎖情境）。
- 所有驗證皆為離線圖論計算，不涉及任何實體感測器或載具控制迴路。

## 技術棧
- 主要：C++20（效能導向）或 Python + Numba/Cython（原型優先，後續視需要重寫熱點）
- 測試框架：GoogleTest（C++）或 pytest（Python）
- 視覺化：matplotlib / Plotly 動畫（展示路徑與時間軸）

## 系統架構
```
┌─────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  Map Loader      │ --> │ Time-Expanded Graph   │ --> │  Path Planner   │
│ (grid/graph def) │     │  Builder              │     │ (CBS / HCA*)    │
└─────────────────┘     └──────────────────────┘     └────────────────┘
                                                              │
                                                              v
                                                     ┌────────────────┐
                                                     │ Conflict        │
                                                     │ Validator       │
                                                     └────────────────┘
                                                              │
                                                              v
                                                     ┌────────────────┐
                                                     │ Visualizer /    │
                                                     │ Benchmark Runner│
                                                     └────────────────┘
```

### 核心元件
1. **Map/Graph Loader**：解析 2D/3D 網格或自訂拓樸圖，支援靜態障礙物。
2. **Time-Expanded Graph Builder**：將空間圖 × 時間步展開為 4D 搜尋空間，處理節點/邊在不同時間點的可達性。
3. **單代理人求解器**：Space-Time A*，作為 CBS 的低階求解器。
4. **多代理人協調器**：實作 Conflict-Based Search (CBS)，高階以衝突樹（CT）分裂約束，低階重新規劃單一代理人路徑；備選/加碼實作 Windowed Hierarchical Cooperative A*（HCA*）做效能對比。
5. **Conflict Validator**：獨立於求解器之外，對輸出路徑做二次驗證（vertex conflict、edge/swap conflict、時間窗違規），作為「對抗式思維」的體現。
6. **Benchmark Runner**：批次跑 benchmark 資料集，輸出成功率、求解時間、路徑總長度等指標。

## 開發里程碑
| 里程碑 | 內容 | 驗收標準 |
|---|---|---|
| M0 | 專案骨架、CI、測試框架建置 | `pytest`/`ctest` 可跑通空測試 |
| M1 | 網格載入 + 單代理人 Space-Time A* | 單代理人在含時間維度的網格上找到最短路徑 |
| M2 | Time-Expanded Graph 建構 + 衝突偵測 | 給定兩條路徑可正確偵測 vertex/edge conflict |
| M3 | CBS 多代理人求解器 | 在 20+ 代理人的小型 benchmark 上求得無衝突解 |
| M4 | 效能優化（記憶體/延遲） | 中型 benchmark（50-100 agents）求解時間降至數十毫秒等級，記錄優化前後對比數據 |
| M5 | 視覺化 + README + Demo | 產出路徑動畫、效能報告，README 含可重現的執行步驟 |

## 非目標（Non-goals）
- 不涉及真實無人機通訊協定、感測器融合或飛控整合。
- 不處理動態即時避障（該部分屬於專案三的斷言引擎/即時系統範疇）。

## Repo 結構建議
```
mapf-router/
├── README.md
├── src/
│   ├── graph/          # 空間圖與 Time-Expanded Graph
│   ├── planner/        # Space-Time A*, CBS, HCA*
│   └── validator/       # 衝突驗證器
├── benchmarks/          # movingai.com 格式測資 + 自製壓力測試
├── tests/
└── viz/                 # 視覺化腳本
```
