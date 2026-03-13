import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import hashlib
import time
import os
from PIL import Image
import io

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA
st.set_page_config(
    page_title="EcoPiracicaba 2026 - Sustentabilidade em Ação",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== ESTILO PROFISSIONAL ==========

def aplicar_estilo_profissional():
    """Aplica CSS profissional ao app"""
    st.markdown("""
    <style>
        /* Importando fontes profissionais */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Reset e estilos base */
        * {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Fundo profissional com gradiente */
        .stApp {
            background: linear-gradient(135deg, #0a2e1f 0%, #1a4a3a 100%);
        }
        
        /* Cards profissionais */
        .card {
            background: rgba(26, 51, 41, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(139, 195, 74, 0.3);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            color: white;
            margin-bottom: 20px;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px -12px rgba(139, 195, 74, 0.4);
            border-color: #8bc34a;
        }
        
        /* Títulos profissionais */
        .titulo-principal {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #8bc34a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .subtitulo {
            color: #8bc34a;
            font-size: 18px;
            text-align: center;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }
        
        .titulo-secao {
            color: white;
            font-size: 28px;
            font-weight: 600;
            margin: 30px 0 25px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #8bc34a;
        }
        
        /* Badges e tags */
        .badge {
            display: inline-block;
            padding: 6px 15px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: white;
            margin: 2px;
        }
        
        .badge-verde {
            background: linear-gradient(135deg, #8bc34a, #4caf50);
        }
        
        .badge-azul {
            background: linear-gradient(135deg, #2196f3, #1976d2);
        }
        
        .badge-laranja {
            background: linear-gradient(135deg, #ff9800, #f57c00);
        }
        
        /* Estatísticas */
        .stat-card {
            background: rgba(26, 51, 41, 0.9);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(139, 195, 74, 0.3);
            margin-bottom: 20px;
        }
        
        .stat-numero {
            color: #8bc34a;
            font-size: 48px;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #e0e0e0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Progresso */
        .progresso-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            height: 10px;
            margin: 15px 0;
            width: 100%;
        }
        
        .progresso-barra {
            background: linear-gradient(90deg, #8bc34a, #4caf50);
            border-radius: 10px;
            height: 100%;
            transition: width 0.5s ease;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {
            background-color: rgba(26, 51, 41, 0.9) !important;
            color: white !important;
            border: 2px solid rgba(139, 195, 74, 0.3) !important;
            border-radius: 12px !important;
            padding: 12px !important;
            font-size: 16px !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #8bc34a !important;
            box-shadow: 0 0 0 3px rgba(139, 195, 74, 0.2) !important;
        }
        
        .stTextInput label, .stTextArea label, .stSelectbox label {
            color: white !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin-bottom: 5px !important;
        }
        
        /* Botões */
        .stButton button {
            background: linear-gradient(135deg, #8bc34a, #4caf50) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            width: 100%;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(139, 195, 74, 0.3) !important;
        }
        
        .stButton button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
            border-bottom: 2px solid rgba(139, 195, 74, 0.3);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(26, 51, 41, 0.9);
            border-radius: 12px 12px 0 0 !important;
            padding: 12px 24px !important;
            color: white !important;
            font-weight: 500;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8bc34a, #4caf50) !important;
            color: white !important;
        }
        
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1a3329;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #8bc34a, #4caf50);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4caf50, #2e7d32);
        }
        
        /* Alertas */
        .stAlert {
            background-color: rgba(26, 51, 41, 0.95) !important;
            color: white !important;
            border: 2px solid #8bc34a !important;
            border-radius: 12px !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: rgba(26, 51, 41, 0.95) !important;
            color: white !important;
            border: 2px solid rgba(139, 195, 74, 0.3) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }
        
        /* Grid de cards */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px 0;
        }
        
        /* Animações */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fadeIn {
            animation: fadeIn 0.6s ease forwards;
        }
        
        /* Divisores */
        .divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #8bc34a, transparent);
            margin: 30px 0;
        }
        
        /* Mensagens de sucesso/erro */
        .success-message {
            background: linear-gradient(135deg, #2e7d32, #1b5e20);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            margin: 10px 0;
            border-left: 4px solid #8bc34a;
        }
        
        .error-message {
            background: linear-gradient(135deg, #c62828, #b71c1c);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            margin: 10px 0;
            border-left: 4px solid #ff5252;
        }
        
        /* Ícones */
        .icone {
            font-size: 24px;
            margin-right: 10px;
            color: #8bc34a;
        }
        
        /* Tooltips */
        [data-tooltip] {
            position: relative;
            cursor: help;
        }
        
        [data-tooltip]:before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 8px 12px;
            background: #1a3329;
            color: white;
            border-radius: 8px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            border: 1px solid #8bc34a;
            z-index: 1000;
        }
        
        [data-tooltip]:hover:before {
            opacity: 1;
        }
        
        /* Sidebar */
        .css-1d391kg, .css-12oz5g7 {
            background: linear-gradient(135deg, #0a2e1f 0%, #1a4a3a 100%) !important;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .titulo-principal {
                font-size: 32px;
            }
            
            .stat-numero {
                font-size: 36px;
            }
            
            .grid-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
    
    <!-- Font Awesome para ícones -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """, unsafe_allow_html=True)

# Aplicar estilo
aplicar_estilo_profissional()

# ========== FUNÇÕES BÁSICAS ==========

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== FUNÇÕES DE NÍVEL ==========

def get_nivel(pontos):
    if pontos < 100:
        return 1, "🌱 EcoIniciante"
    elif pontos < 500:
        return 2, "🌿 EcoAmigo"
    elif pontos < 1000:
        return 3, "🍃 EcoGuardião"
    elif pontos < 5000:
        return 4, "🌳 EcoMestre"
    else:
        return 5, "🏆 EcoHerói"

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
        "tipo": "reciclagem",
        "dica_validacao": "Tire foto dos materiais na balança com peso visível",
        "limite_diario": 1,
        "dias_entre_validacoes": 7
    },
    {
        "id": 2,
        "titulo": "📅 Participar de Evento",
        "descricao": "Participe de 1 evento ambiental",
        "pontos": 150,
        "icone": "📅",
        "tipo": "evento",
        "dica_validacao": "Tire foto no local do evento com a data visível",
        "limite_diario": 1,
        "dias_entre_validacoes": 1
    },
    {
        "id": 3,
        "titulo": "🌳 Plantar Árvore",
        "descricao": "Plante 1 árvore nativa",
        "pontos": 300,
        "icone": "🌳",
        "tipo": "plantio",
        "dica_validacao": "Tire foto da muda plantada",
        "limite_diario": 1,
        "dias_entre_validacoes": 30
    },
    {
        "id": 4,
        "titulo": "🔋 Descartar Pilhas",
        "descricao": "Descarte 5 pilhas em ponto de coleta",
        "pontos": 100,
        "icone": "🔋",
        "tipo": "pilhas",
        "dica_validacao": "Tire foto das pilhas no ponto de coleta",
        "limite_diario": 1,
        "dias_entre_validacoes": 1
    },
    {
        "id": 5,
        "titulo": "🚲 Usar Bike",
        "descricao": "Use bicicleta em vez de carro 3 vezes",
        "pontos": 180,
        "icone": "🚲",
        "tipo": "mobilidade",
        "dica_validacao": "Tire foto do aplicativo de tracking de bike",
        "limite_diario": 1,
        "dias_entre_validacoes": 1
    },
    {
        "id": 6,
        "titulo": "🥫 Doar Alimentos",
        "descricao": "Doe 5kg de alimentos não perecíveis",
        "pontos": 250,
        "icone": "🥫",
        "tipo": "doacao",
        "dica_validacao": "Tire foto dos alimentos no local de doação",
        "limite_diario": 1,
        "dias_entre_validacoes": 15
    },
    {
        "id": 7,
        "titulo": "👕 Doar Roupas",
        "descricao": "Doe 10 peças de roupa",
        "pontos": 200,
        "icone": "👕",
        "tipo": "doacao_roupas",
        "dica_validacao": "Tire foto das roupas no ponto de coleta",
        "limite_diario": 1,
        "dias_entre_validacoes": 15
    }
]

