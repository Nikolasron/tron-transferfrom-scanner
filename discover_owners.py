import requests

TRONSCAN_API = "https://apilist.tronscanapi.com"
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def discover():
    print("Discovering active wallets...")
    url = f"{TRONSCAN_API}/api/token_trc20/transfers?limit=50&start=0&contract_address={USDT_CONTRACT}"
    try:
        res = requests.get(url, timeout=15)
        transfers = res.json().get("token_transfers", [])
        addresses = set()
        for tx in transfers:
            if tx.get("from_address"): addresses.add(tx["from_address"])
            if tx.get("to_address"): addresses.add(tx["to_address"])
            
        with open("discovered_addresses.txt", "w") as f:
            for addr in addresses:
                f.write(f"{addr}\n")
        print(f"Saved {len(addresses)} addresses to discovered_addresses.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    discover()
