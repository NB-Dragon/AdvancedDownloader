#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/22 12:00
# Create User: NB-Dragon
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator


class ActionProgressReceiver(threading.Thread):
    """
    register       : {"mission_uuid": "uuid", "thread": None, "running": False}
    request_result : 如果结果完整，检查是否存在Thread，不存在就创建Thread并启动；否则设置running=False
    start          : 如果running为False, 向info发送request信号, 设置running=True
    pause          : 判断是否存在Thread(mission_uuid)，有则发送停止信号
    stop           : 根据原因分别处理(由具体下载线程发出)
        initiative : 设置thread为空，设置running=False，执行删除逻辑(删除文件: False)
        passive    : 设置thread为空，设置running=False，执行挂起任务
    delete         : 根据running状态分别处理(由用户操作发出)
        true       : 判断是否存在Thread(mission_uuid)，有则发送停止信号，挂起任务
        false      : 执行删除逻辑(删除文件: False|True)
    update         : 根据running状态分别处理，默认重启参数为false(由用户操作发出)
        true       : 判断是否存在Thread(mission_uuid)，有则发送停止信号，修改重启参数，挂起任务
        false      : 向info发送update_mission_config或update_download_name信号
                     根据重启参数，按需向info发送request信号

    备注：
    需要挂起任务的时机：逻辑中明确需要
    执行删除逻辑: 删除注册过的内容，向message.write发送结束信号
    执行挂起任务：每个mission_uuid有对应的挂起数据数组，把所有消息重新压栈到消息队列中
    """
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._mission_info_dict = dict()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            signal_type, mission_uuid = message_dict["type"], message_dict["mission_uuid"]
            self._handle_message_detail(signal_type, mission_uuid, message_dict["detail"])

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, signal_type, mission_uuid, message_detail):
        if signal_type == "register":
            pass

    def _send_analyze_action(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("message.analyze")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    def _send_write_action(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("message.write")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
