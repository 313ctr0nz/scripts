import argparse
import requests
import time
from datetime import datetime
import json


# CoinGecko Price API
'''
for tokens such as time and ohm with multiple ticker symbols in common, 
tokencache will be used to store the users captured preference

this might turn out to be an edge case for those with 2 on chain ticker symbols colliding
'''

limit_per_minute = 500 #CG Rate Limit
time_delay = 60 / limit_per_minute
#time.sleep(time_delay)

tokencache = {}
tokenlist = []

def init():
    url = 'https://api.coingecko.com/api/v3/coins/list'
    print(url)
    global tokenlist
    tokenlist = requests.get(url).json()

def cg_testToken(token):
    print(tokencache)
    if tokencache.get(token.lower()):
        return 200

    url = 'https://api.coingecko.com/api/v3/coins/' + token
    print(url)
    data = requests.get(url)
    return data.status_code

def cg_enumTokenOptions(tokens):
    # print(tokens)
    print("\n")
    for i in range(0,len(tokens)):
        print(f"i: {i}, tok: {tokens[i]}")
    choice = int(input("Please choose row number: "))
    print("\n")
    print(tokens[choice])
    print("\n")
    return tokens[choice].get("id")

def cg_searchToken(token):
    if tokencache.get(token.lower()):
        return tokencache.get(token.lower())

    t = {}
    t['result'] = []
    for i in tokenlist:
        # print(i)
        if (token.lower() in i['symbol'].lower()):
            t['result'].append(i)
    if len(t['result']) == 1:
        print("line 60 " + t['result'][0]['id'])
        tokencache[token.lower()] = t['result'][0]['id']
        return (tokencache[token.lower()])
    elif len(t['result']) > 1:
        print('More than 1 token result in CG Coin List, please choose')
        # print(t)
        tokencache[token.lower()] = cg_enumTokenOptions(t.get("result"))
        return (tokencache[token.lower()])
    else:
        print('ERROR - token not found')
        token = 'ERROR' 
        return token

def cg_getPrice(token,date,currency):
    print(token)
    if cg_testToken(token) == 200:
        placeholder = token
        token = tokencache.get(token.lower()) or placeholder
        url = 'https://api.coingecko.com/api/v3/coins/' + token + '/history?date=' + date + '&localization=en'
        print(url)
        data = (requests.get(url)).json()
        print(data)
        if data.get('market_data'):
            return data['market_data']['current_price'][currency]
        else:
            return None
    else:
        print(f'Token Call Failed: {token}')
        token = cg_searchToken(token)
        if not token == 'ERROR':
            url = 'https://api.coingecko.com/api/v3/coins/' + token + '/history?date=' + date + '&localization=en'
            print(url)
            data = (requests.get(url)).json()
            if data.get('market_data'):
                return data['market_data']['current_price'][currency]
            else:
                return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--date',   type=str, required=True)
    parser.add_argument('--token',  type=str, required=True)
    args = parser.parse_args()
    print(args)

    init()
    price = cg_getPrice(args.token,args.date,'usd')
    print(price)

    # Example cg_getPrice('strong','15-10-2021')
