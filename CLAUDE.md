# CLAUDE.md

このリポジトリで作業するときの決まり。Claude Code が読み込むほか、人が書くときの基準にもする。

README と `readme/` には、使う人に向けた説明を書く。ここには、書く人に向けた細かい決まりを書く。

## このリポジトリの目的

FastAPI による Web API の技術検証と、プロジェクトのひな形を兼ねている。

- `main` は、最小の形のひな形である。**いつ複製されても動く状態**を保つ。
- `example/<内容>` は、`main` に何かを足した見本である。`main` にはマージしない。
- ひな形なので、**足すより、足さない**を選ぶ。特定の用途にしか使わない機能、設定、ライブラリは、`main` に入れない。入れたい場合は、`example/` のブランチにする。

## 文書の置き場所

| 文書 | 内容 |
| --- | --- |
| `README.md` | 入口。概要、ブランチ、バージョン、主なコマンド、文書の一覧だけを書く |
| `readme/01_GETTING_STARTED.md` | 環境構築の手順 |
| `readme/02_COMMAND.md` | すべてのコマンド |
| `readme/03_ARCHITECTURE.md` | 構成 |
| `readme/04_TEMPLATE.md` | ひな形として使う手順 |
| `readme/05_DEVELOPMENT.md` | ブランチと作業の流れ |
| `readme/EXAMPLE_<内容>.md` | `example/` のブランチだけに置く、そのブランチの説明 |
| `CLAUDE.md` | このファイル |

作業を始める前に、`readme/03_ARCHITECTURE.md` と `readme/05_DEVELOPMENT.md` を読む。

## 作業の進め方

### ブランチとコミット

- `main` に直接コミットしない。`feature/`、`fix/`、`docs/` のどれかのブランチを作る。
- `example/` のブランチだけにある内容を直すときは、そのブランチに直接コミットしてよい。
- 1つのコミットには、1つの変更だけを入れる。
- コミットメッセージは、`add:`、`update:`、`fix:`、`docs:` のどれかで始め、日本語で1行に書き、「。」で終える（例：`add: ヘルスチェックの API を追加。`）。
- コミットメッセージとプルリクエストに、ツールが生成したことを示す行（`Co-Authored-By` など）を入れない。
- push、プルリクエストのマージ、ブランチの削除は、人が行う。Claude は、コミットまで行い、実行するコマンドを伝える。

### 変更したら、必ず確かめる

コンテナを起動した状態で、次の3つを実行する。どれかが失敗している状態で、作業を終えたことにしない。

```sh
make py/fix
make py/check
make py/test
```

次のものを変えたときは、追加で確かめる。

| 変えたもの | 確かめること |
| --- | --- |
| `Dockerfile`、`docker-compose.yaml`、`pyproject.toml`、`Makefile` | `make downv` のあとに `make setup` と `make upd` が通り、`curl http://localhost:8000/hello` が応答する |
| モデル（`api/models/`） | `make db/reset` が通り、実際の MySQL につないだ状態で API が動く（`bash scripts/smoke.sh`） |
| API の追加や変更 | `scripts/smoke.sh` に、その API を呼ぶ行を足して、`bash scripts/smoke.sh` が通る |
| `.github/workflows/` | プルリクエストを作って、GitHub Actions が緑になる |

テストは、データベースを SQLite で代用している。SQLite は、文字列の長さの上限などを検査しないので、テストが通っても、MySQL ではエラーになることがある。データベースに関わる変更は、必ず実際の MySQL でも確かめる。

確かめられなかったことは、確かめられなかったと伝える。

### `main` を変えたあと

`main` に入った変更は、`example/` のブランチに取り込む（`git merge main`）。取り込んだあと、そのブランチでも検査とテストを実行する。手順は、`readme/05_DEVELOPMENT.md` の「3-6」にある。

## コードの書き方

### 層

プログラムは、`routers`、`schemas`、`cruds`、`models` の4つの層に分ける。

- **routers**：パス、メソッド、リクエストの受け取り、レスポンスの返却だけを書く。データベースを直接さわらず、cruds の関数を呼ぶ。「見つからなければ 404」のような、HTTP に関わる判断は、ここに書く。
- **schemas**：Pydantic のモデル。リクエスト用とレスポンス用を分ける。リクエスト用には、利用者が決められる項目だけを入れる。
- **cruds**：データベースの読み書き。`HTTPException` を投げない。見つからないときは、`None` を返す。コミットのあとに、`refresh` を呼ぶ必要はない（セッションを、`expire_on_commit=False` で作っているため）。すでにセッションにあるオブジェクトを、`db.add` し直す必要もない。
- **models**：SQLAlchemy のモデル。`api.db.Base` を継承する。

依存の向きは、routers → cruds → models の一方向にする。cruds から routers を読み込まない。

### ファイルの置き方

