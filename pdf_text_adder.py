#!/usr/bin/env python3
"""
PDF Text Adder
PDFファイルの指定位置にテキストを追加するプログラム
"""

import fitz  # PyMuPDF
import sys
import argparse
from pathlib import Path


class PDFTextAdder:
    """PDFにテキストを追加するクラス"""

    def __init__(self, pdf_path):
        """
        初期化

        Args:
            pdf_path (str): PDFファイルのパス
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

        self.doc = fitz.open(str(self.pdf_path))

    def add_text(self, page_number, x, y, text, font_size=12, color=(0, 0, 0), font_name="helv"):
        """
        指定ページの指定位置にテキストを追加

        Args:
            page_number (int): ページ番号（1から開始）
            x (float): X座標（ポイント単位）
            y (float): Y座標（ポイント単位）
            text (str): 追加するテキスト
            font_size (int): フォントサイズ（デフォルト: 12）
            color (tuple): RGB色（0-1の範囲、デフォルト: 黒）
            font_name (str): フォント名（デフォルト: "helv"）
        """
        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(f"ページ番号は1から{len(self.doc)}の範囲で指定してください")

        page = self.doc[page_number - 1]  # 0-indexedに変換

        # テキストを挿入
        point = fitz.Point(x, y)
        page.insert_text(
            point,
            text,
            fontsize=font_size,
            color=color,
            fontname=font_name
        )

        print(f"✓ ページ {page_number} の座標 ({x}, {y}) にテキストを追加しました")

    def add_text_with_box(self, page_number, x, y, width, height, text,
                          font_size=12, color=(0, 0, 0), align=0):
        """
        指定ページの指定領域内にテキストを追加（複数行対応）

        Args:
            page_number (int): ページ番号（1から開始）
            x (float): 左上X座標
            y (float): 左上Y座標
            width (float): 幅
            height (float): 高さ
            text (str): 追加するテキスト
            font_size (int): フォントサイズ
            color (tuple): RGB色（0-1の範囲）
            align (int): 配置（0=左, 1=中央, 2=右）
        """
        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(f"ページ番号は1から{len(self.doc)}の範囲で指定してください")

        page = self.doc[page_number - 1]

        # テキストボックスを作成
        rect = fitz.Rect(x, y, x + width, y + height)
        page.insert_textbox(
            rect,
            text,
            fontsize=font_size,
            color=color,
            align=align
        )

        print(f"✓ ページ {page_number} の領域 ({x}, {y}, {width}, {height}) にテキストボックスを追加しました")

    def save(self, output_path=None):
        """
        PDFを保存

        Args:
            output_path (str): 出力ファイルパス（Noneの場合は元のファイルを上書き）
        """
        if output_path is None:
            # 元のファイル名に "_edited" を追加
            stem = self.pdf_path.stem
            suffix = self.pdf_path.suffix
            output_path = self.pdf_path.parent / f"{stem}_edited{suffix}"

        self.doc.save(str(output_path))
        self.doc.close()
        print(f"✓ PDFを保存しました: {output_path}")
        return output_path

    def get_page_count(self):
        """ページ数を取得"""
        return len(self.doc)

    def get_page_size(self, page_number):
        """
        ページサイズを取得

        Args:
            page_number (int): ページ番号（1から開始）

        Returns:
            tuple: (幅, 高さ)
        """
        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(f"ページ番号は1から{len(self.doc)}の範囲で指定してください")

        page = self.doc[page_number - 1]
        rect = page.rect
        return (rect.width, rect.height)

    def __del__(self):
        """デストラクタ"""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()


def interactive_mode():
    """インタラクティブモード"""
    print("=== PDF テキスト追加ツール ===\n")

    # PDFファイルのパスを入力
    pdf_path = input("PDFファイルのパスを入力してください: ").strip()

    try:
        adder = PDFTextAdder(pdf_path)
        print(f"✓ PDFファイルを読み込みました")
        print(f"  総ページ数: {adder.get_page_count()}")

        # ページ番号を入力
        page_num = int(input("\nテキストを追加するページ番号を入力してください: "))
        page_size = adder.get_page_size(page_num)
        print(f"  ページサイズ: {page_size[0]:.1f} x {page_size[1]:.1f} ポイント")

        # モードを選択
        print("\nモードを選択してください:")
        print("  1. 単純テキスト（1行）")
        print("  2. テキストボックス（複数行対応）")
        mode = input("選択 (1 or 2): ").strip()

        if mode == "1":
            # 単純テキストモード
            x = float(input("X座標を入力してください: "))
            y = float(input("Y座標を入力してください: "))
            text = input("追加するテキストを入力してください: ")
            font_size = int(input("フォントサイズを入力してください (デフォルト: 12): ") or "12")

            adder.add_text(page_num, x, y, text, font_size=font_size)

        elif mode == "2":
            # テキストボックスモード
            x = float(input("左上X座標を入力してください: "))
            y = float(input("左上Y座標を入力してください: "))
            width = float(input("幅を入力してください: "))
            height = float(input("高さを入力してください: "))
            text = input("追加するテキストを入力してください: ")
            font_size = int(input("フォントサイズを入力してください (デフォルト: 12): ") or "12")

            adder.add_text_with_box(page_num, x, y, width, height, text, font_size=font_size)

        else:
            print("無効な選択です")
            return

        # 保存
        output_path = input("\n出力ファイル名を入力してください (空白で自動生成): ").strip()
        output_path = output_path if output_path else None
        adder.save(output_path)

        print("\n✓ 完了しました!")

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='PDFファイルの指定位置にテキストを追加します',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # インタラクティブモード
  python pdf_text_adder.py

  # コマンドラインモード（単純テキスト）
  python pdf_text_adder.py input.pdf -p 1 -x 100 -y 100 -t "Hello World" -o output.pdf

  # テキストボックスモード
  python pdf_text_adder.py input.pdf -p 1 -x 100 -y 100 -w 200 -h 50 -t "複数行\\nテキスト" -o output.pdf
        """
    )

    parser.add_argument('pdf_file', nargs='?', help='PDFファイルのパス')
    parser.add_argument('-p', '--page', type=int, help='ページ番号（1から開始）')
    parser.add_argument('-x', type=float, help='X座標')
    parser.add_argument('-y', type=float, help='Y座標')
    parser.add_argument('-w', '--width', type=float, help='テキストボックスの幅')
    parser.add_argument('-H', '--height', type=float, help='テキストボックスの高さ')
    parser.add_argument('-t', '--text', help='追加するテキスト')
    parser.add_argument('-s', '--font-size', type=int, default=12, help='フォントサイズ（デフォルト: 12）')
    parser.add_argument('-o', '--output', help='出力ファイルパス')
    parser.add_argument('-a', '--align', type=int, choices=[0, 1, 2], default=0,
                       help='テキスト配置（0=左, 1=中央, 2=右、デフォルト: 0）')

    args = parser.parse_args()

    # 引数なしの場合はインタラクティブモード
    if args.pdf_file is None:
        interactive_mode()
        return

    # 必須パラメータのチェック
    if not all([args.page, args.x is not None, args.y is not None, args.text]):
        print("エラー: -p, -x, -y, -t は必須パラメータです", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        adder = PDFTextAdder(args.pdf_file)

        # テキストボックスモードか単純テキストモード
        if args.width and args.height:
            adder.add_text_with_box(
                args.page,
                args.x,
                args.y,
                args.width,
                args.height,
                args.text,
                font_size=args.font_size,
                align=args.align
            )
        else:
            adder.add_text(
                args.page,
                args.x,
                args.y,
                args.text,
                font_size=args.font_size
            )

        output_path = adder.save(args.output)
        print("✓ 完了しました!")

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
