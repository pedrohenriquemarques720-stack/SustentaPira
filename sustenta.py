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

# ========== FUNÇÕES DE GAMIFICAÇÃO (DEFINIDAS PRIMEIRO) ==========

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

# ========== SISTEMA DE GAMIFICAÇÃO ==========

# Níveis e pontuação
NIVEIS = {
    "🌱 EcoIniciante": 0,
    "🌿 EcoAmigo": 100,
    "🍃 EcoGuardião": 500,
    "🌳 EcoMestre": 1000,
    "🏆 EcoHerói": 5000
}

# Tipos de conquistas
CONQUISTAS = {
    "primeiro_login": {"nome": "Primeiro Passo", "pontos": 10, "icone": "👋"},
    "primeiro_evento": {"nome": "Evento Estreia", "pontos": 50, "icone": "📅"},
    "cinco_eventos": {"nome": "Participante Ativo", "pontos": 100, "icone": "🎫"},
    "dez_eventos": {"nome": "Veterano Verde", "pontos": 200, "icone": "🏅"},
    "primeira_dica": {"nome": "Aprendiz", "pontos": 5, "icone": "💡"},
    "cinco_dicas": {"nome": "Curioso", "pontos": 25, "icone": "🔍"},
    "dez_dicas": {"nome": "Sábio Ambiental", "pontos": 50, "icone": "📚"},
    "primeiro_ponto": {"nome": "Explorador", "pontos": 15, "icone": "🗺️"},
    "cinco_pontos": {"nome": "Colecionador", "pontos": 75, "icone": "🎯"},
    "convidar_amigo": {"nome": "Multiplicador", "pontos": 100, "icone": "👥"},
    "reciclar_10kg": {"nome": "Reciclador Bronze", "pontos": 50, "icone": "♻️"},
    "reciclar_50kg": {"nome": "Reciclador Prata", "pontos": 200, "icone": "🥈"},
    "reciclar_100kg": {"nome": "Reciclador Ouro", "pontos": 500, "icone": "🥇"},
    "plantar_arvore": {"nome": "Guardião da Floresta", "pontos": 100, "icone": "🌳"},
}

