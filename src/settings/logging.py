from copy import deepcopy

import ujson
from pythonjsonlogger.json import JsonFormatter

from src import settings
from src.settings.conf import Env


class BaseJsonFormatter(JsonFormatter):
    SECURE_PARAMETERS = ('secret',)

    def add_fields(self, log_record, record, message_dict):
        super(BaseJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        if isinstance(record.msg, dict):
            log_record['json'] = self._filter_json(deepcopy(record.msg.get('json', {})))
            log_record['text'] = self._filter_text(deepcopy(record.msg.get('text', '')))

    def _filter_json(self, json_log: dict) -> dict:
        if json_log and isinstance(json_log, dict):
            for key, value in json_log.copy().items():
                if key in self.SECURE_PARAMETERS:
                    json_log[key] = '***'

                if isinstance(value, dict):
                    json_log[key] = self._filter_json(value)
        return json_log

    def _filter_text(self, json_log: str) -> str:
        if isinstance(json_log, str):
            try:
                log = ujson.loads(json_log or '{}')
            except ujson.JSONDecodeError:
                log = json_log
        else:
            log = json_log

        filtered_log = self._filter_json(log)
        return ujson.dumps(log or filtered_log)


log_level = settings.LOG_LEVEL

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': BaseJsonFormatter,
        },
        'local': {
            '()': 'logging.Formatter',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'local' if settings.ENV == Env.LOCAL else 'json',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'uvicorn': {'handlers': ['default'], 'level': log_level},
        'gunicorn': {'handlers': ['default'], 'level': log_level},
        'gunicorn.access': {'handlers': ['default'], 'level': log_level},
        'gunicorn.error': {'handlers': ['default'], 'level': log_level},
    },
    'root': {'handlers': ['default'], 'level': log_level},
}
