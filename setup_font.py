#!/usr/bin/env python3
"""
日本語フォントセットアップスクリプト（Windows/Mac/Linux対応）
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path


def download_font():
    """Noto Sans JPフォントをダウンロード"""
    print("=" * 60)
    print("日本語フォントセットアップ")
    print("=" * 60)
    print()

    # fontsディレクトリを作成
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)

    # システムフォントをチェック
    system_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "C:\\Windows\\Fonts\\msgothic.ttc",
        "C:\\Windows\\Fonts\\meiryo.ttc",
    ]

    for font_path in system_fonts:
        if os.path.exists(font_path):
            print(f"✓ システムに日本語フォントがインストールされています")
            print(f"  {font_path}")
            print()
            print("追加の設定は不要です。")
            return True

    # フォントをダウンロード
    print("Noto Sans JP フォントをダウンロードしています...")
    print()

    try:
        # Google Fonts APIからダウンロード
        url = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
        font_file = fonts_dir / "NotoSansJP-Regular.ttf"

        print(f"ダウンロード中: {url}")
        print("少々お待ちください...")

        urllib.request.urlretrieve(url, str(font_file))

        if font_file.exists() and font_file.stat().st_size > 0:
            print()
            print(f"✓ フォントをインストールしました: {font_file}")
            print()
            print("=" * 60)
            print("セットアップ完了！")
            print("=" * 60)
            print()
            print("Webアプリケーションを起動してください：")
            print("  python app.py")
            print()
            return True
        else:
            raise Exception("ダウンロードしたファイルが空です")

    except Exception as e:
        print()
        print(f"✗ ダウンロードに失敗しました: {e}")
        print()
        print("手動でインストールしてください：")
        print()
        print("方法1: Google Fontsからダウンロード")
        print("  1. https://fonts.google.com/noto/specimen/Noto+Sans+JP にアクセス")
        print("  2. 'Download family' ボタンをクリック")
        print("  3. ダウンロードしたZIPファイルを解凍")
        print("  4. NotoSansJP-Regular.ttf を fonts/ フォルダにコピー")
        print()
        print("方法2: システムフォントをインストール")
        print("  Ubuntu/Debian: sudo apt-get install fonts-noto-cjk")
        print("  Fedora/RHEL: sudo dnf install google-noto-sans-cjk-jp-fonts")
        print("  macOS: デフォルトで日本語フォントがインストール済み")
        print("  Windows: デフォルトで日本語フォントがインストール済み")
        print()
        return False


if __name__ == "__main__":
    success = download_font()
    sys.exit(0 if success else 1)
