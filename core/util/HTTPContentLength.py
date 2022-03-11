#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import re


class HTTPContentLength(object):
    """
    Refer link:
    Content-Length: https://www.rfc-editor.org/rfc/rfc2616.html#section-14.13
    Content-Range: https://www.rfc-editor.org/rfc/rfc2616.html#section-14.16
    """

    @staticmethod
    def get_length_result(content_length: str, content_range: str):
        if content_range and len(content_range):
            match_result = re.findall("^bytes\\s+\\d+-\\d+/(\\d+)$", content_range)
            return int(match_result[0]) if len(match_result) else None
        elif content_length and len(content_length):
            return int(content_length)
        return None
