import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random
import string
import re
import hashlib
import time

# Configuração da página
st.set_page_config(
    page_title="EcoPiracicaba 2026",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto"
)

# Detectar tema do sistema
def get_theme():
    try:
        if 'theme' in st.session_state:
            return st.session_state.theme
        
        theme = st.get_option("theme.base")
        if theme == "dark":
            st.session_state.theme = "dark"
            return "dark"
        else:
            st.session_state.theme = "light"
            return "light"
    except:
        st.session_state.theme = "light"
        return "light"

# Alternar tema manualmente
def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"
    st.rerun()

# Detectar dispositivo
def detectar_dispositivo():
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
        mobile_keywords = ['android', 'iphone', 'ipad', 'ipod', 'mobile', 'phone', 'tablet']
        for keyword in mobile_keywords:
            if keyword in user_agent:
                return "mobile"
        return "desktop"
    except:
        return "desktop"

# Validar e-mail
def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== SISTEMA DE DESAFIOS SEMANAIS (VERSÃO SIMPLIFICADA) ==========

DESAFIOS = [
    {
        "id": 1,
        "titulo": "♻️ Reciclar 10kg",
        "descricao": "Recicle 10kg de materiais recicláveis esta semana",
        "objetivo": 10,
        "unidade": "kg",
        "pontos": 200,
        "icone": "♻️"
    },
    {
        "id": 2,
        "titulo": "📅 Participar de 2 Eventos",
        "descricao": "Participe de 2 eventos ambientais esta semana",
        "objetivo": 2,
        "unidade": "eventos",
        "pontos": 300,
        "icone": "📅"
    },
    {
        "id": 3,
        "titulo": "🌳 Plantar uma Árvore",
        "descricao": "Plante 1 árvore nativa esta semana",
        "objetivo": 1,
        "unidade": "árvore",
        "pontos": 500,
        "icone": "🌳"
    },
    {
        "id": 4,
        "titulo": "🔋 Descartar Pilhas",
        "descricao": "Descarte 5 pilhas ou baterias em pontos de coleta",
        "objetivo": 5,
        "unidade": "pilhas",
        "pontos": 150,
        "icone": "🔋"
    },
    {
        "id": 5,
        "titulo": "💧 Economizar Água",
        "descricao": "Reduza seu consumo de água em 20% esta semana",
        "objetivo": 20,
        "unidade": "%",
        "pontos": 250,
        "icone": "💧"
    },
    {
        "id": 6,
        "titulo": "🚲 Usar Bike 3x",
        "descricao": "Use bicicleta em vez de carro 3 vezes esta semana",
        "objetivo": 3,
        "unidade": "vezes",
        "pontos": 180,
        "icone": "🚲"
    },
    {
        "id": 7,
        "titulo": "🥕 Comprar Orgânicos",
        "descricao": "Compre produtos orgânicos 3 vezes esta semana",
        "objetivo": 3,
        "unidade": "vezes",
        "pontos": 120,
        "icone": "🥕"
    },
    {
        "id": 8,
        "titulo": "📚 Ler 5 Dicas",
        "descricao": "Leia 5 dicas ambientais no app",
        "objetivo": 5,
        "unidade": "dicas",
        "pontos": 80,
        "icone": "📚"
    }
]

PREMIOS = [
    {
        "nome": "🥉 Bronze Ambiental",
        "descricao": "Complete 3 desafios",
        "icone": "🥉",
        "pontos_bonus": 100,
        "min_desafios": 3
    },
    {
        "nome": "🥈 Prata Ambiental",
        "descricao": "Complete 5 desafios",
        "icone": "🥈",
        "pontos_bonus": 250,
        "min_desafios": 5
    },
    {
        "nome": "🥇 Ouro Ambiental",
        "descricao": "Complete 7 desafios",
        "icone": "🥇",
        "pontos_bonus": 500,
        "min_desafios": 7
    }
]

# ========== INICIALIZAÇÃO DO BANCO DE DADOS (SIMPLIFICADO) ==========

