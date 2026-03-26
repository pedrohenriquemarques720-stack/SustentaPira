import streamlit as st
import base64
from pathlib import Path

# Configuração
st.set_page_config(
    page_title="Amor Cacau",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS extremo para remover tudo
st.markdown("""
    <style>
        /* Remove todos os elementos extras */
        header, footer, .stAppDeploymentButton, .stToolbar,
        #MainMenu, .st-emotion-cache-1dp5vir, .st-emotion-cache-1wrcr25,
        [data-testid="stToolbar"], [data-testid="stDecoration"],
        .st-emotion-cache-1v0mbdj, .st-emotion-cache-1r6slb0 {
            display: none !important;
        }
        
        /* Ajusta o container */
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
            background: #fcf5ec !important;
        }
        
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        
        /* Zoom fixo */
        body {
            zoom: 0.75;
            -moz-transform: scale(0.75);
            -moz-transform-origin: 0 0;
            margin: 0;
            padding: 0;
            background: #fcf5ec;
        }
    </style>
""", unsafe_allow_html=True)

# Carrega o HTML
html_path = Path("pascoa.html")
if html_path.exists():
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Converte imagens para base64
    imagens = ['static/brigadeiro.png.jpeg', 'static/avela.png.jpeg', 
               'static/sensacao.png.jpeg', 'static/maracuja.png.jpeg',
               'static/prestigio.png.jpeg', 'static/trufado.png.jpeg',
               'static/tablet.png.jpeg']
    
    for img in imagens:
        img_path = Path(img)
        if img_path.exists():
            with open(img_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                html_content = html_content.replace(f'src="{img}"', f'src="data:image/jpeg;base64,{img_data}"')
    
    st.components.v1.html(html_content, height=1500, scrolling=True)
else:
    st.error("Arquivo pascoa.html não encontrado!")
