from .manager import LoggerManager

_manager = LoggerManager()

def get_logger(name: str):
    return _manager.get_logger(name)