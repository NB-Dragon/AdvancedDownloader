#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/3/15 20:00
# Create User: NB-Dragon
from math import ceil


class SectionMaker(object):
    def get_download_section(self, current_section_list, expect_section_count: int):
        """
            @:param current_section_list: [[min1, max1], [min2, max2], ...];

            @:param expect_section_count: expect_section_count > 0.
        """
        expect_section_count = self._format_final_section_count(len(current_section_list), expect_section_count)
        sorted_section_list = sorted(current_section_list, key=lambda x: x[1] - x[0], reverse=True)
        section_size_list = [self._get_section_size(item) for item in sorted_section_list]
        granted_list = self._generate_new_capacity_with_weight(section_size_list, expect_section_count)
        return self._generate_new_section_with_capacity(sorted_section_list, granted_list)

    def _generate_new_capacity_with_weight(self, capacity_weight_list, maximum_weight):
        average_number = ceil(sum(capacity_weight_list) / maximum_weight)
        capacity_list = [ceil(x / average_number) for x in capacity_weight_list]
        current_weight = sum(capacity_list)
        while current_weight > maximum_weight:
            number_appearance_dict = self._make_appearance_dict(capacity_list)
            two_max_number = sorted(set(capacity_list), reverse=True)[0:2]
            sub_between_list = two_max_number[0] - two_max_number[1]
            sub_between_num = current_weight - maximum_weight
            real_to_sub = min(sub_between_list, sub_between_num)
            sub_operate_list = self._split_download_size(real_to_sub, number_appearance_dict[two_max_number[0]])
            for index in range(len(sub_operate_list)):
                capacity_list[index] -= sub_operate_list[index]
            capacity_list.sort(reverse=True)
            current_weight = sum(capacity_list)
        return capacity_list

    def _generate_new_section_with_capacity(self, section_list, granted_list):
        result_list = list()
        for index in range(len(section_list)):
            current_section, thread_count = section_list[index], granted_list[index]
            result_list.extend(self._split_download_section(current_section, thread_count))
        return sorted(result_list, key=lambda x: x[0])

    def _split_download_section(self, current_section, thread_count: int):
        content_size = self._get_section_size(current_section)
        section_size_list = self._split_download_size(content_size, thread_count)
        return self._generate_sub_section(current_section, section_size_list)

    @staticmethod
    def _format_final_section_count(section_length, expect_length):
        return max(section_length, expect_length)

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
    def _get_section_size(section_item):
        return section_item[1] - section_item[0] + 1

    @staticmethod
    def _split_download_size(content_size, thread_count):
        low_base_size = content_size // thread_count
        content_size_list = [low_base_size] * thread_count
        height_size_count = content_size % thread_count
        content_size_list[0:height_size_count] = [low_base_size + 1] * height_size_count
        while 0 in content_size_list:
            content_size_list.remove(0)
        return content_size_list

    @staticmethod
    def _generate_sub_section(current_section, section_size_list):
        result_list = list()
        current_position = current_section[0]
        for section_size in section_size_list:
            end_position = current_position + section_size
            result_list.append([current_position, end_position - 1])
            current_position = end_position
        return result_list
