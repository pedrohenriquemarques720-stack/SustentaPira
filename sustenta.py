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

# ========== SISTEMA DE DESAFIOS SEMANAIS ==========

# Lista completa de desafios
DESAFIOS_LISTA = [
    {
        "id": 1,
        "titulo": "♻️ Reciclar 10kg",
        "descricao": "Recicle 10kg de materiais recicláveis esta semana",
        "objetivo": 10,
        "unidade": "kg",
        "pontos": 200,
        "icone": "♻️",
        "tipo": "reciclagem",
        "badge": "♻️ Mestre da Reciclagem"
    },
    {
        "id": 2,
        "titulo": "📅 Participar de 2 Eventos",
        "descricao": "Participe de 2 eventos ambientais esta semana",
        "objetivo": 2,
        "unidade": "eventos",
        "pontos": 300,
        "icone": "📅",
        "tipo": "eventos",
        "badge": "🎉 Participante Ativo"
    },
    {
        "id": 3,
        "titulo": "🌳 Plantar uma Árvore",
        "descricao": "Plante 1 árvore nativa esta semana",
        "objetivo": 1,
        "unidade": "árvore",
        "pontos": 500,
        "icone": "🌳",
        "tipo": "plantio",
        "badge": "🌲 Guardião da Floresta"
    }
]

