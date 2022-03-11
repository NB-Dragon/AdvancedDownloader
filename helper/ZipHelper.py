#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import os
import shutil


class ZipHelper(object):
    def __init__(self, log_printer):
        self._log_printer = log_printer

    def unzip(self, zip_path, unzip_path):
        if self._check_command_install("unzip -h >/dev/null 2>&1"):
            if os.path.exists(unzip_path):
                shutil.rmtree(unzip_path)
            os.system("unzip -q '{}' -d '{}'".format(zip_path, unzip_path))
        else:
            self._make_message_and_send("系统尚未安装或无法检测到unzip命令")

    def zip(self, zip_path, unzip_path):
        if self._check_command_install("zip -h >/dev/null 2>&1"):
            os.system("cd '{}' && zip -q -r -y '{}' *".format(unzip_path, zip_path))
            shutil.rmtree(unzip_path)
        else:
            self._make_message_and_send("系统尚未安装或无法检测到zip命令")

    @staticmethod
    def _check_command_install(command):
        return os.system(command) == 0

    def _make_message_and_send(self, content):
        self._log_printer.print("ZipHelper", content)
