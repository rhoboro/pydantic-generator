from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


class ExitStatus(Enum):
    OK = 0
    ERROR = auto()


class CLI:
    def run(self) -> int:
        try:
            return ExitStatus.OK
        except Exception as e:
            logger.exception(e)
            return ExitStatus.ERROR
