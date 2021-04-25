#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/25 12:00
# Create User: NB-Dragon
from schema.Charset.handles.AsciiHandler import AsciiHandler


class GB18030(AsciiHandler):
    def __init__(self):
        super().__init__()
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\x81-\xFE][\x40-\x7E\x80-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\x81-\xFE][\x30-\x39][\x81-\xFE][\x30-\x39]", "length": 4})
