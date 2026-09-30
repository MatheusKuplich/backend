let paginaAtual = 1;
const ITENS_POR_PAGINA = 8;
let categoriasCache = [];
let produtosCache = [];
let filtroCategoria = null;

async function carregarDestaques() {
  const container = document.getElementById('produtos-destaque');
  if (!container) return;

  try {
    const res = await fetch('/api/produtos/destaques');
    if (!res.ok) throw new Error('Erro ao buscar destaques');
    const produtos = await res.json();

    if (!produtos || produtos.length === 0) {
      container.innerHTML = '<div class="col-12">Nenhum destaque encontrado.</div>';
      return;
    }

    container.innerHTML = produtos.map(p => `
      <div class="col-6 col-md-4 col-lg-3 mb-4">
        <div class="card produto-card h-100">
          <a href="#">
            <img src="${p.imagem || '/static/img/products/placeholder.svg'}" class="card-img-top" alt="${(p.nome||'Produto')}" loading="lazy">
          </a>
          <div class="card-body d-flex flex-column">
            <h6 class="card-title text-truncate">${p.nome}</h6>
            <p class="price mb-2">${p.preco ? ('R$ ' + Number(p.preco).toFixed(2)) : '—'}</p>
            <div class="mt-auto d-flex gap-2">
              <button class="btn btn-outline-primary btn-sm flex-grow-1 btn-ver-produto" data-id="${p.id}" data-bs-toggle="modal" data-bs-target="#modalProduto">Ver</button>
              <button class="btn btn-primary btn-sm btn-comprar" data-id="${p.id}">Comprar</button>
            </div>
          </div>
        </div>
      </div>
    `).join('');

    // Attach listeners to Ver buttons
    document.querySelectorAll('.btn-ver-produto').forEach(btn => {
      btn.addEventListener('click', abrirQuickView);
    });
    document.querySelectorAll('.btn-comprar').forEach(btn => {
      btn.addEventListener('click', comprarProduto);
    });

  } catch (err) {
    container.innerHTML = `<div class="col-12 text-danger">Não foi possível carregar os destaques.</div>`;
    console.error(err);
  }
}

async function carregarCategorias() {
  try {
    const res = await fetch('/api/categorias');
    if (!res.ok) throw new Error('Erro ao buscar categorias');
    categoriasCache = await res.json();
    renderizarFiltrosCategorias();
  } catch (err) {
    console.error('Erro ao carregar categorias:', err);
  }
}

function renderizarFiltrosCategorias() {
  const container = document.getElementById('filtro-categorias');
  if (!container) return;

  container.innerHTML = '<button class="btn btn-outline-secondary btn-sm btn-filtro-cat active" data-cat-id="all">Todas</button>' + 
    categoriasCache.map(c => `
      <button class="btn btn-outline-secondary btn-sm btn-filtro-cat" data-cat-id="${c.id}">${c.nome}</button>
    `).join('');

  document.querySelectorAll('.btn-filtro-cat').forEach(btn => {
    btn.addEventListener('click', () => {
      filtroCategoria = btn.dataset.catId === 'all' ? null : parseInt(btn.dataset.catId);
      paginaAtual = 1;
      document.querySelectorAll('.btn-filtro-cat').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      carregarProdutos();
    });
  });
}

async function carregarProdutos(pagina = 1) {
  paginaAtual = pagina;
  const container = document.getElementById('produtos-lista');
  if (!container) return;

  container.innerHTML = '<div class="col-12 text-center">Carregando...</div>';

  try {
    const res = await fetch('/api/produtos');
    if (!res.ok) throw new Error('Erro ao buscar produtos');
    let produtos = await res.json();

    // Filtrar por categoria se selecionada
    if (filtroCategoria) {
      produtos = produtos.filter(p => p.categoria_id === filtroCategoria);
    }

    produtosCache = produtos;

    const inicio = (pagina - 1) * ITENS_POR_PAGINA;
    const fim = inicio + ITENS_POR_PAGINA;
    const produtosPagina = produtos.slice(inicio, fim);

    if (produtosPagina.length === 0) {
      container.innerHTML = '<div class="col-12 text-center">Nenhum produto encontrado.</div>';
    } else {
      container.innerHTML = produtosPagina.map(p => `
        <div class="col-6 col-md-4 col-lg-3 mb-4">
          <div class="card produto-card h-100">
            <a href="#">
              <img src="${p.imagem || '/static/img/products/placeholder.svg'}" class="card-img-top" alt="${p.nome}" loading="lazy">
            </a>
            <div class="card-body d-flex flex-column">
              <h6 class="card-title text-truncate">${p.nome}</h6>
              <p class="price mb-2">${p.preco ? ('R$ ' + Number(p.preco).toFixed(2)) : '—'}</p>
              <div class="mt-auto d-flex gap-2">
                <button class="btn btn-outline-primary btn-sm flex-grow-1 btn-ver-produto" data-id="${p.id}" data-bs-toggle="modal" data-bs-target="#modalProduto">Ver</button>
                <button class="btn btn-primary btn-sm btn-comprar" data-id="${p.id}">Comprar</button>
              </div>
            </div>
          </div>
        </div>
      `).join('');
    }

    // Renderizar paginação
    const totalPaginas = Math.ceil(produtos.length / ITENS_POR_PAGINA);
    renderizarPaginacao(totalPaginas, pagina);

    // Attach listeners
    document.querySelectorAll('.btn-ver-produto').forEach(btn => {
      btn.addEventListener('click', abrirQuickView);
    });
    document.querySelectorAll('.btn-comprar').forEach(btn => {
      btn.addEventListener('click', comprarProduto);
    });

  } catch (err) {
    container.innerHTML = `<div class="col-12 text-danger">Erro ao carregar produtos: ${err.message}</div>`;
    console.error(err);
  }
}

