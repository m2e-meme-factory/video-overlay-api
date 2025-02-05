import os
from dataclasses import dataclass

WORKDIR = os.path.dirname(__file__)

FOREGROUND_FILE_NAME = 'alpha.mov'
DOWNLOADS_FOLDER = 'downloads'
OVERLAYS_FOLDER = 'overlays'

DOWNLOADS_PATH = os.path.join(WORKDIR, DOWNLOADS_FOLDER)
OVERLAYS_PATH = os.path.join(WORKDIR, OVERLAYS_FOLDER)
FOREGROUND_PATH = os.path.join(WORKDIR, FOREGROUND_FILE_NAME)


@dataclass
class PortraitLimit:
    max_with: int = 1080
    max_height: int = 1920
    max_resolution: str = f'{max_with}:{max_height}'


@dataclass
class LandscapeLimit:
    max_with: int = 1920
    max_height: int = 1080
    max_resolution: str = f'{max_with}:{max_height}'


MAX_VIDEO_SIZE = 1024 * 1024 * 50
MAX_VIDEO_DURATION_SEC = 2 * 60

ACCEPTED_VIDEO_CONTENT_TYPES = [
    'video/mp4',
    'video/quicktime',  # mov
]

ACCEPTED_VIDEO_EXTENSIONS = [
    'mp4',
    'mov',
]

# Разрешаем запросы с вашего фронтенда
ORIGINS = [
    'http://localhost:3050',  # Адрес вашего React приложения
    'http://127.0.0.1:3050',  # Для удобства тестирования на 127.0.0.1
    '*'
]

PROXIES = [
    'http://4dx5E8:S2j81x@45.32.56.105:12426',
    'http://7S5R62:Ao5ErA@45.145.57.233:12615',
    'http://JrZ48F:j9GoTL@217.69.6.173:12659',
    'http://3BpTfg:GBx8bx@45.91.209.156:11167',
]
