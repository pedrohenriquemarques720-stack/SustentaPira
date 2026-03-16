import streamlit as st
from pathlib import Path

# Configuração da página
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

# Se o HTML foi carregado com sucesso
if html_content:
    # CSS para remover elementos do Streamlit
    st.markdown("""
        <style>
            .main > div { padding: 0 !important; margin: 0 !important; }
            .stApp { margin-top: -70px !important; }
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)
    
    # Mostrar o HTML
    st.components.v1.html(html_content, height=1000, scrolling=True)

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
