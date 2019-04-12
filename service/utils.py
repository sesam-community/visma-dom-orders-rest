from datetime import datetime
from typing import Union
import logging


def str_to_bool(s: str) -> bool:
    return (s == 'True' or s == 'true') or False


def ts_to_date(timestamp: int) -> Union[str, None]:
    try:
        return datetime.fromtimestamp(timestamp).astimezone().isoformat()
    except Exception as e:
        logging.warning("error occurred while converting {} : {}".format(str(timestamp), str(e)))
        return None
