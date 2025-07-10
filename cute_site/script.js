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

const API_BASE = location.protocol === 'file:' ? 'http://localhost:8000' : '';

async function fetchPriority() {
    try {
        const res = await fetch(`${API_BASE}/api/priority`);
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
        const res = await fetch(`${API_BASE}/api/products`);
        const data = await res.json();
        const tbody = document.querySelector('#products-table tbody');
        tbody.innerHTML = '';
        data.forEach(p => {
            const tr = document.createElement('tr');
            const name = p.name || '';
            const url = p.url || '#';
            const price = p.price !== undefined ? `$${p.price}` : '';
            const inStock = p.in_stock === '1' ? 'Yes' : 'No';
            tr.innerHTML = `<td><a href="${url}" target="_blank">${name}</a></td><td>${price}</td><td>${inStock}</td>`;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

async function fetchLogs() {
    try {
        const res = await fetch(`${API_BASE}/api/logs`);
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
