import streamlit as st
import sqlite3
from datetime import datetime
import re
import hashlib
import time
import random

# Configuração da página
st.set_page_config(
    page_title="EcoPiracicaba 2026",
    page_icon="🌿",
    layout="wide"
)

# ========== FUNÇÕES BÁSICAS ==========

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    return st.session_state.theme

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"
    st.rerun()

# ========== BANCO DE DADOS MÍNIMO ==========

def init_database():
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # APENAS UMA TABELA - usuários com pontos incluídos
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            pontos INTEGER DEFAULT 0,
            desafios INTEGER DEFAULT 0,
            data_cadastro TEXT
        )
    ''')
    
    # Inserir usuário admin
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, pontos, desafios, data_cadastro) VALUES (?, ?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", 1000, 5, datetime.now().strftime("%d/%m/%Y"))
        )
    
    conn.commit()
    conn.close()

# Inicializar banco
init_database()

# ========== DADOS DOS DESAFIOS (FIXOS) ==========

DESAFIOS = [
    {
        "id": 1,
        "titulo": "♻️ Reciclar 10kg",
        "descricao": "Recicle 10kg de materiais recicláveis",
        "pontos": 200,
        "icone": "♻️"
    },
    {
        "id": 2,
        "titulo": "📅 Participar de Evento",
        "descricao": "Participe de 1 evento ambiental",
        "pontos": 150,
        "icone": "📅"
    },
    {
        "id": 3,
        "titulo": "🌳 Plantar Árvore",
        "descricao": "Plante 1 árvore nativa",
        "pontos": 300,
        "icone": "🌳"
    },
    {
        "id": 4,
        "titulo": "🔋 Descartar Pilhas",
        "descricao": "Descarte 5 pilhas",
        "pontos": 100,
        "icone": "🔋"
    },
    {
        "id": 5,
        "titulo": "💧 Economizar Água",
        "descricao": "Reduza consumo em 20%",
        "pontos": 120,
        "icone": "💧"
    }
]

PREMIOS = [
    {"nome": "🥉 Bronze", "min": 3, "pontos": 100},
    {"nome": "🥈 Prata", "min": 5, "pontos": 250},
    {"nome": "🥇 Ouro", "min": 7, "pontos": 500}
]

# ========== FUNÇÕES ==========

def get_nivel(pontos):
    if pontos < 100:
        return "🌱 Iniciante"
    elif pontos < 500:
        return "🌿 Amigo"
    elif pontos < 1000:
        return "🍃 Guardião"
    else:
        return "🌳 Mestre"

def completar_desafio(usuario_id, pontos_ganhos):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar pontos atuais
    c.execute("SELECT pontos, desafios FROM usuarios WHERE id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais, desafios_atuais = resultado
        novos_pontos = pontos_atuais + pontos_ganhos
        novos_desafios = desafios_atuais + 1
        
        # Atualizar
        c.execute(
            "UPDATE usuarios SET pontos = ?, desafios = ? WHERE id = ?",
            (novos_pontos, novos_desafios, usuario_id)
        )
        
        conn.commit()
        conn.close()
        return novos_desafios, novos_pontos
    
    conn.close()
    return 0, 0

# ========== INTERFACE ==========

tema = get_theme()

# Cores
if tema == "dark":
    bg = "#0a1f17"
    card = "#1a3329"
    text = "#FFFFFF"
    border = "#2a4a3a"
    icon = "#8bc34a"
else:
    bg = "#f0fff5"
    card = "#FFFFFF"
    text = "#000000"
    border = "#c0e0d0"
    icon = "#0f5c3f"

# CSS
st.markdown(f"""
<style>
    .stApp {{ background: {bg}; }}
    .stMarkdown, p, h1, h2, h3, h4 {{ color: {text} !important; }}
    .stButton button {{ background: {icon}; color: white; border: none; border-radius: 50px; }}
    .card {{ background: {card}; padding: 20px; border-radius: 15px; border: 1px solid {border}; margin-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"<h1 style='text-align: center;'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
with col3:
    if st.button("🌓 Tema"):
        toggle_theme()

# Login
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

if st.session_state.usuario_logado is None:
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
                    c.execute("SELECT id, nome, pontos, desafios FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
                    user = c.fetchone()
                    conn.close()
                    if user:
                        st.session_state.usuario_logado = {
                            'id': user[0], 
                            'nome': user[1],
                            'pontos': user[2],
                            'desafios': user[3]
                        }
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos")
        
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
    # Sidebar
    with st.sidebar:
        nivel = get_nivel(st.session_state.usuario_logado['pontos'])
        st.markdown(f"""
        <div class='card' style='text-align: center;'>
            <h3>{st.session_state.usuario_logado['nome']}</h3>
            <h4 style='color: {icon};'>{nivel}</h4>
            <h2 style='color: {icon};'>{st.session_state.usuario_logado['pontos']} pts</h2>
            <p>🎯 {st.session_state.usuario_logado['desafios']} desafios</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Desafios", "👤 Perfil", "ℹ️ Sobre"])
    
    with tab1:
        st.markdown(f"<h2>🎯 Desafios</h2>", unsafe_allow_html=True)
        
        # Progresso
        st.markdown(f"""
        <div class='card' style='text-align: center;'>
            <h3>Seu Progresso</h3>
            <div style='display: flex; justify-content: space-around;'>
                <div><span style='font-size: 36px; color: {icon};'>{st.session_state.usuario_logado['desafios']}</span><br>completados</div>
                <div><span style='font-size: 36px; color: gold;'>🏆</span><br>{st.session_state.usuario_logado['pontos']} pts</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prêmios
        st.markdown(f"<h3>🎁 Prêmios</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, premio in enumerate(PREMIOS):
            with cols[i]:
                cor = "#cd7f32" if i == 0 else "#c0c0c0" if i == 1 else "#ffd700"
                disponivel = st.session_state.usuario_logado['desafios'] >= premio["min"]
                st.markdown(f"""
                <div class='card' style='text-align: center; border: 2px solid {cor if disponivel else border}; opacity: {1 if disponivel else 0.5};'>
                    <span style='font-size: 36px;'>{premio['nome'][0]}</span>
                    <h4>{premio['nome']}</h4>
                    <p>{premio['min']} desafios</p>
                    <p style='color: {icon};'>+{premio['pontos']} pts</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Lista de desafios
        st.markdown(f"<h3>📋 Desafios</h3>", unsafe_allow_html=True)
        
        for desafio in DESAFIOS:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class='card' style='border-left: 6px solid {icon};'>
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <span style='font-size: 40px;'>{desafio['icone']}</span>
                        <div>
                            <h4 style='margin: 0;'>{desafio['titulo']}</h4>
                            <p style='margin: 5px 0;'>{desafio['descricao']}</p>
                            <p style='color: {icon}; margin: 0;'>+{desafio['pontos']} pontos</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅ Completar", key=f"btn_{desafio['id']}"):
                    novos_desafios, novos_pontos = completar_desafio(
                        st.session_state.usuario_logado['id'], 
                        desafio['pontos']
                    )
                    st.session_state.usuario_logado['desafios'] = novos_desafios
                    st.session_state.usuario_logado['pontos'] = novos_pontos
                    
                    # Verificar prêmios
                    for premio in PREMIOS:
                        if novos_desafios == premio["min"]:
                            completar_desafio(st.session_state.usuario_logado['id'], premio["pontos"])
                            st.session_state.usuario_logado['pontos'] += premio["pontos"]
                            st.balloons()
                            st.success(f"🏆 GANHOU {premio['nome']}! +{premio['pontos']} pontos!")
                    
                    st.rerun()
    
    with tab2:
        st.markdown(f"<h2>👤 Perfil</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h2 style='color: {icon};'>{get_nivel(st.session_state.usuario_logado['pontos'])}</h2>
                <h1 style='color: {icon}; font-size: 48px;'>{st.session_state.usuario_logado['pontos']}</h1>
                <p>pontos totais</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h3>🎯 Desafios</h3>
                <h1 style='color: {icon}; font-size: 48px;'>{st.session_state.usuario_logado['desafios']}</h1>
                <p>completados</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Estatísticas
        st.markdown(f"<h3>📊 Estatísticas</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h4>📅 Eventos</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h4>💡 Dicas</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h4>📍 Visitas</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"<h2>ℹ️ Sobre</h2>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card'>
            <h3>🌿 EcoPiracicaba 2026</h3>
            <p>Aplicativo de sustentabilidade para a cidade de Piracicaba.</p>
            <p>Complete desafios, ganhe pontos e suba no ranking!</p>
            <p>📍 Piracicaba - SP</p>
        </div>
        
        <div class='card'>
            <h4>📅 Próximos Eventos</h4>
            <p>🌱 Feira Sustentável - 15/03</p>
            <p>♻️ Workshop Reciclagem - 22/03</p>
            <p>🌊 Mutirão Rio - 05/04</p>
        </div>
        
        <div class='card'>
            <h4>📍 Pontos de Coleta</h4>
            <p>• Ecoponto Centro - Av. Rui Barbosa, 800</p>
            <p>• Shopping Piracicaba - Av. Limeira, 700</p>
            <p>• Coopervidros - R. Treze de Maio, 300</p>
        </div>
        
        <div class='card'>
            <h4>💡 Dicas</h4>
            <p>🌱 50% do lixo pode ser compostado</p>
            <p>💧 Banho de 15 min gasta 135L</p>
            <p>🔋 1 pilha contamina 20 mil litros</p>
            <p>🌳 1 árvore absorve 150kg CO2/ano</p>
        </div>
        """, unsafe_allow_html=True)
