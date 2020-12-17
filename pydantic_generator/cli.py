import logging
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from .core.generator import pydanticgen

logger = logging.getLogger(__name__)


class ExitStatus(Enum):
    OK = 0
    ERROR = auto()


class CLI:
    def run(self, input_: str, output: Optional[str]) -> ExitStatus:
        try:
            with open(input_) as reader:
                name = Path(input_).stem
                module_node = pydanticgen(name, reader)
            output_name = output or f"{module_node.first_class_name}.py"

            with open(output_name, "wt") as f:
                f.write(module_node.unparse())
            return ExitStatus.OK
        except Exception as e:
            logger.exception(e)
            return ExitStatus.ERROR
