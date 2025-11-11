# PDF日付追記Webアプリケーション

PDFファイルの右上に日本語で日付を追記するWebアプリケーションです。

![PDF Date Adder](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 機能

- **日本語対応**: 日本語フォントで「○○年○○月○○日」形式の日付を追記
- **Webインターフェース**: ブラウザから簡単に操作
- **PDFアップロード**: ドラッグ&ドロップまたはクリックでファイル選択
- **日付入力**: 年・月・日を個別に入力（今日の日付が初期値）
- **自動配置**: PDFの右上（上から50px、右端から100px）に自動配置
- **即座にダウンロード**: 処理完了後、編集済みPDFを自動ダウンロード

## 📋 必要要件

- Python 3.7以上
- PyMuPDF (fitz) 1.24.0以上
- Flask 3.0以上
- 日本語フォント（Noto Sans JP推奨）

## 🚀 クイックスタート

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd pdfedit
```

### 2. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

### 3. 日本語フォントをセットアップ

#### 自動セットアップ（推奨）

```bash
# Pythonスクリプトを使用（Windows/Mac/Linux対応）
python setup_font.py

# または、シェルスクリプトを使用（Linux/Mac）
./setup_font.sh
```

#### 手動セットアップ

1. [Google Fonts - Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP) にアクセス
2. "Download family" ボタンをクリック
3. ダウンロードしたZIPファイルを解凍
4. `NotoSansJP-Regular.ttf` を `fonts/` フォルダにコピー

#### システムフォントを使用

```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# Fedora/RHEL
sudo dnf install google-noto-sans-cjk-jp-fonts

# macOS, Windows: デフォルトで日本語フォントがインストール済み
```

### 4. Webアプリケーションを起動

```bash
python app.py
```

サーバーが起動したら、ブラウザで以下にアクセス：
```
http://localhost:5000
```

## 💻 使い方

### Webアプリケーション

1. **PDFファイルを選択**: クリックまたはドラッグ&ドロップでPDFファイルを選択
2. **日付を入力**: 年・月・日を入力（初期値は今日の日付）
3. **追加してダウンロード**: 「日付を追加してダウンロード」ボタンをクリック
4. **完了**: 編集済みPDFが自動的にダウンロードされます

### 日付の追記位置

PDFの右上に以下の形式で追記されます：
- **位置**: 上から50px、右端から100px左
- **形式**: `2025年11月11日`
- **フォントサイズ**: 12pt
- **配置**: 右揃え

### コマンドラインツール（従来版）

コマンドラインから使用することもできます：

```bash
# インタラクティブモード
python pdf_text_adder.py

# コマンドラインモード
python pdf_text_adder.py input.pdf -p 1 -x 100 -y 100 -t "テキスト" -o output.pdf
```

詳細は `pdf_text_adder.py --help` を参照してください。

## 📁 プロジェクト構造

```
pdfedit/
├── app.py                  # Flaskアプリケーション（メイン）
├── pdf_text_adder.py       # PDF編集ライブラリ（コマンドライン版）
├── requirements.txt        # 必要なPythonパッケージ
├── setup_font.py           # フォントセットアップスクリプト（Python）
├── setup_font.sh           # フォントセットアップスクリプト（Shell）
├── templates/
│   └── index.html         # Webインターフェース
├── fonts/                 # 日本語フォント配置フォルダ
├── uploads/               # アップロードされたPDF一時保存
├── outputs/               # 編集済みPDF一時保存
└── example.py             # サンプルコード
```

## 🔧 設定

### フォントの確認

ブラウザで以下にアクセスして、フォントの状態を確認できます：
```
http://localhost:5000/check-font
```

### サーバー設定

`app.py` の以下の部分を編集して設定を変更できます：

```python
# ポート番号を変更
app.run(debug=True, host='0.0.0.0', port=5000)

# 本番環境では debug=False に設定
app.run(debug=False, host='0.0.0.0', port=5000)

# 最大ファイルサイズを変更（バイト単位）
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
```

## 🎨 カスタマイズ

### 日付の位置を変更

`app.py` の `add_date_to_pdf()` 関数内の以下の部分を編集：

```python
# 上からの距離（px）
margin_from_top = 50

# 右からの距離（px）
margin_from_right = 100
```

### フォントサイズを変更

```python
# フォントサイズ
font_size = 12
```

### 日付フォーマットを変更

```python
# 日付テキストを作成
date_text = f"{year}年{month}月{day}日"

# 例: 西暦付き
date_text = f"令和{year-2018}年{month}月{day}日"

# 例: スラッシュ区切り
date_text = f"{year}/{month:02d}/{day:02d}"
```

## 🐛 トラブルシューティング

### 日本語が文字化けする

**原因**: 日本語フォントが見つからない

**解決方法**:
1. `http://localhost:5000/check-font` でフォント状態を確認
2. `python setup_font.py` を実行してフォントをインストール
3. または、手動で `fonts/` フォルダに日本語フォントを配置

### PDFが正しくアップロードされない

**原因**: ファイルサイズが大きすぎる

**解決方法**:
- `app.py` の `MAX_FILE_SIZE` を増やす
- PDFファイルを圧縮する

### ポート5000が使用中

**原因**: 他のアプリケーションがポート5000を使用している

**解決方法**:
```python
# app.py の最終行を変更
app.run(debug=True, host='0.0.0.0', port=8000)  # ポート番号を変更
```

## 📚 サンプルコード

Pythonコードから直接使用する例：

```python
from pdf_text_adder import PDFTextAdder

# PDFを開く
adder = PDFTextAdder("input.pdf")

# テキストを追加
adder.add_text(
    page_number=1,
    x=100,
    y=700,
    text="2025年11月11日",
    font_size=12
)

# 保存
adder.save("output.pdf")
```

詳細なサンプルは `example.py` を参照してください。

## 🔐 セキュリティ

本番環境で使用する場合は、以下の点に注意してください：

1. **シークレットキーの変更**: `app.py` の `app.secret_key` を変更
2. **デバッグモードの無効化**: `debug=False` に設定
3. **ファイルサイズ制限**: `MAX_FILE_SIZE` を適切に設定
4. **アップロードファイルの検証**: 悪意のあるファイルの検証を追加
5. **HTTPS**: 本番環境では HTTPS を使用

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストを歓迎します！

## 📧 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

**注意**: このアプリケーションはローカル環境での使用を想定しています。本番環境で公開する場合は、適切なセキュリティ対策を実施してください。
