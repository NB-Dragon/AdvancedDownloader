#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/10 12:30
# Create User: NB-Dragon
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
        self._mission_dict = dict()
        # mission_dict = {"mission_uuid": {"mission_info": dict, "download_info": dict, "running": bool}}
        self._thread_and_action_dict = dict()
        # thread_and_action_dict = {"mission_uuid": {"thread": threading.Thread, "action":[]}}
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
                self._handle_thread_signal(message_detail["mission_uuid"], message_detail["signal"])
            self._process_the_first_action(message_detail["mission_uuid"])
        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize() or self._has_mission_alive()

    def _has_mission_alive(self):
        alive_mission = [key for key, value in self._mission_dict.items() if value["running"]]
        return len(alive_mission) == 0

    def _handle_operate_action(self, mission_uuid, mission_detail):
        handle_type = mission_detail["type"]
        if handle_type == "create":
            self._mission_dict[mission_uuid] = mission_detail["value"]
        elif handle_type == "open":
            self._thread_and_action_dict[mission_uuid]["action"].append("open")
        elif handle_type == "start":
            self._thread_and_action_dict[mission_uuid]["action"].append("start")
        elif handle_type == "pause":
            self._thread_and_action_dict[mission_uuid]["action"].append("pause")
        elif handle_type == "delete":
            self._thread_and_action_dict[mission_uuid]["action"].append("delete")

    def _handle_thread_signal(self, mission_uuid, signal_type):
        if signal_type == "stop":
            self._synchronize_mission_stop_state(mission_uuid)
            self._synchronize_mission_download_info(mission_uuid)
        elif signal_type == "finish":
            self._synchronize_mission_stop_state(mission_uuid)
            self._append_action_open_if_needed(mission_uuid)

    def _process_the_first_action(self, mission_uuid):
        action_list = self._thread_and_action_dict[mission_uuid]["action"]
        if len(action_list):
            current_action = action_list.pop(0)
            if current_action == "open":
                self._do_with_signal_open(mission_uuid)
            elif current_action == "start":
                self._do_with_signal_start(mission_uuid)
            elif current_action == "pause":
                self._do_with_signal_pause(mission_uuid)
            elif current_action == "delete":
                self._do_with_signal_delete(mission_uuid)

    def _do_with_signal_open(self, mission_uuid):
        sava_file = self._mission_dict[mission_uuid]["download_info"]["save_path"]
        message_dict = dict()
        message_dict["action"] = "open"
        detail_info = {"type": "open", "path": sava_file}
        message_dict["value"] = {"mission_uuid": mission_uuid, "detail": detail_info}
        self._all_listener["message"]["queue"].put(message_dict)

    def _do_with_signal_start(self, mission_uuid):
        self._thread_and_action_dict[mission_uuid]["thread"] = self._create_mission_thread(mission_uuid)
        self._thread_and_action_dict[mission_uuid]["thread"].start()
        self._mission_dict[mission_uuid]["running"] = True

    def _do_with_signal_pause(self, mission_uuid):
        if self._thread_and_action_dict[mission_uuid]["thread"]:
            self._thread_and_action_dict[mission_uuid]["thread"].send_stop_state()

    def _do_with_signal_delete(self, mission_uuid):
        if self._mission_dict[mission_uuid]["running"]:
            self._thread_and_action_dict[mission_uuid]["action"].append("delete")
            self._do_with_signal_pause(mission_uuid)
        else:
            self._mission_dict.pop(mission_uuid)
            self._thread_and_action_dict.pop(mission_uuid)

    def _synchronize_mission_stop_state(self, mission_uuid):
        self._mission_dict[mission_uuid]["running"] = False
        self._thread_and_action_dict[mission_uuid]["thread"] = None

    def _synchronize_mission_download_info(self, mission_uuid):
        history_mission_dict = self._runtime_operator.get_mission_state()
        self._mission_dict[mission_uuid]["download_info"] = history_mission_dict[mission_uuid]["download_info"]

    def _append_action_open_if_needed(self, mission_uuid):
        current_mission_info = self._mission_dict[mission_uuid]["mission_info"]
        if current_mission_info["open_after_finish"]:
            self._thread_and_action_dict[mission_uuid]["action"].append("open")

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
