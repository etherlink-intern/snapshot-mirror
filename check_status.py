#!/usr/bin/env python3
"""Remote Status Reporter for Etherlink snapshots."""

import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "https://snapshotter-sandbox.nomadic-labs.eu/"
NETWORKS = ["etherlink-mainnet", "etherlink-testnet", "etherlink-shadownet"]
TYPES = ["rolling", "full", "archive"]
TIMEOUT = 10

def get_status_icon(code):
    if code == 200:
        return "✅ OK"
    if code == 404:
        return "❌ 404"
    return f"⚠️ {code}"

def check_category(network, snapshot_type):
    url = f"{BASE_URL}{network}/{snapshot_type}/"
    result = {
        "category": f"{network}/{snapshot_type}",
        "listing": "Unavailable",
        "versioned_file": "None",
        "versioned_status": "N/A",
        "latest_status": "N/A"
    }

    try:
        # 1. Check listing page
        resp = requests.get(url, timeout=TIMEOUT)
        result["listing"] = get_status_icon(resp.status_code)
        if resp.status_code != 200:
            return result

        # 2. Scrape for latest versioned file
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
        
        # Filter for versioned files (e.g. etherlink-mainnet-rolling-35084466.gz)
        versioned = [f for f in links if f.startswith(f"{network}-{snapshot_type}-") and "latest" not in f and f.endswith(".gz")]
        
        if versioned:
            # Sort manually by block height if possible
            try:
                versioned.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]), reverse=True)
            except:
                versioned.sort(reverse=True)
            
            latest_v = versioned[0]
            result["versioned_file"] = latest_v
            
            # 3. Check versioned file online status
            try:
                v_resp = requests.head(f"{url}{latest_v}", timeout=TIMEOUT, allow_redirects=True)
                result["versioned_status"] = get_status_icon(v_resp.status_code)
            except:
                result["versioned_status"] = "❌ Error"

        # 4. Check latest.gz alias status
        try:
            alias = f"{network}-{snapshot_type}-latest.gz"
            l_resp = requests.head(f"{url}{alias}", timeout=TIMEOUT, allow_redirects=True)
            result["latest_status"] = get_status_icon(l_resp.status_code)
        except:
            result["latest_status"] = "❌ Error"

    except Exception as e:
        result["listing"] = f"❌ {type(e).__name__}"

    return result

def main():
    print(f"{'CATEGORY':<30} | {'LIST':<8} | {'VERSIONED (LATEST)':<35} | {'V-STAT':<8} | {'L-STAT':<8}")
    print("-" * 100)
    
    for net in NETWORKS:
        for t in TYPES:
            res = check_category(net, t)
            print(f"{res['category']:<30} | {res['listing']:<8} | {res['versioned_file']:<35} | {res['versioned_status']:<8} | {res['latest_status']:<8}")

if __name__ == "__main__":
    main()
