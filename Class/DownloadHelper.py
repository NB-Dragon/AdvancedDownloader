from InterfaceScheme.HTTPDownloader import HTTPDownloader
import urllib.parse


class DownloadHelper(object):
    def __init__(self, message_receiver, download_link, save_path, download_index,
                 headers: dict = None, cookies: dict = None):
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._message_receiver = message_receiver
        self._download_link = download_link
        self._save_path = save_path
        self._download_index = download_index
        self._create_download_mission()

    def _create_download_mission(self):
        link_parse_result = urllib.parse.urlparse(self._download_link)
        scheme = link_parse_result.scheme
        if scheme in ["https", "http"]:
            heep_helper = HTTPDownloader(self._message_receiver, self._download_link, self._save_path,
                                         self._download_index, self._headers, self._cookies)
            heep_helper.start_download_mission()
        else:
            self._make_message_and_send("unknown scheme, please wait to support!", False)

    def _make_message_and_send(self, content, exception):
        message = {"sender": "DownloadHelper", "title": self._download_index, "content": content}
        self._message_receiver.put({"message": message, "exception": exception})
