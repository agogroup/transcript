#!/usr/bin/env python3
"""
Whisper文字起こしツール - Web UI起動スクリプト
"""

import os
import sys

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Webアプリケーションのインポートと起動
from web.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Whisper文字起こしツール - Web UI")
    print("=" * 60)
    print("\nサーバーを起動しています...")
    print("アクセスURL: http://localhost:5000")
    print("\n終了するには Ctrl+C を押してください\n")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