# ========== INICIALIZAÇÃO DO BANCO DE DADOS ==========

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
    
    # Tabela de progresso do usuário (simplificada)
    c.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            usuario_id INTEGER PRIMARY KEY,
            total_pontos INTEGER DEFAULT 0,
            nivel TEXT DEFAULT '🌱 EcoIniciante',
            eventos_participados INTEGER DEFAULT 0,
            dicas_vistas INTEGER DEFAULT 0,
            pontos_visitados INTEGER DEFAULT 0,
            kg_reciclados REAL DEFAULT 0,
            arvores_plantadas INTEGER DEFAULT 0,
            amigos_convidados INTEGER DEFAULT 0,
            streak_dias INTEGER DEFAULT 0,
            ultima_atividade TEXT,
            desafios_completados INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de desafios (catálogo)
    c.execute('''
        CREATE TABLE IF NOT EXISTS desafios (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            descricao TEXT,
            objetivo INTEGER,
            unidade TEXT,
            pontos INTEGER,
            icone TEXT,
            tipo TEXT,
            badge TEXT
        )
    ''')
    
    # Inserir dados iniciais de desafios se não existirem
    c.execute("SELECT COUNT(*) FROM desafios")
    if c.fetchone()[0] == 0:
        for desafio in DESAFIOS_LISTA:
            c.execute(
                """INSERT INTO desafios 
                   (id, titulo, descricao, objetivo, unidade, pontos, icone, tipo, badge) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (desafio["id"], desafio["titulo"], desafio["descricao"], 
                 desafio["objetivo"], desafio["unidade"], desafio["pontos"], 
                 desafio["icone"], desafio["tipo"], desafio["badge"])
            )
    
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

# ========== FUNÇÕES DE GAMIFICAÇÃO ==========

def get_nivel(pontos):
    """Retorna o nível baseado nos pontos"""
    if pontos < 100:
        return "🌱 EcoIniciante"
    elif pontos < 500:
        return "🌿 EcoAmigo"
    elif pontos < 1000:
        return "🍃 EcoGuardião"
    elif pontos < 5000:
        return "🌳 EcoMestre"
    else:
        return "🏆 EcoHerói"

def get_proximo_nivel(pontos):
    """Retorna pontos necessários para próximo nível"""
    if pontos < 100:
        return 100 - pontos
    elif pontos < 500:
        return 500 - pontos
    elif pontos < 1000:
        return 1000 - pontos
    elif pontos < 5000:
        return 5000 - pontos
    else:
        return 0

def inicializar_progresso(usuario_id):
    """Inicializa o progresso de um novo usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    if not c.fetchone():
        c.execute(
            """INSERT INTO progresso 
               (usuario_id, total_pontos, nivel, ultima_atividade, desafios_completados) 
               VALUES (?, ?, ?, ?, ?)""",
            (usuario_id, 0, "🌱 EcoIniciante", datetime.now().strftime("%d/%m/%Y %H:%M"), 0)
        )
    
    conn.commit()
    conn.close()

def adicionar_pontos(usuario_id, pontos_extra):
    """Adiciona pontos ao usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        novos_pontos = pontos_atuais + pontos_extra
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, datetime.now().strftime("%d/%m/%Y %H:%M"), usuario_id)
        )
    
    conn.commit()
    conn.close()
    
    return pontos_extra

def completar_desafio(usuario_id, desafio_id):
    """Registra que um desafio foi completado"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar pontos do desafio
    c.execute("SELECT pontos, badge FROM desafios WHERE id = ?", (desafio_id,))
    desafio = c.fetchone()
    
    if desafio:
        # Adicionar pontos
        adicionar_pontos(usuario_id, desafio[0])
        
        # Incrementar contador de desafios
        c.execute("""
            UPDATE progresso SET 
                desafios_completados = desafios_completados + 1
            WHERE usuario_id = ?
        """, (usuario_id,))
    
    conn.commit()
    conn.close()

def registrar_atividade(usuario_id, tipo, valor=1):
    """Registra atividades do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    if tipo == "evento":
        c.execute("UPDATE progresso SET eventos_participados = eventos_participados + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "dica":
        c.execute("UPDATE progresso SET dicas_vistas = dicas_vistas + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "ponto":
        c.execute("UPDATE progresso SET pontos_visitados = pontos_visitados + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "reciclagem":
        c.execute("UPDATE progresso SET kg_reciclados = kg_reciclados + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "arvore":
        c.execute("UPDATE progresso SET arvores_plantadas = arvores_plantadas + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "amigo":
        c.execute("UPDATE progresso SET amigos_convidados = amigos_convidados + ? WHERE usuario_id = ?", (valor, usuario_id))
    
    conn.commit()
    conn.close()

def gerar_codigo_convite(usuario_id):
    """Gera código único para convidar amigos"""
    codigo = hashlib.md5(f"{usuario_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
    return codigo

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra página dedicada aos desafios - VERSÃO SIMPLIFICADA"""
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar progresso do usuário
    c.execute("SELECT total_pontos, desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    prog = c.fetchone()
    
    if prog:
        pontos = prog[0]
        desafios_completados = prog[1]
    else:
        pontos = 0
        desafios_completados = 0
    
    # Buscar todos os desafios disponíveis
    c.execute("SELECT id, titulo, descricao, objetivo, unidade, pontos, icone FROM desafios")
    todos_desafios = c.fetchall()
    
    conn.close()
    
    # Mostrar estatísticas
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
    
    # Mostrar lista de desafios
    st.markdown(f"<h3 style='color: {text_color};'>📋 Desafios Disponíveis</h3>", unsafe_allow_html=True)
    
    for desafio in todos_desafios:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color};'>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <span style='font-size: 40px;'>{desafio[6]}</span>
                    <div>
                        <h4 style='color: {text_color}; margin: 0;'>{desafio[1]}</h4>
                        <p style='color: {text_color}; margin: 5px 0;'>{desafio[2]}</p>
                        <p style='color: {icon_color}; margin: 0;'>Meta: {desafio[3]} {desafio[4]} | Recompensa: +{desafio[5]} pts</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"✅ Completar", key=f"desafio_{desafio[0]}"):
                completar_desafio(usuario_id, desafio[0])
                st.success(f"Parabéns! Você completou o desafio e ganhou {desafio[5]} pontos!")
                st.rerun()

