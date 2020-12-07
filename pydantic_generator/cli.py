import logging
from enum import Enum, auto
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
                model_schema = pydanticgen(reader)
            output_name = output or model_schema.first_model_name

            with open(output_name, "wt") as f:
                f.write(model_schema.to_string())
            return ExitStatus.OK
        except Exception as e:
            logger.exception(e)
            return ExitStatus.ERROR
