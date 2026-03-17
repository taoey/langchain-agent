#!/bin/env python3
# encoding=utf8
""" tools """
import time
import os
import pandas as pd
import hashlib

def save_to_file(file_name, all_rows):
    """ save_to_file """
    today = time.strftime("%Y%m%d", time.localtime())
    export_dir = f"data/{today}"
    export_filename = f"{file_name}.csv"
    export_filepath = os.path.join(export_dir, export_filename)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    df = pd.DataFrame(all_rows)
    df.to_csv(export_filepath, sep="\t", index=False, header=False, encoding="utf-8")
    return export_filepath




def url_to_filename(url, suffix=".html"):
    # 可选：标准化 URL（如移除 fragment）
    # url = url.split('#')[0]
    
    # 使用 MD5 生成固定长度的文件名（32位十六进制）
    hash_name = hashlib.md5(url.encode('utf-8')).hexdigest()
    return hash_name + suffix
