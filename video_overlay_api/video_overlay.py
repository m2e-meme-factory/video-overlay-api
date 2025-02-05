import asyncio
import cv2
import os
import numpy as np

from constants import FOREGROUND_PATH, MAX_VIDEO_DURATION_SEC, MAX_VIDEO_SIZE, PortraitLimit, LandscapeLimit
from concurrent.futures import ThreadPoolExecutor
from exeptions import VideoCheckError, FfmpegOverlayError
from utils import get_size_in_mb, logger

executor = ThreadPoolExecutor()


def overlay_with_cv2(input_file_path: str, output_file_path: str):
    # Открываем фоновое видео
    background = cv2.VideoCapture(input_file_path)
    if not background.isOpened():
        raise ValueError(f'Не удалось открыть видео {input_file_path}')

    # Открываем видео с наложением
    overlay = cv2.VideoCapture(FOREGROUND_PATH)
    if not overlay.isOpened():
        raise ValueError(f'Не удалось открыть видео {FOREGROUND_PATH}')

    # Получаем параметры выходного видео
    width = int(background.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(background.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = background.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file_path, fourcc, fps, (width, height))

    while True:
        ret_bg, bg_frame = background.read()  # Читаем кадр фона
        ret_ov, ov_frame = overlay.read()  # Читаем кадр наложения

        if not ret_bg or not ret_ov:
            break  # Выходим из цикла, если кадры закончились

        # Изменяем размер наложения под размер фона
        ov_frame = cv2.resize(ov_frame, (width, height))

        # Проверяем, есть ли альфа-канал
        if ov_frame.shape[2] == 4:
            alpha = ov_frame[:, :, 3] / 255.0  # Нормализуем альфа-канал в диапазон [0, 1]
            rgb = ov_frame[:, :, :3]

            # Наложение с использованием альфа-канала
            foreground = cv2.multiply(alpha[:, :, None], rgb.astype(float))
            background_part = cv2.multiply(1 - alpha[:, :, None], bg_frame.astype(float))

            # Объединяем фон и наложение без потери основной непрозрачности
            combined_frame = cv2.add(foreground, background_part).astype(np.uint8)
        else:
            # Если альфа-канала нет, просто накладываем
            combined_frame = cv2.addWeighted(bg_frame, 0.5, ov_frame, 0.5, 0)

        # Сохраняем кадр
        out.write(combined_frame)

    # Освобождаем ресурсы
    background.release()
    overlay.release()
    out.release()


def check_video_resolution(video: cv2.VideoCapture):
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_resolution = f'{width}x{height}'
    is_video_portrait = height > width
    limit = PortraitLimit if is_video_portrait else LandscapeLimit
    if width > getattr(limit, 'max_with') or height > getattr(limit, 'max_height'):
        max_resolution = getattr(limit, 'max_resolution')
        raise VideoCheckError(
            f'Разрешение видео {video_resolution} превышает максимально допустимое {max_resolution}'
        )


def check_video_duration(video: cv2.VideoCapture):
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = int(frame_count / fps)
    if duration > MAX_VIDEO_DURATION_SEC:
        raise VideoCheckError(
            f'Длительность видео {duration}с превышает максимально допустимую {MAX_VIDEO_DURATION_SEC}с',
        )


def check_video_size(file_path: str):
    file_stats = os.stat(file_path)
    if file_stats.st_size > MAX_VIDEO_SIZE:
        current_size_mb = get_size_in_mb(file_stats.st_size)
        max_size_mb = get_size_in_mb(MAX_VIDEO_SIZE)
        raise VideoCheckError(f'Размер видео {current_size_mb}Mb превышает допустимый размер {max_size_mb}Mb')


def check_video_limitations(input_file_path: str):
    video = cv2.VideoCapture(input_file_path)
    check_video_resolution(video)
    check_video_duration(video)
    check_video_size(input_file_path)


async def overlay_with_ffmpeg(input_file_path: str, output_file_path: str):
    command = [
        'ffmpeg',
        '-loglevel', 'error',
        '-y',  # перезаписывает файл, если он уже существует
        '-i', input_file_path,  # фоновое видео
        '-stream_loop', '-1',  # бесконечно проигрываем видео с наложением
        '-i', FOREGROUND_PATH,  # видео с наложением
        '-filter_complex',
        '[1:v]lut=a=val*0.5[alpha]; '  # устанавливаем прозрачность видео с наложением (с альфа-каналом) 0.5
        # скейлим видео с наложением относительно основного видео:
        # уменьшаем высоту наложения до 0.4 от высоты видео (ih*0.4), сохраняя соотношение сторон (oh*mdar)
        '[alpha][0:v]scale2ref=oh*mdar:ih*0.4[front][back]; '
        # выполняем наложение: центрируем наложение относительно основного видео по ширине ((W-w)/2) 
        # и располагаем наложение внизу основного видео по высоте (H-h)
        '[back][front]overlay=(W-w)/2:H-h:shortest=1[out]',
        '-map', '[out]',  # берем итоговое видео из переменной out
        '-map', '0:a',  # берем звук из фонового видео
        '-c:a', 'copy',  # копируем аудио из фонового видео без перекодирования
        '-c:v', 'libx264',  # применяем libx264 для кодировки видео
        '-preset', 'ultrafast',  # быстрое кодирование
        output_file_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *command,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if stderr:
        logger.exception(f'Внутрення ошибка обработки видео {input_file_path}: {stderr.decode()}')
        raise FfmpegOverlayError()
    logger.info(f'Наложение видео выполнено успешно')


async def overlay_by_type(input_file_path: str, output_file_path: str, overlay_type: str = 'ffmpeg'):
    check_video_limitations(input_file_path)
    if overlay_type == 'ffmpeg':
        await overlay_with_ffmpeg(input_file_path, output_file_path)
    elif overlay_type == 'cv2':
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, overlay_with_cv2, input_file_path, output_file_path)
    else:
        raise ValueError(f'Неверный тип наложения {overlay_type}')
