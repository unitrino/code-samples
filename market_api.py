import requests, datetime


def get_volume_from_bitrex(btc_market, timestamp_from):
    url = 'https://python:3xq2jFVpPDFkmQmGadvr8qE3@blockchainflow.io:899/api/1.0/csv/volume/?market={}&exchange' \
          '=Bittrex&timestamp_from=&timestamp_from={}'.format(btc_market, timestamp_from)

    r = requests.get(url)
    text = r.iter_lines()
    next(text)
    answ = []
    for i in text:
        row = i.decode('utf-8')
        row = row.split(',')
        if len(row) == 3:
            try:
                value, timestmp = float(row[1]), datetime.datetime.strptime(row[2],
                                                                            "%Y-%m-%dT%H:%M:%S.%f+00:00")
            except ValueError:
                value, timestmp = float(row[1]), datetime.datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S+00:00")
            if value and timestmp:
                answ.append((float(value), timestmp.replace(tzinfo=datetime.timezone.utc).timestamp()))
    return answ


def get_price_from_bitrex(btc_market, timestamp_from):
    url = 'https://python:3xq2jFVpPDFkmQmGadvr8qE3@blockchainflow.io:899/api/1.0/csv/market_data/?market={}' \
          '&exchange=Bittrex&timestamp_from={}'.format(btc_market, timestamp_from)

    r = requests.get(url)
    text = r.iter_lines()
    next(text)
    answ = []
    for i in text:
        row = i.decode('utf-8')
        row = row.split(',')
        if len(row) == 2 and row[0] and row[1]:
            answ.append((float(row[0][2:]), datetime.datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S.%f+00:00")
                         .replace(tzinfo=datetime.timezone.utc).timestamp()))
    return answ


def get_all_btc_list():
    url = 'https://api:VdhuDa4XCfDXXKfWDMGq5cp@blockchainflow.io:14127/api/1.0/csv/markets_list/?exchange=Bittrex'

    r = requests.get(url)
    text = r.iter_lines()
    next(text)
    answ = []
    for i in text:
        btc_market = i.decode('utf-8')
        answ.append(btc_market)
    return answ


def window_func1(window_size):
    dt = datetime.datetime.now()
    t_end = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    t_start = t_end - window_size
    answ = []
    for market in get_all_btc_list():
        price = [i for i in get_price_from_bitrex(market, t_start) if i[1] <= t_end]
        volume = [i for i in get_volume_from_bitrex(market, t_start) if i[1] <= t_end]

        if price and volume:
            min_price = min(price, key=lambda t: t[0])[0]
            max_price = max(price, key=lambda t: t[0])[0]

            min_volume = min(volume, key=lambda t: t[0])[0]
            max_volume = max(volume, key=lambda t: t[0])[0]

            price_percent = (max_price * 100) / min_price
            volume_percent = (max_volume * 100) / min_volume
            answ.append({"price_percent": price_percent, "volume_percent": volume_percent, "market": market})
    return answ


def window_func2(window_size):
    dt = datetime.datetime.now()
    t_end = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    t_start = t_end - window_size
    answ = []
    for market in get_all_btc_list():
        price = [i for i in get_price_from_bitrex(market, t_start) if i[1] <= t_end]
        volume = [i for i in get_volume_from_bitrex(market, t_start) if i[1] <= t_end]

        if price and volume:
            first_price = max(price, key=lambda t: t[1])[0]
            second_price = min(price, key=lambda t: t[1])[0]

            first_volume = max(volume, key=lambda t: t[1])[0]
            second_volume = min(volume, key=lambda t: t[1])[0]

            if first_price > 0 and first_volume > 0:
                price_percent = (second_price * 100) / first_price
                volume_percent = (second_volume * 100) / first_volume
                answ.append({"price_percent": price_percent, "volume_percent": volume_percent, "market": market})
    return answ