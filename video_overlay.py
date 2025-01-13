import os
import cv2
import numpy as np

def overlay_video_with_alpha(background_path, alpha_video_path, output_path):
    # Открываем фоновое видео
    background = cv2.VideoCapture(background_path)
    if not background.isOpened():
        raise ValueError(f"Не удалось открыть видео {background_path}")

    # Открываем видео с наложением
    overlay = cv2.VideoCapture(alpha_video_path)
    if not overlay.isOpened():
        raise ValueError(f"Не удалось открыть видео {alpha_video_path}")

    # Получаем параметры выходного видео
    width = int(background.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(background.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = background.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret_bg, bg_frame = background.read()  # Читаем кадр фона
        ret_ov, ov_frame = overlay.read()    # Читаем кадр наложения

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

# Пример вызова функции
# overlay_video_with_alpha("background.mp4", "./prod/alpha_converted.mov", "output.mp4")

# donsload_video = os.path.join("prod", "alpha_converted.mov")
# overlay_video_with_alpha("input.mp4", donsload_video, "output.mp4")