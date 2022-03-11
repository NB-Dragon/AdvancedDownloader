#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import re
from core.util.HTTPContentDisposition import HTTPContentDisposition


class HTTPContentType(object):
    def __init__(self):
        self._content_position = HTTPContentDisposition()

    """
    Refer link: https://www.rfc-editor.org/rfc/rfc2231.html#section-2
    """

    def get_type_result(self, content_disposition: str):
        analyze_result = self._content_position.get_disposition_result(content_disposition)
        analyze_result["param"] = self._combine_continue_parameter(analyze_result["param"])
        return analyze_result

    """
    Refer link: https://www.rfc-editor.org/rfc/rfc2231#section-4.1
    """

    @staticmethod
    def _combine_continue_parameter(decode_parm_dict: dict):
        result_dict, indexing_dict = dict(), dict()
        for key, value in decode_parm_dict.items():
            match_result = re.findall("^([^*]+)\\*(\\d+)\\*?$", key)
            if len(match_result):
                token_name, index = match_result[0]
                if token_name not in indexing_dict:
                    indexing_dict[token_name] = dict()
                indexing_dict[token_name][index] = decode_parm_dict[key]
            else:
                result_dict[key] = value
        for key, value in indexing_dict.items():
            value_list = dict(sorted(value.items(), key=lambda item: int(item[0]))).values()
            result_dict[key] = "".join(value_list)
        return result_dict
