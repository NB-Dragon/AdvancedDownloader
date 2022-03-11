#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import json
import os
import sys
import time


class ProjectHelper(object):
    def __init__(self):
        self._code_entrance_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self._cache_directory = os.path.join(self._code_entrance_path, ".cache")
        self._static_directory = os.path.join(self._code_entrance_path, "static")
        self._setup_cache_directory()
        self._project_path = self._init_project_path()
        self._project_config = self._init_project_config()
        self._project_version = self._init_project_version()

    def _setup_cache_directory(self):
        if not os.path.exists(self._cache_directory):
            os.mkdir(self._cache_directory)

    def _init_project_path(self):
        result_dict = dict()
        result_dict["config"] = os.path.join(self._code_entrance_path, "config.json")
        result_dict["log"] = os.path.join(self._cache_directory, "log.txt")
        result_dict["progress"] = os.path.join(self._cache_directory, "progress.json")
        return result_dict

    def _init_project_config(self):
        file_content = self._read_file_content(self._project_path["config"])
        return json.loads(file_content) if file_content else None

    def _init_project_version(self):
        version_description_path = os.path.join(self._code_entrance_path, "RELEASE_VERSION")
        return self._read_file_content(version_description_path)

    def get_project_path(self, key):
        return self._project_path.get(key, None)

    def get_project_config(self):
        return self._project_config

    def get_project_version(self):
        return self._project_version

    def get_static_donate_path(self):
        return os.path.join(self._static_directory, "image", "Payment.png")

    def get_static_cert_path(self):
        return os.path.join(self._static_directory, "cert", "cacert.pem")

    def _read_file_content(self, file_path):
        try:
            reader = open(file_path, 'r')
            content = reader.read()
            reader.close()
            return content
        except Exception as e:
            self._make_message_and_send(str(e))
            return None

    @staticmethod
    def _make_message_and_send(content):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        output_content = "[{}][{}]: {}".format(current_time, "ProjectHelper", content)
        print(output_content)
