#!/usr/bin/env python
#  coding=utf-8
#  Author:  Yoge
#  Time:  2021/3/5


def analyze_data(data, the_date=None):
    if not the_date:
        the_date = datetime.now()
    price_data = []
    for row in data:
        if row[0] != the_date.strftime("%m-%d"):
            continue
        price = exact_price(row[-2])
        price_data.append(price)

    result = dict(
        mean_price=np.mean(price_data),
        mode_price=np.argmax(np.bincount(price_data)),
        max_price=max(price_data),
        min_price=min(price_data),
        stat_count=len(price_data),
    )
    return result


def main():
    keyword = "娇韵诗 隔离粉 50ml"
    with sync_playwright() as playwright:
        raw_data = load_data(playwright, keyword, max_page=10)
        data = parse_raw_data(raw_data)
        print(analyze_data(data))

main()