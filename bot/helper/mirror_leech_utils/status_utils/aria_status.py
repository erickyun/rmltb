# Source: https://github.com/anasty17/mirror-leech-telegram-bot/

from bot import aria2, LOGGER
from bot.helper.mirror_leech_utils.status_utils.status_utils import MirrorStatus


def get_download(gid):
    try:
        return aria2.get_download(gid)
    except Exception as e:
        LOGGER.error(f'{e}: Aria2c, Error while getting torrent info')


class AriaDownloadStatus:
    def __init__(self, gid, listener, seeding=False):
        self.__gid = gid
        self.__listener= listener
        self.__download = get_download(gid)
        self.start_time = 0
        self.seeding = seeding

    def __update(self):
        self.__download = self.__download.live
        if self.__download is None:
             self.__download = get_download(self.__gid)
        elif self.__download.followed_by_ids:
            self.__gid = self.__download.followed_by_ids[0]
            self.__download = get_download(self.__gid)

    def progress(self):
        """
        Calculates the progress of the mirror (upload or download)
        :return: returns progress in percentage
        """
        return self.__download.progress_string()

    def size_raw(self):
        """
        Gets total size of the mirror file/folder
        :return: total size of mirror
        """
        return self.__download.total_length

    def processed_bytes(self):
        return self.__download.completed_length

    def speed(self):
        self.__update()
        return self.__download.download_speed_string()

    def name(self):
        return self.__download.name

    def size(self):
        return self.__download.total_length_string()

    def eta(self):
        return self.__download.eta_string()

    def status(self):
        self.__update()
        download = self.__download
        if download.is_waiting:
            return MirrorStatus.STATUS_WAITING
        elif download.is_paused:
            return MirrorStatus.STATUS_PAUSED
        elif download.seeder and self.seeding:
            return MirrorStatus.STATUS_SEEDING
        else:
            return MirrorStatus.STATUS_DOWNLOADING

    def seeders_num(self):
        return self.__download.num_seeders

    def leechers_num(self):
        return self.__download.connections

    def uploaded_bytes(self):
        return self.__download.upload_length_string()

    def upload_speed(self):
        self.__update()
        return self.__download.upload_speed_string()

    def ratio(self):
        return f"{round(self.__download.upload_length / self.__download.completed_length, 3)}"

    def listener(self):
        return self.__listener
        
    def download(self):
        return self

    def gid(self):
        self.__update()
        return self.__gid

    def type(self):
        return "Aria"

    def cancel_download(self):
        self.__update()
        if len(self.__download.followed_by_ids) != 0:
            LOGGER.info(f"Cancelling Download: {self.name()}")
            downloads = aria2.get_downloads(self.__download.followed_by_ids)
            aria2.remove(downloads, force=True, files=True)
        else:
            LOGGER.info(f"Cancelling Download: {self.name()}")
        aria2.remove([self.__download], force=True, files=True)