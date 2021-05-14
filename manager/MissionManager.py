#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/10 12:30
# Create User: NB-Dragon
import json
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator
from listener.ThreadMessageDistributor import ThreadMessageDistributor


class MissionManager(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._mission_info_dict = dict()
        self._mission_state_dict = dict()
        self._init_all_listener()

    def run(self) -> None:
        self._start_all_listener()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_detail = message_dict["detail"]
            if message_dict["action"] == "operate":
                self._handle_operate_action(message_detail["mission_uuid"], message_detail["detail"])
            elif message_dict["action"] == "signal":
                self._handle_thread_signal(message_detail["mission_uuid"], message_detail["detail"])
            self._process_current_action(message_detail["mission_uuid"])
        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize() or self._has_mission_alive()

    def _has_mission_alive(self):
        alive_mission = [value["running"] for value in self._mission_state_dict.values()]
        return True in alive_mission

    def _handle_operate_action(self, mission_uuid, message_detail):
        handle_type = message_detail["type"]
        if handle_type == "create":
            self._insert_mission_info_item(mission_uuid, message_detail["value"])
            self._insert_mission_state_item(mission_uuid)
        elif handle_type == "open":
            self._mission_state_dict[mission_uuid]["action"] = "open"
        elif handle_type == "start":
            self._mission_state_dict[mission_uuid]["action"] = "start"
        elif handle_type == "pause":
            self._mission_state_dict[mission_uuid]["action"] = "pause"
        elif handle_type == "delete":
            self._mission_state_dict[mission_uuid]["action"] = "delete"

    def _handle_thread_signal(self, mission_uuid, signal_detail):
        signal_type = signal_detail["type"]
        if signal_type == "stop":
            self._synchronize_mission_stop_state(mission_uuid)
            self._synchronize_mission_download_info(mission_uuid, signal_detail["download_info"])
        elif signal_type == "finish":
            self._synchronize_mission_stop_state(mission_uuid)
            self._append_action_open_if_needed(mission_uuid)
        elif signal_type == "update":
            self._synchronize_mission_download_info(mission_uuid, signal_detail["download_info"])

    def _insert_mission_info_item(self, mission_uuid, mission_value):
        mission_info, download_info = mission_value["mission_info"], mission_value["download_info"]
        self._mission_info_dict[mission_uuid] = dict()
        self._mission_info_dict[mission_uuid]["mission_info"] = json.loads(json.dumps(mission_info))
        self._mission_info_dict[mission_uuid]["download_info"] = json.loads(json.dumps(download_info))

    def _insert_mission_state_item(self, mission_uuid):
        self._mission_state_dict[mission_uuid] = dict()
        self._mission_state_dict[mission_uuid]["thread"] = None
        self._mission_state_dict[mission_uuid]["action"] = None
        self._mission_state_dict[mission_uuid]["retry"] = 0
        self._mission_state_dict[mission_uuid]["running"] = False

    def _process_current_action(self, mission_uuid):
        current_action = self._mission_state_dict[mission_uuid]["action"]
        if current_action:
            self._mission_state_dict[mission_uuid]["action"] = None
            if current_action == "open":
                self._do_with_signal_open(mission_uuid)
            elif current_action == "start":
                self._do_with_signal_start(mission_uuid)
            elif current_action == "pause":
                self._do_with_signal_pause(mission_uuid)
            elif current_action == "delete":
                self._do_with_signal_delete(mission_uuid)

    def _do_with_signal_open(self, mission_uuid):
        if self._mission_info_dict[mission_uuid]["download_info"]:
            sava_file = self._mission_info_dict[mission_uuid]["download_info"]["full_path"]
            message_dict = {"action": "open", "value": {"mission_uuid": mission_uuid, "detail": None}}
            message_dict["value"]["detail"] = {"type": "open", "path": sava_file}
            self._all_listener["message"]["queue"].put(message_dict)

    def _do_with_signal_start(self, mission_uuid):
        mission_thread = self._create_mission_thread(mission_uuid)
        if mission_thread is not None:
            self._mission_state_dict[mission_uuid]["running"] = True
            self._mission_state_dict[mission_uuid]["thread"] = mission_thread
            self._mission_state_dict[mission_uuid]["thread"].start()

    def _do_with_signal_pause(self, mission_uuid):
        if self._mission_state_dict[mission_uuid]["thread"]:
            self._mission_state_dict[mission_uuid]["thread"].send_stop_state()

    def _do_with_signal_delete(self, mission_uuid):
        if self._mission_state_dict[mission_uuid]["running"]:
            self._mission_state_dict[mission_uuid]["action"] = "delete"
            self._do_with_signal_pause(mission_uuid)
        else:
            self._mission_info_dict.pop(mission_uuid)
            self._mission_state_dict.pop(mission_uuid)

    def _synchronize_mission_stop_state(self, mission_uuid):
        self._mission_state_dict[mission_uuid]["running"] = False
        self._mission_state_dict[mission_uuid]["thread"] = None

    def _synchronize_mission_download_info(self, mission_uuid, download_info):
        self._mission_info_dict[mission_uuid]["download_info"] = download_info

    def _append_action_open_if_needed(self, mission_uuid):
        current_mission_info = self._mission_info_dict[mission_uuid]["mission_info"]
        if current_mission_info["open_after_finish"]:
            self._mission_state_dict[mission_uuid]["action"] = "open"

    def _create_mission_thread(self, mission_uuid):
        if self._mission_info_dict[mission_uuid]["download_info"] is None:
            if self._mission_state_dict[mission_uuid]["retry"] < 3:
                self._mission_state_dict[mission_uuid]["action"] = "start"
                self._mission_state_dict[mission_uuid]["retry"] += 1
                # 这里发送信号，申请解析获取对应协议的`download_info`
            return None
        else:
            # 这里从任务生成器获取下载线程
            return None

    def _init_all_listener(self):
        """
        message : handle all message with action
        """
        self._all_listener = dict()
        thread_message_distributor = ThreadMessageDistributor(self._runtime_operator)
        thread_message_queue = thread_message_distributor.get_message_queue()
        self._all_listener["message"] = {"receiver": thread_message_distributor, "queue": thread_message_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()
