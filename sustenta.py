import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sustentabilidade Piracicaba",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para melhorar a aparência no Streamlit
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f5c3f 0%, #1a8c5f 100%);
    }
    .block-container {
        padding: 0 !important;
        max-width: 400px !important;
        margin: 0 auto !important;
    }
    .main {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
    footer {display: none}
    header {display: none}
</style>
""", unsafe_allow_html=True)

# Título na barra lateral (opcional)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4148/4148460.png", width=100)
    st.title("🌱 Sustentabilidade")
    st.markdown("---")
    st.markdown("### Sobre o App")
    st.info("""
    Este aplicativo ajuda você a encontrar locais de descarte correto em Piracicaba.
    
    **Funcionalidades:**
    - ♻️ Cores da coleta seletiva
    - 📅 Eventos 2026
    - 🗺️ Ecopontos por categoria
    - 📝 Cadastro de usuários
    - 🔍 Busca de locais
    """)
    st.markdown("---")
    st.caption("Desenvolvido para Piracicaba Sustentável")

# Inicializar banco de dados SQLite
def init_database():
    conn = sqlite3.connect('sustentabilidade.db')
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_cadastro TEXT
        )
    ''')
    
    # Tabela de cadastros
    c.execute('''
        CREATE TABLE IF NOT EXISTS cadastros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nome TEXT NOT NULL,
            telefone TEXT,
            bairro TEXT,
            interesse TEXT,
            data_cadastro TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Inserir usuário de teste se não existir
    c.execute("SELECT * FROM usuarios WHERE email = 'teste@email.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            ("Usuário Teste", "teste@email.com", "123456", datetime.now().strftime("%d/%m/%Y"))
        )
    
    conn.commit()
    conn.close()

# Chamar inicialização
init_database()

# HTML do app (versão completa com todas as funcionalidades)
html_code = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Sustentabilidade Piracicaba</title>
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        body {
            background: #f8fff9;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 10px;
        }

        .phone-mock {
            max-width: 400px;
            width: 100%;
            height: 780px;
            background: #f8fff9;
            border-radius: 46px;
            box-shadow: 0 25px 40px rgba(0,60,20,0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #8bbba0;
            position: relative;
        }

        /* TELA DE LOGIN */
        .login-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(145deg, #0f5c3f 0%, #1a8c5f 100%);
            z-index: 200;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 30px;
            transition: transform 0.4s ease-out;
        }

        .login-screen.oculto {
            transform: translateY(100%);
        }

        .logo {
            font-size: 80px;
            color: #ffd966;
            margin-bottom: 15px;
            text-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .app-nome {
            color: white;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .app-sub {
            color: rgba(255,255,255,0.9);
            margin-bottom: 40px;
        }

        .login-card {
            width: 100%;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .campo {
            width: 100%;
            padding: 16px 20px;
            margin-bottom: 15px;
            border: none;
            border-radius: 50px;
            background: white;
            font-size: 16px;
            outline: none;
        }

        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 50px;
            background: #ffd966;
            color: #0f5c3f;
            font-weight: 700;
            font-size: 18px;
            cursor: pointer;
            margin-bottom: 12px;
            transition: 0.2s;
        }

        .btn:hover {
            background: #ffcd4d;
        }

        .btn-outline {
            background: transparent;
            border: 2px solid white;
            color: white;
        }

        .erro-msg {
            color: #ffb3b3;
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }

        /* APP PRINCIPAL */
        .app-main {
            display: flex;
            flex-direction: column;
            height: 100%;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }

        .app-main.visivel {
            opacity: 1;
            pointer-events: all;
        }

        .status-bar {
            background: #0f5c3f;
            padding: 12px 20px 8px;
            display: flex;
            justify-content: space-between;
            color: white;
        }

        .header {
            background: #0f5c3f;
            padding: 5px 20px 15px;
            color: white;
        }

        .header h1 {
            font-size: 26px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header h1 i {
            color: #ffd966;
        }

        .user-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
        }

        .user-nome {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 14px;
        }

        .sair-btn {
            background: none;
            border: 1px solid white;
            color: white;
            padding: 5px 15px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 13px;
        }

        .search-area {
            background: white;
            padding: 15px 20px 10px;
            border-bottom: 1px solid #b8daca;
        }

        .search-box {
            display: flex;
            background: #eef8f2;
            border-radius: 40px;
            padding: 5px 5px 5px 20px;
            border: 1.5px solid #7fba9c;
        }

        .search-box input {
            flex: 1;
            border: none;
            background: transparent;
            outline: none;
            font-size: 16px;
            padding: 10px 0;
        }

        .search-box button {
            background: #0f5c3f;
            color: white;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
        }

        .result-panel {
            background: #e2f3e9;
            margin: 10px 20px;
            padding: 15px;
            border-radius: 28px;
            border-left: 6px solid #ff9f4b;
            display: none;
            max-height: 220px;
            overflow-y: auto;
        }

        .result-panel.mostrar {
            display: block;
        }

        .result-panel h4 {
            color: #0f5c3f;
            margin-bottom: 8px;
        }

        .result-panel li {
            padding: 6px 0 6px 25px;
            border-bottom: 1px dashed #a6cdb8;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="%230f5c3f"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>') left center no-repeat;
            background-size: 16px;
            list-style: none;
        }

        .tab-bar {
            display: flex;
            padding: 0 15px;
            gap: 5px;
            border-bottom: 2px solid #c1dfd0;
            background: #f8fff9;
        }

        .tab {
            flex: 1;
            text-align: center;
            padding: 10px 0;
            font-weight: 600;
            color: #427a60;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 13px;
        }

        .tab i {
            margin-right: 4px;
        }

        .tab.ativo {
            color: #0f5c3f;
            border-bottom: 3px solid #0f5c3f;
        }

        .conteudo {
            flex: 1;
            overflow-y: auto;
            padding: 10px 15px;
        }

        /* CORES */
        .cor-card {
            display: flex;
            align-items: center;
            background: white;
            border-radius: 50px;
            padding: 12px 15px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
        }

        .cor-bolinha {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            margin-right: 15px;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        .cor-texto {
            flex: 1;
        }

        .cor-nome {
            font-weight: 700;
            font-size: 17px;
        }

        .cor-desc {
            color: #2a5e45;
            font-size: 13px;
        }

        /* EVENTOS */
        .evento-card {
            background: white;
            border-radius: 24px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #bfe1d0;
        }

        .evento-data {
            color: #e0672d;
            font-weight: 700;
            margin-bottom: 5px;
        }

        /* ECOPONTOS */
        .cat-ecoponto {
            background: white;
            border-radius: 26px;
            padding: 12px 15px;
            margin-bottom: 15px;
            border: 1px solid #c2e0cf;
        }

        .cat-titulo {
            font-size: 18px;
            color: #0f5c3f;
            border-bottom: 2px solid #c2e8d4;
            padding-bottom: 5px;
            margin-bottom: 8px;
        }

        .ponto-item {
            padding: 6px 0 6px 22px;
            border-bottom: 1px dashed #cbe6d7;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="%23308563"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>') left center no-repeat;
            background-size: 14px;
        }

        /* CADASTRO */
        .form-cad {
            background: white;
            border-radius: 30px;
            padding: 18px;
            margin: 10px 0;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #0f5c3f;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 1.5px solid #b8daca;
            border-radius: 40px;
            font-size: 15px;
            background: #f4fbf7;
        }

        .btn-salvar {
            background: #0f5c3f;
            color: white;
            border: none;
            padding: 14px;
            width: 100%;
            border-radius: 50px;
            font-weight: 700;
            cursor: pointer;
        }

        .lista-cad {
            margin-top: 15px;
        }

        .cad-item {
            background: #e5f3ec;
            border-radius: 20px;
            padding: 10px;
            margin-bottom: 8px;
            border-left: 4px solid #0f5c3f;
        }

        .bottom-nav {
            background: white;
            display: flex;
            justify-content: space-around;
            padding: 8px 15px 15px;
            border-top: 2px solid #c1dfd0;
        }

        .nav-item {
            color: #679b82;
            text-align: center;
            font-size: 11px;
            cursor: pointer;
        }

        .nav-item i {
            font-size: 20px;
            display: block;
            margin-bottom: 2px;
        }

        .nav-item.ativo {
            color: #0f5c3f;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="phone-mock">
        <!-- TELA DE LOGIN -->
        <div class="login-screen" id="telaLogin">
            <i class="fas fa-seedling logo"></i>
            <div class="app-nome">Piracicaba</div>
            <div class="app-sub">Sustentabilidade 2026</div>
            
            <div class="login-card">
                <input type="text" class="campo" id="loginNome" placeholder="Seu nome">
                <input type="email" class="campo" id="loginEmail" placeholder="E-mail">
                <input type="password" class="campo" id="loginSenha" placeholder="Senha">
                
                <button class="btn" id="btnEntrar">ENTRAR</button>
                <button class="btn btn-outline" id="btnCadastrar">CRIAR CONTA</button>
                
                <div class="erro-msg" id="erroLogin">E-mail ou senha incorretos</div>
            </div>
        </div>

        <!-- APP PRINCIPAL -->
        <div class="app-main" id="appPrincipal">
            <div class="status-bar">
                <span><i class="fas fa-signal"></i> 5G</span>
                <span><i class="fas fa-wifi"></i> Piracicaba</span>
                <span>14:30</span>
            </div>

            <div class="header">
                <h1><i class="fas fa-recycle"></i> Coleta Seletiva</h1>
                <div class="user-info">
                    <span class="user-nome" id="nomeUsuario"></span>
                    <button class="sair-btn" id="btnSair"><i class="fas fa-sign-out-alt"></i> Sair</button>
                </div>
            </div>

            <div class="search-area">
                <div class="search-box">
                    <input type="text" id="buscaInput" placeholder="pilhas, vidros, fios...">
                    <button id="btnBuscar"><i class="fas fa-search"></i></button>
                </div>
            </div>

            <div class="result-panel" id="painelResultado">
                <h4 id="resultadoTitulo"><i class="fas fa-map-pin"></i> Resultado</h4>
                <ul id="resultadoLista"></ul>
            </div>

            <div class="tab-bar">
                <div class="tab ativo" id="tabCores"><i class="fas fa-palette"></i> Cores</div>
                <div class="tab" id="tabEventos"><i class="fas fa-calendar"></i> 2026</div>
                <div class="tab" id="tabEcopontos"><i class="fas fa-trash"></i> Ecopontos</div>
                <div class="tab" id="tabCadastro"><i class="fas fa-user"></i> Cadastro</div>
            </div>

            <div class="conteudo" id="conteudoApp"></div>

            <div class="bottom-nav">
                <div class="nav-item ativo" id="navCores"><i class="fas fa-palette"></i><span>Cores</span></div>
                <div class="nav-item" id="navEventos"><i class="fas fa-calendar"></i><span>2026</span></div>
                <div class="nav-item" id="navEcopontos"><i class="fas fa-trash"></i><span>Ecopontos</span></div>
                <div class="nav-item" id="navCadastro"><i class="fas fa-user"></i><span>Cadastro</span></div>
            </div>
        </div>
    </div>

    <script>
        // ========== DADOS ==========
        const usuarios = [
            { id: 1, nome: "João Silva", email: "joao@email.com", senha: "123" },
            { id: 2, nome: "Maria Oliveira", email: "maria@email.com", senha: "123" }
        ];

        const cadastros = [];

        const locais = {
            pilhas: ["Shopping Piracicaba", "Unimed Sede", "Ecoponto Centro", "Esalq", "Drogaria São Paulo"],
            vidros: ["Ecoponto Vila Rezende", "Coopervidros", "Recicla Piracicaba", "Ecoponto Paulicéia"],
            eletronicos: ["CDI - R. do Porto, 234", "Assistência Consert+", "Ecoponto Monte Líbano"],
            fios: ["Cooperativa Recifios", "Ecoponto Centro", "Ferro Velho Central"],
            coleta: ["Ecoponto Monte Líbano", "Associação Recicladores", "LEV - Av. Limeira"],
            oleo: ["Ecoponto Paulicéia", "Cremeria Santa Helena", "UNIP", "Posto Ipiranga"]
        };

        const cores = [
            { cor: "Azul", desc: "Papel e papelão", ex: "jornais, caixas", icon: "fa-newspaper", bg: "#2196F3" },
            { cor: "Vermelho", desc: "Plástico", ex: "garrafas PET, sacolas", icon: "fa-bottle-water", bg: "#F44336" },
            { cor: "Verde", desc: "Vidro", ex: "garrafas, potes", icon: "fa-wine-bottle", bg: "#4CAF50" },
            { cor: "Amarelo", desc: "Metal", ex: "latas, alumínio", icon: "fa-cog", bg: "#FFEB3B" },
            { cor: "Marrom", desc: "Orgânicos", ex: "restos de comida", icon: "fa-apple-alt", bg: "#795548" },
            { cor: "Cinza", desc: "Não reciclável", ex: "papel higiênico", icon: "fa-trash", bg: "#9E9E9E" },
            { cor: "Laranja", desc: "Perigosos", ex: "pilhas, baterias", icon: "fa-bolt", bg: "#FF9800" },
            { cor: "Roxo", desc: "Radioativos", ex: "hospitalar", icon: "fa-radiation", bg: "#9C27B0" }
        ];

        const palestras = [
            { data: "15 mar 2026", titulo: "Economia Circular", local: "Engenho Central" },
            { data: "22 abr 2026", titulo: "Preservação das Águas", local: "Teatro Municipal" },
            { data: "05 jun 2026", titulo: "Dia do Meio Ambiente", local: "Parque da Rua do Porto" },
            { data: "18 ago 2026", titulo: "Mobilidade Sustentável", local: "SENAI" },
            { data: "10 out 2026", titulo: "Compostagem", local: "Horto Municipal" }
        ];

        let usuarioAtual = null;

        // ========== FUNÇÕES DE LOGIN/CADASTRO ==========
        function mostrarApp() {
            document.getElementById('telaLogin').classList.add('oculto');
            document.getElementById('appPrincipal').classList.add('visivel');
            document.getElementById('nomeUsuario').innerHTML = '<i class="fas fa-user"></i> ' + usuarioAtual.nome.split(' ')[0];
            mostrarCores();
        }

        document.getElementById('btnEntrar').addEventListener('click', () => {
            const email = document.getElementById('loginEmail').value;
            const senha = document.getElementById('loginSenha').value;
            
            const user = usuarios.find(u => u.email === email && u.senha === senha);
            
            if (user) {
                usuarioAtual = user;
                document.getElementById('erroLogin').style.display = 'none';
                mostrarApp();
            } else {
                document.getElementById('erroLogin').style.display = 'block';
            }
        });

        document.getElementById('btnCadastrar').addEventListener('click', () => {
            const nome = document.getElementById('loginNome').value;
            const email = document.getElementById('loginEmail').value;
            const senha = document.getElementById('loginSenha').value;
            
            if (!nome || !email || !senha) {
                alert('Preencha todos os campos');
                return;
            }
            
            if (usuarios.find(u => u.email === email)) {
                alert('E-mail já cadastrado');
                return;
            }
            
            const novoUser = { id: usuarios.length + 1, nome, email, senha };
            usuarios.push(novoUser);
            usuarioAtual = novoUser;
            document.getElementById('erroLogin').style.display = 'none';
            mostrarApp();
        });

        document.getElementById('btnSair').addEventListener('click', () => {
            usuarioAtual = null;
            document.getElementById('telaLogin').classList.remove('oculto');
            document.getElementById('appPrincipal').classList.remove('visivel');
            document.getElementById('loginNome').value = '';
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginSenha').value = '';
        });

        // ========== FUNÇÕES DAS ABAS ==========
        function mostrarCores() {
            let html = '<h3 style="margin:10px 0;color:#0f5c3f;"><i class="fas fa-trash-alt"></i> Cores da Coleta</h3>';
            cores.forEach(c => {
                html += `
                    <div class="cor-card">
                        <div class="cor-bolinha" style="background: ${c.bg};"></div>
                        <div class="cor-texto">
                            <div class="cor-nome">${c.cor}</div>
                            <div class="cor-desc"><strong>${c.desc}</strong> · ${c.ex}</div>
                        </div>
                        <i class="fas ${c.icon}" style="color: #0f5c3f;"></i>
                    </div>
                `;
            });
            document.getElementById('conteudoApp').innerHTML = html;
        }

        function mostrarEventos() {
            let html = '<h3 style="margin:10px 0;color:#0f5c3f;"><i class="fas fa-calendar-alt"></i> Palestras 2026</h3>';
            palestras.forEach(p => {
                html += `
                    <div class="evento-card">
                        <div class="evento-data"><i class="far fa-calendar"></i> ${p.data}</div>
                        <div style="font-weight:700;">${p.titulo}</div>
                        <div style="color:#467a61;"><i class="fas fa-map-marker-alt"></i> ${p.local}</div>
                    </div>
                `;
            });
            document.getElementById('conteudoApp').innerHTML = html;
        }

        function mostrarEcopontos() {
            const cats = [
                { chave: 'pilhas', nome: 'Pilhas', icon: 'fa-bolt' },
                { chave: 'vidros', nome: 'Vidros', icon: 'fa-wine-bottle' },
                { chave: 'eletronicos', nome: 'Eletrônicos', icon: 'fa-laptop' },
                { chave: 'fios', nome: 'Fios', icon: 'fa-plug' },
                { chave: 'coleta', nome: 'Coleta Seletiva', icon: 'fa-trash' },
                { chave: 'oleo', nome: 'Óleo', icon: 'fa-oil-can' }
            ];
            
            let html = '<h3 style="margin:10px 0;color:#0f5c3f;"><i class="fas fa-map-marker-alt"></i> Ecopontos</h3>';
            cats.forEach(cat => {
                if (locais[cat.chave]) {
                    html += '<div class="cat-ecoponto"><div class="cat-titulo"><i class="fas ' + cat.icon + '"></i> ' + cat.nome + '</div>';
                    locais[cat.chave].forEach(item => html += '<div class="ponto-item">' + item + '</div>');
                    html += '</div>';
                }
            });
            document.getElementById('conteudoApp').innerHTML = html;
        }

        function mostrarCadastro() {
            const userCadastros = cadastros.filter(c => c.usuario === usuarioAtual?.id);
            let lista = '';
            if (userCadastros.length > 0) {
                lista = '<div class="lista-cad"><h4>Seus cadastros:</h4>';
                userCadastros.forEach(c => {
                    lista += '<div class="cad-item"><strong>' + c.nome + '</strong> · ' + c.bairro + '<br><small>' + c.telefone + ' | ' + c.interesse + '</small></div>';
                });
                lista += '</div>';
            }

            const html = `
                <div class="form-cad">
                    <h3 style="margin-bottom:15px;"><i class="fas fa-user-plus"></i> Cadastre-se</h3>
                    <div class="form-group">
                        <label>Nome</label>
                        <input type="text" id="cadNome" value="${usuarioAtual.nome}">
                    </div>
                    <div class="form-group">
                        <label>Telefone</label>
                        <input type="text" id="cadTel" placeholder="(19) 99999-9999">
                    </div>
                    <div class="form-group">
                        <label>Bairro</label>
                        <input type="text" id="cadBairro" placeholder="Seu bairro">
                    </div>
                    <div class="form-group">
                        <label>Interesse</label>
                        <select id="cadInteresse">
                            <option>Coleta Seletiva</option>
                            <option>Compostagem</option>
                            <option>Eletrônicos</option>
                            <option>Óleo</option>
                            <option>Voluntariado</option>
                        </select>
                    </div>
                    <button class="btn-salvar" onclick="salvarCadastro()">Salvar</button>
                </div>
                ${lista}
            `;
            document.getElementById('conteudoApp').innerHTML = html;
        }

        window.salvarCadastro = function() {
            const nome = document.getElementById('cadNome').value;
            const tel = document.getElementById('cadTel').value;
            const bairro = document.getElementById('cadBairro').value;
            const interesse = document.getElementById('cadInteresse').value;
            
            if (!tel || !bairro) {
                alert('Preencha telefone e bairro');
                return;
            }
            
            cadastros.push({
                usuario: usuarioAtual.id,
                nome: usuarioAtual.nome,
                telefone: tel,
                bairro: bairro,
                interesse: interesse
            });
            
            alert('Cadastro salvo!');
            mostrarCadastro();
        };

        // ========== BUSCA ==========
        document.getElementById('btnBuscar').addEventListener('click', () => {
            const termo = document.getElementById('buscaInput').value.toLowerCase();
            let resultados = [];
            let titulo = '';
            
            if (termo.includes('pilha') || termo.includes('bateria')) { resultados = locais.pilhas; titulo = 'Pilhas'; }
            else if (termo.includes('vidro')) { resultados = locais.vidros; titulo = 'Vidros'; }
            else if (termo.includes('eletr')) { resultados = locais.eletronicos; titulo = 'Eletrônicos'; }
            else if (termo.includes('fio')) { resultados = locais.fios; titulo = 'Fios'; }
            else if (termo.includes('coleta') || termo.includes('lixo')) { resultados = locais.coleta; titulo = 'Coleta Seletiva'; }
            else if (termo.includes('oleo') || termo.includes('óleo')) { resultados = locais.oleo; titulo = 'Óleo'; }
            else { resultados = ['Nenhum resultado encontrado']; titulo = 'Busca'; }
            
            document.getElementById('resultadoTitulo').innerHTML = '<i class="fas fa-map-pin"></i> ' + titulo;
            const lista = document.getElementById('resultadoLista');
            lista.innerHTML = '';
            resultados.forEach(r => {
                const li = document.createElement('li');
                li.textContent = r;
                lista.appendChild(li);
            });
            document.getElementById('painelResultado').classList.add('mostrar');
        });

        document.getElementById('buscaInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') document.getElementById('btnBuscar').click();
        });

        // ========== NAVEGAÇÃO ==========
        function ativarAba(abaId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('ativo'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('ativo'));
            document.getElementById('tab' + abaId).classList.add('ativo');
            document.getElementById('nav' + abaId).classList.add('ativo');
            document.getElementById('painelResultado').classList.remove('mostrar');
        }

        document.getElementById('tabCores').addEventListener('click', () => { ativarAba('Cores'); mostrarCores(); });
        document.getElementById('tabEventos').addEventListener('click', () => { ativarAba('Eventos'); mostrarEventos(); });
        document.getElementById('tabEcopontos').addEventListener('click', () => { ativarAba('Ecopontos'); mostrarEcopontos(); });
        document.getElementById('tabCadastro').addEventListener('click', () => { ativarAba('Cadastro'); mostrarCadastro(); });

        document.getElementById('navCores').addEventListener('click', () => document.getElementById('tabCores').click());
        document.getElementById('navEventos').addEventListener('click', () => document.getElementById('tabEventos').click());
        document.getElementById('navEcopontos').addEventListener('click', () => document.getElementById('tabEcopontos').click());
        document.getElementById('navCadastro').addEventListener('click', () => document.getElementById('tabCadastro').click());
    </script>
</body>
</html>
"""

# Exibir o HTML no Streamlit
components.html(html_code, height=820, scrolling=False)

# Rodapé com informações (opcional)
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🌱 **Sustentabilidade**")
with col2:
    st.markdown("📍 **Piracicaba**")
with col3:
    st.markdown("📅 **2026**")
