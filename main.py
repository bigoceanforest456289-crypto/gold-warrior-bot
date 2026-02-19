import pandas as pd
import yfinance as yf
import pandas_ta as ta
from flask import Flask, render_template_string
import os

app = Flask(__name__)
status_history = {"4H": None, "1H": None, "30M": None}

def get_signals():
    global status_history
    results = {}
    is_changed = False
    
    try:
        # ลดระยะเวลาดึงข้อมูลเหลือแค่ 8 วัน (พอสำหรับ EMA26 ใน 1H และ 4H)
        df_1h = yf.download("GC=F", interval="1h", period="8d", progress=False, timeout=10)
        df_30m = yf.download("GC=F", interval="30m", period="3d", progress=False, timeout=10)
        
        # คำนวณ 4H จาก 1H
        df_4h = df_1h['Close'].resample('4H').last().dropna().to_frame()
        
        data_map = {"4H": df_4h, "1H": df_1h, "30M": df_30m}

        for label, df in data_map.items():
            if len(df) >= 26:
                ema12 = ta.ema(df['Close'], length=12)
                ema26 = ta.ema(df['Close'], length=26)
                
                curr_close = float(df['Close'].iloc[-1])
                curr_color = "green" if ema12.iloc[-1] > ema26.iloc[-1] else "red"
                
                if status_history[label] and status_history[label] != curr_color:
                    is_changed = True
                
                status_history[label] = curr_color
                results[label] = {"price": round(curr_close, 1), "color": curr_color}
            else:
                results[label] = {"price": "Wait...", "color": "gray"}
    except:
        for label in ["4H", "1H", "30M"]:
            results[label] = {"price": "Retry...", "color": "gray"}
            
    return results, is_changed

@app.route('/')
def index():
    signals, color_changed = get_signals()
    # (ส่วน HTML ก๊อปปี้จากเวอร์ชันก่อนหน้ามาวางได้เลยครับ)
    html_content = """...""" # ใส่ HTML ชุดเดิมที่มีปุ่ม STOP ALARM
    return render_template_string(html_content, signals=signals, color_changed=color_changed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
