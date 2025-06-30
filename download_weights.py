#!/usr/bin/env python3
"""
YOLO权重文件下载脚本
自动下载所需的YOLO模型权重文件
"""

import os
import requests
import hashlib
from pathlib import Path
from tqdm import tqdm

# 权重文件配置
WEIGHTS_CONFIG = {
    'yolo11x-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-obb.pt',
        'description': 'YOLO11x-OBB 模型权重文件',
        'size': '113MB'
    },
    'yolo11n-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-obb.pt',
        'description': 'YOLO11n-OBB 模型权重文件（轻量版）',
        'size': '5.6MB'
    },
    'yolo11s-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s-obb.pt',
        'description': 'YOLO11s-OBB 模型权重文件（小型版）',
        'size': '19.8MB'
    },
    'yolo11m-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m-obb.pt',
        'description': 'YOLO11m-OBB 模型权重文件（中型版）',
        'size': '42.9MB'
    },
    'yolo11l-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11l-obb.pt',
        'description': 'YOLO11l-OBB 模型权重文件（大型版）',
        'size': '54.3MB'
    },
    'yolo11m-obb.pt': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m-obb.pt',
        'description': 'YOLO11m-OBB 模型权重文件（中型版）',
        'size': '42.9MB'
    }
}

def download_file(url, filename, description=""):
    """下载文件并显示进度条"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filename, 'wb') as file, tqdm(
            desc=f"下载 {description}",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))
        
        print(f"✅ {description} 下载完成")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 下载过程中出现错误: {e}")
        return False

def check_file_exists(filepath):
    """检查文件是否存在"""
    return os.path.exists(filepath)

def download_weights(model_name=None):
    """下载权重文件"""
    weights_dir = Path("weights")
    weights_dir.mkdir(exist_ok=True)
    
    if model_name:
        # 下载指定模型
        if model_name not in WEIGHTS_CONFIG:
            print(f"❌ 未知的模型名称: {model_name}")
            print(f"可用的模型: {', '.join(WEIGHTS_CONFIG.keys())}")
            return False
        
        config = WEIGHTS_CONFIG[model_name]
        filepath = weights_dir / model_name
        
        if check_file_exists(filepath):
            print(f"✅ {model_name} 已存在，跳过下载")
            return True
        
        print(f"📥 开始下载 {config['description']} ({config['size']})")
        return download_file(config['url'], filepath, config['description'])
    
    else:
        # 下载所有模型
        print("📥 开始下载所有YOLO权重文件...")
        success_count = 0
        
        for model_name, config in WEIGHTS_CONFIG.items():
            filepath = weights_dir / model_name
            
            if check_file_exists(filepath):
                print(f"✅ {model_name} 已存在，跳过下载")
                success_count += 1
                continue
            
            print(f"\n📥 下载 {config['description']} ({config['size']})")
            if download_file(config['url'], filepath, config['description']):
                success_count += 1
        
        print(f"\n🎉 下载完成! 成功下载 {success_count}/{len(WEIGHTS_CONFIG)} 个文件")
        return success_count == len(WEIGHTS_CONFIG)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YOLO权重文件下载工具")
    parser.add_argument(
        '--model', 
        choices=list(WEIGHTS_CONFIG.keys()),
        help="指定要下载的模型（不指定则下载所有模型）"
    )
    parser.add_argument(
        '--list', 
        action='store_true',
        help="列出所有可用的模型"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 可用的YOLO模型:")
        for model_name, config in WEIGHTS_CONFIG.items():
            print(f"  • {model_name}: {config['description']} ({config['size']})")
        return
    
    try:
        download_weights(args.model)
    except KeyboardInterrupt:
        print("\n❌ 下载被用户中断")
    except Exception as e:
        print(f"❌ 下载过程中出现错误: {e}")

if __name__ == "__main__":
    main() 