import streamlit as st
from pathlib import Path
import base64

# Configuração da página
st.set_page_config(
    page_title="Amor Cacau - Páscoa Gourmet",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS EXTREMO - REMOVE CABEÇALHO, RODAPÉ E QUALQUER ELEMENTO EXTRA
hide_streamlit_style = """
    <style>
        /* Remove o botão Manage App de cima */
        .stAppDeploymentButton {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }
        
        /* Remove o menu principal */
        #MainMenu {display: none !important;}
        
        /* Remove o cabeçalho */
        header {
            display: none !important;
        }
        
        /* REMOVE O RODAPÉ FIXO (O QUE ESTÁ CONGELADO EMBAIXO) */
        footer {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            position: fixed !important;
            bottom: -100px !important;
            z-index: -999 !important;
        }
        
        /* Remove qualquer elemento de rodapé */
        .st-emotion-cache-1s5fgy6 {
            display: none !important;
        }
        
        /* Remove a barra de ferramentas */
        .stToolbar {
            display: none !important;
        }
        
        .stDecoration {
            display: none !important;
        }
        
        /* Remove todos os elementos extras do Streamlit */
        .stAlert {
            display: none !important;
        }
        
        /* Remove classes específicas do rodapé */
        [data-testid="stFooter"] {
            display: none !important;
        }
        
        .st-emotion-cache-1dp5vir {
            display: none !important;
        }
        
        .st-emotion-cache-1wrcr25 {
            display: none !important;
        }
        
        /* Remove qualquer elemento que possa ser rodapé */
        .element-container:last-child {
            margin-bottom: -50px !important;
        }
        
        /* Ajusta o container principal para ocupar toda tela */
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #fcf5ec !important;
        }
        
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            padding-bottom: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* Remove fundo padrão */
        [data-testid="stAppViewContainer"] {
            background-color: #fcf5ec !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Ajuste de zoom */
        body {
            zoom: 0.75;
            -moz-transform: scale(0.75);
            -moz-transform-origin: 0 0;
            overflow-x: hidden;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #fcf5ec !important;
        }
        
        /* Remove espaço extra no final */
        .main {
            margin-bottom: -60px !important;
        }
        
        /* Remove qualquer iframe extra */
        iframe {
            margin-bottom: -60px !important;
        }
        
        /* Força remoção de qualquer elemento fixo inferior */
        [style*="position: fixed"] {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Função para converter imagem para base64
def get_image_base64(image_path):
    if Path(image_path).exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Carrega o HTML
def load_html():
    html_path = Path("pascoa.html")
    
    if not html_path.exists():
        st.error("❌ Arquivo pascoa.html não encontrado!")
        return None
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Imagens
    imagens = [
        'static/brigadeiro.png.jpeg',
        'static/avela.png.jpeg',
        'static/sensacao.png.jpeg', 
        'static/maracuja.png.jpeg',
        'static/prestigio.png.jpeg',
        'static/trufado.png.jpeg',
        'static/tablet.png.jpeg'
    ]
    
    for img in imagens:
        img_path = Path(img)
        img_base64 = get_image_base64(img_path)
        
        if img_base64:
            html_content = html_content.replace(
                f'src="{img}"', 
                f'src="data:image/jpeg;base64,{img_base64}"'
            )
    
    return html_content

html_content = load_html()

if html_content:
    # Renderiza o HTML com altura ajustada
    st.components.v1.html(
        html_content, 
        height=1600, 
        scrolling=True,
        width=None
    )