def mostrar_perfil(usuario_id, nome, text_color, card_bg, icon_color, border_color):
    """Mostra o perfil do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    progresso = c.fetchone()
    conn.close()
    
    if progresso:
        pontos = progresso[1]
        nivel = progresso[2]
        streak = progresso[9] if len(progresso) > 9 else 0
        eventos = progresso[3] if len(progresso) > 3 else 0
        dicas = progresso[4] if len(progresso) > 4 else 0
        visitas = progresso[5] if len(progresso) > 5 else 0
        kg = progresso[6] if len(progresso) > 6 else 0
        arvores = progresso[7] if len(progresso) > 7 else 0
        amigos = progresso[8] if len(progresso) > 8 else 0
        desafios = progresso[11] if len(progresso) > 11 else 0
    else:
        pontos = nivel = 0
        nivel = "🌱 EcoIniciante"
        streak = eventos = dicas = visitas = kg = arvores = amigos = desafios = 0
    
    proximo = get_proximo_nivel(pontos)
    
    # Cards de perfil
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {border_color};'>
            <h2 style='color: {text_color};'>{nivel}</h2>
            <h1 style='color: {icon_color}; font-size: 48px;'>{pontos}</h1>
            <p style='color: {text_color};'>pontos totais</p>
            <div style='height: 8px; background: {border_color}; border-radius: 4px; margin: 10px 0;'>
                <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
            </div>
            <p style='color: {text_color};'>{proximo} pontos para o próximo nível</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {border_color};'>
            <h3 style='color: {text_color};'>🔥 Streak</h3>
            <h1 style='color: #ff9800; font-size: 48px;'>{streak}</h1>
            <p style='color: {text_color};'>dias seguidos</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Estatísticas
    st.markdown(f"<h3 style='color: {text_color};'>📊 Estatísticas</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📅 Eventos</h4>
            <h2 style='color: {icon_color};'>{eventos}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>💡 Dicas</h4>
            <h2 style='color: {icon_color};'>{dicas}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📍 Visitas</h4>
            <h2 style='color: {icon_color};'>{visitas}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>♻️ Kg</h4>
            <h2 style='color: {icon_color};'>{kg}</h2>
        </div>
        """, unsafe_allow_html=True)

def mostrar_ranking(text_color, card_bg, icon_color, border_color):
    """Mostra ranking de usuários"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT u.nome, p.total_pontos, p.nivel, p.desafios_completados
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        ORDER BY p.total_pontos DESC
        LIMIT 10
    """)
    ranking = c.fetchall()
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>🏆 Ranking EcoCidadãos</h3>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
    for i, usuario in enumerate(ranking):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}º"
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='color: {text_color};'><strong>{medalha} {usuario[0]}</strong> - {usuario[2]}</span>
                <span style='color: {icon_color};'><strong>{usuario[1]} pts</strong> | 🎯 {usuario[3]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_convite(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra sistema de convite"""
    codigo = gerar_codigo_convite(usuario_id)
    
    st.markdown(f"<h3 style='color: {text_color};'>👥 Convidar Amigos</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(f"ECOPIRA-{codigo}", language="text")
    with col2:
        if st.button("📋 Copiar"):
            st.success("Código copiado!")

def mostrar_dicas(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra dicas ambientais"""
    st.markdown(f"<h3 style='color: {text_color};'>💡 Dicas Ambientais</h3>", unsafe_allow_html=True)
    
    dicas = [
        ("🌱 Compostagem", "50% do lixo doméstico pode ser compostado!"),
        ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros."),
        ("🔋 Pilhas", "Uma pilha contamina 20 mil litros de água."),
        ("🌳 Árvores", "Uma árvore adulta absorve 150kg de CO2 por ano.")
    ]
    
    for dica in dicas:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 6px solid {icon_color}; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>{dica[0]}</h4>
            <p style='color: {text_color};'>{dica[1]}</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_eventos(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra eventos"""
    st.markdown(f"<h3 style='color: {text_color};'>📅 Próximos Eventos</h3>", unsafe_allow_html=True)
    
    eventos = [
        ("🌱 Feira de Sustentabilidade", "15/03/2026", "Engenho Central"),
        ("♻️ Workshop de Reciclagem", "22/03/2026", "SENAI"),
        ("🌊 Mutirão Rio Piracicaba", "05/04/2026", "Rua do Porto")
    ]
    
    for evento in eventos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ff9f4b; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>{evento[0]}</h4>
            <p style='color: {text_color};'><i class='fas fa-calendar'></i> {evento[1]} | <i class='fas fa-map-marker-alt'></i> {evento[2]}</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_pontos_coleta(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra pontos de coleta"""
    st.markdown(f"<h3 style='color: {text_color};'>📍 Pontos de Coleta</h3>", unsafe_allow_html=True)
    
    pontos = [
        ("Ecoponto Centro", "Av. Rui Barbosa, 800", "⭐ 4.5"),
        ("Shopping Piracicaba", "Av. Limeira, 700", "⭐ 4.8"),
        ("Coopervidros", "R. Treze de Maio, 300", "⭐ 4.2")
    ]
    
    for ponto in pontos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between;'>
                <div>
                    <h4 style='color: {text_color};'>{ponto[0]}</h4>
                    <p style='color: {text_color};'><i class='fas fa-map-pin'></i> {ponto[1]}</p>
                </div>
                <div style='color: gold;'>{ponto[2]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== DETECTAR TEMA ==========
tema = get_theme()
dispositivo = detectar_dispositivo()

# Configurações de cores
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

# CSS
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    
    .stMarkdown, p, h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}
    
    .stButton button {{
        background: {icon_color};
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        font-weight: 600;
    }}
    
    .stButton button:hover {{
        background: #1a8c5f;
        transform: scale(1.05);
    }}
    
    .stTextInput input {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 10px;
    }}
    
    div.stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
    }}
    
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {icon_color} !important;
        color: white !important;
    }}
