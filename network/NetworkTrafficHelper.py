#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/02/05 10:00
# Create User: NB-Dragon
import math


class NetworkTrafficHelper(object):
    def get_speed_and_progress(self, mission_dict: dict, time_interval: int):
        """
        :param mission_dict:
            Example: {"mission_uuid": {"update_size": 0, "current_size": 0, "expect_size": 0}}
        :param time_interval:
            Example: 0
        :return: {"mission_uuid": str, "progress": str, "speed": str}
        """
        speed_content_list = []
        for mission_uuid, mission_item in mission_dict.items():
            progress = self._get_progress_description(mission_item["current_size"], mission_item["expect_size"])
            speed = self._get_speed_description(mission_item["update_size"], time_interval)
            mission_item["update_size"] = 0
            result_item = {"mission_uuid": mission_uuid, "progress": progress, "speed": speed}
            speed_content_list.append(result_item)
        return speed_content_list

    @staticmethod
    def get_current_finish_size(section_info):
        finish_size = 0
        for value in section_info.values():
            current_progress = value["current_progress"]
            if len(current_progress) == 0:
                finish_size += value["section_size"]
            elif len(current_progress[0]) == 2:
                incomplete_size = sum([item[1] - item[0] + 1 for item in current_progress])
                finish_size += value["section_size"] - incomplete_size
        return finish_size

    @staticmethod
    def _get_progress_description(current_size, expect_size):
        return "{:.2f}%".format(current_size / expect_size * 100) if expect_size else "unknown"

    """
    Refer link: https://www.electropedia.org/iev/iev.nsf/display?openform&ievref=112-01-27
    """

    @staticmethod
    def _get_speed_description(update_size, time_interval):
        update_size_per_second = int(update_size // time_interval) if time_interval else 0
        unit_list = ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
        unit_index = min(8, int(math.log2(update_size_per_second) / 10)) if update_size_per_second else 0
        format_size = update_size_per_second / (1 << unit_index * 10)
        if unit_index > 0:
            return "{:.2f}{}/s".format(format_size, unit_list[unit_index])
        else:
            return "{}{}/s".format(int(format_size), unit_list[unit_index])