# Desafios semanais
DESAFIOS_LISTA = [
    {
        "id": 1,
        "titulo": "🌱 Coletor de Pilhas",
        "descricao": "Descarte 5 pilhas ou baterias em pontos de coleta",
        "pontos": 100,
        "icone": "🔋",
        "tipo": "pilhas"
    },
    {
        "id": 2,
        "titulo": "♻️ Mestre da Reciclagem",
        "descricao": "Separe corretamente 10kg de recicláveis",
        "pontos": 150,
        "icone": "🔄",
        "tipo": "reciclagem"
    },
    {
        "id": 3,
        "titulo": "📅 Participante de Eventos",
        "descricao": "Participe de 2 eventos ambientais",
        "pontos": 200,
        "icone": "🎉",
        "tipo": "eventos"
    },
    {
        "id": 4,
        "titulo": "🌳 Plantador de Árvores",
        "descricao": "Plante 1 árvore nativa",
        "pontos": 300,
        "icone": "🌲",
        "tipo": "plantio"
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
            avatar TEXT,
            cidade TEXT DEFAULT 'Piracicaba',
            interesses TEXT,
            login_provider TEXT DEFAULT 'email',
            provider_id TEXT,
            data_cadastro TEXT,
            ultimo_acesso TEXT
        )
    ''')
    
    # Tabela de pontos/conquistas
    c.execute('''
        CREATE TABLE IF NOT EXISTS conquistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tipo TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT,
            icone TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de progresso do usuário
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
    
    # Tabela: desafios (catálogo de desafios)
    c.execute('''
        CREATE TABLE IF NOT EXISTS desafios (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            descricao TEXT,
            pontos INTEGER,
            icone TEXT,
            tipo TEXT
        )
    ''')
    
    # Tabela de desafios ativos do usuário
    c.execute('''
        CREATE TABLE IF NOT EXISTS desafios_ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            desafio_id INTEGER,
            progresso INTEGER DEFAULT 0,
            concluido INTEGER DEFAULT 0,
            data_inicio TEXT,
            data_conclusao TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (desafio_id) REFERENCES desafios (id)
        )
    ''')
    
    # Tabela de badges
    c.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            badge_nome TEXT,
            badge_icone TEXT,
            data_obtencao TEXT,
            UNIQUE(usuario_id, badge_nome),
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
    
    # Tabela de convites
    c.execute('''
        CREATE TABLE IF NOT EXISTS convites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            codigo TEXT UNIQUE,
            usado INTEGER DEFAULT 0,
            usado_por INTEGER,
            data_criacao TEXT,
            data_uso TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (usado_por) REFERENCES usuarios (id)
        )
    ''')
    
    # Inserir dados iniciais de desafios se não existirem
    c.execute("SELECT COUNT(*) FROM desafios")
    if c.fetchone()[0] == 0:
        for desafio in DESAFIOS_LISTA:
            c.execute(
                "INSERT INTO desafios (id, titulo, descricao, pontos, icone, tipo) VALUES (?, ?, ?, ?, ?, ?)",
                (desafio["id"], desafio["titulo"], desafio["descricao"], desafio["pontos"], desafio["icone"], desafio["tipo"])
            )
    
    # Inserir usuário admin
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses, login_provider) VALUES (?, ?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", datetime.now().strftime("%d/%m/%Y"), "sustentabilidade,reciclagem", "email")
        )
    
    # Inserir alguns usuários de exemplo
    usuarios_exemplo = [
        ("João Silva", "joao@email.com", "123", "sustentabilidade,reciclagem"),
        ("Maria Santos", "maria@email.com", "123", "eventos,voluntariado"),
        ("Pedro Oliveira", "pedro@email.com", "123", "compostagem,natureza")
    ]
    
    for nome, email, senha, interesses in usuarios_exemplo:
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses, login_provider) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, email, senha, datetime.now().strftime("%d/%m/%Y"), interesses, "email")
            )
            
            # Pegar o ID do usuário recém-criado
            c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            user_id = c.fetchone()[0]
            
            # Inicializar progresso com alguns pontos aleatórios
            pontos_iniciais = random.randint(50, 300)
            nivel = get_nivel(pontos_iniciais)  # AGORA A FUNÇÃO JÁ FOI DEFINIDA
            c.execute(
                "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade, desafios_completados) VALUES (?, ?, ?, ?, ?)",
                (user_id, pontos_iniciais, nivel, datetime.now().strftime("%d/%m/%Y %H:%M"), random.randint(0, 2))
            )
    
    # Eventos 2026
    c.execute("SELECT * FROM eventos")
    if not c.fetchone():
        eventos = [
            ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos e artesanato sustentável", "15/03/2026", "09:00", "Engenho Central", "Secretaria do Meio Ambiente", "feira", 1000, 0, "🌿", "Prefeitura de Piracicaba", "(19) 3403-1100"),
            ("♻️ Workshop de Reciclagem", "Aprenda técnicas de reciclagem em casa", "22/03/2026", "14:00", "SENAI Piracicaba", "Joana Silva", "workshop", 50, 0, "🔄", "SENAI", "(19) 3412-5000"),
            ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio", "05/04/2026", "08:00", "Rua do Porto", "Movimento Rio Vivo", "mutirão", 200, 0, "💧", "SOS Rio Piracicaba", "(19) 99765-4321"),
            ("🌿 Palestra: Compostagem", "Como fazer compostagem doméstica", "12/04/2026", "10:00", "Horto Municipal", "Dr. Carlos", "palestra", 100, 0, "🌱", "Horto Municipal", "(19) 3434-5678"),
            ("🌍 Dia da Terra", "Celebração com atividades ambientais", "22/04/2026", "09:00", "Parque da Rua do Porto", "Coletivo Ambiental", "evento", 2000, 0, "🌎", "ONG Planeta Verde", "(19) 99876-5432"),
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
            ("🌱 Compostagem Doméstica", "50% do lixo doméstico pode ser compostado! Faça sua própria composteira.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe EcoPiracicaba"),
            ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros. Reduza para 5 minutos e economize 90 litros!", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas e Baterias", "Nunca descarte pilhas no lixo comum. Uma pilha contamina 20 mil litros de água.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Plante uma Árvore", "Uma árvore adulta absorve 150kg de CO2 por ano.", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica")
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
            ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", -22.724, -47.648, 4.5, "Recebe todos os tipos de recicláveis"),
            ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", -22.718, -47.642, 4.8, "Ponto de coleta de pilhas e baterias"),
            ("Coopervidros", "R. Treze de Maio, 300 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", -22.731, -47.651, 4.2, "Cooperativa de reciclagem de vidros")
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

# ========== FUNÇÕES DE GAMIFICAÇÃO (CONTINUAÇÃO) ==========

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

def adicionar_pontos(usuario_id, pontos_extra, descricao="", icone="✨"):
    """Adiciona pontos ao usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Registrar conquista
    c.execute(
        "INSERT INTO conquistas (usuario_id, tipo, pontos, data, descricao, icone) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, "desafio", pontos_extra, data_atual, descricao, icone)
    )
    
    # Atualizar pontos no progresso
    c.execute("SELECT total_pontos, desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        desafios_atuais = resultado[1] if len(resultado) > 1 else 0
        novos_pontos = pontos_atuais + pontos_extra
        novo_nivel = get_nivel(novos_pontos)
        novos_desafios = desafios_atuais + 1
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ?, desafios_completados = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, data_atual, novos_desafios, usuario_id)
        )
    
    conn.commit()
    conn.close()
    
    return True

def completar_desafio(usuario_id, desafio_id, desafio_titulo, desafio_pontos, desafio_icone):
    """Completa um desafio e adiciona pontos"""
    return adicionar_pontos(usuario_id, desafio_pontos, f"Completou: {desafio_titulo}", desafio_icone)

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
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO convites (usuario_id, codigo, data_criacao) VALUES (?, ?, ?)",
        (usuario_id, codigo, datetime.now().strftime("%d/%m/%Y %H:%M"))
    )
    conn.commit()
    conn.close()
    
    return codigo

def iniciar_desafios_semanais(usuario_id):
    """Inicia desafios semanais para o usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verifica se já tem desafios ativos
    c.execute("SELECT * FROM desafios_ativos WHERE usuario_id = ? AND concluido = 0", (usuario_id,))
    if not c.fetchone():
        # Busca todos os desafios disponíveis
        c.execute("SELECT id FROM desafios")
        todos_desafios = [row[0] for row in c.fetchall()]
        
        # Seleciona 3 desafios aleatórios
        if len(todos_desafios) >= 3:
            desafios_selecionados = random.sample(todos_desafios, 3)
            for desafio_id in desafios_selecionados:
                c.execute(
                    "INSERT INTO desafios_ativos (usuario_id, desafio_id, progresso, data_inicio) VALUES (?, ?, ?, ?)",
                    (usuario_id, desafio_id, 0, datetime.now().strftime("%d/%m/%Y"))
                )
    
    conn.commit()
    conn.close()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_perfil(usuario_id, nome, text_color, card_bg, icon_color, border_color):
    """Mostra o perfil do usuário com estatísticas e conquistas"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar progresso
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    progresso = c.fetchone()
    
    # Buscar conquistas recentes
    c.execute("SELECT * FROM conquistas WHERE usuario_id = ? ORDER BY data DESC LIMIT 5", (usuario_id,))
    conquistas = c.fetchall()
    
    # Buscar badges
    c.execute("SELECT * FROM badges WHERE usuario_id = ?", (usuario_id,))
    badges = c.fetchall()
    
    # Buscar desafios ativos
    c.execute("""
        SELECT d.id, d.titulo, d.descricao, d.pontos, d.icone, da.progresso, da.data_inicio, da.concluido
        FROM desafios_ativos da
        JOIN desafios d ON da.desafio_id = d.id
        WHERE da.usuario_id = ?
    """, (usuario_id,))
    desafios = c.fetchall()
    
    conn.close()
    
    # CORREÇÃO: Verificar se progresso existe e tem o tamanho esperado
    if progresso and len(progresso) >= 11:
        pontos = progresso[1] if len(progresso) > 1 else 0
        nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
        eventos = progresso[3] if len(progresso) > 3 else 0
        dicas = progresso[4] if len(progresso) > 4 else 0
        visitas = progresso[5] if len(progresso) > 5 else 0
        kg = progresso[6] if len(progresso) > 6 else 0
        arvores = progresso[7] if len(progresso) > 7 else 0
        amigos = progresso[8] if len(progresso) > 8 else 0
        streak = progresso[9] if len(progresso) > 9 else 0
        desafios_completados = progresso[11] if len(progresso) > 11 else 0
    else:
        pontos = 0
        nivel = "🌱 EcoIniciante"
        eventos = 0
        dicas = 0
        visitas = 0
        kg = 0
        arvores = 0
        amigos = 0
        streak = 0
        desafios_completados = 0
    
    proximo = get_proximo_nivel(pontos)
    
    # Cards de perfil
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid {border_color};'>
            <h3 style='color: {text_color};'>🏆 Badges</h3>
            <h1 style='color: gold; font-size: 48px;'>{len(badges)}</h1>
            <p style='color: {text_color};'>conquistas especiais</p>
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>🌳 Árvores</h4>
            <h2 style='color: {icon_color};'>{arvores}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>👥 Amigos</h4>
            <h2 style='color: {icon_color};'>{amigos}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>🎯 Desafios</h4>
            <h2 style='color: {icon_color};'>{desafios_completados}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>🏆 Nível</h4>
            <h2 style='color: {icon_color};'>{nivel}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Desafios ativos
    if desafios:
        st.markdown(f"<h3 style='color: {text_color};'>🎯 Desafios da Semana</h3>", unsafe_allow_html=True)
        
        for desafio in desafios:
            concluido = desafio[7] if len(desafio) > 7 else 0
            if concluido == 0:  # Só mostrar desafios não concluídos
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color};'>
                        <div style='display: flex; align-items: center; gap: 15px;'>
                            <span style='font-size: 40px;'>{desafio[4]}</span>
                            <div>
                                <h4 style='color: {text_color}; margin: 0;'>{desafio[1]}</h4>
                                <p style='color: {text_color}; margin: 5px 0;'>{desafio[2]}</p>
                                <p style='color: {icon_color}; margin: 0;'>Recompensa: +{desafio[3]} pontos</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button(f"✅ Completar", key=f"completar_{desafio[0]}"):
                        if completar_desafio(usuario_id, desafio[0], desafio[1], desafio[3], desafio[4]):
                            st.success(f"Parabéns! Você ganhou {desafio[3]} pontos!")
                            st.balloons()
                            st.rerun()
    
    # Conquistas recentes
    if conquistas:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Conquistas Recentes</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, conquista in enumerate(conquistas[:3]):
            with cols[i]:
                icone_conquista = conquista[6] if len(conquista) > 6 else '✨'
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid {border_color};'>
                    <span style='font-size: 30px;'>{icone_conquista}</span>
                    <h4 style='color: {text_color};'>{conquista[5]}</h4>
                    <p style='color: {text_color};'><small>{conquista[4][:10] if conquista[4] else ''}</small></p>
                    <span style='color: {icon_color};'>+{conquista[3]} pts</span>
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
    
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid {border_color};'>
        <h4 style='color: {text_color};'>🎁 Benefícios</h4>
        <ul style='color: {text_color};'>
            <li>Você ganha <strong style='color: {icon_color};'>100 pontos</strong> por cada amigo</li>
            <li>Seu amigo ganha <strong style='color: {icon_color};'>50 pontos</strong> de boas-vindas</li>
            <li>Desbloqueia badge de "Multiplicador"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def mostrar_dicas(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra dicas ambientais"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dicas ORDER BY likes DESC")
    dicas = c.fetchall()
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>💡 Dicas Ambientais</h3>", unsafe_allow_html=True)
    
    for dica in dicas:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 6px solid {icon_color}; border: 1px solid {border_color};'>
                <h4 style='color: {text_color};'>{dica[1]}</h4>
                <p style='color: {text_color};'>{dica[2]}</p>
                <small style='color: {text_color};'>Categoria: {dica[3]} | Por: {dica[6]}</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"❤️ {dica[5]}", key=f"like_{dica[0]}_{random.randint(1,1000)}"):
                conn = sqlite3.connect('ecopiracicaba.db')
                c = conn.cursor()
                c.execute("UPDATE dicas SET likes = likes + 1 WHERE id = ?", (dica[0],))
                conn.commit()
                conn.close()
                st.rerun()

def mostrar_eventos(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra eventos"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY data LIMIT 5")
    eventos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>📅 Próximos Eventos</h3>", unsafe_allow_html=True)
    
    for evento in eventos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ff9f4b; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between;'>
                <div>
                    <span style='background: {icon_color}; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px;'>{evento[7].upper()}</span>
                    <h4 style='color: {text_color};'>{evento[1]}</h4>
                    <p style='color: {text_color};'><i class='fas fa-calendar'></i> {evento[3]} às {evento[4]}</p>
                    <p style='color: {text_color};'><i class='fas fa-map-marker-alt'></i> {evento[5]}</p>
                </div>
                <div style='text-align: right;'>
                    <p style='color: {text_color};'><strong>{evento[9]}/{evento[8] if evento[8] > 0 else '∞'}</strong> inscritos</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_pontos_coleta(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra pontos de coleta"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pontos_coleta ORDER BY avaliacao DESC")
    pontos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>📍 Pontos de Coleta</h3>", unsafe_allow_html=True)
    
    for ponto in pontos[:5]:
        estrelas = "★" * int(ponto[8]) + "☆" * (5 - int(ponto[8]))
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between;'>
                <div>
                    <h4 style='color: {text_color};'>{ponto[1]}</h4>
                    <p style='color: {text_color};'><i class='fas fa-map-pin'></i> {ponto[2]}</p>
                    <p style='color: {text_color};'><i class='fas fa-clock'></i> {ponto[4]}</p>
                    <p style='color: {text_color};'><i class='fas fa-phone'></i> {ponto[5]}</p>
                </div>
                <div style='text-align: center;'>
                    <div style='color: gold;'>{estrelas}</div>
                    <p style='color: {text_color};'>{ponto[8]}/5.0</p>
                    <span style='background: {icon_color}; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px;'>{ponto[3].upper()}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== DETECTAR TEMA ==========
tema = get_theme()
dispositivo = detectar_dispositivo()

# Configurações de cores - Sidebar SEMPRE BRANCA com texto PRETO
sidebar_bg = "#FFFFFF"
sidebar_text = "#000000"
sidebar_secondary = "#2a5e45"

# Cores do conteúdo principal baseadas no tema
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

# CSS com sidebar fixa em branco
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    
    /* Sidebar FIXA - sempre branca com texto preto */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4,
    section[data-testid="stSidebar"] .stMarkdown h5,
    section[data-testid="stSidebar"] .stMarkdown h6,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] .stAlert p {{
        color: {sidebar_text} !important;
    }}
    
    section[data-testid="stSidebar"] .stTextInput label {{
        color: {sidebar_text} !important;
    }}
    
    section[data-testid="stSidebar"] .stTextInput input {{
        background-color: #f0f0f0 !important;
        color: {sidebar_text} !important;
        border: 1px solid #cccccc !important;
    }}
    
    section[data-testid="stSidebar"] .stButton button {{
        background-color: {icon_color} !important;
        color: white !important;
        border: none !important;
    }}
    
    section[data-testid="stSidebar"] hr {{
        border-color: #cccccc !important;
    }}
    
    /* Conteúdo principal segue o tema */
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
    
    .stSelectbox div {{
        background-color: {card_bg};
        color: {text_color};
    }}
    
    div.stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
    }}
    
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {icon_color} !important;
        color: white !important;
    }}
    
    /* Animações */
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
</style>

<!-- Font Awesome para ícones -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

if dispositivo == "mobile":
    # Layout mobile
    st.markdown(f"<h1 style='text-align: center; color: {text_color};'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
    
    if st.button("🌓 Tema"):
        toggle_theme()
    
    st.markdown("---")
    
    if st.session_state.usuario_logado is None:
        # Tela de login mobile
        with st.form("login_mobile"):
            st.markdown("### 🔐 Login")
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
                        iniciar_desafios_semanais(user[0])
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos")
        
        st.markdown("---")
        st.markdown("### 🆕 Novo por aqui?")
        with st.form("cadastro_mobile"):
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
        # Menu mobile
        opcao = st.radio("Menu", ["🏠 Início", "👤 Perfil", "🏆 Ranking", "🎯 Desafios", "👥 Convidar", "📍 Pontos"])
        
        if opcao == "👤 Perfil":
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        elif opcao == "🏆 Ranking":
            mostrar_ranking(text_color, card_bg, icon_color, border_color)
        elif opcao == "🎯 Desafios":
            st.rerun()
        elif opcao == "👥 Convidar":
            mostrar_convite(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        elif opcao == "📍 Pontos":
            mostrar_pontos_coleta(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        else:
            st.markdown(f"<h2 style='color: {text_color};'>Bem-vindo, {st.session_state.usuario_logado['nome']}!</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                mostrar_dicas(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
            with col2:
                mostrar_eventos(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)

else:
    # Layout desktop
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: {text_color};'>🌿 EcoPiracicaba 2026</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {secondary_text};'>Sustentabilidade em ação na cidade de Piracicaba</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
            toggle_theme()
    
    if st.session_state.usuario_logado is None:
        # Sidebar de login - AGORA SEMPRE BRANCA
        with st.sidebar:
            st.markdown(f"<h2 style='color: {sidebar_text};'>🔐 Login</h2>", unsafe_allow_html=True)
            
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
                            iniciar_desafios_semanais(user[0])
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos")
            
            st.markdown("---")
            st.markdown(f"<h3 style='color: {sidebar_text};'>🆕 Cadastro</h3>", unsafe_allow_html=True)
            
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
        
        # Página inicial para não logados
        st.markdown(f"""
        <div style='text-align: center; padding: 50px; color: {text_color};'>
            <i class="fas fa-seedling" style='font-size: 80px; color: {icon_color};'></i>
            <h1>Bem-vindo ao EcoPiracicaba</h1>
            <p style='font-size: 1.2rem;'>Faça login para começar a ganhar pontos e subir no ranking!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Preview de conteúdo
        col1, col2 = st.columns(2)
        with col1:
            mostrar_dicas(None, text_color, card_bg, icon_color, border_color)
        with col2:
            mostrar_eventos(None, text_color, card_bg, icon_color, border_color)
    
    else:
        # Sidebar com perfil resumido - AGORA SEMPRE BRANCA
        with st.sidebar:
            conn = sqlite3.connect('ecopiracicaba.db')
            c = conn.cursor()
            c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (st.session_state.usuario_logado['id'],))
            progresso = c.fetchone()
            conn.close()
            
            # CORREÇÃO: Verificar se progresso existe
            if progresso:
                pontos = progresso[1] if len(progresso) > 1 else 0
                nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
                desafios = progresso[11] if len(progresso) > 11 else 0
            else:
                pontos = 0
                nivel = "🌱 EcoIniciante"
                desafios = 0
            
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: #f5f5f5; border-radius: 10px; border: 1px solid #cccccc;'>
                <h3 style='color: {sidebar_text};'>{st.session_state.usuario_logado['nome']}</h3>
                <h4 style='color: {icon_color};'>{nivel}</h4>
                <h2 style='color: {icon_color};'>{pontos} pts</h2>
                <div style='height: 8px; background: #cccccc; border-radius: 4px; margin: 10px 0;'>
                    <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
                </div>
                <p style='color: {sidebar_text};'>🎯 Desafios: {desafios}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.rerun()
        
        # Tabs principais
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Início", "👤 Perfil", "🏆 Ranking", "🎯 Desafios", "👥 Convidar", "📍 Pontos"])
        
        with tab1:
            st.markdown(f"<h2 style='color: {text_color};'>Olá, {st.session_state.usuario_logado['nome']}!</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                mostrar_dicas(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
            with col2:
                mostrar_eventos(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        
        with tab2:
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        
        with tab3:
            mostrar_ranking(text_color, card_bg, icon_color, border_color)
        
        with tab4:
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        
        with tab5:
            mostrar_convite(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        
        with tab6:
            mostrar_pontos_coleta(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
