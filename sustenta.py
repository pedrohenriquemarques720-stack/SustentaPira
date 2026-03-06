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
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

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
    "compartilhar": {"nome": "Influenciador Verde", "pontos": 20, "icone": "📱"},
    "avaliar_ponto": {"nome": "Crítico Ambiental", "pontos": 10, "icone": "⭐"},
}

# Desafios semanais
DESAFIOS = [
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
    },
    {
        "id": 5,
        "titulo": "💧 Economizador de Água",
        "descricao": "Reduza seu consumo em 20%",
        "pontos": 120,
        "icone": "💧",
        "tipo": "agua"
    },
    {
        "id": 6,
        "titulo": "🚲 Ciclista Verde",
        "descricao": "Use bike em vez de carro 3 vezes",
        "pontos": 180,
        "icone": "🚲",
        "tipo": "mobilidade"
    },
    {
        "id": 7,
        "titulo": "🥕 Orgânico é Mais",
        "descricao": "Compre produtos orgânicos 3 vezes",
        "pontos": 90,
        "icone": "🥕",
        "tipo": "alimentacao"
    },
    {
        "id": 8,
        "titulo": "📸 Influenciador Ambiental",
        "descricao": "Compartilhe 3 posts sobre sustentabilidade",
        "pontos": 80,
        "icone": "📱",
        "tipo": "compartilhamento"
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de desafios ativos
    c.execute('''
        CREATE TABLE IF NOT EXISTS desafios_ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            desafio_id INTEGER,
            progresso INTEGER DEFAULT 0,
            concluido INTEGER DEFAULT 0,
            data_inicio TEXT,
            data_conclusao TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de badges/conquistas especiais
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
    
    # Tabela de inscrições
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TEXT,
            confirmado INTEGER DEFAULT 0,
            participou INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (evento_id) REFERENCES eventos (id),
            UNIQUE(usuario_id, evento_id)
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
    
    # Tabela de visualizações de dicas
    c.execute('''
        CREATE TABLE IF NOT EXISTS dicas_vistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            dica_id INTEGER,
            data_vista TEXT,
            UNIQUE(usuario_id, dica_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (dica_id) REFERENCES dicas (id)
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
    
    # Tabela de visitas a pontos
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitas_pontos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            ponto_id INTEGER,
            data_visita TEXT,
            kg_descartados REAL DEFAULT 0,
            UNIQUE(usuario_id, ponto_id, data_visita),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (ponto_id) REFERENCES pontos_coleta (id)
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
    
    # Tabela de compartilhamentos
    c.execute('''
        CREATE TABLE IF NOT EXISTS compartilhamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tipo TEXT,
            data TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
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
            ("🌱 Compostagem Doméstica", "Você sabia que 50% do lixo doméstico pode ser compostado? Aprenda a fazer sua própria composteira com baldes e minhocas californianas. Em 3 meses você terá adubo de alta qualidade.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe EcoPiracicaba"),
            ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros de água. Reduza para 5 minutos e economize 90 litros por banho! Isso representa 2.700 litros por mês.", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas e Baterias", "Nunca descarte pilhas no lixo comum. Leve a pontos de coleta específicos. Uma pilha pode contaminar 20 mil litros de água por até 50 anos.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Plante uma Árvore", "Uma árvore adulta absorve até 150kg de CO2 por ano. Plante árvores nativas da região de Piracicaba como ipê, jatobá e pitanga.", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica"),
            ("🛍️ Sacolas Retornáveis", "Uma sacola plástica leva 400 anos para se decompor. Use sempre sacolas retornáveis nas compras. O Brasil consome 1,5 milhão de sacolas por hora!", "plástico", datetime.now().strftime("%d/%m/%Y"), 0, "WWF"),
            ("🚗 Carona Solidária", "Compartilhe carro com colegas de trabalho. Reduz emissões, congestionamento e você ainda economiza até 40% com combustível.", "mobilidade", datetime.now().strftime("%d/%m/%Y"), 0, "Instituto Clima"),
            ("🥗 Alimentação Orgânica", "Alimentos orgânicos são mais saudáveis e não contaminam o solo com agrotóxicos. Em Piracicaba, feiras orgânicas acontecem aos sábados na ESALQ.", "alimentação", datetime.now().strftime("%d/%m/%Y"), 0, "Feira Orgânica"),
            ("♻️ Separação do Lixo", "Separe sempre recicláveis: papel limpo, plástico, vidro e metal. Lave as embalagens antes de descartar. A reciclagem de uma tonelada de papel salva 20 árvores.", "reciclagem", datetime.now().strftime("%d/%m/%Y"), 0, "Cooperativa Recicladores"),
            ("☀️ Energia Solar", "A energia solar já é a fonte mais barata do Brasil. Uma placa solar de 330W evita a emissão de 4,5 toneladas de CO2 em 25 anos.", "energia", datetime.now().strftime("%d/%m/%Y"), 0, "ABSOLAR"),
            ("🐝 Proteja as Abelhas", "As abelhas são responsáveis por 80% da polinização das plantas. Evite inseticidas e plante flores nativas para ajudar esses insetos essenciais.", "biodiversidade", datetime.now().strftime("%d/%m/%Y"), 0, "Bee Or not to be")
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
            ("Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "organicos", "Seg-Sex 8h-16h", "(19) 3434-5678", -22.730, -47.655, 4.3, "Recebimento de podas e resíduos orgânicos")
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
    
    # Verifica se já existe
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    if not c.fetchone():
        c.execute(
            """INSERT INTO progresso 
               (usuario_id, total_pontos, nivel, ultima_atividade) 
               VALUES (?, ?, ?, ?)""",
            (usuario_id, 0, "🌱 EcoIniciante", datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
    
    conn.commit()
    conn.close()

def adicionar_pontos(usuario_id, tipo, pontos_extra, descricao=""):
    """Adiciona pontos ao usuário e verifica conquistas"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Registrar conquista
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute(
        "INSERT INTO conquistas (usuario_id, tipo, pontos, data, descricao) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, tipo, pontos_extra, data_atual, descricao)
    )
    
    # Atualizar total de pontos
    c.execute("SELECT total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        novos_pontos = pontos_atuais + pontos_extra
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, data_atual, usuario_id)
        )
    
    conn.commit()
    conn.close()
    
    return pontos_extra

def registrar_atividade(usuario_id, tipo, valor=1):
    """Registra atividades do usuário e atualiza streak"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Atualizar contadores específicos
    if tipo == "evento":
        c.execute(
            "UPDATE progresso SET eventos_participados = eventos_participados + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    elif tipo == "dica":
        c.execute(
            "UPDATE progresso SET dicas_vistas = dicas_vistas + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    elif tipo == "ponto":
        c.execute(
            "UPDATE progresso SET pontos_visitados = pontos_visitados + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    elif tipo == "reciclagem":
        c.execute(
            "UPDATE progresso SET kg_reciclados = kg_reciclados + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    elif tipo == "arvore":
        c.execute(
            "UPDATE progresso SET arvores_plantadas = arvores_plantadas + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    elif tipo == "amigo":
        c.execute(
            "UPDATE progresso SET amigos_convidados = amigos_convidados + ? WHERE usuario_id = ?",
            (valor, usuario_id)
        )
    
    # Atualizar streak
    c.execute("SELECT ultima_atividade FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado and resultado[0]:
        ultima = datetime.strptime(resultado[0].split()[0], "%d/%m/%Y")
        hoje = datetime.now()
        
        if (hoje - ultima).days == 1:
            # Streak continua
            c.execute(
                "UPDATE progresso SET streak_dias = streak_dias + 1 WHERE usuario_id = ?",
                (usuario_id,)
            )
        elif (hoje - ultima).days > 1:
            # Streak quebrou
            c.execute(
                "UPDATE progresso SET streak_dias = 1 WHERE usuario_id = ?",
                (usuario_id,)
            )
    
    conn.commit()
    conn.close()

def verificar_conquistas(usuario_id):
    """Verifica e concede conquistas baseadas no progresso"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar progresso
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    progresso = c.fetchone()
    
    if not progresso:
        conn.close()
        return
    
    pontos = c.execute("SELECT SUM(pontos) FROM conquistas WHERE usuario_id = ?", (usuario_id,)).fetchone()[0] or 0
    
    # Verificar conquistas por quantidade
    conquistas_verificar = [
        ("eventos_participados", 1, "primeiro_evento", "Participou do primeiro evento"),
        ("eventos_participados", 5, "cinco_eventos", "Participou de 5 eventos"),
        ("eventos_participados", 10, "dez_eventos", "Participou de 10 eventos"),
        ("dicas_vistas", 1, "primeira_dica", "Leu a primeira dica"),
        ("dicas_vistas", 5, "cinco_dicas", "Leu 5 dicas"),
        ("dicas_vistas", 10, "dez_dicas", "Leu 10 dicas"),
        ("pontos_visitados", 1, "primeiro_ponto", "Visitou o primeiro ponto de coleta"),
        ("pontos_visitados", 5, "cinco_pontos", "Visitou 5 pontos de coleta"),
        ("kg_reciclados", 10, "reciclar_10kg", "Reciclou 10kg"),
        ("kg_reciclados", 50, "reciclar_50kg", "Reciclou 50kg"),
        ("kg_reciclados", 100, "reciclar_100kg", "Reciclou 100kg"),
        ("arvores_plantadas", 1, "plantar_arvore", "Plantou a primeira árvore"),
        ("amigos_convidados", 1, "convidar_amigo", "Convidou um amigo"),
    ]
    
    for coluna, quantidade, tipo, descricao in conquistas_verificar:
        valor_atual = progresso[list(progresso.keys()).index(coluna)] if coluna in progresso.keys() else 0
        if valor_atual >= quantidade:
            # Verificar se já tem essa conquista
            c.execute(
                "SELECT * FROM conquistas WHERE usuario_id = ? AND tipo = ?",
                (usuario_id, tipo)
            )
            if not c.fetchone():
                # Conceder conquista
                pontos_conquista = CONQUISTAS[tipo]["pontos"] if tipo in CONQUISTAS else 10
                adicionar_pontos(usuario_id, tipo, pontos_conquista, descricao)
    
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

def usar_codigo_convite(codigo, novo_usuario_id):
    """Usa código de convite e concede pontos"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM convites WHERE codigo = ? AND usado = 0", (codigo,))
    convite = c.fetchone()
    
    if convite:
        # Marcar como usado
        c.execute(
            "UPDATE convites SET usado = 1, usado_por = ?, data_uso = ? WHERE id = ?",
            (novo_usuario_id, datetime.now().strftime("%d/%m/%Y %H:%M"), convite[0])
        )
        
        # Dar pontos para quem convidou
        adicionar_pontos(convite[1], "convidar_amigo", 100, "Convidou um amigo")
        registrar_atividade(convite[1], "amigo", 1)
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def iniciar_desafios_semanais(usuario_id):
    """Inicia desafios semanais para o usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Selecionar 3 desafios aleatórios
    desafios_selecionados = random.sample(DESAFIOS, 3)
    
    for desafio in desafios_selecionados:
        c.execute(
            """INSERT INTO desafios_ativos 
               (usuario_id, desafio_id, data_inicio) 
               VALUES (?, ?, ?)""",
            (usuario_id, desafio['id'], datetime.now().strftime("%d/%m/%Y"))
        )
    
    conn.commit()
    conn.close()

def atualizar_progresso_desafio(usuario_id, tipo, quantidade=1):
    """Atualiza progresso em desafios ativos"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute(
        """SELECT da.id, d.titulo, d.pontos, da.progresso 
           FROM desafios_ativos da
           JOIN desafios d ON da.desafio_id = d.id
           WHERE da.usuario_id = ? AND da.concluido = 0 AND d.tipo = ?""",
        (usuario_id, tipo)
    )
    
    desafios = c.fetchall()
    
    for desafio in desafios:
        novo_progresso = desafio[3] + quantidade
        c.execute(
            "UPDATE desafios_ativos SET progresso = ? WHERE id = ?",
            (novo_progresso, desafio[0])
        )
        
        # Verificar se concluiu (progresso 100)
        if novo_progresso >= 100:
            c.execute(
                "UPDATE desafios_ativos SET concluido = 1, data_conclusao = ? WHERE id = ?",
                (datetime.now().strftime("%d/%m/%Y %H:%M"), desafio[0])
            )
            # Dar pontos
            adicionar_pontos(usuario_id, f"desafio_{desafio[1]}", desafio[2], f"Completou desafio: {desafio[1]}")
    
    conn.commit()
    conn.close()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_perfil(usuario_id, nome):
    """Mostra o perfil do usuário com estatísticas e conquistas"""
    conn = sqlite3.connect('ecopiracicaba.db')
    
    # Buscar progresso
    progresso = pd.read_sql_query(f"SELECT * FROM progresso WHERE usuario_id = {usuario_id}", conn)
    
    # Buscar conquistas recentes
    conquistas = pd.read_sql_query(
        f"SELECT * FROM conquistas WHERE usuario_id = {usuario_id} ORDER BY data DESC LIMIT 5",
        conn
    )
    
    # Buscar badges
    badges = pd.read_sql_query(f"SELECT * FROM badges WHERE usuario_id = {usuario_id}", conn)
    
    # Buscar desafios ativos
    desafios = pd.read_sql_query(
        f"""SELECT d.*, da.progresso, da.data_inicio 
           FROM desafios_ativos da
           JOIN desafios d ON da.desafio_id = d.id
           WHERE da.usuario_id = {usuario_id} AND da.concluido = 0""",
        conn
    )
    
    conn.close()
    
    if not progresso.empty:
        pontos = progresso.iloc[0]['total_pontos'] if 'total_pontos' in progresso.columns else 0
        nivel = progresso.iloc[0]['nivel'] if 'nivel' in progresso.columns else "🌱 EcoIniciante"
        streak = progresso.iloc[0]['streak_dias'] if 'streak_dias' in progresso.columns else 0
    else:
        pontos = 0
        nivel = "🌱 EcoIniciante"
        streak = 0
    
    proximo = get_proximo_nivel(pontos)
    
    # Cards de perfil
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center;'>
            <h2 style='color: {text_color};'>{nivel}</h2>
            <h1 style='color: {icon_color}; font-size: 48px;'>{pontos}</h1>
            <p>pontos totais</p>
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {min(100, (pontos/5000)*100)}%;'></div>
            </div>
            <p>{proximo} pontos para o próximo nível</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center;'>
            <h3 style='color: {text_color};'>🔥 Streak</h3>
            <h1 style='color: #ff9800; font-size: 48px;'>{streak}</h1>
            <p>dias seguidos</p>
            <p>{'🔥' * min(streak, 10)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; text-align: center;'>
            <h3 style='color: {text_color};'>🏆 Badges</h3>
            <h1 style='color: gold; font-size: 48px;'>{len(badges)}</h1>
            <p>conquistas especiais</p>
            <div style='display: flex; gap: 5px; justify-content: center;'>
                {''.join([f"<span style='font-size: 24px;'>{b[2]}</span>" for b in badges.itertuples()])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Estatísticas
    st.markdown(f"<h3 style='color: {text_color};'>📊 Estatísticas</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center;'>
            <h4>📅 Eventos</h4>
            <h2>{progresso.iloc[0]['eventos_participados'] if not progresso.empty else 0}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center;'>
            <h4>💡 Dicas</h4>
            <h2>{progresso.iloc[0]['dicas_vistas'] if not progresso.empty else 0}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center;'>
            <h4>📍 Visitas</h4>
            <h2>{progresso.iloc[0]['pontos_visitados'] if not progresso.empty else 0}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center;'>
            <h4>♻️ Kg Reciclados</h4>
            <h2>{progresso.iloc[0]['kg_reciclados'] if not progresso.empty else 0}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Desafios ativos
    if not desafios.empty:
        st.markdown(f"<h3 style='color: {text_color};'>🎯 Desafios da Semana</h3>", unsafe_allow_html=True)
        
        for _, desafio in desafios.iterrows():
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 24px;'>{desafio['icone']}</span>
                        <strong>{desafio['titulo']}</strong>
                        <p style='font-size: 12px;'>{desafio['descricao']}</p>
                    </div>
                    <div style='text-align: right;'>
                        <span style='color: {icon_color};'>+{desafio['pontos']} pts</span>
                        <div class='progress-bar' style='width: 100px;'>
                            <div class='progress-fill' style='width: {desafio['progresso']}%;'></div>
                        </div>
                        <small>{desafio['progresso']}%</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Conquistas recentes
    if not conquistas.empty:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Conquistas Recentes</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, (_, conquista) in enumerate(conquistas.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                    <span style='font-size: 30px;'>✨</span>
                    <h4>{conquista['descricao']}</h4>
                    <p><small>{conquista['data']}</small></p>
                    <span style='color: {icon_color};'>+{conquista['pontos']} pts</span>
                </div>
                """, unsafe_allow_html=True)

def mostrar_ranking():
    """Mostra ranking de usuários"""
    conn = sqlite3.connect('ecopiracicaba.db')
    
    ranking = pd.read_sql_query("""
        SELECT u.nome, p.total_pontos, p.nivel 
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        ORDER BY p.total_pontos DESC
        LIMIT 10
    """, conn)
    
    conn.close()
    
    st.markdown(f"<h3 style='color: {text_color};'>🏆 Ranking EcoCidadãos</h3>", unsafe_allow_html=True)
    
    for i, (_, usuario) in enumerate(ranking.iterrows()):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}º"
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>
            <div style='display: flex; justify-content: space-between;'>
                <span><strong>{medalha} {usuario['nome']}</strong> - {usuario['nivel']}</span>
                <span style='color: {icon_color};'><strong>{usuario['total_pontos']} pts</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_convite(usuario_id):
    """Mostra sistema de convite"""
    codigo = gerar_codigo_convite(usuario_id)
    
    st.markdown(f"<h3 style='color: {text_color};'>👥 Convidar Amigos</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(f"ECOPIRA-{codigo}", language="text")
    with col2:
        if st.button("📋 Copiar"):
            st.success("Código copiado!")
    
    st.markdown("""
    <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; margin-top: 10px;'>
        <h4>🎁 Benefícios</h4>
        <ul>
            <li>Você ganha <strong>100 pontos</strong> por cada amigo que se cadastrar</li>
            <li>Seu amigo ganha <strong>50 pontos</strong> de boas-vindas</li>
            <li>Desbloqueia badge de "Multiplicador"</li>
        </ul>
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

# ========== INTERFACE PRINCIPAL ==========

if dispositivo == "mobile":
    # Layout mobile
    st.markdown("<h1 style='text-align: center;'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
    
    # Login/Perfil (simplificado)
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if st.session_state.usuario_logado is None:
        # Tela de login mobile
        with st.form("login_mobile"):
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
    else:
        # Menu mobile
        opcao = st.radio("Menu", ["🏠 Início", "👤 Perfil", "🏆 Ranking", "🎯 Desafios", "👥 Convidar"])
        
        if opcao == "👤 Perfil":
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'])
        elif opcao == "🏆 Ranking":
            mostrar_ranking()
        elif opcao == "🎯 Desafios":
            iniciar_desafios_semanais(st.session_state.usuario_logado['id'])
            st.info("Desafios carregados!")
        elif opcao == "👥 Convidar":
            mostrar_convite(st.session_state.usuario_logado['id'])
        else:
            st.write("Bem-vindo ao EcoPiracicaba!")

else:
    # Layout desktop
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"<h1 style='color: {text_color};'>🌿 EcoPiracicaba</h1>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
            toggle_theme()
    
    # Estado do usuário
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if st.session_state.usuario_logado is None:
        # Sidebar de login
        with st.sidebar:
            st.markdown(f"<h2 style='color: {text_color};'>🔐 Login</h2>", unsafe_allow_html=True)
            
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
            if st.button("Criar conta", use_container_width=True):
                st.info("Função de cadastro em breve!")
    
    else:
        # Sidebar com perfil resumido
        with st.sidebar:
            conn = sqlite3.connect('ecopiracicaba.db')
            progresso = pd.read_sql_query(f"SELECT * FROM progresso WHERE usuario_id = {st.session_state.usuario_logado['id']}", conn)
            conn.close()
            
            pontos = progresso.iloc[0]['total_pontos'] if not progresso.empty else 0
            nivel = progresso.iloc[0]['nivel'] if not progresso.empty else "🌱 EcoIniciante"
            
            st.markdown(f"""
            <div style='text-align: center;'>
                <h3 style='color: {text_color};'>{st.session_state.usuario_logado['nome']}</h3>
                <h4 style='color: {icon_color};'>{nivel}</h4>
                <h2>{pontos} pts</h2>
                <div class='progress-bar'>
                    <div class='progress-fill' style='width: {min(100, (pontos/5000)*100)}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.rerun()
        
        # Tabs principais
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Início", "👤 Perfil", "🏆 Ranking", "👥 Convidar"])
        
        with tab1:
            st.markdown(f"<h2 style='color: {text_color};'>Bem-vindo ao EcoPiracicaba!</h2>", unsafe_allow_html=True)
            st.markdown("Acompanhe seu progresso e participe de desafios ambientais!")
            
            # Feed de conquistas
            conn = sqlite3.connect('ecopiracicaba.db')
            feed = pd.read_sql_query("""
                SELECT u.nome, c.descricao, c.pontos, c.data 
                FROM conquistas c
                JOIN usuarios u ON c.usuario_id = u.id
                ORDER BY c.data DESC
                LIMIT 10
            """, conn)
            conn.close()
            
            if not feed.empty:
                st.markdown(f"<h3 style='color: {text_color};'>📰 Feed de Atividades</h3>", unsafe_allow_html=True)
                for _, item in feed.iterrows():
                    st.markdown(f"""
                    <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>
                        <strong>{item['nome']}</strong> {item['descricao']} 
                        <span style='color: {icon_color};'>+{item['pontos']} pts</span>
                        <br><small>{item['data']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'])
        
        with tab3:
            mostrar_ranking()
        
        with tab4:
            mostrar_convite(st.session_state.usuario_logado['id'])
