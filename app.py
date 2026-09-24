import os
import base64
import streamlit as st
from openai import OpenAI

# 1. Configuración de página
st.set_page_config(
    page_title="Análisis de Imagen", 
    page_icon="🤖", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS personalizados utilizando tu paleta de colores
st.markdown(
    """
    <style>
    /* Tipografía y Encabezados - Primary Purple */
    h1, h2, h3 {
        color: #6650F2 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Barra lateral con degradado - Light Purple */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(235, 179, 242, 0.15) 0%, rgba(255,255,255,0) 100%);
        border-right: 1px solid rgba(235, 179, 242, 0.5);
    }
    
    /* Botones Principales - Primary to Dark Purple */
    .stButton > button {
        background-color: #6650F2 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #503FBF !important;
        box-shadow: 0 4px 12px rgba(80, 63, 191, 0.2) !important;
    }
    
    /* Zona de carga de archivos - Mint Green */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #79D9AC !important;
        background-color: rgba(121, 217, 172, 0.05) !important;
        border-radius: 12px !important;
        transition: background-color 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(121, 217, 172, 0.15) !important;
    }
    
    /* Estado activo de las cajas de texto */
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #6650F2 !important;
        box-shadow: 0 0 0 2px rgba(102, 80, 242, 0.3) !important;
    }

    /* Líneas divisorias - Light Purple */
    hr {
        border-top: 2px solid rgba(235, 179, 242, 0.4) !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Encabezado de la aplicación
st.title("Análisis de Imagen")
st.markdown("Carga una imagen y utiliza inteligencia artificial para analizar su contenido detalladamente.")

# Barra lateral para configuración
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    ke = st.text_input('Ingresa tu Clave de OpenAI', type="password", help="Tu clave API no se guarda.")
    
    if not ke:
        # Advertencia estilizada con Coral (#F27052)
        st.markdown(
            '<div style="padding:10px; border-radius:8px; background-color:rgba(242, 112, 82, 0.1); color:#F27052; font-weight:500;">'
            '⚠️ Por favor ingresa tu clave de API para continuar.</div>', 
            unsafe_allow_html=True
        )
    else:
        # Éxito estilizado con Mint (#79D9AC)
        st.markdown(
            '<div style="padding:10px; border-radius:8px; background-color:rgba(121, 217, 172, 0.1); color:#2E7D58; font-weight:500;">'
            '✅ Clave configurada correctamente.</div>', 
            unsafe_allow_html=True
        )

# Área de carga de archivos
uploaded_file = st.file_uploader("📂 Carga una imagen (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Controles de contexto adicional
st.markdown("---")
show_details = st.toggle("Preguntar algo específico sobre la imagen", value=False)
additional_details = ""

if show_details:
    additional_details = st.text_area(
        "Adiciona contexto o tu pregunta aquí:",
        placeholder="Ej: ¿Qué raza es el perro de la foto? o Describe los colores principales."
    )

# Botón de ejecución
analyze_button = st.button("Analizar Imagen")

# Lógica principal de ejecución
if analyze_button:
    if not ke:
        st.markdown('<div style="padding:15px; border-left: 5px solid #F27052; background-color:rgba(242, 112, 82, 0.1); border-radius:4px; color:#F27052;"><strong>Error:</strong> La clave de API de OpenAI es obligatoria.</div>', unsafe_allow_html=True)
    elif not uploaded_file:
        st.markdown('<div style="padding:15px; border-left: 5px solid #F27052; background-color:rgba(242, 112, 82, 0.1); border-radius:4px; color:#F27052;"><strong>Aviso:</strong> Por favor carga una imagen antes de ejecutar el análisis.</div>', unsafe_allow_html=True)
    else:
        try:
            with st.spinner("Procesando imagen..."):
                client = OpenAI(api_key=ke)
                base64_image = encode_image(uploaded_file)
                
                prompt_text = "Describe detalladamente lo que ves en esta imagen en español."
                
                if show_details and additional_details.strip():
                    prompt_text += f"\n\nContexto adicional o pregunta del usuario:\n{additional_details}"
                
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]
                
                st.markdown("---")
                st.markdown("### 📝 Resultado del Análisis:")
                
                # Contenedor visual estilizado con Mint Green (#79D9AC)
                container_start = '<div style="padding:25px; border: 1px solid #79D9AC; border-radius: 12px; background-color:rgba(121, 217, 172, 0.05); font-size: 16px; line-height: 1.6;">'
                container_end = '</div>'
                
                message_placeholder = st.empty()
                full_response = ""
                
                for completion in client.chat.completions.create(
                    model="gpt-4o", 
                    messages=messages,   
                    max_tokens=1200, 
                    stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        # Renderiza la respuesta dentro del contenedor HTML estilizado
                        message_placeholder.markdown(f"{container_start}{full_response} ▌{container_end}", unsafe_allow_html=True)
                
                # Renderizado final sin el cursor parpadeante
                message_placeholder.markdown(f"{container_start}{full_response}{container_end}", unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f'<div style="padding:15px; border-left: 5px solid #F27052; background-color:rgba(242, 112, 82, 0.1); border-radius:4px; color:#F27052;"><strong>Error de conexión:</strong> {e}</div>', unsafe_allow_html=True)
