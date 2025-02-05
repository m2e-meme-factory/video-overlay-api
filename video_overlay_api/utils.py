import functools
import logging
import os
import urllib

from yt_dlp import YoutubeDL

from constants import DOWNLOADS_PATH, OVERLAYS_PATH


class YoutubeDLCorrectProxy(YoutubeDL):

    @functools.cached_property
    def proxies(self):
        """Global proxy configuration"""
        opts_proxy = self.params.get('proxy')
        if opts_proxy is not None:
            if opts_proxy == '':
                opts_proxy = '__noproxy__'
            proxies = {'http': opts_proxy}
        else:
            proxies = urllib.request.getproxies()
            # compat. Set HTTPS_PROXY to __noproxy__ to revert
            if 'http' in proxies and 'https' not in proxies:
                proxies['https'] = proxies['http']

        return proxies


def create_video_folders():
    for file_path in (DOWNLOADS_PATH, OVERLAYS_PATH):
        os.makedirs(file_path, exist_ok=True)


def get_size_in_mb(size: int) -> float:
    return round(size / (1024 * 1024), 1)


logger = logging.getLogger('video_overlay_api')
