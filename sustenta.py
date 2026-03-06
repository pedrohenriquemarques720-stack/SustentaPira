import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime
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

# Validar e-mail
def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Gerar senha aleatória para login social
def gerar_senha_aleatoria():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Inicializar banco de dados
def init_database():
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verifica se a tabela usuarios existe e tem a estrutura correta
    c.execute("PRAGMA table_info(usuarios)")
    colunas = c.fetchall()
    colunas_existentes = [col[1] for col in colunas]
    
    # Se a tabela não existe, cria com todas as colunas
    if not colunas:
        c.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                avatar TEXT,
                cidade TEXT DEFAULT 'Piracicaba',
                interesses TEXT,
                login_provider TEXT DEFAULT 'email',
                provider_id TEXT,
                biometria_habilitada INTEGER DEFAULT 0,
                biometria_token TEXT,
                data_cadastro TEXT,
                ultimo_acesso TEXT
            )
        ''')
    else:
        # Se a tabela existe mas falta alguma coluna, adiciona
        if 'biometria_habilitada' not in colunas_existentes:
            c.execute("ALTER TABLE usuarios ADD COLUMN biometria_habilitada INTEGER DEFAULT 0")
        if 'biometria_token' not in colunas_existentes:
            c.execute("ALTER TABLE usuarios ADD COLUMN biometria_token TEXT")
        if 'login_provider' not in colunas_existentes:
            c.execute("ALTER TABLE usuarios ADD COLUMN login_provider TEXT DEFAULT 'email'")
        if 'provider_id' not in colunas_existentes:
            c.execute("ALTER TABLE usuarios ADD COLUMN provider_id TEXT")
    
    # Tabela de tokens biométricos
    c.execute('''
        CREATE TABLE IF NOT EXISTS biometria_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER UNIQUE,
            token TEXT NOT NULL,
            dispositivo TEXT,
            data_cadastro TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de inscrições em eventos
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TEXT,
            confirmado INTEGER DEFAULT 0,
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
    
    # Inserir dados iniciais se necessário
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
            ("🌳 Plantio de Árvores", "Mutirão de plantio de árvores nativas", "05/06/2026", "08:30", "Parque Ecológico", "SOS Mata Atlântica", "mutirão", 300, 0, "🌳", "SOS Mata Atlântica", "(11) 3262-4088"),
            ("🚴 Passeio Ciclístico", "Passeio ecológico de bike pela cidade", "20/06/2026", "08:00", "Largo dos Pescadores", "Ciclovida", "passeio", 150, 0, "🚲", "Associação Ciclistas", "(19) 99876-1234"),
            ("🥕 Feira Orgânica", "Feira de produtos orgânicos e agroecológicos", "10/07/2026", "08:00", "Mercado Municipal", "Associação Orgânicos", "feira", 0, 0, "🥬", "Mercadão", "(19) 3434-7890")
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

# Configurações de cores baseadas no tema
if tema == "dark":
    bg_color = "#0a1f17"
    card_bg = "#1a3329"
    text_color = "#FFFFFF"
    secondary_text = "#E0E0E0"
    border_color = "#2a4a3a"
    hover_color = "#2a5a45"
    icon_color = "#8bc34a"
    gradient_start = "#0a1f17"
    gradient_end = "#1a4a3a"
    logo_filter = "brightness(0) invert(1)"
    google_btn_bg = "#4285F4"
    apple_btn_bg = "#000000"
    input_bg = "#2a3a32"
    input_text = "#FFFFFF"
    label_color = "#FFFFFF"
    tab_color = "#FFFFFF"
    tab_active_bg = "#8bc34a"
    tab_active_text = "#000000"
    stat_text = "#FFFFFF"
    stat_number_color = "#8bc34a"
else:
    bg_color = "#f0fff5"
    card_bg = "#FFFFFF"
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
    input_bg = "#FFFFFF"
    input_text = "#000000"
    label_color = "#000000"
    tab_color = "#000000"
    tab_active_bg = "#0f5c3f"
    tab_active_text = "#FFFFFF"
    stat_text = "#000000"
    stat_number_color = "#0f5c3f"

