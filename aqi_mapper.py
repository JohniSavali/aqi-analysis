#!/usr/bin/env python3
"""
台灣即時 AQI 數據地圖顯示程式
串接環境部 API 獲取全台測站 AQI 數據並使用 Folium 在地圖上顯示
"""

import os
import requests
import folium
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json
import geopy
from geopy.distance import geodesic
import csv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv()

class AQIMapper:
    def __init__(self):
        self.api_key = os.getenv('AQI_API_KEY')
        if not self.api_key:
            raise ValueError("請在 .env 檔案中設定 AQI_API_KEY")
        
        self.api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432?language=zh&offset=0&limit=1000"
        self.data = None
        self.taipei_station = (25.0478, 121.5170)  # 台北車站座標
        
    def fetch_aqi_data(self):
        """獲取環境部 AQI API 數據"""
        print("正在獲取 AQI 數據...")
        
        params = {
            'api_key': self.api_key,
            'format': 'json'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            # API 回應是直接陣列，不是包含 records 的物件
            if isinstance(data, list):
                self.data = data
            elif 'records' in data:
                self.data = data['records']
            else:
                raise ValueError("API 回應格式錯誤")
            print(f"成功獲取 {len(self.data)} 個測站數據")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON 解析失敗: {e}")
            return False
        except Exception as e:
            print(f"獲取數據時發生錯誤: {e}")
            return False
    
    def calculate_distance_to_taipei(self, lat, lon):
        """計算測站到台北車站的距離（公里）"""
        try:
            station_coords = (float(lat), float(lon))
            distance = geodesic(station_coords, self.taipei_station).kilometers
            return round(distance, 2)
        except (ValueError, TypeError):
            return None
    
    def get_aqi_color(self, aqi_value):
        """根據 AQI 數值回傳對應顏色（三色系統）"""
        try:
            aqi = float(aqi_value)
        except (ValueError, TypeError):
            return 'gray'
        
        if aqi <= 50:
            return 'green'
        elif aqi <= 100:
            return 'yellow'
        else:
            return 'red'
    
    def get_aqi_level(self, aqi_value):
        """根據 AQI 數值回傳等級描述"""
        try:
            aqi = float(aqi_value)
        except (ValueError, TypeError):
            return '無數據'
        
        if aqi <= 50:
            return '良好'
        elif aqi <= 100:
            return '普通'
        elif aqi <= 150:
            return '對敏感族群不健康'
        elif aqi <= 200:
            return '對所有族群不健康'
        elif aqi <= 300:
            return '非常不健康'
        else:
            return '危害'
    
    def create_map(self):
        """建立 AQI 地圖"""
        if not self.data:
            print("沒有數據可顯示")
            return None
        
        print("正在建立地圖...")
        
        # 以台灣中心為起始點
        taiwan_map = folium.Map(
            location=[23.8, 120.9],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        valid_stations = 0
        
        for station in self.data:
            try:
                # 獲取座標
                lat = float(station.get('latitude', 0))
                lon = float(station.get('longitude', 0))
                
                # 驗證座標範圍（台灣範圍）
                if not (21.5 <= lat <= 25.5 and 119.5 <= lon <= 122.5):
                    continue
                
                # 獲取 AQI 數據
                aqi = station.get('aqi', 'N/A')
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', '未知地區')
                pm25 = station.get('pm2.5', 'N/A')
                pm10 = station.get('pm10', 'N/A')
                
                # 獲取顏色和等級
                color = self.get_aqi_color(aqi)
                level = self.get_aqi_level(aqi)
                
                # 建立簡化的彈出視窗內容
                popup_content = f"""
                <b>{site_name}</b><br>
                地區: {county}<br>
                <b>AQI: {aqi}</b><br>
                更新: {datetime.now().strftime('%m/%d %H:%M')}
                """
                
                # 建立標記
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_content, max_width=300),
                    color='black',
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=1
                ).add_to(taiwan_map)
                
                valid_stations += 1
                
            except (ValueError, TypeError, KeyError) as e:
                continue
        
        print(f"地圖上共顯示 {valid_stations} 個有效測站")
        
        # 加入簡化的圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 140px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>AQI 等級</h4>
        <i class="fa fa-circle" style="color:green"></i> 0-50 良好<br>
        <i class="fa fa-circle" style="color:yellow"></i> 51-100 普通<br>
        <i class="fa fa-circle" style="color:red"></i> 101+ 不健康<br>
        </div>
        '''
        
        taiwan_map.get_root().html.add_child(folium.Element(legend_html))
        
        return taiwan_map
    
    def export_to_csv(self, filename='outputs/aqi_analysis.csv'):
        """將 AQI 數據和距離計算結果匯出為 CSV"""
        if not self.data:
            print("沒有數據可匯出")
            return False
        
        print("正在匯出 CSV 檔案...")
        
        try:
            os.makedirs('outputs', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    '測站名稱', '縣市', 'AQI', '空氣品質等級', 'PM2.5', 'PM10',
                    '緯度', '經度', '距離台北車站(km)', '更新時間'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                valid_records = 0
                for station in self.data:
                    try:
                        lat = float(station.get('latitude', 0))
                        lon = float(station.get('longitude', 0))
                        
                        # 驗證座標範圍
                        if not (21.5 <= lat <= 25.5 and 119.5 <= lon <= 122.5):
                            continue
                        
                        # 計算距離
                        distance = self.calculate_distance_to_taipei(lat, lon)
                        
                        # 準備數據
                        aqi = station.get('aqi', 'N/A')
                        site_name = station.get('sitename', '未知測站')
                        county = station.get('county', '未知地區')
                        pm25 = station.get('pm2.5', 'N/A')
                        pm10 = station.get('pm10', 'N/A')
                        level = self.get_aqi_level(aqi)
                        
                        writer.writerow({
                            '測站名稱': site_name,
                            '縣市': county,
                            'AQI': aqi,
                            '空氣品質等級': level,
                            'PM2.5': pm25,
                            'PM10': pm10,
                            '緯度': lat,
                            '經度': lon,
                            '距離台北車站(km)': distance,
                            '更新時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        valid_records += 1
                        
                    except (ValueError, TypeError, KeyError):
                        continue
                
                print(f"CSV 檔案已匯出，共 {valid_records} 筆有效資料")
                print(f"檔案位置: {filename}")
                return True
                
        except Exception as e:
            print(f"匯出 CSV 失敗: {e}")
            return False
    
    def save_map(self, map_obj, filename='outputs/taiwan_aqi_map.html'):
        """儲存地圖檔案"""
        try:
            os.makedirs('outputs', exist_ok=True)
            map_obj.save(filename)
            print(f"地圖已儲存至: {filename}")
            return True
        except Exception as e:
            print(f"儲存地圖失敗: {e}")
            return False
    
    def run(self):
        """執行完整流程"""
        print("=" * 50)
        print("台灣即時 AQI 數據地圖產生器")
        print("=" * 50)
        
        # 獲取數據
        if not self.fetch_aqi_data():
            return False
        
        # 建立地圖
        aqi_map = self.create_map()
        if not aqi_map:
            return False
        
        # 儲存地圖
        if self.save_map(aqi_map):
            # 匯出 CSV
            if self.export_to_csv():
                print("\n地圖和 CSV 檔案產生完成！")
                print("地圖: outputs/taiwan_aqi_map.html")
                print("數據: outputs/aqi_analysis.csv")
                return True
            else:
                print("\n地圖產生完成，但 CSV 匯出失敗")
                return False
        return False

def main():
    """主程式"""
    try:
        mapper = AQIMapper()
        success = mapper.run()
        
        if success:
            print("\n程式執行成功！")
        else:
            print("\n程式執行失敗，請檢查錯誤訊息")
            
    except Exception as e:
        print(f"程式執行時發生錯誤: {e}")

if __name__ == "__main__":
    main()
