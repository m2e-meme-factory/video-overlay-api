
import os

from video_overlay import overlay_video


file = "aa295ce8-b4b5-49eb-9037-9277d98b01a8"

DOWNLOADS_FOLDER = "downloads"
OVERLAYS_FOLDER = "overlays"

input_file = os.path.join(DOWNLOADS_FOLDER, f"{file}.mp4")
output_file = os.path.join(OVERLAYS_FOLDER, f"{file}_overlayed.mp4")

overlay_video(input_file, output_file)