</style>

<!-- Font Awesome para ícones -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

# Interface
if st.session_state.usuario_logado is None:
    # Tela de login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: {text_color};'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if validar_email(email):
                    conn = sqlite3.connect('ecopiracicaba.db')
                    c = conn.cursor()
                    c.execute("SELECT id, nome, email FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
                    user = c.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.usuario_logado = {
                            'id': user[0], 'nome': user[1], 'email': user[2]
                        }
                        inicializar_progresso(user[0])
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos")
        
        st.markdown("---")
        st.markdown("### 🆕 Novo por aqui?")
        with st.form("cadastro_form"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Criar conta", use_container_width=True):
                if nome and validar_email(email) and len(senha) >= 6:
                    conn = sqlite3.connect('ecopiracicaba.db')
                    c = conn.cursor()
                    try:
                        data_atual = datetime.now().strftime("%d/%m/%Y")
                        c.execute(
                            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
                            (nome, email, senha, data_atual)
                        )
                        conn.commit()
                        st.success("Conta criada! Faça login.")
                    except sqlite3.IntegrityError:
                        st.error("E-mail já existe!")
                    conn.close()
                else:
                    st.error("Preencha todos os campos corretamente")

else:
    # Usuário logado
    if dispositivo == "mobile":
        # Menu mobile
        opcao = st.radio("Menu", ["🏠 Início", "🎯 Desafios", "👤 Perfil", "🏆 Ranking"])
        
        if opcao == "🎯 Desafios":
            mostrar_pagina_desafios(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        elif opcao == "👤 Perfil":
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        elif opcao == "🏆 Ranking":
            mostrar_ranking(text_color, card_bg, icon_color, border_color)
        else:
            st.markdown(f"<h2 style='color: {text_color};'>Bem-vindo, {st.session_state.usuario_logado['nome']}!</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                mostrar_dicas(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
            with col2:
                mostrar_eventos(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
    
    else:
        # Layout desktop
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<h1 style='color: {text_color};'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
        
        with col2:
            if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
                toggle_theme()
        
        # Sidebar com perfil
        with st.sidebar:
            conn = sqlite3.connect('ecopiracicaba.db')
            c = conn.cursor()
            c.execute("SELECT total_pontos, nivel FROM progresso WHERE usuario_id = ?", (st.session_state.usuario_logado['id'],))
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
        
        # Tabs principais
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Início", "🎯 Desafios", "👤 Perfil", "🏆 Ranking", "📍 Pontos"])
        
        with tab1:
            st.markdown(f"<h2 style='color: {text_color};'>Olá, {st.session_state.usuario_logado['nome']}!</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                mostrar_dicas(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
            with col2:
                mostrar_eventos(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        
        with tab2:
            mostrar_pagina_desafios(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        
        with tab3:
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        
        with tab4:
            mostrar_ranking(text_color, card_bg, icon_color, border_color)
        
        with tab5:
            mostrar_pontos_coleta(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
