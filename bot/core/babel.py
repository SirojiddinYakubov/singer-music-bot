import pathlib
from fastapi_babel import _  # noqa
from fastapi_babel import Babel
from fastapi_babel import BabelConfigs

ROOT_DIR = pathlib.Path(__file__).parents[1]
print(7, ROOT_DIR)
ALLOWED_LANGUAGES = ["uz", "ru"]
configs = BabelConfigs(
    ROOT_DIR=str(ROOT_DIR),
    BABEL_DEFAULT_LOCALE=ALLOWED_LANGUAGES[0],
    BABEL_TRANSLATION_DIRECTORY=f"{ROOT_DIR}/locales",
    BABEL_CONFIG_FILE=f"{ROOT_DIR}/babel.cfg"
)
babel = Babel(configs=configs)

if __name__ == "__main__":
    babel.run_cli()