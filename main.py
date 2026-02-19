import yfinance as yf
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

SYMBOL = "PAXG-USD"

def get_data(interval):
    try:
        ticker = yf.Ticker(SYMBOL)
        df = ticker.history(period="2d", interval=interval)
        if not df.empty:
            open_p = df.iloc[-1]['Open']
            close_p = df.iloc[-1]['Close']
            color = "green" if close_p > open_p else "red"
            return {"open": round(open_p, 2), "close": round(close_p, 2), "color": color}
    except:
        return {"open": 0, "close": 0, "color": "gray"}
    return {"open": 0, "close": 0, "color": "gray"}

@app.route('/')
def dashboard():
    data_4h = get_data("4h")
    data_1h = get_data("1h")
    data_30m = get_data("30m")
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # หน้าเว็บแบบง่ายๆ ที่ดูบนมือถือได้สวย
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Warrior Gold Cloud</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background-color: #2c3e50; color: white; font-family: Arial; text-align: center; }}
            .container {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin-top: 20px; }}
            .box {{ width: 120px; padding: 20px; border-radius: 10px; font-weight: bold; }}
            .red {{ background-color: #e74c3c; }}
            .green {{ background-color: #2ecc71; }}
            .gray {{ background-color: #7f8c8d; }}
            .time {{ color: #f1c40f; margin-top: 30px; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <h1>WARRIOR GOLD CLOUD</h1>
        <div class="container">
            <div class="box {data_4h['color']}">4H<br>O: {data_4h['open']}<br>C: {data_4h['close']}</div>
            <div class="box {data_1h['color']}">1H<br>O: {data_1h['open']}<br>C: {data_1h['close']}</div>
            <div class="box {data_30m['color']}">30M<br>O: {data_30m['open']}<br>C: {data_30m['close']}</div>
        </div>
        <div class="time">Last Update: {now}</div>
        <p>Refreshing every 1 minute</p>
        <script>setTimeout(function(){{ location.reload(); }}, 60000);</script>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)