import streamlit as st
from pathlib import Path

# Configuração da página - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="SustentaPira",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Função para ler o arquivo HTML
def carregar_html():
    caminho_html = Path(__file__).parent / "sustenta.html"
    
    if not caminho_html.exists():
        return None, caminho_html
    
    with open(caminho_html, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    
    return conteudo, caminho_html

# Carregar o HTML
html_content, caminho = carregar_html()

# CSS personalizado para remover TODOS os elementos do Streamlit
st.markdown("""
    <style>
        /* Remove todos os elementos padrão do Streamlit */
        .main > div {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        
        /* Remove o cabeçalho e menu */
        header {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        
        /* Remove o footer */
        footer {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Remove o menu hamburger */
        .stApp > header {
            display: none !important;
        }
        
        /* Remove qualquer padding/margin do body */
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
            background: #FFFFFF;
        }
        
        /* Container principal ocupa toda a tela */
        .stApp > div:first-child {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: auto !important; /* ← MUDADO DE 'hidden' PARA 'auto' */
        }
        
        /* Remove o padding do Streamlit */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        
        /* Esconde qualquer elemento indesejado */
        #MainMenu {
            display: none !important;
        }
        
        /* Garante que o iframe ocupe toda a tela mas com scroll */
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            z-index: 9999 !important;
        }
        
        /* Remove scroll do Streamlit MAS PERMITE SCROLL DO CONTEÚDO */
        .stApp {
            overflow: hidden !important; /* Mantém o Streamlit sem scroll */
        }
        
        /* Remove qualquer background extra */
        .stApp, .main, .block-container {
            background: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# Se o HTML foi carregado com sucesso
if html_content:
    # Exibir o HTML em um iframe que ocupa a tela inteira
    st.components.v1.html(
        html_content,
        height=1000,
        scrolling=True  ← MUDADO PARA True
    )
else:
    # Mensagem de erro simplificada
    st.error(f"❌ Arquivo sustenta.html não encontrado em: {caminho}")
    st.info("""
    ### Como resolver:
    1. Certifique-se que o arquivo **sustenta.html** está na mesma pasta que este arquivo Python
    2. O arquivo deve conter todo o código do seu app SustentaPira
    3. Após colocar o arquivo, reinicie o Streamlit
    
    **Pasta atual:** `{}`
    """.format(caminho.parent))
