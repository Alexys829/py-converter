import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path.home() / ".pyconverter" / "history.json"
MAX_ENTRIES = 200


@dataclass
class HistoryEntry:
    timestamp: str
    input_path: str
    output_path: str
    input_format: str
    output_format: str
    converter: str
    success: bool
    error: str | None = None
    options: dict | None = None


class ConversionHistory:
    def __init__(self):
        self._entries: list[HistoryEntry] = []
        self._load()

    def _load(self):
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
                self._entries = [HistoryEntry(**e) for e in data]
            except (json.JSONDecodeError, TypeError):
                self._entries = []

    def _save(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self._entries[-MAX_ENTRIES:]]
        HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, input_path: str, output_path: str, input_format: str,
            output_format: str, converter: str, success: bool,
            error: str | None = None, options: dict | None = None):
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            input_path=input_path,
            output_path=output_path,
            input_format=input_format,
            output_format=output_format,
            converter=converter,
            success=success,
            error=error,
            options=options,
        )
        self._entries.append(entry)
        self._save()

    def get_entries(self, limit: int = 50) -> list[HistoryEntry]:
        return list(reversed(self._entries[-limit:]))

    def clear(self):
        self._entries.clear()
        self._save()
