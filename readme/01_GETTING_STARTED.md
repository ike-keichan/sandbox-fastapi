# Getting Started（環境構築）

手元のパソコンで、この API を動かせるようにするまでの手順です。上から順に進めてください。

- [0. この手順でできること](#0-この手順でできること)
- [1. 必要なソフトウェアを用意する](#1-必要なソフトウェアを用意する)
- [2. リポジトリを手元に持ってくる](#2-リポジトリを手元に持ってくる)
- [3. 環境を作る](#3-環境を作る)
- [4. コンテナを起動する](#4-コンテナを起動する)
- [5. 動作を確かめる](#5-動作を確かめる)
- [6. コンテナを止める](#6-コンテナを止める)
- [7. 2回目からの使い方](#7-2回目からの使い方)
- [8. 環境を作り直す](#8-環境を作り直す)
- [9. うまくいかないとき](#9-うまくいかないとき)

※ 特に指示がない場合、コマンドは、このリポジトリのフォルダの直下で実行してください。

※ コマンドの例の先頭にある `$` は、入力する行であることを表す記号です。`$` 自体は入力しません。`$` のない行は、表示される結果の例です。

---

## 0. この手順でできること

手順を終えると、次の状態になります。

- 手元のパソコンの中で、API のサーバーと、データベース（MySQL）が動いている。
- Web ブラウザで <http://localhost:8000/docs> を開くと、API の一覧が表示され、その場で API を試せる。

Python と MySQL は、Docker のコンテナの中で動きます。**手元のパソコンに、Python や MySQL をインストールする必要はありません。**

所要時間は、初回で10分ほどです（ほとんどが、ダウンロードの待ち時間です）。

---

## 1. 必要なソフトウェアを用意する

必要なものは、次の3つです。

| ソフトウェア | 用途 | 確認したバージョン |
| --- | --- | --- |
| Docker Desktop | コンテナを動かす | Docker 29.9.3、Docker Compose v5.7.0 |
| make | 長いコマンドを、短い名前で実行する | GNU Make 3.81 |
| Git | リポジトリを手元に持ってくる | 2.54.0 |

バージョンは、上の表より新しければ問題ありません。動作は macOS で確認しています。

### 1-1. Docker Desktop

1. [Docker Desktop の公式サイト](https://www.docker.com/products/docker-desktop/)から、自分のパソコンに合ったものをダウンロードして、インストールします。
   - Mac の場合は、チップの種類（Apple シリコンか、Intel か）を選びます。種類は、画面の左上のアップルメニューの「この Mac について」で確認できます。
2. インストールした Docker Desktop を起動します。
3. メニューバー（Windows の場合はタスクトレイ）にクジラのアイコンが出て、動きが止まれば、起動は完了です。

**Docker Desktop は、この先の手順のあいだ、起動したままにしてください。** 起動していないと、コマンドがエラーになります。

インストールできたかを、ターミナルで確認します。

```zsh
$ docker --version
Docker version 29.9.3, build 5457199

$ docker compose version
Docker Compose version v5.7.0
```

バージョンが表示されれば、準備できています。

### 1-2. make

macOS と Linux には、最初から入っています。次のコマンドで確認できます。

```zsh
$ make --version
GNU Make 3.81
```

macOS で「コマンドライン・デベロッパツールが必要です」という画面が出た場合は、「インストール」を押して、終わるまで待ってください。make と Git が、一緒に入ります。

Windows の場合は、WSL2（Windows の中で Linux を動かす仕組み）の中で作業してください。WSL2 の Ubuntu では、`sudo apt install make` で入ります。

### 1-3. Git

```zsh
$ git --version
git version 2.54.0 (Apple Git-157)
```

バージョンが表示されれば、準備できています。

---

## 2. リポジトリを手元に持ってくる

作業用のフォルダに移動して、リポジトリを複製します。

```zsh
$ git clone git@github.com:ike-keichan/sandbox-fastapi.git
$ cd sandbox-fastapi
```

このリポジトリをひな形にして、自分のリポジトリを作った場合は、URL を自分のリポジトリのものに読み替えてください（作り方は、[Template](./04_TEMPLATE.md) を参照）。

以降のコマンドは、すべてこの `sandbox-fastapi` フォルダの直下で実行します。

---

## 3. 環境を作る

次のコマンドを実行します。**初回だけ**行う手順です。

```zsh
$ make setup
```

このコマンドは、次の4つを順番に行います。

| 順番 | 行うこと | 補足 |
| --- | --- | --- |
| 1 | コンテナのビルド | Python のイメージをダウンロードして、API 用のコンテナを作ります |
| 2 | Python のパッケージのインストール | FastAPI などを、`.dockervenv` フォルダの中に入れます |
| 3 | コンテナの起動と、テーブルの作成 | MySQL のイメージをダウンロードして起動し、データベースにテーブルを作ります |
| 4 | コンテナの停止 | 作り終えたら、いったん止めます |

初回は、イメージのダウンロードがあるので、数分かかります。途中で止まっているように見えても、そのまま待ってください。

最後が次のような表示になれば、成功です。

```zsh
docker compose stop
 Container sandbox-fastapi-api-1 Stopping
 Container sandbox-fastapi-api-1 Stopped
 Container sandbox-fastapi-db-1 Stopping
 Container sandbox-fastapi-db-1 Stopped
```

途中に `INFO sqlalchemy.engine.Engine ...` という行がたくさん出ますが、これはテーブルを作るときの記録で、エラーではありません。

`Error` や `failed` という言葉が出て止まった場合は、「[9. うまくいかないとき](#9-うまくいかないとき)」を見てください。

---

## 4. コンテナを起動する

```zsh
$ make up
```

次のような表示が出て、ターミナルが止まった状態になれば、起動しています。

```zsh
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     Started reloader process [1] using WatchFiles
api-1  | INFO:     Started server process [9]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Application startup complete.
```

`Application startup complete.` が、起動が終わった合図です。

このターミナルには、API が受け取ったリクエストの記録が出続けます。**このターミナルは開いたままにして、ほかのコマンドを実行するときは、別のターミナルを開いてください。**

### バックグラウンドで起動する場合

ターミナルを1つで済ませたい場合は、`make up` の代わりに、次のコマンドを使います。

```zsh
$ make upd
```

起動が終わると、すぐにコマンドを入力できる状態に戻ります。記録は表示されません。記録を見たいときは、`docker compose logs -f api` を実行します。

---

## 5. 動作を確かめる

### 5-1. コンテナの状態を見る

別のターミナルで、次のコマンドを実行します。

```zsh
$ make ps
NAME                    IMAGE                 SERVICE   STATUS                    PORTS
sandbox-fastapi-api-1   sandbox-fastapi-api   api       Up 5 seconds              0.0.0.0:8000->8000/tcp
sandbox-fastapi-db-1    mysql:8.4             db        Up 10 seconds (healthy)   0.0.0.0:33306->3306/tcp
```

`api` と `db` の2行があり、どちらの `STATUS` も `Up` で始まっていれば、正常です（表示は、見やすいように一部を省いています）。

### 5-2. Web ブラウザで開く

<http://localhost:8000/docs> を開きます。

「Swagger UI」という、API の一覧の画面が表示されます。`GET /hello` を押し、「Try it out」→「Execute」の順に押すと、その場で API を呼び出せます。「Response body」に次の内容が出れば、正常です。

```json
{
  "message": "hello world!"
}
```

### 5-3. ターミナルから呼ぶ

```zsh
$ curl http://localhost:8000/hello
{"message":"hello world!"}
```

### 5-4. テストとコードの検査を実行する

開発を始める前に、テストと検査が通ることも確かめておきます。

```zsh
$ make py/test
============================== 1 passed in 0.43s ===============================

$ make py/check
docker compose exec api poetry run ruff check
All checks passed!
docker compose exec api poetry run ruff format --check
13 files already formatted
```

`passed` と `All checks passed!` が出れば、正常です。

以上で、環境構築は完了です。

---

## 6. コンテナを止める

作業を終えるときは、コンテナを止めます。

- `make up` で起動した場合：起動したターミナルで、`Ctrl + C` を押します。
- `make upd` で起動した場合：次のコマンドを実行します。

```zsh
$ make stop
```

止めても、データベースの中身は残ります。

---

## 7. 2回目からの使い方

`make setup` は、初回だけで足ります。2回目からは、次の流れになります。

1. Docker Desktop を起動する。
2. `make up`（または `make upd`）で、コンテナを起動する。
3. 作業する。`api/` の中のファイルを保存すると、API は自動で再起動します。コンテナを起動し直す必要はありません。
4. `Ctrl + C`（または `make stop`）で、コンテナを止める。

`pyproject.toml` や `Dockerfile` が変わったとき（`git pull` で更新を取り込んだあとなど）は、パッケージを入れ直します。

```zsh
$ make build
$ make py/install
```

そのほかのコマンドは、[Command](./02_COMMAND.md) にまとめています。

---

## 8. 環境を作り直す

動きがおかしくなったときや、最初の状態に戻したいときは、コンテナとデータベースの中身を消して、作り直せます。

```zsh
$ make downv
$ make setup
```

**`make downv` を実行すると、データベースに保存したデータは、すべて消えます。**

---

## 9. うまくいかないとき

### `Cannot connect to the Docker daemon` と表示される

Docker Desktop が起動していません。Docker Desktop を起動して、クジラのアイコンの動きが止まってから、もう一度コマンドを実行してください。

### `port is already allocated` や `address already in use` と表示される

このリポジトリが使うポート（`8000` と `33306`）を、ほかのソフトウェアが使っています。

- ほかのプロジェクトのコンテナが動いている場合は、そちらを止めてください。
- 止められない場合は、[docker-compose.yaml](../docker-compose.yaml) の `ports` の、左側の数字を変えます。たとえば `8000:8000` を `8001:8000` にすると、<http://localhost:8001/docs> で開けるようになります。

### `make setup` の途中で止まった

ダウンロードの途中で、通信が切れた可能性があります。もう一度 `make setup` を実行してください。途中まで終わった分は、やり直されません。

### <http://localhost:8000/docs> が開けない

1. `make ps` で、`api` の `STATUS` が `Up` になっているかを確認します。
2. `Up` でない場合は、記録を見て、エラーの内容を確認します。

   ```zsh
   $ docker compose logs api
   ```

3. `ModuleNotFoundError`（パッケージが見つからない）と出ている場合は、パッケージを入れ直します。

   ```zsh
   $ make py/install
   $ make restart
   ```

### データベースにつながらないエラーが出る

`make ps` で、`db` の `STATUS` に `(healthy)` と出ているかを確認します。出ていない場合は、MySQL の起動が終わっていません。少し待ってから、`make restart` を実行してください。

### それでも直らない

「[8. 環境を作り直す](#8-環境を作り直す)」の手順で、最初から作り直してください。
