import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
        # Verifica se há preferência salva na sessão
        if 'theme' in st.session_state:
            return st.session_state.theme
        
        # Tenta detectar pelo CSS do navegador
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
    
    # Tabela de estatísticas ambientais
    c.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            valor TEXT,
            unidade TEXT,
            data_atualizacao TEXT,
            fonte TEXT
        )
    ''')
    
    # Inserir dados iniciais
    # Usuário admin
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses) VALUES (?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", datetime.now().strftime("%d/%m/%Y"), "sustentabilidade,reciclagem")
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
            ("♻️ Economia Circular", "Palestra sobre reuso e economia circular nas empresas", "20/06/2026", "15:00", "ESALQ/USP", "Prof. Ricardo Mendes", "palestra", 150, 0, "🔄", "ESALQ", "(19) 3447-8500"),
            ("💡 Energia Solar", "Workshop de energia solar residencial e comunitária", "10/07/2026", "14:00", "SENAI", "Eng. Sofia Santos", "workshop", 40, 0, "☀️", "SENAI", "(19) 3412-5000"),
            ("🚴 Ciclo Turismo", "Passeio ecológico de bike pela cidade", "25/07/2026", "07:00", "Saída do Engenho", "Cicloativistas Piracicaba", "passeio", 100, 0, "🚲", "Ciclovida", "(19) 99887-6543"),
            ("🌾 Agricultura Urbana", "Oficina de hortas urbanas e permacultura", "08/08/2026", "09:00", "Horta Comunitária Vila Sônia", "Ana Agricultora", "oficina", 60, 0, "🥕", "Hortas Urbanas", "(19) 99654-3210"),
            ("💧 Semana da Água", "Palestras e atividades sobre preservação da água", "15/08/2026", "09:00", "Teatro Municipal", "Comitê de Bacias", "evento", 400, 0, "💧", "Comitê PCJ", "(19) 3437-2000"),
            ("🐝 Dia das Abelhas", "Palestra sobre a importância das abelhas", "29/08/2026", "14:00", "ESALQ", "Dra. Maria Apicultora", "palestra", 80, 0, "🐝", "USP", "(19) 3447-8500"),
            ("🌿 Feira de Orgânicos", "Feira especial de produtos orgânicos", "12/09/2026", "08:00", "Mercado Municipal", "Associação Orgânicos", "feira", 0, 0, "🥬", "Mercadão", "(19) 3434-7890"),
            ("🚲 Bike na Rua", "Dia sem carro com passeio ciclístico", "22/09/2026", "08:00", "Largo dos Pescadores", "Prefeitura", "evento", 500, 0, "🚲", "Secretaria de Mobilidade", "(19) 3403-1200")
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
            ("🌱 Compostagem Doméstica", "Você sabia que 50% do lixo doméstico pode ser compostado? Aprenda a fazer sua própria composteira com baldes e minhocas californianas. Em 3 meses você terá adubo de alta qualidade para suas plantas.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe EcoPiracicaba"),
            ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros de água. Reduza para 5 minutos e economize 90 litros por banho! Isso representa 2.700 litros por mês.", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas e Baterias", "Nunca descarte pilhas no lixo comum. Leve a pontos de coleta específicos. Uma pilha pode contaminar 20 mil litros de água por até 50 anos.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Plante uma Árvore", "Uma árvore adulta absorve até 150kg de CO2 por ano. Plante árvores nativas da região de Piracicaba como ipê, jatobá e pitanga.", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica"),
            ("🛍️ Sacolas Retornáveis", "Uma sacola plástica leva 400 anos para se decompor. Use sempre sacolas retornáveis nas compras. O Brasil consome 1,5 milhão de sacolas por hora!", "plástico", datetime.now().strftime("%d/%m/%Y"), 0, "WWF"),
            ("🚗 Carona Solidária", "Compartilhe carro com colegas de trabalho. Reduz emissões, congestionamento e você ainda economiza até 40% com combustível.", "mobilidade", datetime.now().strftime("%d/%m/%Y"), 0, "Instituto Clima"),
            ("🥗 Alimentação Orgânica", "Alimentos orgânicos são mais saudáveis e não contaminam o solo com agrotóxicos. Em Piracicaba, feiras orgânicas acontecem aos sábados na ESALQ.", "alimentação", datetime.now().strftime("%d/%m/%Y"), 0, "Feira Orgânica"),
            ("♻️ Separação do Lixo", "Separe sempre recicláveis: papel limpo, plástico, vidro e metal. Lave as embalagens antes de descartar. A reciclagem de uma tonelada de papel salva 20 árvores.", "reciclagem", datetime.now().strftime("%d/%m/%Y"), 0, "Cooperativa Recicladores"),
            ("☀️ Energia Solar", "A energia solar já é a fonte mais barata do Brasil. Uma placa solar de 330W evita a emissão de 4,5 toneladas de CO2 em 25 anos.", "energia", datetime.now().strftime("%d/%m/%Y"), 0, "ABSOLAR"),
            ("🐝 Proteja as Abelhas", "As abelhas são responsáveis por 80% da polinização das plantas. Evite inseticidas e plante flores nativas para ajudar esses insetos essenciais.", "biodiversidade", datetime.now().strftime("%d/%m/%Y"), 0, "Bee Or not to be"),
            ("🌊 Rio Piracicaba", "O Rio Piracicaba abastece 95% da cidade. Nunca jogue lixo nos córregos e denuncie despejos irregulares para a Cetesb (0800-113560).", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Cetesb"),
            ("🥕 Desperdício Zero", "Aproveite cascas e talos de alimentos para fazer receitas nutritivas. O brasileiro desperdiça 40 mil toneladas de comida por dia.", "alimentação", datetime.now().strftime("%d/%m/%Y"), 0, "FAO")
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
            ("Coopervidros", "R. Treze de Maio, 300 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", -22.731, -47.651, 4.2, "Cooperativa especializada em reciclagem de vidros"),
            ("CDI Eletrônicos", "R. do Porto, 234 - Centro", "eletronicos", "Seg-Sex 9h-18h, Sáb 9h-12h", "(19) 3433-5678", -22.722, -47.646, 4.7, "Centro de Descarte de Eletrônicos - computadores, celulares e pilhas"),
            ("Ecoponto Paulicéia", "R. Javari, 150 - Paulicéia", "geral", "Ter-Sáb 8h-16h", "(19) 3403-2200", -22.710, -47.670, 4.3, "Ecoponto completo com coleta de óleo e recicláveis"),
            ("Drogaria São Paulo", "Av. Limeira, 900 - Centro", "medicamentos", "24 horas", "(19) 3432-7800", -22.720, -47.640, 4.0, "Descarte de medicamentos vencidos e pilhas"),
            ("Unimed Sede", "R. Voluntários, 450 - Centro", "pilhas", "Seg-Sex 7h-19h", "(19) 3432-9000", -22.725, -47.649, 4.6, "Coleta de pilhas e baterias na recepção"),
            ("Esalq/USP", "Av. Pádua Dias, 11 - Agronomia", "eletronicos", "Seg-Sex 8h-17h", "(19) 3447-8500", -22.710, -47.630, 4.9, "Campus da ESALQ com pontos de coleta de eletrônicos"),
            ("Supermercado Pague Menos", "R. Campos Salles, 500 - Centro", "oleo", "Seg-Sáb 8h-21h", "(19) 3434-1234", -22.728, -47.652, 4.4, "Coleta de óleo de cozinha usado"),
            ("Ferro Velho Central", "Av. São Paulo, 320 - Jardim Elite", "metais", "Seg-Sex 8h-17h", "(19) 3422-5678", -22.715, -47.660, 4.1, "Compra e recebimento de metais e sucata"),
            ("Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "organicos", "Seg-Sex 8h-16h", "(19) 3434-5678", -22.730, -47.655, 4.3, "Recebimento de podas e resíduos orgânicos"),
            ("Associação Recicladores", "R. dos Operários, 500 - Centro", "geral", "Seg-Sex 8h-17h", "(19) 3423-7890", -22.726, -47.645, 4.7, "Cooperativa de catadores, recebe todos os recicláveis")
        ]
        for p in pontos:
            c.execute(
                """INSERT INTO pontos_coleta 
                   (nome, endereco, categoria, horario, telefone, latitude, longitude, avaliacao, descricao) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                p
            )
    
    # Estatísticas ambientais
    c.execute("SELECT * FROM estatisticas")
    if not c.fetchone():
        stats = [
            ("Árvores plantadas em 2025", "15.432", "unidades", "2025", "Secretaria do Meio Ambiente"),
            ("CO₂ evitado (toneladas)", "2.450", "toneladas", "2025", "Inventário Municipal"),
            ("Resíduos reciclados", "8.321", "toneladas", "2025", "Cooperativas"),
            ("Participantes em eventos", "12.847", "pessoas", "2025", "Secretaria de Eventos"),
            ("Escolas participantes", "87", "unidades", "2025", "Secretaria de Educação"),
            ("Pontos de coleta", "45", "unidades", "2026", "Prefeitura"),
            ("Qualidade do ar", "Boa", "índice", "2026", "Cetesb"),
            ("Qualidade da água do rio", "Regular", "índice", "2026", "Comitê PCJ")
        ]
        for s in stats:
            c.execute(
                "INSERT INTO estatisticas (titulo, valor, unidade, data_atualizacao, fonte) VALUES (?, ?, ?, ?, ?)",
                s
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
    
    /* Cards personalizados */
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
""", unsafe_allow_html=True)

# Interface mobile ou desktop
if dispositivo == "mobile":
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
    
    # Interface mobile simplificada (código mobile mantido aqui)
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #f0fff5;
                font-family: 'Segoe UI', sans-serif;
            }
            .mobile-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #0f5c3f;
                font-size: 28px;
            }
        </style>
    </head>
    <body>
        <div class="mobile-container">
            <div class="header">
                <i class="fas fa-leaf" style="font-size: 50px; color: #0f5c3f;"></i>
                <h1>EcoPiracicaba</h1>
                <p>Versão Mobile</p>
            </div>
        </div>
    </body>
    </html>
    """, height=800)

else:
    # ========== INTERFACE DESKTOP COMPLETA ==========
    
    # Header com botão de tema
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148460.png", width=80)
    with col2:
        st.markdown(f'<h1 class="main-title">🌿 EcoPiracicaba 2026</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Sustentabilidade em ação na cidade de Piracicaba</p>', unsafe_allow_html=True)
    with col3:
        if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
            toggle_theme()
    
    # Sidebar com informações do usuário
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148460.png", width=120)
        st.markdown(f"<h2 style='color: {text_color};'>🌱 EcoCidadão</h2>", unsafe_allow_html=True)
        
        # Login/Cadastro
        if 'usuario_logado' not in st.session_state:
            st.session_state.usuario_logado = None
        
        if st.session_state.usuario_logado is None:
            with st.expander("🔐 Login / Cadastro", expanded=True):
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
                    with st.form("cadastro"):
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
                                    "INSERT INTO usuarios (nome, email, senha, interesses, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                                    (nome, email, senha, ",".join(interesses), datetime.now().strftime("%d/%m/%Y"))
                                )
                                conn.commit()
                                st.success("Conta criada! Faça login.")
                            except:
                                st.error("E-mail já existe")
                            conn.close()
        else:
            st.success(f"🌿 Olá, {st.session_state.usuario_logado['nome'].split(' ')[0]}!")
            st.markdown(f"<p style='color: {text_color};'>🌍 Nível: EcoAtivista</p>", unsafe_allow_html=True)
            st.progress(0.65, text="65% para próximo nível")
            if st.button("Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.rerun()
        
        st.markdown("---")
        
        # Estatísticas rápidas
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM eventos WHERE data >= '2026'")
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
        st.markdown(f"<p style='color: {secondary_text};'>🌱 Piracicaba - SP</p>", unsafe_allow_html=True)
    
    # Conteúdo principal
    if st.session_state.usuario_logado is None:
        # Página de boas-vindas
        st.markdown(f"""
        <div style='text-align: center; padding: 50px; color: {text_color};'>
            <i class="fas fa-seedling" style='font-size: 80px; color: {icon_color};'></i>
            <h1>Bem-vindo ao EcoPiracicaba</h1>
            <p style='font-size: 1.2rem;'>Faça login ou cadastre-se para acessar todas as funcionalidades</p>
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🌍 Dashboard", "📅 Eventos 2026", "💡 Dicas Verdes", "📍 Pontos de Coleta", "📊 Estatísticas"
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
                # Gráfico de eventos por tipo
                tipos = ['Palestras', 'Workshops', 'Mutirões', 'Feiras', 'Campanhas']
                quantidades = [25, 18, 12, 8, 15]
                fig = px.pie(values=quantidades, names=tipos, title="Eventos por Tipo em 2026",
                            color_discrete_sequence=['#0f5c3f', '#1a8c5f', '#2ecc71', '#27ae60', '#229954'])
                fig.update_layout(template="plotly_white" if tema == "light" else "plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Evolução de participantes
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
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                mes_filter = st.selectbox("Mês", ["Todos", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro"])
            with col2:
                tipo_filter = st.selectbox("Tipo", ["Todos", "palestra", "workshop", "mutirão", "feira", "campanha", "passeio"])
            with col3:
                busca = st.text_input("🔍 Buscar evento", placeholder="Digite palavras-chave")
            
            conn = sqlite3.connect('ecopiracicaba.db')
            query = "SELECT * FROM eventos WHERE 1=1"
            if mes_filter != "Todos":
                query += f" AND data LIKE '%{mes_filter}%'"
            if tipo_filter != "Todos":
                query += f" AND tipo = '{tipo_filter}'"
            eventos = pd.read_sql_query(query + " ORDER BY data", conn)
            conn.close()
            
            if busca:
                eventos = eventos[eventos['titulo'].str.contains(busca, case=False) | 
                                 eventos['descricao'].str.contains(busca, case=False)]
            
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
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
                                <div style='width: 60%;'>
                                    <div class='progress-bar'>
                                        <div class='progress-fill' style='width: {min(100, (evento["inscritos"]/max(evento["vagas"],1))*100)}%;'></div>
                                    </div>
                                    <small>{evento['inscritos']} de {evento['vagas']} vagas</small>
                                </div>
                                <button class='eco-button'>Inscrever-se</button>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown(f"<h2 style='color: {text_color};'>💡 Dicas para um Planeta Mais Verde</h2>", unsafe_allow_html=True)
            
            # Categorias
            categorias = ["Todos", "resíduos", "água", "energia", "natureza", "reciclagem", "alimentação", "mobilidade", "biodiversidade"]
            cat_filter = st.selectbox("Filtrar por categoria", categorias)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            if cat_filter != "Todos":
                dicas = pd.read_sql_query(f"SELECT * FROM dicas WHERE categoria = '{cat_filter}'", conn)
            else:
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
                            <button class='eco-button' style='padding: 5px 15px;'>Curtir</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta Seletiva</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # Mapa simples (simulado)
                st.markdown(f"""
                <div class='eco-card' style='height: 400px; display: flex; align-items: center; justify-content: center;'>
                    <i class='fas fa-map-marked-alt' style='font-size: 100px; color: {icon_color};'></i>
                    <p style='margin-left: 20px;'>Mapa interativo dos 45 pontos de coleta em Piracicaba</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                categoria_map = st.selectbox("Categoria", ["Todos", "geral", "pilhas", "vidros", "eletronicos", "oleo", "organicos", "metais"])
                avaliacao_min = st.slider("Avaliação mínima", 0.0, 5.0, 3.0, 0.5)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            query = "SELECT * FROM pontos_coleta WHERE avaliacao >= ?"
            params = [avaliacao_min]
            if categoria_map != "Todos":
                query += " AND categoria = ?"
                params.append(categoria_map)
            pontos = pd.read_sql_query(query, conn, params=params)
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
        
        with tab5:
            st.markdown(f"<h2 style='color: {text_color};'>📊 Estatísticas Ambientais de Piracicaba</h2>", unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecopiracicaba.db')
            stats = pd.read_sql_query("SELECT * FROM estatisticas", conn)
            conn.close()
            
            # Gráfico de barras
            fig = go.Figure(data=[
                go.Bar(name='Valores', x=stats['titulo'], y=[float(s.split()[0]) if s.split()[0].replace('.','').isdigit() else 0 for s in stats['valor']],
                      marker_color=icon_color)
            ])
            fig.update_layout(title="Indicadores Ambientais",
                            xaxis_title="Indicador", yaxis_title="Valor",
                            template="plotly_white" if tema == "light" else "plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de estatísticas
            st.markdown(f"<h3 style='color: {text_color};'>Detalhamento</h3>", unsafe_allow_html=True)
            for _, stat in stats.iterrows():
                st.markdown(f"""
                <div class='eco-card' style='padding: 15px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='color: {text_color}; margin: 0;'>{stat['titulo']}</h4>
                            <small>Fonte: {stat['fonte']} · Atualizado em {stat['data_atualizacao']}</small>
                        </div>
                        <div style='font-size: 28px; font-weight: bold; color: {icon_color};'>
                            {stat['valor']} {stat['unidade']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
