# Architecture（構成）

このリポジトリが、どういう部品でできていて、どこに何を書くのかの説明です。

- [1. コンテナの構成](#1-コンテナの構成)
- [2. プログラムの層](#2-プログラムの層)
- [3. ディレクトリ構成](#3-ディレクトリ構成)
- [4. テストの仕組み](#4-テストの仕組み)
- [5. 設定](#5-設定)
- [6. 注意点](#6-注意点)

---

## 1. コンテナの構成

Docker Compose で、2つのコンテナを動かします。定義は、[docker-compose.yaml](../docker-compose.yaml) にあります。

```mermaid
flowchart LR
    browser["Web ブラウザ<br>curl など"]
    subgraph compose["Docker Compose"]
        api["api<br>Python + FastAPI + Uvicorn"]
        db[("db<br>MySQL")]
    end
    browser -- "localhost:8000" --> api
    api -- "db:3306" --> db
```

| コンテナ | 中身 | 手元からつなぐ先 |
| --- | --- | --- |
| `api` | Python と FastAPI。[Dockerfile](../Dockerfile) から作ります | `http://localhost:8000` |
| `db` | MySQL。公式のイメージを、そのまま使います | `localhost:33306` |

知っておくとよい点は、次の3つです。

- **ファイルを保存すると、自動で再起動します。** `api` のコンテナは、リポジトリのフォルダをそのまま読み込んでいます。`api/` の中のファイルを保存すると、サーバーが自動で再起動し、変更がすぐ反映されます。
- **パッケージは、`.dockervenv` フォルダに入ります。** コンテナを作り直しても、パッケージを入れ直さずに済むようにするためです。このフォルダは、Git の管理の対象から外しています。パッケージは、イメージの中ではなく、このフォルダにだけ入ります。
- **データベースの中身は、コンテナを止めても残ります。** Docker のボリュームに保存しているためです。消すときは、`make downv` を使います。

`api` は、`db` の準備が終わるのを待ってから起動します（`docker-compose.yaml` の `healthcheck` と `depends_on`）。

---

## 2. プログラムの層

API のプログラムは、役割ごとに4つの層に分けています。リクエストは、上から順に流れます。

```mermaid
flowchart TD
    request["リクエスト"] --> routers
    routers["routers<br>パスと、リクエストの受け取り"] --> cruds
    cruds["cruds<br>データベースの読み書き"] --> models
    models["models<br>テーブルの定義"] --> database[("MySQL")]
    schemas["schemas<br>リクエストとレスポンスの形"] -.-> routers
```

| 層 | 置き場所 | 役割 | 使うライブラリ |
| --- | --- | --- | --- |
| routers | `api/routers/` | パスとメソッドを決め、リクエストを受け取って、レスポンスを返します。処理そのものは書かず、cruds を呼びます | FastAPI |
| schemas | `api/schemas/` | リクエストとレスポンスの形を決めます。値の検査も、ここで行われます | Pydantic |
| cruds | `api/cruds/` | データベースの読み書きを行います | SQLAlchemy |
| models | `api/models/` | テーブルの形を決めます | SQLAlchemy |

層を分けている理由は、変更の影響を小さくするためです。たとえば、レスポンスの項目を変えるときは schemas だけ、SQL の組み立てを変えるときは cruds だけを直せば済みます。

どの層も、機能ごとのディレクトリ（`hello/`、`task/` など）に分けます。機能を1つ足すときは、必要な層それぞれに、同じ名前のディレクトリを作ります。

```
api/
├── routers/
│   ├── hello/index.py
│   └── task/index.py      ← 足す機能
├── schemas/
│   └── task/index.py
├── cruds/
│   └── task/index.py
└── models/
    └── task/index.py
```

`main` ブランチには、`routers/hello/` と `schemas/hello/` だけが入っています。`hello` はデータベースを使わないので、`cruds/` と `models/` は空です。4つの層がそろった例は、`example/task-api` ブランチにあります。

---

## 3. ディレクトリ構成

| ディレクトリ・ファイル | 内容 |
| --- | --- |
| `api/main.py` | 入口です。FastAPI のアプリケーションを作り、ルーターを登録します |
| `api/routers/` | routers の層 |
| `api/schemas/` | schemas の層 |
| `api/cruds/` | cruds の層 |
| `api/models/` | models の層 |
| `api/db.py` | データベースへの接続です。接続先の組み立て、セッションの用意、モデルの基底クラス（`Base`）があります |
| `api/migrate_db.py` | テーブルを作るスクリプトです。`make db/migrate` と `make db/reset` で実行されます |
| `tests/conftest.py` | テストの共通の準備（テスト用のデータベースと、HTTP のクライアント） |
| `tests/test_<機能名>.py` | 機能ごとのテスト |
| `scripts/smoke.sh` | 起動した API を、実際に呼んで確かめるスクリプト。自動テストから実行されます |
| `Dockerfile` | `api` のコンテナの作り方 |
| `docker-compose.yaml` | `api` と `db` のコンテナの定義 |
| `Makefile` | よく使うコマンドをまとめたもの |
| `pyproject.toml` | 依存するパッケージと、pytest の設定 |
| `poetry.lock` | 実際にインストールされるパッケージの、正確なバージョンの記録 |
| `ruff.toml` | Ruff（コードの検査と整形）の設定 |
| `.github/workflows/test.yml` | 自動テストの設定 |
| `.github/dependabot.yml` | Dependabot（依存の更新の通知）の設定 |
| `readme/` | このリポジトリの文書 |

---

## 4. テストの仕組み

テストは、[tests/](../tests/) にあります。機能ごとに、`test_<機能名>.py` というファイルに分けます。どのテストでも使う準備は、[tests/conftest.py](../tests/conftest.py) にまとめています。

- **API を呼ぶ形で書きます。** 関数を直接呼ばずに、HTTP のクライアント（HTTPX）でリクエストを送って、レスポンスを確かめます。
- **MySQL の代わりに、メモリ上の SQLite を使います。** FastAPI の仕組み（`dependency_overrides`）で、データベースへの接続だけを差し替えています。そのため、テストはデータベースの中身に影響せず、テストのたびに空の状態から始まります。
- **非同期のテストです。** pytest-asyncio を使っています。設定は、`pyproject.toml` の `[tool.pytest.ini_options]` にあります。

SQLite と MySQL では、動きが違う部分があります。たとえば、SQLite は、文字列の長さの上限を超えていても保存できてしまいます。そのため、MySQL につないだ状態での確認を、[scripts/smoke.sh](../scripts/smoke.sh) で別に行っています。このスクリプトは、起動した API を `curl` で呼ぶもので、自動テスト（GitHub Actions）から実行されます。機能を足したら、その機能の API を呼ぶ行を足してください。

---

## 5. 設定

データベースの接続先は、環境変数で変えられます。`docker-compose.yaml` の `api` の `environment` に書きます。

| 環境変数 | 既定の値 | 内容 |
| --- | --- | --- |
| `DB_HOST` | `db` | ホスト名 |
| `DB_PORT` | `3306` | ポート番号 |
| `DB_NAME` | `demo` | データベースの名前 |
| `DB_USER` | `root` | ユーザー名 |
| `DB_PASSWORD` | （空） | パスワード。`@` や `/` などの記号が入っていても使えます |
| `DB_ECHO` | `false` | `true` にすると、実行した SQL を記録に出します。`docker-compose.yaml` では、`true` にしています |

読み込んでいるのは、[api/db.py](../api/db.py) です。

---

## 6. 注意点

- **データベースは、パスワードなしの root でつなぐ設定です。** 手元で試すためのものです。公開する環境では、ユーザーとパスワードを設定してください。
- **`make db/migrate` は、まだないテーブルを作るだけの簡単なものです。** すでにあるテーブルの形は変えられません。データを残したままテーブルの形を変えたい場合は、Alembic などのマイグレーションの道具を足してください。
- **API とデータベースには、手元のパソコンからしかつなげません。** `docker-compose.yaml` の `ports` に、`127.0.0.1` を付けているためです。外すと、同じネットワークのほかの機器から、パスワードなしでデータベースに入れてしまいます。
- **手元から MySQL につなぐときのポートは、`33306` です。** コンテナの中では `3306` です。手元の MySQL と重ならないように、ずらしています。
