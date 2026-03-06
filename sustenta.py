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
    },
    {
        "id": 4,
        "titulo": "🔋 Descartar Pilhas",
        "descricao": "Descarte 5 pilhas ou baterias em pontos de coleta",
        "objetivo": 5,
        "unidade": "pilhas",
        "pontos": 150,
        "icone": "🔋",
        "tipo": "pilhas",
        "badge": "🔋 Coletor de Pilhas"
    },
    {
        "id": 5,
        "titulo": "💧 Economizar Água",
        "descricao": "Reduza seu consumo de água em 20% esta semana",
        "objetivo": 20,
        "unidade": "%",
        "pontos": 250,
        "icone": "💧",
        "tipo": "agua",
        "badge": "💧 Amigo da Água"
    },
    {
        "id": 6,
        "titulo": "🚲 Usar Bike 3x",
        "descricao": "Use bicicleta em vez de carro 3 vezes esta semana",
        "objetivo": 3,
        "unidade": "vezes",
        "pontos": 180,
        "icone": "🚲",
        "tipo": "mobilidade",
        "badge": "🚲 Ciclista Verde"
    },
    {
        "id": 7,
        "titulo": "🥕 Comprar Orgânicos",
        "descricao": "Compre produtos orgânicos 3 vezes esta semana",
        "objetivo": 3,
        "unidade": "vezes",
        "pontos": 120,
        "icone": "🥕",
        "tipo": "alimentacao",
        "badge": "🥕 Consumidor Consciente"
    },
    {
        "id": 8,
        "titulo": "📚 Ler 5 Dicas",
        "descricao": "Leia 5 dicas ambientais no app",
        "objetivo": 5,
        "unidade": "dicas",
        "pontos": 80,
        "icone": "📚",
        "tipo": "dicas",
        "badge": "📚 Sábio Ambiental"
    },
    {
        "id": 9,
        "titulo": "👥 Convidar 2 Amigos",
        "descricao": "Convide 2 amigos para o app",
        "objetivo": 2,
        "unidade": "amigos",
        "pontos": 400,
        "icone": "👥",
        "tipo": "convite",
        "badge": "👥 Multiplicador Verde"
    },
    {
        "id": 10,
        "titulo": "📍 Visitar 3 Ecopontos",
        "descricao": "Visite 3 pontos de coleta diferentes",
        "objetivo": 3,
        "unidade": "pontos",
        "pontos": 200,
        "icone": "📍",
        "tipo": "visitas",
        "badge": "📍 Explorador Ambiental"
    }
]

