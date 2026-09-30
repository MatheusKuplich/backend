
const COLUNAS = {
  categorias: [
    { chave: "id", titulo: "ID" },
    { chave: "nome", titulo: "Nome" },
  ],
  produtos: [
    { chave: "id", titulo: "ID" },
    { chave: "codigo", titulo: "Código" },
    { chave: "nome", titulo: "Nome" },
    { chave: "categoria_id", titulo: "Categoria" },
  ],
  clientes: [
    { chave: "id", titulo: "ID" },
    { chave: "nome", titulo: "Nome" },
    { chave: "email", titulo: "E-mail" },
    { chave: "produtos", titulo: "Produtos comprados" },
  ],
};

const TITULOS = {
  categorias: { lista: "Categorias", form: "Nova categoria" },
  produtos: { lista: "Produtos", form: "Novo produto" },
  clientes: { lista: "Clientes", form: "Novo cliente" },
};

const CAMPOS = {
  categorias: [
    { nome: "nome", rotulo: "Nome", obrigatorio: true },
  ],
  produtos: [
    { nome: "nome", rotulo: "Nome", obrigatorio: true },
    { nome: "codigo", rotulo: "Código", obrigatorio: true },
    { nome: "categoria_id", rotulo: "Categoria", tipo: "select", origem: "categorias", obrigatorio: true },
  ],
  clientes: [
    { nome: "nome", rotulo: "Nome", obrigatorio: true },
    { nome: "email", rotulo: "E-mail", tipo: "email" },
    { nome: "produtos_ids", rotulo: "Produtos comprados", tipo: "multiselect", origem: "produtos", obrigatorio: false },
  ],
};
const elementoStatus = document.getElementById("status");
const elementoTituloLista = document.getElementById("titulo-lista");
const elementoTituloFormulario = document.getElementById("titulo-formulario");
const elementoCabecalho = document.getElementById("cabecalho");
const elementoCorpo = document.getElementById("corpo");
const elementoCampos = document.getElementById("campos");
const elementoContadorRegistros = document.getElementById("contador-registros");
const formulario = document.getElementById("formulario");
const mensagemFormulario = document.getElementById("mensagem-formulario");
const botaoRecarregar = document.getElementById("botao-recarregar");
const filtroBusca = document.getElementById("filtro-busca");
const abas = document.querySelectorAll(".aba");

let tipoAtual = "categorias";
let categoriasCache = [];
let produtosCache = [];
let termoBusca = "";
let chaveOrdenacao = "id";
let direcaoOrdenacao = "asc";

async function buscar(tipo) {
  const resposta = await fetch(`/api/${tipo}`);
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return resposta.json();
}

async function carregar(tipo) {
  tipoAtual = tipo;
  elementoTituloLista.textContent = TITULOS[tipo].lista;
  elementoTituloFormulario.textContent = TITULOS[tipo].form;
  limparMensagem();

  await renderizarFormulario(tipo);
  renderizarCabecalho(tipo);
  elementoCorpo.innerHTML = "";

  elementoStatus.classList.remove("erro");
  elementoStatus.textContent = "Carregando...";

  try {
    // Atualiza cache de categorias para usar na renderização (ex.: produtos)
    try {
      categoriasCache = await buscar('categorias');
    } catch (errCat) {
      categoriasCache = [];
    }

    try {
      produtosCache = await buscar('produtos');
    } catch (errProd) {
      produtosCache = [];
    }

    const dados = await buscar(tipo);
    const dadosVisiveis = aplicarBuscaEOrdenacao(tipo, dados);
    await renderizarLinhas(tipo, dadosVisiveis);
    elementoStatus.textContent = `${dados.length} registro(s) carregado(s).`;
    elementoContadorRegistros.textContent = `${dadosVisiveis.length} exibidos`;
  } catch (erro) {
    elementoStatus.textContent = `Falha ao carregar: ${erro.message}`;
    elementoStatus.classList.add("erro");
  }
}

function renderizarCabecalho(tipo) {
  elementoCabecalho.innerHTML = "";
  for (const coluna of COLUNAS[tipo]) {
    const th = document.createElement("th");
    th.className = "ordenavel";
    th.dataset.chave = coluna.chave;
    th.textContent = coluna.titulo;
    th.addEventListener("click", () => alternarOrdenacao(coluna.chave));
    elementoCabecalho.appendChild(th);
  }
  // coluna de ações
  const thAcoes = document.createElement("th");
  thAcoes.textContent = "Ações";
  elementoCabecalho.appendChild(thAcoes);
}

