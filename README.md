# TRON Active Allowance Scanner

Discovers recent TRC-20 `Approval` events on TRON, then audits the **current on-chain allowance** for each owner and reports only approvals that are **still active right now**. 

Each spender is strictly filtered to only include contracts that contain the `transferFrom` function in their ABI.

## How it works
1. `discover_owners.py` fetches recent active wallets and saves them to `discovered_addresses.txt`.
2. `tron_scanner.py` checks approvals for all discovered and manual addresses, verifies the ABI of the spenders for `transferFrom`, and saves the dangerous ones to `active_approvals.json` and `active_approvals.csv`.
3. `index.html` and `app.js` provide a live dashboard to view the results.
