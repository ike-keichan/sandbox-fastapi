# 開発の進め方

このリポジトリ自体を更新するときの決まりごと。1人で開発する前提で書いている。

## 基本の考え方

- `main` は、いつでもひな形として複製できる状態に保つ。壊れた状態を入れない。
- 変更は作業用のブランチで行い、プルリクエストを通して `main` に入れる。プルリクエストを作ると自動テストが動くので、壊れた変更が入るのを防げる。
- 構成の違うものは、`example/` で始まるブランチとして残す。

## ブランチ

| ブランチ | 寿命 | 使いみち |
| --- | --- | --- |
| `main` | 残し続ける | 最小の形のひな形。直接はコミットしない |
| `example/<内容>` | 残し続ける | `main` に何かを足した見本。または、別の構成を試した結果 |
| `feature/<内容>` | マージまで | 機能の追加や変更 |
| `fix/<内容>` | マージまで | 不具合の修正 |
| `docs/<内容>` | マージまで | 文書だけの変更 |
| `dependabot/...` | マージまで | Dependabot が自動で作る。手では作らない |

`<内容>` は、英小文字とハイフンで短く書く（例：`feature/add-health-check`、`example/postgresql`）。

マージまでのブランチは、マージすると GitHub 側で自動で消える設定にしてある。

## 変更を入れる手順

1. `main` を最新にして、ブランチを作る。

   ```sh
   git switch main
   git pull
   git switch -c feature/<内容>
   ```

2. 変更する。
3. 検査とテストを実行する（コンテナの起動中に使う）。

   ```sh
   make py/fix
   make py/check
   make py/test
   ```

4. コミットして push し、プルリクエストを作る。

   ```sh
   git push -u origin feature/<内容>
   gh pr create --fill
   ```

5. プルリクエストの自動テストが緑になるのを待つ。
6. マージして、手元を片付ける。

   ```sh
   gh pr merge --merge
   git switch main
   git pull
   git branch -d feature/<内容>
   ```

7. `main` に入れた変更を、`example/` のブランチにも取り込む（「見本のブランチを保つ」を参照）。

## コミット

- 1つのコミットには、1つの変更だけを入れる。
- メッセージは、種類を先頭に付けて、日本語で1行に書く。

| 種類 | 使う場面 | 例 |
| --- | --- | --- |
| `add:` | 機能やファイルの追加 | `add: ヘルスチェックの API を追加。` |
| `update:` | 既存の機能の変更、依存の更新 | `update: Python を 3.15 に更新。` |
| `fix:` | 不具合の修正 | `fix: 期日が保存されない問題を修正。` |
| `docs:` | 文書だけの変更 | `docs: README に構成の図を追加。` |

## 自動テスト

[.github/workflows/test.yml](../.github/workflows/test.yml) で、次の順に実行する。

1. `make setup`（ビルド、パッケージのインストール、テーブルの作成）
2. コンテナの起動
3. `make py/check`（コードの検査）
4. `make py/test`（テスト）
5. `make db/migrate` と、API の呼び出し（実際の MySQL につないだ状態での確認）

動くのは、プルリクエストを作ったときと、`main` か `example/` のブランチに push したときである。

失敗したときは、GitHub の「Actions」のページで、失敗した手順のログを見る。最後の手順で、コンテナのログも出力される。

## 依存の更新

毎週月曜の朝に、Dependabot が更新をプルリクエストで知らせる。対象は、次の4つである。

| 対象 | 記録されている場所 |
| --- | --- |
| Python のパッケージ | `pyproject.toml`、`poetry.lock` |
| Python のイメージ | `Dockerfile` |
| MySQL のイメージ | `docker-compose.yaml` |
| GitHub Actions のアクション | `.github/workflows/` |

自動テストが緑なら、マージしてよい。赤の場合は、新しい版で書き方が変わっていることが多い。プルリクエストのブランチを手元に持ってきて直すか、プルリクエストを閉じて、`feature/` のブランチで更新と修正をまとめて行う。

### バージョンの方針

- **Python**：最新の安定版を使う。新しい版が出た直後は、対応していないライブラリがあるので、ビルドが通ってから上げる。`Dockerfile` のイメージ、`pyproject.toml` の `requires-python`、`ruff.toml` の `target-version` の3か所をそろえる。
- **MySQL**：長期サポート版（LTS）を使う。短い周期で出る版（Innovation）には上げない。Dependabot は、MySQL のメジャーバージョンの更新を知らせない設定にしてある。次の長期サポート版が出たら、`docker-compose.yaml` を手で書き換える。
- **Poetry**：`Dockerfile` で、版を固定している。上げるときは、`poetry.lock` も作り直す。

### 手で更新する

```sh
make py/update          # pyproject.toml の範囲内で、最新にする
make py/add TARGET=fastapi@latest   # 範囲を超えて、最新版にする
make py/check
make py/test
```

## 見本のブランチを保つ

`example/` のブランチは、`main` に内容を足したものである。`main` を更新したら、取り込んで最新に保つ。

```sh
git switch example/task-api
git pull
git merge main
make py/check
make py/test
git push
```

衝突を減らすために、次の決まりにしている。

- `README.md` は、どのブランチでも同じ内容にする。ブランチごとの説明は、`docs/<ブランチの内容>.md` に書く。
- 見本のブランチでは、`main` にあるファイルの書き換えを、必要な分だけにとどめる（ルーターを登録する `api/main.py` など）。

## 見本のブランチを足す

1. `main` からブランチを作る。

   ```sh
   git switch main
   git pull
   git switch -c example/<内容>
   ```

2. 内容を足す。ブランチの説明を、`docs/<内容>.md` に書く。
3. 検査とテストが通ることを確かめて、push する。

   ```sh
   git push -u origin example/<内容>
   ```

4. `main` の `README.md` の「ブランチ」の表に、1行足す（これは、ふつうの手順でプルリクエストにする）。そのあと、`main` を各 `example/` のブランチに取り込む。

見本のブランチは、`main` にはマージしない。