# CSS base (compartilhado entre mobile e desktop)
base_css = f"""
<style>
    /* Estilos globais */
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    
    /* Todos os textos padrão */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, 
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] h5,
    div[data-testid="stMarkdownContainer"] h6,
    .st-bb, .row-widget, .stAlert p {{
        color: {text_color} !important;
    }}
    
    /* Labels de formulários */
    .stTextInput label, .stSelectbox label, .stMultiselect label,
    .stCheckbox label, .stRadio label, .stDateInput label,
    .stNumberInput label, .stTextArea label {{
        color: {label_color} !important;
        font-weight: 500 !important;
    }}
    
    /* Input fields */
    .stTextInput input, .stSelectbox div, .stMultiselect div,
    .stDateInput input, .stNumberInput input, .stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Placeholders */
    .stTextInput input::placeholder {{
        color: {secondary_text} !important;
        opacity: 0.7;
    }}
    
    /* Botões padrão */
    .stButton button {{
        color: {text_color} !important;
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
    }}
    
    .stButton button:hover {{
        background: {hover_color} !important;
        color: {text_color} !important;
    }}
    
    .main-title {{
        text-align: center;
        color: {text_color} !important;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    
    .sub-title {{
        text-align: center;
        color: {secondary_text} !important;
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
        color: white !important;
        gap: 10px;
    }}
    
    .social-login-btn i {{
        font-size: 20px;
        color: white !important;
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
        color: {secondary_text} !important;
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
        color: {text_color} !important;
    }}
    
    .eco-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,100,50,0.2);
    }}
    
    .eco-card h3, .eco-card p {{
        color: {text_color} !important;
    }}
    
    .evento-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #ff9f4b;
        color: {text_color} !important;
        transition: transform 0.2s;
    }}
    
    .evento-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }}
    
    .evento-card h3, .evento-card p, .evento-card span {{
        color: {text_color} !important;
    }}
    
    .dica-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-right: 6px solid {icon_color};
        color: {text_color} !important;
    }}
    
    .dica-card h3, .dica-card p, .dica-card span {{
        color: {text_color} !important;
    }}
    
    .ponto-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid {border_color};
        color: {text_color} !important;
    }}
    
    .ponto-card h3, .ponto-card p, .ponto-card span {{
        color: {text_color} !important;
    }}
    
    /* Botões */
    .eco-button {{
        background: {icon_color};
        color: white !important;
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
    
    .eco-button i {{
        color: white !important;
    }}
    
    /* Sidebar */
    .stSidebar {{
        background: {card_bg};
    }}
    
    .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3,
    .stSidebar .stMarkdown h4,
    .stSidebar .stMarkdown h5,
    .stSidebar .stMarkdown h6,
    .stSidebar .stText,
    .stSidebar .stAlert p {{
        color: {text_color} !important;
    }}
    
    /* Estatísticas */
    .stat-box {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid {icon_color};
        color: {text_color} !important;
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {stat_number_color} !important;
    }}
    
    .stat-label {{
        font-size: 1rem;
        color: {secondary_text} !important;
    }}
    
    /* Ícones */
    .eco-icon {{
        font-size: 2rem;
        color: {icon_color} !important;
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
        color: {tab_color} !important;
        border: 1px solid {border_color};
        border-bottom: none;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {tab_active_bg} !important;
        color: {tab_active_text} !important;
    }}
    
    /* Badges */
    .categoria-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
        color: white !important;
    }}
    
    .badge-palestra {{ background: #ff9800; }}
    .badge-workshop {{ background: #4caf50; }}
    .badge-mutirao {{ background: #2196f3; }}
    .badge-feira {{ background: #9c27b0; }}
    .badge-campanha {{ background: #f44336; }}
    .badge-passeio {{ background: #00bcd4; }}
    
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
    
    /* Expander */
    .streamlit-expanderHeader {{
        color: {text_color} !important;
        background: {card_bg} !important;
    }}
    
    /* Select boxes */
    .stSelectbox div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
    /* Multiselect */
    .stMultiSelect div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
    /* Success/Error/Warning messages */
    .stAlert {{
        color: {text_color} !important;
    }}
    
    .stAlert p {{
        color: {text_color} !important;
    }}
    
    /* Info boxes */
    .st-info {{
        background: {card_bg} !important;
        color: {text_color} !important;
    }}
</style>

<!-- Font Awesome para ícones -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
"""