function alternarOrdenacao(chave) {
  if (chaveOrdenacao === chave) {
    direcaoOrdenacao = direcaoOrdenacao === "asc" ? "desc" : "asc";
  } else {
    chaveOrdenacao = chave;
    direcaoOrdenacao = "asc";
  }

  carregar(tipoAtual);
}

function buscarTexto(valor) {
  if (valor === null || valor === undefined) return "";
  return String(valor).toLowerCase();
}

function aplicarBuscaEOrdenacao(tipo, dados) {
  const dadosFiltrados = dados.filter((item) => {
    if (!termoBusca) return true;

    const produtosTexto = Array.isArray(item.produtos)
      ? item.produtos.map((produtoId) => {
          const produto = produtosCache.find(p => String(p.id) === String(produtoId));
          return produto ? `${produto.nome} ${produto.codigo}` : `ID ${produtoId}`;
        }).join(" ")
      : "";

    const textoBase = [
      item.id,
      item.nome,
      item.codigo,
      item.email,
      item.categoria_id,
      produtosTexto,
    ]
      .map(buscarTexto)
      .join(" ");

    return textoBase.includes(termoBusca);
  });

  const chave = chaveOrdenacao || "id";
  const direcao = direcaoOrdenacao === "desc" ? -1 : 1;

  return dadosFiltrados.sort((a, b) => {
    const valorA = obterValorParaOrdenacao(tipo, a, chave);
    const valorB = obterValorParaOrdenacao(tipo, b, chave);

    if (valorA === valorB) return 0;
    if (valorA === null || valorA === undefined) return 1;
    if (valorB === null || valorB === undefined) return -1;

    if (typeof valorA === "number" && typeof valorB === "number") {
      return (valorA - valorB) * direcao;
    }

    return String(valorA).localeCompare(String(valorB), undefined, { numeric: true }) * direcao;
  });
}

function obterValorParaOrdenacao(tipo, item, chave) {
  if (tipo === "produtos" && chave === "categoria_id") {
    const categoria = categoriasCache.find(c => String(c.id) === String(item.categoria_id));
    return categoria ? categoria.nome : item.categoria_id;
  }

  if (tipo === "clientes" && chave === "produtos") {
    if (Array.isArray(item.produtos) && item.produtos.length > 0) {
      return item.produtos.length;
    }
    return 0;
  }

  return item[chave];
}

async function renderizarLinhas(tipo, dados) {
  if (!dados.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = COLUNAS[tipo].length + 1;
    td.className = "vazio";
    td.textContent = "Nenhum registro encontrado.";
    tr.appendChild(td);
    elementoCorpo.appendChild(tr);
    return;
  }

  for (const item of dados) {
    const tr = document.createElement("tr");
    for (const coluna of COLUNAS[tipo]) {
      const td = document.createElement("td");
      let valor = item[coluna.chave];
      // mostrar nomes legíveis para referências
      if (tipo === "produtos" && coluna.chave === "categoria_id") {
        const cat = categoriasCache.find(c => String(c.id) === String(valor));
        td.textContent = cat ? cat.nome : (valor === null || valor === undefined ? "—" : valor);
      } else if (tipo === "clientes" && coluna.chave === "produtos") {
        if (Array.isArray(valor) && valor.length > 0) {
          const nomesProdutos = valor.map((produtoId) => {
            const produto = produtosCache.find(p => String(p.id) === String(produtoId));
            return produto ? `${produto.nome} (${produto.codigo})` : `ID ${produtoId}`;
          });
          td.textContent = nomesProdutos.join(", ");
        } else {
          td.textContent = "—";
        }
      } else {
        td.textContent = valor === null || valor === undefined ? "—" : valor;
      }
      tr.appendChild(td);
    }
    // ações: editar / remover
    const tdAcoes = document.createElement("td");

    const botaoEditar = document.createElement("button");
    botaoEditar.type = "button";
    botaoEditar.textContent = "Editar";
    botaoEditar.className = "botao-editar";
    botaoEditar.addEventListener("click", () => iniciarEdicao(tipo, item));

    const botaoRemover = document.createElement("button");
    botaoRemover.type = "button";
    botaoRemover.textContent = "Remover";
    botaoRemover.className = "botao-remover";
    botaoRemover.addEventListener("click", () => excluirItem(tipo, item.id));

    tdAcoes.appendChild(botaoEditar);
    tdAcoes.appendChild(document.createTextNode(" "));
    tdAcoes.appendChild(botaoRemover);
    tr.appendChild(tdAcoes);
    elementoCorpo.appendChild(tr);
  }
}

