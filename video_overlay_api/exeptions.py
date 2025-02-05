from typing import Optional

from fastapi import status


class BaseApiException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str, status_code: Optional[int] = None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class BadRequestException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundException(BaseApiException):
    status_code = status.HTTP_404_NOT_FOUND


class ServiceInternalError(Exception):
    """Внутренние ошибки сервиса"""


class FfmpegOverlayError(ServiceInternalError):
    """Ошибка наложения видея с использованием ffmpeg"""


class DownloadError(ServiceInternalError):
    """Ошибка загрузки видео по сслыке"""


class UnsupportedPlatformError(Exception):
    """Платформа не поддерживается для скачивания видео"""


class VideoCheckError(Exception):
    """Видео превышает максимальное разрешение или длительность"""
