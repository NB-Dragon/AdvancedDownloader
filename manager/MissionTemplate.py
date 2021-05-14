#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/12 12:30
# Create User: NB-Dragon
from tools.RuntimeOperator import RuntimeOperator


class MissionTemplate(object):
    def __init__(self, runtime_operator: RuntimeOperator):
        self._runtime_operator = runtime_operator

    def get_standard_mission_info(self, mission_info):
        standard_mission_info = dict()
        default_save_path = self._runtime_operator.get_code_entrance_path()
        standard_mission_info["download_link"] = mission_info.get("download_link")
        standard_mission_info["save_path"] = mission_info.get("save_path", default_save_path)
        standard_mission_info["thread_num"] = mission_info.get("thread_num", 1)
        standard_mission_info["headers"] = mission_info.get("headers", dict())
        standard_mission_info["proxy"] = mission_info.get("proxy", None)
        standard_mission_info["open_after_finish"] = False
        return standard_mission_info

