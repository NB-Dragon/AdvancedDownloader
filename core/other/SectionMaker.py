#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/3/15 20:00
# Create User: NB-Dragon
from math import ceil


class SectionMaker(object):
    def get_download_section(self, current_section_list, expect_distribute_count: int):
        """
            @:param current_section_list: [[min1, max1], [min2, max2], ...];

            @:param expect_distribute_count: expect_distribute_count > 0;

            @:argument len(current_section_list) <= expect_distribute_count.
        """
        assert_content = "require len(current_section_list) <= expect_distribute_count."
        assert len(current_section_list) <= expect_distribute_count, assert_content
        sorted_list = sorted(current_section_list, key=lambda x: x[1] - x[0], reverse=True)
        section_capacity_list = [x[1] - x[0] + 1 for x in sorted_list]
        granted_list = self._generate_new_capacity_with_weight(section_capacity_list, expect_distribute_count)
        return self._generate_new_section_with_capacity(sorted_list, granted_list)

    def _generate_new_capacity_with_weight(self, capacity_weight_list, weight_maximum):
        average_number = ceil(sum(capacity_weight_list) / weight_maximum)
        capacity_list = [ceil(x / average_number) for x in capacity_weight_list]
        sum_of_weight = sum(capacity_list)
        while sum_of_weight > weight_maximum:
            number_appearance_dict = self._make_appearance_dict(capacity_list)
            two_max_number = sorted(set(capacity_list), reverse=True)[0:2]
            sub_between_list = two_max_number[0] - two_max_number[1]
            sub_between_num = sum_of_weight - weight_maximum
            real_to_sub = min(sub_between_list, sub_between_num)
            sub_operate_list = self._split_download_size(real_to_sub, number_appearance_dict[two_max_number[0]])
            for index in range(len(sub_operate_list)):
                capacity_list[index] -= sub_operate_list[index]
            capacity_list.sort(reverse=True)
            sum_of_weight = sum(capacity_list)
        return capacity_list

    def _generate_new_section_with_capacity(self, section_list, granted_list):
        result_list = list()
        for index in range(len(section_list)):
            operate_item = section_list[index]
            operate_count = granted_list[index]
            result_list.extend(self._split_download_section(operate_item, operate_count))
        return sorted(result_list, key=lambda x: x[0])

    def _split_download_section(self, current_section, thread_count: int):
        content_size = current_section[1] - current_section[0] + 1
        each_section_size = self._split_download_size(content_size, thread_count)
        current_position = current_section[0]
        result_list = list()
        for item in each_section_size:
            end_position = current_position + item
            result_list.append([current_position, end_position - 1])
            current_position = end_position
        return result_list

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
