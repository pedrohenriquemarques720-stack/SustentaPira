import streamlit as st
import sqlite3
from datetime import datetime
import re
import hashlib
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

# ========== BANCO DE DADOS ==========

def init_database():
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Tabela única de usuários
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
    
    # Inserir usuários de teste
    usuarios_teste = [
        ("João Silva", "joao@email.com", "123"),
        ("Maria Santos", "maria@email.com", "123"),
        ("Pedro Oliveira", "pedro@email.com", "123")
    ]
    
    for nome, email, senha in usuarios_teste:
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO usuarios (nome, email, senha, pontos, desafios, data_cadastro) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, email, senha, random.randint(100, 500), random.randint(1, 5), datetime.now().strftime("%d/%m/%Y"))
            )
    
    conn.commit()
    conn.close()

# Inicializar banco
init_database()

# ========== DADOS DOS DESAFIOS ==========

DESAFIOS = [
    {"id": 1, "titulo": "♻️ Reciclar 10kg", "descricao": "Recicle 10kg de materiais recicláveis", "pontos": 200, "icone": "♻️"},
    {"id": 2, "titulo": "📅 Participar de Evento", "descricao": "Participe de 1 evento ambiental", "pontos": 150, "icone": "📅"},
    {"id": 3, "titulo": "🌳 Plantar Árvore", "descricao": "Plante 1 árvore nativa", "pontos": 300, "icone": "🌳"},
    {"id": 4, "titulo": "🔋 Descartar Pilhas", "descricao": "Descarte 5 pilhas", "pontos": 100, "icone": "🔋"},
    {"id": 5, "titulo": "💧 Economizar Água", "descricao": "Reduza consumo em 20%", "pontos": 120, "icone": "💧"}
]

PREMIOS = [
    {"nome": "🥉 Bronze", "min": 3, "pontos": 100, "cor": "#cd7f32"},
    {"nome": "🥈 Prata", "min": 5, "pontos": 250, "cor": "#c0c0c0"},
    {"nome": "🥇 Ouro", "min": 7, "pontos": 500, "cor": "#ffd700"}
]

# ========== FUNÇÕES ==========

def get_nivel(pontos):
    if pontos < 100:
        return "🌱 Iniciante"
    elif pontos < 300:
        return "🌿 Amigo"
    elif pontos < 600:
        return "🍃 Guardião"
    else:
        return "🌳 Mestre"

def get_user_data(user_id):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT nome, pontos, desafios FROM usuarios WHERE id = ?", (user_id,))
    data = c.fetchone()
    conn.close()
    return data

def completar_desafio(usuario_id, pontos_ganhos):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT pontos, desafios FROM usuarios WHERE id = ?", (usuario_id,))
    result = c.fetchone()
    
    if result:
        pontos_atuais, desafios_atuais = result
        novos_pontos = pontos_atuais + pontos_ganhos
        novos_desafios = desafios_atuais + 1
        
        c.execute(
            "UPDATE usuarios SET pontos = ?, desafios = ? WHERE id = ?",
            (novos_pontos, novos_desafios, usuario_id)
        )
        conn.commit()
        conn.close()
        return novos_desafios, novos_pontos
    
    conn.close()
    return 0, 0

def get_ranking():
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT nome, pontos, desafios FROM usuarios ORDER BY pontos DESC LIMIT 10")
    ranking = c.fetchall()
    conn.close()
    return ranking

# ========== CORES DO TEMA ==========

tema = get_theme()

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

# ========== CSS ==========

