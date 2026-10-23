async function loadData() {
    try {
        const response = await fetch('active_approvals.json');
        const data = await response.json();
        const container = document.getElementById('results');
        
        if (data.length === 0) {
            container.innerHTML = "<p style='text-align:center;'>No dangerous transferFrom approvals found in the latest scan.</p>";
            return;
        }

        container.innerHTML = "";
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'card';
            div.innerHTML = `
                <div class="row"><strong>Owner:</strong> <a href="https://tronscan.org/#/address/${item.Owner}" target="_blank">${item.Owner}</a></div>
                <div class="row"><strong>Spender:</strong> <a href="https://tronscan.org/#/contract/${item.Spender}/write" target="_blank">${item.Spender}</a></div>
                <div class="row"><strong>Allowance:</strong> ${item.Allowance} (${item.Token})</div>
                <div class="danger">⚠️ ${item.Risk}</div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        document.getElementById('results').innerHTML = "<p style='text-align:center;'>Error loading data. Run the GitHub Action first.</p>";
    }
}

loadData();