# Aplicar CSS base
st.markdown(base_css, unsafe_allow_html=True)

# Funções de login social
def login_com_google():
    """Login com Google"""
    try:
        nomes_google = ["Ana Silva", "João Pereira", "Maria Santos", "Pedro Oliveira", "Carla Souza"]
        nome = random.choice(nomes_google)
        email = f"{nome.lower().replace(' ', '.')}{random.randint(1,999)}@gmail.com"
        senha = gerar_senha_aleatoria()
        
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        c.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        
        if user:
            st.session_state.usuario_logado = {
                'id': user[0], 'nome': user[1], 'email': user[2]
            }
            st.success(f"Bem-vindo de volta, {user[1]}!")
        else:
            data_atual = datetime.now().strftime("%d/%m/%Y")
            c.execute(
                "INSERT INTO usuarios (nome, email, senha, login_provider, data_cadastro, biometria_habilitada) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, email, senha, 'google', data_atual, 0)
            )
            conn.commit()
            
            c.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
            user = c.fetchone()
            st.session_state.usuario_logado = {
                'id': user[0], 'nome': user[1], 'email': user[2]
            }
            st.success(f"Conta Google criada com sucesso! Bem-vindo, {nome}!")
        
        conn.close()
        st.rerun()
    except Exception as e:
        st.error(f"Erro no login com Google: {str(e)}")

def login_com_apple():
    """Login com Apple"""
    try:
        nomes_apple = ["Michael Chen", "Sophie Dubois", "James Wilson", "Emma Thompson", "David Kim"]
        nome = random.choice(nomes_apple)
        email = f"{nome.lower().replace(' ', '.')}{random.randint(1,999)}@icloud.com"
        senha = gerar_senha_aleatoria()
        
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        c.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        
        if user:
            st.session_state.usuario_logado = {
                'id': user[0], 'nome': user[1], 'email': user[2]
            }
            st.success(f"Bem-vindo de volta, {user[1]}!")
        else:
            data_atual = datetime.now().strftime("%d/%m/%Y")
            c.execute(
                "INSERT INTO usuarios (nome, email, senha, login_provider, data_cadastro, biometria_habilitada) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, email, senha, 'apple', data_atual, 0)
            )
            conn.commit()
            
            c.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
            user = c.fetchone()
            st.session_state.usuario_logado = {
                'id': user[0], 'nome': user[1], 'email': user[2]
            }
            st.success(f"Conta Apple criada com sucesso! Bem-vindo, {nome}!")
        
        conn.close()
        st.rerun()
    except Exception as e:
        st.error(f"Erro no login com Apple: {str(e)}")

