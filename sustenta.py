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
import os
from PIL import Image
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="EcoPiracicaba 2026",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FUNÇÕES BÁSICAS ==========

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

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"
    st.rerun()

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

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== FUNÇÕES DE NÍVEL ==========

def get_nivel(pontos):
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

DESAFIOS_LISTA = [
    {
        "id": 1,
        "titulo": "♻️ Reciclar 10kg",
        "descricao": "Recicle 10kg de materiais recicláveis",
        "pontos": 200,
        "icone": "♻️",
        "tipo": "reciclagem"
    },
    {
        "id": 2,
        "titulo": "📅 Participar de Evento",
        "descricao": "Participe de 1 evento ambiental",
        "pontos": 150,
        "icone": "📅",
        "tipo": "evento"
    },
    {
        "id": 3,
        "titulo": "🌳 Plantar Árvore",
        "descricao": "Plante 1 árvore nativa",
        "pontos": 300,
        "icone": "🌳",
        "tipo": "plantio"
    },
    {
        "id": 4,
        "titulo": "🔋 Descartar Pilhas",
        "descricao": "Descarte 5 pilhas em ponto de coleta",
        "pontos": 100,
        "icone": "🔋",
        "tipo": "pilhas"
    },
    {
        "id": 5,
        "titulo": "🚲 Usar Bike",
        "descricao": "Use bicicleta em vez de carro 3 vezes",
        "pontos": 180,
        "icone": "🚲",
        "tipo": "mobilidade"
    }
]

# ========== INICIALIZAÇÃO DO BANCO DE DADOS ==========

