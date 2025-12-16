"""
創建匿名化的範例資料庫供 Streamlit Demo 使用
"""
import sqlite3
import os

# 創建 database 目錄
os.makedirs('database', exist_ok=True)

# 連接資料庫（會自動創建）
conn = sqlite3.connect('database/wardrobe.db')
cursor = conn.cursor()

# 創建 wardrobe 表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS wardrobe (
    key TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    color_name TEXT,
    category TEXT,
    subcategory TEXT,
    size TEXT,
    image_url TEXT,
    price_twd REAL,
    material TEXT,
    product_code TEXT
)
''')

# 匿名化的範例資料（虛構品項，價格 *5，不提及品牌）
demo_items = [
    # 上衣
    ('top_001_beige_M', '簡約針織上衣', '米色', '上衣', '針織衫', 'M', 
     'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400', 995, '100% 純棉', 'DEMO001'),
    
    ('top_002_black_L', '高領毛衣', '黑色', '上衣', '毛衣', 'L',
     'https://images.unsplash.com/photo-1609873814058-a8928924184a?w=400', 1495, '羊毛混紡', 'DEMO002'),
    
    ('top_003_white_S', '襯衫式上衣', '白色', '上衣', '襯衫', 'S',
     'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400', 1195, '棉麻混紡', 'DEMO003'),
    
    ('top_004_navy_M', '條紋長袖T恤', '深藍色', '上衣', 'T恤', 'M',
     'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=400', 795, '純棉', 'DEMO004'),
    
    # 下身
    ('bottom_001_black_M', '高腰直筒長褲', '黑色', '下身', '長褲', 'M',
     'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?w=400', 1595, '聚酯纖維', 'DEMO005'),
    
    ('bottom_002_denim_L', '牛仔寬褲', '深藍色', '下身', '牛仔褲', 'L',
     'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400', 1895, '100% 棉', 'DEMO006'),
    
    ('bottom_003_beige_S', 'A字中長裙', '卡其色', '下身', '裙子', 'S',
     'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400', 1295, '棉麻混紡', 'DEMO007'),
    
    ('bottom_004_grey_M', '休閒運動褲', '灰色', '下身', '褲子', 'M',
     'https://images.unsplash.com/photo-1624378515195-6bbdb73dff1a?w=400', 995, '聚酯纖維', 'DEMO008'),
    
    # 外套
    ('outer_001_camel_L', '經典風衣外套', '駝色', '外套', '風衣', 'L',
     'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400', 3495, '聚酯纖維', 'DEMO009'),
    
    ('outer_002_black_M', '西裝外套', '黑色', '外套', '西裝外套', 'M',
     'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=400', 2995, '羊毛混紡', 'DEMO010'),
    
    ('outer_003_navy_L', '連帽休閒外套', '深藍色', '外套', '休閒外套', 'L',
     'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400', 1995, '棉質', 'DEMO011'),
    
    # 洋裝
    ('dress_001_floral_M', '碎花長洋裝', '花色', '洋裝', '長洋裝', 'M',
     'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400', 1895, '雪紡紗', 'DEMO012'),
    
    ('dress_002_black_S', '黑色小洋裝', '黑色', '洋裝', '短洋裝', 'S',
     'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400', 1695, '聚酯纖維', 'DEMO013'),
]

# 插入資料
cursor.executemany('''
    INSERT OR REPLACE INTO wardrobe 
    (key, title, color_name, category, subcategory, size, image_url, price_twd, material, product_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', demo_items)

conn.commit()
print(f"✅ 已創建範例資料庫：database/wardrobe.db")
print(f"✅ 共插入 {len(demo_items)} 件虛構商品")

# 驗證資料
cursor.execute("SELECT COUNT(*) FROM wardrobe")
count = cursor.fetchone()[0]
print(f"✅ 資料庫中共有 {count} 筆資料")

conn.close()