async function renderizarFormulario(tipo) {
  elementoCampos.innerHTML = "";
  // Separar campos comuns dos produtos
  let fieldsetProdutos = null;
  for (const campo of CAMPOS[tipo]) {
    // Se for o campo de produtos_ids, criar um fieldset separado com busca e seleção por checkbox
    if (campo.nome === "produtos_ids") {
      fieldsetProdutos = document.createElement("fieldset");
      fieldsetProdutos.className = "campo campo-produtos";
      const legend = document.createElement("legend");
      legend.textContent = campo.rotulo + (campo.obrigatorio ? " *" : "");
      fieldsetProdutos.appendChild(legend);

      const buscaProdutos = document.createElement("input");
      buscaProdutos.type = "search";
      buscaProdutos.className = "busca-produtos";
      buscaProdutos.placeholder = "Buscar produto por nome ou código";
      fieldsetProdutos.appendChild(buscaProdutos);

      const listaProdutos = document.createElement("div");
      listaProdutos.className = "lista-produtos";

      try {
        const itens = await buscar(campo.origem);
        for (const item of itens) {
          const label = document.createElement("label");
          label.className = "opcao-produto";

          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.name = campo.nome;
          checkbox.value = item.id;
          checkbox.dataset.texto = `${item.codigo} ${item.nome}`.toLowerCase();

          const span = document.createElement("span");
          span.textContent = rotuloItem(campo.origem, item);

          label.appendChild(checkbox);
          label.appendChild(span);
          listaProdutos.appendChild(label);
        }
      } catch (erro) {
        const aviso = document.createElement("p");
        aviso.className = "aviso-produtos";
        aviso.textContent = `Erro ao carregar: ${erro.message}`;
        listaProdutos.appendChild(aviso);
      }

      buscaProdutos.addEventListener("input", () => {
        const termo = buscaProdutos.value.trim().toLowerCase();
        const linhas = listaProdutos.querySelectorAll(".opcao-produto");
        linhas.forEach((linha) => {
          const textoLinha = linha.querySelector("input").dataset.texto || "";
          linha.style.display = textoLinha.includes(termo) ? "flex" : "none";
        });
      });

      fieldsetProdutos.appendChild(listaProdutos);
      elementoCampos.appendChild(fieldsetProdutos);
      continue;
    }
    // Campos normais
    const wrapper = document.createElement("div");
    wrapper.className = "campo";
    const label = document.createElement("label");
    label.htmlFor = `campo-${campo.nome}`;
    label.textContent = campo.rotulo + (campo.obrigatorio ? " *" : "");
    wrapper.appendChild(label);

    // Se for um select simples
    if (campo.tipo === "select") {
      const select = document.createElement("select");
      select.id = `campo-${campo.nome}`;
      select.name = campo.nome;
      if (campo.obrigatorio) select.required = true;

      // opção padrão vazia
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = `Selecione ${campo.rotulo}...`;
      placeholder.disabled = true;
      placeholder.selected = true;
      select.appendChild(placeholder);

      try {
        const itens = await buscar(campo.origem);
        for (const item of itens) {
          const option = document.createElement("option");
          option.value = item.id;
          option.textContent = rotuloItem(campo.origem, item);
          select.appendChild(option);
        }
      } catch (erro) {
        const option = document.createElement("option");
        option.disabled = true;
        option.textContent = `Erro ao carregar: ${erro.message}`;
        select.appendChild(option);
      }

      wrapper.appendChild(select);
      elementoCampos.appendChild(wrapper);
      continue;
    }

    const input = document.createElement("input");
    input.type = campo.tipo || "text";
    input.id = `campo-${campo.nome}`;
    input.name = campo.nome;
    if (campo.obrigatorio) input.required = true;
    wrapper.appendChild(input);
    elementoCampos.appendChild(wrapper);
  }
}


