#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import codecs
from core.charset.encoding.ASCII import ASCII
from core.charset.encoding.UTF8 import UTF8
from core.charset.encoding.GB2312 import GB2312
from core.charset.encoding.GBK import GBK
from core.charset.encoding.GB18030 import GB18030
from core.charset.encoding.UTF32 import UTF32
from core.charset.encoding.UTF16 import UTF16


class CharsetDetector(object):
    def __init__(self):
        self._detector_list = list()
        self._init_detector_list()

    def _init_detector_list(self):
        self._detector_list.append(ASCII())
        self._detector_list.append(UTF8())
        self._detector_list.append(GB2312())
        self._detector_list.append(GBK())
        self._detector_list.append(GB18030())
        self._detector_list.append(UTF32())
        self._detector_list.append(UTF16())

    def detect(self, byte_string):
        byte_string = byte_string[0:1000]
        check_result = self._check_bom_header(byte_string)
        if check_result is None:
            check_result = self._check_deeper_content(byte_string)
        return check_result

    @staticmethod
    def _check_bom_header(byte_string: bytes):
        if byte_string.startswith(codecs.BOM_UTF8):
            return {"encoding": "UTF-8", "confidence": 1.0}
        elif byte_string.startswith(codecs.BOM_UTF32_LE):
            return {"encoding": "UTF-32", "confidence": 1.0}
        elif byte_string.startswith(codecs.BOM_UTF32_BE):
            return {"encoding": "UTF-32", "confidence": 1.0}
        elif byte_string.startswith(codecs.BOM_UTF16_LE):
            return {"encoding": "UTF-16", "confidence": 1.0}
        elif byte_string.startswith(codecs.BOM_UTF16_BE):
            return {"encoding": "UTF-16", "confidence": 1.0}
        elif byte_string.startswith(b'\xFE\xFF\x00\x00'):
            return {"encoding": "X-ISO-10646-UCS-4-3412", "confidence": 1.0}
        elif byte_string.startswith(b'\x00\x00\xFF\xFE'):
            return {"encoding": "X-ISO-10646-UCS-4-3412", "confidence": 1.0}
        return None

    def _check_deeper_content(self, byte_string: bytes):
        maximum_detector = {"encoding": "iso-8859-1", "confidence": 0}
        for detector in self._detector_list:
            detect_result = detector.detect(byte_string)
            if detect_result["confidence"] == 1:
                return detect_result
            if detect_result["confidence"] > maximum_detector["confidence"]:
                maximum_detector = detect_result
        return maximum_detector
