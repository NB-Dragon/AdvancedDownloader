#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import os
import re
import urllib.parse
import urllib3
from math import ceil
from tool.RuntimeOperator import RuntimeOperator


class HTTPHelper(object):
    def __init__(self, mission_uuid):
        self._mission_uuid = mission_uuid

    @staticmethod
    def get_download_file_requirement(headers, link):
        filename = HeaderAnalyser.get_download_file_name(headers, link)
        filesize = HeaderAnalyser.get_download_file_size(headers)
        range_header = HeaderAnalyser.judge_download_range_skill(headers)
        range_skill = isinstance(filesize, int) and range_header
        return {"filename": filename, "filesize": filesize, "range": range_skill}

    @staticmethod
    def get_download_region(current_region_list: list, spare_worker_count: int):
        assert_content = "The length of `current_region_list` needs to be less than or equal to `spare_worker_count`"
        assert len(current_region_list) <= spare_worker_count, assert_content
        mission_distributor = MissionDistributor()
        grant_region_dict = mission_distributor.get_granted_num_by_region_list(current_region_list, spare_worker_count)
        result_list = list()
        for index in range(len(current_region_list)):
            operate_item = grant_region_dict["sorted_list"][index]
            operate_count = grant_region_dict["granted_list"][index]
            result_list.extend(mission_distributor.split_download_region(operate_item, operate_count))
        return sorted(result_list, key=lambda x: x[0])

    @staticmethod
    def get_request_pool_manager(alive_count):
        code_entrance_path = RuntimeOperator().get_code_entrance_path()
        cert_pem_file = os.path.join(code_entrance_path, "static", "cert", "ca-cert.pem")
        return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file, maxsize=alive_count, timeout=10)


class HeaderAnalyser(object):
    @staticmethod
    def get_download_file_name(headers, link):
        content_disposition = headers.get("content-disposition")
        content_type = headers.get("content-type")
        if content_disposition and "filename=" in content_disposition:
            content_item_list = content_disposition.split(";")
            filename_item_list = [item.strip() for item in content_item_list if "filename=" in item]
            first_disposition = filename_item_list[0].split(",")[0]
            filename = re.findall("(?<=filename=).*", first_disposition)[0]
            if re.findall("^[\"].*?[\"]$", filename):
                filename = eval(filename)
        else:
            link_parse_result = urllib.parse.urlparse(link)
            filename = link_parse_result.path.split("/")[-1]
        if content_type and "text/html" in headers.get("content-type"):
            filename = "index.html" if filename == "" else filename
        while re.findall("%[0-9a-fA-F]{2}", filename):
            filename = urllib.parse.unquote(filename)
        return filename

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


class MissionDistributor(object):
    def get_granted_num_by_region_list(self, current_region_list: list, maximum: int):
        sorted_by_region_length = sorted(current_region_list, key=lambda x: x[1] - x[0], reverse=True)
        sum_of_region_list = [x[1] - x[0] + 1 for x in sorted_by_region_length]
        average_of_full_size = ceil(sum(sum_of_region_list) / maximum)
        result_list = self._average_distribute_by_capacity(sum_of_region_list, average_of_full_size, maximum)
        return {"sorted_list": sorted_by_region_length, "granted_list": result_list}

    def split_download_region(self, current_region: list, thread_count: int):
        """
            @:param current_region: (min, max); 0 <= min, max
            @:param count: 0 < count
        """
        content_size = current_region[1] - current_region[0] + 1
        each_small_region_size = self._split_download_size(content_size, thread_count)
        current_position = current_region[0]
        result_list = list()
        for item in each_small_region_size:
            end_position = current_position + item
            result_list.append([current_position, end_position - 1])
            current_position = end_position
        return result_list

    def _average_distribute_by_capacity(self, capacity_weight_list: list, average_number, total_distribution):
        times_of_weight_list = [ceil(x / average_number) for x in capacity_weight_list]
        sum_of_number = sum(times_of_weight_list)
        while sum_of_number > total_distribution:
            number_appearance_dict = self._make_appearance_dict(times_of_weight_list)
            two_max_number = sorted(set(times_of_weight_list), reverse=True)[0:2]
            sub_between_list = two_max_number[0] - two_max_number[1]
            sub_between_num = sum_of_number - total_distribution
            real_to_sub = min(sub_between_list, sub_between_num)
            sub_operate_list = self._split_download_size(real_to_sub, number_appearance_dict[two_max_number[0]])
            for index in range(len(sub_operate_list)):
                times_of_weight_list[index] -= sub_operate_list[index]
            times_of_weight_list = sorted(times_of_weight_list, reverse=True)
            sum_of_number = sum(times_of_weight_list)
        return list(times_of_weight_list)

    @staticmethod
    def _make_appearance_dict(number_list):
        result_dict = {}
        for value in number_list:
            if value in result_dict:
                result_dict[value] += 1
            else:
                result_dict[value] = 1
        return result_dict

    @staticmethod
    def _split_download_size(content_size, thread_count):
        low_base_size = content_size // thread_count
        content_size_list = [low_base_size] * thread_count
        height_size_count = content_size - low_base_size * thread_count
        content_size_list[0:height_size_count] = [low_base_size + 1] * height_size_count
        while 0 in content_size_list:
            content_size_list.remove(0)
        return content_size_list
