import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import random
import string

# Configuração da página
st.set_page_config(
    page_title="EcoPiracicaba 2026",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto"
)

# Detectar tema do sistema
def get_theme():
    """Detecta se o sistema está em modo dark ou light"""
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

# Gerar senha aleatória para login social
def gerar_senha_aleatoria():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Inicializar banco de dados
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
            avatar TEXT,
            cidade TEXT DEFAULT 'Piracicaba',
            interesses TEXT,
            login_provider TEXT DEFAULT 'email',
            data_cadastro TEXT,
            ultimo_acesso TEXT
        )
    ''')
    
    # Tabela de inscrições em eventos
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TEXT,
            confirmado BOOLEAN DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de eventos
    c.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data TEXT,
            hora TEXT,
            local TEXT,
            palestrante TEXT,
            tipo TEXT,
            vagas INTEGER,
            inscritos INTEGER DEFAULT 0,
            imagem TEXT,
            organizador TEXT,
            contato TEXT
        )
    ''')
    
    # Tabela de dicas ambientais
    c.execute('''
        CREATE TABLE IF NOT EXISTS dicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT,
            categoria TEXT,
            data_publicacao TEXT,
            likes INTEGER DEFAULT 0,
            autor TEXT
        )
    ''')
    
    # Tabela de pontos de coleta
    c.execute('''
        CREATE TABLE IF NOT EXISTS pontos_coleta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT,
            categoria TEXT,
            horario TEXT,
            telefone TEXT,
            latitude REAL,
            longitude REAL,
            avaliacao REAL DEFAULT 0,
            descricao TEXT
        )
    ''')
    
    # Inserir dados iniciais
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses, login_provider) VALUES (?, ?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", datetime.now().strftime("%d/%m/%Y"), "sustentabilidade,reciclagem", "email")
        )
    
    # Eventos 2026
    c.execute("SELECT * FROM eventos")
    if not c.fetchone():
        eventos = [
            ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos, artesanato sustentável e startups verdes", "15/03/2026", "09:00", "Engenho Central", "Secretaria do Meio Ambiente", "feira", 1000, 0, "🌿", "Prefeitura de Piracicaba", "(19) 3403-1100"),
            ("♻️ Workshop de Reciclagem", "Aprenda técnicas avançadas de reciclagem em casa", "22/03/2026", "14:00", "SENAI Piracicaba", "Joana Silva - Engenheira Ambiental", "workshop", 50, 0, "🔄", "SENAI", "(19) 3412-5000"),
            ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio com atividades educativas", "05/04/2026", "08:00", "Rua do Porto", "Movimento Rio Vivo", "mutirão", 200, 0, "💧", " SOS Rio Piracicaba", "(19) 99765-4321"),
            ("🌿 Palestra: Compostagem", "Como fazer compostagem doméstica e comunitária", "12/04/2026", "10:00", "Horto Municipal", "Dr. Carlos Ambiental", "palestra", 100, 0, "🌱", "Horto Municipal", "(19) 3434-5678"),
            ("🌍 Dia da Terra", "Celebração com atividades, música e feira verde", "22/04/2026", "09:00", "Parque da Rua do Porto", "Coletivo Ambiental", "evento", 2000, 0, "🌎", "ONG Planeta Verde", "(19) 99876-5432"),
            ("🔋 Descarte de Eletrônicos", "Campanha de coleta de lixo eletrônico", "10/05/2026", "09:00", "Shopping Piracicaba", "Green Eletronics", "campanha", 0, 0, "📱", "Shopping Piracicaba", "(19) 3403-3000"),
            ("🌳 Plantio de Árvores", "Mutirão de plantio de árvores nativas", "05/06/2026", "08:30", "Parque Ecológico", "SOS Mata Atlântica", "mutirão", 300, 0, "🌳", "SOS Mata Atlântica", "(11) 3262-4088")
        ]
        for e in eventos:
            c.execute(
                """INSERT INTO eventos 
                   (titulo, descricao, data, hora, local, palestrante, tipo, vagas, inscritos, imagem, organizador, contato) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                e
            )
    
    # Dicas ambientais
    c.execute("SELECT * FROM dicas")
    if not c.fetchone():
        dicas = [
            ("🌱 Compostagem Doméstica", "Você sabia que 50% do lixo doméstico pode ser compostado? Aprenda a fazer sua própria composteira com baldes e minhocas californianas.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe EcoPiracicaba"),
            ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros de água. Reduza para 5 minutos e economize 90 litros por banho!", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas e Baterias", "Nunca descarte pilhas no lixo comum. Leve a pontos de coleta específicos. Uma pilha pode contaminar 20 mil litros de água.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Plante uma Árvore", "Uma árvore adulta absorve até 150kg de CO2 por ano. Plante árvores nativas da região de Piracicaba.", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica")
        ]
        for d in dicas:
            c.execute(
                "INSERT INTO dicas (titulo, conteudo, categoria, data_publicacao, likes, autor) VALUES (?, ?, ?, ?, ?, ?)",
                d
            )
    
    # Pontos de coleta
    c.execute("SELECT * FROM pontos_coleta")
    if not c.fetchone():
        pontos = [
            ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", -22.724, -47.648, 4.5, "Recebe todos os tipos de recicláveis, eletrônicos e óleo de cozinha"),
            ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", -22.718, -47.642, 4.8, "Ponto de coleta de pilhas e baterias no piso G1"),
            ("Coopervidros", "R. Treze de Maio, 300 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", -22.731, -47.651, 4.2, "Cooperativa especializada em reciclagem de vidros")
        ]
        for p in pontos:
            c.execute(
                """INSERT INTO pontos_coleta 
                   (nome, endereco, categoria, horario, telefone, latitude, longitude, avaliacao, descricao) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                p
            )
    
    conn.commit()
    conn.close()

