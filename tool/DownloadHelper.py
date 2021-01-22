import uuid
import urllib.parse
from schema.Downloader.HTTPDownloader import HTTPDownloader


class DownloadHelper(object):
    def __init__(self, message_receiver):
        self._message_receiver = message_receiver

    def create_new_download_mission(self, base_info: dict):
        uuid_description = "".join(str(uuid.uuid1()).split("-"))
        link_parse_result = urllib.parse.urlparse(base_info["download_link"])
        scheme = link_parse_result.scheme
        if scheme in ["https", "http"]:
            http_helper = HTTPDownloader(uuid_description, base_info, dict(), self._message_receiver)
            http_helper.start_download_mission()
        else:
            self._make_message_and_send(uuid_description, "unknown scheme, please wait to support!", False)
        self._do_final_tips(uuid_description)

    def _do_final_tips(self, uuid_description):
        final_donate_message = "如有帮助，请前往项目主页赞助，感谢各位：https://github.com/NB-Dragon/AdvancedDownloader"
        self._make_message_and_send(uuid_description, "下载完成", False)
        self._make_message_and_send(uuid_description, final_donate_message, False)

    def _make_message_and_send(self, uuid_description, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "DownloadHelper", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": uuid_description, "detail": detail_info}
        self._message_receiver.put(message_dict)
