#!/bin/bash
# VERSIONファイルを生成するスクリプト
# デプロイ前に実行してください

set -e

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Gitコミット情報を取得
if command -v git &> /dev/null && [ -d .git ]; then
    COMMIT_HASH=$(git rev-parse --short HEAD)
    COMMIT_DATE=$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M')
    VERSION="v${COMMIT_HASH} (${COMMIT_DATE})"

    echo "$VERSION" > VERSION
    echo "✓ VERSIONファイルを生成しました: $VERSION"
else
    echo "✗ Gitが利用できないため、VERSIONファイルを生成できませんでした"
    exit 1
fi
