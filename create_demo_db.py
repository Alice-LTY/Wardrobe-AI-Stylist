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

# 範例商品資料（使用真實圖片，價格 *5，涵蓋多種分類與子分類）
products_data = [
    # トップス - 針織
    ('DEMO1254', '喇叭袖針織頂與斗篷領帶', 1700, 1955, '時尚的喇叭袖針織上衣', '針織混紡', 'トップス', 'ニット', 'https://example.com/demo1254'),
    ('DEMO02', '肩部剪彩針織頂', 1800, 2070, '設計感肩部剪裁針織上衣', '針織', 'トップス', 'ニット', 'https://example.com/demo02'),
    ('DEMO1061', '高頸珍珠縫袖針織頂', 1100, 1265, '優雅的高領珍珠裝飾針織', '針織混紡', 'トップス', 'ニット', 'https://example.com/demo1061'),
    ('DEMO342', '顏色協調的荷葉邊敞開的肩部針織頂', 1300, 1495, '撞色荷葉邊針織上衣', '針織', 'トップス', 'ニット', 'https://example.com/demo342'),
    
    # トップス - 襯衫
    ('DEMO201', '基本款襯衫', 1400, 1610, '百搭白色襯衫', '棉質', 'トップス', 'シャツ・ブラウス', 'https://example.com/demo201'),
    ('DEMO202', '蕾絲襯衫', 1600, 1840, '優雅蕾絲襯衫', '棉混紡', 'トップス', 'シャツ・ブラウス', 'https://example.com/demo202'),
    
    # トップス - T恤
    ('DEMO301', '基本款T恤', 800, 920, '純色基本款', '棉質', 'トップス', 'カットソー', 'https://example.com/demo301'),
    
    # アウター - 夾克
    ('DEMO401', '牛仔夾克', 2200, 2530, '經典牛仔外套', '棉質', 'アウター', 'ジャケット', 'https://example.com/demo401'),
    ('DEMO402', '西裝外套', 2800, 3220, '正式西裝外套', '聚酯纖維', 'アウター', 'ジャケット', 'https://example.com/demo402'),
    
    # アウター - 大衣
    ('DEMO501', '長版大衣', 3500, 4025, '保暖長版大衣', '羊毛混紡', 'アウター', 'コート', 'https://example.com/demo501'),
    
    # ワンピース - 素色
    ('DEMO601', '基本款連身裙', 1800, 2070, '簡約連身裙', '棉質', 'ワンピース', '無地', 'https://example.com/demo601'),
    ('DEMO602', '針織連身裙', 2000, 2300, '舒適針織洋裝', '針織', 'ワンピース', '無地', 'https://example.com/demo602'),
    
    # ワンピース - 圖案
    ('DEMO701', '花卉連身裙', 1900, 2185, '浪漫花卉圖案', '雪紡', 'ワンピース', '柄', 'https://example.com/demo701'),
    
    # ワンピース - 背心裙
    ('DEMO801', '背心連身裙', 1700, 1955, '休閒背心裙', '棉質', 'ワンピース', 'ジャンパースカート', 'https://example.com/demo801'),
    
    # ボトムス - 裙子
    ('DEMO1122', '薄紗分層裙子', 1300, 1495, '優雅的分層設計薄紗裙', '聚酯纖維', 'ボトムス', 'スカート', 'https://example.com/demo1122'),
    ('DEMO071', '花薄紗側聚集的裙子', 1500, 1725, '浪漫花卉薄紗裙', '聚酯纖維', 'ボトムス', 'スカート', 'https://example.com/demo071'),
    
    # ボトムス - 人魚裙
    ('DEMO901', '人魚裙', 1600, 1840, '修身人魚裙', '針織', 'ボトムス', 'マーメイドスカート', 'https://example.com/demo901'),
    
    # ボトムス - 喇叭裙
    ('DEMO1001', '喇叭裙', 1400, 1610, '優雅喇叭裙', '聚酯纖維', 'ボトムス', 'フレアスカート', 'https://example.com/demo1001'),
    
    # ボトムス - 迷你裙
    ('DEMO1101', '迷你裙', 1200, 1380, '俏麗迷你裙', '棉質', 'ボトムス', 'ミニスカート', 'https://example.com/demo1101'),
    
    # ボトムス - 褲子
    ('DEMO1201', '直筒長褲', 1800, 2070, '修身直筒褲', '聚酯纖維', 'ボトムス', 'パンツ・デニム', 'https://example.com/demo1201'),
    
    # シューズ - 長靴
    ('DEMO1186', 'Ultra伸展厚實的腳跟長靴子', 2300, 2645, '舒適的伸展材質長靴', '合成皮革', 'シューズ', 'ロングブーツ', 'https://example.com/demo1186'),
    
    # シューズ - 樂福鞋
    ('DEMO1057', '珍珠皮帶皮革厚鞋底', 2000, 2300, '復古珍珠皮帶樂福鞋', '合成皮革', 'シューズ', 'ローファー', 'https://example.com/demo1057'),
    
    # アクセサリー - 腰帶
    ('DEMO1301', '編織腰帶', 600, 690, '時尚編織腰帶', '人造皮革', 'アクセサリー', 'ベルト', 'https://example.com/demo1301'),
]