# Inicializar banco
init_database()

# Detectar tema e dispositivo
tema = get_theme()
dispositivo = detectar_dispositivo()

# CSS com temas dinâmicos
if tema == "dark":
    bg_color = "#0a1f17"
    card_bg = "#1a3329"
    text_color = "#ffffff"
    secondary_text = "#c0e0d0"
    border_color = "#2a4a3a"
    hover_color = "#2a5a45"
    icon_color = "#8bc34a"
    gradient_start = "#0a1f17"
    gradient_end = "#1a4a3a"
    logo_filter = "brightness(0) invert(1)"
    google_btn_bg = "#4285F4"
    apple_btn_bg = "#000000"
else:
    bg_color = "#f0fff5"
    card_bg = "#ffffff"
    text_color = "#000000"
    secondary_text = "#2a5e45"
    border_color = "#c0e0d0"
    hover_color = "#e0f5e9"
    icon_color = "#0f5c3f"
    gradient_start = "#e8f5e9"
    gradient_end = "#c8e6c9"
    logo_filter = "brightness(0.5) sepia(1) hue-rotate(120deg)"
    google_btn_bg = "#4285F4"
    apple_btn_bg = "#000000"

# CSS personalizado
st.markdown(f"""
<style>
    /* Estilos globais */
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    
    .main-title {{
        text-align: center;
        color: {text_color};
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    
    .sub-title {{
        text-align: center;
        color: {secondary_text};
        font-size: 1.5rem;
        margin-bottom: 2rem;
        font-style: italic;
    }}
    
    /* Botões de login social */
    .social-login-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        border: none;
        border-radius: 50px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        color: white;
        gap: 10px;
    }}
    
    .social-login-btn i {{
        font-size: 20px;
    }}
    
    .social-login-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    .google-btn {{
        background: {google_btn_bg};
    }}
    
    .apple-btn {{
        background: {apple_btn_bg};
    }}
    
    .divider {{
        display: flex;
        align-items: center;
        text-align: center;
        color: {secondary_text};
        margin: 20px 0;
    }}
    
    .divider::before,
    .divider::after {{
        content: '';
        flex: 1;
        border-bottom: 1px solid {border_color};
    }}
    
    .divider::before {{
        margin-right: .25em;
    }}
    
    .divider::after {{
        margin-left: .25em;
    }}
    
    /* Cards */
    .eco-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid {border_color};
        margin-bottom: 20px;
        transition: transform 0.3s, box-shadow 0.3s;
        color: {text_color};
    }}
    
    .eco-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,100,50,0.2);
    }}
    
    .evento-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #ff9f4b;
        color: {text_color};
        transition: transform 0.2s;
    }}
    
    .evento-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }}
    
    .dica-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-right: 6px solid {icon_color};
        color: {text_color};
    }}
    
    .ponto-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid {border_color};
        color: {text_color};
    }}
    
    /* Botões */
    .eco-button {{
        background: {icon_color};
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 600;
        cursor: pointer;
        transition: 0.2s;
        text-decoration: none;
        display: inline-block;
    }}
    
    .eco-button:hover {{
        background: #1a8c5f;
        transform: scale(1.05);
    }}
    
    /* Sidebar */
    .stSidebar {{
        background: {card_bg};
    }}
    
    .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {{
        color: {text_color} !important;
    }}
    
    /* Estatísticas */
    .stat-box {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid {icon_color};
        color: {text_color};
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {icon_color};
    }}
    
    .stat-label {{
        font-size: 1rem;
        color: {secondary_text};
    }}
    
    /* Ícones */
    .eco-icon {{
        font-size: 2rem;
        color: {icon_color};
        filter: {logo_filter};
    }}
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {card_bg};
        border-radius: 50px 50px 0 0;
        padding: 10px 20px;
        color: {text_color};
        border: 1px solid {border_color};
        border-bottom: none;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {icon_color} !important;
        color: white !important;
    }}
    
    /* Badges */
    .categoria-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }}
    
    .badge-palestra {{ background: #ff9800; color: white; }}
    .badge-workshop {{ background: #4caf50; color: white; }}
    .badge-mutirao {{ background: #2196f3; color: white; }}
    .badge-feira {{ background: #9c27b0; color: white; }}
    .badge-campanha {{ background: #f44336; color: white; }}
    
    /* Progresso */
    .progress-bar {{
        height: 8px;
        background: {border_color};
        border-radius: 4px;
        margin: 10px 0;
    }}
    
    .progress-fill {{
        height: 100%;
        background: {icon_color};
        border-radius: 4px;
        transition: width 0.3s;
    }}
</style>

<!-- Font Awesome para ícones sociais -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# Funções de login social
def login_com_google():
    """Simula login com Google"""
    # Em produção, aqui viria a integração real com OAuth
    nome = f"Usuário Google {random.randint(100, 999)}"
    email = f"usuario.google{random.randint(1000, 9999)}@gmail.com"
    senha = gerar_senha_aleatoria()
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verifica se já existe
    c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = c.fetchone()
    
    if user:
        st.session_state.usuario_logado = {
            'id': user[0], 'nome': user[1], 'email': user[2]
        }
    else:
        # Cria novo usuário
        c.execute(
            """INSERT INTO usuarios (nome, email, senha, login_provider, data_cadastro) 
               VALUES (?, ?, ?, ?, ?)""",
            (nome, email, senha, 'google', datetime.now().strftime("%d/%m/%Y"))
        )
        conn.commit()
        
        # Busca o usuário recém-criado
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        st.session_state.usuario_logado = {
            'id': user[0], 'nome': user[1], 'email': user[2]
        }
    
    conn.close()
    st.rerun()

def login_com_apple():
    """Simula login com Apple"""
    nome = f"Usuário Apple {random.randint(100, 999)}"
    email = f"usuario.apple{random.randint(1000, 9999)}@icloud.com"
    senha = gerar_senha_aleatoria()
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = c.fetchone()
    
    if user:
        st.session_state.usuario_logado = {
            'id': user[0], 'nome': user[1], 'email': user[2]
        }
    else:
        c.execute(
            """INSERT INTO usuarios (nome, email, senha, login_provider, data_cadastro) 
               VALUES (?, ?, ?, ?, ?)""",
            (nome, email, senha, 'apple', datetime.now().strftime("%d/%m/%Y"))
        )
        conn.commit()
        
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        st.session_state.usuario_logado = {
            'id': user[0], 'nome': user[1], 'email': user[2]
        }
    
    conn.close()
    st.rerun()

# Interface principal
if dispositivo == "mobile":
    # Versão mobile simplificada
    st.markdown("""
    <style>
        .block-container {
            padding: 0 !important;
            max-width: 400px !important;
            margin: 0 auto !important;
        }
        header {display: none}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align: center; padding: 20px;'>
        <i class='fas fa-leaf' style='font-size: 80px; color: {icon_color};'></i>
        <h1 style='color: {text_color};'>EcoPiracicaba</h1>
        <p style='color: {secondary_text};'>Versão Mobile</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # ========== INTERFACE DESKTOP ==========
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"<i class='fas fa-leaf eco-icon' style='font-size: 60px;'></i>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<h1 class="main-title">🌿 EcoPiracicaba 2026</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Sustentabilidade em ação na cidade de Piracicaba</p>', unsafe_allow_html=True)
    with col3:
        if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
            toggle_theme()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"<i class='fas fa-leaf eco-icon' style='font-size: 80px; display: block; text-align: center;'></i>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: {text_color}; text-align: center;'>🌱 EcoCidadão</h2>", unsafe_allow_html=True)
        
        # Estado do usuário
        if 'usuario_logado' not in st.session_state:
            st.session_state.usuario_logado = None
        
        if st.session_state.usuario_logado is None:
            # Login com Google e Apple
            st.markdown(f"<h3 style='color: {text_color};'>Acesso Rápido</h3>", unsafe_allow_html=True)
            
            # Botão Google
            st.markdown(f"""
            <button class='social-login-btn google-btn' onclick='login_google()'>
                <i class='fab fa-google'></i> Continuar com Google
            </button>
            """, unsafe_allow_html=True)
            if st.button("🌐 Login com Google", key="google_btn", use_container_width=True):
                login_com_google()
            
            # Botão Apple
            st.markdown(f"""
            <button class='social-login-btn apple-btn' onclick='login_apple()'>
                <i class='fab fa-apple'></i> Continuar com Apple
            </button>
            """, unsafe_allow_html=True)
            if st.button("🍎 Login com Apple", key="apple_btn", use_container_width=True):
                login_com_apple()
            
            # Divisor
            st.markdown(f'<div class="divider">ou</div>', unsafe_allow_html=True)
            
            # Login tradicional
            with st.expander("📧 Login com E-mail", expanded=True):
                tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
                
                with tab1:
                    email = st.text_input("E-mail", key="login_email")
                    senha = st.text_input("Senha", type="password", key="login_senha")
                    
                    if st.button("🌿 Entrar", use_container_width=True):
                        conn = sqlite3.connect('ecopiracicaba.db')
                        c = conn.cursor()
                        c.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
                        user = c.fetchone()
                        conn.close()
                        
                        if user:
                            st.session_state.usuario_logado = {
                                'id': user[0], 'nome': user[1], 'email': user[2]
                            }
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos")
                
                with tab2:
                    with st.form("cadastro_form"):
                        nome = st.text_input("Nome completo")
                        email = st.text_input("E-mail")
                        senha = st.text_input("Senha", type="password")
                        interesses = st.multiselect("Interesses", 
                            ["Sustentabilidade", "Reciclagem", "Eventos", "Voluntariado", "Compostagem"])
                        
                        if st.form_submit_button("🌱 Criar conta", use_container_width=True):
                            conn = sqlite3.connect('ecopiracicaba.db')
                            c = conn.cursor()
                            try:
                                c.execute(
                                    """INSERT INTO usuarios 
                                       (nome, email, senha, interesses, data_cadastro, login_provider) 
                                       VALUES (?, ?, ?, ?, ?, ?)""",
                                    (nome, email, senha, ",".join(interesses), 
                                     datetime.now().strftime("%d/%m/%Y"), "email")
                                )
                                conn.commit()
                                st.success("Conta criada! Faça login.")
                            except Exception as e:
                                st.error("E-mail já existe")
                            conn.close()
        else:
            # Usuário logado
            st.success(f"🌿 Olá, {st.session_state.usuario_logado['nome'].split(' ')[0]}!")
            
            # Busca provider do login
            conn = sqlite3.connect('ecopiracicaba.db')
            c = conn.cursor()
            c.execute("SELECT login_provider FROM usuarios WHERE id = ?", (st.session_state.usuario_logado['id'],))
            provider = c.fetchone()
            conn.close()
            
            if provider and provider[0] == 'google':
                st.markdown("<p style='color: #4285F4;'><i class='fab fa-google'></i> Conectado com Google</p>", unsafe_allow_html=True)
            elif provider and provider[0] == 'apple':
                st.markdown("<p style='color: #000000;'><i class='fab fa-apple'></i> Conectado com Apple</p>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='color: {text_color};'>🌍 Nível: EcoAtivista</p>", unsafe_allow_html=True)
            st.progress(0.65, text="65% para próximo nível")
            
            if st.button("Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.rerun()
        
        st.markdown("---")
        
        # Estatísticas rápidas
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM eventos WHERE data LIKE '%2026%'")
        total_eventos = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM dicas")
        total_dicas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM pontos_coleta")
        total_pontos = c.fetchone()[0]
        conn.close()
        
        st.markdown(f"""
        <div style='text-align: center; color: {text_color};'>
            <h4>📊 Estatísticas</h4>
            <p>🌍 {total_eventos} Eventos em 2026</p>
            <p>💡 {total_dicas} Dicas Ambientais</p>
            <p>📍 {total_pontos} Pontos de Coleta</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"<p style='color: {secondary_text}; text-align: center;'>🌱 Piracicaba - SP</p>", unsafe_allow_html=True)
    
    # Conteúdo principal
    if st.session_state.usuario_logado is None:
        # Página de boas-vindas
        st.markdown(f"""
        <div style='text-align: center; padding: 50px; color: {text_color};'>
            <i class="fas fa-seedling" style='font-size: 80px; color: {icon_color};'></i>
            <h1>Bem-vindo ao EcoPiracicaba</h1>
            <p style='font-size: 1.2rem;'>Faça login com Google, Apple ou e-mail para acessar todas as funcionalidades</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards de apresentação
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='eco-card' style='text-align: center;'>
                <i class='fas fa-calendar-alt eco-icon' style='font-size: 40px;'></i>
                <h3>Eventos 2026</h3>
                <p>Palestras, workshops, mutirões e feiras sustentáveis</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='eco-card' style='text-align: center;'>
                <i class='fas fa-lightbulb eco-icon' style='font-size: 40px;'></i>
                <h3>Dicas Ambientais</h3>
                <p>Aprenda a viver de forma mais sustentável</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='eco-card' style='text-align: center;'>
                <i class='fas fa-map-marker-alt eco-icon' style='font-size: 40px;'></i>
                <h3>Pontos de Coleta</h3>
                <p>Onde descartar cada tipo de resíduo</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Abas principais
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌍 Dashboard", "📅 Eventos 2026", "💡 Dicas Verdes", "📍 Pontos de Coleta"
        ])
        
        with tab1:
            st.markdown(f"<h2 style='color: {text_color};'>🌍 Dashboard Ambiental</h2>", unsafe_allow_html=True)
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-number'>15.432</div>
                    <div class='stat-label'>🌳 Árvores Plantadas</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-number'>2.450</div>
                    <div class='stat-label'>♻️ Toneladas Recicladas</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-number'>87</div>
                    <div class='stat-label'>🏫 Escolas Participantes</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-number'>12.847</div>
                    <div class='stat-label'>👥 Participantes</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            with col1:
                tipos = ['Palestras', 'Workshops', 'Mutirões', 'Feiras', 'Campanhas']
                quantidades = [25, 18, 12, 8, 15]
                fig = px.pie(values=quantidades, names=tipos, title="Eventos por Tipo em 2026",
                            color_discrete_sequence=['#0f5c3f', '#1a8c5f', '#2ecc71', '#27ae60', '#229954'])
                fig.update_layout(template="plotly_white" if tema == "light" else "plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
                participantes = [850, 1200, 2100, 1850, 2300, 2800]
                fig = go.Figure(data=go.Scatter(x=meses, y=participantes, mode='lines+markers',
                                               line=dict(color='#0f5c3f', width=4)))
                fig.update_layout(title="Participação em Eventos - 1º Semestre 2026",
                                 xaxis_title="Mês", yaxis_title="Participantes",
                                 template="plotly_white" if tema == "light" else "plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            # Próximos eventos
            st.markdown(f"<h3 style='color: {text_color};'>📅 Próximos Eventos</h3>", unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            eventos = pd.read_sql_query("SELECT * FROM eventos ORDER BY data LIMIT 3", conn)
            conn.close()
            
            for _, evento in eventos.iterrows():
                st.markdown(f"""
                <div class='evento-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <span class='categoria-badge badge-{evento["tipo"]}'>{evento["tipo"].upper()}</span>
                            <h3 style='color: {text_color};'>{evento['titulo']}</h3>
                            <p><i class='fas fa-calendar'></i> {evento['data']} às {evento['hora']}</p>
                            <p><i class='fas fa-map-marker-alt'></i> {evento['local']}</p>
                            <p><i class='fas fa-user'></i> {evento['palestrante']}</p>
                        </div>
                        <div style='text-align: right;'>
                            <i class='fas fa-users' style='color: {icon_color};'></i>
                            <p><strong>{evento['inscritos']}/{evento['vagas']}</strong> inscritos</p>
                            <div class='progress-bar'>
                                <div class='progress-fill' style='width: {min(100, (evento["inscritos"]/max(evento["vagas"],1))*100)}%;'></div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown(f"<h2 style='color: {text_color};'>📅 Agenda Sustentável 2026</h2>", unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            eventos = pd.read_sql_query("SELECT * FROM eventos ORDER BY data", conn)
            conn.close()
            
            for _, evento in eventos.iterrows():
                st.markdown(f"""
                <div class='evento-card'>
                    <div style='display: flex; gap: 20px;'>
                        <div style='min-width: 100px; text-align: center; background: {icon_color}; border-radius: 10px; padding: 10px; color: white;'>
                            <div style='font-size: 24px; font-weight: bold;'>{evento['data'].split('/')[0]}</div>
                            <div style='font-size: 14px;'>{evento['data'].split('/')[1]}</div>
                            <div style='font-size: 12px;'>{evento['hora']}</div>
                        </div>
                        <div style='flex: 1;'>
                            <div style='display: flex; gap: 10px; margin-bottom: 10px;'>
                                <span class='categoria-badge badge-{evento["tipo"]}'>{evento["tipo"].upper()}</span>
                                <span style='color: {secondary_text};'><i class='fas fa-map-marker-alt'></i> {evento['local']}</span>
                            </div>
                            <h3 style='color: {text_color}; margin: 0;'>{evento['titulo']}</h3>
                            <p style='color: {secondary_text};'>{evento['descricao']}</p>
                            <p><i class='fas fa-user'></i> {evento['palestrante']} · <i class='fas fa-building'></i> {evento['organizador']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown(f"<h2 style='color: {text_color};'>💡 Dicas para um Planeta Mais Verde</h2>", unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            dicas = pd.read_sql_query("SELECT * FROM dicas ORDER BY likes DESC", conn)
            conn.close()
            
            col1, col2 = st.columns(2)
            for i, (_, dica) in enumerate(dicas.iterrows()):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f"""
                    <div class='dica-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span class='categoria-badge' style='background: {icon_color}; color: white;'>{dica['categoria'].upper()}</span>
                            <span><i class='fas fa-heart' style='color: #ff6b6b;'></i> {dica['likes']}</span>
                        </div>
                        <h3 style='color: {text_color};'>{dica['titulo']}</h3>
                        <p style='color: {secondary_text};'>{dica['conteudo']}</p>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <small><i class='fas fa-user'></i> {dica['autor']} · {dica['data_publicacao']}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta Seletiva</h2>", unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            pontos = pd.read_sql_query("SELECT * FROM pontos_coleta ORDER BY avaliacao DESC", conn)
            conn.close()
            
            for _, ponto in pontos.iterrows():
                st.markdown(f"""
                <div class='ponto-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <h3 style='color: {text_color};'>{ponto['nome']}</h3>
                            <p><i class='fas fa-map-pin'></i> {ponto['endereco']}</p>
                            <p><i class='fas fa-clock'></i> {ponto['horario']}</p>
                            <p><i class='fas fa-phone'></i> {ponto['telefone']}</p>
                            <p><small>{ponto['descricao']}</small></p>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 24px; color: gold;'>{'★' * int(ponto['avaliacao'])}{'☆' * (5 - int(ponto['avaliacao']))}</div>
                            <p>{ponto['avaliacao']}/5.0</p>
                            <span class='categoria-badge' style='background: {icon_color}; color: white;'>{ponto['categoria'].upper()}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