# ========== INICIALIZAÇÃO DO BANCO DE DADOS ==========

def init_database():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    conn = sqlite3.connect('ecopiracicaba.db', check_same_thread=False)
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            telefone TEXT,
            cidade TEXT DEFAULT 'Piracicaba',
            data_cadastro TIMESTAMP,
            ultimo_acesso TIMESTAMP,
            pontos_total INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            streak_dias INTEGER DEFAULT 0,
            banido INTEGER DEFAULT 0
        )
    ''')
    
    # Tabela de progresso
    c.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            pontos_ganhos INTEGER,
            data TIMESTAMP,
            descricao TEXT,
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
            endereco TEXT,
            tipo TEXT,
            vagas INTEGER,
            inscritos INTEGER DEFAULT 0,
            organizador TEXT,
            contato TEXT,
            pontos_evento INTEGER DEFAULT 100,
            destaque INTEGER DEFAULT 0,
            data_criacao TIMESTAMP
        )
    ''')
    
    # Tabela de inscrições
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TIMESTAMP,
            participou INTEGER DEFAULT 0,
            codigo_confirmacao TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (evento_id) REFERENCES eventos (id),
            UNIQUE(usuario_id, evento_id)
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
    
    # Tabela de conquistas
    c.execute('''
        CREATE TABLE IF NOT EXISTS conquistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT,
            descricao TEXT,
            data TIMESTAMP,
            icone TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de notificações
    c.execute('''
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT,
            mensagem TEXT,
            tipo TEXT,
            lida INTEGER DEFAULT 0,
            data_criacao TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    
    # Inserir dados iniciais se necessário
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        dados_iniciais(conn, c)
        conn.commit()
    
    conn.close()
    return conn

def dados_iniciais(conn, c):
    """Insere dados iniciais no banco"""
    data_atual = datetime.now()
    
    # Admin
    senha_hash = hashlib.sha256("eco2026".encode()).hexdigest()
    c.execute(
        "INSERT INTO usuarios (nome, email, senha, data_cadastro, pontos_total, nivel) VALUES (?, ?, ?, ?, ?, ?)",
        ("Administrador", "admin@ecopiracicaba.com", senha_hash, data_atual, 1000, 4)
    )
    
    # Usuários exemplo
    usuarios = [
        ("João Silva", "joao@email.com", "123456", 350),
        ("Maria Santos", "maria@email.com", "123456", 520),
        ("Pedro Oliveira", "pedro@email.com", "123456", 180),
        ("Ana Costa", "ana@email.com", "123456", 780),
        ("Carlos Souza", "carlos@email.com", "123456", 420)
    ]
    
    for nome, email, senha, pontos in usuarios:
        nivel, _ = get_nivel(pontos)
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, pontos_total, nivel) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, email, senha_hash, data_atual, pontos, nivel)
        )
    
    # Eventos
    eventos = [
        ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos, artesanato sustentável e startups verdes. Haverá palestras, oficinas e food trucks.", "15/03/2026", "09:00", "Engenho Central", "Av. Maurice Allain, 454", "feira", 1000, "Prefeitura de Piracicaba", "(19) 3403-1100", 150, data_atual),
        ("♻️ Workshop de Reciclagem", "Aprenda técnicas avançadas de reciclagem em casa. Transforme materiais recicláveis em objetos úteis.", "22/03/2026", "14:00", "SENAI", "Av. Luiz Ralph Benatti, 500", "workshop", 50, "SENAI", "(19) 3412-5000", 150, data_atual),
        ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio com atividades educativas e distribuição de mudas.", "05/04/2026", "08:00", "Rua do Porto", "Rua do Porto - Centro", "mutirão", 200, "SOS Rio Piracicaba", "(19) 99765-4321", 200, data_atual),
    ]
    
    for e in eventos:
        c.execute(
            "INSERT INTO eventos (titulo, descricao, data, hora, local, endereco, tipo, vagas, organizador, contato, pontos_evento, data_criacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            e
        )
    
    # Pontos de coleta
    pontos = [
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", 4.5, "Recebe todos os tipos de recicláveis, eletrônicos e óleo de cozinha"),
        ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", 4.8, "Ponto de coleta de pilhas e baterias no piso G1"),
        ("CDI Eletrônicos", "R. do Porto, 234 - Centro", "eletronicos", "Seg-Sex 9h-18h, Sáb 9h-12h", "(19) 3433-5678", 4.7, "Centro de Descarte de Eletrônicos"),
    ]
    
    for p in pontos:
        c.execute(
            "INSERT INTO pontos_coleta (nome, endereco, categoria, horario, telefone, avaliacao, descricao) VALUES (?, ?, ?, ?, ?, ?, ?)",
            p
        )

