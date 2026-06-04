"""外卖管理系统 — 启动入口

运行:
    conda activate takeout
    python run.py

浏览器访问: http://127.0.0.1:5000
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
