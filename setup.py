#!/usr/bin/env python3
"""
自動環境安裝腳本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """執行命令並處理錯誤"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失敗:")
        print(f"錯誤訊息: {e.stderr}")
        return False

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要 Python 3.7 或更高版本")
        print(f"當前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def main():
    """主安裝流程"""
    print("=" * 60)
    print("台灣 AQI 地圖程式 - 自動環境安裝")
    print("=" * 60)
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    # 檢查 pip
    print("\n檢查 pip...")
    try:
        import pip
        print("✓ pip 已安裝")
    except ImportError:
        print("❌ pip 未安裝，請先安裝 pip")
        return False
    
    # 升级 pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升級 pip")
    
    # 安裝套件
    packages = [
        "requests==2.31.0",
        "folium==0.14.0", 
        "python-dotenv==1.0.0",
        "pandas==3.0.0",
        "geopy==2.4.1"
    ]
    
    for package in packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"安裝 {package}"):
            return False
    
    # 檢查 .env 檔案
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"\n⚠️  未找到 {env_file} 檔案")
        print("請建立 .env 檔案並設定 AQI_API_KEY")
        print("範例內容:")
        print("AQI_API_KEY=your_api_key_here")
        return False
    
    # 檢查 API Key 是否設定
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'AQI_API_KEY=' not in content or 'your_api_key_here' in content:
            print(f"\n⚠️  請在 {env_file} 檔案中設定正確的 AQI_API_KEY")
            print("您可以從環境部開放平台申請 API Key")
            return False
    
    print("\n" + "=" * 60)
    print("✅ 環境安裝完成！")
    print("=" * 60)
    print("\n現在可以執行以下命令啟動程式:")
    print("python aqi_mapper.py")
    print("\n程式會在 outputs 資料夾中產生地圖檔案")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n安裝過程中遇到問題，請檢查錯誤訊息")
        sys.exit(1)
