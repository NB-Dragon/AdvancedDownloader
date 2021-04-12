#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import re
import urllib.parse
import urllib3
from tool.RuntimeOperator import RuntimeOperator


class HTTPHelper(object):
    @staticmethod
    def get_download_file_requirement(headers, link):
        filename = HeaderAnalyser().get_download_file_name(headers, link)
        filesize = HeaderAnalyser().get_download_file_size(headers)
        range_header = HeaderAnalyser().judge_download_range_skill(headers)
        range_skill = isinstance(filesize, int) and range_header
        return {"filename": filename, "filesize": filesize, "range": range_skill}

    @staticmethod
    def get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/&=?%;@+$,~")

    @staticmethod
    def get_request_pool_manager(alive_count):
        cert_pem_file = RuntimeOperator().get_static_cert_path()
        return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file, maxsize=alive_count, timeout=15)


class HeaderAnalyser(object):
    def get_download_file_name(self, headers, link):
        content_disposition = headers.get("content-disposition")
        content_type = headers.get("content-type")
        if content_disposition and "filename=" in content_disposition:
            filename = self._get_file_name_from_content_disposition(content_disposition)
        else:
            link_parse_result = urllib.parse.urlparse(link)
            filename = link_parse_result.path.split("/")[-1]
        filename = self._get_default_file_name(content_type, filename)
        while re.findall("%[0-9a-fA-F]{2}", filename):
            filename = urllib.parse.unquote(filename)
        return filename

    @staticmethod
    def _get_file_name_from_content_disposition(content_disposition):
        content_item_list = content_disposition.split(";")
        filename_item_list = [item.strip() for item in content_item_list if "filename=" in item]
        first_disposition = filename_item_list[0].split(",")[0]
        filename = re.findall("(?<=filename=).*", first_disposition)[0]
        if re.findall("^[\"].*?[\"]$", filename):
            filename = eval(filename)
        """
            Fix the decoding problem: https://github.com/pypa/warehouse/issues/9368
        """
        try:
            import chardet
            byte_string = filename.encode("iso-8859-1")
            real_encoding = chardet.detect(byte_string)["encoding"]
            filename = byte_string.decode(real_encoding)
        except ModuleNotFoundError:
            pass
        return filename

    @staticmethod
    def _get_default_file_name(content_type, current_name):
        if content_type and "text/html" in content_type:
            current_name = "unknown.html" if "." not in current_name else current_name
        default_name = "unknown.dat" if current_name == "" else current_name
        return default_name

    @staticmethod
    def get_download_file_size(headers):
        if "content-range" in headers:
            return int(re.findall("bytes \\d+-\\d+/(\\d+)", headers["content-range"])[0])
        elif "content-length" in headers:
            return int(headers.get("content-length"))
        else:
            return None

    @staticmethod
    def judge_download_range_skill(headers):
        return "content-range" in headers or "accept-ranges" in headers


class HeaderGenerator(object):
    @staticmethod
    def get_header_user_agent():
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0 (X11; Linux x86_64)")
        user_agent_list.append("AppleWebKit/537.36 (KHTML, like Gecko)")
        user_agent_list.append("AdvancedDownloader/0.5.7")
        return {"User-Agent": " ".join(user_agent_list)}

    @staticmethod
    def get_header_baidu_net_disk(bduss: str):
        headers = dict()
        headers["User-Agent"] = "netdisk"
        headers["Cookie"] = "BDUSS={}".format(bduss)
        return headers

    @staticmethod
    def make_dict_from_headers(content):
        each_value_list = content.split("\n")
        result_dict = {}
        for key_value in each_value_list:
            if key_value == "": continue
            key, value = key_value.split(":", 1)
            result_dict[key.strip()] = value.strip()
        return result_dict
