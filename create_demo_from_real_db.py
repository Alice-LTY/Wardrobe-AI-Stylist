"""
從原始資料庫提取真實商品資料創建 Demo 資料庫
每個子分類最多選擇 4 件商品
確保分類、子分類、顏色、圖片都正確
"""
import sqlite3
import os

# 原始資料庫路徑
SOURCE_DB = '/Users/alice_li/Downloads/Wardrobe/database/wardrobe.db'
TARGET_DB = 'database/wardrobe.db'

# 創建 database 目錄
os.makedirs('database', exist_ok=True)

# 連接原始資料庫
print("📋 讀取原始資料庫...")
source_conn = sqlite3.connect(SOURCE_DB)
source_cursor = source_conn.cursor()

# 創建新的目標資料庫
if os.path.exists(TARGET_DB):
    os.remove(TARGET_DB)
    
target_conn = sqlite3.connect(TARGET_DB)
target_cursor = target_conn.cursor()

# 複製資料庫結構
print("🏗️  創建資料庫結構...")
source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for (sql,) in source_cursor.fetchall():
    if sql:
        target_cursor.execute(sql)

# 查詢所有分類與子分類
source_cursor.execute("SELECT DISTINCT category, subcategory FROM wardrobe ORDER BY category, subcategory")
categories = source_cursor.fetchall()

# 為每個子分類選擇最多 4 件商品
print("🎯 為每個子分類選擇最多 4 件商品...")
selected_product_codes = set()
selected_keys = []

for category, subcategory in categories:
    query = """
    SELECT w.key, w.product_code 
    FROM wardrobe w 
    WHERE w.category = ? AND w.subcategory = ? 
    LIMIT 4
    """
    source_cursor.execute(query, (category, subcategory))
    items = source_cursor.fetchall()
    for key, product_code in items:
        selected_keys.append(key)
        selected_product_codes.add(product_code)

# 複製選中的商品資料
print("📦 複製商品資料...")
for product_code in selected_product_codes:
    source_cursor.execute("SELECT * FROM products WHERE product_code = ?", (product_code,))
    row = source_cursor.fetchone()
    if row:
        # 調整價格 (* 5) - price_jpy 和 price_twd 分別是第 8 和第 9 個欄位
        row = list(row)
        if row[8]:  # price_jpy
            row[8] = int(row[8] * 5)
        if row[9]:  # price_twd
            row[9] = int(row[9] * 5)
        placeholders = ','.join(['?'] * len(row))
        target_cursor.execute(f"INSERT INTO products VALUES ({placeholders})", row)

# 複製選中的衣櫥資料
print(" 複製衣櫥資料...")
for key in selected_keys:
    source_cursor.execute("SELECT * FROM wardrobe WHERE key = ?", (key,))
    row = source_cursor.fetchone()
    if row:
        # 調整價格 (* 5)
        row = list(row)
        if row[6]:  # price_twd
            row[6] = int(row[6] * 5)
        placeholders = ','.join(['?'] * len(row))
        target_cursor.execute(f"INSERT INTO wardrobe VALUES ({placeholders})", row)

target_conn.commit()

# 統計資料
target_cursor.execute("SELECT COUNT(*) FROM products")
products_count = target_cursor.fetchone()[0]

target_cursor.execute("SELECT COUNT(*) FROM wardrobe")
wardrobe_count = target_cursor.fetchone()[0]

target_cursor.execute("SELECT DISTINCT category FROM wardrobe ORDER BY category")
categories = [row[0] for row in target_cursor.fetchall()]

target_cursor.execute("SELECT category, subcategory, COUNT(*) FROM wardrobe GROUP BY category, subcategory ORDER BY category")
subcategory_stats = target_cursor.fetchall()

print(f"\n✅ Demo 資料庫創建完成：database/wardrobe.db")
print(f"✅ Products 表: {products_count} 筆")
print(f"✅ Wardrobe 表: {wardrobe_count} 筆")
print(f"✅ 分類: {', '.join(categories)}")
print(f"\n📊 分類與子分類統計 (每個子分類最多 4 件):")
for cat, subcat, count in subcategory_stats:
    print(f"  {cat} > {subcat}: {count} 件")

source_conn.close()
target_conn.close()
