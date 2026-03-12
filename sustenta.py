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
import json
from PIL import Image
import io
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="EcoPiracicaba 2026",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FUNÇÕES BÁSICAS ==========

def get_theme():
    return "dark"

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
        "tipo": "reciclagem",
        "dica_validacao": "Tire foto dos materiais na balança",
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
        "dica_validacao": "Tire foto da muda plantada com coordenadas GPS",
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
    }
]

# ========== SISTEMA DE VALIDAÇÃO DE FOTOS ==========

def validar_foto(imagem_bytes, tipo_desafio, usuario_id):
    """
    Sistema de validação de fotos em múltiplas camadas
    Retorna: (aprovado, mensagem, pontos_ajustados)
    """
    try:
        # Carregar imagem
        imagem = Image.open(io.BytesIO(imagem_bytes))
        
        # ===== CAMADA 1: VALIDAÇÕES BÁSICAS DA IMAGEM =====
        
        # Verificar tamanho mínimo
        if len(imagem_bytes) < 1024:  # Menos de 1KB
            return False, "Imagem muito pequena. Tire uma foto de melhor qualidade.", 0
        
        # Verificar dimensões mínimas
        if imagem.width < 300 or imagem.height < 300:
            return False, "Imagem com resolução muito baixa. Tire uma foto mais nítida.", 0
        
        # Verificar se é colorida (não é totalmente preta/branca)
        img_array = np.array(imagem.convert('L'))
        if np.std(img_array) < 5:  # Pouca variação de cor
            return False, "Imagem parece ser muito escura ou uniforme. Tire uma foto mais clara.", 0
        
        # ===== CAMADA 2: PREVENÇÃO DE REUSO DE FOTOS =====
        
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        # Gerar hash da imagem para detectar reuso
        image_hash = hashlib.md5(imagem_bytes).hexdigest()
        
        # Verificar se esta imagem já foi usada por alguém
        c.execute("SELECT id, usuario_id, data FROM comprovantes WHERE imagem_hash = ?", (image_hash,))
        imagem_existente = c.fetchone()
        
        if imagem_existente:
            if imagem_existente[1] == usuario_id:
                return False, "Esta foto já foi enviada por você anteriormente. Tire uma nova foto.", 0
            else:
                return False, "Esta foto já foi usada por outro usuário. Tire sua própria foto.", 0
        
        # ===== CAMADA 3: LIMITE DE TEMPO ENTRE VALIDAÇÕES =====
        
        desafio = next((d for d in DESAFIOS_LISTA if d["tipo"] == tipo_desafio), None)
        if desafio:
            # Verificar última submissão do mesmo tipo
            c.execute("""
                SELECT data FROM comprovantes 
                WHERE usuario_id = ? AND tipo = ? 
                ORDER BY data DESC LIMIT 1
            """, (usuario_id, tipo_desafio))
            ultima_submissao = c.fetchone()
            
            if ultima_submissao:
                try:
                    data_ultima = datetime.strptime(ultima_submissao[0].split()[0], "%d/%m/%Y")
                    hoje = datetime.now()
                    dias_diferenca = (hoje - data_ultima).days
                    
                    if dias_diferenca < desafio["dias_entre_validacoes"]:
                        dias_restantes = desafio["dias_entre_validacoes"] - dias_diferenca
                        return False, f"Você precisa aguardar {dias_restantes} dias antes de enviar outro comprovante deste tipo.", 0
                except:
                    pass
        
        # ===== CAMADA 4: LIMITE DIÁRIO =====
        
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        c.execute("""
            SELECT COUNT(*) FROM comprovantes 
            WHERE usuario_id = ? AND data LIKE ? AND tipo = ?
        """, (usuario_id, f"{hoje_str}%", tipo_desafio))
        count_hoje = c.fetchone()[0]
        
        if desafio and count_hoje >= desafio["limite_diario"]:
            return False, f"Você já atingiu o limite diário para este tipo de desafio. Tente novamente amanhã.", 0
        
        # ===== CAMADA 5: VALIDAÇÃO ESPECÍFICA POR TIPO =====
        
        pontos_ajustados = desafio["pontos"] if desafio else 100
        
        if tipo_desafio == "reciclagem":
            # Tentar estimar quantidade de material
            # Simulação: quanto maior a imagem, mais material (heurística simples)
            tamanho_arquivo = len(imagem_bytes)
            if tamanho_arquivo > 500000:  # >500KB
                pontos_ajustados = 250  # Bônus por foto de qualidade
            elif tamanho_arquivo < 50000:  # <50KB
                pontos_ajustados = 150  # Redução por foto suspeita
        
        elif tipo_desafio == "evento":
            # Verificar metadados da foto (data)
            try:
                # Extrair metadados EXIF se disponíveis
                from PIL.ExifTags import TAGS
                exif_data = {}
                if hasattr(imagem, '_getexif') and imagem._getexif():
                    exif = imagem._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    
                    # Verificar data da foto
                    if 'DateTime' in exif_data:
                        data_foto = exif_data['DateTime']
                        # Aqui poderia validar se a foto é recente
                        pass
            except:
                pass
        
        # ===== CAMADA 6: ANÁLISE DE METADADOS =====
        
        # Salvar hash e metadados para análise futura
        conn.close()
        
        return True, "Comprovante validado com sucesso!", pontos_ajustados
        
    except Exception as e:
        print(f"Erro na validação da foto: {e}")
        return False, "Erro ao processar a imagem. Tente novamente.", 0

