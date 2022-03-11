#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import json
import os


class ProgressTool(object):
    def __init__(self, project_helper):
        self._project_helper = project_helper

    def get_download_progress(self):
        progress_file_path = self._project_helper.get_project_path("progress")
        return self._get_dict_from_file(progress_file_path)

    def set_download_progress(self, mission_dict: dict):
        progress_file_path = self._project_helper.get_project_path("progress")
        json_content = json.dumps(mission_dict)
        self._set_file_content(progress_file_path, json_content)

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
