# PDF Text Adder

PDFファイルの指定位置にテキストを追加するPythonプログラムです。

## 機能

- PDFの任意のページ、任意の座標にテキストを追加
- 単純なテキスト追加とテキストボックス（複数行対応）の2つのモード
- インタラクティブモードとコマンドラインモードの両方に対応
- フォントサイズ、配置（左・中央・右）のカスタマイズが可能

## インストール

必要なライブラリをインストールします：

```bash
pip install -r requirements.txt
```

## 使い方

### インタラクティブモード

引数なしで実行すると、対話形式でテキストを追加できます：

```bash
python pdf_text_adder.py
```

プログラムが以下の情報を順番に尋ねます：
1. PDFファイルのパス
2. ページ番号
3. 追加モード（単純テキスト or テキストボックス）
4. 座標やサイズ
5. 追加するテキスト
6. フォントサイズ
7. 出力ファイル名

### コマンドラインモード

#### 単純テキストの追加

1行のテキストを指定座標に追加します：

```bash
python pdf_text_adder.py input.pdf -p 1 -x 100 -y 100 -t "Hello World" -o output.pdf
```

#### テキストボックスの追加

複数行のテキストを指定領域に追加します：

```bash
python pdf_text_adder.py input.pdf -p 1 -x 100 -y 100 -w 200 -h 50 -t "複数行\nテキスト" -o output.pdf
```

### オプション一覧

| オプション | 説明 | 必須 |
|-----------|------|------|
| `pdf_file` | 入力PDFファイルのパス | ○ |
| `-p`, `--page` | ページ番号（1から開始） | ○ |
| `-x` | X座標（ポイント単位） | ○ |
| `-y` | Y座標（ポイント単位） | ○ |
| `-t`, `--text` | 追加するテキスト | ○ |
| `-w`, `--width` | テキストボックスの幅 | テキストボックスの場合必須 |
| `-H`, `--height` | テキストボックスの高さ | テキストボックスの場合必須 |
| `-s`, `--font-size` | フォントサイズ（デフォルト: 12） | × |
| `-o`, `--output` | 出力ファイルパス（指定なしの場合は自動生成） | × |
| `-a`, `--align` | テキスト配置（0=左, 1=中央, 2=右） | × |

## 座標系について

PDFの座標系は左下が原点(0, 0)です：
- X座標：左から右へ増加
- Y座標：下から上へ増加

一般的なPDFのサイズ：
- A4サイズ：約 595 x 842 ポイント
- レターサイズ：約 612 x 792 ポイント

## 使用例

### 例1: 請求書に日付を追加

```bash
python pdf_text_adder.py invoice.pdf -p 1 -x 400 -y 750 -t "2025-11-11" -s 10 -o invoice_dated.pdf
```

### 例2: 契約書に署名欄を追加

```bash
python pdf_text_adder.py contract.pdf -p 5 -x 100 -y 100 -w 200 -h 80 -t "署名: _______________\n\n日付: _______________" -s 11 -o contract_signed.pdf
```

### 例3: 証明書に名前を中央揃えで追加

```bash
python pdf_text_adder.py certificate.pdf -p 1 -x 150 -y 400 -w 300 -h 50 -t "山田 太郎" -s 18 -a 1 -o certificate_named.pdf
```

## プログラムとして使用

Pythonコードから直接使用することもできます：

```python
from pdf_text_adder import PDFTextAdder

# PDFを開く
adder = PDFTextAdder("input.pdf")

# テキストを追加
adder.add_text(
    page_number=1,
    x=100,
    y=100,
    text="Hello World",
    font_size=12
)

# テキストボックスを追加
adder.add_text_with_box(
    page_number=1,
    x=100,
    y=200,
    width=200,
    height=50,
    text="複数行\nテキスト",
    font_size=11,
    align=1  # 中央揃え
)

# 保存
adder.save("output.pdf")
```

## トラブルシューティング

### 日本語が表示されない

PyMuPDFのデフォルトフォント（Helvetica）は日本語に対応していません。日本語を使用する場合は、プログラムを修正して日本語フォントを指定する必要があります。

### 座標がわからない

インタラクティブモードでページサイズを確認できます。また、PDF編集ソフトで座標を確認することもできます。

## ライセンス

MIT License

## 必要要件

- Python 3.6以上
- PyMuPDF (fitz) 1.24.0以上
