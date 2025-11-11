#!/usr/bin/env python3
"""
PDF日付追記Webアプリケーション
PDFファイルをアップロードし、年月日を入力してPDFの右上に日本語で日付を追記します。
"""

import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import uuid
from urllib.parse import quote
import json
import time
import subprocess

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


def get_version_info():
    """
    バージョン情報を取得
    優先順位: VERSIONファイル > Gitコマンド > unknown
    """
    # 1. VERSIONファイルから読み込み（本番環境用）
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception:
            pass

    # 2. Gitコマンドから取得（開発環境用）
    try:
        # Gitコミットハッシュを取得（短縮版）
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(__file__) or '.'
        ).decode('utf-8').strip()

        # コミット日時を取得
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d %H:%M'],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(__file__) or '.'
        ).decode('utf-8').strip()

        version = f"v{commit_hash} ({commit_date})"

        # VERSIONファイルに保存（次回用）
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(version)
        except Exception:
            pass

        return version
    except Exception:
        # Gitが使えない場合
        return "unknown"


def allowed_file(filename):
    """アップロード可能なファイルかチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files(age_minutes=5):
    """
    指定時間より古いファイルを削除

    Args:
        age_minutes (int): この時間（分）より古いファイルを削除
    """
    current_time = time.time()
    age_seconds = age_minutes * 60
    deleted_count = 0

    # uploadsフォルダとoutputsフォルダをクリーンアップ
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            continue

        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)

                # ファイルのみ処理（ディレクトリは除外）
                if not os.path.isfile(file_path):
                    continue

                # ファイルの最終更新時刻を取得
                file_mtime = os.path.getmtime(file_path)
                file_age = current_time - file_mtime

                # 指定時間より古いファイルを削除
                if file_age > age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"古いファイルを削除: {file_path} (経過時間: {file_age/60:.1f}分)")
        except Exception as e:
            print(f"クリーンアップエラー ({folder}): {e}")

    if deleted_count > 0:
        print(f"合計 {deleted_count} 個の古いファイルを削除しました")

    return deleted_count


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
        # 左上から：上端から20mm下、左端から150mm右の位置
        # PDF座標系は左下が原点なので、y座標を変換
        # mm → ポイント変換: 1mm = 2.83465ポイント
        margin_from_top = 20 * 2.83465  # 20mm = 56.7ポイント
        margin_from_left = 150 * 2.83465  # 150mm = 425.2ポイント

        # PDF座標系での位置（左下原点）
        # 上端から20mm下の位置を計算
        x = margin_from_left
        # ページ上端（page_height）から20mm下に配置
        y = page_height - margin_from_top

        # 日本語フォントを取得
        font_path = get_japanese_font()

        if font_path:
            # カスタムフォントを使用
            # フォントサイズ（2pt小さく）
            font_size = 10

            # insert_textで直接テキストを配置（座標が明確）
            fontfile = font_path
            fontname = "myfont"

            # テキストを挿入
            # insert_textは指定座標（ベースライン）にテキストを配置
            page.insert_text(
                (x, y),
                date_text,
                fontsize=font_size,
                fontname=fontname,
                fontfile=fontfile
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
    version = get_version_info()
    return render_template('index.html', version=version)


@app.route('/upload', methods=['POST'])
def upload_file():
    """PDFアップロードと日付追加処理"""
    # 古いファイルをクリーンアップ（5分以上前のファイルを削除）
    cleanup_old_files(age_minutes=5)

    # ファイルがアップロードされているかチェック
    if 'pdf_file' not in request.files:
        return jsonify({'success': False, 'message': 'PDFファイルが選択されていません'}), 400

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'PDFファイルが選択されていません'}), 400

    # ファイル形式チェック
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'PDFファイルのみアップロード可能です'}), 400

    # 年月日を取得
    try:
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])

        # 日付の妥当性チェック
        if not (1900 <= year <= 2100):
            return jsonify({'success': False, 'message': '年は1900から2100の範囲で入力してください'}), 400

        if not (1 <= month <= 12):
            return jsonify({'success': False, 'message': '月は1から12の範囲で入力してください'}), 400

        if not (1 <= day <= 31):
            return jsonify({'success': False, 'message': '日は1から31の範囲で入力してください'}), 400

        # 日付の存在チェック
        try:
            datetime(year, month, day)
        except ValueError:
            return jsonify({'success': False, 'message': '無効な日付です'}), 400

    except ValueError:
        return jsonify({'success': False, 'message': '年月日は数値で入力してください'}), 400

    # ファイルを保存
    # 元のファイル名を保持（日本語対応）
    original_filename = file.filename
    # ファイルシステム用の安全なファイル名
    safe_filename = secure_filename(file.filename)
    # safe_filenameが空の場合（全て非ASCII文字の場合）、UUIDを使用
    if not safe_filename:
        safe_filename = f"{uuid.uuid4()}.pdf"

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_filename = f"{timestamp}_{safe_filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)

    # 出力ファイル用のユニークIDを生成
    file_id = str(uuid.uuid4())
    output_filename = f"{file_id}.pdf"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # PDFに日付を追加
    success, message = add_date_to_pdf(input_path, output_path, year, month, day)

    if success:
        # メタデータを保存（ダウンロード後の削除用）
        metadata = {
            'input_path': input_path,
            'output_path': output_path,
            'timestamp': datetime.now().isoformat()
        }
        metadata_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)

        # ダウンロードファイル名: 元のファイル名_yyyyMMddHHmmss.pdf
        # 元の日本語ファイル名を使用
        download_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        download_filename = f"{base_name}_{download_timestamp}.pdf"

        return jsonify({
            'success': True,
            'message': message,
            'file_id': file_id,
            'download_filename': download_filename
        })
    else:
        # 処理失敗時はアップロードファイルを削除
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({'success': False, 'message': message}), 500


@app.route('/download/<file_id>')
def download_file(file_id):
    """処理済みPDFをダウンロード（日本語ファイル名対応）"""
    try:
        # ファイル名をサニタイズ
        safe_file_id = secure_filename(file_id)
        output_filename = f"{safe_file_id}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        metadata_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{safe_file_id}.json")

        # ファイルが存在するかチェック
        if not os.path.exists(output_path):
            return "ファイルが見つかりません", 404

        # メタデータを読み込む
        input_path = None
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                input_path = metadata.get('input_path')

        # ダウンロードファイル名を取得（クエリパラメータから）
        download_filename = request.args.get('filename', 'output.pdf')

        # ファイルを読み込む
        with open(output_path, 'rb') as f:
            pdf_data = f.read()

        # 日本語ファイル名対応のContent-Dispositionヘッダーを作成
        # RFC 5987に従って、ASCIIフォールバックとUTF-8エンコードの両方を提供
        # quoteは文字列を受け取り、UTF-8としてエンコードしてからパーセントエンコードする
        encoded_filename = quote(download_filename)

        # ASCIIフォールバック用のファイル名（日本語を削除）
        ascii_filename = download_filename.encode('ascii', 'ignore').decode('ascii')
        if not ascii_filename or len(ascii_filename) < 4:
            ascii_filename = 'output.pdf'

        # Content-Dispositionヘッダー
        # filename: ASCIIフォールバック
        # filename*: RFC 5987形式のUTF-8エンコード
        content_disposition = f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"

        # Responseを作成
        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': content_disposition,
                'Content-Length': str(len(pdf_data))
            }
        )

        # ダウンロード後にファイルを削除
        @response.call_on_close
        def cleanup():
            """レスポンス送信後にファイルを削除"""
            try:
                # 出力ファイルを削除
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"削除: {output_path}")

                # 入力ファイルを削除
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)
                    print(f"削除: {input_path}")

                # メタデータファイルを削除
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                    print(f"削除: {metadata_path}")
            except Exception as e:
                print(f"ファイル削除エラー: {e}")

        return response
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500


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