function renderizarPaginacao(totalPaginas, paginaAtualParam) {
  const container = document.getElementById('paginacao');
  if (!container || totalPaginas <= 1) {
    if (container) container.innerHTML = '';
    return;
  }

  let html = '';
  if (paginaAtualParam > 1) {
    html += `<li class="page-item"><a class="page-link" href="#" onclick="carregarProdutos(${paginaAtualParam - 1}); return false;">Anterior</a></li>`;
  }

  for (let i = 1; i <= totalPaginas; i++) {
    const ativo = i === paginaAtualParam ? 'active' : '';
    html += `<li class="page-item ${ativo}"><a class="page-link" href="#" onclick="carregarProdutos(${i}); return false;">${i}</a></li>`;
  }

  if (paginaAtualParam < totalPaginas) {
    html += `<li class="page-item"><a class="page-link" href="#" onclick="carregarProdutos(${paginaAtualParam + 1}); return false;">Próximo</a></li>`;
  }

  container.innerHTML = html;
}

function abrirQuickView(e) {
  e.preventDefault();
  const produtoId = parseInt(this.dataset.id);
  const produto = produtosCache.find(p => p.id === produtoId);

  // Se não encontrar em cache, buscar todos
  if (!produto) {
    fetch('/api/produtos')
      .then(r => r.json())
      .then(prods => {
        const p = prods.find(x => x.id === produtoId);
        if (p) preencherModal(p, prods);
      });
  } else {
    preencherModal(produto, produtosCache);
  }
}

function preencherModal(produto, todosOsProdutos) {
  const catNome = categoriasCache.find(c => c.id === produto.categoria_id)?.nome || 'Categoria desconhecida';
  
  document.getElementById('modal-nome').textContent = produto.nome;
  document.getElementById('modal-imagem').src = produto.imagem || '/static/img/products/placeholder.svg';
  document.getElementById('modal-preco').textContent = produto.preco ? `R$ ${Number(produto.preco).toFixed(2)}` : 'Preço sob consulta';
  document.getElementById('modal-categoria').textContent = `Categoria: ${catNome}`;
  document.getElementById('modal-descricao').textContent = `Código: ${produto.codigo}`;
  document.getElementById('modal-quantidade').value = 1;

  // Update button label
  const btn = document.getElementById('modal-comprar-btn');
  btn.textContent = 'Comprar (1 un.)';
  btn.onclick = () => comprarModalProduto(produto.id, 1);

  // Update quantity
  document.getElementById('modal-quantidade').onchange = () => {
    const qty = parseInt(document.getElementById('modal-quantidade').value) || 1;
    btn.textContent = `Comprar (${qty} un.)`;
    btn.onclick = () => comprarModalProduto(produto.id, qty);
  };
}

async function comprarModalProduto(produtoId, quantidade) {
  try {
    const res = await fetch(`/api/produtos/${produtoId}`);
    if (!res.ok) throw new Error('Produto não encontrado');
    const produto = await res.json();
    
    // Adicionar ao carrinho usando o gerenciador
    if (carrinhoManager) {
      for (let i = 0; i < quantidade; i++) {
        carrinhoManager.adicionarAoCarrinho(produto);
      }
    }
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('modalProduto'));
    if (modal) modal.hide();
  } catch (err) {
    alert('Erro ao adicionar ao carrinho: ' + err.message);
  }
}

async function comprarProduto(e) {
  e.preventDefault();
  const produtoId = parseInt(this.dataset.id);
  
  try {
    const res = await fetch(`/api/produtos/${produtoId}`);
    if (!res.ok) throw new Error('Produto não encontrado');
    const produto = await res.json();
    
    // Adicionar ao carrinho usando o gerenciador
    if (carrinhoManager) {
      carrinhoManager.adicionarAoCarrinho(produto);
    }
  } catch (err) {
    alert('Erro ao adicionar ao carrinho: ' + err.message);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  carregarDestaques();
  carregarCategorias();
  carregarProdutos(1);
});
