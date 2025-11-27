import traceback
import time
import requests
from functools import wraps
from typing import Callable, Literal

def monitoring(platform: Literal["discord", "teams"], webhook_url: str) -> Callable:
    """
    関数の実行時間の計測と実行・失敗状況を監視するデコレータ。
    処理終了時およびエラー時に指定されたプラットフォームへ通知を送信する。
    Args:
        platform: 通知先のプラットフォーム. "discord" または "teams" を指定。
        webhook_url: 通知先のWebhook URL.
    Example:
        ```python
        @monitoring(platform="discord", webhook_url="~~~discord_webhook_url~~~")
        def hoge_function():
            ...

        ```

        ```python
        @monitoring(platform="teams", webhook_url="~~~teams_webhook_url~~~")
        def hoge_function():
            ...

        ```

    """
    def _send_discord_message(message: str):
        requests.post(webhook_url, json={"content": message})

    def _send_teams_message(message: str):
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": message,
                                "wrap": True,
                            }
                        ],
                    },
                }
            ],
        }
        requests.post(webhook_url, json=payload)

    _send_message_exporter = {
        "discord": _send_discord_message,
        "teams": _send_teams_message,
    }
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time

                hours = int(elapsed_time // 3600)
                minutes = int((elapsed_time % 3600) // 60)
                seconds = int(elapsed_time % 60)
                time_str = f"{hours}時間{minutes}分{seconds}秒"

                message = f"✅ 実行が正常に完了しました\n関数: {func.__name__}\n実行時間: {time_str} ({elapsed_time:.2f}秒)"
                _send_message_exporter[platform](message)

                return result
            except Exception as e:
                elapsed_time = time.time() - start_time

                traceback_str = ''.join(traceback.format_exception(e))
                print(traceback_str)

                hours = int(elapsed_time // 3600)
                minutes = int((elapsed_time % 3600) // 60)
                seconds = int(elapsed_time % 60)
                time_str = f"{hours}時間{minutes}分{seconds}秒"

                message = f"❌ エラーが発生しました: {e}\n関数: {func.__name__}\n実行時間: {time_str} ({elapsed_time:.2f}秒)\nスタックトレース:\n{traceback_str}"
                _send_message_exporter[platform](message)

                raise e
        return wrapper
    return decorator

 