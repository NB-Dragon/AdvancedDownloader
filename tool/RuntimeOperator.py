#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import os
import sys
import json


class RuntimeOperator(object):
    def __init__(self):
        self._code_entrance_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self._cache_directory = os.path.join(self._code_entrance_path, ".cache")
        self._check_cache_directory()
        self._setup_cache_inner_file()

    def get_mission_state(self):
        mission_cache_path = self._get_cache_file("mission")
        return self._get_dict_from_file(mission_cache_path)

    def set_mission_state(self, mission_dict: dict):
        mission_cache_path = self._get_cache_file("mission")
        json_content = json.dumps(mission_dict)
        self._set_file_content(mission_cache_path, json_content)

    def append_run_log_content(self, run_log: str):
        run_log_path = self._get_cache_file("log")
        self._append_file_content(run_log_path, run_log)

    def get_content_type_postfix(self):
        content_type_postfix_path = self.get_static_postfix_path()
        return self._get_dict_from_file(content_type_postfix_path)

    def get_static_donate_image_path(self):
        return os.path.join(self._code_entrance_path, "static", "image", "Payment.png")

    def get_static_cert_path(self):
        return os.path.join(self._code_entrance_path, "static", "cert", "ca-cert.pem")

    def get_static_postfix_path(self):
        return os.path.join(self._code_entrance_path, "static", "config", "postfix.json")

    def _get_cache_file(self, file_type: str):
        return self._cache_inner_file[file_type]

    def _check_cache_directory(self):
        if not os.path.exists(self._cache_directory):
            os.mkdir(self._cache_directory)

    def _setup_cache_inner_file(self):
        self._cache_inner_file = dict()
        self._cache_inner_file["mission"] = os.path.join(self._cache_directory, "mission.json")
        self._cache_inner_file["log"] = os.path.join(self._cache_directory, "log.txt")

    def _get_dict_from_file(self, file_path):
        if os.path.isfile(file_path):
            file_content = self._get_file_content(file_path)
            if len(file_content):
                return json.loads(file_content)
            else:
                return {}
        else:
            return {}

    @staticmethod
    def _get_file_content(file_path):
        reader = open(file_path, 'r')
        content = reader.read()
        reader.close()
        return content

    @staticmethod
    def _set_file_content(file_path, content):
        writer = open(file_path, 'w')
        writer.write(content)
        writer.close()

    @staticmethod
    def _append_file_content(file_path, content):
        writer = open(file_path, 'a')
        writer.write(content)
        writer.close()
