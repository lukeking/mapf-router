<!--
Sync Impact Report
==================
Version change: (template, unversioned) → 1.0.0
Bump rationale: MAJOR — initial ratification; all five principles newly defined.

Modified principles:
  [PRINCIPLE_1_NAME] → I. 對抗式驗證 (Adversarial Validation)
  [PRINCIPLE_2_NAME] → II. 效能以階梯衡量 (Performance as a Ladder)
  [PRINCIPLE_3_NAME] → III. 文獻可追溯且可理解 (Traceable AND Comprehensible)
  [PRINCIPLE_4_NAME] → IV. Benchmark 可重現 (Reproducible Benchmarks)
  [PRINCIPLE_5_NAME] → V. 證據等級制 (Evidence Tiers)

Added sections:
  [SECTION_2_NAME] → 技術棧與階段策略
  [SECTION_3_NAME] → 開發流程與品質門檻

Removed sections: none

Templates requiring updates:
  ✅ updated  .specify/templates/plan-template.md   — Constitution Check 已填入七項具體 gate；
                                                      Performance Goals 改為階梯表述
  ⚠ pending  .specify/templates/spec-template.md   — 效能需求須以階梯（L0–L4）表述；
                                                      待首個 feature 走 specify 時一併確認
  ⚠ pending  .specify/templates/tasks-template.md  — 需含 validator 獨立性檢查與
                                                      benchmark provenance 任務類型
  ✅ aligned  docs/decisions/001-tech-stack-evaluation.md

Deferred TODOs: none
-->

# MAPF Router Constitution

本專案為**能力建構導向**（非求職導向）：以無人機領域的職缺描述作為能力規格，
透過實作時空多代理人路徑規劃器取得該領域所要求的實力。本專案為該 JD 所涵蓋的
三個專案之一，各專案獨立開設 GitHub repo。

學習路徑為**從實作反推理論**：先做出可運作的系統，再回頭理解其背後的理論。
本憲章多處條款（原則 III 的白話橋接、視覺化驗收）皆為此路徑的支撐設施。

以下原則的存在目的，是確保「專案完成」與「能力真正長出來」兩者同時成立——
任何為了讓專案看起來完成而繞過學習的捷徑，都違反本憲章的根本意圖。

## Core Principles

### I. 對抗式驗證 (Adversarial Validation) — NON-NEGOTIABLE

Conflict Validator MUST 獨立於求解器之外實作：

- MUST 置於獨立模組（`src/validator/`），MUST NOT 匯入 `src/planner/` 的任何符號
- MUST NOT 與求解器共用衝突判定邏輯、約束表示法或路徑資料結構；驗證器
  自行從最原始的輸出（路徑序列）重新解讀語意
- 所有求解器輸出，在測試與 benchmark 中 MUST 通過驗證器
- CI MUST 以相依性檢查強制上述隔離

**理由**：求解器與驗證器共用假設時，兩者會一起錯而互相背書。獨立實作使得一個錯誤
必須同時在兩處以相同形式發生才能逃過偵測，這是本專案「對抗式思維」的具體載體。

### II. 效能以階梯衡量 (Performance as a Ladder)

效能 MUST 以「階數 + 場景」表述，MUST NOT 以裸露的毫秒數宣稱達標：

| 階 | 場景 | 速度 | 延遲預算 |
|---|---|---|---:|
| L0 | 室內倉儲、受限空間 | 1 m/s | 1000 ms |
| L1 | 室內低速巡檢 | 2 m/s | 500 ms |
| L2 | 室外低速 | 5 m/s | 200 ms |
| L3 | 室外巡航 | 10 m/s | 100 ms |
| L4 | 高速巡航 | 15 m/s | 67 ms |

- 延遲預算由 `網格邊長 ÷ 機隊速度` 推導（網格邊長 1 m）
- L0 為必須通過的底線；任何版本 MUST 聲明其已達階數
- 階梯參數（速度、網格邊長）為暫定值，MUST 於領域知識累積後修正，
  修正 MUST 走憲章修訂程序

**理由**：單一門檻是一堵牆，過不去就沒有中間狀態；對不熟悉的領域而言，這等於用一個
自己都不確定的數字把專案吊死。階梯讓入門門檻低到必過，同時強迫每個延遲數字綁定
真實場景，使優化工作成為可敘述的進展而非通過與否的二元判定。

### III. 文獻可追溯且可理解 (Traceable AND Comprehensible)

每個演算法模組 MUST 標註文獻來源，**且 MUST 附帶白話橋接說明**：

