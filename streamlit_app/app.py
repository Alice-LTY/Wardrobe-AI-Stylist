import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
from google import genai
from datetime import datetime

# 添加父目錄到 path 以導入 backend 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Page Config ---
st.set_page_config(page_title="Wardrobe AI Stylist", page_icon="👗", layout="wide")

# --- Custom CSS (模仿 React App 配色) ---
st.markdown("""
<style>
    /* 全局樣式 */
    .main {
        background-color: #ffffff;
        font-family: "Roboto", sans-serif;
    }
    
    .block-container {
        max-width: 1600px;
        padding: 40px 60px;
    }
    
    /* 商品卡片樣式 */
    .product-card {
        background-color: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 20px;
        position: relative;
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
    
    .product-info {
        font-size: 12px;
        color: #484848;
        text-align: center;
        margin: 4px 0px;
    }
    
    .delete-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .delete-btn:hover {
        background-color: #ff4444;
        color: white;
    }
    
    /* 分類標籤 */
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
    
    /* AI 建議區塊 */
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
    
    h3 {
        color: #484848;
        font-size: 19px;
        margin: 19px 0px 9px;
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
    
    /* 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #484848;
        font-size: 16px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #c691a5;
        border-bottom-color: #c691a5;
    }
</style>
""", unsafe_allow_html=True)

# --- Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'wardrobe.db')

# 分類順序
CATEGORY_ORDER = [
    "トップス", "アウター", "ワンピース", "ボトムス", 
    "シューズ", "バッグ・カバン", "アクセサリー", "セットアイテム"
]

# --- Database Functions ---
def get_db_connection():
    """獲取資料庫連接"""
    return sqlite3.connect(DB_PATH)

def load_wardrobe_data(search_query="", category_filter=None):
    """從 SQLite 讀取衣櫥資料（支援搜尋和篩選）"""
    if not os.path.exists(DB_PATH):
        st.error(f"找不到資料庫：{DB_PATH}")
        return pd.DataFrame()
    
    conn = get_db_connection()
    query = """
    SELECT w.key, 
           COALESCE(p.title, SUBSTR(w.key, 1, INSTR(w.key, '_') - 1)) as title,
           w.color_name, w.category, w.subcategory, 
           w.size, w.image_url, w.price_twd, w.quantity, w.arrival_date
    FROM wardrobe w
    LEFT JOIN products p ON w.product_code = p.product_code
    WHERE 1=1
    """
    
    params = []
    if search_query:
        query += " AND (p.title LIKE ? OR w.color_name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    if category_filter and category_filter != "全部":
        query += " AND w.category = ?"
        params.append(category_filter)
    
    try:
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        st.error(f"讀取資料庫失敗: {e}")
        return pd.DataFrame()

def add_item_to_wardrobe(product_code, title, color_name, size, image_url, 
                         category, subcategory, quantity=1):
    """新增商品到衣櫥"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 生成 key
        key = f"{title}_{color_name}_{size}"
        
        # 檢查 product 是否存在
        cursor.execute("SELECT product_code FROM products WHERE product_code = ?", (product_code,))
        if not cursor.fetchone():
            # 新增到 products 表
            cursor.execute("""
                INSERT INTO products (product_code, title, product_url, category, subcategory)
                VALUES (?, ?, ?, ?, ?)
            """, (product_code, title, '', category, subcategory))
        
        # 新增到 wardrobe 表
        cursor.execute("""
            INSERT INTO wardrobe (key, product_code, product_url, color_name, size, 
                                 image_url, category, subcategory, quantity, arrival_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (key, product_code, '', color_name, size, image_url, 
              category, subcategory, quantity, datetime.now()))
        
        conn.commit()
        conn.close()
        return True, "✅ 成功新增商品！"
    except Exception as e:
        conn.close()
        return False, f"❌ 新增失敗：{str(e)}"

def delete_item_from_wardrobe(key):
    """從衣櫥刪除商品"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM wardrobe WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        st.error(f"刪除失敗：{str(e)}")
        return False

def update_item_quantity(key, new_quantity):
    """更新商品數量"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE wardrobe SET quantity = ? WHERE key = ?", (new_quantity, key))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        st.error(f"更新失敗：{str(e)}")
        return False

