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
        # ดึงข้อมูล 1h และ 30m
        df_1h = yf.download("GC=F", interval="1h", period="15d", progress=False)
        df_30m = yf.download("GC=F", interval="30m", period="5d", progress=False)
        
        # คำนวณ 4H จาก 1H
        df_4h = df_1h['Close'].resample('4H').last().dropna().to_frame()
        
        data_configs = {
            "4H": df_4h,
            "1H": df_1h,
            "30M": df_30m
        }

        for label, df in data_configs.items():
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
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WARRIOR GOLD CLOUD</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
            .container { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }
            .box { width: 220px; padding: 25px; border-radius: 15px; margin: 10px; border: 2px solid #444; }
            .green { background: #004d00; box-shadow: 0 0 25px #2ecc71; }
            .red { background: #660000; box-shadow: 0 0 25px #e74c3c; }
            .gray { background: #333; }
            .btn-stop { background: #f39c12; border: none; padding: 18px 40px; color: white; 
                        border-radius: 8px; font-size: 20px; cursor: pointer; margin-top: 40px; }
        </style>
    </head>
    <body>
        <h1 style="color: #f1c40f; font-size: 40px;">WARRIOR GOLD CLOUD</h1>
        <div class="container">
            {% for tf, data in signals.items() %}
            <div class="box {{ data.color }}">
                <h2 style="font-size: 30px;">{{ tf }}</h2>
                <p style="font-size: 45px; font-weight: bold; margin: 10px 0;">{{ data.price }}</p>
            </div>
            {% endfor %}
        </div>
        <button class="btn-stop" id="stopBtn" onclick="stopAlarm()">STOP ALARM (MUTE)</button>
        <script>
            let alarmMuted = localStorage.getItem('alarmMuted') === 'true';
            if (alarmMuted) document.getElementById('stopBtn').innerText = "ALARM IS MUTED";
            function stopAlarm() {
                alarmMuted = !alarmMuted;
                localStorage.setItem('alarmMuted', alarmMuted);
                document.getElementById('stopBtn').innerText = alarmMuted ? "ALARM IS MUTED" : "STOP ALARM (MUTE)";
            }
            function playSound() {
                if (alarmMuted) return;
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.type = 'sine'; osc.frequency.setValueAtTime(660, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                osc.start(); osc.stop(audioCtx.currentTime + 1);
            }
            if ({{ 'true' if color_changed else 'false' }}) { playSound(); }
        </script
