import json
from pathlib import Path
from dataclasses import dataclass, field, asdict


PROFILES_DIR = Path.home() / ".pyconverter" / "profiles"


@dataclass
class ConversionProfile:
    name: str
    output_format: str
    options: dict = field(default_factory=dict)

    def save(self) -> Path:
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        path = PROFILES_DIR / f"{self.name}.json"
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, name: str) -> "ConversionProfile":
        path = PROFILES_DIR / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    @classmethod
    def list_profiles(cls) -> list[str]:
        if not PROFILES_DIR.exists():
            return []
        return [p.stem for p in PROFILES_DIR.glob("*.json")]

    @classmethod
    def delete(cls, name: str) -> None:
        path = PROFILES_DIR / f"{name}.json"
        if path.exists():
            path.unlink()
