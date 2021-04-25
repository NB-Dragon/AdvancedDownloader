#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
from schema.Charset.handles.AsciiHandler import AsciiHandler


class UTF8(AsciiHandler):
    def __init__(self):
        super().__init__()
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\xC0-\xDF][\x80-\xBF]{1}", "length": 2})
        self._rule_list.append({"regex": b"[\xE0-\xEF][\x80-\xBF]{2}", "length": 3})
        self._rule_list.append({"regex": b"[\xF0-\xF7][\x80-\xBF]{3}", "length": 4})
        self._rule_list.append({"regex": b"[\xF8-\xFB][\x80-\xBF]{4}", "length": 5})
        self._rule_list.append({"regex": b"[\xFC-\xFD][\x80-\xBF]{5}", "length": 6})
