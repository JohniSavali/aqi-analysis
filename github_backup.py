#!/usr/bin/env python3
"""
GitHub 雲端備份腳本
使用 GitHub CLI 初始化倉庫並推送代碼到 GitHub
"""

import subprocess
import sys
import os

def run_command(command, description, check_result=True):
    """執行命令並處理錯誤"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=check_result, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        print(f"✓ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失敗:")
        if e.stderr:
            print(f"錯誤訊息: {e.stderr.strip()}")
        return False

def check_git_cli():
    """檢查 Git 和 GitHub CLI 是否安裝"""
    print("檢查必要工具...")
    
    # 檢查 Git
    try:
        subprocess.run("git --version", shell=True, check=True, capture_output=True)
        print("✓ Git 已安裝")
    except subprocess.CalledProcessError:
        print("❌ Git 未安裝，請先安裝 Git")
        return False
    
    # 檢查 GitHub CLI
    try:
        subprocess.run("gh --version", shell=True, check=True, capture_output=True)
        print("✓ GitHub CLI 已安裝")
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI 未安裝")
        print("請安裝 GitHub CLI: https://cli.github.com/")
        print("Windows: winget install GitHub.cli")
        print("或從 https://cli.github.com/ 下載安裝")
        return False
    
    return True

def check_github_auth():
    """檢查 GitHub 登入狀態"""
    print("\n檢查 GitHub 登入狀態...")
    
    try:
        result = subprocess.run("gh auth status", shell=True, check=True, capture_output=True, text=True)
        print("✓ 已登入 GitHub")
        return True
    except subprocess.CalledProcessError:
        print("❌ 未登入 GitHub")
        print("請先執行: gh auth login")
        return False

def initialize_git_repo():
    """初始化 Git 倉庫"""
    commands = [
        ("git init", "初始化 Git 倉庫"),
        ("git add .", "添加所有檔案到暫存區"),
        ("git commit -m \"Initial commit: AQI Analysis Project\"", "建立初始提交")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def create_github_repo():
    """在 GitHub 建立倉庫"""
    repo_name = "aqi-analysis"
    description = "台灣即時 AQI 數據分析與地圖顯示專案"
    
    cmd = f"gh repo create {repo_name} --public --description \"{description}\""
    return run_command(cmd, f"在 GitHub 建立倉庫 {repo_name}")

def push_to_github():
    """推送代碼到 GitHub"""
    commands = [
        ("git branch -M main", "設定主分支為 main"),
        ("git remote add origin https://github.com/$(gh api user --jq .login)/aqi-analysis.git", "添加遠端倉庫"),
        ("git push -u origin main", "推送代碼到 GitHub")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def main():
    """主備份流程"""
    print("=" * 60)
    print("GitHub 雲端備份 - AQI Analysis 專案")
    print("=" * 60)
    
    # 檢查工具
    if not check_git_cli():
        return False
    
    # 檢查登入狀態
    if not check_github_auth():
        print("\n請先登入 GitHub 後再執行此腳本")
        print("執行命令: gh auth login")
        return False
    
    # 檢查是否已在 Git 倉庫中
    if os.path.exists(".git"):
        print("\n⚠️  檢測到已存在 Git 倉庫")
        response = input("是否要重新初始化？(y/N): ").lower().strip()
        if response != 'y':
            print("跳過初始化，直接推送...")
        else:
            # 刪除現有 Git 倉庫
            if not run_command("rm -rf .git", "刪除現有 Git 倉庫"):
                return False
            # 初始化新的 Git 倉庫
            if not initialize_git_repo():
                return False
    else:
        # 初始化 Git 倉庫
        if not initialize_git_repo():
            return False
    
    # 建立 GitHub 倉庫
    if not create_github_repo():
        print("建立 GitHub 倉庫失敗，可能倉庫已存在")
        response = input("是否要繼續推送到現有倉庫？(y/N): ").lower().strip()
        if response != 'y':
            return False
    
    # 推送到 GitHub
    if not push_to_github():
        return False
    
    print("\n" + "=" * 60)
    print("✅ 雲端備份完成！")
    print("=" * 60)
    print("\n專案已成功推送到 GitHub:")
    print("https://github.com/[你的用戶名]/aqi-analysis")
    print("\n你可以在 GitHub 上查看和管理你的程式碼")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n備份過程中遇到問題，請檢查錯誤訊息")
        sys.exit(1)
