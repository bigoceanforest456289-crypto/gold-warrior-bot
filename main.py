import pandas as pd
import yfinance as yf
import pandas_ta as ta
from flask import Flask, render_template_string
import os
import time

app = Flask(__name__)

status_history = {"4H": None, "1H": None, "30M": None}

def get_data_with_retry(ticker_symbol, tf, retries=3):
    """ฟังก์ชันช่วยดึงข้อมูลแบบลองใหม่ถ้าพลาด"""
    for i in range(retries):
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(interval=tf, period="10d") # ขยาย period เป็น 10 วันเพื่อให้ชัวร์
            if not data.empty and len(data) >= 26: # ต้องมีข้อมูลพอคำนวณ EMA26
                return data
        except:
            time.sleep(1) # รอ 1 วินาทีก่อนลองใหม่
    return pd.DataFrame()

def get_signals():
    global status_history
    # ปรับ TF 4H ให้ดึงข้อมูลแบบ 1h มาจำลองหรือระบุให้ชัดเจนขึ้น
    intervals = {"4H": "90m", "1H": "60m", "30M": "30m"}
    results = {}
    is_changed = False

    for label, tf in intervals.items():
        # ถ้าเป็น 4H เราจะลองดึงแบบ '4h' ก่อน ถ้าไม่ได้จะใช้ '1h' มาช่วย
        actual_tf = "4h" if label == "4H" else tf
        data = get_data_with_retry("GC=F", actual_tf)
        
        if not data.empty:
            try:
                ema12 = ta.ema(data['Close'], length=12)
                ema26 = ta.ema(data['Close'], length=26)
                
                current_close = float(data['Close'].iloc[-1])
                current_ema12 = float(ema12.iloc[-1])
                current_ema26 = float(ema26.iloc[-1])
                
                new_color = "green" if current_ema12 > current_ema26 else "red"
                
                if status_history[label] is not None and status_history[label] != new_color:
                    is_changed = True
                
                status_history[label] = new_color
                results[label] = {"price": round(current_close, 1), "color": new_color}
            except:
                results[label] = {"price": "Retry...", "color": "gray"}
        else:
            results[label] = {"price": "Retry...", "color": "gray"}
            
    return results, is_changed

@app.route('/')
def index():
    signals, color_changed = get_signals()
    # (ส่วน HTML คงเดิมจากเวอร์ชันที่มีปุ่ม STOP ALARM)
    # ... [ก๊อปปี้ส่วน HTML จากโค้ดก่อนหน้ามาวางที่นี่] ...
