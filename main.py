import pandas as pd
import yfinance as yf
import pandas_ta as ta
from flask import Flask, render_template_string
import os

app = Flask(__name__)

status_history = {"4H": None, "1H": None, "30M": None}

def get_signals():
    global status_history
    intervals = {"4H": "4h", "1H": "1h", "30M": "30m"}
    results = {}
    is_changed = False

    for label, tf in intervals.items():
        try:
            # ใช้ Ticker object เพื่อตั้งค่า Proxy หรือ Headers ได้ดีกว่าในอนาคต
            ticker = yf.Ticker("GC=F")
            # ดึงข้อมูลย้อนหลัง 5 วัน
            data = ticker.history(interval=tf, period="5d")
            
            if not data.empty:
                # คำนวณ EMA โดยใช้ pandas_ta
                ema12 = ta.ema(data['Close'], length=12)
                ema26 = ta.ema(data['Close'], length=26)
                
                current_close = float(data['Close'].iloc[-1])
                current_ema12 = float(ema12.iloc[-1])
                current_ema26 = float(ema26.iloc[-1])
                
                new_color = "green" if current_ema12 > current_ema26 else "red"
                
                if status_history[label] is not None and status_history[label] != new_color:
                    is_changed = True
                
                status_history[label] = new_color
                results[label] = {"price": round(current_close, 2), "color": new_color}
            else:
                results[label] = {"price": "No Data", "color": "gray"}
        except Exception as e:
            # แสดง Error สั้นๆ เพื่อให้เรารู้ว่าเกิดจากอะไร
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
            .box { width: 200px; padding: 20px; border-radius: 10px; margin: 10px; border: 2px solid #444; }
            .green { background: #006400; box-shadow: 0 0 20px #2ecc71; }
            .red { background: #8b0000; box-shadow: 0 0 20px #e74c3c; }
            .gray { background: #333; }
            .btn-stop { background: #f39c12; border: none; padding: 15px 30px; color: white; 
                        border-radius: 5px; font-size: 18px; cursor: pointer; margin-top: 30px; border-bottom: 4px solid #d35400; }
        </style>
    </head>
    <body>
        <h1 style="color: #f1c40f;">WARRIOR GOLD CLOUD</h1>
        <div class="container">
            {% for tf, data in signals.items() %}
            <div class="box {{ data.color }}">
                <h2>{{ tf }}</h2>
                <p style="font-size: 32px; font-weight: bold;">{{ data.price }}</p>
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
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(660, audioCtx.currentTime);
                gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
                oscillator.start();
                oscillator.stop(audioCtx.currentTime + 1);
            }

            if ({{ 'true' if color_changed else 'false' }}) {
                playSound();
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, signals=signals, color_changed=color_changed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
