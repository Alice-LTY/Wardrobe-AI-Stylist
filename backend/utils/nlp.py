from deep_translator import GoogleTranslator
import json
import os

JPY_TO_TWD_RATE = 0.23  # 1 JPY ≈ 0.23 TWD (可根據市場調整)

# 載入顏色映射表
COLOR_MAPPING = {}
COLOR_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "../../color_mapping.json")
try:
    if os.path.exists(COLOR_MAPPING_PATH):
        with open(COLOR_MAPPING_PATH, 'r', encoding='utf-8') as f:
            COLOR_MAPPING = json.load(f)
            # 反向映射：日文 -> 中文（從 key 提取日文部分）
            # 例如："黑色的（ブラック）" -> "ブラック": "黑色的"
            COLOR_MAPPING_JA_TO_ZH = {}
            for zh_ja_key in COLOR_MAPPING.keys():
                # 提取括號內的日文
                if "（" in zh_ja_key and "）" in zh_ja_key:
                    zh_part = zh_ja_key.split("（")[0]
                    ja_part = zh_ja_key.split("（")[1].split("）")[0]
                    COLOR_MAPPING_JA_TO_ZH[ja_part] = zh_part
            print(f"✅ 成功載入顏色映射表，共 {len(COLOR_MAPPING_JA_TO_ZH)} 個顏色")
    else:
        print(f"⚠️ 找不到顏色映射表: {COLOR_MAPPING_PATH}")
        COLOR_MAPPING_JA_TO_ZH = {}
except Exception as e:
    print(f"❌ 載入顏色映射表失敗: {e}")
    COLOR_MAPPING_JA_TO_ZH = {}

def convert_currency(amount, rate=JPY_TO_TWD_RATE):
    """
    將日圓 (JPY) 轉換為台幣 (TWD)。
    
    Args:
        amount (int/float): 以 JPY 計價的金額
        rate (float, optional): 匯率，默認使用 JPY_TO_TWD_RATE
    
    Returns:
        int: 四捨五入後的台幣價格
    """
    if amount is None:
        return None
    return round(amount * rate)

def translate_text(text, src='ja', dest='zh-TW'):
    """
    翻譯文字（使用 deep-translator，支援 Python 3.13）
    
    Args:
        text (str): 要翻譯的文字
        src (str): 來源語言（預設：'ja' 日文）
        dest (str): 目標語言（預設：'zh-TW' 繁體中文）
    
    Returns:
        str: 翻譯後的文字，失敗則返回原文
    """
    try:
        translator = GoogleTranslator(source=src, target=dest)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"翻譯失敗：{e}")
        return text  # 如果翻譯失敗，返回原始文字

def translate_color(color_ja):
    """
    翻譯顏色名稱（優先使用映射表，找不到才用 API）
    
    Args:
        color_ja (str): 日文顏色名稱
    
    Returns:
        str: 中文顏色名稱（格式：中文（日文））
    """
    if not color_ja:
        return color_ja
    
    # 1. 先嘗試從映射表查找
    if color_ja in COLOR_MAPPING_JA_TO_ZH:
        color_zh = COLOR_MAPPING_JA_TO_ZH[color_ja]
        result = f"{color_zh}（{color_ja}）"
        print(f"🎨 顏色映射: {color_ja} -> {result}")
        return result
    
    # 2. 映射表找不到，使用 API 翻譯
    print(f"⚠️ 顏色映射表中找不到 '{color_ja}'，使用 API 翻譯")
    color_zh = translate_text(color_ja)
    result = f"{color_zh}（{color_ja}）"
    return result
    
