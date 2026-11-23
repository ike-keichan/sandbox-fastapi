.PHONY: up upd stop restart build down downv ps db/migrate db/reset py/install py/add py/add-d py/fix py/fix-lint py/fix-format py/check py/check-lint py/check-format py/update py/test python/login python/repl db/login db/repl setup

# コンテナを、手元のパソコンと同じユーザーで動かすために、ユーザーの番号を渡す（docker-compose.yaml の user を参照）。
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)

## コンテナ操作系
# コンテナの起動
up:
	docker compose up --force-recreate
# コンテナの起動（バックグランド）
upd:
	docker compose up -d --force-recreate
# コンテナの停止
stop:
	docker compose stop
# コンテナの再起動（停止+起動）
restart:
	docker compose restart
# コンテナのビルド
build:
	docker compose build
# コンテナの削除
down:
	docker compose down --remove-orphans
# コンテナの削除（ボリューム含む）
downv:
	docker compose down -v --remove-orphans
# コンテナの状態確認
ps:
	docker compose ps -a


## DB操作系
# DBのマイグレーション（まだないテーブルを作る。データは残る）
db/migrate:
	docker compose exec api poetry run python -m api.migrate_db
# DBのリセット（全テーブルを削除して、作り直す。データは消える）
db/reset:
	docker compose exec api poetry run python -m api.migrate_db --reset


## Poetry操作系
# パッケージインストール
py/install:
	mkdir -p .dockervenv
	docker compose run --rm --no-deps api poetry install --no-root
# パッケージ追加
py/add:
	docker compose exec api poetry add $(TARGET)
# パッケージ追加（devDependency）
py/add-d:
	docker compose exec api poetry add -G dev $(TARGET)
# コード修正
py/fix: py/fix-lint py/fix-format
# コード修正（リンター）
py/fix-lint:
	docker compose exec api poetry run ruff check --fix
# コード修正（フォーマッタ）
py/fix-format:
	docker compose exec api poetry run ruff format
# コードチェック
py/check: py/check-lint py/check-format
# コードチェック（リンター）
py/check-lint:
	docker compose exec api poetry run ruff check
# コードチェック（フォーマッタ）
py/check-format:
	docker compose exec api poetry run ruff format --check
# パッケージ更新（pyproject.toml の範囲内で最新にする）
py/update:
	docker compose exec api poetry update
# テスト
py/test:
	docker compose exec api poetry run pytest


## コンソール系
# pythonコンテナのシェル
python/login:
	docker compose exec api bash
# pythonコンテナのpythonのrepl
python/repl:
	docker compose exec api poetry run python
# dbコンテナのシェル
db/login:
	docker compose exec db bash
# dbコンテナのmysqlのrepl
db/repl:
	docker compose exec db mysql demo


## その他
# セットアップ
# パッケージを入れるフォルダ（.dockervenv）は、先に作る。ないと、Docker が root の持ち物として作ってしまう。
setup:
	mkdir -p .dockervenv
	docker compose build
	docker compose run --rm --no-deps api poetry install --no-root
	docker compose up -d --force-recreate --wait
	docker compose exec api poetry run python -m api.migrate_db
	docker compose stop
