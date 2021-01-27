#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import re
import queue
import chardet


class FileOperator(object):
    def __init__(self, file_name, mission_uuid, thread_message: queue.Queue):
        self._file_name = file_name
        self._mission_uuid = mission_uuid
        self._thread_message = thread_message

    def set_file_content(self, content):
        try:
            writer = open(self._file_name, 'w', encoding='UTF8')
            writer.write(content)
            writer.close()
        except Exception as e:
            self._make_message_and_send(str(e), True)

    def get_file_content(self):
        try:
            encoding = self._find_right_encoding(self._file_name)
            reader = open(self._file_name, 'r', encoding=encoding)
            content = reader.read()
            reader.close()
            return content
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def get_lines_from_file(self):
        file_content = self.get_file_content()
        if file_content:
            return re.findall('(.+)\n', file_content)
        else:
            return None

    @staticmethod
    def _find_right_encoding(file_name):
        file = open(file_name, 'rb')
        content = file.read()
        file.close()
        charset = chardet.detect(content)['encoding']
        return 'GB2312' if charset == 'GB2312' else 'UTF8'

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "FileOperator", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)