def init_database():
    conn = sqlite3.connect('ecopiracicaba.db')
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
    
    # Tabela de progresso - APENAS O NECESSÁRIO
    c.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            usuario_id INTEGER PRIMARY KEY,
            pontos INTEGER DEFAULT 0,
            nivel TEXT DEFAULT '🌱 EcoIniciante',
            desafios_completados INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            ultima_atividade TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Inserir usuário admin
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", datetime.now().strftime("%d/%m/%Y"))
        )
    
    conn.commit()
    conn.close()

# Inicializar banco
init_database()

# ========== FUNÇÕES DE PROGRESSO ==========

def get_nivel(pontos):
    if pontos < 100:
        return "🌱 EcoIniciante"
    elif pontos < 500:
        return "🌿 EcoAmigo"
    elif pontos < 1000:
        return "🍃 EcoGuardião"
    else:
        return "🌳 EcoMestre"

def inicializar_progresso(usuario_id):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO progresso (usuario_id, pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (usuario_id, 0, "🌱 EcoIniciante", datetime.now().strftime("%d/%m/%Y"))
        )
    
    conn.commit()
    conn.close()

def adicionar_pontos(usuario_id, pontos_extra):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        novos_pontos = pontos_atuais + pontos_extra
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, datetime.now().strftime("%d/%m/%Y"), usuario_id)
        )
    
    conn.commit()
    conn.close()

