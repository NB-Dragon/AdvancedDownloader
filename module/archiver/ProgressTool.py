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

    def update_download_progress(self, mission_dict: dict, mission_uuid, update_settings: dict):
        section_uuid = update_settings["section_uuid"]
        section_progress = mission_dict[mission_uuid]["section_info"][section_uuid]["current_progress"]
        write_position, write_length = update_settings["write_position"], update_settings["write_length"]
        match_section = self._pop_match_section(section_progress, write_position)
        if isinstance(match_section, list):
            update_section = self._update_match_section(match_section, write_position, write_length)
            section_progress.extend(update_section)
            section_progress.sort(key=lambda x: x[0])

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
    def _pop_match_section(all_section, position):
        for index in range(len(all_section)):
            if len(all_section[index]) == 1:
                return all_section.pop(index)
            elif all_section[index][0] <= position <= all_section[index][1]:
                return all_section.pop(index)
        return None

    @staticmethod
    def _update_match_section(match_section, position, length):
        if len(match_section) == 1:
            return [[match_section[0] + length]] if match_section[0] == position else []
        else:
            result_list = []
            if match_section[0] <= position - 1:
                result_list.append([match_section[0], position - 1])
            if position + length <= match_section[1]:
                result_list.append([position + length, match_section[1]])
            return result_list

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
