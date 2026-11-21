#!/usr/bin/env bash
# 起動したAPIを、実際に呼んで確かめるスクリプト。自動テスト（GitHub Actions）から実行する。
# テスト（make py/test）はDBをSQLiteで代用するので、MySQLにつないだ状態の確認は、ここで行う。
# 機能を足したら、その機能のAPIを呼ぶ行を足す。
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

# 起動が終わるまで、少し待ちながら呼ぶ。
curl --fail --silent --show-error --retry 10 --retry-connrefused --retry-delay 2 "${BASE_URL}/hello"
echo
