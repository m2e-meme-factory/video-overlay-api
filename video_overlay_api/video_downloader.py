import random
from typing import Literal
from uuid import uuid4

from constants import DOWNLOADS_PATH, MAX_VIDEO_SIZE, PROXIES, LandscapeLimit, PortraitLimit
from exeptions import DownloadError, UnsupportedPlatformError
from utils import YoutubeDLCorrectProxy, logger


def get_video_format_opts(best_quality: bool, video_orientation: Literal['portrait', 'landscape']) -> dict:
    base_video_format = f'best[filesize<?{MAX_VIDEO_SIZE}]'
    if best_quality:
        max_height = PortraitLimit.max_height if video_orientation == 'portrait' else LandscapeLimit.max_height
        opts = {
            # лучшее видео не превышающее допустимую высоту и размер и лучшее аудио
            # или видео, где размер не известен и лучшее аудио
            # или лучший комбинилрованный файл (видео и аудио) не превышующий максимальный размер,
            # или комбинилрованный файл, где размер не известен
            'format': f'bestvideo[height<={max_height}][filesize<?{MAX_VIDEO_SIZE}]+bestaudio[ext=m4a]/{base_video_format}',
            'merge_output_format': 'mp4',  # расширение для объединенного файла
        }
    else:
        opts = {
            # лучший комбинилрованный файл (видео и аудио) не превышующий максимальный размер,
            # или комбинилрованный файл, где размер не известен
            'format': base_video_format,
            'merge_output_format': None,
        }
    return opts


def download_video(url: str, best_quality: bool, video_orientation: Literal['portrait', 'landscape']) -> str:
    """Определяет платформу и скачивает видео с соответствующего сайта"""
    file_name = f'{uuid4()}.mp4'
    video_format_opts = get_video_format_opts(best_quality, video_orientation)
    ydl_opts = {
        **video_format_opts,
        'outtmpl': f'{DOWNLOADS_PATH}/{file_name}',  # Шаблон имени файла
        'proxy': random.choice(PROXIES),
        'verbose': True,
        'debug_printtraffic': True,
    }
    if 'youtube.com' in url or 'youtu.be' in url:  # Если ссылка с YouTube
        platform = 'YouTube'
    elif 'instagram.com' in url:  # Если ссылка с Instagram
        platform = 'Instagram'
    elif 'tiktok.com' in url:  # Если ссылка с TikTok
        platform = 'TikTok'
    else:
        raise UnsupportedPlatformError(
            'Платформа не поддерживается. Пожалуйста, введите ссылку с YouTube, Instagram или TikTok.',
        )

    try:
        with YoutubeDLCorrectProxy(ydl_opts) as ydl:
            ydl._ies['Youtube'] = ydl.get_info_extractor('Youtube')
            ydl.download([url])
        logger.info(f'Видео с {platform} успешно загружено в папку: {DOWNLOADS_PATH}')
        return file_name
    except Exception:
        logger.exception(f'Внутренняя ошибка при загрузке видео c {platform}')
        raise DownloadError()