def completar_desafio(usuario_id, desafio):
    """Função para completar um desafio"""
    adicionar_pontos(usuario_id, desafio['pontos'])
    
    # Atualizar contador de desafios
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("UPDATE progresso SET desafios_completados = desafios_completados + 1 WHERE usuario_id = ?", (usuario_id,))
    
    # Buscar total de desafios
    c.execute("SELECT desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    total = c.fetchone()[0]
    conn.commit()
    conn.close()
    
    return total

def gerar_codigo_convite(usuario_id):
    return hashlib.md5(f"{usuario_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color):
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios</h2>", unsafe_allow_html=True)
    
    # Buscar progresso do usuário
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT pontos, desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    conn.close()
    
    if resultado:
        pontos = resultado[0]
        desafios_completados = resultado[1]
    else:
        pontos = 0
        desafios_completados = 0
    
    # Mostrar progresso
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Seu Progresso</h3>
        <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
            <div>
                <span style='font-size: 36px; color: {icon_color};'>{desafios_completados}</span>
                <p style='color: {text_color};'>Desafios Completados</p>
            </div>
            <div>
                <span style='font-size: 36px; color: gold;'>🏆</span>
                <p style='color: {text_color};'>{pontos} Pontos</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar prêmios
    st.markdown(f"<h3 style='color: {text_color};'>🎁 Prêmios</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, premio in enumerate(PREMIOS):
        with cols[i]:
            cor = "#cd7f32" if i == 0 else "#c0c0c0" if i == 1 else "#ffd700"
            disponivel = desafios_completados >= premio["min_desafios"]
            
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid {cor if disponivel else border_color}; opacity: {1 if disponivel else 0.5};'>
                <span style='font-size: 36px;'>{premio['icone']}</span>
                <h4 style='color: {text_color};'>{premio['nome']}</h4>
                <p style='color: {text_color};'>{premio['descricao']}</p>
                <p style='color: {icon_color};'>+{premio['pontos_bonus']} pts</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar lista de desafios
    st.markdown(f"<h3 style='color: {text_color};'>📋 Desafios Disponíveis</h3>", unsafe_allow_html=True)
    
    for desafio in DESAFIOS:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color};'>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <span style='font-size: 40px;'>{desafio['icone']}</span>
                    <div>
                        <h4 style='color: {text_color}; margin: 0;'>{desafio['titulo']}</h4>
                        <p style='color: {text_color}; margin: 5px 0;'>{desafio['descricao']}</p>
                        <p style='color: {icon_color}; margin: 0;'>Recompensa: +{desafio['pontos']} pontos</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"✅ Completar", key=f"desafio_{desafio['id']}"):
                total = completar_desafio(usuario_id, desafio)
                st.success(f"Parabéns! Você completou o desafio e ganhou {desafio['pontos']} pontos!")
                
                # Verificar se ganhou prêmio
                for premio in PREMIOS:
                    if total == premio["min_desafios"]:
                        adicionar_pontos(usuario_id, premio["pontos_bonus"])
                        st.balloons()
                        st.success(f"🎉 VOCÊ GANHOU O PRÊMIO {premio['nome']}! +{premio['pontos_bonus']} pontos extras!")
                
                st.rerun()

def mostrar_perfil(usuario_id, nome, text_color, card_bg, icon_color, border_color):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT pontos, nivel, desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    conn.close()
    
    if resultado:
        pontos, nivel, desafios = resultado
    else:
        pontos, nivel, desafios = 0, "🌱 EcoIniciante", 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {border_color};'>
            <h2 style='color: {text_color};'>{nivel}</h2>
            <h1 style='color: {icon_color}; font-size: 48px;'>{pontos}</h1>
            <p style='color: {text_color};'>pontos totais</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {border_color};'>
            <h3 style='color: {text_color};'>🎯 Desafios</h3>
            <h1 style='color: {icon_color}; font-size: 48px;'>{desafios}</h1>
            <p style='color: {text_color};'>completados</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_ranking(text_color, card_bg, icon_color, border_color):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT u.nome, p.pontos, p.nivel, p.desafios_completados
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        ORDER BY p.pontos DESC
        LIMIT 10
    """)
    ranking = c.fetchall()
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>🏆 Ranking</h3>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
    for i, usuario in enumerate(ranking):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}º"
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: {text_color};'><strong>{medalha} {usuario[0]}</strong> - {usuario[2]}</span>
                <span style='color: {icon_color};'><strong>{usuario[1]} pts</strong> | 🎯 {usuario[3]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_convite(usuario_id, text_color, card_bg, icon_color, border_color):
    codigo = gerar_codigo_convite(usuario_id)
    
    st.markdown(f"<h3 style='color: {text_color};'>👥 Convidar Amigos</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(f"ECOPIRA-{codigo}", language="text")
    with col2:
        if st.button("📋 Copiar"):
            st.success("Código copiado!")

def mostrar_dicas(text_color, card_bg, icon_color, border_color):
    st.markdown(f"<h3 style='color: {text_color};'>💡 Dicas</h3>", unsafe_allow_html=True)
    
    dicas = [
        ("🌱 Compostagem", "50% do lixo pode ser compostado"),
        ("💧 Água", "Banho de 15 min gasta 135L"),
        ("🔋 Pilhas", "1 pilha contamina 20 mil litros"),
        ("🌳 Árvores", "1 árvore absorve 150kg CO2/ano")
    ]
    
    for dica in dicas:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-right: 6px solid {icon_color}; border: 1px solid {border_color};'>
            <strong style='color: {text_color};'>{dica[0]}:</strong> <span style='color: {text_color};'>{dica[1]}</span>
        </div>
        """, unsafe_allow_html=True)

def mostrar_eventos(text_color, card_bg, icon_color, border_color):
    st.markdown(f"<h3 style='color: {text_color};'>📅 Eventos</h3>", unsafe_allow_html=True)
    
    eventos = [
        ("🌱 Feira Sustentável", "15/03 - Engenho Central"),
        ("♻️ Workshop", "22/03 - SENAI"),
        ("🌊 Mutirão Rio", "05/04 - Rua do Porto")
    ]
    
    for evento in eventos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ff9f4b; border: 1px solid {border_color};'>
            <strong style='color: {text_color};'>{evento[0]}</strong><br>
            <span style='color: {text_color};'>{evento[1]}</span>
        </div>
        """, unsafe_allow_html=True)

def mostrar_pontos_coleta(text_color, card_bg, icon_color, border_color):
    st.markdown(f"<h3 style='color: {text_color};'>📍 Pontos</h3>", unsafe_allow_html=True)
    
    pontos = [
        ("Ecoponto Centro", "Av. Rui Barbosa, 800"),
        ("Shopping Piracicaba", "Av. Limeira, 700"),
        ("Coopervidros", "R. Treze de Maio, 300")
    ]
    
    for ponto in pontos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
            <strong style='color: {text_color};'>{ponto[0]}</strong><br>
            <span style='color: {text_color};'>{ponto[1]}</span>
        </div>
        """, unsafe_allow_html=True)

