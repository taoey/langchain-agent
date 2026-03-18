#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time           : 2026-03-17 15:49
@Author         : tao
@Python Version : 3.13.3
@Desc           : None
"""

import time

from langchain.tools import tool
@tool
def get_current_time() -> str:
    """获取当前时间

    Returns:
        str: 当前时间的字符串表示
    """
    return "当前时间是: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())