# Inicializar banco
init_database()

# ========== FUNÇÕES DE AUTENTICAÇÃO ==========

def fazer_login(email, senha):
    """Faz login do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    c.execute("SELECT id, nome, pontos_total, nivel, streak_dias FROM usuarios WHERE email = ? AND senha = ? AND banido = 0", 
              (email, senha_hash))
    user = c.fetchone()
    
    if user:
        data_atual = datetime.now()
        c.execute("UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?", (data_atual, user[0]))
        
        # Verificar streak
        c.execute("SELECT data FROM progresso WHERE usuario_id = ? ORDER BY data DESC LIMIT 1", (user[0],))
        ultima_atividade = c.fetchone()
        
        if ultima_atividade:
            try:
                ultima_data = datetime.strptime(ultima_atividade[0], "%Y-%m-%d %H:%M:%S.%f")
                if (data_atual.date() - ultima_data.date()).days == 1:
                    c.execute("UPDATE usuarios SET streak_dias = streak_dias + 1 WHERE id = ?", (user[0],))
                elif (data_atual.date() - ultima_data.date()).days > 1:
                    c.execute("UPDATE usuarios SET streak_dias = 1 WHERE id = ?", (user[0],))
            except:
                pass
        
        conn.commit()
        conn.close()
        return user
    else:
        conn.close()
        return None

def criar_usuario(nome, email, senha, telefone=""):
    """Cria um novo usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verificar se email já existe
    c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False, "E-mail já cadastrado!"
    
    data_atual = datetime.now()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, telefone, data_cadastro, pontos_total, nivel, streak_dias) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, email, senha_hash, telefone, data_atual, 0, 1, 0)
        )
        user_id = c.lastrowid
        
        # Criar notificação de boas-vindas
        c.execute(
            "INSERT INTO notificacoes (usuario_id, titulo, mensagem, tipo, data_criacao) VALUES (?, ?, ?, ?, ?)",
            (user_id, "🎉 Bem-vindo ao EcoPiracicaba!", "Comece a participar de eventos e completar desafios para ganhar pontos!", "boas-vindas", data_atual)
        )
        
        conn.commit()
        conn.close()
        return True, "Conta criada com sucesso!"
    except Exception as e:
        conn.close()
        return False, f"Erro ao criar conta: {str(e)}"

