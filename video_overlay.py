import os
import tempfile
import cv2
import numpy as np
from moviepy.editor import AudioFileClip, VideoFileClip

def overlay_video(background_path: str, output_path: str, lang="ru"):
    # Путь к файлу с плашкой (foreground)
    foreground_path = './overlay.mp4'

    if lang == "ru":
        foreground_path = './overlay.mp4'
    if lang == "en":
        foreground_path = './overlay_en.mp4'
    if lang == "it":
        foreground_path = './overlay_it.mp4'

    # Создаем временный файл для сохранения промежуточного результата
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output_file:
        output_temp = temp_output_file.name  # Путь к временному файлу

    # Открываем видео-файл с фоном (background)
    background = cv2.VideoCapture(background_path)
    if not background.isOpened():
        raise ValueError(f"Не удалось открыть видео {background_path}")
    
    # Открываем видео с плашкой (foreground)
    foreground = cv2.VideoCapture(foreground_path)
    if not foreground.isOpened():
        raise ValueError(f"Не удалось открыть видео {foreground_path}")

    # Получаем размеры и параметры background
    b_width = int(background.get(cv2.CAP_PROP_FRAME_WIDTH))
    b_height = int(background.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = background.get(cv2.CAP_PROP_FPS)
    background_frame_count = int(background.get(cv2.CAP_PROP_FRAME_COUNT))

    # Получаем размеры foreground
    f_width = int(foreground.get(cv2.CAP_PROP_FRAME_WIDTH))
    f_height = int(foreground.get(cv2.CAP_PROP_FRAME_HEIGHT))
    foreground_frame_count = int(foreground.get(cv2.CAP_PROP_FRAME_COUNT))

    # Вычисляем общее количество кадров
    max_frame_count = max(background_frame_count, foreground_frame_count)

    # Выводим информацию для проверки
    print(f"Background: {b_width}x{b_height}, FPS: {fps}, Frames: {background_frame_count}")
    print(f"Foreground: {f_width}x{f_height}, Frames: {foreground_frame_count}")

    # Настроим VideoWriter для записи в промежуточный файл
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(output_temp, fourcc, fps, (b_width, b_height))

    # Рассчитываем размеры foreground
    new_f_width = b_width
    new_f_height = int(f_height / f_width * new_f_width)
    y_offset = b_height - new_f_height - int(0.2 * b_height)
    x_offset = 0

    # Переменные для хранения последнего кадра
    last_b_frame = None
    last_f_frame = None

    # Обрабатываем кадры
    for current_frame in range(max_frame_count):
        # Читаем кадры из background и foreground
        b_success, b_frame = background.read()
        f_success, f_frame = foreground.read()

        # Если background заканчивается, используем последний кадр
        if not b_success:
            b_frame = last_b_frame
        else:
            last_b_frame = b_frame

        # Если foreground заканчивается, перезапускаем его
        if not f_success:
            foreground.set(cv2.CAP_PROP_POS_FRAMES, 0)
            f_success, f_frame = foreground.read()

        if not f_success:
            f_frame = last_f_frame
        else:
            last_f_frame = f_frame

        # Масштабируем foreground
        foreground_resized = cv2.resize(f_frame, (new_f_width, new_f_height))

        # Создаём маску для foreground
        foreground_gray = cv2.cvtColor(foreground_resized, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(foreground_gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Выделяем области
        roi = b_frame[y_offset:y_offset + new_f_height, x_offset:x_offset + new_f_width]
        background_part = cv2.bitwise_and(roi, roi, mask=mask_inv)
        foreground_part = cv2.bitwise_and(foreground_resized, foreground_resized, mask=mask)

        combined = cv2.add(background_part, foreground_part)

        # Вставляем наложение обратно в кадр background
        b_frame[y_offset:y_offset + new_f_height, x_offset:x_offset + new_f_width] = combined

        # Записываем обработанный кадр
        output_video.write(b_frame)

    # Освобождаем ресурсы
    background.release()
    foreground.release()
    output_video.release()

    # Загружаем звук и видео для финальной обработки
    back_audio = AudioFileClip(background_path)  # Используем путь к оригинальному background
    output_video_clip = VideoFileClip(output_temp)

    # Добавляем аудио
    final_clip = output_video_clip.set_audio(back_audio)

    # Сохраняем финальный видеоролик
    final_output_path = output_path
    final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac")

    # Удаляем временный файл после обработки
    os.remove(output_temp)

    return final_output_path  # Путь к финальному видео
