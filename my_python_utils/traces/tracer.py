from typing import List, Literal, Any, Sequence, Mapping
import os
import uuid
import ulid
import json
import zipfile
from datetime import datetime
from pathlib import Path


class Tracer:
    def __init__(
        self, pattern: Literal["uuid", "ulid", "timestamp"], base_dir: str = "./outputs"
    ):
        """
        Args:
            pattern: ディレクトリ名の命名パターン。uuid, ulid, timestampのいずれかを指定。
            base_dir: トレースディレクトリの保存先ディレクトリ。デフォルトは./outputs。
        Example:
            ```python
            tracer = Tracer(pattern="uuid")
            ```

            ```python
            tracer = Tracer(pattern="ulid")
            ```

            ```python
            tracer = Tracer(pattern="timestamp")
            ```


        """
        stamp: str
        match pattern:
            case "uuid":
                stamp = str(uuid.uuid4())
            case "ulid":
                stamp = str(ulid.ulid())
            case "timestamp":
                stamp = datetime.now().strftime("%Y%m%d%H%M%S")

        self.trace_dir = os.path.join(base_dir, stamp)
        os.makedirs(self.trace_dir, exist_ok=True)

    def describe(self, description: str = "", file_name: str = "README.md"):
        """
        トレースディレクトリにREADME.mdファイルを作成し、descriptionを保存する。
        Args:
            description: トレースの説明。
            file_name: README.mdファイルの名前。デフォルトはREADME.md。
        Example:
            ```python
            tracer.describe(description="Some description of the trace", file_name="DESC.md")
            ```

        """
        file_path = os.path.join(self.trace_dir, file_name)
        save_text = f"# {file_name}\n\n{description}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(save_text)

    def backup(self, targets: List[str], compression: Literal["zip"] = "zip"):
        """
        バックアップファイルを作成する。
        Args:
            targets: バックアップ対象のファイルまたはディレクトリのリスト。
            compression: 圧縮形式。zipのみサポート。
        Example:
            ```python
            tracer.backup(targets=["some_script.py", "some_function.py", "some_module.py"], compression="zip")
            ```
        """
        files_to_backup = []
        for target in targets:
            if not os.path.exists(target):
                print(f"Warning: Path does not exist, skipping: {target}")
                continue

            if os.path.isfile(target):
                files_to_backup.append((target, os.path.basename(target)))
            elif os.path.isdir(target):
                for root, _, files in os.walk(target):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, target)
                        files_to_backup.append((file_path, rel_path))

        if not files_to_backup:
            print("Warning: No files to backup")
            return

        zip_name = "backup.zip"
        zip_path = os.path.join(self.trace_dir, zip_name)
        counter = 1
        while os.path.exists(zip_path):
            zip_name = f"backup_{counter}.zip"
            zip_path = os.path.join(self.trace_dir, zip_name)
            counter += 1

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path, arc_name in files_to_backup:
                zipf.write(file_path, arc_name)

    def save(self, value: Any, file_name: str):
        """
        値をファイルに保存する。
        Args:
            value: 保存する値。
            file_name: 保存するファイルの名前。
        Example:
            ```python
            tracer.save(value="Some value", file_name="some_value.txt")
            ```
        """
        file_path = os.path.join(self.trace_dir, file_name)
        suffix = Path(file_name).suffix.lower()

        if suffix in [".txt", ".md"]:
            self._save_as_text(value, file_path)
        elif suffix == ".json":
            self._save_as_json(value, file_path)
        else:
            raise ValueError(f"Unsupported file extension: {suffix}")

    # ===============================
    # Private methods
    # ===============================
    def _save_as_text(self, value: Any, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(value))

    def _save_as_json(self, value: Any, file_path: str):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            self._save_as_text(value, file_path)


if __name__ == "__main__":

    tracer = Tracer(pattern="timestamp")  # or "uuid" or "timestamp"
    tracer.describe(description="Some description of the trace", file_name="DESC.md")
    tracer.backup(
        targets=["some_script.py", "some_function.py", "some_module.py"],
        compression="zip",
    )  # save targets in zip or tar.gz file.

    some_output = "Some output from module or function or ,,,,"

    # save some output values to files specified by file_name.
    tracer.save(some_output, file_name="some_output.txt")
    tracer.save(some_output, file_name="some_output.json")
