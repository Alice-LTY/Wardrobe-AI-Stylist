"""
創建匿名化的範例資料庫供 Streamlit Demo 使用
使用真實商品圖片，但價格 *5 且不顯示品牌資訊
"""
import sqlite3
import os

# 創建 database 目錄
os.makedirs('database', exist_ok=True)

# 連接資料庫（會自動創建）
conn = sqlite3.connect('database/wardrobe.db')
cursor = conn.cursor()

# 創建 products 表格（與原系統一致）
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_code VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    price_jpy INTEGER,
    price_twd INTEGER,
    description VARCHAR,
    material VARCHAR,
    category VARCHAR NOT NULL,
    subcategory VARCHAR,
    product_url VARCHAR
)
''')

# 創建 wardrobe 表格（與原系統一致）
cursor.execute('''
CREATE TABLE IF NOT EXISTS wardrobe (
    "key" VARCHAR NOT NULL PRIMARY KEY,
    product_code VARCHAR NOT NULL,
    product_url VARCHAR NOT NULL,
    color_name VARCHAR NOT NULL,
    size VARCHAR NOT NULL,
    image_url VARCHAR NOT NULL,
    price_twd INTEGER,
    category VARCHAR NOT NULL,
    subcategory VARCHAR,
    quantity INTEGER,
    arrival_date DATETIME,
    FOREIGN KEY(product_code) REFERENCES products (product_code)
)
''')

# 範例商品資料（使用真實圖片，價格 *5）
products_data = [
    # (product_code, title, price_jpy, price_twd, description, material, category, subcategory, product_url)
    ('DEMO1122', '薄紗分層裙子', 1300, 1495, '優雅的分層設計薄紗裙', '聚酯纖維', 'ボトムス', 'スカート', 'https://example.com/demo1122'),
    ('DEMO1254', '喇叭袖針織頂與斗篷領帶', 1700, 1955, '時尚的喇叭袖針織上衣', '針織混紡', 'トップス', 'ニット', 'https://example.com/demo1254'),
    ('DEMO1186', 'Ultra伸展厚實的腳跟長靴子', 2300, 2645, '舒適的伸展材質長靴', '合成皮革', 'シューズ', 'ロングブーツ', 'https://example.com/demo1186'),
    ('DEMO02', '肩部剪彩針織頂', 1800, 2070, '設計感肩部剪裁針織上衣', '針織', 'トップス', 'ニット', 'https://example.com/demo02'),
    ('DEMO1061', '高頸珍珠縫袖針織頂', 1100, 1265, '優雅的高領珍珠裝飾針織', '針織混紡', 'トップス', 'ニット', 'https://example.com/demo1061'),
    ('DEMO071', '花薄紗側聚集的裙子', 1500, 1725, '浪漫花卉薄紗裙', '聚酯纖維', 'ボトムス', 'スカート', 'https://example.com/demo071'),
    ('DEMO342', '顏色協調的荷葉邊敞開的肩部針織頂', 1300, 1495, '撞色荷葉邊針織上衣', '針織', 'トップス', 'ニット', 'https://example.com/demo342'),
    ('DEMO1057', '珍珠皮帶皮革厚鞋底', 2000, 2300, '復古珍珠皮帶樂福鞋', '合成皮革', 'シューズ', 'ローファー', 'https://example.com/demo1057'),
]

# 衣櫥項目資料（使用真實的顏色圖片 URL）
wardrobe_data = [
    # (key, product_code, product_url, color_name, size, image_url, price_twd, category, subcategory, quantity, arrival_date)
    ('薄紗分層裙子_黑色的（ブラック）_S', 'DEMO1122', 'https://example.com/demo1122', '黑色的（ブラック）', 'S', 
     'https://cdn.grail.bz/images/goods/d/tw1122/tw1122_col_11.jpg', 1495, 'ボトムス', 'スカート', 1, '2024-01-15'),
    
    ('喇叭袖針織頂與斗篷領帶_黑色的（ブラック）_S', 'DEMO1254', 'https://example.com/demo1254', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/tu1254/tu1254_col_11.jpg', 1955, 'トップス', 'ニット', 1, '2024-02-01'),
    
    ('Ultra伸展厚實的腳跟長靴子_象牙（アイボリー）_23.0cm', 'DEMO1186', 'https://example.com/demo1186', '象牙（アイボリー）', '23.0cm',
     'https://cdn.grail.bz/images/goods/d/zr1186/zr1186_col_28.jpg', 2645, 'シューズ', 'ロングブーツ', 1, '2024-03-10'),
    
    ('肩部剪彩針織頂_薰衣草（ラベンダー）_S', 'DEMO02', 'https://example.com/demo02', '薰衣草（ラベンダー）', 'S',
     'https://cdn.grail.bz/images/goods/d/lt02/lt02_col_39.jpg', 2070, 'トップス', 'ニット', 1, '2024-01-20'),
    
    ('高頸珍珠縫袖針織頂_黑色的（ブラック）_S', 'DEMO1061', 'https://example.com/demo1061', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/ru1061/ru1061_col_11.jpg', 1265, 'トップス', 'ニット', 1, '2024-02-15'),
    
    ('花薄紗側聚集的裙子_黑色的（ブラック）_S', 'DEMO071', 'https://example.com/demo071', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/ta071/ta071_col_11.jpg', 1725, 'ボトムス', 'スカート', 1, '2024-03-01'),
    
    ('顏色協調的荷葉邊敞開的肩部針織頂_黑色的（ブラック）_S', 'DEMO342', 'https://example.com/demo342', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/dr342/dr342_col_11.jpg', 1495, 'トップス', 'ニット', 1, '2024-01-25'),
    
    ('珍珠皮帶皮革厚鞋底_黑色的（ブラック）_23.0cm', 'DEMO1057', 'https://example.com/demo1057', '黑色的（ブラック）', '23.0cm',
     'https://cdn.grail.bz/images/goods/d/zr1057/zr1057_col_11.jpg', 2300, 'シューズ', 'ローファー', 1, '2024-02-20'),
]

# 插入商品資料
cursor.executemany('''
    INSERT OR REPLACE INTO products 
    (product_code, title, price_jpy, price_twd, description, material, category, subcategory, product_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', products_data)

# 插入衣櫥資料
cursor.executemany('''
    INSERT OR REPLACE INTO wardrobe 
    ("key", product_code, product_url, color_name, size, image_url, price_twd, category, subcategory, quantity, arrival_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', wardrobe_data)

conn.commit()
print(f"✅ 已創建範例資料庫：database/wardrobe.db")
print(f"✅ 共插入 {len(products_data)} 件商品")
print(f"✅ 共插入 {len(wardrobe_data)} 筆衣櫥記錄")

# 驗證資料
cursor.execute("SELECT COUNT(*) FROM products")
products_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM wardrobe")
wardrobe_count = cursor.fetchone()[0]
print(f"✅ products 表: {products_count} 筆")
print(f"✅ wardrobe 表: {wardrobe_count} 筆")

conn.close()
