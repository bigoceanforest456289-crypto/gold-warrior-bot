# ใช้ Python เวอร์ชันมาตรฐาน
FROM python:3.9-slim

# ตั้งค่าตำแหน่งทำงานในเครื่อง
WORKDIR /app

# ก๊อปปี้ไฟล์ใบสั่งของมาติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้โค้ดทั้งหมดลงไป
COPY . .

# สั่งให้บอททำงานผ่านพอร์ต 8080
CMD ["python", "main.py"]
