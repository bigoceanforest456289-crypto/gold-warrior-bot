import pandas as pd
import yfinance as yf
import pandas_ta as ta
from flask import Flask, render_template_string
import threading
import time

app = Flask(__name__)

# ตัวแปรเก็บสถานะล่าสุดเพื่อเช็คการเปลี่ยนสี
last_signals = {"4H": None, "1H": None, "30M": None}

def get_gold_signals():
    global last_signals
    intervals = {"4H": "4h", "1H": "1h", "30M": "30m"}
    results = {}
    changed = False

    for label, tf in intervals.items():
        data = yf.download("GC=F", interval=tf, period="5d", progress=False)
        if not data.empty:
            # ใช้ pandas_ta คำนวณ EMA 12, 26
            ema12 = ta.ema(data['Close'], length=12)
            ema26 = ta.ema(data['Close'], length=26)
            
            current_close = data['Close'].iloc[-1]
            current_ema12 = ema12.iloc[-1]
            current_ema26 = ema26.iloc[-1]
            
            # ตัดสินใจสี: เขียวถ้า EMA12 > EMA26
            color = "green" if current_ema12 > current_ema26 else "red"
            
            # เช็คว่าสีเปลี่ยนจากครั้งก่อนหรือไม่
            if last_signals[label] is not None and last_signals[label] != color:
                changed = True
            
            last_signals[label] = color
            results[label] = {
                "price": round(float(current_close), 2),
                "color": color,
                "time": data.index[-1].strftime('%H:%M')
            }
    return results, changed

@app.route('/')
def index():
    signals, is_changed = get_gold_signals()
    
    # HTML + CSS + JavaScript สำหรับเสียงเตือนและปุ่ม Stop
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WARRIOR GOLD CLOUD</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { background: #1a1a1a; color: white; font-family: Arial; text-align: center; padding-top: 50px; }
            .container { display: flex; justify-content: center; gap: 20px; }
            .box { width: 250px; padding: 20px; border-radius: 15px; border: 2px solid #555; }
            .green { background: #006400; }
            .red { background: #8b0000; }
            h1 { color: #ffd700; margin-bottom: 30px; }
            .btn-stop { 
                margin-top: 50px; padding: 15px 40px; font-size: 20px; 
                background: #ff4500; color: white; border: none; border-radius: 10px; cursor: pointer;
                box-shadow: 0 5px #999;
            }
            .btn-stop:active { transform: translateY(4px); box-shadow: 0 2px #666; }
        </style>
    </head>
    <body>
        <h1>GOLD WARRIOR SIGNAL (OREGON STATION)</h1>
        <div class="container">
            {% for tf, data in signals.items() %}
            <div class="box {{ data.color }}">
                <h2>{{ tf }}</h2>
                <p style="font-size: 30px; font-weight: bold;">{{ data.price }}</p>
                <p>Last Update: {{ data.time }}</p>
            </div>
            {% endfor %}
        </div>

        <button class="btn-stop" onclick="stopAlarm()">STOP ALARM (MUTE)</button>

        <script>
            // สร้างเสียง Beep
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            let isMuted = false;

            function playSound() {
                if (isMuted) return;
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // ความถี่เสียง
                gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
                oscillator.start();
                oscillator.stop(audioCtx.currentTime + 1); // ร้องนาน 1 วินาที
            }

            function stopAlarm() {
                isMuted = true;
                alert("Alarm Muted for this session.");
            }

            // ถ้ามีการเปลี่ยนสี (ค่าจาก Server) ให้ส่งเสียง
            if ({{ "true" if is_changed else "false" }}) {
                playSound();
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, signals=signals, is_changed=is_changed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
