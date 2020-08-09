import importlib
from pathlib import Path
from mirai import Mirai
from mirai.logger import Session as SessionLogger


def load_mods(app: Mirai):
    mod_dir = Path(__file__).parent
    module_prefix = mod_dir.name

    for mod in mod_dir.iterdir():
        if mod.is_dir() and mod.joinpath('__init__.py').exists():
            load_mod(app, f'{module_prefix}.{mod.name}')


def load_mod(app: Mirai, module_path: str):
    try:
        importlib.import_module(module_path)
        SessionLogger.info(f'Succeeded to import "{module_path}"')
    except Exception as e:
        SessionLogger.error(f'Failed to import "{module_path}", error: {e}')
        SessionLogger.exception(e)