- MUST 於模組層級註解記錄論文出處與對應的虛擬碼圖表編號
- MUST 附白話說明，涵蓋：這個演算法在解決什麼問題、關鍵直覺是什麼、
  論文符號與本專案資料結構的對應關係
- 白話說明 MUST 足以讓未讀過該論文的人理解實作在做什麼；
  「請參閱原論文」MUST NOT 作為說明
- 實作與已發表虛擬碼的任何偏離 MUST 記錄偏離內容與理由
- 為效能而做的結構改寫 MUST 保留一份可對照的樸素版本供正確性交叉驗證

**理由**：本專案採「從實作反推理論」的學習路徑，**不預設實作者具備直接閱讀論文的
能力**。只有引用而無橋接的追溯，對學習者等於沒有追溯。橋接說明本身即是理論學習的
載體，也是日後互動式教學環節的素材來源。

### IV. Benchmark 可重現 (Reproducible Benchmarks)

Benchmark 結果 MUST 隨附完整來源資訊：

- MUST 記錄：資料集與版本、commit SHA、硬體規格、執行參數、亂數種子
- 所有隨機測資生成器 MUST 接受顯式種子參數
- 缺乏上述來源資訊的數據 MUST NOT 出現在報告或 README 中

**理由**：M4 的核心產出是優化前後的對比。不可重現的數字之間無法比較，
對比也就不成立。

### V. 證據等級制 (Evidence Tiers)

所有效能與能力宣稱 MUST 標註證據等級：

- **E1 實測** — 有本專案跑出的數據
- **E2 推論** — 有外部依據（文獻、社群共識、可類比經驗）
- **E3 判斷** — 主觀意見

- 任何 Gate 判定 MUST 僅接受 E1
- 技術決策文件中若關鍵準則僅有 E3，該文件 MUST 標記為暫定

**理由**：推論一旦未標註，會隨時間被當作既成事實累積，最終導致決策建立在
沒有人驗證過的假設上。

## 技術棧與階段策略

依 `docs/decisions/001-tech-stack-evaluation.md`，採**分階段混合方案**：

- **階段一（Python）**：完成涵蓋 M0–M5 的完整專案
- **階段二（C++ 核心）**：核心求解器以 C++ 重寫，經 pybind11 綁定；
  Python 保留 orchestration、benchmark、視覺化與測試

強制條件：

- 階段一 MUST 完整且可展示後，階段二方得開始——確保階段二停擺時專案仍然完整
- 跨階段的公開 API MUST 保持穩定，使 benchmark harness、視覺化與測試在重寫後
  原封不動重用；這是階段二的效能對比得以成立的前提
- Numba 經評估未採用，理由記錄於決策文件 001；重新採用 MUST 走憲章修訂程序

## 開發流程與品質門檻

- 每個 feature MUST 走 SDD 流程：specify → clarify → plan → tasks → implement
- 演算法核心 MUST 測試先行；測試 MUST 先失敗再實作
- 每次 commit 前，求解器輸出 MUST 通過獨立驗證器（原則 I）
- **驗收輸出 SHOULD 包含視覺化佐證**（路徑動畫、衝突標示、搜尋樹展開過程），
  而非僅有 pass/fail。理由：視覺化是「從實作反推理論」的主要理解管道，
  對本專案而言屬於學習基礎設施，不是 M5 才處理的裝飾
- 理論教學環節與實作交付**刻意解耦**：教學產出不列入 feature 的驗收標準，
  亦 MUST NOT 因實作進度而被省略
- 重大技術決策 MUST 於 `docs/decisions/` 留下決策記錄，含重新評估的觸發條件
- 決策記錄一旦標記為「已關閉」，MUST NOT 在其觸發條件成立前重新提出

## Governance

本憲章的效力高於其他開發慣例。當任何實作、計畫或工具設定與本憲章衝突時，
以本憲章為準，或先修訂憲章再行動。

**修訂程序**：修訂 MUST 以文件形式提出，載明變更內容、理由與對既有產出的影響，
並更新本檔的 Sync Impact Report 與版本號。

**版本政策**（語意化版本）：

- **MAJOR** — 移除原則、或以不相容方式重新定義既有原則
- **MINOR** — 新增原則或章節、實質擴充既有指引
- **PATCH** — 釐清措辭、修正錯字等不改變語意的調整

**合規審查**：每個 feature 的 plan 階段 MUST 執行 Constitution Check；
違反原則的設計 MUST 在該處記錄理由，或改採合規做法。複雜度 MUST 有正當理由——
「之後可能會用到」不構成理由。

**Version**: 1.0.0 | **Ratified**: 2026-07-20 | **Last Amended**: 2026-07-20
