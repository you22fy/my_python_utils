# my_python_utils

自作のpythonユーティリティライブラリ

## インストール
```bash
# pip
pip install git+https://github.com/your_username/my_python_utils

# uv
uv add git+https://github.com/your_username/my_python_utils
```

## 使用例
### decorators

#### monitoring
実行の終了と失敗をモニタリングする。完了時に指定したプラットフォームへ通知を送信する。
関数自体の実行時間も合わせて計測して通知する。

```python
from my_python_utils import monitoring

@monitoring(platform="discord", webhook_url="~~~discord_webhook_url~~~")
def hoge_function():
    ...
```

#### retry
指定した回数まで実行し、エラーが発生した場合は指定された時間間隔で再実行する。

```python
from my_python_utils import retry

@retry(retries=3, exceptions=(Exception,), delay=0.5, backoff=2.0)
def hoge_function():
    ...
```

#### rate_limit
指定された期間に指定された回数まで実行を許可する。
指定された回数実行後は指定された期間待つ。

```python
from my_python_utils import rate_limit

@rate_limit(calls=10, period=60)
def hoge_function():
    ...
```