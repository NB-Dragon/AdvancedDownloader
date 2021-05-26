#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/20 10:00
# Create User: anonymous
from manager.MissionActionDistributor import MissionActionDistributor
from tools.RuntimeOperator import RuntimeOperator

if __name__ == '__main__':
    runtime_operator = RuntimeOperator()
    mission_action_distributor = MissionActionDistributor(runtime_operator)
    mission_action_queue = mission_action_distributor.get_message_queue()
    mission_action_distributor.start()

    mission_action_queue.put(None)
