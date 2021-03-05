#!/usr/bin/env python
#  coding=utf-8
#  Author:  Yoge
#  Time:  2021/3/5

import time
import numpy as np
from datetime import datetime
from playwright.sync_api import sync_playwright


def load_data(playwright, keyword="", max_page=30, headless=True):
    browser = playwright.firefox.launch(headless=headless)
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    # Go to http://wukong.mz.gold/
    page.goto("http://wukong.mz.gold/")
    page.wait_for_selector("[placeholder=\"请输入关键词\"]")
    page.click("[placeholder=\"请输入关键词\"]")
    # Fill [placeholder="请输入关键词"]
    time.sleep(0.1)
    page.fill("[placeholder=\"请输入关键词\"]", keyword)
    time.sleep(0.1)
    # Press Enter
    page.press("[placeholder=\"请输入关键词\"]", "Enter")
    # ---------------------
    time.sleep(1)
    try:
        page.wait_for_selector("[id=\"goods_list\"]", timeout=3000)
        for i in range(max_page):
            time.sleep(1)
            page.press("[placeholder=\"请输入关键词\"]", "PageDown")
        ele = page.wait_for_selector("[id=\"goods_list\"]")
        tc = ele.text_content()
        return tc
    except:
        print(keyword, "超时,可能无数据")
        return ""
    finally:
        context.close()
        browser.close()

def parse_raw_data(raw_data):
    raw = raw_data.strip().split("呼叫")
    data = []
    for row in raw:
        if not row:
            continue
        data.append(row.strip().split())
    return data


def exact_price(price_data):
    if price_data.isdigit():
        return int(price_data)
    else:
        res = []
        for c in price_data[::-1]:
            if c.isdigit():
                res.append(c)
            else:
                break
        res.reverse()
        return int("".join(res) or 0)


def analyze_data(data, the_date=None):
    if not the_date:
        the_date = datetime.now()
    price_data = []
    for row in data:
        if row[0] != the_date.strftime("%m-%d"):
            continue
        price = exact_price(row[-2])
        price_data.append(price)

    stat_count = len(price_data)
    if not price_data:
        price_data = [0]
    result = dict(
        mean_price=np.mean(price_data),
        mode_price=np.argmax(np.bincount(price_data)),
        max_price=max(price_data),
        min_price=min(price_data),
        stat_count=stat_count,
    )
    return result


def fetch_product_price_stat(product, max_page=10):
    with sync_playwright() as playwright:
        raw_data = load_data(playwright, product, max_page=max_page)
        data = parse_raw_data(raw_data)
        return analyze_data(data)

