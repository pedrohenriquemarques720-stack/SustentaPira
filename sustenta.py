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

# Configuração da página
st.set_page_config(
    page_title="SustentaPira",
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

# ===== FUNÇÃO PARA RESETAR O BANCO DE DADOS =====
def reset_database():
    """Remove o banco de dados existente para recriar com os novos dados"""
    db_path = os.path.join(os.path.dirname(__file__), 'ecopiracicaba.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Banco de dados antigo removido. Novos dados serão inseridos.")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")

# DESCOMENTE A LINHA ABAIXO PARA RESETAR O BANCO (faça isso apenas uma vez)
# reset_database()  # <--- Descomente esta linha para resetar o banco

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
        telefone TEXT,
        avatar TEXT,
        cidade TEXT DEFAULT 'Piracicaba',
        data_cadastro TEXT,
        ultimo_acesso TEXT,
        banido INTEGER DEFAULT 0,
        motivo_ban TEXT
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
            tentativas_falhas INTEGER DEFAULT 0,
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
            motivo_rejeicao TEXT,
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
            endereco TEXT,
            tipo TEXT,
            vagas INTEGER,
            inscritos INTEGER DEFAULT 0,
            organizador TEXT,
            contato TEXT,
            codigo_confirmacao TEXT,
            pontos_evento INTEGER DEFAULT 150
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
            nome_participante TEXT,
            email_participante TEXT,
            telefone_participante TEXT,
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
            descricao TEXT,
            latitude REAL,
            longitude REAL
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
    
    conn.commit()
    
    # Criar índices
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_comprovantes_hash ON comprovantes(imagem_hash)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_comprovantes_usuario ON comprovantes(usuario_id, tipo, data)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_inscricoes_evento ON inscricoes(evento_id, participou)')
    except:
        pass
    
    conn.commit()
    
    # VERIFICAR SE JÁ EXISTEM DADOS
    c.execute("SELECT COUNT(*) FROM usuarios")
    tem_usuarios = c.fetchone()[0] > 0
    
    c.execute("SELECT COUNT(*) FROM eventos")
    tem_eventos = c.fetchone()[0] > 0
    
    c.execute("SELECT COUNT(*) FROM pontos_coleta")
    tem_pontos = c.fetchone()[0] > 0
    
    # SE NÃO TIVER DADOS OU FORÇAR RESET, INSERIR DADOS INICIAIS
    if not tem_usuarios or not tem_eventos or not tem_pontos:
        try:
            # Limpar dados existentes se houver
            if tem_usuarios:
                print("Atualizando dados existentes...")
            
            dados_iniciais(conn, c)
            conn.commit()
            print("✅ Dados iniciais inseridos/atualizados com sucesso!")
            print(f"   - Eventos: {len(eventos)}")
            print(f"   - Pontos de coleta: {len(pontos_gerais) + len(pontos_pilhas) + len(pontos_eletronicos) + len(pontos_oleo) + len(pontos_vidros) + len(pontos_papel) + len(pontos_plasticos) + len(pontos_organicos) + len(pontos_medicamentos) + len(pontos_lampadas) + len(pontos_roupas) + len(pontos_moveis) + len(pontos_metais) + len(pontos_pilhas_extra)}")
        except Exception as e:
            print(f"❌ Erro ao inserir dados iniciais: {e}")
    
    conn.close()

# ===== DADOS INICIAIS =====
eventos = []  # Lista vazia para ser preenchida
pontos_gerais = []
pontos_pilhas = []
pontos_eletronicos = []
pontos_oleo = []
pontos_vidros = []
pontos_papel = []
pontos_plasticos = []
pontos_organicos = []
pontos_medicamentos = []
pontos_lampadas = []
pontos_roupas = []
pontos_moveis = []
pontos_metais = []
pontos_pilhas_extra = []

def dados_iniciais(conn, c):
    """Insere dados iniciais no banco"""
    global eventos, pontos_gerais, pontos_pilhas, pontos_eletronicos, pontos_oleo, pontos_vidros, pontos_papel, pontos_plasticos, pontos_organicos, pontos_medicamentos, pontos_lampadas, pontos_roupas, pontos_moveis, pontos_metais, pontos_pilhas_extra
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Só insere usuários se não existirem
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        # Admin
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin@sustentapira.com", "eco2026", data_atual)
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
    
    # ===== EVENTOS 2026 - PIRACICABA (MEGA EXPANDIDO) =====
    eventos = [
        # JANEIRO 2026
        ("🌱 1º Mutirão de Limpeza 2026", "Inicie o ano contribuindo com a limpeza das margens do Rio Piracicaba. Haverá café da manhã comunitário e distribuição de mudas.", "10/01/2026", "08:00", "Rua do Porto", "Rua do Porto - Centro", "mutirão", 150, "SOS Rio Piracicaba", "(19) 99765-4321", "JANLIMPEZA", 200),
        ("♻️ Oficina de Reciclagem de Papel", "Aprenda a fazer papel reciclado artesanal. Traga papéis usados.", "17/01/2026", "14:00", "SENAI", "Av. Luiz Ralph Benatti, 500 - Vila Industrial", "oficina", 30, "SENAI", "(19) 3412-5000", "JANPAPEL", 150),
        ("🌿 Palestra: Agricultura Urbana", "Como cultivar alimentos em pequenos espaços na cidade.", "24/01/2026", "10:00", "Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "palestra", 80, "Horto Municipal", "(19) 3434-5678", "JANAGRIC", 120),
        ("🚴 Pedal do Sol Nascente", "Passeio ciclístico ao amanhecer para celebrar o início do ano.", "31/01/2026", "06:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 200, "Ciclovida", "(19) 99876-1234", "JANPEDAL", 180),
        
        # FEVEREIRO 2026
        ("🌊 Expedição Rio Piracicaba - Verão", "Passeio de barco educativo com biólogos, observação de aves e plantas aquáticas.", "07/02/2026", "09:00", "Rua do Porto", "Rua do Porto - Centro", "passeio", 60, "Comitê PCJ", "(19) 3437-2000", "FEVEXPED", 200),
        ("🌱 Feira de Orgânicos Especial", "Edição de verão da feira orgânica com produtos sazonais e food trucks saudáveis.", "14/02/2026", "08:00", "Mercado Municipal", "Praça Dr. Alfredo Stead, 100 - Centro", "feira", 0, "Associação Orgânicos", "(19) 3434-7890", "FEVFEIRA", 120),
        ("♻️ Workshop de Compostagem para Apartamentos", "Técnicas de compostagem para quem mora em apartamento, com minhocas e composteiras compactas.", "21/02/2026", "15:00", "SESC", "Rua Ipiranga, 155 - Centro", "workshop", 40, "SESC", "(19) 3437-9292", "FEVCOMP", 180),
        ("🌿 Trilha Ecológica Noturna", "Trilha guiada no Parque Ecológico para observação de animais noturnos.", "28/02/2026", "19:00", "Parque Ecológico", "Av. Dr. Paulo de Moraes, 2000 - Santa Terezinha", "trilha", 50, "Parque Ecológico", "(19) 3434-1234", "FEVTRILHA", 200),
        
        # MARÇO 2026
        ("🌱 Feira de Sustentabilidade", "Feira com produtos orgânicos, artesanato sustentável e startups verdes. Haverá palestras, oficinas e food trucks com comida saudável.", "15/03/2026", "09:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "feira", 1000, "Prefeitura de Piracicaba", "(19) 3403-1100", "FEIRA2026", 150),
        ("♻️ Workshop de Reciclagem", "Aprenda técnicas avançadas de reciclagem em casa. Transforme materiais recicláveis em objetos úteis.", "22/03/2026", "14:00", "SENAI Piracicaba", "Av. Luiz Ralph Benatti, 500 - Vila Industrial", "workshop", 50, "SENAI", "(19) 3412-5000", "WORKSHOP01", 150),
        ("🌊 Mutirão Rio Piracicaba", "Limpeza das margens do rio com atividades educativas e distribuição de mudas.", "05/04/2026", "08:00", "Rua do Porto", "Rua do Porto - Centro", "mutirão", 200, "SOS Rio Piracicaba", "(19) 99765-4321", "MUTIRAO01", 200),
        ("🌿 Semana da Água 2026", "Palestras, oficinas e atividades sobre preservação dos recursos hídricos. Com participação de especialistas da USP.", "22/03/2026", "09:00", "ESALQ/USP", "Av. Pádua Dias, 11 - São Dimas", "palestra", 300, "ESALQ/USP", "(19) 3447-8500", "AGUA2026", 180),
        
        # ABRIL 2026
        ("🍃 Feira de Trocas Sustentáveis", "Traga objetos que não usa mais e troque por outros. Roupas, livros, brinquedos e eletrônicos.", "10/04/2026", "10:00", "Praça José Bonifácio", "Praça José Bonifácio - Centro", "feira", 0, "Coletivo Transition", "(19) 99876-5432", "TROCA2026", 120),
        ("🌳 Plantio do Dia da Terra", "Mutirão de plantio de 500 árvores nativas em comemoração ao Dia da Terra.", "22/04/2026", "08:30", "Parque Ecológico", "Av. Dr. Paulo de Moraes, 2000 - Santa Terezinha", "mutirão", 400, "SOS Mata Atlântica", "(11) 3262-4088", "PLANTIO22", 250),
        ("🐝 Oficina de Abelhas sem Ferrão", "Aprenda sobre a importância das abelhas nativas e como criar abelhas sem ferrão em casa.", "25/04/2026", "14:00", "ESALQ/USP", "Av. Pádua Dias, 11 - São Dimas", "oficina", 40, "USP", "(19) 3447-8500", "ABRABELHA", 180),
        ("♻️ Feira de Artesanato Reciclado", "Exposição e venda de artesanato feito com materiais reciclados.", "29/04/2026", "09:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "feira", 0, "Artesanato Solidário", "(19) 99888-7766", "ABRARTE", 120),
        
        # MAIO 2026
        ("🔋 Descarte de Eletrônicos", "Campanha de coleta de lixo eletrônico: computadores, celulares, pilhas e baterias.", "15/05/2026", "09:00", "Shopping Piracicaba", "Av. Limeira, 700 - Areão", "campanha", 0, "Green Eletronics", "(19) 3403-3000", "ELETRO26", 100),
        ("🚴 Pedal Verde", "Passeio ciclístico ecológico de 15km pelas áreas verdes da cidade.", "23/05/2026", "08:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 200, "Ciclovida", "(19) 99876-1234", "PEDAL26", 180),
        ("🌿 Dia do Sol - Energia Solar", "Feira de energia solar com expositores, palestras e oficinas sobre instalação de painéis solares.", "16/05/2026", "10:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "feira", 300, "CPFL Energia", "(19) 3421-2121", "MAISOL", 150),
        ("💧 Caminhada das Águas", "Caminhada de 5km pelas margens do rio conscientizando sobre a preservação da água.", "30/05/2026", "08:30", "Rua do Porto", "Rua do Porto - Centro", "caminhada", 500, "Comitê PCJ", "(19) 3437-2000", "MAIAGUA", 120),
        
        # JUNHO 2026
        ("🥕 Feira Agroecológica", "Feira de produtos orgânicos, agroecológicos e artesanato sustentável.", "05/06/2026", "08:00", "Mercado Municipal", "Praça Dr. Alfredo Stead, 100 - Centro", "feira", 0, "Associação Orgânicos", "(19) 3434-7890", "AGRO26", 120),
        ("🌍 Dia Mundial do Meio Ambiente", "Evento especial com shows, palestras, oficinas e feira de sustentabilidade.", "05/06/2026", "09:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "evento", 2000, "Prefeitura de Piracicaba", "(19) 3403-1100", "DIAMUNDIAL", 200),
        ("🌱 Oficina de Compostagem", "Aprenda a fazer compostagem doméstica e comunitária com minhocas californianas.", "15/06/2026", "14:00", "Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "oficina", 40, "Horto Municipal", "(19) 3434-5678", "COMPOST26", 150),
        ("♻️ Feira de Reciclagem Criativa", "Exposição e venda de produtos feitos com materiais reciclados. Oficinas de artesanato sustentável.", "20/06/2026", "10:00", "SESC Piracicaba", "Rua Ipiranga, 155 - Centro", "feira", 0, "SESC", "(19) 3437-9292", "RECICRIA", 150),
        ("🌿 Noite das Estrelas no Parque", "Observação astronômica no Parque Ecológico com astrônomos amadores.", "27/06/2026", "19:00", "Parque Ecológico", "Av. Dr. Paulo de Moraes, 2000 - Santa Terezinha", "evento", 150, "Observatório de Piracicaba", "(19) 3434-5678", "JUNESTRELAS", 180),
        
        # JULHO 2026
        ("🌿 Palestra: Energia Solar", "Como instalar e economizar com energia solar residencial.", "05/07/2026", "19:00", "Teatro Municipal", "Av. Independência, 100 - Centro", "palestra", 200, "CPFL Energia", "(19) 3421-2121", "SOLAR26", 120),
        ("💧 Expedição Rio Piracicaba", "Passeio de barco educativo pelas águas do rio com biólogos explicando o ecossistema.", "18/07/2026", "09:00", "Rua do Porto", "Rua do Porto - Centro", "passeio", 80, "Comitê PCJ", "(19) 3437-2000", "EXPED26", 200),
        ("🌳 Plantio de Árvores Frutíferas", "Mutirão de plantio de árvores frutíferas nativas em áreas urbanas.", "25/07/2026", "08:30", "Parque da Rua do Porto", "Rua do Porto - Centro", "mutirão", 150, "Projeto Pomar", "(19) 99888-7766", "FRUTAS26", 250),
        ("♻️ Férias Sustentáveis - Oficina para Crianças", "Oficinas de reciclagem e arte para crianças durante as férias.", "11/07/2026", "14:00", "SESC", "Rua Ipiranga, 155 - Centro", "oficina", 30, "SESC", "(19) 3437-9292", "JULCRIANCA", 180),
        ("🚴 Pedal Noturno", "Passeio ciclístico noturno pelas ruas de Piracicaba com iluminação especial.", "24/07/2026", "19:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 150, "Ciclovida", "(19) 99876-1234", "JULPEDAL", 180),
        
        # AGOSTO 2026
        ("🐝 Dia das Abelhas", "Palestra e oficina sobre a importância das abelhas para o meio ambiente e como criar abelhas sem ferrão.", "29/08/2026", "14:00", "ESALQ/USP", "Av. Pádua Dias, 11 - São Dimas", "palestra", 100, "USP", "(19) 3447-8500", "ABELHAS26", 150),
        ("🌱 Feira de Mudas Nativas", "Feira de troca e venda de mudas de árvores nativas do cerrado e mata atlântica.", "08/08/2026", "09:00", "Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "feira", 0, "Horto Municipal", "(19) 3434-5678", "AGOMUDAS", 120),
        ("♻️ Workshop de Upcycling de Móveis", "Aprenda a restaurar e transformar móveis velhos em peças novas e estilosas.", "15/08/2026", "14:00", "SENAC", "Rua Santa Cruz, 1145 - Centro", "workshop", 25, "SENAC", "(19) 3412-3000", "AGOUPCYCLE", 200),
        ("🌿 Caminhada Ecológica no Parque", "Caminhada guiada pelo Parque Ecológico com identificação de árvores e aves.", "22/08/2026", "08:00", "Parque Ecológico", "Av. Dr. Paulo de Moraes, 2000 - Santa Terezinha", "caminhada", 100, "Parque Ecológico", "(19) 3434-1234", "AGOCAMINHADA", 120),
        
        # SETEMBRO 2026
        ("♻️ Workshop de Upcycling", "Transforme roupas velhas em novas peças. Traga suas roupas e aprenda técnicas de customização.", "12/09/2026", "14:00", "SENAC Piracicaba", "Rua Santa Cruz, 1145 - Centro", "workshop", 30, "SENAC", "(19) 3412-3000", "UPCYCLE", 180),
        ("🚴 Bike na Rua", "Dia com ruas fechadas para bicicletas, com atividades, food trucks e música.", "20/09/2026", "09:00", "Av. Independência", "Av. Independência - Centro", "evento", 0, "Prefeitura de Piracicaba", "(19) 3403-1100", "BIKERUA", 150),
        ("🌱 Semana da Árvore", "Eventos durante toda a semana sobre a importância das árvores, com plantios e palestras.", "21/09/2026", "09:00", "Vários locais", "Diversos pontos da cidade", "evento", 0, "SOS Mata Atlântica", "(11) 3262-4088", "SETARVORE", 200),
        ("🌿 Palestra: Permacultura", "Introdução à permacultura e design de ecossistemas sustentáveis.", "26/09/2026", "10:00", "ESALQ/USP", "Av. Pádua Dias, 11 - São Dimas", "palestra", 80, "ESALQ", "(19) 3447-8500", "SETPERMA", 150),
        
        # OUTUBRO 2026
        ("🌱 Feira de Mudas", "Feira de troca e venda de mudas de árvores nativas, frutíferas e ornamentais.", "05/10/2026", "09:00", "Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "feira", 0, "Horto Municipal", "(19) 3434-5678", "MUDAS26", 120),
        ("💧 Fórum das Águas", "Encontro com especialistas discutindo a preservação dos recursos hídricos da região.", "18/10/2026", "08:30", "Acadêmico", "Rua São João, 500 - Centro", "palestra", 150, "Comitê PCJ", "(19) 3437-2000", "FORUMAGUA", 180),
        ("♻️ Semana Lixo Zero", "Eventos durante toda a semana sobre redução, reutilização e reciclagem de resíduos.", "25/10/2026", "09:00", "Vários locais", "Diversos pontos da cidade", "evento", 0, "Instituto Lixo Zero", "(11) 99999-8888", "LIXOZERO", 200),
        ("🌿 Oficina de Sabonetes Naturais", "Aprenda a fazer sabonetes e produtos de limpeza ecológicos.", "10/10/2026", "14:00", "SESC", "Rua Ipiranga, 155 - Centro", "oficina", 30, "SESC", "(19) 3437-9292", "OUTSABONETE", 150),
        ("🚴 Pedal da Primavera", "Passeio ciclístico para celebrar a primavera, com flores e cores.", "17/10/2026", "09:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 200, "Ciclovida", "(19) 99876-1234", "OUTPEDAL", 180),
        
        # NOVEMBRO 2026
        ("🌳 Plantio da Primavera", "Mutirão de plantio de árvores para celebrar a primavera.", "08/11/2026", "08:30", "Parque Ecológico", "Av. Dr. Paulo de Moraes, 2000 - Santa Terezinha", "mutirão", 300, "SOS Mata Atlântica", "(11) 3262-4088", "PRIMAVERA", 250),
        ("🥕 Feira Orgânica Especial", "Edição especial da feira orgânica com produtos sazonais e alimentos da reforma agrária.", "15/11/2026", "08:00", "Mercado Municipal", "Praça Dr. Alfredo Stead, 100 - Centro", "feira", 0, "Associação Orgânicos", "(19) 3434-7890", "ORGSPECIAL", 120),
        ("🌿 Encontro de Sustentabilidade", "Palestras e debates com líderes ambientais sobre o futuro sustentável de Piracicaba.", "22/11/2026", "09:00", "Teatro Municipal", "Av. Independência, 100 - Centro", "evento", 400, "ONG Planeta Verde", "(19) 99876-5432", "ENCONTRO26", 180),
        ("♻️ Feira de Troca de Livros e Brinquedos", "Traga livros e brinquedos usados em bom estado e troque por outros.", "14/11/2026", "10:00", "Praça José Bonifácio", "Praça José Bonifácio - Centro", "feira", 0, "Coletivo Cultural", "(19) 99888-7766", "NOVTROCA", 120),
        ("🚴 Pedal da Consciência Negra", "Passeio ciclístico em homenagem ao Dia da Consciência Negra, com música e cultura.", "20/11/2026", "09:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 200, "Ciclovida", "(19) 99876-1234", "NOVCONSCIENCIA", 180),
        
        # DEZEMBRO 2026
        ("♻️ Feira de Natal Sustentável", "Presentes sustentáveis, artesanato ecológico e decoração feita com materiais reciclados.", "05/12/2026", "10:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "feira", 0, "Prefeitura de Piracicaba", "(19) 3403-1100", "NATALECO", 150),
        ("🚴 Pedal de Natal", "Passeio ciclístico natalino com decoração temática e arrecadação de alimentos.", "12/12/2026", "18:00", "Largo dos Pescadores", "Rua do Porto - Centro", "passeio", 200, "Ciclovida", "(19) 99876-1234", "PEDALNATAL", 180),
        ("🌱 Natal Verde - Plantio de Árvores", "Plante uma árvore e ganhe uma muda para presentear no Natal.", "19/12/2026", "08:30", "Parque da Rua do Porto", "Rua do Porto - Centro", "mutirão", 150, "Projeto Pomar", "(19) 99888-7766", "DEZNATALVERDE", 250),
        ("🌿 Reveillon Sustentável", "Celebração de Ano Novo com fogos de artifício silenciosos e baixo impacto ambiental.", "31/12/2026", "22:00", "Engenho Central", "Av. Maurice Allain, 454 - Engenho Central", "evento", 2000, "Prefeitura de Piracicaba", "(19) 3403-1100", "DEZREVEILLON", 200),
        ("♻️ Feira de Artesanato de Natal", "Artesanato sustentável e ecológico para presentes de Natal.", "13/12/2026", "10:00", "Mercado Municipal", "Praça Dr. Alfredo Stead, 100 - Centro", "feira", 0, "Artesanato Solidário", "(19) 99888-7766", "DEZARTESANATO", 120)
    ]
    
    # Limpar eventos existentes e inserir novos
    c.execute("DELETE FROM eventos")
    for e in eventos:
        c.execute(
            """INSERT INTO eventos 
               (titulo, descricao, data, hora, local, endereco, tipo, vagas, organizador, contato, codigo_confirmacao, pontos_evento) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            e
        )
    
    # ===== PONTOS DE COLETA EM PIRACICABA (MEGA EXPANDIDO POR CATEGORIA) =====
    
    # 1. PONTOS GERAIS (Ecopontos)
    pontos_gerais = [
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "geral", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3403-1100", 4.5, "Recebe todos os tipos de recicláveis, eletrônicos e óleo de cozinha"),
        ("Ecoponto Paulicéia", "R. Javari, 150 - Paulicéia", "geral", "Ter-Sáb 8h-16h", "(19) 3403-2200", 4.3, "Ecoponto completo com coleta de óleo, recicláveis e eletrônicos"),
        ("Ecoponto Santa Terezinha", "Av. Dr. Paulo de Moraes, 1500 - Santa Terezinha", "geral", "Seg-Sáb 8h-17h", "(19) 3403-2300", 4.4, "Recebe recicláveis, entulho e resíduos volumosos"),
        ("Ecoponto Vila Sônia", "R. Benedito Tolosa, 500 - Vila Sônia", "geral", "Seg-Sáb 8h-17h", "(19) 3403-2400", 4.2, "Ponto de entrega voluntária de recicláveis"),
        ("Ecoponto Nova Piracicaba", "Av. Cruzeiro do Sul, 2000 - Nova Piracicaba", "geral", "Seg-Sáb 8h-17h", "(19) 3403-2500", 4.6, "Ecoponto moderno com coleta seletiva completa"),
        ("Ecoponto Vila Rezende", "R. dos Operários, 500 - Vila Rezende", "geral", "Seg-Sáb 8h-16h", "(19) 3403-2600", 4.3, "Ponto de coleta para a região norte"),
        ("Ecoponto Ártemis", "Av. 1º de Agosto, 1000 - Ártemis", "geral", "Seg-Sáb 8h-16h", "(19) 3403-2700", 4.2, "Ecoponto para o distrito de Ártemis"),
        ("Ecoponto Tupi", "R. Tiradentes, 300 - Tupi", "geral", "Seg-Sáb 8h-16h", "(19) 3403-2800", 4.1, "Ponto de coleta para o distrito de Tupi"),
    ]
    
    # 2. PILHAS E BATERIAS
    pontos_pilhas = [
        ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "pilhas", "Seg-Sáb 10h-22h, Dom 14h-20h", "(19) 3432-4545", 4.8, "Ponto de coleta de pilhas e baterias no piso G1"),
        ("Unimed Sede", "R. Voluntários, 450 - Centro", "pilhas", "Seg-Sex 7h-19h", "(19) 3432-9000", 4.6, "Coleta de pilhas e baterias na recepção"),
        ("Hospital dos Fornecedores", "R. Dr. Paulo Pinto, 500 - Cidade Alta", "pilhas", "Seg-Sex 8h-18h", "(19) 3421-3000", 4.5, "Ponto de coleta de pilhas no saguão principal"),
        ("Santa Casa de Piracicaba", "Av. Independência, 950 - Centro", "pilhas", "Seg-Sex 8h-18h", "(19) 3412-2000", 4.4, "Coletores de pilhas na entrada principal"),
        ("Prefeitura Municipal", "R. Antônio Corrêa Barbosa, 2233 - Centro Cívico", "pilhas", "Seg-Sex 8h-17h", "(19) 3403-1000", 4.5, "Coletores no hall de entrada"),
        ("Câmara Municipal", "R. do Rosário, 833 - Centro", "pilhas", "Seg-Sex 8h-17h", "(19) 3403-1500", 4.4, "Ponto de coleta no saguão"),
        ("Terminal Central de Ônibus", "Av. Dr. Paulo de Moraes, 200 - Centro", "pilhas", "Seg-Dom 5h-23h", "(19) 3403-3000", 4.3, "Coletores no terminal"),
        ("Estação da Paulista", "Av. Rio Claro, 500 - Paulista", "pilhas", "Seg-Dom 5h-23h", "(19) 3403-3100", 4.2, "Ponto de coleta na estação"),
    ]
    
    # 3. ELETRÔNICOS
    pontos_eletronicos = [
        ("CDI Eletrônicos", "R. do Porto, 234 - Centro", "eletronicos", "Seg-Sex 9h-18h, Sáb 9h-12h", "(19) 3433-5678", 4.7, "Centro de Descarte de Eletrônicos - computadores, celulares e pilhas"),
        ("Associação Comercial", "R. Gov. Pedro de Toledo, 345 - Centro", "eletronicos", "Seg-Sex 9h-17h", "(19) 3412-4500", 4.3, "Ponto de coleta de eletrônicos para reciclagem"),
        ("ESALQ/USP", "Av. Pádua Dias, 11 - Agronomia", "eletronicos", "Seg-Sex 8h-17h", "(19) 3447-8500", 4.9, "Campus da ESALQ com pontos de coleta de eletrônicos"),
        ("UNIMEP", "R. do Rosário, 1301 - Centro", "eletronicos", "Seg-Sex 8h-22h", "(19) 3421-3000", 4.7, "Universidade Metodista com pontos de coleta"),
        ("FUMEP", "Av. Monsenhor Martinho Salgot, 560 - Areião", "eletronicos", "Seg-Sex 8h-17h", "(19) 3412-4000", 4.4, "Fundação Municipal de Ensino"),
        ("Senai", "Av. Luiz Ralph Benatti, 500 - Vila Industrial", "eletronicos", "Seg-Sex 8h-17h", "(19) 3412-5000", 4.6, "Escola técnica com ponto de coleta"),
        ("Sesc", "R. Ipiranga, 155 - Centro", "eletronicos", "Seg-Sex 9h-21h, Sáb 9h-17h", "(19) 3437-9292", 4.8, "Unidade Sesc com coletores"),
        ("Sesi", "Av. Luiz Ralph Benatti, 700 - Vila Industrial", "eletronicos", "Seg-Sex 8h-17h", "(19) 3412-6000", 4.5, "Ponto de coleta no Sesi"),
    ]
    
    # 4. ÓLEO DE COZINHA
    pontos_oleo = [
        ("Oleobom", "R. São João, 678 - Centro", "oleo", "Seg-Sex 9h-18h, Sáb 9h-13h", "(19) 3421-5678", 4.6, "Ponto de coleta de óleo de cozinha usado"),
        ("Supermercados Pague Menos", "Av. Limeira, 1200 - Areão", "oleo", "Seg-Dom 8h-22h", "(19) 3434-2000", 4.5, "Coletores de óleo no estacionamento"),
        ("Supermercados Savegnago", "Av. Cruzeiro do Sul, 800 - Nova Piracicaba", "oleo", "Seg-Dom 8h-22h", "(19) 3433-3000", 4.7, "Ponto de coleta de óleo usado"),
        ("Supermercados Covabra", "Av. Limeira, 1500 - Areão", "oleo", "Seg-Dom 8h-22h", "(19) 3434-4000", 4.6, "Coletores de óleo na entrada"),
        ("Supermercados São Vicente", "R. do Porto, 500 - Centro", "oleo", "Seg-Dom 8h-22h", "(19) 3421-7000", 4.5, "Ponto de coleta de óleo"),
        ("Atacadão", "Av. Limeira, 2000 - Areão", "oleo", "Seg-Dom 8h-22h", "(19) 3434-5000", 4.4, "Coletores de óleo no estacionamento"),
        ("Associação Comercial", "R. Gov. Pedro de Toledo, 345 - Centro", "oleo", "Seg-Sex 9h-17h", "(19) 3412-4500", 4.3, "Ponto de coleta de óleo"),
        ("Feira Noturna", "Praça José Bonifácio - Centro", "oleo", "Qui 17h-22h", "(19) 3403-1100", 4.2, "Ponto de coleta durante a feira"),
    ]
    
    # 5. VIDROS
    pontos_vidros = [
        ("Coopervidros", "R. Treze de Maio, 300 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3421-1234", 4.2, "Cooperativa especializada em reciclagem de vidros"),
        ("Recicla Vidros", "Av. Rio Claro, 450 - Vila Industrial", "vidros", "Seg-Sex 8h-16h", "(19) 3434-5678", 4.3, "Recebimento de vidros para reciclagem"),
        ("Vidrocenter", "R. do Vergueiro, 600 - Centro", "vidros", "Seg-Sex 8h-18h", "(19) 3422-3344", 4.4, "Empresa especializada em vidros"),
        ("Cooperativa Recicla Piracicaba", "R. dos Operários, 200 - Centro", "vidros", "Seg-Sex 8h-16h", "(19) 3422-3344", 4.3, "Recebimento de vidros"),
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "vidros", "Seg-Sex 8h-17h", "(19) 3403-1100", 4.5, "Recebe vidros no ecoponto"),
        ("Ecoponto Paulicéia", "R. Javari, 150 - Paulicéia", "vidros", "Ter-Sáb 8h-16h", "(19) 3403-2200", 4.3, "Recebe vidros"),
        ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "vidros", "Seg-Sáb 10h-22h", "(19) 3432-4545", 4.5, "Coletores de vidros no estacionamento"),
        ("Bares e Restaurantes", "R. do Porto, 400 - Centro", "vidros", "Parceria com estabelecimentos", "(19) 99888-7766", 4.2, "Rede de coleta em bares parceiros"),
    ]
    
    # 6. PAPEL E PAPELÃO
    pontos_papel = [
        ("Cooperativa Recicla Piracicaba", "R. dos Operários, 200 - Centro", "papel", "Seg-Sex 8h-16h", "(19) 3422-3344", 4.4, "Cooperativa de catadores de papel e papelão"),
        ("Papelão Recicla", "Av. Independência, 1800 - Centro", "papel", "Seg-Sex 8h-17h", "(19) 3433-4455", 4.2, "Compra e recebimento de papelão"),
        ("Recicla Papel", "R. do Porto, 567 - Centro", "papel", "Seg-Sex 8h-16h", "(19) 3423-4567", 4.3, "Recebimento de papel e papelão"),
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "papel", "Seg-Sex 8h-17h", "(19) 3403-1100", 4.5, "Recebe papel e papelão"),
        ("Escolas Municipais", "Diversos endereços", "papel", "Seg-Sex 8h-17h", "(19) 3403-1800", 4.3, "Rede de coleta nas escolas"),
        ("Faculdades", "Campus UNIMEP e ESALQ", "papel", "Seg-Sex 8h-22h", "(19) 3421-3000", 4.6, "Pontos de coleta nas universidades"),
        ("Prédios Comerciais", "Centro empresarial", "papel", "Seg-Sex 8h-18h", "(19) 3422-3344", 4.2, "Coleta seletiva em edifícios comerciais"),
        ("Gráficas", "Av. Rio Claro, 300 - Centro", "papel", "Seg-Sex 8h-18h", "(19) 3423-4567", 4.3, "Parceria com gráficas para coleta de aparas"),
    ]
    
    # 7. PLÁSTICOS
    pontos_plasticos = [
        ("Recicla Plásticos", "R. do Porto, 567 - Centro", "plasticos", "Seg-Sex 8h-16h", "(19) 3423-4567", 4.3, "Recebimento de todos os tipos de plásticos"),
        ("Plástico Verde", "Av. Cruzeiro do Sul, 1500 - Nova Piracicaba", "plasticos", "Seg-Sex 8h-17h", "(19) 3434-6789", 4.5, "Reciclagem de plásticos PET e PVC"),
        ("Cooperativa Recicla", "R. dos Operários, 200 - Centro", "plasticos", "Seg-Sex 8h-16h", "(19) 3422-3344", 4.4, "Recebimento de plásticos"),
        ("Ecoponto Santa Terezinha", "Av. Dr. Paulo de Moraes, 1500", "plasticos", "Seg-Sáb 8h-17h", "(19) 3403-2300", 4.4, "Recebe plásticos"),
        ("Supermercados", "Rede Pague Menos", "plasticos", "Seg-Dom 8h-22h", "(19) 3434-2000", 4.5, "Coletores de plásticos nos mercados"),
        ("Escolas", "Rede municipal", "plasticos", "Seg-Sex 8h-17h", "(19) 3403-1800", 4.3, "Programa Escola Sustentável"),
        ("Condomínios", "Diversos endereços", "plasticos", "24h", "(19) 99888-7766", 4.2, "Coleta seletiva em condomínios"),
        ("Indústrias", "Distrito Industrial", "plasticos", "Seg-Sex 8h-17h", "(19) 3423-4567", 4.4, "Parceria com indústrias"),
    ]
    
    # 8. RESÍDUOS ORGÂNICOS
    pontos_organicos = [
        ("Horto Municipal", "Av. Maurílio Biagi, 1500 - Santa Cecília", "organicos", "Seg-Sex 8h-16h", "(19) 3434-5678", 4.3, "Recebimento de podas e resíduos orgânicos"),
        ("Feira Noturna", "Praça José Bonifácio - Centro", "organicos", "Qui 17h-22h", "(19) 3403-1100", 4.1, "Ponto de coleta de resíduos orgânicos da feira"),
        ("Feira do Areião", "Av. Limeira - Areão", "organicos", "Sáb 7h-12h", "(19) 3403-1100", 4.2, "Coleta de orgânicos na feira"),
        ("Feira da Paulista", "Av. Rio Claro - Paulista", "organicos", "Dom 7h-12h", "(19) 3403-1100", 4.1, "Ponto de coleta de orgânicos"),
        ("Composteiras Comunitárias", "Praça José Bonifácio", "organicos", "24h", "(19) 99888-7766", 4.5, "Composteira comunitária para resíduos de feira"),
        ("Restaurantes Parceiros", "Centro", "organicos", "Parceria", "(19) 99888-7766", 4.3, "Coleta de orgânicos em restaurantes"),
        ("Sítios e Chácaras", "Zona rural", "organicos", "Parceria", "(19) 99888-7766", 4.4, "Programa de compostagem rural"),
        ("Escolas com Composteira", "Rede municipal", "organicos", "Seg-Sex", "(19) 3403-1800", 4.5, "Escolas com projeto de compostagem"),
    ]
    
    # 9. MEDICAMENTOS VENCIDOS
    pontos_medicamentos = [
        ("Farmácias Pague Menos", "Av. Independência, 1000 - Centro", "medicamentos", "Seg-Dom 8h-22h", "(19) 3412-9000", 4.6, "Coleta de medicamentos vencidos"),
        ("Drogasil", "Rua do Rosário, 500 - Centro", "medicamentos", "Seg-Dom 8h-22h", "(19) 3421-8000", 4.5, "Descarte correto de medicamentos"),
        ("Droga Raia", "Av. Limeira, 800 - Areão", "medicamentos", "Seg-Dom 8h-22h", "(19) 3434-7000", 4.6, "Coleta de medicamentos"),
        ("Farmácias São João", "R. Gov. Pedro de Toledo, 400 - Centro", "medicamentos", "Seg-Dom 8h-22h", "(19) 3421-9000", 4.5, "Ponto de coleta"),
        ("Farmácias Drogal", "Av. Cruzeiro do Sul, 1000 - Nova Piracicaba", "medicamentos", "Seg-Dom 8h-22h", "(19) 3433-8000", 4.4, "Descarte de medicamentos"),
        ("Farmácia Municipal", "R. do Rosário, 200 - Centro", "medicamentos", "Seg-Sex 8h-17h", "(19) 3403-1700", 4.7, "Farmácia pública com coleta"),
        ("UBSs", "Diversos endereços", "medicamentos", "Seg-Sex 8h-17h", "(19) 3403-1800", 4.5, "Unidades Básicas de Saúde com coleta"),
        ("Hospitais", "Santa Casa, Unimed", "medicamentos", "Seg-Sex 8h-18h", "(19) 3412-2000", 4.6, "Hospitais com pontos de coleta"),
    ]
    
    # 10. LÂMPADAS
    pontos_lampadas = [
        ("Lumi Recicla", "Av. Rio Claro, 800 - Vila Industrial", "lampadas", "Seg-Sex 9h-17h", "(19) 3433-2121", 4.4, "Reciclagem de lâmpadas fluorescentes e LED"),
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "lampadas", "Seg-Sex 8h-17h", "(19) 3403-1100", 4.5, "Recebe lâmpadas para reciclagem"),
        ("Ecoponto Paulicéia", "R. Javari, 150 - Paulicéia", "lampadas", "Ter-Sáb 8h-16h", "(19) 3403-2200", 4.3, "Recebe lâmpadas"),
        ("Shopping Piracicaba", "Av. Limeira, 700 - Areão", "lampadas", "Seg-Sáb 10h-22h", "(19) 3432-4545", 4.6, "Ponto de coleta de lâmpadas"),
        ("Home Center", "Av. Limeira, 1500 - Areão", "lampadas", "Seg-Dom 8h-20h", "(19) 3434-9000", 4.5, "Lojas de material de construção com coleta"),
        ("Leroy Merlin", "Av. Limeira, 1800 - Areão", "lampadas", "Seg-Dom 8h-20h", "(19) 3434-9500", 4.7, "Coleta de lâmpadas"),
        ("Prefeitura", "R. Antônio Corrêa Barbosa, 2233", "lampadas", "Seg-Sex 8h-17h", "(19) 3403-1000", 4.4, "Ponto de coleta no Centro Cívico"),
        ("Câmara Municipal", "R. do Rosário, 833 - Centro", "lampadas", "Seg-Sex 8h-17h", "(19) 3403-1500", 4.3, "Coleta de lâmpadas"),
    ]
    
    # 11. ROUPAS E TECIDOS
    pontos_roupas = [
        ("Brechó Solidário", "R. Governador, 400 - Centro", "roupas", "Seg-Sex 9h-17h", "(19) 3421-4321", 4.5, "Doação de roupas para projetos sociais"),
        ("Casa da Fraternidade", "R. do Vergueiro, 200 - Centro", "roupas", "Seg-Sex 8h-16h", "(19) 3422-1234", 4.7, "Ponto de coleta de roupas e agasalhos"),
        ("Igrejas", "Diversas paróquias", "roupas", "Parceria", "(19) 3422-1234", 4.5, "Rede de coleta em igrejas"),
        ("Escolas", "Rede municipal e estadual", "roupas", "Seg-Sex", "(19) 3403-1800", 4.4, "Campanhas do agasalho"),
        ("Sesc", "R. Ipiranga, 155 - Centro", "roupas", "Seg-Sex 9h-21h", "(19) 3437-9292", 4.6, "Ponto permanente de coleta"),
        ("Senac", "R. Santa Cruz, 1145 - Centro", "roupas", "Seg-Sex 8h-17h", "(19) 3412-3000", 4.5, "Coleta de roupas"),
        ("Faculdades", "ESALQ, UNIMEP", "roupas", "Seg-Sex", "(19) 3447-8500", 4.6, "Pontos de coleta nas universidades"),
        ("Condomínios", "Diversos endereços", "roupas", "24h", "(19) 99888-7766", 4.3, "Coleta em condomínios"),
    ]
    
    # 12. MÓVEIS E ELETRODOMÉSTICOS
    pontos_moveis = [
        ("Ecoponto Volumosos", "Av. Limeira, 2000 - Areão", "moveis", "Seg-Sáb 8h-16h", "(19) 3403-2500", 4.2, "Recebimento de móveis e eletrodomésticos inservíveis"),
        ("Ecoponto Santa Terezinha", "Av. Dr. Paulo de Moraes, 1500", "moveis", "Seg-Sáb 8h-17h", "(19) 3403-2300", 4.3, "Recebe móveis e eletros"),
        ("Ecoponto Vila Sônia", "R. Benedito Tolosa, 500", "moveis", "Seg-Sáb 8h-17h", "(19) 3403-2400", 4.2, "Recebe resíduos volumosos"),
        ("Associação Comercial", "R. Gov. Pedro de Toledo, 345", "moveis", "Seg-Sex 9h-17h", "(19) 3412-4500", 4.1, "Campanhas pontuais"),
        ("Sindloja", "R. do Rosário, 700 - Centro", "moveis", "Seg-Sex 9h-17h", "(19) 3421-5000", 4.2, "Parceria com lojistas"),
        ("Lojas de Móveis", "Diversos endereços", "moveis", "Parceria", "(19) 99888-7766", 4.1, "Programa de logística reversa"),
        ("Condomínios", "Diversos", "moveis", "Agendamento", "(19) 3403-2500", 4.0, "Coleta agendada de volumosos"),
        ("Cooperativas", "R. dos Operários, 200", "moveis", "Seg-Sex 8h-16h", "(19) 3422-3344", 4.3, "Recebimento para reciclagem"),
    ]
    
    # 13. FERRO VELHO E METAIS
    pontos_metais = [
        ("Ferro Velho Central", "Av. Rio Claro, 600 - Centro", "metais", "Seg-Sex 8h-17h, Sáb 8h-12h", "(19) 3421-6000", 4.3, "Compra de sucata e metais"),
        ("Reciclagem de Metais", "R. dos Operários, 300 - Centro", "metais", "Seg-Sex 8h-17h", "(19) 3422-4455", 4.4, "Recebimento de metais ferrosos e não ferrosos"),
        ("Sucata Piracicaba", "Av. Cruzeiro do Sul, 500 - Nova Piracicaba", "metais", "Seg-Sex 8h-17h", "(19) 3433-5566", 4.3, "Compra de sucata"),
        ("Ecoponto Centro", "Av. Rui Barbosa, 800 - Centro", "metais", "Seg-Sex 8h-17h", "(19) 3403-1100", 4.4, "Recebe metais"),
        ("Indústrias", "Distrito Industrial", "metais", "Parceria", "(19) 3421-6000", 4.5, "Parceria com indústrias"),
        ("Oficinas Mecânicas", "Diversos", "metais", "Parceria", "(19) 99888-7766", 4.2, "Coleta de peças e sucata"),
        ("Sucatas de Carros", "Estrada da Velha", "metais", "Seg-Sex 8h-17h", "(19) 3421-6000", 4.1, "Compra de veículos para reciclagem"),
        ("Cooperativas", "R. dos Operários, 200", "metais", "Seg-Sex 8h-16h", "(19) 3422-3344", 4.4, "Recebimento de metais"),
    ]
    
    # 14. PILHAS E BATERIAS (LUGARES ADICIONAIS)
    pontos_pilhas_extra = [
        ("Farmácias Drogasil", "Av. Independência, 800 - Centro", "pilhas", "Seg-Dom 8h-22h", "(19) 3421-8000", 4.5, "Coletores de pilhas"),
        ("Farmácias Pague Menos", "Av. Limeira, 900 - Areão", "pilhas", "Seg-Dom 8h-22h", "(19) 3434-2000", 4.5, "Coletores de pilhas"),
        ("Supermercados Covabra", "Av. Cruzeiro do Sul, 1000", "pilhas", "Seg-Dom 8h-22h", "(19) 3433-4000", 4.5, "Coletores de pilhas"),
        ("Sesc", "R. Ipiranga, 155 - Centro", "pilhas", "Seg-Sex 9h-21h", "(19) 3437-9292", 4.6, "Coletores de pilhas"),
        ("Sesi", "Av. Luiz Ralph Benatti, 700", "pilhas", "Seg-Sex 8h-17h", "(19) 3412-6000", 4.4, "Coletores de pilhas"),
        ("ESALQ", "Av. Pádua Dias, 11", "pilhas", "Seg-Sex 8h-17h", "(19) 3447-8500", 4.8, "Coletores nos departamentos"),
        ("UNIMEP", "R. do Rosário, 1301", "pilhas", "Seg-Sex 8h-22h", "(19) 3421-3000", 4.6, "Coletores no campus"),
        ("Escolas Estaduais", "Diversos", "pilhas", "Seg-Sex 8h-17h", "(19) 3403-1800", 4.3, "Programa Escola Sustentável"),
    ]
    
    # Limpar pontos existentes e inserir novos
    c.execute("DELETE FROM pontos_coleta")
    
    # Combinar todos os pontos
    todos_pontos = (
        pontos_gerais + pontos_pilhas + pontos_eletronicos + pontos_oleo + 
        pontos_vidros + pontos_papel + pontos_plasticos + pontos_organicos + 
        pontos_medicamentos + pontos_lampadas + pontos_roupas + pontos_moveis + 
        pontos_metais + pontos_pilhas_extra
    )
    
    for p in todos_pontos:
        c.execute(
            "INSERT INTO pontos_coleta (nome, endereco, categoria, horario, telefone, avaliacao, descricao) VALUES (?, ?, ?, ?, ?, ?, ?)",
            p
        )
    
    # Dicas
    c.execute("DELETE FROM dicas")
    dicas = [
        ("🌱 Compostagem Doméstica", "50% do lixo doméstico pode ser compostado! Faça sua própria composteira com baldes e minhocas californianas. Use restos de frutas, verduras e cascas de ovos.", "resíduos", data_atual, 0, "Equipe SustentaPira"),
        ("💧 Economia de Água", "Um banho de 15 minutos gasta 135 litros. Reduza para 5 minutos e economize 90 litros por banho! Instale arejadores nas torneiras.", "água", data_atual, 0, "Sabesp"),
        ("🔋 Pilhas e Baterias", "Uma pilha pode contaminar 20 mil litros de água por até 50 anos. Descarte sempre em pontos de coleta específicos.", "resíduos", data_atual, 0, "Greenpeace"),
        ("🌳 Plante uma Árvore", "Uma árvore adulta absorve até 150kg de CO2 por ano. Plante árvores nativas como ipê, pitanga e jatobá.", "natureza", data_atual, 0, "SOS Mata Atlântica"),
        ("🛍️ Sacolas Retornáveis", "Uma sacola plástica leva 400 anos para se decompor. Use sempre sacolas retornáveis nas compras.", "plástico", data_atual, 0, "WWF"),
        ("🥗 Alimentação Orgânica", "Alimentos orgânicos são mais saudáveis e não contaminam o solo com agrotóxicos. Prefira produtos da agricultura familiar.", "alimentação", data_atual, 0, "Feira Orgânica"),
        ("♻️ Separação de Lixo", "Separe sempre o lixo seco (reciclável) do úmido (orgânico). Lave as embalagens antes de descartar.", "reciclagem", data_atual, 0, "Prefeitura de Piracicaba"),
        ("🚲 Mobilidade Sustentável", "Use bicicleta para trajetos curtos. Além de saudável, reduz a emissão de poluentes.", "mobilidade", data_atual, 0, "Ciclovida"),
        ("🧴 Óleo de Cozinha", "1 litro de óleo contamina 1 milhão de litros de água. Guarde em garrafas PET e leve aos pontos de coleta.", "resíduos", data_atual, 0, "Oleobom"),
        ("📱 Eletrônicos", "Celulares e computadores contêm metais pesados. Nunca descarte no lixo comum.", "eletrônicos", data_atual, 0, "CDI Eletrônicos"),
        ("💊 Medicamentos", "Medicamentos vencidos não devem ser jogados no lixo ou pia. Farmárias têm pontos de coleta.", "saúde", data_atual, 0, "Anvisa"),
        ("👕 Roupas", "Doe roupas que não usa mais. Tecidos levam anos para se decompor em aterros.", "têxtil", data_atual, 0, "Casa da Fraternidade"),
    ]
    
    for d in dicas:
        c.execute(
            "INSERT INTO dicas (titulo, conteudo, categoria, data_publicacao, likes, autor) VALUES (?, ?, ?, ?, ?, ?)",
            d
        )

# ===== FUNÇÃO PARA VERIFICAR DADOS =====
def verificar_dados():
    """Verifica quantos eventos e pontos foram inseridos"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM eventos")
    total_eventos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM pontos_coleta")
    total_pontos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dicas")
    total_dicas = c.fetchone()[0]
    conn.close()
    print(f"\n📊 VERIFICAÇÃO DE DADOS:")
    print(f"   - Eventos: {total_eventos}")
    print(f"   - Pontos de coleta: {total_pontos}")
    print(f"   - Dicas: {total_dicas}\n")
    return total_eventos, total_pontos

# Inicializar banco
init_database()

# Verificar dados inseridos
verificar_dados()

# ========== FUNÇÕES DE PROGRESSO ==========

def get_user_data(user_id):
    """Busca dados completos do usuário"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    # Verificar se usuário está banido
    c.execute("SELECT banido, motivo_ban FROM usuarios WHERE id = ?", (user_id,))
    banido = c.fetchone()
    if banido and banido[0] == 1:
        conn.close()
        return None, None, None, None, None, None, None, None, banido[1]
    
    # Dados do usuário
    c.execute("SELECT nome, email, cidade, data_cadastro FROM usuarios WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    # Adicionar telefone como string vazia se não existir
    telefone = ""
    if user:
        try:
            c.execute("SELECT telefone FROM usuarios WHERE id = ?", (user_id,))
            telefone_result = c.fetchone()
            if telefone_result and telefone_result[0]:
                telefone = telefone_result[0]
        except:
            telefone = ""
        user = (user[0], user[1], telefone, user[2], user[3])
    
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
    
    return user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites, None

def criar_usuario(nome, email, senha, telefone=""):
    """Cria um novo usuário no banco"""
    conn = None
    try:
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        # Verificar se email já existe
        c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if c.fetchone():
            return False, None, "Este e-mail já está cadastrado!"
        
        # Inserir usuário
        c.execute(
            "INSERT INTO usuarios (nome, email, senha, telefone, data_cadastro) VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha, telefone, data_atual)
        )
        
        # Pegar ID do usuário
        user_id = c.lastrowid
        
        # Inserir progresso
        c.execute(
            "INSERT INTO progresso (usuario_id, total_pontos, nivel, ultima_atividade) VALUES (?, ?, ?, ?)",
            (user_id, 0, "🌱 EcoIniciante", data_atual)
        )
        
        # Gerar código de convite
        codigo = hashlib.md5(f"{user_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
        c.execute(
            "INSERT INTO convites (usuario_id, codigo, data_criacao) VALUES (?, ?, ?)",
            (user_id, codigo, data_atual)
        )
        
        conn.commit()
        return True, user_id, "Conta criada com sucesso! Faça o login."
    except sqlite3.IntegrityError:
        return False, None, "Erro ao criar conta. Tente novamente."
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False, None, "Erro ao criar conta. Tente novamente."
    finally:
        if conn:
            conn.close()

def fazer_login(email, senha):
    """Faz login do usuário"""
    conn = None
    try:
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        
        # Buscar usuário com email e senha
        c.execute("SELECT id, nome, banido FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        resultado = c.fetchone()
        
        if resultado:
            user_id, nome, banido = resultado
            
            # Verificar se está banido
            if banido == 1:
                conn.close()
                return None, "Usuário banido por atividades suspeitas."
            
            # Atualizar último acesso
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.execute("UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?", (data_atual, user_id))
            
            # Atualizar streak
            c.execute("SELECT ultima_atividade FROM progresso WHERE usuario_id = ?", (user_id,))
            row = c.fetchone()
            
            if row and row[0]:
                try:
                    ultima_data_str = row[0].split()[0] if ' ' in row[0] else row[0]
                    ultima_data = datetime.strptime(ultima_data_str, "%d/%m/%Y")
                    hoje = datetime.now()
                    
                    diff_dias = (hoje.date() - ultima_data.date()).days
                    
                    if diff_dias == 1:
                        c.execute("UPDATE progresso SET streak_dias = streak_dias + 1 WHERE usuario_id = ?", (user_id,))
                    elif diff_dias > 1:
                        c.execute("UPDATE progresso SET streak_dias = 1 WHERE usuario_id = ?", (user_id,))
                except Exception as e:
                    print(f"Erro ao calcular streak: {e}")
            
            # Atualizar última atividade
            c.execute("UPDATE progresso SET ultima_atividade = ? WHERE usuario_id = ?", (data_atual, user_id))
            
            conn.commit()
            conn.close()
            return (user_id, nome), None
        else:
            conn.close()
            return None, "E-mail ou senha inválidos"
            
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return None, f"Erro ao fazer login: {str(e)}"
    finally:
        if conn:
            conn.close()

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
        novos_pontos = resultado[0] + pontos
        novo_nivel = get_nivel(novos_pontos)
        
        c.execute(
            "UPDATE progresso SET total_pontos = ?, nivel = ?, ultima_atividade = ? WHERE usuario_id = ?",
            (novos_pontos, novo_nivel, data_atual, usuario_id)
        )
    
    # Atualizar estatísticas específicas
    if tipo == "reciclagem":
        c.execute("UPDATE progresso SET kg_reciclados = kg_reciclados + 10 WHERE usuario_id = ?", (usuario_id,))
    elif tipo == "plantio":
        c.execute("UPDATE progresso SET arvores_plantadas = arvores_plantadas + 1 WHERE usuario_id = ?", (usuario_id,))
    
    conn.commit()
    conn.close()
    return True

def salvar_comprovante(usuario_id, tipo, descricao, imagem_bytes):
    """Salva comprovante com validação básica"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    image_hash = hashlib.md5(imagem_bytes).hexdigest()
    
    # Validar imagem básica
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes))
        
        # Verificar tamanho mínimo
        if len(imagem_bytes) < 1024:
            conn.close()
            return False, "Imagem muito pequena. Tire uma foto de melhor qualidade.", 0
        
        # Verificar dimensões
        if imagem.width < 200 or imagem.height < 200:
            conn.close()
            return False, "Resolução muito baixa. Tire uma foto mais nítida.", 0
        
    except Exception as e:
        conn.close()
        return False, "Arquivo de imagem inválido.", 0
    
    # Verificar se já existe
    c.execute("SELECT id FROM comprovantes WHERE imagem_hash = ?", (image_hash,))
    if c.fetchone():
        conn.close()
        return False, "Esta foto já foi enviada antes.", 0
    
    # Buscar desafio para pontos
    desafio = next((d for d in DESAFIOS_LISTA if d["tipo"] == tipo), None)
    pontos = desafio["pontos"] if desafio else 100
    
    # Salvar comprovante
    try:
        c.execute(
            """INSERT INTO comprovantes 
               (usuario_id, tipo, descricao, imagem, imagem_hash, pontos_ganhos, data, aprovado) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (usuario_id, tipo, descricao, imagem_bytes, image_hash, pontos, data_atual, 1)
        )
        
        conn.commit()
        conn.close()
        
        # Adicionar pontos
        adicionar_pontos(usuario_id, pontos, f"Completou: {descricao}", desafio["icone"], tipo)
        
        return True, f"Comprovante validado! Você ganhou {pontos} pontos.", pontos
        
    except Exception as e:
        conn.close()
        print(f"Erro ao salvar: {e}")
        return False, "Erro ao salvar comprovante.", 0

def get_ranking():
    """Busca ranking de usuários"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT u.nome, p.total_pontos, p.nivel
        FROM usuarios u
        JOIN progresso p ON u.id = p.usuario_id
        WHERE u.banido = 0
        ORDER BY p.total_pontos DESC
        LIMIT 20
    """)
    
    ranking = c.fetchall()
    conn.close()
    
    return ranking

def inscrever_evento(usuario_id, evento_id, nome, email, telefone):
    """Inscreve usuário em evento com ficha de inscrição"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    
    try:
        # Verificar se evento existe e tem vagas
        c.execute("SELECT titulo, vagas, inscritos, pontos_evento FROM eventos WHERE id = ?", (evento_id,))
        evento = c.fetchone()
        
        if not evento:
            conn.close()
            return False, "Evento não encontrado."
        
        titulo, vagas, inscritos, pontos_evento = evento
        
        if vagas > 0 and inscritos >= vagas:
            conn.close()
            return False, "Evento sem vagas disponíveis."
        
        # Verificar se já está inscrito
        c.execute("SELECT id FROM inscricoes WHERE usuario_id = ? AND evento_id = ?", (usuario_id, evento_id))
        if c.fetchone():
            conn.close()
            return False, "Você já está inscrito neste evento."
        
        # Inserir inscrição com dados completos
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        codigo = hashlib.md5(f"{usuario_id}{evento_id}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
        
        c.execute(
            """INSERT INTO inscricoes 
               (usuario_id, evento_id, data_inscricao, codigo_confirmacao, nome_participante, email_participante, telefone_participante) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (usuario_id, evento_id, data_atual, codigo, nome, email, telefone)
        )
        
        c.execute("UPDATE eventos SET inscritos = inscritos + 1 WHERE id = ?", (evento_id,))
        conn.commit()
        conn.close()
        
        return True, f"Inscrição realizada com sucesso! Seu código de confirmação: {codigo}\n\n📅 Evento: {titulo}\n🆔 Código: {codigo}\n📧 Enviamos os detalhes para {email}"
        
    except Exception as e:
        conn.close()
        print(f"Erro na inscrição: {e}")
        return False, "Erro ao realizar inscrição."

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
    
    col1, col2 = st.columns(2)
    
    for i, evento in enumerate(eventos):
        with col1 if i % 2 == 0 else col2:
            tipo_evento = evento[6]
            vagas = evento[7]
            inscritos = evento[8]
            
            disponibilidade = (inscritos / vagas * 100) if vagas > 0 else 0
            
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid {icon_color}; border: 1px solid {border_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div style='flex: 1;'>
                        <span style='background: {icon_color}; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px;'>{tipo_evento.upper()}</span>
                        <h3 style='color: {text_color}; margin: 10px 0 5px 0;'>{evento[1]}</h3>
                        <p style='color: {text_color}; margin: 5px 0; font-size: 14px;'>{evento[2][:100]}...</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
                        <p style='margin: 5px 0; color: {icon_color};'><i class='fas fa-star'></i> +{evento[12] if len(evento) > 12 else 150} pontos</p>
                    </div>
                    <div style='text-align: right; min-width: 120px;'>
                        <p style='color: {secondary_text};'><strong>{inscritos}/{vagas if vagas > 0 else '∞'}</strong> inscritos</p>
                        <div style='height: 6px; background: {border_color}; border-radius: 3px; margin: 10px 0;'>
                            <div style='height: 100%; width: {disponibilidade}%; background: {icon_color}; border-radius: 3px;'></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_perfil_completo(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    """Mostra perfil completo com estatísticas"""
    result = get_user_data(usuario_id)
    
    if len(result) == 9:
        user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites, motivo_ban = result
    else:
        user, progresso, conquistas, comprovantes, inscricoes, dicas_vistas, visitas, convites = result
        motivo_ban = None
    
    if motivo_ban:
        st.error(f"🚫 Usuário banido: {motivo_ban}")
        if st.button("Sair"):
            st.session_state.usuario_logado = None
            st.rerun()
        return
    
    if not user or not progresso:
        st.error("Erro ao carregar perfil")
        return
    
    nome, email, telefone, cidade, data_cadastro = user
    
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
        st.markdown(f"<span style='color: {text_color};'>**Telefone:** {telefone or 'Não informado'}</span>", unsafe_allow_html=True)
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
    
    if comprovantes:
        with st.expander("📸 Histórico de Comprovantes"):
            for comp in comprovantes[:10]:
                status = "✅ Aprovado" if comp[7] else "⏳ Pendente"
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid {border_color};'>
                    <strong style='color: {text_color};'>{comp[2]}</strong><br>
                    <small style='color: {text_color};'>{comp[6]} | {comp[5]} pontos | {status}</small>
                </div>
                """, unsafe_allow_html=True)

def mostrar_pagina_desafios(usuario_id, text_color, card_bg, icon_color, border_color, secondary_text):
    """Página de desafios com upload de arquivo"""
    st.markdown(f"<h2 style='color: {text_color};'>🎯 Desafios Ambientais</h2>", unsafe_allow_html=True)
    
    result = get_user_data(usuario_id)
    progresso = result[1] if result[1] else None
    
    pontos = progresso[1] if progresso and len(progresso) > 1 else 0
    
    st.markdown(f"""
    <div style='background: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {border_color}; text-align: center;'>
        <h3 style='color: {text_color};'>📊 Seus Pontos</h3>
        <h1 style='color: {icon_color}; font-size: 48px;'>{pontos}</h1>
        <p style='color: {text_color};'>Continue completando desafios!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color: {text_color};'>📋 Desafios Disponíveis</h3>", unsafe_allow_html=True)
    
    # Verificar desafios completados hoje
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("""
        SELECT tipo FROM comprovantes 
        WHERE usuario_id = ? AND data LIKE ? 
        ORDER BY data DESC
    """, (usuario_id, f"{datetime.now().strftime('%d/%m/%Y')}%"))
    completados_hoje = [row[0] for row in c.fetchall()]
    conn.close()
    
    for desafio in DESAFIOS_LISTA:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                bloqueado = desafio['tipo'] in completados_hoje
                st.markdown(f"""
                <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color}; opacity: {0.5 if bloqueado else 1};'>
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <span style='font-size: 40px;'>{desafio['icone']}</span>
                        <div>
                            <h4 style='color: {text_color}; margin: 0;'>{desafio['titulo']}</h4>
                            <p style='color: {text_color}; margin: 5px 0;'>{desafio['descricao']}</p>
                            <p style='color: {icon_color}; margin: 0;'>Recompensa: +{desafio['pontos']} pontos</p>
                            <p style='color: {secondary_text}; font-size: 12px; margin: 5px 0 0 0;'><i class='fas fa-info-circle'></i> {desafio['dica_validacao']}</p>
                            {f"<p style='color: #ff9800; font-size: 12px; margin-top: 5px;'>⏳ Limite diário atingido</p>" if bloqueado else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not bloqueado:
                    if st.button(f"📸 Comprovar", key=f"btn_{desafio['id']}_{usuario_id}"):
                        st.session_state['desafio_atual'] = desafio
                        st.session_state['mostrar_upload'] = True
                        st.rerun()
                else:
                    st.button(f"✅ Concluído", key=f"done_{desafio['id']}_{usuario_id}", disabled=True)
    
    # Modal de upload de foto
    if st.session_state.get('mostrar_upload', False):
        desafio = st.session_state['desafio_atual']
        
        st.markdown("---")
        st.markdown(f"<h3 style='color: {text_color};'>📸 Comprovar: {desafio['titulo']}</h3>", unsafe_allow_html=True)
        
        with st.container():
            st.info(f"**Dica para validação:** {desafio['dica_validacao']}")
            
            uploaded_file = st.file_uploader(
                "Escolha uma foto ou imagem do comprovante",
                type=['jpg', 'jpeg', 'png'],
                key=f"upload_comprovante_{desafio['id']}_{usuario_id}"
            )
            
            if uploaded_file is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(uploaded_file, caption="Prévia da imagem", use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background: {card_bg}; padding: 15px; border-radius: 10px; border: 1px solid {border_color};'>
                        <h4 style='color: {text_color};'>Resumo</h4>
                        <p style='color: {text_color};'><strong>Desafio:</strong> {desafio['titulo']}</p>
                        <p style='color: {text_color};'><strong>Pontos:</strong> +{desafio['pontos']}</p>
                        <p style='color: {text_color};'><strong>Arquivo:</strong> {uploaded_file.name}</p>
                        <p style='color: {text_color};'><strong>Tamanho:</strong> {len(uploaded_file.getvalue()) / 1024:.1f} KB</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("✅ Confirmar e enviar", key=f"confirmar_upload_{desafio['id']}_{usuario_id}", use_container_width=True):
                        with st.spinner("Validando imagem..."):
                            bytes_data = uploaded_file.getvalue()
                            sucesso, mensagem, pontos_ganhos = salvar_comprovante(
                                usuario_id,
                                desafio['tipo'],
                                f"Completou: {desafio['titulo']}",
                                bytes_data
                            )
                            
                            if sucesso:
                                st.balloons()
                                st.success(mensagem)
                                time.sleep(2)
                                st.session_state['mostrar_upload'] = False
                                st.session_state['desafio_atual'] = None
                                st.rerun()
                            else:
                                st.error(mensagem)
            
            if st.button("❌ Cancelar", key=f"cancelar_upload_{desafio['id']}_{usuario_id}"):
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
    """Mostra pontos de coleta com expanders por categoria"""
    conn = sqlite3.connect('ecopiracicaba.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pontos_coleta ORDER BY categoria, nome")
    pontos = c.fetchall()
    conn.close()
    
    st.markdown(f"<h2 style='color: {text_color};'>📍 Pontos de Coleta em Piracicaba</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {secondary_text}; margin-bottom: 30px;'>Encontre o ponto mais próximo para descartar cada tipo de resíduo</p>", unsafe_allow_html=True)
    
    # Agrupar por categoria
    categorias = {}
    for ponto in pontos:
        categoria = ponto[3]
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(ponto)
    
    # Dicionário de ícones por categoria
    icones_categoria = {
        'geral': '🗑️',
        'pilhas': '🔋',
        'eletronicos': '💻',
        'oleo': '🫒',
        'vidros': '🥃',
        'papel': '📄',
        'plasticos': '🧴',
        'organicos': '🌱',
        'medicamentos': '💊',
        'lampadas': '💡',
        'roupas': '👕',
        'moveis': '🪑',
        'metais': '⚙️'
    }
    
    # Mostrar estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h3 style='color: {icon_color}; font-size: 32px;'>{len(pontos)}</h3>
            <p style='color: {text_color};'>Total de Pontos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <h3 style='color: {icon_color}; font-size: 32px;'>{len(categorias)}</h3>
            <p style='color: {text_color};'>Categorias</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avaliacao_media = sum([p[6] for p in pontos]) / len(pontos) if pontos else 0
        estrelas = "★" * int(avaliacao_media) + "☆" * (5 - int(avaliacao_media))
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
            <div style='color: gold; font-size: 20px;'>{estrelas}</div>
            <p style='color: {text_color};'>Avaliação Média</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar pontos por categoria em expanders
    for categoria, pontos_cat in sorted(categorias.items()):
        icone = icones_categoria.get(categoria, '📍')
        with st.expander(f"{icone} {categoria.upper()} ({len(pontos_cat)} pontos)", expanded=False):
            # Subdividir em 2 colunas para melhor visualização
            cols = st.columns(2)
            for i, ponto in enumerate(pontos_cat):
                with cols[i % 2]:
                    estrelas = "★" * int(ponto[6]) + "☆" * (5 - int(ponto[6]))
                    st.markdown(f"""
                    <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid {border_color};'>
                        <h4 style='color: {text_color}; margin: 0 0 10px 0;'>{ponto[1]}</h4>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-map-pin' style='color: {icon_color};'></i> {ponto[2]}</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-clock' style='color: {icon_color};'></i> {ponto[4]}</p>
                        <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-phone' style='color: {icon_color};'></i> {ponto[5]}</p>
                        <p style='margin: 5px 0; color: {secondary_text}; font-size: 12px;'>{ponto[7]}</p>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
                            <div style='color: gold; font-size: 16px;'>{estrelas}</div>
                            <span style='background: {icon_color}; color: white; padding: 3px 8px; border-radius: 50px; font-size: 11px;'>{ponto[6]}/5.0</span>
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
    
    .stButton button:disabled {{
        background: #444 !important;
        opacity: 0.5;
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
    
    .stInfo {{
        background-color: #1a4a6e !important;
    }}
    
    .stSuccess {{
        background-color: #1a6e4a !important;
    }}
    
    .stWarning {{
        background-color: #6e4a1a !important;
    }}
    
    .stError {{
        background-color: #6e1a1a !important;
    }}
</style>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# ========== INTERFACE PRINCIPAL ==========

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state['mostrar_upload'] = False
    st.session_state['desafio_atual'] = None
    st.session_state['mostrar_inscricao'] = False
    st.session_state['evento_atual'] = None

with st.sidebar:
    st.markdown(f"<h2 style='color: {sidebar_text}; text-align: center;'>🌿 SustentaPira</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {sidebar_text}; text-align: center;'>Sustentabilidade em ação</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.usuario_logado is None:
        st.markdown(f"<h3 style='color: {sidebar_text};'>🔐 Login</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user, erro = fazer_login(email, senha)
                if user:
                    st.session_state.usuario_logado = {
                        'id': user[0],
                        'nome': user[1]
                    }
                    st.rerun()
                else:
                    st.error(erro)
        
        st.markdown("---")
        st.markdown(f"<h3 style='color: {sidebar_text};'>🆕 Cadastro</h3>", unsafe_allow_html=True)
        
        with st.form("cadastro_form"):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone (opcional)")
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
                    sucesso, user_id, mensagem = criar_usuario(nome, email, senha, telefone)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)
    else:
        result = get_user_data(st.session_state.usuario_logado['id'])
        
        if len(result) == 9:
            user, progresso, conquistas, _, _, _, _, convites, motivo_ban = result
        else:
            user, progresso, conquistas, _, _, _, _, convites = result
            motivo_ban = None
        
        if motivo_ban:
            st.error(f"🚫 {motivo_ban}")
            if st.button("Sair"):
                st.session_state.usuario_logado = None
                st.rerun()
        else:
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
            <p style='color: {secondary_text};'>Mais de 50 eventos durante o ano</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <i class='fas fa-map-marker-alt' style='font-size: 30px; color: {icon_color};'></i>
            <h4 style='color: {text_color};'>Pontos de Coleta</h4>
            <p style='color: {secondary_text};'>Mais de 100 pontos em 14 categorias</p>
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
        
        st.markdown(f"<h2 style='color: {text_color};'>📅 Eventos 2026 - Piracicaba</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {secondary_text}; margin-bottom: 30px;'>Participe dos eventos e ganhe pontos extras! Total de {len(eventos)} eventos durante o ano.</p>", unsafe_allow_html=True)
        
        # Estatísticas dos eventos
        total_eventos = len(eventos)
        eventos_com_vagas = sum(1 for e in eventos if e[7] == 0 or e[8] < e[7])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
                <h3 style='color: {icon_color}; font-size: 32px;'>{total_eventos}</h3>
                <p style='color: {text_color};'>Eventos em 2026</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
                <h3 style='color: {icon_color}; font-size: 32px;'>{eventos_com_vagas}</h3>
                <p style='color: {text_color};'>Com vagas disponíveis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_pontos = sum(e[12] for e in eventos if len(e) > 12)
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {border_color};'>
                <h3 style='color: {icon_color}; font-size: 32px;'>+{total_pontos}</h3>
                <p style='color: {text_color};'>Pontos totais</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Verificar inscrições do usuário
        conn = sqlite3.connect('ecopiracicaba.db')
        c = conn.cursor()
        c.execute("SELECT evento_id, participou FROM inscricoes WHERE usuario_id = ?", (st.session_state.usuario_logado['id'],))
        inscricoes_usuario = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        
        # Buscar dados do usuário para pré-preencher formulário
        user_data = get_user_data(st.session_state.usuario_logado['id'])[0]
        if user_data:
            nome_usuario, email_usuario, telefone_usuario, cidade_usuario, data_cadastro = user_data
        
        # Agrupar eventos por mês
        eventos_por_mes = {}
        for evento in eventos:
            mes = evento[3].split('/')[1]
            if mes not in eventos_por_mes:
                eventos_por_mes[mes] = []
            eventos_por_mes[mes].append(evento)
        
        # Mostrar eventos por mês em expanders
        meses = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
            '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
            '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }
        
        for mes_num, eventos_mes in sorted(eventos_por_mes.items()):
            nome_mes = meses.get(mes_num, f'Mês {mes_num}')
            with st.expander(f"📅 {nome_mes} 2026 ({len(eventos_mes)} eventos)", expanded=False):
                for evento in eventos_mes:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        pontos_evento = evento[12] if len(evento) > 12 else 150
                        st.markdown(f"""
                        <div style='background: {card_bg}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid {icon_color}; border: 1px solid {border_color};'>
                            <h4 style='color: {text_color}; margin: 0 0 5px 0;'>{evento[1]}</h4>
                            <p style='color: {text_color}; font-size: 14px; margin: 5px 0;'>{evento[2]}</p>
                            <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-calendar' style='color: {icon_color};'></i> {evento[3]} às {evento[4]}</p>
                            <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> {evento[5]}</p>
                            <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-building' style='color: {icon_color};'></i> {evento[9]}</p>
                            <p style='margin: 5px 0; color: {icon_color};'><i class='fas fa-star'></i> +{pontos_evento} pontos</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if evento[0] in inscricoes_usuario:
                            if inscricoes_usuario[evento[0]] == 1:
                                st.success("✅ Participou")
                            else:
                                st.info("📝 Inscrito")
                        else:
                            if evento[7] == 0 or evento[8] < evento[7]:
                                if st.button(f"📝 Inscrever", key=f"insc_{evento[0]}_{st.session_state.usuario_logado['id']}"):
                                    st.session_state['evento_atual'] = evento
                                    st.session_state['mostrar_inscricao'] = True
                                    st.rerun()
                            else:
                                st.error("❌ Esgotado")
    
    with tab5:
        mostrar_pontos_completos(text_color, card_bg, icon_color, border_color, secondary_text)

# Modal de inscrição em evento
if st.session_state.get('mostrar_inscricao', False) and st.session_state['evento_atual']:
    evento = st.session_state['evento_atual']
    
    with st.container():
        st.markdown("---")
        st.markdown(f"<h3 style='color: {text_color};'>📝 Ficha de Inscrição</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            pontos_evento = evento[12] if len(evento) > 12 else 150
            st.markdown(f"""
            <div style='background: {card_bg}; padding: 20px; border-radius: 15px; border: 1px solid {border_color}; margin-bottom: 20px;'>
                <h4 style='color: {text_color};'>{evento[1]}</h4>
                <p style='color: {text_color};'>{evento[2]}</p>
                <p style='margin: 10px 0; color: {text_color};'><i class='fas fa-calendar' style='color: {icon_color};'></i> <strong>Data:</strong> {evento[3]} às {evento[4]}</p>
                <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-map-marker-alt' style='color: {icon_color};'></i> <strong>Local:</strong> {evento[5]}</p>
                <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-building' style='color: {icon_color};'></i> <strong>Organizador:</strong> {evento[9]}</p>
                <p style='margin: 5px 0; color: {text_color};'><i class='fas fa-phone' style='color: {icon_color};'></i> <strong>Contato:</strong> {evento[10]}</p>
                <p style='margin: 5px 0; color: {icon_color};'><i class='fas fa-star'></i> <strong>Pontos ao participar:</strong> +{pontos_evento}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            with st.form("form_inscricao"):
                st.markdown(f"<h4 style='color: {text_color};'>Seus Dados</h4>", unsafe_allow_html=True)
                
                nome_inscricao = st.text_input("Nome completo *", value=st.session_state.usuario_logado['nome'] if st.session_state.usuario_logado else "")
                email_inscricao = st.text_input("E-mail *", value=email_usuario if 'email_usuario' in locals() else "")
                telefone_inscricao = st.text_input("Telefone *", value=telefone_usuario if 'telefone_usuario' in locals() else "")
                
                st.markdown(f"<small style='color: {secondary_text};'>* Campos obrigatórios</small>", unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    confirmar = st.form_submit_button("✅ Confirmar inscrição", use_container_width=True)
                with col_b:
                    cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if confirmar:
                    if not nome_inscricao or not email_inscricao or not telefone_inscricao:
                        st.error("Preencha todos os campos obrigatórios!")
                    elif not validar_email(email_inscricao):
                        st.error("E-mail inválido!")
                    else:
                        with st.spinner("Processando inscrição..."):
                            sucesso, mensagem = inscrever_evento(
                                st.session_state.usuario_logado['id'],
                                evento[0],
                                nome_inscricao,
                                email_inscricao,
                                telefone_inscricao
                            )
                            
                            if sucesso:
                                st.balloons()
                                st.success(mensagem)
                                time.sleep(3)
                                st.session_state['mostrar_inscricao'] = False
                                st.session_state['evento_atual'] = None
                                st.rerun()
                            else:
                                st.error(mensagem)
                
                if cancelar:
                    st.session_state['mostrar_inscricao'] = False
                    st.session_state['evento_atual'] = None
                    st.rerun()
