import requests
import json
import csv
import time
import os

# --- CONFIGURATION ---
TRONGRID_API = "https://api.trongrid.io"
TRONSCAN_API = "https://apilist.tronscanapi.com"

# Read keys securely from GitHub Secrets
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY", "")
TRONSCAN_API_KEY = os.environ.get("TRONSCAN_API_KEY", "")

headers = {
    "TRON-PRO-API-KEY": TRONGRID_API_KEY,
    "Accept": "application/json"
}

def get_addresses():
    addresses = set()
    try:
        with open("discovered_addresses.txt", "r") as f:
            addresses.update([line.strip() for line in f if line.strip()])
    except FileNotFoundError:
        pass
        
    try:
        with open("manual_addresses.txt", "r") as f:
            addresses.update([line.strip() for line in f if line.strip()])
    except FileNotFoundError:
        pass
        
    return list(addresses)

def check_abi_for_transfer_from(spender):
    """
    Fetches the contract ABI and STRICTLY checks for 'transferFrom' with a destination address.
    """
    url = f"{TRONGRID_API}/wallet/getcontract"
    payload = {"value": spender, "visible": True}
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()
        
        if "abi" not in data or not data["abi"]:
            return "UNVERIFIED CONTRACT"

        abi = data["abi"].get("entrys", [])
        
        for item in abi:
            name = item.get("name", "")
            # ONLY CHECK FOR transferFrom
            if name == "transferFrom":
                inputs = item.get("inputs", [])
                if len(inputs) >= 3:
                    addr_count = sum(1 for i in inputs if i.get("type") == "address")
                    if addr_count >= 2:
                        return "DANGEROUS: transferFrom(address,address,uint256)"
                        
        return "SAFE" 
    except Exception:
        return "UNKNOWN"

def main():
    addresses = get_addresses()
    print(f"Scanning {len(addresses)} addresses for active allowances...\n")
    
    results = []
    
    for i, owner in enumerate(addresses):
        print(f"[{i+1}/{len(addresses)}] {owner}")
        url = f"{TRONSCAN_API}/api/account/approve/list?address={owner}&limit=100&start=0&type=token"
        try:
            # Use TronScan headers just for this request
            ts_headers = {"TRON-PRO-API-KEY": TRONSCAN_API_KEY, "Accept": "application/json"}
            res = requests.get(url, headers=ts_headers, timeout=10)
            approvals = res.json().get("data", [])
            for app in approvals:
                val = app.get("allowance") or app.get("value") or "0"
                if str(val).lower() == "unlimited" or (str(val).isdigit() and int(val) > 0):
                    spender = app.get("spender") or app.get("approved_address")
                    if not spender: continue
                    
                    print(f"  -> Checking Spender: {spender}")
                    risk = check_abi_for_transfer_from(spender)
                    
                    if risk != "SAFE" and risk != "UNKNOWN":
                        results.append({
                            "Owner": owner,
                            "Spender": spender,
                            "Token": app.get("tokenSymbol", "Unknown"),
                            "Allowance": val,
                            "Risk": risk
                        })
                    time.sleep(0.2)
        except Exception:
            pass

    # Save to JSON
    with open("active_approvals.json", "w") as f:
        json.dump(results, f, indent=4)
        
    # Save to CSV
    with open("active_approvals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Owner", "Spender", "Token", "Allowance", "Risk"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n✅ Done. Found {len(results)} spenders with transferFrom.")

if __name__ == "__main__":
    main()