# Prêmios especiais por completar múltiplos desafios
PREMIOS = [
    {
        "nome": "🥉 Bronze Ambiental",
        "descricao": "Complete 3 desafios na semana",
        "icone": "🥉",
        "pontos_bonus": 100,
        "min_desafios": 3
    },
    {
        "nome": "🥈 Prata Ambiental",
        "descricao": "Complete 5 desafios na semana",
        "icone": "🥈",
        "pontos_bonus": 250,
        "min_desafios": 5
    },
    {
        "nome": "🥇 Ouro Ambiental",
        "descricao": "Complete 7 desafios na semana",
        "icone": "🥇",
        "pontos_bonus": 500,
        "min_desafios": 7
    },
    {
        "nome": "🏆 Campeão da Sustentabilidade",
        "descricao": "Complete todos os 10 desafios na semana",
        "icone": "🏆",
        "pontos_bonus": 1000,
        "min_desafios": 10
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
    
    # Verificar se a tabela progresso existe e quais colunas ela tem
    c.execute("PRAGMA table_info(progresso)")
    colunas_progresso = [col[1] for col in c.fetchall()]
    
    # Se a tabela não existe, criar com todas as colunas
    if not colunas_progresso:
        c.execute('''
            CREATE TABLE progresso (
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
                desafios_completados_semana INTEGER DEFAULT 0,
                melhor_semana INTEGER DEFAULT 0,
                total_desafios_completados INTEGER DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
    else:
        # Se a tabela existe mas falta alguma coluna, adicionar
        colunas_necessarias = [
            'desafios_completados_semana', 'melhor_semana', 'total_desafios_completados'
        ]
        
        for coluna in colunas_necessarias:
            if coluna not in colunas_progresso:
                try:
                    c.execute(f"ALTER TABLE progresso ADD COLUMN {coluna} INTEGER DEFAULT 0")
                except:
                    pass  # Coluna já existe
    
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
    
    # Tabela de desafios ativos do usuário (semana atual)
    c.execute('''
        CREATE TABLE IF NOT EXISTS desafios_ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            desafio_id INTEGER,
            progresso REAL DEFAULT 0,
            concluido INTEGER DEFAULT 0,
            data_inicio TEXT,
            data_conclusao TEXT,
            premio_recebido INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (desafio_id) REFERENCES desafios (id)
        )
    ''')
    
    # Tabela de histórico semanal
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_semanal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            semana TEXT,
            desafios_completados INTEGER,
            pontos_ganhos INTEGER,
            premio_especial TEXT,
            data_registro TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
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
    
    # Tabela de inscrições em eventos
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TEXT,
            participou INTEGER DEFAULT 0,
            UNIQUE(usuario_id, evento_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (evento_id) REFERENCES eventos (id)
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
            quantidade REAL DEFAULT 0,
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
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses, login_provider) VALUES (?, ?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", datetime.now().strftime("%d/%m/%Y"), "sustentabilidade,reciclagem", "email")
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
               (usuario_id, total_pontos, nivel, ultima_atividade, desafios_completados_semana, total_desafios_completados) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (usuario_id, 0, "🌱 EcoIniciante", datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0)
        )
    
    conn.commit()
    conn.close()

def adicionar_pontos(usuario_id, tipo, pontos_extra, descricao="", icone="✨"):
    """Adiciona pontos ao usuário e registra conquista"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute(
        "INSERT INTO conquistas (usuario_id, tipo, pontos, data, descricao, icone) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, tipo, pontos_extra, data_atual, descricao, icone)
    )
    
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

def adicionar_badge(usuario_id, badge_nome, badge_icone):
    """Adiciona um badge ao usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO badges (usuario_id, badge_nome, badge_icone, data_obtencao) VALUES (?, ?, ?, ?)",
            (usuario_id, badge_nome, badge_icone, datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Badge já existe
        pass
    
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
    
    # Atualizar progresso dos desafios
    atualizar_progresso_desafios(usuario_id, tipo, valor)
    
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

# ========== FUNÇÕES DE DESAFIOS ==========

def iniciar_desafios_semanais(usuario_id):
    """Inicia desafios semanais para o usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verifica se já tem desafios ativos desta semana
    c.execute("""
        SELECT * FROM desafios_ativos 
        WHERE usuario_id = ? AND concluido = 0 
        AND date(data_inicio) >= date('now', '-7 days')
    """, (usuario_id,))
    
    if not c.fetchone():
        # Remove desafios antigos
        c.execute("DELETE FROM desafios_ativos WHERE usuario_id = ?", (usuario_id,))
        
        # Seleciona 5 desafios aleatórios
        c.execute("SELECT id FROM desafios")
        todos_desafios = [row[0] for row in c.fetchall()]
        
        if len(todos_desafios) >= 5:
            desafios_selecionados = random.sample(todos_desafios, 5)
            for desafio_id in desafios_selecionados:
                c.execute(
                    """INSERT INTO desafios_ativos 
                       (usuario_id, desafio_id, progresso, data_inicio) 
                       VALUES (?, ?, ?, ?)""",
                    (usuario_id, desafio_id, 0, datetime.now().strftime("%Y-%m-%d"))
                )
    
    conn.commit()
    conn.close()

def atualizar_progresso_desafios(usuario_id, tipo, valor):
    """Atualiza o progresso dos desafios baseado nas atividades"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Busca desafios ativos do tipo correspondente
    c.execute("""
        SELECT da.id, d.id, d.objetivo, d.pontos, d.badge, d.titulo, da.progresso
        FROM desafios_ativos da
        JOIN desafios d ON da.desafio_id = d.id
        WHERE da.usuario_id = ? AND d.tipo = ? AND da.concluido = 0
    """, (usuario_id, tipo))
    
    desafios = c.fetchall()
    
    for desafio in desafios:
        novo_progresso = desafio[6] + valor
        if novo_progresso >= desafio[2]:
            # Desafio completado
            c.execute(
                "UPDATE desafios_ativos SET progresso = ?, concluido = 1, data_conclusao = ? WHERE id = ?",
                (desafio[2], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), desafio[0])
            )
            
            # Dar pontos
            adicionar_pontos(usuario_id, f"desafio_{desafio[1]}", desafio[3], 
                           f"Completou o desafio: {desafio[5]}", desafio[4])
            
            # Dar badge
            adicionar_badge(usuario_id, desafio[4], desafio[4])
            
            # Atualizar contador de desafios da semana
            c.execute("""
                UPDATE progresso SET 
                    desafios_completados_semana = desafios_completados_semana + 1,
                    total_desafios_completados = total_desafios_completados + 1
                WHERE usuario_id = ?
            """, (usuario_id,))
        else:
            # Atualizar progresso
            c.execute(
                "UPDATE desafios_ativos SET progresso = ? WHERE id = ?",
                (novo_progresso, desafio[0])
            )
    
    conn.commit()
    
    # Verificar prêmios especiais
    verificar_premios_especiais(usuario_id)
    
    conn.close()

def verificar_premios_especiais(usuario_id):
    """Verifica se o usuário ganhou prêmios por completar múltiplos desafios"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Quantos desafios completou esta semana
    c.execute("""
        SELECT COUNT(*) FROM desafios_ativos 
        WHERE usuario_id = ? AND concluido = 1
    """, (usuario_id,))
    completados = c.fetchone()[0]
    
    # Buscar melhor semana atual
    c.execute("SELECT melhor_semana FROM progresso WHERE usuario_id = ?", (usuario_id,))
    melhor_semana = c.fetchone()
    if melhor_semana:
        if completados > melhor_semana[0]:
            c.execute("UPDATE progresso SET melhor_semana = ? WHERE usuario_id = ?", (completados, usuario_id))
    
    # Verificar prêmios não recebidos ainda
    for premio in PREMIOS:
        if completados >= premio["min_desafios"]:
            # Verificar se já recebeu esse prêmio esta semana
            c.execute("""
                SELECT * FROM historico_semanal 
                WHERE usuario_id = ? AND premio_especial = ? 
                ORDER BY id DESC LIMIT 1
            """, (usuario_id, premio["nome"]))
            
            if not c.fetchone():
                # Dar prêmio
                adicionar_pontos(usuario_id, f"premio_semana", premio["pontos_bonus"], 
                               f"Ganhou: {premio['nome']}", premio["icone"])
                adicionar_badge(usuario_id, premio["nome"], premio["icone"])
                
                # Registrar no histórico
                c.execute("""
                    INSERT INTO historico_semanal 
                    (usuario_id, semana, desafios_completados, pontos_ganhos, premio_especial, data_registro)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario_id, datetime.now().strftime("%Y-%m-%d"), completados, 
                      premio["pontos_bonus"], premio["nome"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra página dedicada aos desafios"""
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios Semanais</h2>", unsafe_allow_html=True)
    
    # Iniciar desafios se não existirem
    iniciar_desafios_semanais(usuario_id)
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar progresso - CORRIGIDO: verificar se a coluna existe
    try:
        c.execute("SELECT desafios_completados_semana, total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
        prog = c.fetchone()
        completados = prog[0] if prog else 0
        pontos = prog[1] if prog else 0
    except:
        # Se a coluna não existir, usar valor padrão
        c.execute("SELECT total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
        prog = c.fetchone()
        completados = 0
        pontos = prog[0] if prog else 0
    
    # Buscar desafios ativos - CORRIGIDO: verificar se existem
    c.execute("""
        SELECT d.id, d.titulo, d.descricao, d.objetivo, d.unidade, d.pontos, d.icone, 
               COALESCE(da.progresso, 0) as progresso, COALESCE(da.concluido, 0) as concluido, 
               COALESCE(da.data_inicio, '') as data_inicio
        FROM desafios d
        LEFT JOIN desafios_ativos da ON d.id = da.desafio_id AND da.usuario_id = ?
        WHERE da.usuario_id = ? OR da.usuario_id IS NULL
        ORDER BY da.concluido, d.id
        LIMIT 5
    """, (usuario_id, usuario_id))
    
    desafios = c.fetchall()
    
    conn.close()
    
    # Mostrar progresso semanal
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Progresso Semanal</h3>
        <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
            <div>
                <span style='font-size: 36px; color: {icon_color};'>{completados}</span>
                <p style='color: {text_color};'>Desafios Completados</p>
            </div>
            <div>
                <span style='font-size: 36px; color: gold;'>🏆</span>
                <p style='color: {text_color};'>{pontos} Pontos</p>
            </div>
        </div>
        <div style='height: 10px; background: {border_color}; border-radius: 5px;'>
            <div style='height: 100%; width: {min(100, (completados/5)*100)}%; background: {icon_color}; border-radius: 5px;'></div>
        </div>
        <p style='color: {text_color}; margin-top: 10px;'>Complete 5 desafios para ganhar prêmios especiais!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar prêmios disponíveis
    st.markdown(f"<h3 style='color: {text_color};'>🎁 Prêmios da Semana</h3>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, premio in enumerate(PREMIOS):
        with cols[i]:
            cor = "#cd7f32" if i == 0 else "#c0c0c0" if i == 1 else "#ffd700" if i == 2 else "#ff6b6b"
            disponivel = completados >= premio["min_desafios"]
            
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid {cor if disponivel else border_color}; opacity: {1 if disponivel else 0.5};'>
                <span style='font-size: 36px;'>{premio['icone']}</span>
                <h4 style='color: {text_color};'>{premio['nome']}</h4>
                <p style='color: {text_color};'>{premio['descricao']}</p>
                <p style='color: {icon_color};'>+{premio['pontos_bonus']} pts</p>
                {'' if disponivel else '<p style="color: #f44336;">🔒 Bloqueado</p>'}
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar desafios
    if desafios:
        st.markdown(f"<h3 style='color: {text_color};'>📋 Seus Desafios</h3>", unsafe_allow_html=True)
        
        for desafio in desafios:
            if desafio[7] is not None:  # Se tem progresso
                progresso_percent = (desafio[7] / desafio[3]) * 100 if desafio[3] > 0 else 0
                status = "✅ Concluído" if desafio[8] == 1 else f"Progresso: {desafio[7]:.0f}/{desafio[3]} {desafio[4]}"
                cor_status = icon_color if desafio[8] == 1 else text_color
                
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 6px solid {icon_color if desafio[8]==0 else '#4caf50'}; border: 1px solid {border_color};'>
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <span style='font-size: 40px;'>{desafio[6]}</span>
                        <div style='flex: 1;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <h4 style='color: {text_color}; margin: 0;'>{desafio[1]}</h4>
                                <span style='color: {icon_color};'>+{desafio[5]} pts</span>
                            </div>
                            <p style='color: {text_color}; margin: 5px 0;'>{desafio[2]}</p>
                            <div style='display: flex; align-items: center; gap: 10px;'>
                                <div style='flex: 1; height: 10px; background: {border_color}; border-radius: 5px;'>
                                    <div style='height: 100%; width: {progresso_percent}%; background: {icon_color if desafio[8]==0 else '#4caf50'}; border-radius: 5px;'></div>
                                </div>
                                <span style='color: {cor_status}; min-width: 120px;'>{status}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Carregando desafios...")
    
    # Badges conquistados
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT badge_nome, badge_icone, data_obtencao FROM badges WHERE usuario_id = ? ORDER BY data_obtencao DESC LIMIT 8", (usuario_id,))
    badges = c.fetchall()
    conn.close()
    
    if badges:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Suas Conquistas</h3>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, badge in enumerate(badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid gold;'>
                    <span style='font-size: 30px;'>{badge[1]}</span>
                    <p style='color: {text_color}; font-weight: bold;'>{badge[0]}</p>
                    <p style='color: {text_color}; font-size: 10px;'>{badge[2][:10] if badge[2] else ''}</p>
                </div>
                """, unsafe_allow_html=True)

def mostrar_perfil(usuario_id, nome, text_color, card_bg, icon_color, border_color):
    """Mostra o perfil do usuário com estatísticas e conquistas"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Buscar progresso - CORRIGIDO: verificar colunas existentes
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (usuario_id,))
    progresso = c.fetchone()
    
    if progresso:
        # Mapear valores baseado no número de colunas
        pontos = progresso[1] if len(progresso) > 1 else 0
        nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
        eventos = progresso[3] if len(progresso) > 3 else 0
        dicas = progresso[4] if len(progresso) > 4 else 0
        visitas = progresso[5] if len(progresso) > 5 else 0
        kg = progresso[6] if len(progresso) > 6 else 0
        arvores = progresso[7] if len(progresso) > 7 else 0
        amigos = progresso[8] if len(progresso) > 8 else 0
        streak = progresso[9] if len(progresso) > 9 else 0
        desafios_semana = progresso[11] if len(progresso) > 11 else 0
        total_desafios = progresso[12] if len(progresso) > 12 else 0
    else:
        pontos = 0
        nivel = "🌱 EcoIniciante"
        eventos = dicas = visitas = kg = arvores = amigos = streak = desafios_semana = total_desafios = 0
    
    # Buscar conquistas recentes
    c.execute("SELECT * FROM conquistas WHERE usuario_id = ? ORDER BY data DESC LIMIT 5", (usuario_id,))
    conquistas = c.fetchall()
    
    # Buscar badges
    c.execute("SELECT * FROM badges WHERE usuario_id = ?", (usuario_id,))
    badges = c.fetchall()
    
    conn.close()
    
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
            <h2 style='color: {icon_color};'>{desafios_semana}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>🏅 Total</h4>
            <h2 style='color: {icon_color};'>{total_desafios}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Conquistas recentes
    if conquistas:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Conquistas Recentes</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, conquista in enumerate(conquistas[:3]):
            with cols[i]:
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid {border_color};'>
                    <span style='font-size: 30px;'>{conquista[6] if len(conquista) > 6 else '✨'}</span>
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
        SELECT u.nome, p.total_pontos, p.nivel, 
               COALESCE(p.desafios_completados_semana, 0) as desafios
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
                <div>
                    <span style='color: {text_color};'><strong>{medalha} {usuario[0]}</strong> - {usuario[2]}</span>
                </div>
                <div>
                    <span style='color: {icon_color}; margin-right: 15px;'><strong>{usuario[1]} pts</strong></span>
                    <span style='color: #ff9800;'>🎯 {usuario[3]}</span>
                </div>
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
            <li>Complete o desafio "👥 Convidar 2 Amigos" para ganhar <strong style='color: {icon_color};'>400 pontos extras</strong> e badge especial!</li>
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
    
    .premio-disponivel {{
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
        opcao = st.radio("Menu", ["🏠 Início", "🎯 Desafios", "👤 Perfil", "🏆 Ranking", "👥 Convidar", "📍 Pontos"])
        
        if opcao == "🎯 Desafios":
            mostrar_pagina_desafios(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        elif opcao == "👤 Perfil":
            mostrar_perfil(st.session_state.usuario_logado['id'], st.session_state.usuario_logado['nome'], 
                          text_color, card_bg, icon_color, border_color)
        elif opcao == "🏆 Ranking":
            mostrar_ranking(text_color, card_bg, icon_color, border_color)
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
                            iniciar_desafios_semanais(user[0])
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos")
            
            st.markdown("---")
            st.markdown(f"<h3 style='color: {text_color};'>🆕 Cadastro</h3>", unsafe_allow_html=True)
            
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
            <p style='font-size: 1.2rem;'>Faça login para começar a ganhar pontos, completar desafios e subir no ranking!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Preview de conteúdo
        col1, col2 = st.columns(2)
        with col1:
            mostrar_dicas(None, text_color, card_bg, icon_color, border_color)
        with col2:
            mostrar_eventos(None, text_color, card_bg, icon_color, border_color)
    
    else:
        # Sidebar com perfil resumido
        with st.sidebar:
            conn = sqlite3.connect('ecopiracicaba.db')
            c = conn.cursor()
            c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (st.session_state.usuario_logado['id'],))
            progresso = c.fetchone()
            
            # Buscar desafios completados na semana
            c.execute("SELECT COUNT(*) FROM desafios_ativos WHERE usuario_id = ? AND concluido = 1", (st.session_state.usuario_logado['id'],))
            completados = c.fetchone()[0]
            conn.close()
            
            pontos = progresso[1] if progresso and len(progresso) > 1 else 0
            nivel = progresso[2] if progresso and len(progresso) > 2 else "🌱 EcoIniciante"
            
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background: {card_bg}; border-radius: 10px; border: 1px solid {border_color};'>
                <h3 style='color: {text_color};'>{st.session_state.usuario_logado['nome']}</h3>
                <h4 style='color: {icon_color};'>{nivel}</h4>
                <h2 style='color: {icon_color};'>{pontos} pts</h2>
                <div style='height: 8px; background: {border_color}; border-radius: 4px; margin: 10px 0;'>
                    <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
                </div>
                <p style='color: {text_color};'>🎯 Desafios: {completados}/5</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.rerun()
        
        # Tabs principais
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Início", "🎯 Desafios", "👤 Perfil", "🏆 Ranking", "👥 Convidar", "📍 Pontos"])
        
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
            mostrar_convite(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
        
        with tab6:
            mostrar_pontos_coleta(st.session_state.usuario_logado['id'], text_color, card_bg, icon_color, border_color)
