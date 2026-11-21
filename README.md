# sandbox-fastapi

FastAPI（MySQL、Docker Compose）の技術検証と、プロジェクトのひな形を兼ねたリポジトリ。

FastAPI で Web API を作るときの土台を、すぐ動く状態でまとめています。新しいプロジェクトを始めるときのひな形として使うほか、ライブラリの新しい版や、別の構成を試す場所としても使います。

## Description

- [Branch](#branch)
- [Tool Versions](#tool-versions)
- [Getting Started](#getting-started)
- [Command](#command)
- [Documents](#documents)

---

## Branch

目的の違う内容を、ブランチで分けています。

| ブランチ | 内容 | 使いみち |
| --- | --- | --- |
| [`main`](https://github.com/ike-keichan/sandbox-fastapi) | 最小の形。API は、動作の確認用の `GET /hello` だけ | 新しいプロジェクトの出発点にします |
| [`example/task-api`](https://github.com/ike-keichan/sandbox-fastapi/tree/example/task-api) | `main` に、タスクを管理する API を足した見本 | 機能の足し方の手本にします |

`README.md` と、`readme/` の番号つきの文書は、どのブランチでも同じ内容です。`example/` で始まるブランチには、そのブランチの説明（`readme/EXAMPLE_*.md`）が入っています。

---

## Tool Versions

| 役割 | 使っているもの | バージョン |
| --- | --- | --- |
| 言語 | Python | 3.15 |
| Web フレームワーク | FastAPI | 0.165 |
| サーバー | Uvicorn | 0.54 |
| データベース | MySQL | 8.4（長期サポート版） |
| データベースの操作 | SQLAlchemy（非同期。ドライバは aiomysql） | 2.1 |
| パッケージ管理 | Poetry | 2.5 |
| コードの検査と整形 | Ruff | 0.17 |
| テスト | pytest（非同期のテストに pytest-asyncio、API の呼び出しに HTTPX） | 9.2 |

Python と MySQL は、Docker のコンテナの中で動きます。手元に必要なのは、Docker Desktop、make、Git だけです。

正確なバージョンは、[pyproject.toml](./pyproject.toml)、`poetry.lock`、[Dockerfile](./Dockerfile)、[docker-compose.yaml](./docker-compose.yaml) に記録しています。

---

## Getting Started

環境構築の手順は、[こちら](./readme/01_GETTING_STARTED.md)。

手順を終えると、<http://localhost:8000/docs> で API を試せるようになります。

---

## Command

主要なコマンドは、以下のとおりです。それ以外のコマンドの詳細は、[こちら](./readme/02_COMMAND.md)。

| コマンド | 内容 |
| --- | --- |
| `make setup` | 環境を作ります（初回だけ） |
| `make up` | コンテナを起動します |
| `make upd` | コンテナを、バックグラウンドで起動します |
| `make stop` | コンテナを止めます |
| `make py/test` | テストを実行します |
| `make py/check` | コードを検査します |
| `make py/fix` | 検査の指摘のうち、自動で直せるものを直します |
| `make db/migrate` | まだないテーブルを作ります（データは残ります） |
| `make db/reset` | 全テーブルを削除して、作り直します（データは消えます） |

---

## Documents

| 文書 | 内容 |
| --- | --- |
| [Getting Started](./readme/01_GETTING_STARTED.md) | 環境構築の手順。必要なソフトウェアの用意から、動作の確認、うまくいかないときの対処まで |
| [Command](./readme/02_COMMAND.md) | すべてのコマンドの説明 |
| [Architecture](./readme/03_ARCHITECTURE.md) | コンテナの構成、プログラムの層、ディレクトリ構成、テストの仕組み、設定 |
| [Template](./readme/04_TEMPLATE.md) | ひな形として使う手順。自分のリポジトリの作り方、名前の変え方、機能の足し方 |
| [Development](./readme/05_DEVELOPMENT.md) | このリポジトリ自体を更新するときの決まり。ブランチ、作業の流れ、依存の更新、見本のブランチの保ち方 |
| [CLAUDE.md](./CLAUDE.md) | コードと文書の書き方の細かい決まり。Claude Code に作業を頼むときにも読み込まれます |
