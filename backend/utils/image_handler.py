"""
圖片處理模組 - 優化 GRL 商品圖片處理
功能：
1. 將小像素圖片 URL 轉換為高畫質 URL
2. 下載圖片到本地快取
3. 支援圖片備份到雲端（Cloudinary/Imgur）
4. 為二手轉售準備高品質圖片
"""

import os
import requests
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import hashlib

# 圖片快取目錄（相對於專案根目錄）
IMAGE_CACHE_DIR = Path("images/cache")
IMAGE_BACKUP_DIR = Path("images/backup")


def ensure_image_directories():
    """確保圖片目錄存在"""
    IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ 圖片目錄已準備: {IMAGE_CACHE_DIR.absolute()}")


def upgrade_image_url_to_high_quality(img_url: str) -> str:
    """
    將 GRL 小像素圖片 URL 升級為高畫質 URL
    
    GRL 圖片 URL 格式分析：
    - 低畫質: https://cdn.grail.bz/images/goods/t/dk988/dk988_v1.jpg (/t/ 路徑)
    - 高畫質: https://cdn.grail.bz/images/goods/d/dk988/dk988_v1.jpg (/d/ 路徑)
    - 舊格式小圖: https://img.grail.bz/item/GRL-S3225/col_01_150x150.jpg
    - 舊格式中圖: https://img.grail.bz/item/GRL-S3225/col_01_300x300.jpg
    - 舊格式大圖: https://img.grail.bz/item/GRL-S3225/col_01.jpg (原圖)
    
    參數:
        img_url: 原始圖片 URL（可能是小像素）
    
    返回:
        高畫質圖片 URL
    """
    if not img_url:
        return img_url
    
    # 步驟 1: 將 /t/ 路徑替換為 /d/ 路徑（新版 CDN 格式）
    # 例如: /images/goods/t/dk988/ -> /images/goods/d/dk988/
    high_quality_url = img_url.replace('/images/goods/t/', '/images/goods/d/')
    
    # 步驟 2: 移除尺寸後綴（舊格式：_150x150, _300x300 等）
    # 匹配模式: _數字x數字.jpg
    high_quality_url = re.sub(r'_\d+x\d+(\.\w+)$', r'\1', high_quality_url)
    
    # 只在有變更時才顯示訊息
    if high_quality_url != img_url:
        print(f"🔄 圖片升級: {os.path.basename(img_url)} -> {os.path.basename(high_quality_url)}")
    
    return high_quality_url


def construct_image_url_from_product_code(
    product_code: str, 
    color_code: str = "01",
    high_quality: bool = True
) -> str:
    """
    根據商品代碼和顏色代碼構建圖片 URL
    即使商品頁面失效，仍能取得圖片（重要！為二手轉售準備）
    
    參數:
        product_code: 商品代碼 (例如: GRL-S3225)
        color_code: 顏色代碼 (01, 02, 03...)
        high_quality: 是否返回高畫質版本
    
    返回:
        圖片 URL
        
    範例:
        >>> construct_image_url_from_product_code("GRL-S3225", "01")
        'https://img.grail.bz/item/GRL-S3225/col_01.jpg'
    """
    base_url = "https://img.grail.bz/item"
    
    if high_quality:
        img_url = f"{base_url}/{product_code}/col_{color_code}.jpg"
    else:
        img_url = f"{base_url}/{product_code}/col_{color_code}_300x300.jpg"
    
    return img_url


def extract_color_code_from_url(img_url: str) -> Optional[str]:
    """
    從圖片 URL 中提取顏色代碼
    
    參數:
        img_url: 圖片 URL
    
    返回:
        顏色代碼 (例如: "01", "02") 或 None
        
    範例:
        >>> extract_color_code_from_url("https://img.grail.bz/item/GRL-S3225/col_01.jpg")
        '01'
    """
    match = re.search(r'col_(\d+)', img_url)
    return match.group(1) if match else None


def generate_image_filename(product_code: str, color: str, index: int = 1, extension: str = "jpg") -> str:
    """
    生成標準化的圖片檔名
    
    參數:
        product_code: 商品代碼
        color: 顏色名稱（中文或日文）
        index: 圖片序號
        extension: 檔案副檔名
    
    返回:
        檔名 (例如: GRL-S3225_black_01.jpg)
    """
    # 清理顏色名稱（移除括號和特殊字符）
    clean_color = re.sub(r'[（）\(\)]', '_', color).replace(' ', '_')
    filename = f"{product_code}_{clean_color}_{index:02d}.{extension}"
    return filename


