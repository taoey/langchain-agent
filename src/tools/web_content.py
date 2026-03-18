#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time           : 2026-03-17 14:34
@Author         : tao
@Python Version : 3.13.3
@Desc           : None
"""

from langchain.tools import tool
from src.utils.tool_web_client import get_web_content

@tool
def get_url_web_content(url:str) ->str:
    """
    args:
        url: 要访问的网页URL
    return:
        网页内容
    """
    content = get_web_content(url)
    # print(content)
    return content
