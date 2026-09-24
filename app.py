import os
import base64
import streamlit as st
from openai import OpenAI

# 1. Configuración de página (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Análisis de Imagen", 
    page_icon="🤖", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS personalizados para mantener la coherencia visual
st.markdown(
    """
    <style>
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
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #79D9AC !important;
        background-color: rgba(121, 217, 172, 0.05) !important;
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Encabezado de la aplicación
st.title("Análisis de Imagen 🤖🏞️")
st.markdown("Carga una imagen y utiliza inteligencia artificial para analizar su contenido detalladamente.")

# Barra lateral para configuración
with st.sidebar:
    st.subheader("⚙️ Configuración")
    ke = st.text_input('Ingresa tu Clave de OpenAI', type="password", help="Tu clave API no se guarda.")
    if not ke:
        st.warning("⚠️ Por favor ingresa tu clave de API para continuar.")

# Área de carga de archivos
uploaded_file = st.file_uploader("📂 Carga una imagen (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Controles de contexto adicional
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
        st.error("⚠️ La clave de API de OpenAI es obligatoria para realizar el análisis.")
    elif not uploaded_file:
        st.warning("⚠️ Por favor carga una imagen antes de ejecutar el análisis.")
    else:
        try:
            # Inicializar el cliente SOLO cuando la clave está disponible y el botón es presionado
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
            
            # Contenedor para el efecto de escritura en vivo (streaming)
            message_placeholder = st.empty()
            full_response = ""
            
            # Petición a la API con streaming
            for completion in client.chat.completions.create(
                model="gpt-4o", 
                messages=messages,   
                max_tokens=1200, 
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    # Agrega un cursor parpadeante simulado durante la generación
                    message_placeholder.markdown(full_response + "▌")
            
            # Actualización final sin el cursor
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Ocurrió un error durante la comunicación con OpenAI: {e}")
