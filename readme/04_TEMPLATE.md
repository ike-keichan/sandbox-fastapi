# Template（ひな形として使う）

このリポジトリをもとに、新しいプロジェクトを始める手順です。

- [1. 自分のリポジトリを作る](#1-自分のリポジトリを作る)
- [2. 手元に持ってきて、動くことを確かめる](#2-手元に持ってきて動くことを確かめる)
- [3. 名前を変える](#3-名前を変える)
- [4. 機能を足す](#4-機能を足す)
- [5. 不要なものを消す](#5-不要なものを消す)

---

## 1. 自分のリポジトリを作る

1. GitHub で、[このリポジトリのページ](https://github.com/ike-keichan/sandbox-fastapi)を開きます。
2. 右上の「Use this template」を押し、「Create a new repository」を選びます。
3. リポジトリの名前と、公開範囲（Public か Private）を決めます。
4. どのブランチから始めるかで、次のどちらかを選びます。

   | 始めたい内容 | 「Include all branches」 | 作ったあとに使うブランチ |
   | --- | --- | --- |
   | 最小の形（API は `GET /hello` だけ） | チェックしない | `main` |
   | タスクを管理する API の見本つき | チェックする | `example/task-api` |

   迷ったら、最小の形で始めてください。見本は、このリポジトリの `example/task-api` ブランチを、あとからいつでも見られます。

5. 「Create repository」を押します。

「Use this template」で作ったリポジトリは、このリポジトリの履歴を引き継ぎません。最初のコミットが1つだけある状態から始まります。

---

## 2. 手元に持ってきて、動くことを確かめる

名前を変える前に、まず、そのままで動くことを確かめます。

[Getting Started](./01_GETTING_STARTED.md) の手順を、「2. リポジトリを手元に持ってくる」から進めてください。`git clone` の URL は、いま作った自分のリポジトリのものを使います。

<http://localhost:8000/docs> が開けたら、次へ進みます。

---

## 3. 名前を変える

`sandbox-fastapi` や `demo` という名前を、自分のプロジェクトの名前に変えます。

| ファイル | 変える場所 | いまの値 |
| --- | --- | --- |
| `pyproject.toml` | `name` | `sandbox-fastapi` |
| `pyproject.toml` | `description` | `FastAPI による Web API のひな形` |
| `docker-compose.yaml` | `MYSQL_DATABASE`（`db` の `environment`） | `demo` |
| `docker-compose.yaml` | `DB_NAME`（`api` の `environment`） | `demo` |
| `Makefile` | `db/repl` の最後の `demo` | `demo` |
| `README.md`、`readme/` | 題名、説明、URL | |

データベースの名前を変えた場合は、古い名前のデータベースが残っているので、環境を作り直します。

```zsh
$ make downv
$ make setup
$ make up
```

コンテナの名前（`sandbox-fastapi-api-1` など）は、フォルダの名前から自動で付きます。手で変える必要はありません。

---

## 4. 機能を足す

`task`（タスク）という機能を足す場合を例に、書く順番を説明します。完成した形は、[`example/task-api` ブランチ](https://github.com/ike-keichan/sandbox-fastapi/tree/example/task-api)にあります。各層の役割は、[Architecture](./03_ARCHITECTURE.md) を参照してください。

| 順番 | 書くファイル | 書くこと |
| --- | --- | --- |
| 1 | `api/models/task/index.py` | テーブルの定義 |
| 2 | `api/models/__init__.py` | 1 で作ったモデルを読み込む1行（ファイルの中に、書き方をコメントで示しています） |
| 3 | `api/schemas/task/index.py` | リクエストとレスポンスの形 |
| 4 | `api/cruds/task/index.py` | データベースの読み書き |
| 5 | `api/routers/task/index.py` | パスと、リクエストの受け取り |
| 6 | `api/main.py` | 5 で作ったルーターを登録する2行 |
| 7 | `tests/test_task.py` | テスト |
| 8 | `scripts/smoke.sh` | 起動した API を呼んで確かめる行 |

書き終えたら、テーブルを作って、確かめます。

```zsh
$ make db/migrate
$ make py/fix
$ make py/check
$ make py/test
```

<http://localhost:8000/docs> を開くと、足した API が一覧に出ます。

新しいディレクトリを作るときは、ほかの機能と同じ構成にしてください。`<機能名>/index.py` と、空の `<機能名>/__init__.py` を置きます。

---

## 5. 不要なものを消す

自分の機能ができたら、見本の `hello` は消してかまいません。

| 消すもの | 場所 |
| --- | --- |
| `hello` のルーター | `api/routers/hello/` |
| `hello` の登録 | `api/main.py` の `hello` の2行 |
| `hello` のスキーマ | `api/schemas/hello/` |
| `hello` のテスト | `tests/test_hello.py` |
| 起動の確認の呼び出し | `scripts/smoke.sh` の `curl ... /hello` の行（自分の API のパスに変える） |

`readme/` の文書も、自分のプロジェクトに合わせて書き換えてください。
