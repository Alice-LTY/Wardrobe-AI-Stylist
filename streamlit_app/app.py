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

# --- Custom CSS (模仿 React App 配色) ---
st.markdown("""
<style>
    /* 全局樣式 - 模仿 React App */
    .main {
        background-color: #ffffff;
        font-family: "Roboto", sans-serif;
    }
    
    .block-container {
        max-width: 1600px;
        padding: 40px 60px;
    }
    
    /* 商品卡片樣式 - 模仿 GRL 電商風格 */
    .product-card {
        background-color: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 20px;
        height: 100%;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px 0 rgba(0, 0, 0, 0.15);
    }
    
    .product-image {
        width: 100%;
        height: auto;
        object-fit: cover;
        transition: transform 0.3s ease;
        background-color: #f3f4f6;
    }
    
    .product-card:hover .product-image {
        transform: scale(1.05);
    }
    
    .product-title {
        font-size: 14px;
        font-weight: 400;
        color: #111111;
        margin: 9px 0px;
        text-align: center;
        padding: 0 10px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        line-height: 1.4;
    }
    
    .product-color {
        font-size: 12px;
        color: #484848;
        text-align: center;
        margin: 4px 0px 10px;
    }
    
    /* 分類標籤 - 使用 React App 粉紫色系 */
    .category-badge {
        background-color: transparent;
        color: #c691a5;
        padding: 8px 0px;
        border-radius: 0px;
        display: inline-block;
        font-weight: 400;
        font-size: 19px;
        margin: 39px 0px 19px;
        border-bottom: 2px solid #c691a5;
    }
    
    /* AI 建議區塊 - 使用粉紫色系 */
    .ai-advice-box {
        background-color: #f9f5f7;
        border-left: 4px solid #c691a5;
        padding: 25px;
        border-radius: 12px;
        color: #111111;
        margin: 20px 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .ai-advice-box h3 {
        color: #c691a5;
        margin-top: 0;
        font-size: 19px;
    }
    
    /* 標題樣式 */
    h1 {
        color: #000000;
        font-size: 29px;
        font-weight: 400;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 19px;
    }
    
    h2 {
        color: #c691a5;
        font-size: 14px;
        margin: 99px 0px 0px;
    }
    
    /* 統計卡片 */
    [data-testid="stMetricValue"] {
        font-size: 2em;
        color: #c691a5;
    }
    
    [data-testid="stMetricLabel"] {
        color: #484848;
        font-size: 14px;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background-color: #c691a5;
        color: white;
        border-radius: 9px;
        border: 2px solid #c195ac;
        padding: 9px 19px;
        font-size: 14px;
        transition: background-color 0.4s ease;
    }
    
    .stButton > button:hover {
        background-color: #a9738b;
        border-color: #a9738b;
    }
    
    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        border-radius: 19px;
        border: 2px solid #ccc;
        padding: 14px 19px;
        font-size: 14px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

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
    st.subheader("智慧衣櫥造型師")
    user_input = st.text_input("今天要去哪裡？心情如何？（例如：明天要去面試，想要正式一點但不要太老氣）")
    
    if st.button("✨ 生成穿搭建議", type="primary", use_container_width=True):
        if not api_key:
            st.error("請輸入 API Key 才能呼叫 AI。")
        else:
            advice = get_ai_advice(user_input, df, api_key)
            
            # AI 建議區塊
            st.markdown(f"""
            <div class="ai-advice-box">
                <h3>💡 AI 穿搭建議</h3>
                <p style="font-size: 14px; line-height: 1.6; color: #111111;">{advice}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Bonus: 嘗試顯示 AI 提到的衣服圖片 (簡單關鍵字比對)
            st.markdown("#### 推薦單品")
            img_cols = st.columns(4)
            col_idx = 0
            for idx, row in df.iterrows():
                # 如果 AI 的回答中有包含這件衣服的標題關鍵字 (這只是一個簡單的 demo logic)
                # 實際應用可以使用更強的 embedding search
                if row['title'][:5] in advice or row['color_name'] in advice: 
                    if col_idx < 4:
                        with img_cols[col_idx]:
                            card_html = f"""
                            <div class="product-card">
                                <img src="{row['image_url']}" class="product-image" alt="{row['title']}">
                                <div class="product-title">{row['title'][:30]}...</div>
                                <div class="product-color"> {row['color_name']}</div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                        col_idx += 1

    st.markdown("---")
    st.markdown("## 我的衣櫥")
    
    # 分類顯示
    categories = df['category'].unique()
    for category in categories:
        # 分類標題徽章
        st.markdown(f'<div class="category-badge">{category}</div>', unsafe_allow_html=True)
        category_items = df[df['category'] == category]
        
        # 每行顯示 4 件商品
        cols = st.columns(4)
        for idx, (_, item) in enumerate(category_items.iterrows()):
            with cols[idx % 4]:
                # 使用 HTML 創建卡片效果
                card_html = f"""
                <div class="product-card">
                    <img src="{item['image_url']}" class="product-image" alt="{item['title']}">
                    <div class="product-title">{item['title'][:30]}...</div>
                    <div class="product-color"> {item['color_name']}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