def download_image(
    img_url: str,
    save_path: Path,
    force_download: bool = False
) -> Dict[str, any]:
    """
    下載圖片到本地
    
    參數:
        img_url: 圖片 URL
        save_path: 儲存路徑
        force_download: 是否強制重新下載（覆蓋已存在的檔案）
    
    返回:
        下載結果字典 {'success': bool, 'path': str, 'size': int, 'message': str}
    """
    # 如果檔案已存在且不強制下載，跳過
    if save_path.exists() and not force_download:
        file_size = save_path.stat().st_size
        return {
            "success": True,
            "path": str(save_path),
            "size": file_size,
            "message": f"圖片已存在，跳過下載 ({file_size / 1024:.1f} KB)"
        }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        response = requests.get(img_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 確保父目錄存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入檔案
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        file_size = save_path.stat().st_size
        
        return {
            "success": True,
            "path": str(save_path),
            "size": file_size,
            "message": f"✅ 下載成功 ({file_size / 1024:.1f} KB)"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "path": str(save_path),
            "size": 0,
            "message": f"❌ 下載失敗: {str(e)}"
        }


def download_product_images(
    product_code: str,
    color_images: List[Dict],
    save_to_backup: bool = True
) -> Dict[str, any]:
    """
    下載商品的所有顏色圖片（高畫質版本）
    
    參數:
        product_code: 商品代碼
        color_images: 顏色圖片列表 [{"color": "黑色", "image_url": "..."}]
        save_to_backup: 是否同時備份到 backup 目錄
    
    返回:
        下載結果字典
    """
    ensure_image_directories()
    
    results = {
        "product_code": product_code,
        "total_colors": len(color_images),
        "downloaded": 0,
        "failed": 0,
        "details": []
    }
    
    for idx, color_data in enumerate(color_images, 1):
        color_name = color_data.get("color", f"color_{idx}")
        img_url = color_data.get("image_url", "")
        
        # 升級為高畫質 URL
        hq_url = upgrade_image_url_to_high_quality(img_url)
        
        # 生成檔名
        filename = generate_image_filename(product_code, color_name, idx)
        
        # 下載到快取目錄
        cache_path = IMAGE_CACHE_DIR / product_code / filename
        result_cache = download_image(hq_url, cache_path)
        
        # 可選：備份到 backup 目錄
        if save_to_backup and result_cache["success"]:
            backup_path = IMAGE_BACKUP_DIR / product_code / filename
            result_backup = download_image(hq_url, backup_path, force_download=False)
        
        # 記錄結果
        results["details"].append({
            "color": color_name,
            "original_url": img_url,
            "high_quality_url": hq_url,
            "local_path": result_cache.get("path"),
            "success": result_cache["success"],
            "message": result_cache["message"]
        })
        
        if result_cache["success"]:
            results["downloaded"] += 1
        else:
            results["failed"] += 1
        
        print(result_cache["message"])
    
    return results


def get_local_image_path(product_code: str, color: str, index: int = 1) -> Optional[Path]:
    """
    獲取本地快取圖片路徑（如果存在）
    
    參數:
        product_code: 商品代碼
        color: 顏色名稱
        index: 圖片序號
    
    返回:
        本地圖片路徑（Path 物件）或 None
    """
    filename = generate_image_filename(product_code, color, index)
    cache_path = IMAGE_CACHE_DIR / product_code / filename
    
    return cache_path if cache_path.exists() else None


def cleanup_old_cache(days: int = 30) -> Dict[str, int]:
    """
    清理舊的快取圖片（可選功能）
    
    參數:
        days: 保留最近 N 天的圖片
    
    返回:
        清理統計 {'deleted_files': int, 'freed_space': int}
    """
    if not IMAGE_CACHE_DIR.exists():
        return {"deleted_files": 0, "freed_space": 0}
    
    now = datetime.now().timestamp()
    cutoff_time = now - (days * 24 * 60 * 60)
    
    deleted_count = 0
    freed_space = 0
    
    for img_file in IMAGE_CACHE_DIR.rglob("*.jpg"):
        if img_file.stat().st_mtime < cutoff_time:
            file_size = img_file.stat().st_size
            img_file.unlink()
            deleted_count += 1
            freed_space += file_size
            print(f"🗑️ 刪除舊快取: {img_file.name}")
    
    return {
        "deleted_files": deleted_count,
        "freed_space": freed_space
    }


# ========================================
# 雲端備份功能（Cloudinary/Imgur）
# ========================================

def upload_to_cloudinary(image_path: Path, product_code: str) -> Optional[str]:
    """
    上傳圖片到 Cloudinary（需安裝 cloudinary 套件）
    
    參數:
        image_path: 本地圖片路徑
        product_code: 商品代碼
    
    返回:
        雲端圖片 URL 或 None
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # 需要在 .env 設定 CLOUDINARY_* 環境變數
        result = cloudinary.uploader.upload(
            str(image_path),
            folder=f"wardrobe/{product_code}",
            use_filename=True
        )
        
        return result.get("secure_url")
        
    except ImportError:
        print("⚠️ 未安裝 cloudinary 套件，跳過雲端備份")
        return None
    except Exception as e:
        print(f"❌ Cloudinary 上傳失敗: {e}")
        return None


def upload_to_imgur(image_path: Path) -> Optional[str]:
    """
    上傳圖片到 Imgur（需要 Imgur API key）
    
    參數:
        image_path: 本地圖片路徑
    
    返回:
        Imgur 圖片 URL 或 None
    """
    IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    
    if not IMGUR_CLIENT_ID:
        print("⚠️ 未設定 IMGUR_CLIENT_ID，跳過 Imgur 上傳")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(
                "https://api.imgur.com/3/image",
                headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
                files={"image": f}
            )
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]["link"]
        else:
            print(f"❌ Imgur 上傳失敗: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Imgur 上傳錯誤: {e}")
        return None


# ========================================
# 測試與使用範例
# ========================================

if __name__ == "__main__":
    # 測試圖片 URL 升級
    test_url = "https://img.grail.bz/item/GRL-S3225/col_01_150x150.jpg"
    hq_url = upgrade_image_url_to_high_quality(test_url)
    print(f"原始: {test_url}")
    print(f"高畫質: {hq_url}")
    
    # 測試構建 URL
    url = construct_image_url_from_product_code("GRL-S3225", "01")
    print(f"構建 URL: {url}")
    
    # 測試下載（取消註解以實際測試）
    # ensure_image_directories()
    # test_path = IMAGE_CACHE_DIR / "test.jpg"
    # result = download_image(hq_url, test_path)
    # print(result)
