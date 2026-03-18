from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class ConversionOption:
    name: str
    label: str
    type: str  # "int", "float", "bool", "choice", "str"
    default: object
    choices: list | None = None
    min_val: float | None = None
    max_val: float | None = None


@dataclass
class ConversionTask:
    input_path: Path
    output_path: Path
    output_format: str
    options: dict = field(default_factory=dict)


class BaseConverter(ABC):

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def supported_input_formats(self) -> list[str]:
        ...

    @abstractmethod
    def supported_output_formats(self) -> list[str]:
        ...

    @abstractmethod
    def get_options(self, input_format: str, output_format: str) -> list[ConversionOption]:
        ...

    @abstractmethod
    def convert(
        self,
        task: ConversionTask,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        ...

    def can_convert(self, input_format: str, output_format: str) -> bool:
        return (
            input_format in self.supported_input_formats()
            and output_format in self.supported_output_formats()
        )