def get_ai_advice(prompt_text, wardrobe_df, api_key):
    """呼叫 Gemini API"""
    if not api_key:
        return "請先輸入 API Key"
    
    client = genai.Client(api_key=api_key)
    model = "gemini-1.5-flash"
    
    # 構建 Context (RAG)
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
            response = client.models.generate_content(
                model=model,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"AI 思考時發生錯誤: {e}"

# --- Main UI ---
st.title("👗 Wardrobe AI Stylist")
st.caption("Taica AIGC 期末專題 Demo | 基於 Wardrobe 全端系統延伸")

# Sidebar: Settings
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Gemini API Key", type="password", help="用於 AI 穿搭建議功能")
    
    st.markdown("---")
    st.subheader("🔍 搜尋與篩選")
    search_query = st.text_input("搜尋商品", placeholder="輸入名稱或顏色...")
    
    # 獲取所有分類
    df_all = load_wardrobe_data()
    if not df_all.empty:
        categories = ["全部"] + sorted(df_all['category'].unique().tolist())
        category_filter = st.selectbox("分類篩選", categories)
    else:
        category_filter = "全部"
    
    st.markdown("---")
    st.info("💡 本專題使用 RAG 技術，讀取 SQLite 資料庫並透過 LLM 生成建議。")
    st.markdown("📦 原始專案: [Wardrobe](https://github.com/Alice-LTY/Wardrobe)")

# 創建標籤頁
tab1, tab2, tab3 = st.tabs(["🏠 我的衣櫥", "➕ 新增商品", "🤖 AI 造型師"])

# === Tab 1: 我的衣櫥 ===
with tab1:
    # 載入資料
    df = load_wardrobe_data(search_query, None if category_filter == "全部" else category_filter)
    
    if df.empty:
        st.warning("🤷‍♀️ 目前衣櫥是空的！點選「新增商品」開始建立你的衣櫥。")
    else:
        # 統計資訊
        col1, col2, col3 = st.columns(3)
        col1.metric("衣櫥總數", f"{len(df)} 件")
        col2.metric("分類數", f"{df['category'].nunique()} 種")
        col3.metric("子分類數", f"{df['subcategory'].nunique()} 個")
        
        st.markdown("---")
        
        # 分類顯示
        all_categories = df['category'].unique()
        categories = [cat for cat in CATEGORY_ORDER if cat in all_categories]
        categories += [cat for cat in all_categories if cat not in CATEGORY_ORDER]
        
        for category in categories:
            # 分類標題
            st.markdown(f'<div class="category-badge">{category}</div>', unsafe_allow_html=True)
            category_items = df[df['category'] == category]
            
            # 按子分類分組
            subcategories = category_items['subcategory'].unique()
            for subcategory in subcategories:
                if subcategory and pd.notna(subcategory):
                    st.markdown(f'<h3 style="color: #484848; font-size: 19px; margin: 19px 0px 9px;">{subcategory}</h3>', unsafe_allow_html=True)
                
                subcategory_items = category_items[category_items['subcategory'] == subcategory]
                
                # 每行顯示 4 件商品
                cols = st.columns(4)
                for idx, (_, item) in enumerate(subcategory_items.iterrows()):
                    with cols[idx % 4]:
                        # 顯示商品圖片
                        st.image(item['image_url'], use_container_width=True)
                        
                        # 商品資訊
                        title = str(item['title']) if pd.notna(item['title']) else '未命名商品'
                        st.markdown(f"**{title[:40]}{'...' if len(title) > 40 else ''}**")
                        st.caption(f"🎨 {item['color_name']}")
                        st.caption(f"📏 {item['size']}")
                        if pd.notna(item['quantity']) and item['quantity'] > 1:
                            st.caption(f"📦 數量：{item['quantity']}")
                        
                        # 操作按鈕
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️", key=f"edit_{item['key']}", help="編輯", use_container_width=True):
                                st.session_state['editing_item'] = item.to_dict()
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️", key=f"del_{item['key']}", help="刪除", use_container_width=True):
                                if delete_item_from_wardrobe(item['key']):
                                    st.success("✅ 刪除成功！")
                                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

# === Tab 2: 新增商品 ===
with tab2:
    st.subheader("➕ 新增商品到衣櫥")
    
    # 選擇新增方式
    add_method = st.radio(
        "選擇新增方式",
        ["🔗 貼商品連結（爬蟲自動抓取）", "✍️ 手動輸入"],
        horizontal=True
    )
    
    if add_method == "🔗 貼商品連結（爬蟲自動抓取）":
        st.markdown("---")
        st.markdown("#### 🕷️ 從 GRL 網站抓取商品")
        
        # 商品 URL 輸入
        product_url = st.text_input(
            "商品連結或代碼",
            placeholder="例如：https://www.grail.bz/disp/item/tw1122/ 或直接輸入 tw1122",
            help="支援完整 URL 或只輸入商品代碼"
        )
        
        # 爬取按鈕
        if st.button("🔍 抓取商品資訊", type="primary", use_container_width=True):
            if not product_url:
                st.error("❌ 請輸入商品連結或代碼")
            else:
                with st.spinner("正在抓取商品資訊..."):
                    try:
                        # 導入爬蟲函數
                        from backend.utils.crawl import scrape_product_page
                        
                        # 執行爬蟲
                        product_data = scrape_product_page(product_url)
                        
                        if "error" in product_data:
                            st.error(f"❌ 爬取失敗：{product_data['error']}")
                        else:
                            # 將資料存入 session_state
                            st.session_state['scraped_product'] = product_data
                            st.success("✅ 成功抓取商品資訊！請選擇顏色和尺寸後加入衣櫥。")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ 爬取錯誤：{str(e)}")
        
        # 如果已經爬取到資料，顯示選擇介面
        if 'scraped_product' in st.session_state:
            product_data = st.session_state['scraped_product']
            
            st.markdown("---")
            st.markdown("#### 📦 商品資訊")
            
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                if product_data.get('colors') and len(product_data['colors']) > 0:
                    st.image(product_data['colors'][0]['image_url'], width=250)
            
            with col_info:
                st.markdown(f"**商品名稱**: {product_data.get('title', 'N/A')}")
                st.markdown(f"**商品代碼**: {product_data.get('product_code', 'N/A')}")
                st.markdown(f"**分類**: {product_data.get('category', 'N/A')} > {product_data.get('subcategory', 'N/A')}")
                if product_data.get('price_twd'):
                    st.markdown(f"**價格**: NT$ {product_data['price_twd']:,}")
            
            # 顏色和尺寸選擇
            st.markdown("#### 🎨 選擇顏色與尺寸")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_color = st.selectbox(
                    "顏色",
                    options=[c['color'] for c in product_data.get('colors', [])],
                    key="scraped_color"
                )
            
            with col2:
                selected_size = st.selectbox(
                    "尺寸",
                    options=list(product_data.get('sizes', [])),
                    key="scraped_size"
                )
            
            with col3:
                quantity = st.number_input("數量", min_value=1, value=1, key="scraped_qty")
            
            # 加入衣櫥按鈕
            if st.button("💾 加入衣櫥", type="primary", use_container_width=True):
                # 找到選擇的顏色圖片
                selected_color_data = next(
                    (c for c in product_data['colors'] if c['color'] == selected_color),
                    product_data['colors'][0]
                )
                
                success, message = add_item_to_wardrobe(
                    product_code=product_data['product_code'],
                    title=product_data['title'],
                    color_name=selected_color,
                    size=selected_size,
                    image_url=selected_color_data['image_url'],
                    category=product_data['category'],
                    subcategory=product_data.get('subcategory', ''),
                    quantity=quantity
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                    # 清除 session_state
                    del st.session_state['scraped_product']
                    st.rerun()
                else:
                    st.error(message)
    
    else:  # 手動輸入
        st.markdown("---")
        with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_code = st.text_input("商品代碼*", placeholder="例如：TW1122")
            title = st.text_input("商品名稱*", placeholder="例如：薄紗分層裙子")
            color_name = st.text_input("顏色*", placeholder="例如：黑色的（ブラック）")
            size = st.text_input("尺寸*", placeholder="例如：S")
        
        with col2:
            category = st.selectbox("分類*", CATEGORY_ORDER)
            subcategory = st.text_input("子分類", placeholder="例如：スカート")
            quantity = st.number_input("數量", min_value=1, value=1)
        
        image_url = st.text_input("圖片 URL*", placeholder="https://cdn.grail.bz/images/...")
        
            submitted = st.form_submit_button("💾 新增到衣櫥", use_container_width=True)
            
            if submitted:
                if not all([product_code, title, color_name, size, image_url]):
                    st.error("❌ 請填寫所有必填欄位（標記 * 者）")
                else:
                    success, message = add_item_to_wardrobe(
                        product_code, title, color_name, size, image_url,
                        category, subcategory, quantity
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)

# === Tab 3: AI 造型師 ===
with tab3:
    st.subheader("🤖 請問造型師")
    
    df_for_ai = load_wardrobe_data()
    
    if df_for_ai.empty:
        st.warning("衣櫥是空的，請先新增一些衣服！")
    else:
        user_input = st.text_area(
            "今天要去哪裡？心情如何？", 
            placeholder="例如：明天要去面試，想要正式一點但不要太老氣",
            height=100
        )
        
        if st.button("✨ 生成穿搭建議", type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ 請在側邊欄輸入 Gemini API Key")
            elif not user_input:
                st.error("❌ 請描述你的需求")
            else:
                advice = get_ai_advice(user_input, df_for_ai, api_key)
                
                st.markdown(f"""
                <div class="ai-advice-box">
                    <h3>💡 AI 穿搭建議</h3>
                    <p style="font-size: 14px; line-height: 1.6; color: #111111;">{advice}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 推薦單品
                st.markdown("#### 🎯 相關單品")
                img_cols = st.columns(4)
                col_idx = 0
                for idx, row in df_for_ai.iterrows():
                    if row['title'] and (row['title'][:5] in advice or row['color_name'] in advice):
                        if col_idx < 4:
                            with img_cols[col_idx]:
                                st.image(row['image_url'], use_container_width=True)
                                st.caption(f"**{row['title'][:30]}**")
                                st.caption(f"🎨 {row['color_name']}")
                            col_idx += 1
