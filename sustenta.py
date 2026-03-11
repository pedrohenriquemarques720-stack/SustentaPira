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
    page_title="SustentaPira",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto"
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
    
    # Inserir dados iniciais
    dados_iniciais(conn, c)
    
    conn.commit()
    conn.close()

def dados_iniciais(conn, c):
    """Insere dados iniciais no banco"""
    
    # Usuário admin
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@ecopiracicaba.com'")
    if not c.fetchone():
        data_atual = datetime.now().strftime("%d/%m/%Y")
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro, interesses) VALUES (?, ?, ?, ?, ?)",
            ("Administrador", "admin@ecopiracicaba.com", "eco2026", data_atual, "sustentabilidade,reciclagem")
        )
        
        # Criar progresso para admin
        admin_id = c.lastrowid
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (admin_id, 1000, get_nivel(1000), data_atual)
        )
    
    # Eventos 2026
    c.execute("SELECT COUNT(*) FROM eventos")
    if c.fetchone()[0] == 0:
        eventos = [
            ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos e artesanato sustentável", "15/03/2026", "09:00", "Engenho Central", "feira", 1000, "Prefeitura", "(19) 3403-1100"),
            ("♻️ Workshop de Reciclagem", "Aprenda técnicas de reciclagem em casa", "22/03/2026", "14:00", "SENAI", "workshop", 50, "SENAI", "(19) 3412-5000"),
            ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio", "05/04/2026", "08:00", "Rua do Porto", "mutirão", 200, "SOS Rio", "(19) 99765-4321"),
            ("🌿 Palestra: Compostagem", "Como fazer compostagem doméstica", "12/04/2026", "10:00", "Horto Municipal", "palestra", 100, "Horto", "(19) 3434-5678"),
            ("🌍 Dia da Terra", "Celebração com atividades ambientais", "22/04/2026", "09:00", "Parque da Rua do Porto", "evento", 2000, "ONG Planeta", "(19) 99876-5432")
        ]
        for e in eventos:
            c.execute(
                "INSERT INTO eventos (titulo, descricao, data, hora, local, tipo, vagas, organizador, contato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                e
            )
    
    # Dicas ambientais
    c.execute("SELECT COUNT(*) FROM dicas")
    if c.fetchone()[0] == 0:
        dicas = [
            ("🌱 Compostagem", "50% do lixo pode ser compostado", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Equipe Eco"),
            ("💧 Economia de Água", "Banho de 15 min gasta 135L", "água", datetime.now().strftime("%d/%m/%Y"), 0, "Sabesp"),
            ("🔋 Pilhas", "1 pilha contamina 20 mil litros", "resíduos", datetime.now().strftime("%d/%m/%Y"), 0, "Greenpeace"),
            ("🌳 Árvores", "1 árvore absorve 150kg CO2/ano", "natureza", datetime.now().strftime("%d/%m/%Y"), 0, "SOS Mata Atlântica")
        ]
        for d in dicas:
            c.execute(
                "INSERT INTO dicas (titulo, conteudo, categoria, data_publicacao, likes, autor) VALUES (?, ?, ?, ?, ?, ?)",
                d
            )
    
    # Pontos de coleta
    c.execute("SELECT COUNT(*) FROM pontos_coleta")
    if c.fetchone()[0] == 0:
        pontos = [
            ("Ecoponto Centro", "Av. Rui Barbosa, 800", "geral", "Seg-Sex 8h-17h", "(19) 3403-1100", 4.5, "Todos os recicláveis"),
            ("Shopping Piracicaba", "Av. Limeira, 700", "pilhas", "Seg-Sáb 10h-22h", "(19) 3432-4545", 4.8, "Pilhas e baterias"),
            ("Coopervidros", "R. Treze de Maio, 300", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", 4.2, "Apenas vidros")
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
    
    conn.close()
    
    return user, progresso, conquistas, comprovantes

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
        
        # Inicializar progresso
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (user_id, 0, "🌱 EcoIniciante", data_atual)
        )
        
        conn.commit()
        return True, user_id
    except sqlite3.IntegrityError:
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
    c.execute("SELECT total_pontos, desafios_completados FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        desafios_atuais = resultado[1] if resultado[1] else 0
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
        SELECT u.nome, p.total_pontos, p.nivel, p.desafios_completados
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        ORDER BY p.total_pontos DESC
        LIMIT 20
    """)
    ranking = c.fetchall()
    conn.close()
    
    return ranking

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_perfil_completo(usuario_id, text_color, card_bg, icon_color, border_color):
    """Mostra perfil completo com estatísticas"""
    user, progresso, conquistas, comprovantes = get_user_data(usuario_id)
    
    if not user or not progresso:
        st.error("Erro ao carregar perfil")
        return
    
    nome, email, cidade, interesses, data_cadastro = user
    
    # Dados do progresso
    pontos = progresso[1]
    nivel = progresso[2]
    eventos = progresso[3]
    dicas = progresso[4]
    visitas = progresso[5]
    kg = progresso[6]
    arvores = progresso[7]
    amigos = progresso[8]
    streak = progresso[9]
    desafios = progresso[11] if len(progresso) > 11 else 0
    
    proximo = get_proximo_nivel(pontos)
    
    st.markdown(f"<h2 style='color: {text_color};'>👤 Meu Perfil</h2>", unsafe_allow_html=True)
    
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
            <h3 style='color: {text_color};'>🏆 Desafios</h3>
            <h1 style='color: {icon_color}; font-size: 48px;'>{desafios}</h1>
            <p style='color: {text_color};'>completados</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Estatísticas detalhadas
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
    
    # Conquistas recentes
    if conquistas:
        st.markdown(f"<h3 style='color: {text_color};'>🏅 Conquistas Recentes</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, conquista in enumerate(conquistas[:3]):
            with cols[i]:
                icone = conquista[6] if len(conquista) > 6 else '✨'
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid {border_color};'>
                    <span style='font-size: 30px;'>{icone}</span>
                    <h4 style='color: {text_color};'>{conquista[5]}</h4>
                    <p style='color: {text_color};'><small>{conquista[4][:10]}</small></p>
                    <span style='color: {icon_color};'>+{conquista[3]} pts</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Histórico de comprovantes
    if comprovantes:
        with st.expander("📸 Histórico de Comprovantes"):
            for comp in comprovantes[:5]:
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
                    <strong>{comp[2]}</strong> - {comp[3]}<br>
                    <small>{comp[6]} | {comp[5]} pontos</small>
                </div>
                """, unsafe_allow_html=True)

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color):
    """Página de desafios com comprovação por foto"""
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios Ambientais</h2>", unsafe_allow_html=True)
    
    # Progresso do usuário
    user, progresso, _, _ = get_user_data(usuario_id)
    
    if progresso:
        pontos = progresso[1]
        desafios_feitos = progresso[11] if len(progresso) > 11 else 0
    else:
        pontos = 0
        desafios_feitos = 0
    
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Seu Progresso</h3>
        <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
            <div><span style='font-size: 36px; color: {icon_color};'>{desafios_feitos}</span><br>desafios</div>
            <div><span style='font-size: 36px; color: gold;'>🏆</span><br>{pontos} pts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Lista de desafios
    st.markdown(f"<h3 style='color: {text_color};'>📋 Desafios Disponíveis</h3>", unsafe_allow_html=True)
    
    for desafio in DESAFIOS_LISTA:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
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
            type=['jpg', 'jpeg', 'png', 'heic'],
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
                    
                    # Registrar atividade específica
                    if desafio['tipo'] == 'reciclagem':
                        registrar_atividade(usuario_id, 'reciclagem', 10)
                    elif desafio['tipo'] == 'evento':
                        registrar_atividade(usuario_id, 'evento', 1)
                    elif desafio['tipo'] == 'plantio':
                        registrar_atividade(usuario_id, 'arvore', 1)
                    
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

def registrar_atividade(usuario_id, tipo, valor):
    """Registra atividades no progresso"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    if tipo == "evento":
        c.execute("UPDATE progresso SET eventos_participados = eventos_participados + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "reciclagem":
        c.execute("UPDATE progresso SET kg_reciclados = kg_reciclados + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "arvore":
        c.execute("UPDATE progresso SET arvores_plantadas = arvores_plantadas + ? WHERE usuario_id = ?", (valor, usuario_id))
    elif tipo == "desafio":
        c.execute("UPDATE progresso SET desafios_completados = desafios_completados + 1 WHERE usuario_id = ?", (usuario_id,))
    
    conn.commit()
    conn.close()

def mostrar_ranking_completo(text_color, card_bg, icon_color, border_color):
    """Mostra ranking completo"""
    ranking = get_ranking()
    
    st.markdown(f"<h2 style='color: {text_color};'>🏆 Ranking EcoCidadãos</h2>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
    for i, (nome, pontos, nivel, desafios) in enumerate(ranking):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}º"
        
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 8px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='font-size: 20px;'>{medalha}</span>
                    <strong style='color: {text_color}; margin-left: 10px;'>{nome}</strong>
                    <span style='color: {secondary_text}; margin-left: 10px;'>{nivel}</span>
                </div>
                <div>
                    <span style='color: {icon_color}; font-size: 18px;'>{pontos} pts</span>
                    <span style='color: #ff9800; margin-left: 15px;'>🎯 {desafios}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_dicas_completas(text_color, card_bg, icon_color, border_color):
    """Mostra dicas ambientais"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dicas ORDER BY likes DESC")
    dicas = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>💡 Dicas Ambientais</h2>", unsafe_allow_html=True)
    
    for dica in dicas:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 6px solid {icon_color}; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>{dica[1]}</h4>
            <p style='color: {text_color};'>{dica[2]}</p>
            <small style='color: {text_color};'>Categoria: {dica[3]} | 👍 {dica[5]} curtidas</small>
        </div>
        """, unsafe_allow_html=True)

def mostrar_eventos_completos(text_color, card_bg, icon_color, border_color):
    """Mostra eventos"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY data LIMIT 5")
    eventos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>📅 Eventos 2026</h2>", unsafe_allow_html=True)
    
    for evento in eventos:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ff9f4b; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>{evento[1]}</h4>
            <p style='color: {text_color};'>{evento[2]}</p>
            <p><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
            <p><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
            <p><small>Organização: {evento[10]}</small></p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_pontos_completos(text_color, card_bg, icon_color, border_color):
    """Mostra pontos de coleta"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pontos_coleta ORDER BY avaliacao DESC")
    pontos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta</h2>", unsafe_allow_html=True)
    
    for ponto in pontos:
        estrelas = "★" * int(ponto[6]) + "☆" * (5 - int(ponto[6]))
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between;'>
                <div>
                    <h4 style='color: {text_color};'>{ponto[1]}</h4>
                    <p><i class='fas fa-map-pin' style='color: {icon_color};'></i> {ponto[2]}</p>
                    <p><i class='fas fa-clock' style='color: {icon_color};'></i> {ponto[4]}</p>
                    <p><i class='fas fa-phone' style='color: {icon_color};'></i> {ponto[5]}</p>
                </div>
                <div style='text-align: center;'>
                    <div style='color: gold; font-size: 20px;'>{estrelas}</div>
                    <p>{ponto[6]}/5.0</p>
                    <span style='background: {icon_color}; color: white; padding: 5px 10px; border-radius: 50px; font-size: 12px;'>{ponto[3].upper()}</span>
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
    }}
    
    /* Conteúdo principal */
    .stMarkdown, p, h1, h2, h3, h4 {{
        color: {text_color} !important;
    }}
    
    .stButton button {{
        background: {icon_color};
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
    }}
    
    .stButton button:hover {{
        background: #1a8c5f;
        transform: scale(1.05);
    }}
    
    div.stTabs [data-baseweb="tab-list"] button {{
        color: {text_color} !important;
    }}
    
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {icon_color} !important;
        color: white !important;
    }}
</style>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state['mostrar_upload'] = False
    st.session_state['desafio_atual'] = None

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(f"<h1 style='text-align: center;'>🌿 SustentaPira</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {secondary_text};'>Não herdamos a Terra de nossos antepassados, nós a pegamos emprestada de nossos filhos.</p>", unsafe_allow_html=True)
with col3:
    if st.button("🌓 " + ("Modo Claro" if tema == "dark" else "Modo Escuro")):
        toggle_theme()

if st.session_state.usuario_logado is None:
    # Sidebar de login
    with st.sidebar:
        st.markdown(f"<h2 style='color: {sidebar_text};'>🔐 Login</h2>", unsafe_allow_html=True)
        
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
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            interesses = st.multiselect("Interesses", 
                ["Sustentabilidade", "Reciclagem", "Eventos", "Voluntariado"])
            
            if st.form_submit_button("Criar conta", use_container_width=True):
                if nome and validar_email(email) and len(senha) >= 6:
                    sucesso, user_id = criar_usuario(
                        nome, email, senha, ",".join(interesses) if interesses else ""
                    )
                    if sucesso:
                        st.success("Conta criada! Faça login.")
                    else:
                        st.error("E-mail já existe!")
                else:
                    st.error("Preencha todos os campos corretamente")
    
    # Página inicial
    st.markdown(f"""
    <div style='text-align: center; padding: 50px;'>
        <i class="fas fa-seedling" style='font-size: 80px; color: {icon_color};'></i>
        <h1>Bem-vindo ao EcoPiracicaba</h1>
        <p style='font-size: 1.2rem;'>Faça login para começar a ganhar pontos e subir no ranking!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        mostrar_dicas_completas(text_color, card_bg, icon_color, border_color)
    with col2:
        mostrar_eventos_completos(text_color, card_bg, icon_color, border_color)

