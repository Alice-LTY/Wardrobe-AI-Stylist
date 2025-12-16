# 資料庫說明

## 隱私保護政策

出於個人隱私考量，實際的衣櫥與願望清單資料庫檔案 **未包含** 在此公開 repository 中。

原始專案包含：
- `wardrobe.db` - 個人擁有的衣物清單
- `wishlist.db` - 個人的購物願望清單

這些資料庫包含真實的購物記錄、品項資訊與個人偏好，不適合公開分享。

## Demo 資料說明

本專案的 Streamlit App 展示了 AI 功能的運作原理，但使用的是作者本地的真實資料庫。

## 如何測試本專案

若您想測試此 AI Stylist 功能，可以：

1. **使用原始專案建立資料庫**：參考 [Wardrobe 原始專案](https://github.com/Alice-LTY/Wardrobe) 中的爬蟲與資料庫架構
2. **創建自己的測試資料**：建立符合 schema 的 SQLite 資料庫
3. **修改 app.py**：調整資料庫連接路徑指向您的測試資料

## 資料庫 Schema 參考

詳細的資料表結構請參考原始專案的 `backend/models/` 目錄。
