import functions_framework
from datetime import datetime
import pytz

@functions_framework.http
def tradingview_handler(request):
    request_json = request.get_json(silent=True)
    
    # ใช้ Application Set 1 ของคุณ
    MY_APP_ID = "55801cdccbcfa4322a9a585996b74211"
    
    if request_json and request_json.get("app_set") == MY_APP_ID:
        symbol = request_json.get("symbol", "XAUUSD")
        tf = request_json.get("tf", "Unknown TF")
        status = request_json.get("status", "No Status")
        
        # ตั้งค่าเวลาเป็น Pacific Standard Time (PST) ตามที่ Office ใช้
        pst_timezone = pytz.timezone('America/Los_Angeles')
        current_time_pst = datetime.now(pst_timezone).strftime('%Y-%m-%d %H:%M:%S')
        
        emoji = "🟢" if status.lower() == "green" else "🔴"
        
        log_message = f"{emoji} [{current_time_pst} PST] {symbol} | TF: {tf} | Status: {status.upper()}"
        print(log_message)
        
        return f"Robot #3 Active: {log_message}", 200
    else:
        return "Unauthorized", 401
