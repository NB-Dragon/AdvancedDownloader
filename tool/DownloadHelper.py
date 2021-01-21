import uuid
import urllib.parse
from schema.Downloader.HTTPDownloader import HTTPDownloader


class DownloadHelper(object):
    def __init__(self, message_receiver, download_link, save_path, headers: dict = None, cookies: dict = None):
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._uuid_description = "".join(str(uuid.uuid1()).split("-"))
        self._message_receiver = message_receiver
        self._download_link = download_link
        self._save_path = save_path
        self._create_download_mission()

    def _create_download_mission(self):
        link_parse_result = urllib.parse.urlparse(self._download_link)
        scheme = link_parse_result.scheme
        if scheme in ["https", "http"]:
            http_helper = HTTPDownloader(self._download_link, self._save_path, self._uuid_description,
                                         self._message_receiver, self._headers, self._cookies)
            http_helper.start_download_mission(128)
            self._do_final_tips()
        else:
            self._make_message_and_send("unknown scheme, please wait to support!", False)

    def _do_final_tips(self):
        self._make_message_and_send("下载完成", False)
        self._make_message_and_send("如有帮助，请前往项目主页赞助，感谢各位：https://github.com/NB-Dragon/AdvancedDownloader", False)

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        message_dict["value"] = {"sender": "DownloadHelper", "mission_uuid": self._uuid_description,
                                 "content": content, "exception": exception}
        self._message_receiver.put(message_dict)
