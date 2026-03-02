# 台灣即時 AQI 數據地圖

這個程式可以串接環境部 API 獲取全台即時 AQI 數據，並使用 Folium 在地圖上標示所有測站位置。

## 功能特色

- 🌍 串接環境部 AQI API (aqx_p_432)
- 📍 在地圖上顯示全台測站位置
- 📏 計算各測站到台北車站的距離
- 📊 顯示詳細測站資訊（AQI、PM2.5、PM10）
- � 匯出 CSV 數據分析報表
- � 自動環境安裝腳本
- ☁️ GitHub 雲端備份功能

## 快速開始

### 1. 設定 API Key

在 `.env` 檔案中加入你的環境部 API Key：

```bash
AQI_API_KEY=your_api_key_here
```

> 💡 **如何取得 API Key？**
> 前往 [環境部開放平台](https://data.epa.gov.tw/) 申請 API Key

### 2. 自動安裝環境

執行自動安裝腳本：

```bash
python setup.py
```

### 3. 執行程式

```bash
python aqi_mapper.py
```

程式會產生以下輸出檔案：
- `outputs/taiwan_aqi_map.html` - 互動式 AQI 地圖
- `outputs/aqi_analysis.csv` - 完整數據分析報表（含距離計算）

### 4. 雲端備份（可選）

使用 GitHub CLI 將專案備份到 GitHub：

```bash
python github_backup.py
```

> 💡 **GitHub CLI 安裝**
> - Windows: `winget install GitHub.cli`
> - 或從 https://cli.github.com/ 下載安裝

## 手動安裝（可選）

如果想手動安裝依賴套件：

```bash
pip install -r requirements.txt
```

## 專案結構

```
python_project/
├── aqi_mapper.py       # 主程式
├── setup.py           # 自動安裝腳本
├── github_backup.py   # GitHub 備份腳本
├── requirements.txt    # 依賴套件列表
├── .env               # 環境變數檔案
├── .gitignore         # Git 忽略檔案
├── README.md          # 說明文件
├── data/              # 資料資料夾
└── outputs/           # 輸出資料夾
    ├── taiwan_aqi_map.html
    └── aqi_analysis.csv
```

## AQI 等級說明

| AQI 數值 | 等級 | 顏色 | 健康建議 |
|---------|------|------|----------|
| 0-50    | 良好 | 🟢 綠色 | 空氣品質令人滿意 |
| 51-100  | 普通 | 🟡 黃色 | 空氣品質可接受 |
| 101-150 | 對敏感族群不健康 | 🟠 橙色 | 敏感族群應減少戶外活動 |
| 151-200 | 對所有族群不健康 | 🔴 紅色 | 所有人應減少戶外活動 |
| 201-300 | 非常不健康 | 🟣 紫色 | 所有人應避免戶外活動 |
| 300+    | 危害 | 🔴 栗色 | 所有人應留在室內 |

## 故障排除

### 常見問題

1. **API Key 錯誤**
   - 檢查 `.env` 檔案中的 API Key 是否正確
   - 確認 API Key 仍有效且未超過使用限制

2. **網路連線問題**
   - 檢查網路連線是否正常
   - 確認防火牆未阻擋 API 請求

3. **套件安裝失敗**
   - 嘗試升級 pip：`python -m pip install --upgrade pip`
   - 使用管理員權限執行安裝

### 取得技術支援

如果遇到問題，請檢查：
1. Python 版本是否為 3.7+
2. 網路連線是否正常
3. API Key 是否正確設定

## 授權

本專案僅供學習和研究使用。
