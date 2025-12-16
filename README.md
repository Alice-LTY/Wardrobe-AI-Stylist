# 👗 Wardrobe AI Stylist: 基於 RAG 與多模態模型的智慧衣櫥助手

**課程名稱**：生成式 AI：文字與圖像生成的原理與實務 (Taica AIGC)  
**指導教授**：蔡炎龍 教授 (Prof. Yen-Lung Tsai)  
**參考專案**：[yenlung/AI-Demo](https://github.com/yenlung/AI-Demo)

---

## 1. Report 摘要 (Abstract)

**標題：結合檢索增強生成 (RAG) 與多模態大型語言模型之個人化穿搭顧問系統**

本專題「Wardrobe AI Stylist」旨在將傳統的 Full-Stack 衣櫥管理系統，延伸整合為具備生成式 AI 能力的智慧應用。原系統透過爬蟲構建了包含豐富後設資料（Metadata，如材質、顏色、版型）的 SQLite 資料庫，本研究以此為基礎，實作了「檢索增強生成 (Retrieval-Augmented Generation, RAG)」架構。

在深度學習模型部署方面，我們面臨了 Streamlit Community Cloud 等免費 PaaS 平台缺乏 GPU 算力，無法本地運行 LLaMA-3 或 Stable Diffusion 等大型模型的限制（Deploy Deep Learning on Streamlit GPU Issue）。為解決此問題，本專題採用「混合雲端推論 (Hybrid Cloud Inference)」策略：前端利用 Streamlit 構建輕量化互動介面，並直接讀取本地結構化資料庫；核心推論則透過 API 串接 **Google Gemini 1.5 Pro/Flash** 多模態模型。

本系統實現了兩大核心 AI 功能：
1.  **情境式穿搭生成 (Context-Aware Outfit Generation)**：AI 代理人 (Agent) 根據使用者輸入的自然語言（如「明天要去海邊婚禮」），檢索資料庫中真實擁有的衣物，生成符合場合的穿搭建議。
2.  **多模態購物決策 (Multimodal Shopping Assistant)**：結合 Vision Transformer 能力，使用者可針對願望清單中的商品圖片提問（如「這件裙子跟我衣櫥裡的哪件上衣最搭？」），系統會進行跨模態的視覺語義比對並提供建議。

本實作證明了在資源受限環境下，透過 API 代理與 RAG 技術，能有效賦予傳統資料庫應用具備高度客製化的生成式 AI 體驗。

---

## 2. Agent 開發過程對話紀錄

本專案開發過程採用 AI Agent (Gemini/ChatGPT) 作為技術顧問。以下為針對「深度學習模型部署」與「舊系統整合」的關鍵對話紀錄：

* **Phase 1: 整合策略 (Integration Strategy)**
    * **User**: 我有一個用 React+FastAPI 寫好的衣櫥 App，資料庫是 SQLite。我想做 Taica AIGC 的期末作業，要怎麼把 Deep Learning 加進去？
    * **Agent**: 既然你已經有完善的資料庫 (`wardrobe.db`)，做 **RAG (Retrieval-Augmented Generation)** 是最好的選擇。與其讓 AI 憑空畫圖，不如讓 AI 讀取你的 SQL 資料，變成一個「懂你衣櫥的穿搭顧問」。
    * **User**: 那我需要重寫前端嗎？React 寫起來比較慢。
    * **Agent**: 為了作業需求（Streamlit Demo），建議採用 **Sidecar 模式**。保留原本的 React App 不動，另外寫一個 `streamlit_app.py` 專門讀取同一個 SQLite 資料庫做 AI 展示。這樣既能繳交作業，又不用破壞原專案結構。

* **Phase 2: 解決 GPU 限制 (Addressing GPU Issue)**
    * **User**: 我想跑一個開源的時尚分類模型 (Fashion Clip)，但 Streamlit Cloud 只有 CPU，跑不動怎麼辦？
    * **Agent**: 這就是經典的 "Deploy Deep learning on streamlit GPU issue"。
        1.  **方案 A**: 量化模型 (Quantization)，但效果可能打折。
        2.  **方案 B (推薦)**: 使用 API Proxy。改用 **Google Gemini 1.5 Flash**，它是多模態模型，既能讀你資料庫的文字描述，也能直接看你爬蟲下來的圖片 (`image_url`)。
    * **User**: 這樣速度夠快嗎？
    * **Agent**: Gemini Flash 的 Latency 極低。我們會把資料庫查詢結果轉成 Text Prompt 丟給它，Streamlit 只要負責顯示圖片和文字，完全不消耗本地算力，完美解決 OOM 問題。

* **Phase 3: 功能延伸 (Extension)**
    * **User**: 我還想做「願望清單」的分析。
    * **Agent**: 可以做 **VQA (Visual Question Answering)**。使用者選一件想買的衣服（圖片），AI 自動掃描 `wardrobe` 資料表，分析：「你已經有 3 件類似的黑色寬褲了，建議不要買」或是「這件很適合搭你上次買的米色針織衫」。

---

## 3. GitHub 與 Streamlit App

* **GitHub Repository**: [Wardrobe AI Stylist](https://github.com/Alice-LTY/Wardrobe/tree/feature/ai-stylist)
* **Streamlit App Demo**: [Wardrobe AI Stylist Demo](https://wardrobe-ai-stylist.streamlit.app)

---

## 4. 系統架構與實作細節 (Technical Implementation)

本專題是基於一個完整 Full-Stack 專案 (**Wardrobe**) 的 AI 延伸實作。

### 核心技術堆疊
* **Frontend**: Streamlit (用於 AI 互動 Demo)
* **Backend Data**: SQLite (`wardrobe.db`, `wishlist.db`) - 由原 FastAPI 爬蟲系統建置
* **AI Engine**: Google Gemini 1.5 Pro/Flash (via API)
* **Technique**: RAG (Retrieval-Augmented Generation), Prompt Engineering

### 功能展示

#### 🤖 AI 穿搭顧問 (AI Stylist)
使用者輸入自然語言指令（例如：「今天下雨，氣溫 18 度，要去圖書館唸書」），系統執行以下流程：
1.  **Retrieve**: Python 腳本查詢 `wardrobe.db`，撈出所有「長袖」、「外套」、「長褲」類別的衣物。
2.  **Augment**: 將這些衣物的屬性（顏色、材質、圖片 URL）組合成結構化 Prompt。
3.  **Generate**: 呼叫 Gemini API，要求從候選清單中組合出一套最佳穿搭，並說明理由。
4.  **Display**: Streamlit 介面即時顯示推薦的衣物圖片與 AI 建議。

#### 🛍️ 購物決策輔助 (Shopping Assistant)
針對 `wishlist.db` 中的待購商品，AI 會進行跨資料庫分析：
* **重複性檢查**：分析是否已有極為相似的單品。
* **搭配性預測**：讀取商品圖片，建議衣櫥中現有的可搭配下身/上身。

### 如何執行 Demo (Installation)

若需在本地端執行此 AI Demo：

1.  **Clone 專案並切換分支**
    ```bash
    git clone https://github.com/Alice-LTY/Wardrobe.git
    cd Wardrobe
    git checkout feature/ai-stylist
    ```

2.  **安裝 Python 依賴**
    ```bash
    pip install -r streamlit_app/requirements.txt
    ```

3.  **設定 API Key**
    在 Streamlit secrets 中設定 `GOOGLE_API_KEY`，或使用環境變數。

4.  **啟動 Streamlit**
    ```bash
    streamlit run streamlit_app/app.py
    ```

---

> **Original Project: Wardrobe**  
> 本 AI Demo 之底層資料來自作者開發之全端專案 [Wardrobe](https://github.com/Alice-LTY/Wardrobe)，該系統具備 GRL 電商爬蟲、自動翻譯、顏色映射與前後端分離架構。本專題專注於該系統之「生成式 AI 應用延伸」。
