#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/2/21 18:00
# Create User: NB-Dragon
import os
import platform
import subprocess


class FileOpenHelper(object):
    def __init__(self, message_receiver):
        self._message_receiver = message_receiver
        self._default_open_method = self._find_default_system_open_method()

    def open(self, file_path):
        try:
            if self._default_open_method:
                self._default_open_method(file_path)
            else:
                self._make_message_and_send("当前系统暂未适配，如有需要，请提交issue", False)
        except Exception as e:
            self._make_message_and_send(str(e), True)
            self._make_message_and_send("自动打开文件失败，请自行检查是否为桌面版系统", False)

    def _find_default_system_open_method(self):
        current_platform = platform.system()
        if current_platform == "Linux":
            return self._open_in_linux
        elif current_platform == "Darwin":
            return self._open_in_mac
        elif current_platform == "Windows":
            return self._open_in_windows
        else:
            return None

    @staticmethod
    def _open_in_linux(file_path):
        subprocess.call(["xdg-open", file_path], stderr=subprocess.DEVNULL)

    @staticmethod
    def _open_in_mac(file_path):
        subprocess.call(["open", file_path], stderr=subprocess.DEVNULL)

    @staticmethod
    def _open_in_windows(file_path):
        os.startfile(file_path)

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "FileOpenHelper", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": None, "detail": detail_info}
        self._message_receiver.put(message_dict)
