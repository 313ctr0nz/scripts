import argparse
import datetime
import json
import requests
import time 

import cg

currency = "usd"

signatures = {
    "Transfer"  : "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "Approve"   : "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
    "Sync"      : "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1",
    "Swap"      : "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
}

addrs = {}

def fetchtkn(contractAddr, apikey):
    url = f"https://api.snowtrace.io/api?module=account&action=tokentx&contractaddress={contractAddr}&page=1&offset=1&sort=desc&apikey={apikey}"
    # print(url)
    try:
        res = requests.get(url, timeout=1)
        r=res.json().get("result")[0]
        # print(r)
        return { "name" : r.get('tokenName'), "symbol" : r.get('tokenSymbol'), "decimal" : r.get('tokenDecimal')}
    except:
        print("Timeout")
        return {}

def fetchdate(blockno, apikey):
    url = f"https://api.snowtrace.io/api?module=block&action=getblockreward&blockno={blockno}&apikey={apikey}"
    # print(url)
    res = requests.get(url)
    # print(json.dumps(res.json()))   
    return datetime.datetime.fromtimestamp(int(res.json().get("result").get("timeStamp"))).strftime("%d-%m-%Y")

def parsedata(log):
    data = []
    if len(log.get("data")) == 66:
        data.append(log.get("data"))
    if len(log.get("data")) == 130:
        data.append(log.get("data")[0:66])
        data.append(log.get("data")[66:])
        # print(data)
    if len(log.get("data")) == 258:
        data.append(log.get("data")[0:66])
        data.append(log.get("data")[66:])
        # print(data)

    returndata = []
    for d in data:
        returndata.append({"amount" : int(d,16)/(10**int(addrs[log.get("address")].get("decimal")))})

    return returndata

def fetchtxn(r, apikey):
    # print(r)
    url = "https://api.snowtrace.io/api?module=proxy&action=eth_getTransactionReceipt&txhash="+r.get("hash")+"&apikey=" + apikey
    # print(url)
    res = requests.get(url)
    # print(json.dumps(res.json()))   
    print("-"*50)
    if res.json().get("result").get("logs"):
        print("txn: " + res.json().get("result").get("transactionHash"))

        txndate = fetchdate(int(res.json().get("result").get("blockNumber"),16),apikey)
        print(txndate)

        # print(res.json().get("result"))
        for log in res.json().get("result").get("logs"):
            # print(log) 
            if signatures.get("Transfer") not in log.get("topics"):
                continue
            if not addrs.get(log.get("address")):
                time.sleep(0.1)
                token = fetchtkn(log.get("address"),apikey)
                # print(token)
                if "symbol" not in token:
                    print("token lookup error")
                    continue
                else:
                    addrs[log.get("address")] = token

            value = cg.cg_getPrice(addrs[log.get("address")].get("symbol").lower(), txndate, currency)
            print(value)

            print(addrs[log.get("address")])
            # print(log.get("address"))
            txndata = parsedata(log) 
            print(txndata)             

def fetch(address, apikey):
    url = "https://api.snowtrace.io/api?module=account&action=txlist&address="+address+"&startblock=1&endblock=99999999&sort=asc&apikey=" + apikey
    # print(url)

    res = requests.get(url)
    # print(res.json())
    for r in res.json().get("result"):
        fetchtxn(r, apikey)
        time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr',   type=str, required=True)
    parser.add_argument('--apikey', type=str, required=True)
    parser.add_argument('--txn',    type=str, required=False)
    args = parser.parse_args()

    cg.init()

    if args.txn:
        fetchtxn({ "hash" : args.txn }, args.apikey)
    else:
        fetch(args.addr, args.apikey)