st.markdown(f"""
<style>
    .stApp {{ background: {bg}; }}
    .stMarkdown, p, h1, h2, h3, h4 {{ color: {text} !important; }}
    .stButton button {{ background: {icon}; color: white; border: none; border-radius: 50px; }}
    .card {{
        background: {card};
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {border};
        margin-bottom: 10px;
    }}
    .stat-box {{
        background: {card};
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid {border};
    }}
    .premio-card {{
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"<h1 style='text-align: center;'>🌿 EcoPiracicaba 2026</h1>", unsafe_allow_html=True)
with col3:
    if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
        toggle_theme()

# ========== LOGIN / CADASTRO ==========

if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
    st.session_state.usuario_nome = None
    st.session_state.usuario_pontos = 0
    st.session_state.usuario_desafios = 0

if st.session_state.usuario_id is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Login
        with st.form("login_form"):
            st.markdown("### 🔐 Login")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            login_btn = st.form_submit_button("Entrar", use_container_width=True)
            
            if login_btn:
                if validar_email(email):
                    conn = sqlite3.connect('ecopiracicaba.db')
                    c = conn.cursor()
                    c.execute("SELECT id, nome, pontos, desafios FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
                    user = c.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.usuario_id = user[0]
                        st.session_state.usuario_nome = user[1]
                        st.session_state.usuario_pontos = user[2]
                        st.session_state.usuario_desafios = user[3]
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos")
        
        st.markdown("---")
        
        # Cadastro
        with st.form("cadastro_form"):
            st.markdown("### 🆕 Cadastro")
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            cadastro_btn = st.form_submit_button("Criar conta", use_container_width=True)
            
            if cadastro_btn:
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
                    st.error("Preencha todos os campos corretamente")

else:
    # ========== USUÁRIO LOGADO ==========
    
    # Sidebar
    with st.sidebar:
        nivel = get_nivel(st.session_state.usuario_pontos)
        
        st.markdown(f"""
        <div class='card' style='text-align: center;'>
            <h3>{st.session_state.usuario_nome}</h3>
            <h4 style='color: {icon};'>{nivel}</h4>
            <h2 style='color: {icon};'>{st.session_state.usuario_pontos} pts</h2>
            <p>🎯 {st.session_state.usuario_desafios} desafios</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_id = None
            st.session_state.usuario_nome = None
            st.session_state.usuario_pontos = 0
            st.session_state.usuario_desafios = 0
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Ranking")
        ranking = get_ranking()
        for i, (nome, pontos, desafios) in enumerate(ranking[:5]):
            medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}º"
            st.markdown(f"""
            <div style='padding: 5px; border-bottom: 1px solid {border};'>
                {medalha} {nome}: <strong style='color: {icon};'>{pontos} pts</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== TABS ==========
    
    tab1, tab2, tab3 = st.tabs(["🎯 Desafios", "👤 Perfil", "ℹ️ Informações"])
    
    with tab1:
        st.markdown(f"<h2>🎯 Desafios Semanais</h2>", unsafe_allow_html=True)
        
        # Progresso
        st.markdown(f"""
        <div class='card' style='text-align: center;'>
            <h3>Seu Progresso</h3>
            <div style='display: flex; justify-content: space-around; font-size: 20px;'>
                <div><span style='font-size: 36px; color: {icon};'>{st.session_state.usuario_desafios}</span><br>completados</div>
                <div><span style='font-size: 36px; color: gold;'>🏆</span><br>{st.session_state.usuario_pontos} pts</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prêmios
        st.markdown(f"<h3>🎁 Prêmios</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, premio in enumerate(PREMIOS):
            with cols[i]:
                disponivel = st.session_state.usuario_desafios >= premio["min"]
                st.markdown(f"""
                <div class='card' style='text-align: center; border: 2px solid {premio["cor"] if disponivel else border}; opacity: {1 if disponivel else 0.5};'>
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
                        st.session_state.usuario_id, 
                        desafio['pontos']
                    )
                    
                    # Atualizar sessão
                    st.session_state.usuario_desafios = novos_desafios
                    st.session_state.usuario_pontos = novos_pontos
                    
                    # Verificar prêmios
                    for premio in PREMIOS:
                        if novos_desafios == premio["min"]:
                            _, novos_pontos = completar_desafio(
                                st.session_state.usuario_id, 
                                premio["pontos"]
                            )
                            st.session_state.usuario_pontos = novos_pontos
                            st.balloons()
                            st.success(f"🏆 PARABÉNS! Você ganhou {premio['nome']}! +{premio['pontos']} pontos!")
                    
                    st.rerun()
    
    with tab2:
        st.markdown(f"<h2>👤 Meu Perfil</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h2 style='color: {icon};'>{get_nivel(st.session_state.usuario_pontos)}</h2>
                <h1 style='color: {icon}; font-size: 48px;'>{st.session_state.usuario_pontos}</h1>
                <p>pontos totais</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card' style='text-align: center;'>
                <h3>🎯 Desafios</h3>
                <h1 style='color: {icon}; font-size: 48px;'>{st.session_state.usuario_desafios}</h1>
                <p>completados</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Estatísticas
        st.markdown(f"<h3>📊 Estatísticas</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='stat-box'>
                <h4>📅 Eventos</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-box'>
                <h4>💡 Dicas</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='stat-box'>
                <h4>📍 Visitas</h4>
                <h2 style='color: {icon};'>0</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"<h2>ℹ️ EcoPiracicaba</h2>", unsafe_allow_html=True)
        
        # Eventos
        st.markdown(f"""
        <div class='card'>
            <h3>📅 Eventos 2026</h3>
            <p>🌱 Feira de Sustentabilidade - 15/03 - Engenho Central</p>
            <p>♻️ Workshop de Reciclagem - 22/03 - SENAI</p>
            <p>🌊 Mutirão Rio Piracicaba - 05/04 - Rua do Porto</p>
            <p>🌳 Plantio de Árvores - 05/06 - Parque Ecológico</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pontos de coleta
        st.markdown(f"""
        <div class='card'>
            <h3>📍 Pontos de Coleta</h3>
            <p><strong>Ecoponto Centro</strong> - Av. Rui Barbosa, 800</p>
            <p><strong>Shopping Piracicaba</strong> - Av. Limeira, 700 (Pilhas)</p>
            <p><strong>Coopervidros</strong> - R. Treze de Maio, 300</p>
            <p><strong>CDI Eletrônicos</strong> - R. do Porto, 234</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Dicas
        st.markdown(f"""
        <div class='card'>
            <h3>💡 Dicas Ambientais</h3>
            <p>🌱 <strong>Compostagem:</strong> 50% do lixo doméstico pode ser compostado</p>
            <p>💧 <strong>Água:</strong> Banho de 15 min gasta 135 litros</p>
            <p>🔋 <strong>Pilhas:</strong> 1 pilha contamina 20 mil litros de água</p>
            <p>🌳 <strong>Árvores:</strong> 1 árvore absorve 150kg de CO2 por ano</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sobre
        st.markdown(f"""
        <div class='card'>
            <h3>🌿 Sobre</h3>
            <p>EcoPiracicaba é um aplicativo de sustentabilidade que ajuda você a:</p>
            <p>• Completar desafios ambientais</p>
            <p>• Ganhar pontos e subir no ranking</p>
            <p>• Encontrar pontos de coleta seletiva</p>
            <p>• Participar de eventos sustentáveis</p>
            <p>📍 Piracicaba - SP</p>
        </div>
        """, unsafe_allow_html=True)
