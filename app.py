#!/usr/bin/env python3
"""
PDF日付追記Webアプリケーション
PDFファイルをアップロードし、年月日を入力してPDFの右上に日本語で日付を追記します。
"""

import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from urllib.parse import quote
import json
import time
import subprocess
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# 設定
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
FONT_FOLDER = 'fonts'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
FILE_AGE_MINUTES = 5  # 古いファイルを削除する時間（分）
MM_TO_POINTS = 2.83465  # mmからポイントへの変換係数

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# フォルダを作成
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, FONT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# バージョン情報のキャッシュ
_version_cache = None


def get_version_info():
    """
    バージョン情報を取得（キャッシュ付き）
    優先順位: キャッシュ > VERSIONファイル > Gitコマンド > unknown
    """
    global _version_cache

    # キャッシュがあれば返す
    if _version_cache:
        return _version_cache

    # VERSIONファイルから読み込み（本番環境）
    version_file = Path(__file__).parent / 'VERSION'
    if version_file.exists():
        try:
            _version_cache = version_file.read_text(encoding='utf-8').strip()
            return _version_cache
        except (IOError, OSError):
            pass

    # Gitコマンドから取得（開発環境）
    try:
        cwd = Path(__file__).parent or Path('.')
        env = os.environ.copy()
        env['TZ'] = 'Asia/Tokyo'  # 日本時間を使用

        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
            cwd=str(cwd),
            text=True
        ).strip()

        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=format-local:%Y-%m-%d %H:%M'],
            stderr=subprocess.DEVNULL,
            cwd=str(cwd),
            env=env,
            text=True
        ).strip()

        _version_cache = f"v{commit_hash} ({commit_date} JST)"

        # VERSIONファイルに保存（次回用）
        try:
            version_file.write_text(_version_cache, encoding='utf-8')
        except (IOError, OSError):
            pass

        return _version_cache
    except (subprocess.SubprocessError, OSError):
        _version_cache = "unknown"
        return _version_cache


def allowed_file(filename):
    """アップロード可能なファイルかチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files(age_minutes=FILE_AGE_MINUTES):
    """
    指定時間より古いファイルを削除

    Args:
        age_minutes (int): この時間（分）より古いファイルを削除
    """
    current_time = time.time()
    age_seconds = age_minutes * 60
    deleted_files = []

    # uploadsフォルダとoutputsフォルダをクリーンアップ
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue

        try:
            # 古いファイルをフィルタリング
            old_files = [
                f for f in folder_path.iterdir()
                if f.is_file() and (current_time - f.stat().st_mtime) > age_seconds
            ]

            # 削除処理
            for file_path in old_files:
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    file_path.unlink()
                    deleted_files.append((str(file_path), file_age / 60))
                except OSError as e:
                    print(f"削除失敗: {file_path} - {e}")
        except OSError as e:
            print(f"クリーンアップエラー ({folder}): {e}")

    # ログ出力
    if deleted_files:
        for path, age in deleted_files:
            print(f"古いファイルを削除: {path} (経過時間: {age:.1f}分)")
        print(f"合計 {len(deleted_files)} 個の古いファイルを削除しました")

    return len(deleted_files)


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

        # 日付テキストを作成（年月日の文字なし、全角スペース2文字で区切り）
        # PDF側に「年　月　日」が既に印字されているため、数字のみ
        date_text = f"{year}　　{month}　　{day}"

        # 座標を計算（左上から：上端から22mm下、左端から156mm右）
        margin_from_top = 22 * MM_TO_POINTS
        margin_from_left = 156 * MM_TO_POINTS

        # PDF座標系での位置
        # PyMuPDFの座標系：左上が原点(0,0)、y軸は上から下に増加
        # したがって、上端から22mm下の位置は単純に margin_from_top
        x = margin_from_left
        y = margin_from_top

        # 日本語フォントを取得
        font_path = get_japanese_font()

        if font_path:
            # フォントサイズ（元は12pt、2pt小さく）
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


def _error_response(message, status_code=400):
    """エラーレスポンスを返す"""
    return jsonify({'success': False, 'message': message}), status_code


@app.route('/upload', methods=['POST'])
def upload_file():
    """PDFアップロードと日付追加処理"""
    # 古いファイルをクリーンアップ
    cleanup_old_files()

    # ファイルがアップロードされているかチェック
    if 'pdf_file' not in request.files or request.files['pdf_file'].filename == '':
        return _error_response('PDFファイルが選択されていません')

    file = request.files['pdf_file']

    # ファイル形式チェック
    if not allowed_file(file.filename):
        return _error_response('PDFファイルのみアップロード可能です')

    # 年月日を取得とバリデーション
    try:
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])

        # 範囲チェック
        if not (1900 <= year <= 2100):
            return _error_response('年は1900から2100の範囲で入力してください')
        if not (1 <= month <= 12):
            return _error_response('月は1から12の範囲で入力してください')
        if not (1 <= day <= 31):
            return _error_response('日は1から31の範囲で入力してください')

        # 日付の存在チェック
        datetime(year, month, day)

    except ValueError as e:
        return _error_response('年月日は正しい数値で入力してください')

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

    if not success:
        # 処理失敗時はアップロードファイルを削除
        Path(input_path).unlink(missing_ok=True)
        return _error_response(message, 500)

    # メタデータを保存（ダウンロード後の削除用）
    metadata_path = Path(OUTPUT_FOLDER) / f"{file_id}.json"
    metadata_path.write_text(json.dumps({
        'input_path': input_path,
        'output_path': output_path,
        'timestamp': datetime.now().isoformat()
    }), encoding='utf-8')

    # ダウンロードファイル名: 元のファイル名_yyyyMMddHHmmss.pdf
    base_name = Path(original_filename).stem
    download_filename = f"{base_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    return jsonify({
        'success': True,
        'message': message,
        'file_id': file_id,
        'download_filename': download_filename
    })


@app.route('/download/<file_id>')
def download_file(file_id):
    """処理済みPDFをダウンロード（日本語ファイル名対応）"""
    try:
        # ファイルパスを構築
        safe_file_id = secure_filename(file_id)
        output_path = Path(OUTPUT_FOLDER) / f"{safe_file_id}.pdf"
        metadata_path = Path(OUTPUT_FOLDER) / f"{safe_file_id}.json"

        # ファイルの存在確認
        if not output_path.exists():
            return "ファイルが見つかりません", 404

        # メタデータを読み込む
        input_path = None
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
            input_path = metadata.get('input_path')

        # ダウンロードファイル名を取得
        download_filename = request.args.get('filename', 'output.pdf')

        # PDFデータを読み込む
        pdf_data = output_path.read_bytes()

        # 日本語ファイル名対応のContent-Dispositionヘッダー（RFC 5987準拠）
        encoded_filename = quote(download_filename)
        ascii_filename = download_filename.encode('ascii', 'ignore').decode('ascii') or 'output.pdf'
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
            files_to_delete = [
                output_path,
                metadata_path,
                Path(input_path) if input_path else None
            ]

            for file_path in files_to_delete:
                if file_path:
                    try:
                        file_path.unlink(missing_ok=True)
                        print(f"削除: {file_path}")
                    except OSError as e:
                        print(f"ファイル削除エラー: {file_path} - {e}")

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