# Função para mostrar a interface do usuário logado
def mostrar_conteudo_logado():
    """Mostra o conteúdo principal quando o usuário está logado"""
    
    # Sidebar com informações do usuário
    with st.sidebar:
        st.markdown(f"<i class='fas fa-leaf eco-icon' style='font-size: 80px; display: block; text-align: center;'></i>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: {text_color}; text-align: center;'>🌱 {st.session_state.usuario_logado['nome'].split(' ')[0]}</h2>", unsafe_allow_html=True)
        
        # Mostra provider do login
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT login_provider FROM usuarios WHERE id = ?", (st.session_state.usuario_logado['id'],))
        provider = c.fetchone()
        
        if provider and provider[0] == 'google':
            st.markdown("<p style='color: #4285F4; text-align: center;'><i class='fab fa-google'></i> Google</p>", unsafe_allow_html=True)
        elif provider and provider[0] == 'apple':
            st.markdown("<p style='color: #000000; text-align: center;'><i class='fab fa-apple'></i> Apple</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: {text_color}; text-align: center;'><i class='fas fa-envelope'></i> E-mail</p>", unsafe_allow_html=True)
        
        conn.close()
        
        st.markdown(f"<p style='color: {text_color}; text-align: center;'>🌍 Nível: EcoAtivista</p>", unsafe_allow_html=True)
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
            <p>🌍 {total_eventos} Eventos</p>
            <p>💡 {total_dicas} Dicas</p>
            <p>📍 {total_pontos} Pontos</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"<p style='color: {secondary_text}; text-align: center;'>🌱 Piracicaba - SP</p>", unsafe_allow_html=True)
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Dashboard", "📅 Eventos", "💡 Dicas", "📍 Pontos"
    ])
    
    with tab1:
        st.markdown(f"<h2 style='color: {text_color};'>🌍 Dashboard</h2>", unsafe_allow_html=True)
        
        # Métricas principais
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>15.432</div>
                <div class='stat-label'>🌳 Árvores</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>2.450</div>
                <div class='stat-label'>♻️ Toneladas</div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>87</div>
                <div class='stat-label'>🏫 Escolas</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>12.8k</div>
                <div class='stat-label'>👥 Participantes</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Próximos eventos
        st.markdown(f"<h3 style='color: {text_color};'>📅 Próximos</h3>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('ecopiracicaba.db')
        eventos = pd.read_sql_query("SELECT * FROM eventos ORDER BY data LIMIT 3", conn)
        conn.close()
        
        for _, evento in eventos.iterrows():
            st.markdown(f"""
            <div class='evento-card'>
                <div>
                    <span class='categoria-badge badge-{evento["tipo"]}'>{evento["tipo"].upper()}</span>
                    <h4 style='color: {text_color}; margin: 10px 0;'>{evento['titulo']}</h4>
                    <p><i class='fas fa-calendar'></i> {evento['data']}</p>
                    <p><i class='fas fa-map-marker-alt'></i> {evento['local']}</p>
                    <div class='progress-bar'>
                        <div class='progress-fill' style='width: {min(100, (evento["inscritos"]/max(evento["vagas"],1))*100)}%;'></div>
                    </div>
                    <small>{evento['inscritos']}/{evento['vagas'] if evento['vagas'] > 0 else '∞'}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown(f"<h2 style='color: {text_color};'>📅 Eventos 2026</h2>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('ecopiracicaba.db')
        eventos = pd.read_sql_query("SELECT * FROM eventos ORDER BY data", conn)
        conn.close()
        
        for _, evento in eventos.iterrows():
            st.markdown(f"""
            <div class='evento-card'>
                <div style='background: {icon_color}; color: white; padding: 5px 10px; border-radius: 10px; margin-bottom: 10px; display: inline-block;'>
                    {evento['data']}
                </div>
                <h4 style='color: {text_color}; margin: 5px 0;'>{evento['titulo']}</h4>
                <p><i class='fas fa-map-marker-alt'></i> {evento['local']}</p>
                <p><small>{evento['descricao'][:100]}...</small></p>
                <span class='categoria-badge badge-{evento["tipo"]}'>{evento["tipo"].upper()}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"<h2 style='color: {text_color};'>💡 Dicas Verdes</h2>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('ecopiracicaba.db')
        dicas = pd.read_sql_query("SELECT * FROM dicas ORDER BY likes DESC", conn)
        conn.close()
        
        for _, dica in dicas.iterrows():
            st.markdown(f"""
            <div class='dica-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <span class='categoria-badge' style='background: {icon_color}; color: white;'>{dica['categoria'].upper()}</span>
                    <span><i class='fas fa-heart' style='color: #ff6b6b;'></i> {dica['likes']}</span>
                </div>
                <h4 style='color: {text_color}; margin: 10px 0;'>{dica['titulo']}</h4>
                <p style='font-size: 14px;'>{dica['conteudo'][:120]}...</p>
                <small><i class='fas fa-user'></i> {dica['autor']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta</h2>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('ecopiracicaba.db')
        pontos = pd.read_sql_query("SELECT * FROM pontos_coleta ORDER BY avaliacao DESC", conn)
        conn.close()
        
        for _, ponto in pontos.iterrows():
            st.markdown(f"""
            <div class='ponto-card'>
                <h4 style='color: {text_color}; margin: 0 0 5px 0;'>{ponto['nome']}</h4>
                <p style='font-size: 13px;'><i class='fas fa-map-pin'></i> {ponto['endereco']}</p>
                <p style='font-size: 13px;'><i class='fas fa-clock'></i> {ponto['horario']}</p>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span class='categoria-badge' style='background: {icon_color}; color: white;'>{ponto['categoria'].upper()}</span>
                    <div>
                        <span style='color: gold;'>{'★' * int(ponto['avaliacao'])}</span>
                        <span>{ponto['avaliacao']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Interface principal baseada no dispositivo
if dispositivo == "mobile":
    # CSS específico para mobile
    st.markdown("""
    <style>
        .block-container {
            padding: 0.5rem !important;
            max-width: 100% !important;
        }
        .main-title {
            font-size: 2rem !important;
        }
        .sub-title {
            font-size: 1rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 10px !important;
            font-size: 12px !important;
        }
        .stat-box {
            padding: 15px !important;
        }
        .stat-number {
            font-size: 1.8rem !important;
        }
        .stat-label {
            font-size: 0.8rem !important;
        }
        .evento-card, .dica-card, .ponto-card {
            padding: 12px !important;
        }
        .stButton button {
            padding: 10px !important;
        }
        /* Ajustes para sidebar em mobile */
        .stSidebar .stMarkdown h2 {
            font-size: 1.2rem !important;
        }
        .stSidebar .stProgress {
            margin: 5px 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header mobile
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<i class='fas fa-leaf eco-icon' style='font-size: 40px;'></i>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1 style='color: {text_color}; font-size: 1.5rem; margin: 0;'>EcoPiracicaba</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {secondary_text}; font-size: 0.8rem; margin: 0;'>Sustentabilidade em ação</p>", unsafe_allow_html=True)
    
    # Botão de tema compacto
    if st.button("🌓", key="theme_mobile"):
        toggle_theme()
    
    st.markdown("---")
    
    # Estado do usuário
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if st.session_state.usuario_logado is None:
        # Login mobile
        st.markdown(f"<h3 style='color: {text_color}; text-align: center;'>🔐 Acesso Rápido</h3>", unsafe_allow_html=True)
        
        # Botões sociais
        if st.button("🌐 Google", key="google_mobile", use_container_width=True):
            login_com_google()
        if st.button("🍎 Apple", key="apple_mobile", use_container_width=True):
            login_com_apple()
        
        st.markdown(f'<div class="divider">ou</div>', unsafe_allow_html=True)
        
        # Login com e-mail
        with st.expander("📧 Login com E-mail"):
            tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
            
            with tab1:
                email = st.text_input("E-mail", key="login_email_mobile")
                senha = st.text_input("Senha", type="password", key="login_senha_mobile")
                if st.button("Entrar", key="entrar_mobile", use_container_width=True):
                    if not validar_email(email):
                        st.error("E-mail inválido!")
                    else:
                        conn = sqlite3.connect('ecopiracicaba.db')
                        c = conn.cursor()
                        c.execute("SELECT id, nome, email FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
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
                with st.form("cadastro_mobile"):
                    nome = st.text_input("Nome")
                    email = st.text_input("E-mail")
                    senha = st.text_input("Senha", type="password")
                    confirmar = st.text_input("Confirmar", type="password")
                    interesses = st.multiselect("Interesses", 
                        ["Sustentabilidade", "Reciclagem", "Eventos"])
                    
                    if st.form_submit_button("Criar conta", use_container_width=True):
                        if not nome:
                            st.error("Nome obrigatório")
                        elif not validar_email(email):
                            st.error("E-mail inválido")
                        elif senha != confirmar:
                            st.error("Senhas não coincidem")
                        elif len(senha) < 6:
                            st.error("Mínimo 6 caracteres")
                        else:
                            conn = sqlite3.connect('ecopiracicaba.db')
                            c = conn.cursor()
                            try:
                                data_atual = datetime.now().strftime("%d/%m/%Y")
                                c.execute(
                                    "INSERT INTO usuarios (nome, email, senha, interesses, data_cadastro, login_provider, biometria_habilitada) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (nome, email, senha, ",".join(interesses), data_atual, "email", 0)
                                )
                                conn.commit()
                                st.success("Conta criada! Faça login.")
                            except sqlite3.IntegrityError:
                                st.error("E-mail já existe!")
                            conn.close()
    else:
        # Usuário logado - mostra o mesmo conteúdo do desktop adaptado
        mostrar_conteudo_logado()

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
    
    # Estado do usuário
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if st.session_state.usuario_logado is None:
        # Sidebar para login
        with st.sidebar:
            st.markdown(f"<i class='fas fa-leaf eco-icon' style='font-size: 80px; display: block; text-align: center;'></i>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: {text_color}; text-align: center;'>🌱 EcoCidadão</h2>", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='color: {text_color};'>🔐 Acesso Rápido</h3>", unsafe_allow_html=True)
            
            if st.button("🌐 Continuar com Google", key="google_desktop", use_container_width=True):
                login_com_google()
            if st.button("🍎 Continuar com Apple", key="apple_desktop", use_container_width=True):
                login_com_apple()
            
            st.markdown(f'<div class="divider">ou</div>', unsafe_allow_html=True)
            
            with st.expander("📧 Login com E-mail", expanded=True):
                tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
                
                with tab1:
                    email = st.text_input("E-mail", key="login_email_desktop")
                    senha = st.text_input("Senha", type="password", key="login_senha_desktop")
                    if st.button("🌿 Entrar", use_container_width=True):
                        if not validar_email(email):
                            st.error("E-mail inválido!")
                        else:
                            conn = sqlite3.connect('ecopiracicaba.db')
                            c = conn.cursor()
                            c.execute("SELECT id, nome, email FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
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
                    with st.form("cadastro_desktop"):
                        nome = st.text_input("Nome completo")
                        email = st.text_input("E-mail")
                        senha = st.text_input("Senha", type="password")
                        confirmar_senha = st.text_input("Confirmar senha", type="password")
                        interesses = st.multiselect("Interesses", 
                            ["Sustentabilidade", "Reciclagem", "Eventos", "Voluntariado", "Compostagem"])
                        
                        if st.form_submit_button("🌱 Criar conta", use_container_width=True):
                            if not nome:
                                st.error("Nome é obrigatório!")
                            elif not validar_email(email):
                                st.error("E-mail inválido!")
                            elif senha != confirmar_senha:
                                st.error("As senhas não coincidem!")
                            elif len(senha) < 6:
                                st.error("A senha deve ter pelo menos 6 caracteres!")
                            else:
                                conn = sqlite3.connect('ecopiracicaba.db')
                                c = conn.cursor()
                                try:
                                    data_atual = datetime.now().strftime("%d/%m/%Y")
                                    c.execute(
                                        "INSERT INTO usuarios (nome, email, senha, interesses, data_cadastro, login_provider, biometria_habilitada) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                        (nome, email, senha, ",".join(interesses), data_atual, "email", 0)
                                    )
                                    conn.commit()
                                    st.success("Conta criada! Faça login.")
                                except sqlite3.IntegrityError:
                                    st.error("E-mail já existe!")
                                conn.close()
            
            st.markdown("---")
            st.markdown(f"<p style='color: {secondary_text}; text-align: center;'>🌱 Piracicaba - SP</p>", unsafe_allow_html=True)
        
        # Página de boas-vindas
        st.markdown(f"""
        <div style='text-align: center; padding: 50px; color: {text_color};'>
            <i class="fas fa-seedling" style='font-size: 80px; color: {icon_color};'></i>
            <h1>Bem-vindo ao EcoPiracicaba</h1>
            <p style='font-size: 1.2rem;'>Use sua conta Google, Apple ou e-mail para acessar</p>
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
        # Usuário logado no desktop
        mostrar_conteudo_logado()
