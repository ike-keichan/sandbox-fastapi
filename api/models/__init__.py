# モデルを足したら、ここで読み込む。読み込まないと、テーブルが作られない。
# 「from ... import index as task」のように別名を付けると、api.models.task という名前を
# 上書きしてしまい、ほかの場所から読み込めなくなる。別名を付けずに、import だけを書く。
import api.models.task.index  # noqa: F401
