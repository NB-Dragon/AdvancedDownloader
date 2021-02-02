#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import json
import queue
import threading
from tool.RuntimeOperator import RuntimeOperator


class ActionWriterReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._parent_queue = parent_queue
        self._mission_dict = dict()
        self._writer_and_lock_dict = dict()
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            # {"mission_uuid": str, "detail": Any}
            if message_dict:
                self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _handle_message_detail(self, mission_uuid, mission_detail):
        handle_type = mission_detail.pop("type")
        if handle_type == "write":
            # mission_detail = {"type": "write", "current_region": list, "content": bytes}
            content_info = {"content": mission_detail["content"], "length": len(mission_detail["content"])}
            self._send_speed_size_message(mission_uuid, content_info["length"])
            self._write_bytes_into_file(mission_uuid, mission_detail["current_region"], content_info["content"])
            self._update_mission_region(mission_uuid, mission_detail["current_region"], content_info["length"])
        elif handle_type == "split":
            # mission_detail = {"type": "split", "current_region": list, "update_region": list}
            current_region = mission_detail["current_region"]
            update_region = mission_detail["update_region"]
            self._do_with_mission_split(mission_uuid, current_region, update_region)
        elif handle_type == "register":
            # mission_detail = {"type": "register", "mission_info": dict, "download_info": dict, "lock": Any}
            self._send_speed_register_message(mission_uuid, mission_detail["download_info"])
            self._do_with_mission_register(mission_uuid, mission_detail)
        elif handle_type == "finish":
            # mission_detail = {"type": "finish"}
            self._send_speed_finish_message(mission_uuid)
            self._do_with_mission_finish(mission_uuid)
        self._update_mission_progress()

    def _do_with_mission_split(self, mission_uuid, current_region, update_region):
        all_region = self._mission_dict[mission_uuid]["download_info"]["all_region"]
        all_region.remove(current_region)
        all_region.extend(json.loads(json.dumps(update_region)))
        all_region.sort(key=lambda x: x[0])

    def _do_with_mission_register(self, mission_uuid, mission_detail):
        self._writer_and_lock_dict[mission_uuid] = dict()
        tmp_file_path = mission_detail["download_info"]["tmp_path"]
        self._writer_and_lock_dict[mission_uuid]["writer"] = open(tmp_file_path, 'r+b')
        self._writer_and_lock_dict[mission_uuid]["lock"] = mission_detail.pop("lock")
        # Regenerate mission_detail to ensure the absolute difference of memory addresses.
        self._mission_dict[mission_uuid] = json.loads(json.dumps(mission_detail))

    def _do_with_mission_combine(self, mission_uuid, mission_detail):
        tmp_file_path = self._mission_dict[mission_uuid]["download_info"]["tmp_path"]
        self._writer_and_lock_dict[mission_uuid]["writer"] = open(tmp_file_path, 'r+b')
        self._writer_and_lock_dict[mission_uuid]["lock"] = mission_detail.pop("lock")

    def _do_with_mission_finish(self, mission_uuid):
        self._writer_and_lock_dict[mission_uuid]["writer"].close()
        self._writer_and_lock_dict[mission_uuid]["lock"].release()
        self._writer_and_lock_dict.pop(mission_uuid)
        self._mission_dict.pop(mission_uuid)

    def _update_mission_progress(self):
        self._runtime_operator.set_mission_state(self._mission_dict)

    def _write_bytes_into_file(self, mission_uuid: str, current_region: list, content):
        writer = self._writer_and_lock_dict[mission_uuid]["writer"]
        writer.seek(current_region[0])
        writer.write(content)
        writer.flush()

    def _update_mission_region(self, mission_uuid: str, current_region: list, length):
        all_region = self._mission_dict[mission_uuid]["download_info"]["all_region"]
        correct_region_index = self._find_correct_region_index(all_region, current_region)
        if isinstance(correct_region_index, int):
            modify_region = all_region.pop(correct_region_index)
            modify_region[0] += length
            if len(current_region) == 1 or modify_region[0] <= modify_region[1]:
                all_region.insert(correct_region_index, modify_region)
        mission_range_skill = self._mission_dict[mission_uuid]["download_info"]["file_info"]["range"]
        if len(all_region) == 0 and mission_range_skill:
            self._send_speed_finish_message(mission_uuid)
            self._do_with_mission_finish(mission_uuid)

    @staticmethod
    def _find_correct_region_index(all_region, current_region):
        for index in range(len(all_region)):
            if all_region[index][0] == current_region[0]:
                return index
        return None

    def _send_speed_size_message(self, mission_uuid: str, content_length):
        self._send_speed_info(mission_uuid, {"type": "size", "length": content_length})

    def _send_speed_register_message(self, mission_uuid: str, download_info):
        self._send_speed_info(mission_uuid, {"type": "register", "download_info": download_info})

    def _send_speed_finish_message(self, mission_uuid: str):
        self._send_speed_info(mission_uuid, {"type": "finish"})

    def _send_speed_info(self, mission_uuid: str, detail: dict):
        message_dict = dict()
        message_dict["action"] = "speed"
        message_dict["value"] = {"mission_uuid": mission_uuid, "detail": detail}
        self._parent_queue.put(message_dict)
