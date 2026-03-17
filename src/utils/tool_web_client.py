#!/bin/env python3
# encoding=utf8
""" tools """
import time
import os
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.utils import tool_file
from bs4 import BeautifulSoup
import os
import re
from selenium_stealth import stealth
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig

import asyncio

MAC_WEBDRIVER_PATH = r"/Users/th/Documents/workspace/spider-common/driver/chromedriver-mac-arm64/chromedriver"
# proxy = f"http://127.0.0.1:7890"

# 设定浏览器缓存目录
user_data_dir = "/tmp/chrome_cache"  # Linux/macOS
os.makedirs(user_data_dir, exist_ok=True)


def wait_element_with_retry(driver, css, timeout=10, retry=2):
    print("开始等待元素出现：", css)
    for i in range(retry + 1):
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            questions = soup.select(".faq-question")
            if questions:
                print(questions)
                return questions
            else:
                raise Exception(f"元素 {css} 不存在于页面源代码中")
        except Exception as e:
            print(f"第 {i+1} 次失败: {e}")
            if i < retry:
                driver.refresh()
                time.sleep(2)  # 等待一段时间再重试
            else:
                return None


def safe_execute_script(driver, script, *args):
    """安全执行 JS，自动处理意外弹出的 alert"""
    try:
        return driver.execute_script(script, *args)
    except UnexpectedAlertPresentException:
        # 处理 alert
        try:
            alert = driver.switch_to.alert
            print(f"⚠️ 检测到 alert，内容: '{alert.text}'，正在关闭...")
            alert.accept()  # 或 dismiss()
        except NoAlertPresentException:
            pass
        # 可选：重试一次（谨慎使用，避免死循环）
        try:
            return driver.execute_script(script, *args)
        except UnexpectedAlertPresentException:
            print("❌ 再次遇到 alert，放弃执行脚本")
            return None


PIC_DIR = "data_pics"
def get_web_with_catch_by_driver(day_change, driver, url):
    """ get_web_with_catch
    day_change : bool, 缓存是否需要天级变化
    func : functions
    """
    today = time.strftime("%Y%m%d", time.localtime())
    if day_change:
        catch_dir = f"cache/{today}/"
    else:
        catch_dir = f"cache/data/"

    domain = url.split("//")[1].split("/")[0]
    catch_dir = os.path.join(catch_dir, domain)
    if not os.path.exists(catch_dir):
        os.makedirs(catch_dir)

    cache_name = f"{url.split('//')[1].replace('/', '_')}.html"
    if len(cache_name) > 200:
        cache_name = tool_file.url_to_filename(cache_name)

    cache_filepath = os.path.join(catch_dir, cache_name)
    if os.path.exists(cache_filepath):
        with open(cache_filepath, "r", encoding="utf-8") as file:
            print("load_from_cache", url)
            return file.read(),cache_filepath
    print("load_from_web", url)
    driver.get(url)
    # 针对某些网站，增加随机等待时间，模拟人类行为
    # 模拟下拉到最后
    # 执行 execute_script 前禁止弹窗
    count = 0
    last_height = safe_execute_script(driver,"return document.body.scrollHeight")

    while True:
        # 缓慢滚动：每次滚动一小段，直到接近底部
        scroll_pause_time = 0.2  # 每次滚动后暂停时间（秒）
        current_scroll = safe_execute_script(driver,"return window.pageYOffset;")
        target_scroll = safe_execute_script(driver,"return document.body.scrollHeight;")
        
        # 逐步滚动（例如每次滚动 1000 像素）
        while current_scroll < target_scroll:
            safe_execute_script(driver,"window.scrollBy(0,2000);")
            time.sleep(scroll_pause_time)
            current_scroll += 2000
            # 更新目标高度（因为可能在滚动中加载了新内容）
            target_scroll = safe_execute_script(driver,"return document.body.scrollHeight;")

        count += 1
        # time.sleep(1)  # 等待新内容充分加载

        # 检查是否到底（高度不再变化）
        new_height = safe_execute_script(driver,"return document.body.scrollHeight")
        if new_height == last_height:
            break

        if count >= 10:
            break

        last_height = new_height

    sleep_time = random.uniform(3,5)
    # wait_element_with_retry(driver, ".faq-question")
    web_content = driver.page_source
    if web_content:
        with open(cache_filepath, "w", encoding="utf-8") as file:
            file.write(web_content)
    

    return web_content,cache_filepath


def get_browser():
    service = Service(MAC_WEBDRIVER_PATH)
    chrome_options = webdriver.ChromeOptions()
    # 禁止加载图片
    prefs = {
        "profile.managed_default_content_settings.images": 2  # 2 表示禁用，1 表示启用
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--disable-web-security")  # 可选
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.binary_location = chrome_binary_location
    # chrome_options.add_argument(f"--proxy-server={proxy}") # 设置代理
    browser = webdriver.Chrome(options=chrome_options, service=service)
    stealth(
        browser,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return browser


def browser_add_cookie(driver, domain, cookie_str):
    driver.get("http://www" + domain)
    for cookie in cookie_str.split("; "):
        if "=" in cookie:
            name, value = cookie.split("=", 1)
            driver.add_cookie({
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain,
                "path": "/"
            })
    driver.refresh()  # 刷新页面以应用新的 Cookie
    return 

def download_image(driver,image_url):
    """ 
    download_image 
    添加缓存判断功能，如果文件已存在则跳过下载
    """
    import requests
    # 网络图片 https://img.haijiaoluv.top/cdn/1/3681040.webp 文件存储路径：img.haijiaoluv.top/3681040.webp
    save_path = image_url.split("//")[1]  # 去掉协议部分
    save_path_list = save_path.split('/')  # 去掉多余的路径部分
    save_path = save_path_list[0] + '/' + save_path_list[-1]
    save_path = os.path.join(PIC_DIR, save_path)
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    if os.path.exists(save_path):
        print(f"Image already exists at {save_path}, skipping download.")
        return

    # 通过driver下载图片，避免反爬虫
    # 图片中可能存在gif图，需要保存为webp格式
    try:
        driver.get(image_url)
        image_data = driver.find_element("tag name", "img").screenshot_as_png
        with open(save_path, "wb") as f:
            f.write(image_data)
        print(f"Image downloaded and saved to {save_path}")
    except Exception as e:
        print(f"Failed to download image from {image_url}. Error: {e}")
    
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()

    return text


def html2markdown(html_content):
    raw_html_url = f"raw:{html_content}"
    config = CrawlerRunConfig()
    async def run():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=raw_html_url, config=config)
            if result.success:
                return result.markdown
    return asyncio.run(run())



def get_web_content(url):
    browser = get_browser()
    html_content, cache_filepath = get_web_with_catch_by_driver(True, browser, url)
    # markdown_content = html2markdown(html_content)
    content = clean_html(html_content)
    browser.quit()
    return content


if __name__ == "__main__":
    browser = get_browser()
    url  = "https://tool.lu/article/"
    html_content, cache_filepath = get_web_with_catch_by_driver(False, browser, url)
    print("hello")
    print(cache_filepath)
    print(html_content)
    markdown_content = html2markdown(html_content)
    print(markdown_content)

    browser.quit()

    