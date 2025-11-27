import time
import functools

def retry(retries=3, exceptions=(Exception,), delay=0.5, backoff=2.0):
    """
    関数を最大retry回数まで実行し、エラーが発生した場合は指定された時間間隔で再実行するデコレータ。
    Args:
        retries: 最大実行回数
        exceptions: エラーを再実行する例外クラスのタプル
        delay: 最初の再実行までの待ち時間
        backoff: 待ち時間の倍率
    Returns:
        Callable: デコレータ適用後の関数
    Example:
        ```python
        @retry(retries=3, exceptions=(Exception,), delay=0.5, backoff=2.0)
        def sample_function():
            print("sample_function")
            raise Exception("sample_exception")
        ```


    """
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == retries - 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff
        return wrapper
    return deco