- どの層も、機能ごとのディレクトリに分け、ファイル名は `index.py` にする（例：`api/routers/task/index.py`）。
- 1つの機能の中で、種類の違う操作を分けるときは、ファイルを足す（例：`api/routers/task/done.py`）。分けたルーターは、その機能の `index.py` の最後で取り込む。
- 読み込むときは、層が分かる別名を付ける。

  ```python
  import api.cruds.task.index as task_crud
  import api.models.task.index as task_model
  import api.schemas.task.index as task_schema
  ```

- 機能のディレクトリには、空の `__init__.py` を置く。
- ルーターを足したら、`api/main.py` に登録する。モデルを足したら、`api/models/__init__.py` で読み込む（読み込まないと、テーブルが作られない）。このとき、別名を付けない（`import api.models.task.index  # noqa: F401`）。`from api.models.task import index as task` と書くと、`api.models.task` という名前を上書きしてしまい、ほかの場所から読み込めなくなる。

### 書式と型

- 書式と規則は、Ruff に従う（`ruff.toml`）。1行は100文字まで。手で整えず、`make py/fix` を使う。
- 規則を無効にする場合（`# noqa`）は、理由が分かるコメントを添える。`ruff.toml` の `ignore` を増やすのは、最後の手段にする。
- 関数の引数と戻り値に、型を書く。ルーターの関数と、テストの関数にも書く。
- 型は、新しい書き方を使う（`str | None`、`list[Task]`）。`Optional`、`List` は使わない。
- データベースの処理は、非同期で書く（`async def`、`await`、`AsyncSession`）。同期のエンジンを使うのは、`api/migrate_db.py` だけである。

### コメントと docstring

- コメントと docstring は、日本語で書く。
- cruds の関数には、docstring を書く。1行目に何をするか、続けて `Args:` と `Returns:` を書く。

  ```python
  async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
      """
      タスクの取得

      Args:
          db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
          task_id (int): 取得したいタスクのID。

      Returns:
          task_model.Task | None: 指定されたIDのタスクのオブジェクト。存在しない場合はNone。
      """
  ```

- routers の関数には、docstring の代わりに、直前に1行のコメントを書く（例：`# タスク一覧の取得`）。
- ルーターには、`tags` と `response_model` を付ける。Swagger UI の表示が、これで決まる。`tags` と、パスの共通の部分は、`APIRouter(prefix="/tasks", tags=["task"])` でまとめて付ける。
- 状態コードは、内容に合わせる。作成は 201（`status_code=status.HTTP_201_CREATED`）、本文を返さない削除は 204、見つからないときは 404、値が不正なときは 422 にする。
- データベースのセッションは、`api.db.DbSession` を引数の型に書いて受け取る（`db: DbSession`）。`db: AsyncSession = Depends(get_db)` とは書かない。
- 複数のルーターで同じ前処理をするときは、依存関係（`Depends`）にまとめる。たとえば、「パスの ID から1件を取得して、なければ 404」は、関数にして、`Annotated[..., Depends(...)]` の型として使う。
- 同じ操作を何度呼んでも、結果が同じになるようにする（PUT と DELETE）。「呼ぶたびに切り替わる」操作は、作らない。再送されたときに、結果が逆になる。
- コードを読めば分かることは、コメントにしない。なぜそうしているかを書く。

### 新しい版の書き方を使う

古い書き方は、警告やエラーになる。次の書き方を使う。

| 対象 | 使う書き方 | 使わない書き方 |
| --- | --- | --- |
| Pydantic：モデルから辞書を作る | `model_dump()` | `dict()` |
| Pydantic：モデルの設定 | `model_config = ConfigDict(...)` | `class Config:` |
| Pydantic：ORM から読み込む設定 | `from_attributes=True` | `orm_mode = True` |
| Pydantic：項目の例 | `Field(examples=["..."])` | `Field(example="...")` |
| SQLAlchemy：非同期のセッション | `async_sessionmaker` | `sessionmaker(class_=AsyncSession)` |
| SQLAlchemy：基底クラス | `class Base(DeclarativeBase)` | `declarative_base()` |
| SQLAlchemy：主キーで1件を取り出す | `await db.get(Task, task_id)` | `select(...)` と `result.first()[0]` |
| SQLAlchemy：複数件を取り出す | `await db.scalars(statement)` | `(await db.execute(statement)).all()` |
| SQLAlchemy：絞り込み | `select(Task).where(...)` | `select(Task).filter(...)` |
| SQLAlchemy：モデルの列 | `id: Mapped[int] = mapped_column(primary_key=True)` | `id = Column(Integer, primary_key=True)` |
| SQLAlchemy：接続先の URL | `URL.create(...)` | 文字列の連結（記号入りのパスワードで壊れる） |
| FastAPI：依存関係 | `Annotated[AsyncSession, Depends(get_db)]` | `db: AsyncSession = Depends(get_db)` |
| HTTPX：テスト用のクライアント | `AsyncClient(transport=ASGITransport(app=app))` | `AsyncClient(app=app)` |
| Starlette：状態コード 422 | `HTTP_422_UNPROCESSABLE_CONTENT` | `HTTP_422_UNPROCESSABLE_ENTITY` |