# ========== FUNÇÕES DE DADOS DO USUÁRIO ==========

def get_user_stats(user_id):
    """Retorna estatísticas do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Pontos totais e nível
    c.execute("SELECT pontos_total, nivel, streak_dias FROM usuarios WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    
    # Eventos participados
    c.execute("SELECT COUNT(*) FROM inscricoes WHERE usuario_id = ? AND participou = 1", (user_id,))
    eventos_participados = c.fetchone()[0]
    
    # Progresso registrado
    c.execute("SELECT COUNT(*) FROM progresso WHERE usuario_id = ?", (user_id,))
    total_atividades = c.fetchone()[0]
    
    pontos = user_data[0] if user_data else 0
    nivel_atual = user_data[1] if user_data else 1
    streak = user_data[2] if user_data else 0
    
    # Pontos para próximo nível
    if nivel_atual == 1:
        pontos_proximo = 100 - pontos
        progresso = (pontos / 100) * 100
    elif nivel_atual == 2:
        pontos_proximo = 500 - pontos
        progresso = (pontos / 500) * 100
    elif nivel_atual == 3:
        pontos_proximo = 1000 - pontos
        progresso = (pontos / 1000) * 100
    elif nivel_atual == 4:
        pontos_proximo = 5000 - pontos
        progresso = (pontos / 5000) * 100
    else:
        pontos_proximo = 0
        progresso = 100
    
    conn.close()
    
    return {
        'pontos': pontos,
        'nivel': nivel_atual,
        'streak': streak,
        'eventos': eventos_participados,
        'atividades': total_atividades,
        'progresso': min(100, progresso),
        'pontos_proximo': max(0, pontos_proximo)
    }

def get_ranking():
    """Retorna ranking de usuários"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT nome, pontos_total, nivel, streak_dias 
        FROM usuarios 
        WHERE banido = 0 
        ORDER BY pontos_total DESC 
        LIMIT 20
    """)
    
    ranking = c.fetchall()
    conn.close()
    return ranking

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_header():
    """Mostra o header do aplicativo"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 class='titulo-principal'>🌿 EcoPiracicaba 2026</h1>
            <p class='subtitulo'>Transformando Piracicaba em uma cidade mais sustentável</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_login():
    """Mostra tela de login"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class='card' style='padding: 40px;'>
            <h2 style='color: white; text-align: center; margin-bottom: 30px;'>🔐 Acesse sua conta</h2>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                user = fazer_login(email, senha)
                if user:
                    st.session_state['usuario_logado'] = {
                        'id': user[0],
                        'nome': user[1],
                        'pontos': user[2],
                        'nivel': user[3]
                    }
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card' style='padding: 40px;'>
            <h3 style='color: white; margin-bottom: 20px;'>✨ Por que participar?</h3>
            <ul style='color: #e0e0e0; list-style: none; padding: 0;'>
                <li style='margin: 15px 0;'><i class='fas fa-check-circle' style='color: #8bc34a;'></i> Ganhe pontos e suba de nível</li>
                <li style='margin: 15px 0;'><i class='fas fa-check-circle' style='color: #8bc34a;'></i> Participe de eventos exclusivos</li>
                <li style='margin: 15px 0;'><i class='fas fa-check-circle' style='color: #8bc34a;'></i> Conheça pessoas engajadas</li>
                <li style='margin: 15px 0;'><i class='fas fa-check-circle' style='color: #8bc34a;'></i> Receba certificados de participação</li>
            </ul>
            <div style='text-align: center; margin-top: 30px;'>
                <i class='fas fa-leaf' style='font-size: 48px; color: #8bc34a;'></i>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='card' style='padding: 30px; text-align: center;'>
            <h3 style='color: white;'>Ainda não tem conta?</h3>
            <p style='color: #e0e0e0; margin: 20px 0;'>Junte-se a nós e comece a fazer a diferença!</p>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Criar conta gratuita", use_container_width=True):
            st.session_state['pagina'] = 'cadastro'
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_cadastro():
    """Mostra tela de cadastro"""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div class='card' style='padding: 40px;'>
            <h2 style='color: white; text-align: center; margin-bottom: 30px;'>📝 Criar nova conta</h2>
        """, unsafe_allow_html=True)
        
        with st.form("cadastro_form"):
            nome = st.text_input("Nome completo *", placeholder="João Silva")
            email = st.text_input("E-mail *", placeholder="joao@email.com")
            telefone = st.text_input("Telefone (opcional)", placeholder="(19) 99999-9999")
            senha = st.text_input("Senha *", type="password", placeholder="••••••••")
            confirmar_senha = st.text_input("Confirmar senha *", type="password", placeholder="••••••••")
            
            st.markdown("<small style='color: #e0e0e0;'>* Campos obrigatórios</small>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Criar conta", use_container_width=True)
            with col_b:
                voltar = st.form_submit_button("Voltar", use_container_width=True)
            
            if submit:
                if not nome or not email or not senha:
                    st.error("Preencha todos os campos obrigatórios!")
                elif not validar_email(email):
                    st.error("E-mail inválido!")
                elif len(senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                elif senha != confirmar_senha:
                    st.error("As senhas não coincidem!")
                else:
                    sucesso, mensagem = criar_usuario(nome, email, senha, telefone)
                    if sucesso:
                        st.success(mensagem)
                        st.balloons()
                        time.sleep(2)
                        st.session_state['pagina'] = 'login'
                        st.rerun()
                    else:
                        st.error(mensagem)
            
            if voltar:
                st.session_state['pagina'] = 'login'
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_dashboard_usuario(user_id):
    """Mostra dashboard do usuário logado"""
    stats = get_user_stats(user_id)
    _, nome_nivel = get_nivel(stats['pontos'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <i class='fas fa-star' style='font-size: 30px; color: #8bc34a;'></i>
            <div class='stat-numero'>{stats['pontos']}</div>
            <div class='stat-label'>Pontos totais</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <i class='fas fa-trophy' style='font-size: 30px; color: #8bc34a;'></i>
            <div class='stat-numero'>Nível {stats['nivel']}</div>
            <div class='stat-label'>{nome_nivel}</div>
            <div class='progresso-container'>
                <div class='progresso-barra' style='width: {stats['progresso']}%;'></div>
            </div>
            <small style='color: #e0e0e0;'>{stats['pontos_proximo']} pts para próximo nível</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <i class='fas fa-fire' style='font-size: 30px; color: #ff9800;'></i>
            <div class='stat-numero'>{stats['streak']}</div>
            <div class='stat-label'>Dias de streak</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <i class='fas fa-calendar-check' style='font-size: 30px; color: #8bc34a;'></i>
            <div class='stat-numero'>{stats['eventos']}</div>
            <div class='stat-label'>Eventos</div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_eventos_destaque():
    """Mostra eventos em destaque"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY data LIMIT 6")
    eventos = c.fetchall()
    conn.close()
    
    st.markdown("<h2 class='titulo-secao'>📅 Próximos Eventos</h2>", unsafe_allow_html=True)
    
    if not eventos:
        st.info("Nenhum evento programado no momento.")
        return
    
    cols = st.columns(3)
    for idx, evento in enumerate(eventos):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class='card animate-fadeIn'>
                <span class='badge badge-verde'>{evento[7].upper()}</span>
                <h3 style='margin: 15px 0 10px 0;'>{evento[1]}</h3>
                <p style='color: #e0e0e0; font-size: 14px;'>{evento[2][:100]}...</p>
                <p><i class='fas fa-calendar' style='color: #8bc34a;'></i> {evento[3]} às {evento[4]}</p>
                <p><i class='fas fa-map-marker-alt' style='color: #8bc34a;'></i> {evento[5]}</p>
                <p><i class='fas fa-users' style='color: #8bc34a;'></i> {evento[8]}/{evento[7]} inscritos</p>
                <div style='margin-top: 15px;'>
                    <span class='badge badge-verde'><i class='fas fa-star'></i> +{evento[11]} pts</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_pontos_coleta():
    """Mostra pontos de coleta"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pontos_coleta ORDER BY categoria")
    pontos = c.fetchall()
    conn.close()
    
    st.markdown("<h2 class='titulo-secao'>📍 Pontos de Coleta</h2>", unsafe_allow_html=True)
    
    # Agrupar por categoria
    categorias = {}
    for ponto in pontos:
        categoria = ponto[3]
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(ponto)
    
    for categoria, pontos_cat in categorias.items():
        with st.expander(f"📌 {categoria.upper()} ({len(pontos_cat)} pontos)"):
            cols = st.columns(2)
            for idx, ponto in enumerate(pontos_cat):
                with cols[idx % 2]:
                    estrelas = "★" * int(ponto[6]) + "☆" * (5 - int(ponto[6]))
                    st.markdown(f"""
                    <div class='card' style='padding: 15px;'>
                        <h4>{ponto[1]}</h4>
                        <p><i class='fas fa-map-pin' style='color: #8bc34a;'></i> {ponto[2]}</p>
                        <p><i class='fas fa-clock' style='color: #8bc34a;'></i> {ponto[4]}</p>
                        <p><i class='fas fa-phone' style='color: #8bc34a;'></i> {ponto[5]}</p>
                        <p style='color: #e0e0e0; font-size: 12px;'>{ponto[7]}</p>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='color: gold;'>{estrelas}</div>
                            <span class='badge badge-verde'>{ponto[6]}/5.0</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def mostrar_ranking():
    """Mostra ranking de usuários"""
    ranking = get_ranking()
    
    st.markdown("<h2 class='titulo-secao'>🏆 Ranking dos EcoCidadãos</h2>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
    # Top 3 em destaque
    col1, col2, col3 = st.columns(3)
    
    for i, (nome, pontos, nivel, streak) in enumerate(ranking[:3]):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        cor_borda = "#ffd700" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32"
        
        col = col1 if i == 0 else col2 if i == 1 else col3
        
        with col:
            st.markdown(f"""
            <div class='card' style='text-align: center; border: 2px solid {cor_borda};'>
                <div style='font-size: 48px;'>{medalha}</div>
                <h3>{nome}</h3>
                <p style='color: #8bc34a;'>Nível {nivel}</p>
                <div style='font-size: 32px; color: #8bc34a;'>{pontos}</div>
                <p>pontos</p>
                <span class='badge badge-azul'><i class='fas fa-fire'></i> {streak} dias</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Restante do ranking
    st.markdown("<br>", unsafe_allow_html=True)
    
    for i, (nome, pontos, nivel, streak) in enumerate(ranking[3:], start=4):
        st.markdown(f"""
        <div class='card' style='padding: 15px; margin-bottom: 10px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='display: flex; align-items: center; gap: 20px;'>
                    <span style='font-size: 20px; font-weight: 700; color: #8bc34a;'>{i}º</span>
                    <div>
                        <strong style='font-size: 16px;'>{nome}</strong>
                        <p style='margin: 0; color: #e0e0e0;'>Nível {nivel}</p>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 20px;'>
                    <span class='badge badge-azul'><i class='fas fa-fire'></i> {streak}</span>
                    <span style='font-size: 18px; color: #8bc34a;'>{pontos} pts</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_desafios():
    """Mostra desafios disponíveis"""
    st.markdown("<h2 class='titulo-secao'>🎯 Desafios Ambientais</h2>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    
    for idx, desafio in enumerate(DESAFIOS_LISTA):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class='card'>
                <div style='display: flex; align-items: center; gap: 20px;'>
                    <div style='font-size: 48px;'>{desafio['icone']}</div>
                    <div>
                        <h3 style='margin: 0;'>{desafio['titulo']}</h3>
                        <p style='color: #e0e0e0; margin: 5px 0;'>{desafio['descricao']}</p>
                        <div style='display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;'>
                            <span class='badge badge-verde'><i class='fas fa-star'></i> +{desafio['pontos']} pts</span>
                            <span class='badge badge-azul' data-tooltip='{desafio['dica_validacao']}'><i class='fas fa-info-circle'></i> Dica</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_perfil(user_id):
    """Mostra perfil do usuário"""
    stats = get_user_stats(user_id)
    _, nome_nivel = get_nivel(stats['pontos'])
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT nome, email, telefone, cidade, data_cadastro FROM usuarios WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        nome, email, telefone, cidade, data_cadastro = user
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>Informações Pessoais</h3>
                <p><i class='fas fa-user'></i> <strong>Nome:</strong> {nome}</p>
                <p><i class='fas fa-envelope'></i> <strong>E-mail:</strong> {email}</p>
                <p><i class='fas fa-phone'></i> <strong>Telefone:</strong> {telefone or 'Não informado'}</p>
                <p><i class='fas fa-map-marker-alt'></i> <strong>Cidade:</strong> {cidade or 'Piracicaba'}</p>
                <p><i class='fas fa-calendar-alt'></i> <strong>Membro desde:</strong> {data_cadastro[:10] if data_cadastro else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3>Progresso</h3>
                <p><i class='fas fa-trophy'></i> <strong>Nível:</strong> {stats['nivel']} - {nome_nivel}</p>
                <p><i class='fas fa-star'></i> <strong>Pontos:</strong> {stats['pontos']}</p>
                <p><i class='fas fa-fire'></i> <strong>Streak:</strong> {stats['streak']} dias</p>
                <p><i class='fas fa-calendar-check'></i> <strong>Eventos:</strong> {stats['eventos']}</p>
                <p><i class='fas fa-chart-line'></i> <strong>Progresso:</strong> {stats['progresso']:.1f}%</p>
                <div class='progresso-container'>
                    <div class='progresso-barra' style='width: {stats['progresso']}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

def main():
    """Função principal do aplicativo"""
    
    # Inicializar session state
    if 'usuario_logado' not in st.session_state:
        st.session_state['usuario_logado'] = None
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'login'
    
    # Header sempre visível
    mostrar_header()
    
    # Roteamento de páginas
    if st.session_state['usuario_logado'] is None:
        # Usuário não logado
        if st.session_state['pagina'] == 'login':
            mostrar_login()
        elif st.session_state['pagina'] == 'cadastro':
            mostrar_cadastro()
        
        # Mostrar eventos e pontos mesmo sem login
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        mostrar_eventos_destaque()
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        mostrar_pontos_coleta()
        
    else:
        # Usuário logado
        user_id = st.session_state.usuario_logado['id']
        
        # Sidebar com menu
        with st.sidebar:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <div style='width: 80px; height: 80px; background: linear-gradient(135deg, #8bc34a, #4caf50); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px;'>
                    <span style='font-size: 40px;'>👤</span>
                </div>
                <h3 style='color: white; margin: 0;'>{st.session_state.usuario_logado['nome']}</h3>
                <p style='color: #8bc34a; margin: 5px 0;'>Nível {st.session_state.usuario_logado['nivel']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            menu = st.radio(
                "Menu",
                ["🏠 Dashboard", "🎯 Desafios", "📅 Eventos", "📍 Pontos de Coleta", "🏆 Ranking", "👤 Perfil"],
                label_visibility="collapsed"
            )
            
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state['usuario_logado'] = None
                st.rerun()
        
        # Conteúdo principal baseado no menu
        if menu == "🏠 Dashboard":
            mostrar_dashboard_usuario(user_id)
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            mostrar_eventos_destaque()
            
        elif menu == "🎯 Desafios":
            mostrar_desafios()
            
        elif menu == "📅 Eventos":
            mostrar_eventos_destaque()
            
        elif menu == "📍 Pontos de Coleta":
            mostrar_pontos_coleta()
            
        elif menu == "🏆 Ranking":
            mostrar_ranking()
            
        elif menu == "👤 Perfil":
            mostrar_perfil(user_id)

if __name__ == "__main__":
    main()
