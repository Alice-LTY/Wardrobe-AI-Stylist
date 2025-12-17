# -*- coding: utf-8 -*-
"""
GRL 顏色編號對照表與模特照片 URL 生成器
自動生成於: 2025-11-24 10:04:54
注意：部分顏色可能有多個編號（列表格式）
"""

COLOR_CODE_MAPPING = {
    "沒有任何（なし）": "0",
    "黑色的（ブラック）": "11",
    "紅色的（レッド）": "13",
    "藍色的（ブルー）": "15",
    "粉色的（ピンク）": "17",
    "棕色的（ブラウン）": "19",
    "海軍（ネイビー）": "21",
    "灰色的（グレー）": "26",
    "象牙（アイボリー）": "28",
    "薰衣草（ラベンダー）": "39",
    "淺褐色的（ベージュ）": "40",
    "珍珠從白色（パールオフホワイト）": "50",
    "卡其色（カーキ）": "52",
    "木炭（チャコール）": "56",
    "米白色（オフホワイト）": "59",
    "米色（オフベージュ）": "91",
    "白色X黑色（オフホワイト×ブラック）": "138",
    "黑色X象牙（ブラック×アイボリー）": "157",
    "粉紅色X偏離白色（ピンク×オフホワイト）": "279",
    "薰衣草灰色（ラベンダーグレー）": "338",
    "摩卡（モカ）": "561",
    "淺灰色（ライトグレー）": "564",
    "格雷格（グレージュ）": "588",
    "12件套件（12点セット）": "983",
}

def get_color_code(color_name, index=0):
    """
    根據顏色名稱取得顏色編號
    
    Args:
        color_name: 顏色名稱（例如：黑色的（ブラック））
        index: 當顏色有多個編號時，指定要取得第幾個（預設為 0）
    
    Returns:
        str: 顏色編號（例如："11"），若找不到則返回 None
        若該顏色有多個編號，會根據 index 返回對應的編號
    """
    code = COLOR_CODE_MAPPING.get(color_name)
    if code is None:
        return None
    
    # 如果是列表，返回指定索引的編號
    if isinstance(code, list):
        if 0 <= index < len(code):
            return code[index]
        return code[0]  # 索引超出範圍則返回第一個
    
    return code

def get_all_color_codes(color_name):
    """
    取得顏色的所有編號
    
    Args:
        color_name: 顏色名稱
    
    Returns:
        list: 編號列表，若只有一個編號則返回單元素列表
    """
    code = COLOR_CODE_MAPPING.get(color_name)
    if code is None:
        return []
    
    if isinstance(code, list):
        return code
    
    return [code]

def get_color_image_url(product_code, color_name, quality="d", index=0):
    """
    根據產品代碼和顏色名稱生成圖片 URL
    
    Args:
        product_code: 產品代碼（例如："dk988"）
        color_name: 顏色名稱（例如："黑色的（ブラック）"）
        quality: 圖片品質 "d" (高畫質) 或 "t" (低畫質)，預設為 "d"
        index: 當顏色有多個編號時，指定使用第幾個（預設為 0）
    
    Returns:
        str: 圖片 URL，若顏色不存在則返回 None
    """
    color_code = get_color_code(color_name, index)
    if color_code:
        return f"https://cdn.grail.bz/images/goods/{quality}/{product_code}/{product_code}_col_{color_code}.jpg"
    return None

def get_all_color_image_urls(product_code, color_name, quality="d"):
    """
    取得顏色的所有可能圖片 URL（當有多個編號時）
    
    Args:
        product_code: 產品代碼
        color_name: 顏色名稱
        quality: 圖片品質
    
    Returns:
        list: 圖片 URL 列表
    """
    codes = get_all_color_codes(color_name)
    return [f"https://cdn.grail.bz/images/goods/{quality}/{product_code}/{product_code}_col_{code}.jpg" for code in codes]


# ==================== 模特試穿照片功能 ====================

def get_model_photo_url(product_code, v_number, quality="d"):
    """
    根據產品代碼和 v 編號生成模特試穿照片 URL
    
    Args:
        product_code: 產品代碼（例如："dk909"）
        v_number: 模特照片編號（例如：6）
        quality: 圖片品質 "d" (高畫質) 或 "t" (低畫質)，預設為 "d"
    
    Returns:
        str: 模特照片 URL
        
    Example:
        >>> get_model_photo_url("dk909", 6)
        'https://cdn.grail.bz/images/goods/d/dk909/dk909_v6.jpg'
    """
    return f"https://cdn.grail.bz/images/goods/{quality}/{product_code}/{product_code}_v{v_number}.jpg"


def get_all_model_photo_urls(product_code, v_min=1, v_max=11, quality="d"):
    """
    生成產品所有可能的模特試穿照片 URL
    
    根據資料庫分析，GRL 商品的模特照片編號範圍為 v1 ~ v11
    系統會生成所有可能的 URL，前端可以自動檢測哪些圖片實際存在
    
    分析結果：
    - 範圍：v1 ~ v11（涵蓋 100% 的照片）
    - 總樣本：1278 張模特照片
    - 分佈：非常均勻，每個編號約 10% 使用率
    
    Args:
        product_code: 產品代碼（例如："dk909"）
        v_min: 最小 v 編號（預設為 1）
        v_max: 最大 v 編號（預設為 11，基於實際分析結果）
        quality: 圖片品質 "d" (高畫質) 或 "t" (低畫質)
    
    Returns:
        list: 包含所有可能模特照片資訊的列表
        每個元素為 dict: {"v_number": int, "url": str}
        
    Example:
        >>> urls = get_all_model_photo_urls("dk909")
        >>> len(urls)
        11
        >>> urls[5]
        {'v_number': 6, 'url': 'https://cdn.grail.bz/images/goods/d/dk909/dk909_v6.jpg'}
    """
    return [
        {
            "v_number": v_num,
            "url": f"https://cdn.grail.bz/images/goods/{quality}/{product_code}/{product_code}_v{v_num}.jpg"
        }
        for v_num in range(v_min, v_max + 1)
    ]


def get_model_photo_urls_batch(product_code, v_numbers, quality="d"):
    """
    批量生成指定 v 編號的模特照片 URL
    
    Args:
        product_code: 產品代碼
        v_numbers: v 編號列表（例如：[1, 3, 5, 6, 10]）
        quality: 圖片品質
    
    Returns:
        list: 模特照片 URL 列表
        
    Example:
        >>> get_model_photo_urls_batch("dk909", [1, 6, 10])
        [
            {'v_number': 1, 'url': '...dk909_v1.jpg'},
            {'v_number': 6, 'url': '...dk909_v6.jpg'},
            {'v_number': 10, 'url': '...dk909_v10.jpg'}
        ]
    """
    return [
        {
            "v_number": v_num,
            "url": f"https://cdn.grail.bz/images/goods/{quality}/{product_code}/{product_code}_v{v_num}.jpg"
        }
        for v_num in v_numbers
    ]