else:
    # Sidebar do usuário logado
    with st.sidebar:
        user, progresso, _, _ = get_user_data(st.session_state.usuario_logado['id'])
        
        if progresso:
            pontos = progresso[1]
            nivel = progresso[2]
            desafios = progresso[11] if len(progresso) > 11 else 0
        else:
            pontos = 0
            nivel = "🌱 EcoIniciante"
            desafios = 0
        
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #f5f5f5; border-radius: 10px;'>
            <h3 style='color: {sidebar_text};'>{st.session_state.usuario_logado['nome']}</h3>
            <h4 style='color: {icon_color};'>{nivel}</h4>
            <h2 style='color: {icon_color};'>{pontos} pts</h2>
            <div style='height: 8px; background: #cccccc; border-radius: 4px; margin: 10px 0;'>
                <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
            </div>
            <p style='color: {sidebar_text};'>🎯 {desafios} desafios</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Desafios", "👤 Perfil", "🏆 Ranking", "📅 Eventos", "📍 Pontos"])
    
    with tab1:
        mostrar_pagina_desafios(
            st.session_state.usuario_logado['id'],
            text_color, card_bg, icon_color, border_color
        )
    
    with tab2:
        mostrar_perfil_completo(
            st.session_state.usuario_logado['id'],
            text_color, card_bg, icon_color, border_color
        )
    
    with tab3:
        mostrar_ranking_completo(text_color, card_bg, icon_color, border_color)
    
    with tab4:
        mostrar_eventos_completos(text_color, card_bg, icon_color, border_color)
    
    with tab5:
        mostrar_pontos_completos(text_color, card_bg, icon_color, border_color)
