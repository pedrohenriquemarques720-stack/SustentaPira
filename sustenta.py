import streamlit as st
from pathlib import Path
import os

# Configuração da página
st.set_page_config(
    page_title="SustentaPira",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CONFIGURAÇÃO PARA SERVIR ARQUIVOS ESTÁTICOS ==========
# Criar diretório static se não existir
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Copiar arquivos da pasta tabs para static se necessário
tabs_dir = Path(__file__).parent / "tabs"
if tabs_dir.exists():
    for file in tabs_dir.glob("*.html"):
        dest = static_dir / file.name
        if not dest.exists():
            import shutil
            shutil.copy(file, dest)

# Servir arquivos estáticos
st.markdown("""
    <script>
        // Forçar carregamento dos arquivos da pasta static
        window.staticPath = '/app/static/';
    </script>
""", unsafe_allow_html=True)

# ========== FUNÇÃO PARA LER O ARQUIVO HTML ==========
def carregar_html():
    caminho_html = Path(__file__).parent / "sustenta.html"
    
    if not caminho_html.exists():
        return None
    
    with open(caminho_html, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    
    # Substituir o caminho dos arquivos para apontar para a pasta static
    conteudo = conteudo.replace('src="tabs/', 'src="static/')
    conteudo = conteudo.replace("src='tabs/", "src='static/")
    
    return conteudo

# CSS para remover elementos do Streamlit
st.markdown("""
    <style>
        .main > div { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        header { display: none !important; }
        footer { display: none !important; }
        .stApp > header { display: none !important; }
        .stApp { margin: 0 !important; padding: 0 !important; background: #FFFFFF; }
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        #MainMenu { display: none !important; }
        iframe { width: 100% !important; height: 100vh !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# Carregar e exibir o HTML
html_content = carregar_html()

if html_content:
    st.components.v1.html(html_content, height=1000, scrolling=True)
else:
    st.error("❌ Arquivo sustenta.html não encontrado!")
