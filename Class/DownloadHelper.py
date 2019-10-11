import requests
import threading
import os
import re
import queue
import time
import shutil


class DownloadThread(threading.Thread):
    """
    download_range: [queue_index, start, end, fail_count]
    """

    def __init__(self, link, save_path, file_name, download_range, main_queue: queue.Queue,
                 headers: dict, cookies: dict) -> None:
        super().__init__()
        self._link = link
        self._save_path = save_path
        self._file_name = file_name
        self._download_range = download_range
        self._main_queue = main_queue
        self._headers = headers.copy()
        self._cookies = cookies.copy()
        self._download_step_size = 2 ** 20

    """
    message [queue_index, state_code]
    state_code=1 : download success
    state_code=0 : download failed
    state_code=-1: download forbidden
    """

    def run(self) -> None:
        save_file_name = self._make_file_name()
        self._headers['Range'] = self._make_part_file_range(save_file_name)
        if self._headers['Range']:
            stream_response = self._make_response(self._headers, self._cookies)
            if stream_response is None:
                self._main_queue.put([self._download_range[0], 0])
            elif stream_response.status_code in [200, 206]:
                self._write_file_from_stream(stream_response, save_file_name)
                if self._check_part_file_normal_finish(save_file_name):
                    self._main_queue.put([self._download_range[0], 1])
                else:
                    self._main_queue.put([self._download_range[0], 0])
            elif stream_response.status_code == 416:
                self._main_queue.put([self._download_range[0], 1])
            elif stream_response.status_code == 403:
                self._main_queue.put([self._download_range[0], -1])
            else:
                self._main_queue.put([self._download_range[0], 0])
        else:
            self._main_queue.put([self._download_range[0], 1])

    def _make_response(self, headers, cookies):
        try:
            return requests.get(self._link, stream=True, headers=headers, cookies=cookies, timeout=10)
        except Exception:
            return None

    def _make_file_name(self):
        return os.path.join(self._save_path, "{}.part{}".format(self._file_name, self._download_range[0]))

    def _make_download_position(self, current_size):
        return self._download_range[1] + current_size, self._download_range[2]

    def _write_file_from_stream(self, stream_response, save_file_name):
        current_size = self._get_file_size(save_file_name)
        writer = open(save_file_name, 'a+b')
        try:
            self._seek_and_truncate_file(writer, current_size)
            for content in stream_response.iter_content(self._download_step_size):
                writer.write(content)
                writer.flush()
        except Exception:
            self._seek_and_truncate_file(writer, current_size)
        finally:
            writer.close()
            stream_response.close()

    def _make_part_file_range(self, save_file_name):
        current_size = self._get_file_size(save_file_name)
        start_position, end_position = self._make_download_position(current_size)
        if end_position == 0 or start_position <= end_position:
            return "bytes={}-{}".format(start_position, "" if end_position == 0 else end_position)
        else:
            return None

    def _check_part_file_normal_finish(self, save_file_name):
        if self._download_range[2] != 0:
            current_file_size = self._get_file_size(save_file_name)
            normal_file_size = self._download_range[2] - self._download_range[1] + 1
            return current_file_size == normal_file_size
        else:
            return True

    @staticmethod
    def _get_file_size(each_part_file_name):
        if os.path.exists(each_part_file_name):
            return os.path.getsize(each_part_file_name)
        else:
            return 0

    @staticmethod
    def _seek_and_truncate_file(writer, position):
        if position != 0:
            writer.seek(position)
            writer.truncate()


