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
        if os.path.isfile(self._cache_inner_file["mission"]):
            file_content = self._get_file_content(self._cache_inner_file["mission"])
            if len(file_content):
                return json.loads(file_content)
            else:
                return {}
        else:
            return {}

    def set_mission_state(self, mission_dict: dict):
        json_content = json.dumps(mission_dict)
        self._set_file_content(self._cache_inner_file["mission"], json_content)

    def get_cache_file(self, file_type: str):
        return self._cache_inner_file[file_type]

    def get_code_entrance_path(self):
        return self._code_entrance_path

    def get_donate_image_path(self):
        return os.path.join(self._code_entrance_path, "static", "image", "Payment.png")

    def _check_cache_directory(self):
        if not os.path.exists(self._cache_directory):
            os.mkdir(self._cache_directory)

    def _setup_cache_inner_file(self):
        self._cache_inner_file = dict()
        self._cache_inner_file["mission"] = os.path.join(self._cache_directory, "mission.json")
        self._cache_inner_file["log"] = os.path.join(self._cache_directory, "log.txt")

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
