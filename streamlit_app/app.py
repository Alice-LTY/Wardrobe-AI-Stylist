import streamlit as st
import pandas as pd
import sqlite3
import os
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

# --- Page Config ---
st.set_page_config(page_title="Wardrobe AI Stylist", page_icon="👗", layout="wide")

# --- Setup ---
# 自動尋找資料庫路徑 (假設在專案根目錄的 database 資料夾)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'wardrobe.db')

# --- Helper Functions ---
def load_wardrobe_data():
    """從 SQLite 讀取衣櫥資料"""
    if not os.path.exists(DB_PATH):
        st.error(f"找不到資料庫：{DB_PATH}。請確認你已執行過原專案的爬蟲。")
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    # JOIN products 表格以獲取商品標題
    query = """
    SELECT w.key, p.title, w.color_name, w.category, w.image_url, w.subcategory 
    FROM wardrobe w
    LEFT JOIN products p ON w.product_code = p.product_code
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        st.error(f"讀取資料庫失敗: {e}")
        return pd.DataFrame()

def get_ai_advice(prompt_text, wardrobe_df, api_key):
    """呼叫 Gemini API"""
    if not api_key:
        return "請先輸入 API Key"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 構建 Context (RAG)
    # 為了節省 token，我們只取前 50 件或隨機取樣，或根據關鍵字篩選
    # 這裡簡單示範：將資料轉為文字清單
    inventory_context = "我的衣櫥清單如下:\n"
    for idx, row in wardrobe_df.iterrows():
        inventory_context += f"- ID: {idx}, 名稱: {row['title']}, 顏色: {row['color_name']}, 類別: {row['category']}\n"
    
    full_prompt = f"""
    你是一位專業的個人穿搭造型師。
    {inventory_context}
    
    使用者的需求是："{prompt_text}"
    
    請從上述「我的衣櫥清單」中，挑選適合的單品組合成一套穿搭。
    請明確指出你要我穿哪一件（講出名稱和顏色），並說明為什麼這樣搭配適合這個場合。
    如果衣櫥裡沒有適合的，請直說。
    """
    
    with st.spinner("AI 造型師正在翻箱倒櫃..."):
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"AI 思考時發生錯誤: {e}"

# --- Main UI ---
st.title("👗 Wardrobe AI Stylist")
st.caption("Taica AIGC 期末專題 Demo | 基於 Wardrobe 全端系統延伸")

# Sidebar: Settings
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Key", type="password")
    st.info("本專題使用 RAG 技術，讀取 SQLite 資料庫並透過 LLM 生成建議。")
    st.markdown("---")
    st.markdown("原始專案: [Wardrobe](https://github.com/Alice-LTY/Wardrobe)")

# Load Data
df = load_wardrobe_data()

if df.empty:
    st.warning("目前衣櫥是空的，請先使用主程式加入一些衣服！")
else:
    # Top Section: Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("衣櫥總數", f"{len(df)} 件")
    col2.metric("包含類別", f"{len(df['category'].unique())} 種")
    
    st.markdown("---")

    # AI Interaction Section
    st.subheader("🤖 請問造型師")
    user_input = st.text_input("今天要去哪裡？心情如何？（例如：明天要去面試，想要正式一點但不要太老氣）")
    
    if st.button("生成穿搭建議", type="primary"):
        if not api_key:
            st.error("請輸入 API Key 才能呼叫 AI。")
        else:
            advice = get_ai_advice(user_input, df, api_key)
            st.markdown("### 💡 AI 建議")
            st.write(advice)
            
            # Bonus: 嘗試顯示 AI 提到的衣服圖片 (簡單關鍵字比對)
            st.markdown("#### 相關單品參考")
            img_cols = st.columns(4)
            col_idx = 0
            for idx, row in df.iterrows():
                # 如果 AI 的回答中有包含這件衣服的標題關鍵字 (這只是一個簡單的 demo logic)
                # 實際應用可以使用更強的 embedding search
                if row['title'][:5] in advice or row['color_name'] in advice: 
                    if col_idx < 4:
                        with img_cols[col_idx]:
                            st.image(row['image_url'], caption=row['title'])
                        col_idx += 1

    st.markdown("---")
    st.subheader("📦 目前衣櫥庫存 (Database View)")
    st.dataframe(df)