# ========== SISTEMA DE VALIDAÇÃO DE EVENTOS ==========

def validar_inscricao_evento(usuario_id, evento_id):
    """
    Valida se o usuário pode se inscrever no evento
    """
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        # Verificar se evento existe e tem vagas
        c.execute("SELECT vagas, inscritos, data FROM eventos WHERE id = ?", (evento_id,))
        evento = c.fetchone()
        
        if not evento:
            return False, "Evento não encontrado."
        
        vagas, inscritos, data_evento = evento
        
        if vagas > 0 and inscritos >= vagas:
            return False, "Evento sem vagas disponíveis."
        
        # Verificar se já está inscrito
        c.execute("SELECT id FROM inscricoes WHERE usuario_id = ? AND evento_id = ?", (usuario_id, evento_id))
        if c.fetchone():
            return False, "Você já está inscrito neste evento."
        
        # Verificar data do evento (não pode ser no passado)
        try:
            data_ev = datetime.strptime(data_evento, "%d/%m/%Y")
            if data_ev < datetime.now():
                return False, "Este evento já ocorreu."
        except:
            pass
        
        return True, "Inscrição válida."
        
    except Exception as e:
        print(f"Erro na validação do evento: {e}")
        return False, "Erro ao validar inscrição."
    finally:
        conn.close()

def confirmar_presenca_evento(usuario_id, evento_id):
    """
    Confirma presença do usuário no evento e concede pontos
    """
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        # Verificar se está inscrito e ainda não participou
        c.execute("""
            SELECT id, participou FROM inscricoes 
            WHERE usuario_id = ? AND evento_id = ?
        """, (usuario_id, evento_id))
        inscricao = c.fetchone()
        
        if not inscricao:
            return False, "Você não está inscrito neste evento."
        
        if inscricao[1] == 1:
            return False, "Presença já confirmada anteriormente."
        
        # Verificar data do evento (deve ser hoje)
        c.execute("SELECT data FROM eventos WHERE id = ?", (evento_id,))
        data_evento = c.fetchone()[0]
        
        hoje = datetime.now().strftime("%d/%m/%Y")
        if data_evento != hoje:
            return False, "A presença só pode ser confirmada no dia do evento."
        
        # Atualizar participação
        c.execute("UPDATE inscricoes SET participou = 1 WHERE id = ?", (inscricao[0],))
        
        # Atualizar contador no progresso
        c.execute("""
            UPDATE progresso 
            SET eventos_participados = eventos_participados + 1 
            WHERE usuario_id = ?
        """, (usuario_id,))
        
        conn.commit()
        
        # Conceder pontos
        adicionar_pontos(usuario_id, 150, "Participou de evento", "📅", "evento")
        
        return True, "Presença confirmada! Pontos concedidos."
        
    except Exception as e:
        print(f"Erro ao confirmar presença: {e}")
        return False, "Erro ao confirmar presença."
    finally:
        conn.close()

# ========== INICIALIZAÇÃO DO BANCO DE DADOS ==========

