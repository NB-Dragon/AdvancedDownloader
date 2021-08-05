#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
from management.mission.thread.HTTPThread import HTTPThread
from tools.RuntimeOperator import RuntimeOperator


class ThreadController(object):
    def __init__(self, runtime_operator: RuntimeOperator, mission_message_queue):
        self._runtime_operator = runtime_operator
        self._mission_message_queue = mission_message_queue
        self._init_all_thread()

    def _init_all_thread(self):
        self._all_thread = dict()
        self._all_thread["http"] = HTTPThread
        self._all_thread["https"] = HTTPThread

    def _create_thread(self, schema):
        thread_class = self._all_thread[schema]
        title_message = "schema for '{}' doesn't have method 'start_download_mission'.".format(schema)
        assert hasattr(thread_class, "start_download_mission"), title_message
        return thread_class(schema, self._mission_message_queue, self._runtime_operator)

    def get_thread_by_schema(self, schema):
        return self._create_thread(schema)
