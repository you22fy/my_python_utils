import time
import functools
from collections import deque

def rate_limit(calls, period):
    """
    レートリミットを行う。period間に最大calls回の実行を許可する。
    calls回実行後はperiod秒待つ。
    Args:
        calls: 最大実行回数
        period: 期間
    Returns:
        Callable: デコレータ適用後の関数
    Example:
        ```python
        @rate_limit(calls=10, period=60)
        def sample_function():
            print("sample_function")
        ```


    """
    def deco(func):
        q = deque()
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            while q and now - q[0] > period:
                q.popleft()
            if len(q) >= calls:
                sleep_for = period - (now - q[0])
                time.sleep(sleep_for)
            q.append(time.monotonic())
            return func(*args, **kwargs)
        return wrapper
    return deco