def init_database():
    db_path = os.path.join(os.path.dirname(__file__), 'ecopiracicaba.db')
    db_exists = os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Criar tabelas se não existirem
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            avatar TEXT,
            cidade TEXT DEFAULT 'Piracicaba',
            data_cadastro TEXT,
            ultimo_acesso TEXT
        )
    ''')
    
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
    
    # Modificar tabela de comprovantes para incluir hash e status de validação
    c.execute('''
        CREATE TABLE IF NOT EXISTS comprovantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            imagem BLOB,
            imagem_hash TEXT UNIQUE,
            pontos_ganhos INTEGER DEFAULT 0,
            data TEXT NOT NULL,
            aprovado INTEGER DEFAULT 0,
            validado_por TEXT,
            data_validacao TEXT,
            metadados TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
    
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
            contato TEXT,
            codigo_confirmacao TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            evento_id INTEGER,
            data_inscricao TEXT,
            participou INTEGER DEFAULT 0,
            data_confirmacao TEXT,
            codigo_confirmacao TEXT,
            UNIQUE(usuario_id, evento_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (evento_id) REFERENCES eventos (id) ON DELETE CASCADE
        )
    ''')
    
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
    
    # Criar índices para melhor performance
    c.execute('CREATE INDEX IF NOT EXISTS idx_comprovantes_hash ON comprovantes(imagem_hash)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_comprovantes_usuario ON comprovantes(usuario_id, tipo, data)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_inscricoes_evento ON inscricoes(evento_id, participou)')
    
    conn.commit()
    
    # Inserir dados iniciais se necessário
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        try:
            dados_iniciais(conn, c)
            conn.commit()
        except Exception as e:
            print(f"Erro ao inserir dados iniciais: {e}")
    
    conn.close()

def dados_iniciais(conn, c):
    """Insere dados iniciais no banco"""
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Admin
    c.execute(
        "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
        ("Administrador", "admin@ecopiracicaba.com", "eco2026", data_atual)
    )
    admin_id = c.lastrowid
    c.execute(
        "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
        (admin_id, 1000, get_nivel(1000), data_atual)
    )
    
    # Usuários exemplo
    usuarios_exemplo = [
        ("João Silva", "joao@email.com", "123456", 350),
        ("Maria Santos", "maria@email.com", "123456", 520),
        ("Pedro Oliveira", "pedro@email.com", "123456", 180)
    ]
    
    for nome, email, senha, pontos in usuarios_exemplo:
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            (nome, email, senha, data_atual)
        )
        user_id = c.lastrowid
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (user_id, pontos, get_nivel(pontos), data_atual)
        )
    
    # Eventos com código de confirmação
    eventos = [
        ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos, artesanato sustentável e startups verdes", "15/03/2026", "09:00", "Engenho Central - Piracicaba", "feira", 1000, "Prefeitura de Piracicaba", "(19) 3403-1100", "FEIRA2026"),
        ("♻️ Workshop de Reciclagem", "Aprenda técnicas avançadas de reciclagem em casa", "22/03/2026", "14:00", "SENAI Piracicaba", "workshop", 50, "SENAI", "(19) 3412-5000", "WORKSHOP01"),
        ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio com atividades educativas", "05/04/2026", "08:00", "Rua do Porto - Piracicaba", "mutirão", 200, "SOS Rio Piracicaba", "(19) 99765-4321", "MUTIRAO01"),
        ("🌿 Palestra: Compostagem", "Como fazer compostagem doméstica e comunitária", "12/04/2026", "10:00", "Horto Municipal - Piracicaba", "palestra", 100, "Horto Municipal", "(19) 3434-5678", "PALESTRA01"),
        ("🌍 Dia da Terra", "Celebração com atividades, música e feira verde", "22/04/2026", "09:00", "Parque da Rua do Porto - Piracicaba", "evento", 2000, "ONG Planeta Verde", "(19) 99876-5432", "DIATERRA")
    ]
    
    for e in eventos:
        c.execute(
            "INSERT INTO eventos (titulo, descricao, data, hora, local, tipo, vagas, organizador, contato, codigo_confirmacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            e
        )
    
    # Dicas
    dicas = [
        ("🌱 Compostagem Doméstica", "50% do lixo doméstico pode ser compostado! Faça sua própria composteira com baldes e minhocas californianas.", "resíduos", data_atual, 0, "Equipe EcoPiracicaba"),
        ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros. Reduza para 5 minutos e economize 90 litros por banho!", "água", data_atual, 0, "Sabesp"),
        ("🔋 Pilhas e Baterias", "Uma pilha pode contaminar 20 mil litros de água por até 50 anos. Descarte sempre em pontos de coleta.", "resíduos", data_atual, 0, "Greenpeace")
    ]
    for d in dicas:
        c.execute(
            "INSERT INTO dicas (titulo, conteudo, categoria, data_publicacao, likes, autor) VALUES (?, ?, ?, ?, ?, ?)",
            d
        )
    
    # Pontos de coleta
    pontos = [
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", 4.5, "Recebe todos os tipos de recicláveis, eletrônicos e óleo de cozinha"),
        ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", 4.8, "Ponto de coleta de pilhas e baterias no piso G1")
    ]
    for p in pontos:
        c.execute(
            "INSERT INTO pontos_coleta (nome, endereco, categoria, horario, telefone, avaliacao, descricao) VALUES (?, ?, ?, ?, ?, ?, ?)",
            p
        )

init_database()

# ========== FUNÇÕES DE PROGRESSO ==========

def get_user_data(user_id):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("SELECT nome, email, cidade, data_cadastro FROM usuarios WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    c.execute("SELECT * FROM progresso WHERE usuario_id = ?", (user_id,))
    progresso = c.fetchone()
    
    c.execute("SELECT * FROM conquistas WHERE usuario_id = ? ORDER BY data DESC LIMIT 10", (user_id,))
    conquistas = c.fetchall()
    
    c.execute("SELECT * FROM comprovantes WHERE usuario_id = ? ORDER BY data DESC", (user_id,))
    comprovantes = c.fetchall()
    
    c.execute("SELECT evento_id FROM inscricoes WHERE usuario_id = ?", (user_id,))
    inscricoes = c.fetchall()
    
    c.execute("SELECT dica_id FROM dicas_vistas WHERE usuario_id = ?", (user_id,))
    dicas_vistas = c.fetchall()
    
    c.execute("SELECT ponto_id FROM visitas_pontos WHERE usuario_id = ?", (user_id,))
    visitas = c.fetchall()
    
    c.execute("SELECT codigo FROM convites WHERE usuario_id = ? AND usado = 0", (user_id,))
    convites = c.fetchall()
    
    conn.close()
    
    return user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites

def criar_usuario(nome, email, senha):
    conn = None
    try:
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if c.fetchone():
            return False, None, "Este e-mail já está cadastrado!"
        
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            (nome, email, senha, data_atual)
        )
        
        user_id = c.lastrowid
        
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (user_id, 0, "🌱 EcoIniciante", data_atual)
        )
        
        codigo = hashlib.md5(f"{user_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
        c.execute(
            "INSERT INTO convites (usuario_id, codigo, data_criacao) VALUES (?, ?, ?)",
            (user_id, codigo, data_atual)
        )
        
        conn.commit()
        return True, user_id, "Conta criada com sucesso!"
    except Exception as e:
        print(f"Erro: {e}")
        return False, None, "Erro ao criar conta."
    finally:
        if conn:
            conn.close()

def fazer_login(email, senha):
    conn = None
    try:
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        user = c.fetchone()
        
        if user:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.execute("UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?", (data_atual, user[0]))
            
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
            return user
        return None
    except Exception as e:
        print(f"Erro no login: {e}")
        return None
    finally:
        if conn:
            conn.close()

def adicionar_pontos(usuario_id, pontos, descricao, icone="✨", tipo="geral"):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    c.execute(
        "INSERT INTO conquistas (usuario_id, tipo, pontos, data, descricao, icone) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, tipo, pontos, data_atual, descricao, icone)
    )
    
    c.execute("SELECT total_pontos FROM progresso WHERE usuario_id = ?", (usuario_id,))
    resultado = c.fetchone()
    
    if resultado:
        novos_pontos = resultado[0] + pontos
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, data_atual, usuario_id)
        )
    
    conn.commit()
    conn.close()
    return True

def salvar_comprovante(usuario_id, tipo, descricao, imagem_bytes, pontos_sugeridos):
    """Salva comprovante com validação"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    image_hash = hashlib.md5(imagem_bytes).hexdigest()
    
    # Validar a foto
    aprovado, mensagem, pontos_ajustados = validar_foto(imagem_bytes, tipo, usuario_id)
    
    if not aprovado:
        conn.close()
        return False, mensagem, 0
    
    # Salvar metadados básicos
    metadados = json.dumps({
        "tamanho": len(imagem_bytes),
        "data_envio": data_atual
    })
    
    c.execute(
        """INSERT INTO comprovantes 
           (usuario_id, tipo, descricao, imagem, imagem_hash, pontos_ganhos, data, aprovado, metadados) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (usuario_id, tipo, descricao, imagem_bytes, image_hash, pontos_ajustados, data_atual, 1, metadados)
    )
    
    conn.commit()
    conn.close()
    
    # Adicionar pontos automaticamente (aprovado)
    adicionar_pontos(usuario_id, pontos_ajustados, f"Completou: {descricao}", "📸", tipo)
    
    return True, f"Comprovante validado! Você ganhou {pontos_ajustados} pontos.", pontos_ajustados

def get_ranking():
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
    """Inscreve usuário em evento com validação"""
    valido, mensagem = validar_inscricao_evento(usuario_id, evento_id)
    
    if not valido:
        return False, mensagem
    
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Gerar código de confirmação único
        codigo = hashlib.md5(f"{usuario_id}{evento_id}{time.time()}".encode()).hexdigest()[:8].upper()
        
        c.execute(
            """INSERT INTO inscricoes 
               (usuario_id, evento_id, data_inscricao, codigo_confirmacao) 
               VALUES (?, ?, ?, ?)""",
            (usuario_id, evento_id, data_atual, codigo)
        )
        
        c.execute("UPDATE eventos SET inscritos = inscritos + 1 WHERE id = ?", (evento_id,))
        conn.commit()
        
        return True, f"Inscrição realizada! Seu código: {codigo}"
    except Exception as e:
        print(f"Erro na inscrição: {e}")
        return False, "Erro ao realizar inscrição."
    finally:
        conn.close()

# ========== COMPONENTES DE INTERFACE ==========

def mostrar_eventos_destaque(text_color, card_bg, icon_color, border_color, secondary_text):
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY data LIMIT 6")
    eventos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h1 style='text-align: center; color: {text_color}; margin-bottom: 30px;'>🌿 EcoPiracicaba 2026</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: {secondary_text}; margin-bottom: 40px;'>Eventos em Piracicaba</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    for i, evento in enumerate(eventos):
        with col1 if i % 2 == 0 else col2:
            vagas_text = f"{evento[8]}/{evento[7]}" if evento[7] > 0 else "Sem limite"
            disponibilidade = (evento[8] / evento[7] * 100) if evento[7] > 0 else 0
            
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid {icon_color}; border: 1px solid {border_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div style='flex: 1;'>
                        <span style='background: {icon_color}; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px;'>{evento[6].upper()}</span>
                        <h3 style='color: {text_color}; margin: 10px 0 5px 0;'>{evento[1]}</h3>
                        <p style='color: {text_color}; margin: 5px 0; font-size: 14px;'>{evento[2][:100]}...</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
                    </div>
                    <div style='text-align: right; min-width: 120px;'>
                        <p style='color: {secondary_text};'><strong>{evento[8]}/{evento[7] if evento[7] > 0 else '∞'}</strong> inscritos</p>
                        <div style='height: 6px; background: {border_color}; border-radius: 3px; margin: 10px 0;'>
                            <div style='height: 100%; width: {disponibilidade}%; background: {icon_color}; border-radius: 3px;'></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_perfil_completo(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites = get_user_data(usuario_id)
    
    if not user or not progresso:
        st.error("Erro ao carregar perfil")
        return
    
    nome, email, cidade, data_cadastro = user
    
    pontos = progresso[1] if len(progresso) > 1 else 0
    nivel = progresso[2] if len(progresso) > 2 else "🌱 EcoIniciante"
    eventos = progresso[3] if len(progresso) > 3 else 0
    dicas = progresso[4] if len(progresso) > 4 else 0
    pontos_visitados = progresso[5] if len(progresso) > 5 else 0
    kg = progresso[6] if len(progresso) > 6 else 0
    streak = progresso[9] if len(progresso) > 9 else 0
    
    proximo = get_proximo_nivel(pontos)
    
    st.markdown(f"<h2 style='color: {text_color};'>👤 Meu Perfil</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<span style='color: {text_color};'>**Nome:** {nome}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: {text_color};'>**Email:** {email}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<span style='color: {text_color};'>**Cidade:** {cidade or 'Piracicaba'}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: {text_color};'>**Membro desde:** {data_cadastro}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
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
    
    # Estatísticas
    st.markdown(f"<h3 style='color: {text_color};'>📊 Estatísticas</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📅 Eventos</h4>
            <h2 style='color: {icon_color};'>{eventos}</h2>
            <small style='color: {text_color};'>{len(inscricoes)} inscrições</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>💡 Dicas</h4>
            <h2 style='color: {icon_color};'>{dicas}</h2>
            <small style='color: {text_color};'>{len(dicas_vistas)} lidas</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>📍 Visitas</h4>
            <h2 style='color: {icon_color};'>{pontos_visitados}</h2>
            <small style='color: {text_color};'>{len(visitas)} pontos</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h4 style='color: {text_color};'>♻️ Kg</h4>
            <h2 style='color: {icon_color};'>{kg}</h2>
            <p style='color: {text_color};'>reciclados</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Histórico de comprovantes
    if comprovantes:
        with st.expander("📸 Histórico de Comprovantes"):
            for comp in comprovantes[:5]:
                status = "✅ Aprovado" if comp[7] else "⏳ Pendente"
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
                    <strong style='color: {text_color};'>{comp[2]}</strong><br>
                    <small style='color: {text_color};'>{comp[6]} | {comp[5]} pontos | {status}</small>
                </div>
                """, unsafe_allow_html=True)

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios Ambientais</h2>", unsafe_allow_html=True)
    
    user, progresso, conquistas, _, _, _, _, _ = get_user_data(usuario_id)
    
    pontos = progresso[1] if progresso and len(progresso) > 1 else 0
    
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Seus Pontos</h3>
        <h1 style='color: {icon_color}; font-size: 48px;'>{pontos}</h1>
        <p style='color: {text_color};'>Continue completando desafios!</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                            <p style='color: {secondary_text}; font-size: 12px; margin: 5px 0 0 0;'><i class='fas fa-info-circle'></i> {desafio['dica_validacao']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📸 Comprovar", key=f"btn_{desafio['id']}"):
                    st.session_state['desafio_atual'] = desafio
                    st.session_state['mostrar_upload'] = True
                    st.rerun()
    
    if st.session_state.get('mostrar_upload', False):
        desafio = st.session_state['desafio_atual']
        
        st.markdown("---")
        st.markdown(f"### 📸 Comprovar: {desafio['titulo']}")
        st.info(f"**Dica:** {desafio['dica_validacao']}")
        
        uploaded_file = st.file_uploader(
            "Tire uma foto ou envie um comprovante",
            type=['jpg', 'jpeg', 'png'],
            key="upload_comprovante"
        )
        
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Sua foto", use_container_width=True)
            
            with col2:
                st.markdown(f"<span style='color: {text_color};'>**Desafio:** {desafio['titulo']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: {text_color};'>**Pontos base:** +{desafio['pontos']}</span>", unsafe_allow_html=True)
                
                if st.button("✅ Enviar para validação", key="confirmar_upload"):
                    with st.spinner("Validando imagem..."):
                        sucesso, mensagem, pontos_ganhos = salvar_comprovante(
                            usuario_id,
                            desafio['tipo'],
                            f"Completou: {desafio['titulo']}",
                            bytes_data,
                            desafio['pontos']
                        )
                        
                        if sucesso:
                            st.balloons()
                            st.success(mensagem)
                            st.session_state['mostrar_upload'] = False
                            st.session_state['desafio_atual'] = None
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(mensagem)
            
            if st.button("❌ Cancelar"):
                st.session_state['mostrar_upload'] = False
                st.session_state['desafio_atual'] = None
                st.rerun()

def mostrar_ranking_completo(text_color, card_bg, icon_color, border_color, secondary_text):
    ranking = get_ranking()
    
    st.markdown(f"<h2 style='color: {text_color};'>🏆 Ranking EcoCidadãos</h2>", unsafe_allow_html=True)
    
    if not ranking:
        st.info("Nenhum usuário no ranking ainda.")
        return
    
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
    
    for i, (nome, pontos, nivel) in enumerate(ranking[3:], start=4):
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 12px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='font-size: 16px; font-weight: bold; color: {text_color};'>{i}º</span>
                    <strong style='color: {text_color}; margin-left: 10px;'>{nome}</strong>
                    <span style='color: {secondary_text}; margin-left: 10px;'>{nivel}</span>
                </div>
                <div>
                    <span style='color: {icon_color};'>{pontos} pts</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_pontos_completos(text_color, card_bg, icon_color, border_color, secondary_text):
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
                        <p style='margin: 3px 0; color: {text_color};'><i class='fas fa-map-pin' style='color: {icon_color};'></i> {ponto[2]}</p>
                        <p style='margin: 3px 0; color: {text_color};'><i class='fas fa-clock' style='color: {icon_color};'></i> {ponto[4]}</p>
                        <p style='margin: 3px 0; color: {text_color};'><i class='fas fa-phone' style='color: {icon_color};'></i> {ponto[5]}</p>
                    </div>
                    <div style='text-align: center;'>
                        <div style='color: gold; font-size: 18px;'>{estrelas}</div>
                        <p style='margin: 5px 0; color: {text_color};'>{ponto[6]}/5.0</p>
                        <span style='background: {icon_color}; color: white; padding: 3px 8px; border-radius: 50px; font-size: 11px;'>{ponto[3].upper()}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ========== CONFIGURAÇÕES DE TEMA ==========

bg_color = "#0a1f17"
card_bg = "#1a3329"
text_color = "#FFFFFF"
secondary_text = "#E0E0E0"
border_color = "#2a4a3a"
icon_color = "#8bc34a"
gradient_start = "#0a1f17"
gradient_end = "#1a4a3a"

sidebar_bg = "#1a3329"
sidebar_text = "#FFFFFF"

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
    }}
    
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
        background-color: #2a4a3a !important;
        color: {sidebar_text} !important;
        border: 1px solid {border_color} !important;
    }}
    
    section[data-testid="stSidebar"] .stButton button {{
        background-color: {icon_color} !important;
        color: white !important;
        border: none !important;
    }}
    
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, div:not(.stButton) {{
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
        background: #6ba539;
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
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: #2a4a3a !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    .stTextInput label, .stTextArea label, .stSelectbox label {{
        color: {text_color} !important;
    }}
    
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
    
    .stAlert {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
</style>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state['mostrar_upload'] = False
    st.session_state['desafio_atual'] = None

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
                    sucesso, user_id, mensagem = criar_usuario(nome, email, senha)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)
    else:
        user, progresso, conquistas, _, _, _, _, convites = get_user_data(st.session_state.usuario_logado['id'])
        
        pontos = progresso[1] if progresso and len(progresso) > 1 else 0
        nivel = progresso[2] if progresso and len(progresso) > 2 else "🌱 EcoIniciante"
        streak = progresso[9] if progresso and len(progresso) > 9 else 0
        
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #2a4a3a; border-radius: 10px;'>
            <h3 style='color: {sidebar_text};'>{st.session_state.usuario_logado['nome']}</h3>
            <h4 style='color: {icon_color};'>{nivel}</h4>
            <h2 style='color: {icon_color};'>{pontos} pts</h2>
            <div style='height: 8px; background: {border_color}; border-radius: 4px; margin: 10px 0;'>
                <div style='height: 100%; width: {min(100, (pontos/5000)*100)}%; background: {icon_color}; border-radius: 4px;'></div>
            </div>
            <div style='display: flex; justify-content: space-around; margin-top: 10px;'>
                <div><span style='color: #ff9800;'>🔥 {streak}</span><br><small style='color: {sidebar_text};'>dias</small></div>
                <div><span style='color: {icon_color};'>🏅 {len(conquistas)}</span><br><small style='color: {sidebar_text};'>conquistas</small></div>
                <div><span style='color: gold;'>🔗 {len(convites)}</span><br><small style='color: {sidebar_text};'>convites</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

if st.session_state.usuario_logado is None:
    mostrar_eventos_destaque(text_color, card_bg, icon_color, border_color, secondary_text)
    
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
                    <h4 style='color: {text_color};'>{evento[1]}</h4>
                    <p style='color: {text_color};'>{evento[2]}</p>
                    <p style='color: {text_color};'><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
                    <p style='color: {text_color};'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if evento[7] == 0 or evento[8] < evento[7]:
                    if st.button(f"📝 Inscrever-se", key=f"insc_{evento[0]}"):
                        sucesso, mensagem = inscrever_evento(st.session_state.usuario_logado['id'], evento[0])
                        if sucesso:
                            st.success(mensagem)
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(mensagem)
                else:
                    st.info("Esgotado")
    
    with tab5:
        mostrar_pontos_completos(text_color, card_bg, icon_color, border_color, secondary_text)
