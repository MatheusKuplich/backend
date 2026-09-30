/**
 * Lógica de Carrinho para a loja
 * Gerencia localStorage + API do servidor
 */

// Gerar ID de sessão do cliente (simulado)
function obterClienteId() {
  let clienteId = localStorage.getItem('cliente_id');
  if (!clienteId) {
    clienteId = 'visitante-' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('cliente_id', clienteId);
  }
  return clienteId;
}

class CarrinhoManager {
  constructor() {
    this.clienteId = null;
    this.carrinho = null;
    this.modal = null;
    this.badges = null;
    this.init();
  }

  async init() {
    // Se cliente não tem ID no DB, criar um
    const clienteId = obterClienteId();
    // TODO: Para versão com auth real, pegar ID do servidor
    this.clienteId = clienteId;
    
    this.modal = document.getElementById('modal-carrinho');
    this.badges = {
      quantidade: document.getElementById('badge-carrinho'),
      modal: document.getElementById('carrinho-itens'),
      total: document.getElementById('total-valor'),
      vazio: document.getElementById('carrinho-vazio'),
      tabela: document.getElementById('carrinho-tabela'),
      totalDiv: document.getElementById('carrinho-total'),
    };

    this.attachListeners();
    await this.carregarCarrinho();
  }

  attachListeners() {
    document.getElementById('btn-abrir-carrinho')?.addEventListener('click', () => this.mostrarModal());
    document.getElementById('btn-limpar-carrinho')?.addEventListener('click', () => this.limparCarrinho());
    document.getElementById('btn-checkout')?.addEventListener('click', () => this.finalizarCompra());
  }

  async carregarCarrinho() {
    try {
      // Carrinho salvo em localStorage
      const carrinhoLocal = localStorage.getItem('carrinho_' + this.clienteId);
      this.carrinho = carrinhoLocal ? JSON.parse(carrinhoLocal) : { itens: [], total: 0 };
      this.atualizarBadge();
    } catch (err) {
      console.warn('Erro ao carregar carrinho:', err);
      this.carrinho = { itens: [], total: 0 };
    }
  }

  adicionarAoCarrinho(produto) {
    // produto deve ter: id, nome, preco, imagem
    const itemExistente = this.carrinho.itens.find(i => i.produto_id === produto.id);

    if (itemExistente) {
      itemExistente.quantidade += 1;
    } else {
      this.carrinho.itens.push({
        id: 'item-' + Math.random().toString(36),
        produto_id: produto.id,
        produto_nome: produto.nome,
        preco_unitario: produto.preco || 0,
        quantidade: 1,
      });
    }

    this.recalcularTotal();
    this.salvarCarrinho();
    this.atualizarBadge();
    this.mostrarNotificacao(`${produto.nome} adicionado ao carrinho!`);
  }

  removerDoCarrinho(itemId) {
    this.carrinho.itens = this.carrinho.itens.filter(i => i.id !== itemId);
    this.recalcularTotal();
    this.salvarCarrinho();
    this.atualizarBadge();
    this.renderizarCarrinho();
  }

  atualizarQuantidade(itemId, novaQtd) {
    const item = this.carrinho.itens.find(i => i.id === itemId);
    if (item) {
      item.quantidade = Math.max(1, novaQtd);
      this.recalcularTotal();
      this.salvarCarrinho();
      this.atualizarBadge();
      this.renderizarCarrinho();
    }
  }

  recalcularTotal() {
    this.carrinho.total = this.carrinho.itens.reduce(
      (sum, item) => sum + (item.preco_unitario * item.quantidade),
      0
    );
  }

  salvarCarrinho() {
    localStorage.setItem('carrinho_' + this.clienteId, JSON.stringify(this.carrinho));
  }

  atualizarBadge() {
    const total = this.carrinho.itens.reduce((sum, i) => sum + i.quantidade, 0);
    if (this.badges.quantidade) {
      this.badges.quantidade.textContent = total;
    }
  }

  async mostrarModal() {
    this.renderizarCarrinho();
    if (this.modal) {
      const bsModal = new bootstrap.Modal(this.modal);
      bsModal.show();
    }
  }

  renderizarCarrinho() {
    if (!this.modal) return;

    const { vazio, tabela, totalDiv, modal } = this.badges;
    const tbody = document.getElementById('carrinho-itens');
    
    if (this.carrinho.itens.length === 0) {
      if (vazio) vazio.style.display = 'block';
      if (tabela) tabela.style.display = 'none';
      if (totalDiv) totalDiv.style.display = 'none';
      document.getElementById('btn-checkout').disabled = true;
      return;
    }

    if (vazio) vazio.style.display = 'none';
    if (tabela) tabela.style.display = 'table';
    if (totalDiv) totalDiv.style.display = 'block';
    document.getElementById('btn-checkout').disabled = false;

    tbody.innerHTML = this.carrinho.itens.map(item => `
      <tr>
        <td>${item.produto_nome}</td>
        <td>R$ ${Number(item.preco_unitario).toFixed(2)}</td>
        <td>
          <input type="number" min="1" value="${item.quantidade}" 
            onchange="carrinhoManager.atualizarQuantidade('${item.id}', this.value)"
            class="form-control form-control-sm" style="width: 60px;">
        </td>
        <td>R$ ${(item.preco_unitario * item.quantidade).toFixed(2)}</td>
        <td>
          <button class="btn btn-danger btn-sm"
            onclick="carrinhoManager.removerDoCarrinho('${item.id}')">Remover</button>
        </td>
      </tr>
    `).join('');

    if (this.badges.total) {
      this.badges.total.textContent = this.carrinho.total.toFixed(2);
    }
  }

  async limparCarrinho() {
    if (confirm('Tem certeza que deseja limpar todo o carrinho?')) {
      this.carrinho.itens = [];
      this.carrinho.total = 0;
      this.salvarCarrinho();
      this.atualizarBadge();
      this.renderizarCarrinho();
      this.mostrarNotificacao('Carrinho limpo!');
    }
  }

  async finalizarCompra() {
    if (this.carrinho.itens.length === 0) {
      alert('Carrinho vazio!');
      return;
    }

    try {
      const payload = {
        cliente_id: null,
        itens: this.carrinho.itens.map((item) => ({
          produto_id: item.produto_id,
          quantidade: item.quantidade,
          preco_unitario: item.preco_unitario,
        })),
      };

      const resposta = await fetch('/api/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const dados = await resposta.json().catch(() => ({}));
      if (!resposta.ok) {
        throw new Error(dados.erro || 'Não foi possível finalizar a compra.');
      }

      this.carrinho.itens = [];
      this.carrinho.total = 0;
      this.salvarCarrinho();
      this.atualizarBadge();
      this.renderizarCarrinho();
      this.mostrarNotificacao(`Compra confirmada! Pedido #${dados.id}`);
    } catch (erro) {
      console.error('Erro ao finalizar compra:', erro);
      alert(erro.message || 'Não foi possível finalizar a compra.');
    }
  }

  mostrarNotificacao(mensagem) {
    // Criar um toast/notificação simples
    const toast = document.createElement('div');
    toast.className = 'alert alert-success position-fixed bottom-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.textContent = mensagem;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }
}

// Instanciar globalmente
let carrinhoManager;

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  carrinhoManager = new CarrinhoManager();
});
