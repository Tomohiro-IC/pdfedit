#!/usr/bin/env python3
"""
PDF日付追記Webアプリケーション
PDFファイルをアップロードし、年月日を入力してPDFの右上に日本語で日付を追記します。
"""

import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# 設定
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
FONT_FOLDER = 'fonts'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# フォルダを作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FONT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """アップロード可能なファイルかチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_japanese_font():
    """
    日本語フォントのパスを取得
    優先順位: fonts/フォルダ > システムフォント
    """
    # fonts/フォルダ内のフォントをチェック
    font_files = [
        os.path.join(FONT_FOLDER, 'NotoSansJP-Regular.ttf'),
        os.path.join(FONT_FOLDER, 'NotoSansCJKjp-Regular.ttf'),
        os.path.join(FONT_FOLDER, 'ipag.ttf'),
        os.path.join(FONT_FOLDER, 'ipaexg.ttf'),
    ]

    for font_file in font_files:
        if os.path.exists(font_file):
            return font_file

    # システムフォントをチェック
    system_fonts = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        'C:\\Windows\\Fonts\\msgothic.ttc',
        'C:\\Windows\\Fonts\\meiryo.ttc',
        '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf',
        '/usr/share/fonts/ipa-gothic/ipag.ttf',
    ]

    for font_file in system_fonts:
        if os.path.exists(font_file):
            return font_file

    return None


def add_date_to_pdf(input_pdf_path, output_pdf_path, year, month, day):
    """
    PDFの右上に日付を追加

    Args:
        input_pdf_path (str): 入力PDFファイルのパス
        output_pdf_path (str): 出力PDFファイルのパス
        year (int): 年
        month (int): 月
        day (int): 日

    Returns:
        tuple: (成功フラグ, メッセージ)
    """
    try:
        # PDFを開く
        doc = fitz.open(input_pdf_path)

        # 最初のページを取得
        page = doc[0]
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        # 日付テキストを作成
        date_text = f"{year}年{month}月{day}日"

        # 座標を計算
        # 右上から：上から50px、左から100px離れた位置
        # PDF座標系は左下が原点なので、y座標を変換
        margin_from_top = 50
        margin_from_right = 100

        # PDF座標系での位置
        x = page_width - margin_from_right
        y = page_height - margin_from_top

        # 日本語フォントを取得
        font_path = get_japanese_font()

        if font_path:
            # カスタムフォントを使用
            # フォントサイズ
            font_size = 12

            # テキストの幅を計算（右揃えにするため）
            # PyMuPDFでは直接テキスト幅を計算する方法が限られているので、
            # insert_textboxを使用

            # テキストボックスの領域を定義（右揃え）
            text_width = 150  # 推定幅
            rect = fitz.Rect(x - text_width, y - 20, x, y + 5)

            # カスタムフォントでテキストを挿入
            fontfile = font_path
            fontname = "myfont"

            # フォントを登録
            page.insert_textbox(
                rect,
                date_text,
                fontsize=font_size,
                fontname=fontname,
                fontfile=fontfile,
                align=2  # 右揃え
            )
        else:
            # フォールバック: 組み込みフォントを使用（日本語は正しく表示されない可能性）
            return False, "日本語フォントが見つかりません。fontsフォルダにNotoSansJP-Regular.ttfなどの日本語フォントを配置してください。"

        # PDFを保存
        doc.save(output_pdf_path)
        doc.close()

        return True, f"日付「{date_text}」をPDFに追加しました"

    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"


@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """PDFアップロードと日付追加処理"""
    # ファイルがアップロードされているかチェック
    if 'pdf_file' not in request.files:
        flash('PDFファイルが選択されていません', 'error')
        return redirect(url_for('index'))

    file = request.files['pdf_file']

    if file.filename == '':
        flash('PDFファイルが選択されていません', 'error')
        return redirect(url_for('index'))

    # ファイル形式チェック
    if not allowed_file(file.filename):
        flash('PDFファイルのみアップロード可能です', 'error')
        return redirect(url_for('index'))

    # 年月日を取得
    try:
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])

        # 日付の妥当性チェック
        if not (1900 <= year <= 2100):
            flash('年は1900から2100の範囲で入力してください', 'error')
            return redirect(url_for('index'))

        if not (1 <= month <= 12):
            flash('月は1から12の範囲で入力してください', 'error')
            return redirect(url_for('index'))

        if not (1 <= day <= 31):
            flash('日は1から31の範囲で入力してください', 'error')
            return redirect(url_for('index'))

        # 日付の存在チェック
        try:
            datetime(year, month, day)
        except ValueError:
            flash('無効な日付です', 'error')
            return redirect(url_for('index'))

    except ValueError:
        flash('年月日は数値で入力してください', 'error')
        return redirect(url_for('index'))

    # ファイルを保存
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_filename = f"{timestamp}_{filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)

    # 出力ファイル名
    output_filename = f"dated_{input_filename}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # PDFに日付を追加
    success, message = add_date_to_pdf(input_path, output_path, year, month, day)

    if success:
        flash(message, 'success')
        # ファイルをダウンロード
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"dated_{filename}",
            mimetype='application/pdf'
        )
    else:
        flash(message, 'error')
        return redirect(url_for('index'))


@app.route('/check-font')
def check_font():
    """フォント状態をチェック"""
    font_path = get_japanese_font()
    if font_path:
        return f"日本語フォントが見つかりました: {font_path}"
    else:
        return """
        日本語フォントが見つかりません。<br>
        以下のいずれかの方法でフォントを設定してください：<br>
        <br>
        1. fontsフォルダに日本語フォントファイルを配置<br>
        推奨: NotoSansJP-Regular.ttf<br>
        ダウンロード: <a href="https://fonts.google.com/noto/specimen/Noto+Sans+JP" target="_blank">Google Fonts - Noto Sans JP</a><br>
        <br>
        2. システムに日本語フォントをインストール<br>
        Ubuntu/Debian: sudo apt-get install fonts-noto-cjk<br>
        """


if __name__ == '__main__':
    print("=" * 60)
    print("PDF日付追記Webアプリケーション")
    print("=" * 60)

    # フォントチェック
    font_path = get_japanese_font()
    if font_path:
        print(f"✓ 日本語フォント: {font_path}")
    else:
        print("⚠ 警告: 日本語フォントが見つかりません")
        print("  http://localhost:5000/check-font でフォント設定方法を確認してください")

    print("\nサーバーを起動しています...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
