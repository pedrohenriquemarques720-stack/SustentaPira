import streamlit as st
import os
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
    # Caminho do arquivo HTML (deve estar na mesma pasta)
    caminho_html = Path(__file__).parent / "sustenta.html"
    
    # Verificar se o arquivo existe
    if not caminho_html.exists():
        st.error(f"❌ Arquivo sustenta.html não encontrado em: {caminho_html}")
        st.info("Certifique-se que o arquivo sustenta.html está na mesma pasta que este script Python.")
        return None
    
    # Ler o conteúdo do arquivo
    with open(caminho_html, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    
    return conteudo

# Carregar o HTML
html_content = carregar_html()

# Se o HTML foi carregado com sucesso, exibe no Streamlit
if html_content:
    # Injetar CSS personalizado para o Streamlit
    st.markdown(
        """
        <style>
            /* Remover padding e margin padrão do Streamlit */
            .main > div {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }
            
            /* Remover espaço em branco do topo */
            .stApp {
                margin-top: -70px !important;
            }
            
            /* Esconder elementos padrão do Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Garantir que o iframe ocupe toda a tela */
            iframe {
                width: 100vw !important;
                height: 100vh !important;
                border: none !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                z-index: 999999 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Exibir o HTML em um iframe para ocupar a tela inteira
    st.components.v1.html(
        html_content,
        height=1000,
        scrolling=True
    )
else:
    # Se não encontrou o arquivo, mostra instruções
    st.title("🌿 SustentaPira")
    st.markdown("""
    ### ⚠️ Arquivo HTML não encontrado
    
    **Instruções:**
    1. Certifique-se que o arquivo `sustenta.html` está na mesma pasta que este arquivo Python
    2. O arquivo deve conter todo o código do seu app SustentaPira
    3. Após colocar o arquivo, reinicie o Streamlit
    
    **Caminho esperado:** {}
    
    ---
    
    ### 📝 Criando o arquivo
    Se você ainda não tem o arquivo, copie o código HTML completo e salve como `sustenta.html` na pasta:
