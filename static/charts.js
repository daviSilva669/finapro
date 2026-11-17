function showTab(tabId, btn) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
    if (btn) btn.classList.add('active');
}

let filtroStatusAtual = 'todos';

function setFiltroStatus(status, btn) {
    filtroStatusAtual = status;
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    filtrarClientes();
}

function filtrarClientes() {
    const input = document.getElementById('buscaCliente');
    const termo = input ? input.value.toLowerCase().trim() : '';
    const cards = document.querySelectorAll('.cliente-card');
    let visiveis = 0;

    cards.forEach(card => {
        const texto = card.getAttribute('data-busca') || '';
        const temPendente = card.getAttribute('data-pendente') === '1';

        const bateTexto = texto.includes(termo);
        const bateStatus = (filtroStatusAtual === 'todos') || (filtroStatusAtual === 'pendentes' && temPendente);

        if (bateTexto && bateStatus) {
            card.style.display = 'block';
            visiveis++;
        } else {
            card.style.display = 'none';
        }
    });

    const msgVazio = document.getElementById('semResultadosBusca');
    if (msgVazio) {
        msgVazio.style.display = (cards.length > 0 && visiveis === 0) ? 'block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const dados = window.DADOS_FINANCEIROS;

    if (dados.abaAtiva) {
        const btnAtivo = document.querySelector(`.tab-btn[data-tab="${dados.abaAtiva}"]`);
        if (btnAtivo) showTab(dados.abaAtiva, btnAtivo);
    }

    const ctxCat = document.getElementById('graficoCategorias');
    if (ctxCat) {
        new Chart(ctxCat, {
            type: 'doughnut',
            data: {
                labels: dados.catLabels.length ? dados.catLabels : ['Sem gastos'],
                datasets: [{
                    data: dados.catValores.length ? dados.catValores : [1],
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '68%',
                plugins: { legend: { position: 'bottom', labels: { color: '#f8fafc', padding: 14 } } }
            }
        });
    }

    const ctxRes = document.getElementById('graficoResumo');
    if (ctxRes) {
        new Chart(ctxRes, {
            type: 'bar',
            data: {
                labels: ['Ganhos', 'Gastos', 'Lucro'],
                datasets: [{
                    data: [dados.ganhosMes, dados.gastosMes, dados.lucroMes],
                    backgroundColor: ['#10b981', '#ef4444', '#3b82f6'],
                    borderRadius: 8
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } }
                }
            }
        });
    }
});
