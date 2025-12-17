import requests
from bs4 import BeautifulSoup
from backend.utils.nlp import translate_text, translate_color, convert_currency, map_subcategory_to_category  # ✅ 新增 translate_color
from backend.utils.image_handler import (
    upgrade_image_url_to_high_quality,
    download_product_images
)
import re

def scrape_product_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if "https" not in url:
            url = url.lower()
            url = "https://www.grail.bz/disp/item/"+ url +"/"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch the webpage. Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, "html.parser")

        # 提取商品名稱和貨號
        title_section = soup.find("h1", class_="ttl-name")
        if not title_section:
            return {"error": "Product details not found on the page."}
        
        title = title_section.text.strip()
        title_translated = translate_text(title) if title else title  # 翻譯商品名稱
        product_code = title_section.find("span", class_="txt-code").text.strip("[]").lower()  # ✅ 統一轉換為小寫

        # 提取推薦圖片並篩選顏色圖片
        recommendation_images = []
        color_images = []
        color_urls = set()  # 用來過濾顏色圖片

        recommendation_section = soup.select("div.modal-detaillist img")  # 定位推薦圖片區塊

        for img_tag in recommendation_section:
            img_url = img_tag.get("src", "").strip()
            alt_text = img_tag.get("alt", "").strip()  # 提取顏色名稱
            if img_url:
                # 🔥 升級為高畫質 URL
                img_url = upgrade_image_url_to_high_quality(img_url)
                
                # 判斷是否為顏色圖片（`col_xx`）
                if "col" in img_url and alt_text:
                    # ✅ 使用新的 translate_color 函數（優先查找映射表）
                    color_name_translated = translate_color(alt_text)
                    color_data = {"color": color_name_translated, "image_url": img_url}
                    if img_url not in color_urls:
                        color_images.append(color_data)
                        color_urls.add(img_url)
                else:
                    # 如果不是顏色圖片，加入推薦列表
                    recommendation_images.append(img_url)

        # 從推薦圖片中移除已經加入顏色的圖片
        recommendation_images = [img for img in recommendation_images if img not in color_urls]

        # 提取商品詳細
        product_detail = ""
        material = ""

        detail_sections = soup.find_all("div", class_="tab-content")
        for section in detail_sections:
            header = section.find("h2", class_="contents-ttl only-pc")
            if header:
                header_text = header.get_text(strip=True)
                if "商品詳細" in header_text:
                    product_detail = section.get_text(strip=True)
                    product_detail = translate_text(product_detail) if product_detail else product_detail
                elif "サイズ・素材" in header_text:
                    material = section.get_text(strip=False)
                    material_match = re.search(r'☆素材は【.*?】', material)
                    if material_match:
                        material = material_match.group(0)
                        material = material.replace('\r', '').replace('\n', '').strip()
                        material = translate_text(material) if material else material
                    else:
                        material = None

        # 提取所有可選尺寸
        sizes = set()  # 使用 set 避免重複
        size_options = soup.select("select.size-select option")
        for option in size_options:
            size_text = option.text.strip().split("/")[0]  # 只取 S/M/L，不取庫存資訊
            if size_text:
                sizes.add(size_text)

        # 如果任一元素包含 "cm"，則認為是鞋子尺寸
        if any("cm" in s for s in sizes):
            size_order = ["22.0cm", "22.5cm", "23.0cm", "23.5cm", "24.0cm", "24.5cm", "25.0cm"]
            sizes = sorted(list(sizes), key=lambda x: size_order.index(x) if x in size_order else len(size_order))
        else:
            size_order = ["F", "XS", "S", "M", "L", "XL"]
            sizes = sorted(list(sizes), key=lambda x: size_order.index(x) if x in size_order else len(size_order))
       
        # 提取價格
        price_section = soup.find("p", class_="txt-price")
        if price_section:
            price_text = price_section.text.strip()
            match = re.search(r"¥\s?([\d,]+)", price_text)  # 更新正則，支持包含逗號的價格
            if match:
                price_jpy_str = match.group(1).replace(",", "")  # 移除千分位逗號
                price_jpy = int(price_jpy_str)  # 將清理後的價格轉為整數
                price_twd = convert_currency(price_jpy)  # ✅ 使用 utils/nlp.py 的函數轉換台幣
            else:
                print(f"Price text did not match regex: {price_text}")  # ✅ 調試用
                price_jpy = None
                price_twd = None
        else:
            print("Price section not found in the page")  # ✅ 調試用
            price_jpy = None
            price_twd = None

        # 提取分類
        breadcrumb_items = soup.select(".list-breadcrumb li a")
        if len(breadcrumb_items) >= 3:
            category = breadcrumb_items[1].text.strip()  # 主分類（第二個項目）
            subcategory = breadcrumb_items[2].text.strip()  # 次分類（第三個項目）
            subcategory = map_subcategory_to_category(category, subcategory, title)    # 使用 map_subcategory_to_category 修正子類別
            print(f"📌 爬取分類: {category} -> {subcategory}")
        elif len(breadcrumb_items) >= 2:
            category = breadcrumb_items[1].text.strip()  # 只有主分類
            subcategory = None
            print(f"📌 爬取分類: {category} -> None")
        if category == "浴衣":
            category = "ワンピース"
            subcategory = "浴衣"
            print(f"📌 調整分類: {category} -> {subcategory}")
        
        # 🔥 可選：下載商品圖片到本地（高畫質版本）
        # 取消下面的註解以啟用自動下載
        # download_result = download_product_images(product_code, color_images, save_to_backup=True)
        # print(f"📥 圖片下載結果: {download_result['downloaded']}/{download_result['total_colors']} 成功")
        
        # 組合返回結果
        return {
            "title": (title_translated+"（"+title+"）"),
            "product_code": product_code,
            "product_url": url,
            "colors": color_images,
            "colors_opt": [c["color"] for c in color_images],
            "recommendations": recommendation_images,
            "product_detail": product_detail,
            "material": material,
            "sizes": sizes, 
            "price_jpy": price_jpy,  # ✅ 日幣價格
            "price_twd": price_twd,  # ✅ 台幣價格
            # "url": url,
            "category": category,
            "subcategory": subcategory
        }
    except Exception as e:
        return {"error": str(e)}

# # # 測試程式
# url = "https://www.grail.bz/item/dk9881112/?s=2"  # 替換為實際商品網址
# product_data = scrape_product_page(url)
# print(product_data)