class DownloadHelper(object):
    def __init__(self, link, save_path, headers: dict = None, cookies: dict = None):
        self._link = link
        self._save_path = save_path
        self._download_path = ""
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._link_info = self._analyse_info()
        self._download_queue = {}
        self._message_queue = queue.Queue()
        self._alive_thread_count = 0
        self._max_thread_count = 128  # 每个任务最多同时128个线程下载
        self.current_file_size = 0
        self.known_file_size = None

    def start_mission(self):
        if self._check_download_mission_can_run():
            self._download_path = self._get_download_directory()
            self._make_download_queue()
            self._create_mission()
            self._listen_mission()
            self._splice_all_part()

    def pause_mission(self):
        pass

    def delete_mission(self):
        shutil.rmtree(self._download_path)

    def _check_download_mission_can_run(self):
        if self._link_info and self._link_info['file-name']:
            return True
        else:
            print("任务连接超时，请重试")
            return False

    def _get_download_directory(self):
        file_name_no_postfix = os.path.splitext(self._link_info['file-name'])[0]
        return os.path.join(self._save_path, file_name_no_postfix)

    def _make_download_queue(self):
        self._init_download_directory()
        if self._link_info['range-download'] and self._link_info['content-length']:
            mission_content_size = self._link_info['content-length']
            if mission_content_size >= self._max_thread_count:
                each_thread_size = self._make_each_thread_size(mission_content_size, self._max_thread_count)
                current_sum_size = 0
                for index in range(1, self._max_thread_count + 1):
                    start_position = current_sum_size
                    end_position = current_sum_size + each_thread_size[index - 1] - 1
                    self._download_queue[str(index)] = [str(index), start_position, end_position, False, 0]
                    current_sum_size += each_thread_size[index - 1]
                self._download_queue[str(self._max_thread_count)][2] = 0
            else:
                self._download_queue["1"] = ["1", 0, 0, False, 0]
        else:
            self._download_queue["1"] = ["1", 0, 0, False, 0]

    def _init_download_directory(self):
        if not os.path.exists(self._download_path):
            os.mkdir(self._download_path)
        self.current_file_size = self._calculate_download_directory_size()
        self.known_file_size = self._link_info['content-length']

    def _create_mission(self):
        for each_mission_key in self._download_queue.keys():
            self._start_thread_by_identity(each_mission_key)
            self._alive_thread_count += 1
            if self._alive_thread_count >= min(len(self._download_queue), self._max_thread_count):
                break

    def _listen_mission(self):
        start_time = time.time()
        while len(self._download_queue) != 0:
            end_time = time.time()
            if not self._message_queue.empty():
                message = self._message_queue.get()
                if message[1] == 1:
                    self._download_queue.pop(message[0])
                elif message[1] == 0:
                    self._download_queue[message[0]][4] += 1
                    self._download_queue[message[0]][3] = False
                elif message[1] == -1:
                    print("资源禁止访问，请确认验证信息")
                    break
                new_mission_identity = self._get_new_mission_identity()
                if new_mission_identity:
                    self._start_thread_by_identity(new_mission_identity)
            if end_time - start_time >= 1:
                end_size = self._calculate_download_directory_size()
                end_time = time.time()
                speed = (end_size - self.current_file_size) / (end_time - start_time)
                print("当前下载速度为:{}".format(self._get_format_file_size(speed)))
                start_time = end_time
                self.current_file_size = end_size

    def _start_thread_by_identity(self, thread_id: str):
        mission_info = self._download_queue[thread_id]
        self._download_queue[thread_id][3] = True
        new_thread = DownloadThread(self._link, self._download_path, self._link_info['file-name'],
                                    mission_info, self._message_queue, self._headers, self._cookies)
        new_thread.start()

    def _splice_all_part(self):
        file_list = os.listdir(self._download_path)
        file_match_rule = re.compile("{}\\.part\\d+".format(self._link_info['file-name']))
        for file_name in file_list:
            if not file_match_rule.match(file_name):
                file_list.remove(file_name)
        if len(file_list) != 0:
            final_save_name = os.path.join(self._save_path, self._link_info['file-name'])
            file_writer = open(final_save_name, 'w+b')
            for index in range(1, len(file_list) + 1):
                part_file_name = "{}.part{}".format(self._link_info['file-name'], index)
                part_file_path = os.path.join(self._download_path, part_file_name)
                part_file_reader = open(part_file_path, 'rb')
                file_writer.write(part_file_reader.read())
                part_file_reader.close()
                os.remove(part_file_path)
            file_writer.close()
            last_file = os.listdir(self._download_path)
            if len(last_file) == 1 and last_file[0] == "download.conf" and os.path.isfile(last_file[0]):
                shutil.rmtree(self._download_path)

    def _calculate_download_directory_size(self):
        file_list = os.listdir(self._download_path)
        current_size = 0
        for file_name in file_list:
            if re.findall("\\.part\\d+$", file_name):
                current_size += os.path.getsize(os.path.join(self._download_path, file_name))
        return current_size

    def _get_new_mission_identity(self):
        sleep_thread = {key: value for key, value in self._download_queue.items() if value[3] is False}
        min_failed_list = sorted(sleep_thread.items(), key=lambda value: value[1][4])
        return min_failed_list[0][0] if len(min_failed_list) else None

    def _analyse_info(self):
        if not self._recursive_update_link():
            return None
        stream_response = self._make_response(self._headers, self._cookies)
        if not stream_response:
            return None
        file_name = self._analyse_file_name(stream_response)
        content_length = stream_response.headers.get('content-length')
        stream_response.close()
        content_length = int(content_length) if content_length is not None else False
        return {"file-name": file_name, "content-length": content_length,
                "range-download": self._judge_can_range_file()}

    @staticmethod
    def _analyse_file_name(response):
        content_disposition = response.headers.get('Content-disposition')
        if content_disposition and "filename=" in content_disposition:
            content_list = content_disposition.split(";")
            content_list = [content.strip() for content in content_list[:]]
            filename_content = [content for content in content_list if content.startswith("filename=")][0]
            filename = re.findall("(?<=filename=).*", filename_content)[0]
            if re.findall("^[\"].*?[\"]$", filename):
                filename = eval(filename)
        else:
            filename = os.path.split(response.url)[-1].split("?")[0]
        return filename

    def _recursive_update_link(self):
        while True:
            stream_response = self._make_response(self._headers, self._cookies)
            if stream_response is None: return False
            temp_link = stream_response.url
            stream_response.close()
            if temp_link != self._link:
                self._link = temp_link
            else:
                break
        return True

    def _judge_can_range_file(self):
        temp_agent = self._headers.copy()
        temp_agent['Range'] = "bytes=0-19"
        stream_response = self._make_response(temp_agent, self._cookies)
        content_range = stream_response.headers.get('content-range')
        stream_response.close()
        return content_range is not None

    def _make_response(self, headers, cookies):
        try:
            return requests.get(self._link, stream=True, headers=headers, cookies=cookies, timeout=10)
        except Exception:
            return None

    @staticmethod
    def _make_each_thread_size(content_size, thread_count):
        low_base_size = content_size // thread_count
        content_size_list = [low_base_size] * thread_count
        height_size_count = content_size - low_base_size * thread_count
        content_size_list[0:height_size_count] = [low_base_size + 1] * height_size_count
        return content_size_list

    @staticmethod
    def _get_format_file_size(size):
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB", "NB", "DB", "CB"]
        unit_step = 0
        while size >= 1024:
            size /= 1024
            unit_step += 1
        return "{:.2f}{}/s".format(size, units[unit_step])
