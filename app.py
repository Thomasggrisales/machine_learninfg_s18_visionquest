import os
import streamlit as st
import base64
from openai import OpenAI

# 1. Configuración de la página (debe ser lo primero)
st.set_page_config(
    page_title="Análisis de Imagen con IA",
    page_icon="📸",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS personalizados para mejorar la interfaz
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        border-color: #FF6B6B;
    }
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Función para codificar la imagen
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# 3. Encabezado de la aplicación
st.markdown("<h1 class='main-header'>📸 Asistente de Análisis de Imagen 🤖</h1>", unsafe_allow_html=True)
st.markdown("Sube una imagen desde tu dispositivo o toma una foto con tu cámara para que la Inteligencia Artificial analice cada detalle.")

# 4. Configuración del Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Este Agente analiza el contenido de la imagen y responde tus preguntas en detalle.")
    # El type="password" oculta los caracteres de la API Key por seguridad
    api_key = st.text_input("🔑 Ingresa tu Clave de OpenAI:", type="password")
    
    st.divider()
    st.caption("Asegúrate de tener saldo en tu cuenta de OpenAI para usar el modelo GPT-4o.")

# 5. Sistema de pestañas para Subir Archivo vs Usar Cámara
tab1, tab2 = st.tabs(["📁 Subir desde el equipo", "📷 Tomar Foto"])

uploaded_file = None

with tab1:
    file_upload = st.file_uploader("Arrastra o selecciona una imagen", type=["jpg", "png", "jpeg"])
    if file_upload:
        uploaded_file = file_upload

with tab2:
    camera_upload = st.camera_input("Toma una foto con tu cámara")
    if camera_upload:
        uploaded_file = camera_upload

# 6. Lógica de procesamiento si hay una imagen cargada
if uploaded_file is not None:
    st.divider()
    
    # Mostrar la imagen seleccionada con un diseño limpio
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(uploaded_file, caption="Imagen lista para analizar", use_container_width=True)

    # Opciones de personalización del prompt
    show_details = st.toggle("📝 Añadir preguntas específicas o contexto (Opcional)", value=False)
    additional_details = ""
    
    if show_details:
        additional_details = st.text_area(
            "¿Qué quieres saber específicamente sobre la imagen?",
            placeholder="Ej: ¿Qué raza de perro es? o Extrae el texto que aparece en la imagen..."
        )

    # Botón de análisis
    analyze_button = st.button("🚀 Analizar Imagen")

    if analyze_button:
        if not api_key:
            st.warning("⚠️ Por favor, ingresa tu clave de OpenAI en el menú lateral para continuar.")
        else:
            with st.spinner("🧠 La IA está analizando la imagen. Por favor espera..."):
                try:
                    # Inicializar el cliente con la API key proporcionada
                    client = OpenAI(api_key=api_key)
                    base64_image = encode_image(uploaded_file)

                    # Preparar el prompt
                    if show_details and additional_details.strip():
                        prompt_text = f"Responde a lo siguiente basándote en la imagen, siempre en español:\n\n{additional_details}"
                    else:
                        prompt_text = "Describe detalladamente lo que ves en la imagen en español."

                    # Llamada a la API
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=400
                    )
                    
                    # Mostrar resultados
                    st.success("✅ ¡Análisis completado con éxito!")
                    st.markdown("### 📋 Resultados del Análisis:")
                    
                    # Contenedor para el resultado
                    with st.container(border=True):
                        st.write(response.choices[0].message.content)
                        
                except Exception as e:
                    st.error(f"❌ Ocurrió un error durante el análisis: {e}")
