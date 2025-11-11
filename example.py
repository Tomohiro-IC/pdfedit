#!/usr/bin/env python3
"""
使用例スクリプト
PDFTextAdderの基本的な使い方を示すサンプルコード
"""

from pdf_text_adder import PDFTextAdder


def example_basic_usage():
    """基本的な使い方の例"""
    print("=== 例1: 基本的なテキスト追加 ===")

    # PDFを開く
    adder = PDFTextAdder("input.pdf")

    # ページ1の座標 (100, 700) にテキストを追加
    adder.add_text(
        page_number=1,
        x=100,
        y=700,
        text="これはサンプルテキストです",
        font_size=12
    )

    # 保存
    output = adder.save("output_basic.pdf")
    print(f"保存しました: {output}\n")


def example_textbox():
    """テキストボックスの使い方の例"""
    print("=== 例2: テキストボックス（複数行） ===")

    adder = PDFTextAdder("input.pdf")

    # 複数行のテキストをテキストボックスで追加
    adder.add_text_with_box(
        page_number=1,
        x=100,
        y=500,
        width=400,
        height=100,
        text="これは複数行のテキストです。\n\n"
             "テキストボックスを使うと、\n"
             "指定した領域内に自動的に\n"
             "折り返して表示されます。",
        font_size=11,
        align=0  # 左揃え
    )

    output = adder.save("output_textbox.pdf")
    print(f"保存しました: {output}\n")


def example_centered_text():
    """中央揃えテキストの例"""
    print("=== 例3: 中央揃えのテキスト ===")

    adder = PDFTextAdder("input.pdf")

    # タイトルを中央揃えで追加
    adder.add_text_with_box(
        page_number=1,
        x=100,
        y=750,
        width=400,
        height=40,
        text="重要なお知らせ",
        font_size=18,
        align=1  # 中央揃え
    )

    output = adder.save("output_centered.pdf")
    print(f"保存しました: {output}\n")


def example_multiple_texts():
    """複数のテキストを追加する例"""
    print("=== 例4: 複数のテキストを追加 ===")

    adder = PDFTextAdder("input.pdf")

    # ページ情報を取得
    page_count = adder.get_page_count()
    page_size = adder.get_page_size(1)
    print(f"総ページ数: {page_count}")
    print(f"ページ1のサイズ: {page_size[0]:.1f} x {page_size[1]:.1f} ポイント")

    # 複数のテキストを追加
    texts = [
        {"x": 50, "y": 800, "text": "タイトル", "size": 16},
        {"x": 50, "y": 750, "text": "サブタイトル", "size": 12},
        {"x": 50, "y": 700, "text": "本文が始まります...", "size": 10},
    ]

    for item in texts:
        adder.add_text(
            page_number=1,
            x=item["x"],
            y=item["y"],
            text=item["text"],
            font_size=item["size"]
        )

    output = adder.save("output_multiple.pdf")
    print(f"保存しました: {output}\n")


def example_form_filling():
    """フォーム入力の例（請求書や申請書など）"""
    print("=== 例5: フォーム入力 ===")

    adder = PDFTextAdder("invoice_template.pdf")

    # 請求書のフィールドを埋める
    fields = {
        "invoice_number": {"x": 450, "y": 750, "text": "INV-2025-001"},
        "date": {"x": 450, "y": 730, "text": "2025-11-11"},
        "customer_name": {"x": 100, "y": 650, "text": "株式会社サンプル"},
        "total_amount": {"x": 450, "y": 200, "text": "¥100,000"},
    }

    for field_name, field_data in fields.items():
        adder.add_text(
            page_number=1,
            x=field_data["x"],
            y=field_data["y"],
            text=field_data["text"],
            font_size=10
        )

    output = adder.save("invoice_filled.pdf")
    print(f"保存しました: {output}\n")


def main():
    """メイン関数"""
    print("PDFTextAdder 使用例\n")
    print("注意: これらの例を実行するには、適切なPDFファイルが必要です")
    print("      実際に実行する前に、PDFファイル名を適切なものに変更してください\n")

    # コメントを外して実行したい例を選択
    # example_basic_usage()
    # example_textbox()
    # example_centered_text()
    # example_multiple_texts()
    # example_form_filling()

    print("各関数のコメントを外して実行してください")


if __name__ == "__main__":
    main()