テストの実行で警告が出たら、放置せずに、新しい書き方に直す。

## テストの書き方

- テストは、機能ごとに `tests/test_<機能名>.py` に書く。どのテストでも使う準備は、`tests/conftest.py` に置く。
- テストは、API を呼ぶ形で書く。cruds の関数を直接呼ばず、`async_client` でリクエストを送って、状態コードとレスポンスの中身を確かめる。状態コードだけでなく、本文も確かめる。
- API を足したら、成功する場合と、失敗する場合（見つからない、値が不正）の両方のテストを書く。値の検査は、境目（上限ちょうどと、上限を1つ超えた値）を確かめる。失敗する場合は、データが変わっていないことも確かめる。
- テストは、メモリ上の SQLite で動く。テストごとに空の状態から始まるので、ほかのテストが作ったデータに頼らない。必要なデータは、そのテストの中で作る。
- 状態コードは、数値ではなく、`starlette.status` の定数で書く。
- 入力だけが違うテストは、`@pytest.mark.parametrize` でまとめる。
- 非同期のテストに、`@pytest.mark.asyncio` を付ける必要はない（`pyproject.toml` で、自動にしている）。

## 設定ファイルを変えるとき

### パッケージ

- パッケージの追加と更新は、`make py/add`、`make py/add-d`、`make py/update` で行う。`pyproject.toml` と `poetry.lock` を、手で書き換えない。
- `poetry.lock` は、コミットする。
- 開発にしか使わないもの（テスト、検査）は、`make py/add-d` で開発用として追加する。
- パッケージを足す前に、標準ライブラリか、すでに入っているパッケージで足りないかを確かめる。

### バージョン

- Python のバージョンは、`Dockerfile`、`pyproject.toml` の `requires-python`、`ruff.toml` の `target-version` の3か所に書いてある。変えるときは、3か所をそろえる。
- MySQL は、長期サポート版を使う。短い周期で出る版には上げない。
- バージョンを変えたら、`README.md` の「Tool Versions」の表も直す。

### Makefile

- コマンドを足したら、`.PHONY` の行にも足し、`readme/02_COMMAND.md` に説明を書く。主なコマンドなら、`README.md` の表にも足す。
- コマンドの名前は、対象を先に書く（`py/test`、`db/migrate`）。
- コマンドの直前に、何をするかを日本語のコメントで書く。

### データベース

- 接続先は、環境変数（`DB_HOST` など）から読み込む。コードに、接続先やパスワードを直接書かない。
- 文字列の長さの上限のように、データベースが決めている制限は、リクエストの検査（schemas）にも同じ値を書く。書かないと、データベースのエラーが、そのまま 500 になる。同じ値を2か所に書かずに済むように、モデルの側に定数を置いて、schemas から読み込む。
- `make db/migrate` は、まだないテーブルを作るだけで、データは消さない。`make db/reset` は、全テーブルを消して作り直す。
- パスワードや鍵を、リポジトリに入れない。必要になったら、`.env` を使い、`.gitignore` に入っていることを確かめる。

## 文書の書き方

- `README.md` と `readme/` は、です・ます調で書く。`CLAUDE.md` は、である調で書く。
- `README.md` には、細かい説明を書かない。入口として、`readme/` の文書に案内する。
- `README.md` と、`readme/` の番号つきの文書は、**どのブランチでも同じ内容にする**。ブランチごとの説明は、`readme/EXAMPLE_<内容>.md` に書く。こうしないと、`main` を取り込むたびに衝突する。
- 手順には、実行するコマンドだけでなく、**成功したときに何が表示されるか**を書く。表示の例は、実際に実行したものを使う。想像で書かない。
- コマンドの例は、`zsh` のコードブロックに書き、入力する行の先頭に `$` を付ける。
- 読む人が知らないかもしれない言葉は、最初に出たところで説明する。
- コードを変えたら、関係する文書も同じコミットか、同じプルリクエストで直す。とくに、次の対応に注意する。

  | 変えたもの | 直す文書 |
  | --- | --- |
  | コマンド（`Makefile`） | `readme/02_COMMAND.md`、`README.md` の「Command」 |
  | ディレクトリやファイルの構成 | `readme/03_ARCHITECTURE.md` |
  | 環境構築の手順、表示される内容 | `readme/01_GETTING_STARTED.md` |
  | 名前や設定値（`demo` など） | `readme/04_TEMPLATE.md` の「名前を変える」 |
  | バージョン | `README.md` の「Tool Versions」 |
  | ブランチの追加 | `README.md` の「Branch」 |

## やらないこと

- `main` に、見本の機能（タスクの API など）を入れない。
- 動作を確かめていない変更を、確かめたことにしない。
- 頼まれていない機能の追加や、大きな書き換えをしない。気づいた問題は、直す前に伝える。
- `.dockervenv/`、`.venv/`、`__pycache__/` などの生成物を、コミットしない。