def map_subcategory_to_category(category, subcategory, title):
    """
    將子類別「其他」映射到對應的主類別 + 子類別
    """
    # category_mapping = {
    #     "トップス": "トップス_その他",
    #     "アウター": "アウター_その他",
    #     "ワンピース": "ワンピース_その他",
    #     "ボトムス": "ボトムス_その他",
    #     "シューズ": "シューズ_その他",
    #     "バッグ・カバン": "バッグ・カバン_その他",
    #     "アクセサリー": "アクセサリー_その他",
    #     "セットアイテム": "セットアイテム_その他",
    # }

    TopsSubcategory = [ 
    #   "すべて", # 全部
        "ニット", # 針織
        "シャツ・ブラウス", # 襯衫 & 襯衣
        "カットソー", # 縫製 T 恤
        "スウェット", # 運動衫
        "プリントTシャツ", # 印花 T 恤
        "Tシャツ[無地]", # 素色 T 恤
        "パーカー", # 帽 T
        "タンクトップ・キャミソール", # 背心和吊帶背心
        "ベスト", # 背心
        "トップスセット", # 上衣套裝
        "ベアトップ・チューブトップ", # 抹胸 & 管狀上衣
        "トップス_その他", # 其他
    #   "[セール}トップス" # 特價上衣  
    ]
    OuterwearSubcategory = [ # 外套
    #   "すべて", # 全部
        "ジャケット", # 夾克
        "カーディガン", # 羊毛衫
        "コート", # 大衣
        "アウターセット", # 外套套裝
        "アウター_その他", # 其他
    #   "[セール}アウター" # 特價外套
    ]
    DressesSubcategory = [ # 連衣裙
    #   "すべて", # 全部
        "柄", # 圖案
        "無地", # 素色
        "ニットワンピース", # 針織連衣裙
        "ロングワンピース", # 長款連衣裙
        "シャツワンピース", # 襯衫式連衣裙
        "キャミワンピース", # 吊帶連衣裙
        "オールインワン・サロペット", # 連身褲 & 背帶褲
        "ジャンパースカート", # 套頭背心裙
        "浴衣",
        "ワンピース_その他", # 其他
    #   "[セール}ワンピース" # 特價連衣裙
    ]
    BottomsSubcategory = [ # 下
    #   "すべて", # 全部
        "パンツ・デニム", # 褲子 & 牛仔褲
        "ショートパンツ", # 短褲
        "マーメイドスカート", #新增人魚裙分類
        "フレアスカート", #新增喇叭裙分類
        "ミニスカート", #新增迷你裙分類
        "スカート", # 裙子
        "ボトムスセット", # 下裝套裝
        "ボトムス_その他", # 其他
    #   "[セール}ボトムス" # 特價下裝
    ]
    ShoesSubcategory = [ # 鞋子
    #   "すべて", # 全部
        "パンプス", # 高跟鞋
        "サンダル", # 涼鞋
        "ショートブーツ・ブーティ", # 短靴
        "ロングブーツ", # 長靴
        "スニーカー", # 運動鞋
        "ローファー", # 樂福鞋
        "シューズ_その他", # 其他
    #   "[セール}シューズ" # 特價鞋子
    ]
    BagsSubcategory = [ # 包包
    #   "すべて", # 全部
        "ショルダーバッグ", # 肩背包
        "ハンドバッグ", # 手提包
        "リュック", # 背包
        "トートバッグ", # 托特包
        "クラッチバッグ", # 手拿包
        "かごバッグ", # 編織包
        "ポシェット", # 小肩包
        "バッグ・カバン_その他", # 其他
    #   "[セール}バッグ" # 特價包包
    ]
    AccessoriesSubcategory = [ # 配件
    #   "すべて", # 全部
        "ピアス・リング", # 耳環 & 戒指
        "ネックレス", # 項鍊
        "ベルト", # 腰帶
        "ブレス", # 手鐲
        "帽子", # 帽子
        "ヘッドアクセ", # 頭部配件
        "スカーフ", # 圍巾
        "ストール・マフラー", # 披肩 & 圍脖
        "レッグウェア", # 襪子
        "インナー", # 內搭
        "メガネ・サングラス", # 眼鏡 & 太陽鏡
        "時計", # 手錶
        "アクセサリー_その他", # 其他
    #   "[セール}アクセサリー" # 特價配件
    ]
    SetsSubcategory = [ # 套裝
    #   "すべて", # 全部
        "セットアップ", # 套裝
        "その他セット", # 其他套裝
        "セットアイテム_その他", # 居家服
    #   "[セール}セットアイテム" # 特價套裝
    ]
    category_mapping = {
        "トップス": TopsSubcategory,
        "アウター": OuterwearSubcategory,
        "ワンピース": DressesSubcategory,
        "ボトムス": BottomsSubcategory,
        "シューズ": ShoesSubcategory,
        "バッグ・カバン": BagsSubcategory,
        "アクセサリー": AccessoriesSubcategory,
        "セットアイテム": SetsSubcategory,
    }
    # # 如果子類別已經是正確的，不做修正
    # if subcategory in category_mapping.get(category, []):
    #     return subcategory
    # 如果子類別已在列表中，直接回傳，但針對下裝中「スカート」則不直接返回，
    # 以便進一步根據 title 進行更細部分類
    if category in category_mapping:
        if not (category == "ボトムス" and subcategory == "スカート"):
            if subcategory in category_mapping[category]:
                return subcategory

    keyword_mapping = {
    "トップス": {  # 上衣
        "ニット": ["ニット"],
        "シャツ・ブラウス": ["シャツ", "ブラウス"],
        "カットソー": ["カットソー"],
        "スウェット": ["スウェット"],
        "プリントTシャツ": ["プリントTシャツ", "プリント"],
        "Tシャツ[無地]": ["無地Tシャツ", "無地 Tシャツ"],
        "パーカー": ["パーカー"],
        "タンクトップ・キャミソール": ["タンクトップ", "キャミソール"],
        "ベスト": ["ベスト"],
        "トップスセット": ["セット"],
        "ベアトップ・チューブトップ": ["ベアトップ", "チューブトップ"]
        },
    "アウター": {  # 外套
        "ジャケット": ["ジャケット"],
        "カーディガン": ["カーディガン"],
        "コート": ["コート"],
        "アウターセット": ["セット"]
        },
    "ワンピース": {  # 連衣裙
        "柄": ["柄"],
        "無地": ["無地"],
        "ニットワンピース": ["ニットワンピース", "ニット ドレス"],
        "ロングワンピース": ["ロングワンピース", "ロングドレス"],
        "シャツワンピース": ["シャツワンピース", "シャツ ドレス"],
        "キャミワンピース": ["キャミワンピース", "キャミソール ドレス"],
        "オールインワン・サロペット": ["オールインワン", "サロペット"],
        "ジャンパースカート": ["ジャンパースカート"],
        "浴衣": ["浴衣"]
        },
    "ボトムス": {  # 下裝
        "マーメイドスカート": ["マーメイドスカート"],
        "フレアスカート": ["フレアスカート"],
        "ミニスカート": ["ミニスカート"],
        "パンツ・デニム": ["パンツ", "デニム"],
        "ショートパンツ": ["ショートパンツ"],
        "スカート": ["スカート"],
        "ボトムスセット": ["セット"]
        },
    "シューズ": {  # 鞋子
        "パンプス": ["パンプス"],
        "サンダル": ["サンダル"],
        "ショートブーツ・ブーティ": ["ショートブーツ", "ブーティ"],
        "ロングブーツ": ["ロングブーツ"],
        "スニーカー": ["スニーカー"],
        "ローファー": ["ローファー"]
        },
    "バッグ・カバン": {  # 包包
        "ショルダーバッグ": ["ショルダーバッグ"],
        "ハンドバッグ": ["ハンドバッグ"],
        "リュック": ["リュック"],
        "トートバッグ": ["トートバッグ"],
        "クラッチバッグ": ["クラッチバッグ"],
        "かごバッグ": ["かごバッグ"],
        "ポシェット": ["ポシェット"]
        },
    "アクセサリー": {  # 配件
        "ピアス・リング": ["ピアス", "リング"],
        "ネックレス": ["ネックレス"],
        "ベルト": ["ベルト"],
        "ブレス": ["ブレスレット"],
        "帽子": ["帽子"],
        "ヘッドアクセ": ["ヘッドアクセ"],
        "スカーフ": ["スカーフ"],
        "ストール・マフラー": ["ストール", "マフラー"],
        "レッグウェア": ["レッグウェア", "靴下"],
        "インナー": ["インナー"],
        "メガネ・サングラス": ["メガネ", "サングラス"],
        "時計": ["時計"]
        },
    "セットアイテム": {  # 套裝
        "セットアップ": ["セットアップ"],
        "その他セット": ["その他セット"],
        "セットアイテム_その他": ["ルームウェア", "パジャマ"]
    }
    }
    


    # ✅ 移除 `[セール}`
    subcategory = subcategory.replace("[セール}", "").strip()

    # ✅ 若 `subcategory == category`，嘗試從 `title` 重新分類
    # if subcategory == category or subcategory == "":
    if category in keyword_mapping:
        for subcat, keywords in keyword_mapping[category].items():
            if any(keyword in title for keyword in keywords):
                print(subcat)
                return subcat  # ✅ 找到匹配的關鍵字，返回對應子類別
    return category_mapping.get(category, "その他")  # ✅ 若找不到匹配，則歸類為 "其他"

    # return subcategory