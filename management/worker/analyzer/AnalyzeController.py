#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
from management.worker.analyzer.HTTPAnalyzer import HTTPAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class AnalyzeController(object):
    def __init__(self, runtime_operator: RuntimeOperator, worker_message_queue):
        self._runtime_operator = runtime_operator
        self._worker_message_queue = worker_message_queue
        self._init_all_analyzer()

    def _init_all_analyzer(self):
        self._all_analyzer = dict()
        self._all_analyzer["http"] = HTTPAnalyzer
        self._all_analyzer["https"] = HTTPAnalyzer

    def _create_analyzer(self, schema):
        analyzer_class = self._all_analyzer[schema]
        title_message = "schema for '{}' doesn't have method 'get_download_info'.".format(schema)
        assert hasattr(analyzer_class, "get_download_info"), title_message
        return analyzer_class(schema, self._worker_message_queue, self._runtime_operator)

    def get_analyzer_by_schema(self, schema):
        return self._create_analyzer(schema)
