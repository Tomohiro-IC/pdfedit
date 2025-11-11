#!/bin/bash
# 日本語フォントのセットアップスクリプト

echo "=========================================="
echo "日本語フォントセットアップ"
echo "=========================================="
echo ""

# fontsディレクトリを作成
mkdir -p fonts

# システムにフォントがインストールされているかチェック
if [ -f "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" ]; then
    echo "✓ システムに日本語フォントがインストールされています"
    echo "  /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    echo ""
    echo "追加の設定は不要です。"
    exit 0
fi

# Noto Sans JPフォントをダウンロード
echo "Noto Sans JP フォントをダウンロードしています..."
echo ""

# 一時ディレクトリを作成
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Noto Sans JPの最新版をダウンロード（Google Fonts APIから）
echo "Google Fontsからダウンロード中..."
wget -q --show-progress "https://fonts.google.com/download?family=Noto%20Sans%20JP" -O NotoSansJP.zip

if [ $? -eq 0 ]; then
    echo "✓ ダウンロード完了"
    echo ""

    # 解凍
    echo "解凍しています..."
    unzip -q NotoSansJP.zip

    # Regularフォントをコピー
    if [ -f "NotoSansJP-Regular.ttf" ]; then
        cp NotoSansJP-Regular.ttf "$OLDPWD/fonts/"
        echo "✓ フォントをインストールしました: fonts/NotoSansJP-Regular.ttf"
    elif ls static/NotoSansJP-Regular.ttf 2>/dev/null; then
        cp static/NotoSansJP-Regular.ttf "$OLDPWD/fonts/"
        echo "✓ フォントをインストールしました: fonts/NotoSansJP-Regular.ttf"
    elif ls *.ttf 2>/dev/null; then
        # 最初のttfファイルをコピー
        cp *.ttf "$OLDPWD/fonts/NotoSansJP-Regular.ttf"
        echo "✓ フォントをインストールしました: fonts/NotoSansJP-Regular.ttf"
    else
        echo "✗ エラー: フォントファイルが見つかりませんでした"
        echo ""
        echo "手動でインストールしてください："
        echo "1. https://fonts.google.com/noto/specimen/Noto+Sans+JP にアクセス"
        echo "2. 'Download family' ボタンをクリック"
        echo "3. ダウンロードしたZIPファイルを解凍"
        echo "4. NotoSansJP-Regular.ttf を fonts/ フォルダにコピー"
        cd "$OLDPWD"
        rm -rf "$TMP_DIR"
        exit 1
    fi
else
    echo "✗ ダウンロードに失敗しました"
    echo ""
    echo "手動でインストールしてください："
    echo "1. https://fonts.google.com/noto/specimen/Noto+Sans+JP にアクセス"
    echo "2. 'Download family' ボタンをクリック"
    echo "3. ダウンロードしたZIPファイルを解凍"
    echo "4. NotoSansJP-Regular.ttf を fonts/ フォルダにコピー"
    cd "$OLDPWD"
    rm -rf "$TMP_DIR"
    exit 1
fi

# 一時ディレクトリを削除
cd "$OLDPWD"
rm -rf "$TMP_DIR"

echo ""
echo "=========================================="
echo "セットアップ完了！"
echo "=========================================="
echo ""
echo "Webアプリケーションを起動してください："
echo "  python app.py"
echo ""
