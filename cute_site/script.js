function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.toggle('active', el.id === tab);
    });
    document.querySelectorAll('.tabs button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
}

document.querySelectorAll('.tabs button').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

async function fetchPriority() {
    try {
        const res = await fetch('/api/priority');
        const data = await res.json();
        const list = document.getElementById('priority-list');
        list.innerHTML = '';
        data.forEach(link => {
            const li = document.createElement('li');
            li.textContent = link;
            list.appendChild(li);
        });
    } catch (e) {
        console.error(e);
    }
}

async function fetchProducts() {
    try {
        const res = await fetch('/api/products');
        const data = await res.json();
        const tbody = document.querySelector('#products-table tbody');
        tbody.innerHTML = '';
        data.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${p.name || ''}</td><td>$${p.price || ''}</td><td>${p.in_stock === '1' ? 'Yes' : 'No'}</td>`;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

async function fetchLogs() {
    try {
        const res = await fetch('/api/logs');
        const data = await res.json();
        document.getElementById('log-text').textContent = data.logs || '';
    } catch (e) {
        console.error(e);
    }
}

function refreshData() {
    fetchPriority();
    fetchProducts();
    fetchLogs();
}

document.addEventListener('DOMContentLoaded', () => {
    refreshData();
    setInterval(refreshData, 30000);
});