function rotuloItem(origem, item) {
  if (origem === "categorias") return `${item.nome} (id ${item.id})`;
  if (origem === "produtos") return `${item.codigo} - ${item.nome}`;
  return `${item.id}`;
}
function limparMensagem() {
  mensagemFormulario.textContent = "";
  mensagemFormulario.classList.remove("sucesso", "erro");
}

let modoEdicao = false;
let idEditando = null;

function iniciarEdicao(tipo, item) {
  modoEdicao = true;
  idEditando = item.id;
  elementoTituloFormulario.textContent = `Editando ${TITULOS[tipo].form.toLowerCase()}`;
  // preencher campos
  for (const campo of CAMPOS[tipo]) {
    const elemento = formulario.elements[campo.nome];
    if (!elemento) continue;
    if (campo.tipo === "multiselect") {
      const valores = item[campo.nome] || [];
      const listaCheckboxes = formulario.querySelectorAll(`input[name="${campo.nome}"]`);
      listaCheckboxes.forEach((checkbox) => {
        const selecionado = valores.includes(Number(checkbox.value)) || valores.includes(checkbox.value);
        checkbox.checked = selecionado;
      });
    } else {
      elemento.value = item[campo.nome] === null || item[campo.nome] === undefined ? "" : item[campo.nome];
    }
  }
}

async function excluirItem(tipo, id) {
  if (!confirm("Confirma exclusão deste item?")) return;
  try {
    const resposta = await fetch(`/api/${tipo}/${id}`, { method: "DELETE" });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    await carregar(tipo);
  } catch (erro) {
    elementoStatus.classList.add("erro");
    elementoStatus.textContent = `Falha ao excluir: ${erro.message}`;
  }
}

async function enviarFormulario(evento) {
  evento.preventDefault();
  limparMensagem();

  const dados = {};
  for (const campo of CAMPOS[tipoAtual]) {
    const elemento = formulario.elements[campo.nome];
    if (campo.tipo === "multiselect") {
      const valores = Array.from(formulario.querySelectorAll(`input[name="${campo.nome}"]:checked`)).map((checkbox) => checkbox.value);
      if (campo.obrigatorio && valores.length === 0) {
        mensagemFormulario.textContent = `Selecione ao menos um ${campo.rotulo}.`;
        mensagemFormulario.classList.add("erro");
        const primeiroCampo = formulario.querySelector(`input[name="${campo.nome}"]`);
        if (primeiroCampo) primeiroCampo.focus();
        return;
      }
      dados[campo.nome] = valores;
    } else {
      const valor = elemento.value.trim();
      if (campo.obrigatorio && !valor) {
        mensagemFormulario.textContent = `Preencha ${campo.rotulo}.`;
        mensagemFormulario.classList.add("erro");
        elemento.focus();
        return;
      }

      if (campo.tipo === "email" && valor !== "") {
        const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor);
        if (!emailValido) {
          mensagemFormulario.textContent = `Informe um e-mail válido em ${campo.rotulo}.`;
          mensagemFormulario.classList.add("erro");
          elemento.focus();
          return;
        }
      }

      if (valor !== "") dados[campo.nome] = valor;
    }
  }

  const botao = formulario.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    const url = modoEdicao ? `/api/${tipoAtual}/${idEditando}` : `/api/${tipoAtual}`;
    const method = modoEdicao ? "PUT" : "POST";
    const resposta = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });

    const corpo = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      throw new Error(corpo.erro || `HTTP ${resposta.status}`);
    }

    mensagemFormulario.textContent = "Cadastrado com sucesso.";
    mensagemFormulario.classList.add("sucesso");
    formulario.reset();
    modoEdicao = false;
    idEditando = null;
    await carregar(tipoAtual);
  } catch (erro) {
    mensagemFormulario.textContent = erro.message;
    mensagemFormulario.classList.add("erro");
  } finally {
    botao.disabled = false;
  }
}

abas.forEach((aba) => {
  aba.addEventListener("click", () => {
    abas.forEach((a) => a.classList.remove("ativa"));
    aba.classList.add("ativa");
    carregar(aba.dataset.tipo);
  });
});

botaoRecarregar.addEventListener("click", () => carregar(tipoAtual));
formulario.addEventListener("submit", enviarFormulario);
filtroBusca.addEventListener("input", (evento) => {
  termoBusca = evento.target.value.trim().toLowerCase();
  carregar(tipoAtual);
});

carregar("categorias");