# ========== CONFIGURAÇÕES DE TEMA ==========

tema = get_theme()
dispositivo = detectar_dispositivo()

if tema == "dark":
    bg_color = "#0a1f17"
    card_bg = "#1a3329"
    text_color = "#FFFFFF"
    secondary_text = "#E0E0E0"
    border_color = "#2a4a3a"
    icon_color = "#8bc34a"
    gradient_start = "#0a1f17"
    gradient_end = "#1a4a3a"
else:
    bg_color = "#f0fff5"
    card_bg = "#FFFFFF"
    text_color = "#000000"
    secondary_text = "#2a5e45"
    border_color = "#c0e0d0"
    icon_color = "#0f5c3f"
    gradient_start = "#e8f5e9"
    gradient_end = "#c8e6c9"

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    .stMarkdown, p, h1, h2, h3, h4 {{
        color: {text_color} !important;
    }}
    .stButton button {{
        background: {icon_color};
        color: white;
        border: none;
        border-radius: 50px;
    }}
    .stTextInput input {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
    }}
    div.stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
    }}
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {icon_color} !important;
        color: white !important;
    }}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"<h1 style='text-align: center;'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
with col3:
    if st.button("🌓 Tema"):
        toggle_theme()

# Conteúdo principal
if st.session_state.usuario_logado is None:
    # Tela de login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login"):
            st.markdown("### 🔐 Login")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if validar_email(email):
                    conn = sqlite3.connect('ecopiracicaba.db')
                    c = conn.cursor()
                    c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
                    user = c.fetchone()
                    conn.close()
                    if user:
                        st.session_state.usuario_logado = {'id': user[0], 'nome': user[1]}
                        inicializar_progresso(user[0])
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos")
        
        st.markdown("---")
        with st.form("cadastro"):
            st.markdown("### 🆕 Cadastro")
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Criar conta", use_container_width=True):
                if nome and validar_email(email) and len(senha) >= 6:
                    conn = sqlite3.connect('ecopiracicaba.db')
                    c = conn.cursor()
                    try:
                        c.execute(
                            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
                            (nome, email, senha, datetime.now().strftime("%d/%m/%Y"))
                        )
                        conn.commit()
                        st.success("Conta criada! Faça login.")
                    except:
                        st.error("E-mail já existe")
                    conn.close()
                else:
                    st.error("Preencha todos os campos")

else:
    # Usuário logado
    with st.sidebar:
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT pontos, nivel FROM progresso WHERE usuario_id = ?", (st.session_state.usuario_logado['id'],))
        prog = c.fetchone()
        conn.close()
        
        pontos = prog[0] if prog else 0
        nivel = prog[1] if prog else "🌱 EcoIniciante"
        
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background: {card_bg}; border-radius: 10px; border: 1px solid {border_color};'>
            <h3 style='color: {text_color};'>{st.session_state.usuario_logado['nome']}</h3>
            <h4 style='color: {icon_color};'>{nivel}</h4>
            <h2 style='color: {icon_color};'>{pontos} pts</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Início", "🎯 Desafios", "👤 Perfil", "🏆 Ranking", "📍 Pontos"])
    
    with tab1:
        st.markdown(f"## Olá, {st.session_state.usuario_logado['nome']}!")
        col1, col2 = st.columns(2)
        with col1:
            mostrar_dicas(text_color, card_bg, icon_color, border_color)
        with col2:
            mostrar_eventos(text_color, card_bg, icon_color, border_color)
    
    with tab2:
        mostrar_pagina_desafios(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
    
    with tab3:
        mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                      text_color, card_bg, icon_color, border_color)
    
    with tab4:
        mostrar_ranking(text_color, card_bg, icon_color, border_color)
    
    with tab5:
        mostrar_pontos_coleta(text_color, card_bg, icon_color, border_color)