def init_database():
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Para garantir estrutura nova, dropamos as tabelas existentes (apenas em desenvolvimento)
    # Em produção, comente estas linhas
    c.execute("DROP TABLE IF EXISTS convites")
    c.execute("DROP TABLE IF EXISTS visitas_pontos")
    c.execute("DROP TABLE IF EXISTS pontos_coleta")
    c.execute("DROP TABLE IF EXISTS dicas_vistas")
    c.execute("DROP TABLE IF EXISTS dicas")
    c.execute("DROP TABLE IF EXISTS inscricoes")
    c.execute("DROP TABLE IF EXISTS eventos")
    c.execute("DROP TABLE IF EXISTS comprovantes")
    c.execute("DROP TABLE IF EXISTS conquistas")
    c.execute("DROP TABLE IF EXISTS progresso")
    c.execute("DROP TABLE IF EXISTS usuarios")
    
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
    
    # Tabela de progresso do usuário - SEM a coluna desafios_completados
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de conquistas
    c.execute('''
        CREATE TABLE IF NOT EXISTS conquistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tipo TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT,
            icone TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de comprovantes (fotos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS comprovantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            imagem BLOB,
            pontos_ganhos INTEGER DEFAULT 0,
            data TEXT NOT NULL,
            aprovado INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
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
            tipo TEXT,
            vagas INTEGER,
            inscritos INTEGER DEFAULT 0,
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (evento_id) REFERENCES eventos (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de dicas
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (dica_id) REFERENCES dicas (id) ON DELETE CASCADE
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (ponto_id) REFERENCES pontos_coleta (id) ON DELETE CASCADE
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (usado_por) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    
    # Agora que as tabelas estão criadas, vamos inserir os dados iniciais
    dados_iniciais(conn, c)
    
    conn.commit()
    conn.close()

def dados_iniciais(conn, c):
    """Insere dados iniciais no banco - VERSÃO FINAL SEM DESAFIOS_COMPLETADOS"""
    
    # ===== USUÁRIO ADMIN =====
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        data_atual = datetime.now().strftime("%d/%m/%Y")
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses) VALUES (?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", data_atual, "sustentabilidade,reciclagem")
        )
        admin_id = c.lastrowid
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (admin_id, 1000, get_nivel(1000), data_atual)
        )
    
    # ===== USUÁRIOS DE EXEMPLO =====
    usuarios_exemplo = [
        ("João Silva", "joao@email.com", "123", "sustentabilidade,reciclagem", 350),
        ("Maria Santos", "maria@email.com", "123", "eventos,voluntariado", 520),
        ("Pedro Oliveira", "pedro@email.com", "123", "compostagem,natureza", 180)
    ]
    
    for nome, email, senha, interesses, pontos in usuarios_exemplo:
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not c.fetchone():
            data_atual = datetime.now().strftime("%d/%m/%Y")
            c.execute(
                "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses) VALUES (?, ?, ?, ?, ?)",
                (nome, email, senha, data_atual, interesses)
            )
            user_id = c.lastrowid
            nivel = get_nivel(pontos)
            c.execute(
                "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
                (user_id, pontos, nivel, data_atual)
            )
    
    # ===== EVENTOS 2026 - PIRACICABA =====
    c.execute("SELECT COUNT(*) FROM eventos")
    if c.fetchone()[0] == 0:
        eventos = [
            ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos, artesanato sustentável e startups verdes", "15/03/2026", "09:00", "Engenho Central - Piracicaba", "feira", 1000, "Prefeitura de Piracicaba", "(19) 3403-1100"),
            ("♻️ Workshop de Reciclagem", "Aprenda técnicas avançadas de reciclagem em casa", "22/03/2026", "14:00", "SENAI Piracicaba", "workshop", 50, "SENAI", "(19) 3412-5000"),
            ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio com atividades educativas", "05/04/2026", "08:00", "Rua do Porto - Piracicaba", "mutirão", 200, "SOS Rio Piracicaba", "(19) 99765-4321"),
            ("🌿 Palestra: Compostagem", "Como fazer compostagem doméstica e comunitária", "12/04/2026", "10:00", "Horto Municipal - Piracicaba", "palestra", 100, "Horto Municipal", "(19) 3434-5678"),
            ("🌍 Dia da Terra", "Celebração com atividades, música e feira verde", "22/04/2026", "09:00", "Parque da Rua do Porto - Piracicaba", "evento", 2000, "ONG Planeta Verde", "(19) 99876-5432"),
            ("🔋 Descarte de Eletrônicos", "Campanha de coleta de lixo eletrônico", "10/05/2026", "09:00", "Shopping Piracicaba", "campanha", 0, "Green Eletronics", "(19) 3403-3000"),
            ("🌳 Plantio de Árvores", "Mutirão de plantio de árvores nativas", "05/06/2026", "08:30", "Parque Ecológico - Piracicaba", "mutirão", 300, "SOS Mata Atlântica", "(11) 3262-4088"),
            ("🚴 Passeio Ciclístico", "Passeio ecológico de bike pela cidade", "20/06/2026", "08:00", "Largo dos Pescadores - Piracicaba", "passeio", 150, "Ciclovida", "(19) 99876-1234"),
            ("🥕 Feira Orgânica", "Feira de produtos orgânicos e agroecológicos", "10/07/2026", "08:00", "Mercado Municipal - Piracicaba", "feira", 0, "Associação Orgânicos", "(19) 3434-7890"),
            ("💧 Semana da Água", "Palestras e atividades sobre preservação da água", "15/08/2026", "09:00", "Teatro Municipal - Piracicaba", "evento", 400, "Comitê PCJ", "(19) 3437-2000"),
            ("🐝 Dia das Abelhas", "Palestra sobre a importância das abelhas", "29/08/2026", "14:00", "ESALQ - Piracicaba", "palestra", 80, "USP", "(19) 3447-8500")
        ]
        for e in eventos:
            c.execute(
                "INSERT INTO eventos (titulo, descricao, data, hora, local, tipo, vagas, organizador, contato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                e
            )
    
    # ===== DICAS AMBIENTAIS =====
    c.execute("SELECT COUNT(*) FROM dicas")
    if c.fetchone()[0] == 0:
        dicas = [
            ("🌱 Compostagem Doméstica", "50% do lixo doméstico pode ser compostado! Faça sua própria composteira com baldes e minhocas californianas.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe EcoPiracicaba"),
            ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros. Reduza para 5 minutos e economize 90 litros por banho!", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas e Baterias", "Uma pilha pode contaminar 20 mil litros de água por até 50 anos. Descarte sempre em pontos de coleta.", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Plante uma Árvore", "Uma árvore adulta absorve até 150kg de CO2 por ano. Plante árvores nativas como ipê e pitanga.", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica"),
            ("🛍️ Sacolas Retornáveis", "Uma sacola plástica leva 400 anos para se decompor. Use sempre sacolas retornáveis nas compras.", "plástico", datetime.now().strftime("%d/%m/%Y"), 0, "WWF"),
            ("🥗 Alimentação Orgânica", "Alimentos orgânicos são mais saudáveis e não contaminam o solo com agrotóxicos.", "alimentação", datetime.now().strftime("%d/%m/%Y"), 0, "Feira Orgânica")
        ]
        for d in dicas:
            c.execute(
                "INSERT INTO dicas (titulo, conteudo, categoria, data_publicacao, likes, autor) VALUES (?, ?, ?, ?, ?, ?)",
                d
            )
    
    # ===== PONTOS DE COLETA EM PIRACICABA =====
    c.execute("SELECT COUNT(*) FROM pontos_coleta")
    if c.fetchone()[0] == 0:
        pontos = [
            ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", 4.5, "Recebe todos os tipos de recicláveis, eletrônicos e óleo de cozinha"),
            ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", 4.8, "Ponto de coleta de pilhas e baterias no piso G1"),
            ("Coopervidros", "R. Treze de Maio, 300 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", 4.2, "Cooperativa especializada em reciclagem de vidros"),
            ("CDI Eletrônicos", "R. do Porto, 234 - Centro", "eletronicos", "Seg-Sex 9h-18h, Sáb 9h-12h", "(19) 3433-5678", 4.7, "Centro de Descarte de Eletrônicos - computadores, celulares e pilhas"),
            ("Ecoponto Paulicéia", "R. Javari, 150 - Paulicéia", "geral", "Ter-Sáb 8h-16h", "(19) 3403-2200", 4.3, "Ecoponto completo com coleta de óleo e recicláveis"),
            ("Unimed Sede", "R. Voluntários, 450 - Centro", "pilhas", "Seg-Sex 7h-19h", "(19) 3432-9000", 4.6, "Coleta de pilhas e baterias na recepção"),
            ("Esalq/USP", "Av. Pádua Dias, 11 - Agronomia", "eletronicos", "Seg-Sex 8h-17h", "(19) 3447-8500", 4.9, "Campus da ESALQ com pontos de coleta de eletrônicos"),
            ("Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "organicos", "Seg-Sex 8h-16h", "(19) 3434-5678", 4.3, "Recebimento de podas e resíduos orgânicos")
        ]
        for p in pontos:
            c.execute(
                "INSERT INTO pontos_coleta (nome, endereco, categoria, horario, telefone, avaliacao, descricao) VALUES (?, ?, ?, ?, ?, ?, ?)",
                p
            )

# Inicializar banco
init_database()

# ========== FUNÇÕES DE PROGRESSO ==========

def get_user_data(user_id):
    """Busca dados completos do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Dados do usuário
    c.execute("SELECT nome, email, cidade, interesses, data_cadastro FROM usuarios WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    # Progresso
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (user_id,))
    progresso = c.fetchone()
    
    # Conquistas
    c.execute("SELECT * FROM conquistas WHERE usuario_id = ? ORDER BY data DESC LIMIT 10", (user_id,))
    conquistas = c.fetchall()
    
    # Comprovantes
    c.execute("SELECT * FROM comprovantes WHERE usuario_id = ? ORDER BY data DESC", (user_id,))
    comprovantes = c.fetchall()
    
    # Inscrições em eventos
    c.execute("SELECT evento_id FROM inscricoes WHERE usuario_id = ?", (user_id,))
    inscricoes = c.fetchall()
    
    # Dicas vistas
    c.execute("SELECT dica_id FROM dicas_vistas WHERE usuario_id = ?", (user_id,))
    dicas_vistas = c.fetchall()
    
    # Visitas a pontos
    c.execute("SELECT ponto_id FROM visitas_pontos WHERE usuario_id = ?", (user_id,))
    visitas = c.fetchall()
    
    # Convites
    c.execute("SELECT codigo FROM convites WHERE usuario_id = ? AND usado = 0", (user_id,))
    convites = c.fetchall()
    
    conn.close()
    
    return user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites

def criar_usuario(nome, email, senha, interesses=""):
    """Cria um novo usuário no banco"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        # Inserir usuário
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, interesses, data_cadastro) VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha, interesses, data_atual)
        )
        
        # Pegar ID do usuário
        user_id = c.lastrowid
        
        # Inserir progresso
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (user_id, 0, "🌱 EcoIniciante", data_atual)
        )
        
        # Gerar código de convite para o usuário
        codigo = hashlib.md5(f"{user_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
        c.execute(
            "INSERT INTO convites (usuario_id, codigo, data_criacao) VALUES (?, ?, ?)",
            (user_id, codigo, data_atual)
        )
        
        conn.commit()
        return True, user_id
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade: {e}")
        return False, None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False, None
    finally:
        conn.close()

def fazer_login(email, senha):
    """Faz login do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    user = c.fetchone()
    
    if user:
        # Atualizar último acesso
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute("UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?", (data_atual, user[0]))
        
        # Atualizar streak
        c.execute("SELECT ultima_atividade FROM progresso WHERE usuario_id = ?", (user[0],))
        resultado = c.fetchone()
        
        if resultado and resultado[0]:
            try:
                ultima = datetime.strptime(resultado[0].split()[0], "%d/%m/%Y")
                hoje = datetime.now()
                
                if (hoje - ultima).days == 1:
                    c.execute("UPDATE progresso SET streak_dias = streak_dias + 1 WHERE usuario_id = ?", (user[0],))
                elif (hoje - ultima).days > 1:
                    c.execute("UPDATE progresso SET streak_dias = 1 WHERE usuario_id = ?", (user[0],))
            except:
                pass
        
        conn.commit()
    
    conn.close()
    return user

def adicionar_pontos(usuario_id, pontos, descricao, icone="✨", tipo="geral"):
    """Adiciona pontos ao usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Registrar conquista
    c.execute(
        "INSERT INTO conquistas (usuario_id, tipo, pontos, data, descricao, icone) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, tipo, pontos, data_atual, descricao, icone)
    )
    
    # Atualizar progresso
    c.execute("SELECT total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        novos_pontos = pontos_atuais + pontos
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, data_atual, usuario_id)
        )
    
    conn.commit()
    conn.close()
    return True

def salvar_comprovante(usuario_id, tipo, descricao, imagem_bytes, pontos):
    """Salva um comprovante de ação (foto)"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    c.execute(
        "INSERT INTO comprovantes (usuario_id, tipo, descricao, imagem, pontos_ganhos, data) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, tipo, descricao, imagem_bytes, pontos, data_atual)
    )
    
    conn.commit()
    conn.close()

def get_ranking():
    """Busca ranking de usuários"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT u.nome, p.total_pontos, p.nivel
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        ORDER BY p.total_pontos DESC
        LIMIT 20
    """)
    
    ranking = c.fetchall()
    conn.close()
    
    return ranking

def inscrever_evento(usuario_id, evento_id):
    """Inscreve usuário em um evento"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute(
            "INSERT INTO inscricoes (usuario_id, evento_id, data_inscricao) VALUES (?, ?, ?)",
            (usuario_id, evento_id, data_atual)
        )
        c.execute("UPDATE eventos SET inscritos = inscritos + 1 WHERE id = ?", (evento_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_eventos_destaque(text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra eventos em destaque na página inicial"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY data LIMIT 6")
    eventos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h1 style='text-align: center; color: {text_color}; margin-bottom: 30px;'>🌿 EcoPiracicaba 2026</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: {secondary_text}; margin-bottom: 40px;'>Eventos em Piracicaba</h2>", unsafe_allow_html=True)
    
    # Layout em grid de 2 colunas
    col1, col2 = st.columns(2)
    
    for i, evento in enumerate(eventos):
        with col1 if i % 2 == 0 else col2:
            # Calcular disponibilidade
            vagas_text = f"{evento[8]}/{evento[7]}" if evento[7] > 0 else "Sem limite"
            disponibilidade = (evento[8] / evento[7] * 100) if evento[7] > 0 else 0
            
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid {icon_color}; border: 1px solid {border_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div style='flex: 1;'>
                        <span style='background: {icon_color}; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px;'>{evento[6].upper()}</span>
                        <h3 style='color: {text_color}; margin: 10px 0 5px 0;'>{evento[1]}</h3>
                        <p style='color: {text_color}; margin: 5px 0; font-size: 14px;'>{evento[2][:100]}...</p>
                        <p style='margin: 5px 0;'><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
                        <p style='margin: 5px 0;'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
                        <p style='margin: 5px 0;'><i class='fas fa-building' style='color: {icon_color};'></i> {evento[9]}</p>
                    </div>
                    <div style='text-align: right; min-width: 120px;'>
                        <p style='color: {secondary_text};'><strong>{evento[8]}/{evento[7] if evento[7] > 0 else '∞'}</strong> inscritos</p>
                        <div style='height: 6px; background: {border_color}; border-radius: 3px; margin: 10px 0;'>
                            <div style='height: 100%; width: {disponibilidade}%; background: {icon_color}; border-radius: 3px;'></div>
                        </div>
                        <p style='color: {icon_color}; font-size: 12px;'>{vagas_text}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_perfil_completo(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra perfil completo com estatísticas"""
    user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites = get_user_data(usuario_id)
    
    if not user or not progresso:
        st.error("Erro ao carregar perfil")
        return
    
    nome, email, cidade, interesses, data_cadastro = user
    
    # Dados do progresso
    pontos = progresso[1] if len(progresso) > 1 else 0
    nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
    eventos = progresso[3] if len(progresso) > 3 else 0
    dicas = progresso[4] if len(progresso) > 4 else 0
    pontos_visitados = progresso[5] if len(progresso) > 5 else 0
    kg = progresso[6] if len(progresso) > 6 else 0
    arvores = progresso[7] if len(progresso) > 7 else 0
    amigos = progresso[8] if len(progresso) > 8 else 0
    streak = progresso[9] if len(progresso) > 9 else 0
    
    proximo = get_proximo_nivel(pontos)
    
    st.markdown(f"<h2 style='color: {text_color};'>👤 Meu Perfil</h2>", unsafe_allow_html=True)
    
    # Informações básicas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Nome:** {nome}")
        st.markdown(f"**Email:** {email}")
    with col2:
        st.markdown(f"**Cidade:** {cidade or 'Piracicaba'}")
        st.markdown(f"**Membro desde:** {data_cadastro}")
    
    if interesses:
        st.markdown(f"**Interesses:** {interesses.replace(',', ', ')}")
    
    st.markdown("---")
    
    # Cards principais
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
            <p style='color: {text_color};'>{proximo} para próximo nível</p>
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
            <h3 style='color: {text_color};'>🏆 Conquistas</h3>
            <h1 style='color: {icon_color}; font-size: 48px;'>{len(conquistas)}</h1>
            <p style='color: {text_color};'>conquistas</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Estatísticas detalhadas
    st.markdown(f"<h3 style='color: {text_color};'>📊 Estatísticas Detalhadas</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📅 Eventos</h4>
            <h2 style='color: {icon_color};'>{eventos}</h2>
            <small>{len(inscricoes)} inscrições</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>💡 Dicas</h4>
            <h2 style='color: {icon_color};'>{dicas}</h2>
            <small>{len(dicas_vistas)} lidas</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📍 Visitas</h4>
            <h2 style='color: {icon_color};'>{pontos_visitados}</h2>
            <small>{len(visitas)} pontos</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>♻️ Kg</h4>
            <h2 style='color: {icon_color};'>{kg}</h2>
            <p>reciclados</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Conquistas recentes
    if conquistas:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Conquistas Recentes</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, conquista in enumerate(conquistas[:6]):
            with cols[i % 3]:
                icone = conquista[6] if len(conquista) > 6 else '✨'
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid {border_color};'>
                    <span style='font-size: 30px;'>{icone}</span>
                    <h4 style='color: {text_color}; font-size: 14px;'>{conquista[5][:30]}</h4>
                    <p style='color: {text_color};'><small>{conquista[4][:10] if conquista[4] else ''}</small></p>
                    <span style='color: {icon_color};'>+{conquista[3]} pts</span>
                </div>
                """, unsafe_allow_html=True)

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    """Página de desafios com comprovação por foto"""
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios Ambientais</h2>", unsafe_allow_html=True)
    
    # Progresso do usuário
    user, progresso, conquistas, _, _, _, _, _ = get_user_data(usuario_id)
    
    if progresso and len(progresso) > 1:
        pontos = progresso[1]
    else:
        pontos = 0
    
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Seus Pontos</h3>
        <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
            <div><span style='font-size: 36px; color: gold;'>🏆</span><br>{pontos} pts</div>
            <div><span style='font-size: 36px; color: {icon_color};'>{len(conquistas)}</span><br>conquistas</div>
        </div>
        <div style='height: 8px; background: {border_color}; border-radius: 4px; margin: 10px 0;'>
            <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
        </div>
        <p style='color: {text_color};'>Continue completando desafios!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lista de desafios
    st.markdown(f"<h3 style='color: {text_color};'>📋 Desafios Disponíveis</h3>", unsafe_allow_html=True)
    
    for desafio in DESAFIOS_LISTA:
        with st.container():
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
                if st.button(f"📸 Comprovar", key=f"btn_{desafio['id']}"):
                    st.session_state['desafio_atual'] = desafio
                    st.session_state['mostrar_upload'] = True
                    st.rerun()
    
    # Modal de upload de foto
    if st.session_state.get('mostrar_upload', False):
        desafio = st.session_state['desafio_atual']
        
        st.markdown("---")
        st.markdown(f"### 📸 Comprovar: {desafio['titulo']}")
        
        uploaded_file = st.file_uploader(
            "Tire uma foto ou envie um comprovante",
            type=['jpg', 'jpeg', 'png'],
            key="upload_comprovante"
        )
        
        if uploaded_file is not None:
            # Converter para bytes
            bytes_data = uploaded_file.getvalue()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Sua foto", use_container_width=True)
            
            with col2:
                st.markdown(f"**Desafio:** {desafio['titulo']}")
                st.markdown(f"**Pontos:** +{desafio['pontos']}")
                
                if st.button("✅ Confirmar e ganhar pontos"):
                    # Salvar comprovante
                    salvar_comprovante(
                        usuario_id,
                        desafio['tipo'],
                        f"Completou: {desafio['titulo']}",
                        bytes_data,
                        desafio['pontos']
                    )
                    
                    # Adicionar pontos
                    adicionar_pontos(
                        usuario_id,
                        desafio['pontos'],
                        f"Completou: {desafio['titulo']}",
                        desafio['icone'],
                        desafio['tipo']
                    )
                    
                    st.balloons()
                    st.success(f"Parabéns! Você ganhou {desafio['pontos']} pontos!")
                    
                    # Limpar estado
                    st.session_state['mostrar_upload'] = False
                    st.session_state['desafio_atual'] = None
                    time.sleep(2)
                    st.rerun()
            
            if st.button("❌ Cancelar"):
                st.session_state['mostrar_upload'] = False
                st.session_state['desafio_atual'] = None
                st.rerun()

def mostrar_ranking_completo(text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra ranking completo"""
    ranking = get_ranking()
    
    st.markdown(f"<h2 style='color: {text_color};'>🏆 Ranking EcoCidadãos</h2>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
    # Destaque para o top 3
    for i, (nome, pontos, nivel) in enumerate(ranking[:3]):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        cor_medalha = "#ffd700" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32"
        
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 10px; border: 2px solid {cor_medalha};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <span style='font-size: 40px;'>{medalha}</span>
                    <div>
                        <h3 style='color: {text_color}; margin: 0;'>{nome}</h3>
                        <span style='color: {secondary_text};'>{nivel}</span>
                    </div>
                </div>
                <div style='text-align: right;'>
                    <span style='color: {icon_color}; font-size: 24px;'>{pontos} pts</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Restante do ranking
    for i, (nome, pontos, nivel) in enumerate(ranking[3:], start=4):
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 12px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='font-size: 16px; font-weight: bold;'>{i}º</span>
                    <strong style='color: {text_color}; margin-left: 10px;'>{nome}</strong>
                    <span style='color: {secondary_text}; margin-left: 10px;'>{nivel}</span>
                </div>
                <div>
                    <span style='color: {icon_color};'>{pontos} pts</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_dicas_completas(text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra dicas ambientais"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dicas ORDER BY likes DESC")
    dicas = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>💡 Dicas Ambientais</h2>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, dica in enumerate(dicas):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 6px solid {icon_color}; border: 1px solid {border_color};'>
                <h4 style='color: {text_color}; margin-top: 0;'>{dica[1]}</h4>
                <p style='color: {text_color}; font-size: 14px;'>{dica[2]}</p>
                <div style='display: flex; justify-content: space-between; margin-top: 10px;'>
                    <span style='color: {secondary_text}; font-size: 12px;'>Categoria: {dica[3]}</span>
                    <span style='color: {icon_color};'>👍 {dica[5]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_pontos_completos(text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra pontos de coleta"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pontos_coleta ORDER BY avaliacao DESC")
    pontos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta</h2>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, ponto in enumerate(pontos):
        with cols[i % 2]:
            estrelas = "★" * int(ponto[6]) + "☆" * (5 - int(ponto[6]))
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <h4 style='color: {text_color}; margin: 0 0 5px 0;'>{ponto[1]}</h4>
                        <p style='margin: 3px 0;'><i class='fas fa-map-pin' style='color: {icon_color};'></i> {ponto[2]}</p>
                        <p style='margin: 3px 0;'><i class='fas fa-clock' style='color: {icon_color};'></i> {ponto[4]}</p>
                        <p style='margin: 3px 0;'><i class='fas fa-phone' style='color: {icon_color};'></i> {ponto[5]}</p>
                        <p style='margin: 5px 0; font-size: 12px; color: {secondary_text};'>{ponto[7]}</p>
                    </div>
                    <div style='text-align: center;'>
                        <div style='color: gold; font-size: 18px;'>{estrelas}</div>
                        <p style='margin: 5px 0;'>{ponto[6]}/5.0</p>
                        <span style='background: {icon_color}; color: white; padding: 3px 8px; border-radius: 50px; font-size: 11px;'>{ponto[3].upper()}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ========== CONFIGURAÇÕES DE TEMA ==========

tema = get_theme()
dispositivo = detectar_dispositivo()

# Sidebar sempre branca
sidebar_bg = "#FFFFFF"
sidebar_text = "#000000"

# Cores do conteúdo principal
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
    
    /* Sidebar fixa branca */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 2px solid {border_color};
    }}
    
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
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
    
    /* Conteúdo principal */
    .main-content {{
        padding: 20px;
    }}
    
    .stMarkdown, p, h1, h2, h3, h4 {{
        color: {text_color} !important;
    }}
    
    .stButton button {{
        background: {icon_color};
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        transition: all 0.3s;
    }}
    
    .stButton button:hover {{
        background: #1a8c5f;
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    div.stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
    }}
    
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {icon_color} !important;
        color: white !important;
    }}
    
    /* Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {border_color};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {icon_color};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #1a8c5f;
    }}
</style>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state['mostrar_upload'] = False
    st.session_state['desafio_atual'] = None

# Sidebar de login - SEMPRE VISÍVEL
with st.sidebar:
    st.markdown(f"<h2 style='color: {sidebar_text}; text-align: center;'>🌿 EcoPiracicaba</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {sidebar_text}; text-align: center;'>Sustentabilidade em ação</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.usuario_logado is None:
        st.markdown(f"<h3 style='color: {sidebar_text};'>🔐 Login</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user = fazer_login(email, senha)
                if user:
                    st.session_state.usuario_logado = {
                        'id': user[0],
                        'nome': user[1]
                    }
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos")
        
        st.markdown("---")
        st.markdown(f"<h3 style='color: {sidebar_text};'>🆕 Cadastro</h3>", unsafe_allow_html=True)
        
        with st.form("cadastro_form"):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            confirmar_senha = st.text_input("Confirmar senha", type="password")
            interesses = st.multiselect("Interesses", 
                ["Sustentabilidade", "Reciclagem", "Eventos", "Voluntariado", "Compostagem", "Mobilidade"])
            
            if st.form_submit_button("Criar conta", use_container_width=True):
                if not nome:
                    st.error("Nome é obrigatório!")
                elif not validar_email(email):
                    st.error("E-mail inválido!")
                elif len(senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                elif senha != confirmar_senha:
                    st.error("As senhas não coincidem!")
                else:
                    sucesso, user_id = criar_usuario(
                        nome, email, senha, ",".join(interesses) if interesses else ""
                    )
                    if sucesso:
                        st.success("Conta criada com sucesso! Faça login.")
                    else:
                        st.error("Este e-mail já está cadastrado!")
    else:
        # Sidebar do usuário logado
        user, progresso, conquistas, _, _, _, _, convites = get_user_data(st.session_state.usuario_logado['id'])
        
        if progresso and len(progresso) > 1:
            pontos = progresso[1]
            nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
            streak = progresso[9] if len(progresso) > 9 else 0
        else:
            pontos = 0
            nivel = "🌱 EcoIniciante"
            streak = 0
        
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #f5f5f5; border-radius: 10px;'>
            <h3 style='color: {sidebar_text};'>{st.session_state.usuario_logado['nome']}</h3>
            <h4 style='color: {icon_color};'>{nivel}</h4>
            <h2 style='color: {icon_color};'>{pontos} pts</h2>
            <div style='height: 8px; background: #cccccc; border-radius: 4px; margin: 10px 0;'>
                <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
            </div>
            <div style='display: flex; justify-content: space-around; margin-top: 10px;'>
                <div><span style='color: #ff9800;'>🔥 {streak}</span><br><small>dias</small></div>
                <div><span style='color: {icon_color};'>🏅 {len(conquistas)}</span><br><small>conquistas</small></div>
                <div><span style='color: gold;'>🔗 {len(convites)}</span><br><small>convites</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

# Conteúdo principal
if st.session_state.usuario_logado is None:
    # Página inicial com eventos em destaque
    mostrar_eventos_destaque(text_color, card_bg, icon_color, border_color, secondary_text)
    
    # Rodapé com informações
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <i class='fas fa-calendar-alt' style='font-size: 30px; color: {icon_color};'></i>
            <h4 style='color: {text_color};'>Eventos 2026</h4>
            <p style='color: {secondary_text};'>Acompanhe todos os eventos sustentáveis de Piracicaba</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <i class='fas fa-map-marker-alt' style='font-size: 30px; color: {icon_color};'></i>
            <h4 style='color: {text_color};'>Pontos de Coleta</h4>
            <p style='color: {secondary_text};'>Encontre onde descartar cada tipo de resíduo</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <i class='fas fa-leaf' style='font-size: 30px; color: {icon_color};'></i>
            <h4 style='color: {text_color};'>Dicas Ambientais</h4>
            <p style='color: {secondary_text};'>Aprenda a viver de forma mais sustentável</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Usuário logado - mostrar conteúdo completo
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Desafios", "👤 Perfil", "🏆 Ranking", "📅 Eventos", "📍 Pontos"])
    
    with tab1:
        mostrar_pagina_desafios(
            st.session_state.usuario_logado['id'],
            text_color, card_bg, icon_color, border_color, secondary_text
        )
    
    with tab2:
        mostrar_perfil_completo(
            st.session_state.usuario_logado['id'],
            text_color, card_bg, icon_color, border_color, secondary_text
        )
    
    with tab3:
        mostrar_ranking_completo(text_color, card_bg, icon_color, border_color, secondary_text)
    
    with tab4:
        # Para usuários logados, mostrar eventos com opção de inscrição
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT * FROM eventos ORDER BY data")
        eventos = c.fetchall()
        conn.close()
        
        st.markdown(f"<h2 style='color: {text_color};'>📅 Eventos 2026</h2>", unsafe_allow_html=True)
        
        for evento in eventos:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color};'>
                    <h4>{evento[1]}</h4>
                    <p>{evento[2]}</p>
                    <p><i class='fas fa-calendar'></i> {evento[3]} às {evento[4]}</p>
                    <p><i class='fas fa-map-marker-alt'></i> {evento[5]}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if evento[7] == 0 or evento[8] < evento[7]:
                    if st.button(f"📝 Inscrever-se", key=f"insc_{evento[0]}"):
                        if inscrever_evento(st.session_state.usuario_logado['id'], evento[0]):
                            st.success("Inscrição realizada!")
                            st.rerun()
                        else:
                            st.warning("Você já está inscrito neste evento.")
                else:
                    st.info("Esgotado")
    
    with tab5:
        mostrar_pontos_completos(text_color, card_bg, icon_color, border_color, secondary_text)
