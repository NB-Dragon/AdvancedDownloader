#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
from controller.analyzer.HTTPAnalyzer import HTTPAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class AnalyzeController(object):
    def __init__(self):
        self._all_analyser = dict()

    def init_all_analyzer(self, runtime_operator: RuntimeOperator, main_thread_message: queue.Queue):
        self._all_analyser["http"] = HTTPAnalyzer("http", main_thread_message, runtime_operator)
        self._all_analyser["https"] = HTTPAnalyzer("https", main_thread_message, runtime_operator)
        self._check_all_analyzer()

    def _check_all_analyzer(self):
        for analyzer in self._all_analyser.values():
            method = analyzer.get_download_info
            method = analyzer.get_current_finish_size

    def get_analyzer(self, schema):
        return self._all_analyser.get(schema)