# 衣櫥項目資料（使用真實的顏色圖片 URL）
wardrobe_data = [
    # トップス - 針織
    ('喇叭袖針織頂與斗篷領帶_黑色的（ブラック）_S', 'DEMO1254', 'https://example.com/demo1254', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/tu1254/tu1254_col_11.jpg', 1955, 'トップス', 'ニット', 1, '2024-02-01'),
    
    ('肩部剪彩針織頂_薰衣草（ラベンダー）_S', 'DEMO02', 'https://example.com/demo02', '薰衣草（ラベンダー）', 'S',
     'https://cdn.grail.bz/images/goods/d/lt02/lt02_col_39.jpg', 2070, 'トップス', 'ニット', 1, '2024-01-20'),
    
    ('高頸珍珠縫袖針織頂_黑色的（ブラック）_S', 'DEMO1061', 'https://example.com/demo1061', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/ru1061/ru1061_col_11.jpg', 1265, 'トップス', 'ニット', 1, '2024-02-15'),
    
    ('顏色協調的荷葉邊敞開的肩部針織頂_黑色的（ブラック）_S', 'DEMO342', 'https://example.com/demo342', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/dr342/dr342_col_11.jpg', 1495, 'トップス', 'ニット', 1, '2024-01-25'),
    
    # トップス - 襯衫
    ('基本款襯衫_白色（ホワイト）_M', 'DEMO201', 'https://example.com/demo201', '白色（ホワイト）', 'M',
     'https://cdn.grail.bz/images/goods/d/k9206d/k9206d_col_52.jpg', 1610, 'トップス', 'シャツ・ブラウス', 1, '2024-03-05'),
    
    ('蕾絲襯衫_米色（ベージュ）_S', 'DEMO202', 'https://example.com/demo202', '米色（ベージュ）', 'S',
     'https://cdn.grail.bz/images/goods/d/k9064b/k9064b_col_40.jpg', 1840, 'トップス', 'シャツ・ブラウス', 1, '2024-03-12'),
    
    # トップス - T恤
    ('基本款T恤_黑色的（ブラック）_M', 'DEMO301', 'https://example.com/demo301', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/dr679/dr679_col_59.jpg', 920, 'トップス', 'カットソー', 1, '2024-04-01'),
    
    # アウター - 夾克
    ('牛仔夾克_藍色（ブルー）_M', 'DEMO401', 'https://example.com/demo401', '藍色（ブルー）', 'M',
     'https://cdn.grail.bz/images/goods/d/ze749/ze749_col_56.jpg', 2530, 'アウター', 'ジャケット', 1, '2024-01-10'),
    
    ('西裝外套_黑色的（ブラック）_M', 'DEMO402', 'https://example.com/demo402', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/dr672a/dr672a_col_17.jpg', 3220, 'アウター', 'ジャケット', 1, '2024-02-05'),
    
    # アウター - 大衣
    ('長版大衣_駝色（キャメル）_L', 'DEMO501', 'https://example.com/demo501', '駝色（キャメル）', 'L',
     'https://cdn.grail.bz/images/goods/d/dr616a/dr616a_col_26.jpg', 4025, 'アウター', 'コート', 1, '2024-01-05'),
    
    # ワンピース - 素色
    ('基本款連身裙_黑色的（ブラック）_M', 'DEMO601', 'https://example.com/demo601', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/al94/al94_col_56.jpg', 2070, 'ワンピース', '無地', 1, '2024-02-20'),
    
    ('針織連身裙_米色（ベージュ）_S', 'DEMO602', 'https://example.com/demo602', '米色（ベージュ）', 'S',
     'https://cdn.grail.bz/images/goods/d/k9205z/k9205z_col_11.jpg', 2300, 'ワンピース', '無地', 1, '2024-03-15'),
    
    # ワンピース - 圖案
    ('花卉連身裙_花色（フラワー）_M', 'DEMO701', 'https://example.com/demo701', '花色（フラワー）', 'M',
     'https://cdn.grail.bz/images/goods/d/dk1292/dk1292_col_21.jpg', 2185, 'ワンピース', '柄', 1, '2024-04-10'),
    
    # ワンピース - 背心裙
    ('背心連身裙_黑色的（ブラック）_M', 'DEMO801', 'https://example.com/demo801', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/sm42/sm42_col_11.jpg', 1955, 'ワンピース', 'ジャンパースカート', 1, '2024-03-20'),
    
    # ボトムス - 裙子
    ('薄紗分層裙子_黑色的（ブラック）_S', 'DEMO1122', 'https://example.com/demo1122', '黑色的（ブラック）', 'S', 
     'https://cdn.grail.bz/images/goods/d/tw1122/tw1122_col_11.jpg', 1495, 'ボトムス', 'スカート', 1, '2024-01-15'),
    
    ('花薄紗側聚集的裙子_黑色的（ブラック）_S', 'DEMO071', 'https://example.com/demo071', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/ta071/ta071_col_11.jpg', 1725, 'ボトムス', 'スカート', 1, '2024-03-01'),
    
    # ボトムス - 人魚裙
    ('人魚裙_黑色的（ブラック）_M', 'DEMO901', 'https://example.com/demo901', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/dk1080/dk1080_col_28.jpg', 1840, 'ボトムス', 'マーメイドスカート', 1, '2024-02-25'),
    
    # ボトムス - 喇叭裙
    ('喇叭裙_米色（ベージュ）_S', 'DEMO1001', 'https://example.com/demo1001', '米色（ベージュ）', 'S',
     'https://cdn.grail.bz/images/goods/d/tu1082/tu1082_col_11.jpg', 1610, 'ボトムス', 'フレアスカート', 1, '2024-03-08'),
    
    # ボトムス - 迷你裙
    ('迷你裙_黑色的（ブラック）_S', 'DEMO1101', 'https://example.com/demo1101', '黑色的（ブラック）', 'S',
     'https://cdn.grail.bz/images/goods/d/gm728/gm728_col_11.jpg', 1380, 'ボトムス', 'ミニスカート', 1, '2024-04-05'),
    
    # ボトムス - 褲子
    ('直筒長褲_黑色的（ブラック）_M', 'DEMO1201', 'https://example.com/demo1201', '黑色的（ブラック）', 'M',
     'https://cdn.grail.bz/images/goods/d/ks003/ks003_col_21.jpg', 2070, 'ボトムス', 'パンツ・デニム', 1, '2024-02-10'),
    
    # シューズ - 長靴
    ('Ultra伸展厚實的腳跟長靴子_象牙（アイボリー）_23.0cm', 'DEMO1186', 'https://example.com/demo1186', '象牙（アイボリー）', '23.0cm',
     'https://cdn.grail.bz/images/goods/d/zr1186/zr1186_col_28.jpg', 2645, 'シューズ', 'ロングブーツ', 1, '2024-03-10'),
    
    # シューズ - 樂福鞋
    ('珍珠皮帶皮革厚鞋底_黑色的（ブラック）_23.0cm', 'DEMO1057', 'https://example.com/demo1057', '黑色的（ブラック）', '23.0cm',
     'https://cdn.grail.bz/images/goods/d/zr1057/zr1057_col_11.jpg', 2300, 'シューズ', 'ローファー', 1, '2024-02-20'),
    
    # アクセサリー - 腰帶
    ('編織腰帶_黑色的（ブラック）_Free', 'DEMO1301', 'https://example.com/demo1301', '黑色的（ブラック）', 'Free',
     'https://cdn.grail.bz/images/goods/d/tr98/tr98_col_19.jpg', 690, 'アクセサリー', 'ベルト', 1, '2024-04-15'),
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
