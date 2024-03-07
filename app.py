import streamlit as st
import cloudinary
import cloudinary.uploader
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import base64
from PIL import Image
import numpy as np
from gtts import gTTS
import tempfile
import os
import google.generativeai as genai

api_key = 'AIzaSyABFNeXQMQNy-MFlPf9818zmFn5wnuFZHc'
if api_key is None:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it before running the script.")

# Configuring the GenerativeAI API with the obtained API key
genai.configure(api_key=api_key)

# Creating a GenerativeModel instance
model = genai.GenerativeModel('gemini-pro-vision')

cloudinary.config(
    cloud_name='dxe1nduh4',
    api_key='573436633192792',
    api_secret='5cA5vSrDNN_-q6xtqDijz5pYsrM'
)

GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwn-KjyS7S_bFAdbujXOmwebd8vdA1vXO539Ijr_RiC22gfVMDPkMYLcByjWrN1xXg/exec'
GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1Fa-B9CWSDsctbWFjcidB5GqY_3uk8ME5dxoaPBU0lbA/edit#gid=0'

@st.cache_data
def upload_image_to_cloudinary(image):
    try:
        response = cloudinary.uploader.upload(image)
        return response.get('secure_url', None)
    except Exception as e:
        st.error(f"Error al cargar la imagen en Cloudinary: {str(e)}")
        return None

@st.cache_data
def get_value_from_google_sheet(link):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(GOOGLE_SHEET_URL).get_worksheet(0)
    time.sleep(3)
    # Buscar el link en la columna "f" y obtener el valor de la columna "g" correspondiente
    cell = sheet.find(link)
    value = sheet.cell(cell.row, 7).value
    return value


def generate_content(image, prompt=None):
    # Convert Streamlit Image to PIL Image
    if isinstance(image, np.ndarray):
        image_pil = Image.fromarray(image)
    else:
        image_pil = Image.open(image)

    if prompt:
        # Generating content using the model with prompt
        response = model.generate_content([prompt, image_pil])
        response.resolve()

        # Extracting the generated text
        generated_text = response.text.strip()
    else:
        # If no prompt is provided, generate content without prompt
        response = model.generate_content([image_pil])
        response.resolve()

        # Extracting the generated text
        generated_text = response.text.strip()

    return generated_text
def text_to_speech(text):
    tts = gTTS(text=text, lang="es", tld='us')
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    tts.save(temp_file.name)
    return temp_file.name
st.markdown(
    """
    <style>
        .container {
        display: flex;
    }
    .logo-img {
        max-width: 200px; /* Adjust the width to your desired value */
        max-height: 100px; /* Adjust the height to your desired value */
    }
    .logo-text {
        font-weight: 700 !important;
        font-size: 30px !important;
        color: gray !important;
        padding-top: 10px !important;
    }
    
        div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
        /* Estilos generales */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f1f1f1;
            margin: 0;
            padding: 0;
        }
        button.step-up {display: none;}
        button.step-down {display: none;}
        div[data-baseweb] {border-radius: 4px;}
        .container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Estilos del formulario */
        form {
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input[type="text"],
        .form-group input[type="number"],
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        
        .form-group textarea {
            height: 100px;
            resize: vertical;
        }
        
        .form-submit-button {
            display: block;
            width: 100%;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            background-color: #007bff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .form-submit-button:hover {
            background-color: #0056b3;
        }
        
        .success-message {
            margin-top: 20px;
            padding: 10px;
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 4px;
        }
        
        .error-message {
            margin-top: 20px;
            padding: 10px;
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
        }
        .container {
        display: flex;
    
    }
    </style>
    """,
    unsafe_allow_html=True,
)


expander = st.expander("Instrucciones:")
expander.write(""" Debe subir una imagen, al hacerlo se visualizara la misma en el panel izquierdo,
  el texto extraido de la misma se reflejara en pantalla , editar el texto de la misma para obtener un resultado
  satisfactorio, en la parte infierior  del audio,  debe escribir las instrucciones de lo que desea realizar, por ejemplo
  resumir el siguiente texto, resolver las siguientes operaciones, contestar el siguiente cuestionario, etc.
  Presionar "Enter" para visualizar el resultado """)


@st.cache_data
def sheets(url):

  data = {
                    'func': 'Create',
                    'usuario': 'NombreUsuario',  # Reemplaza esto por el nombre del usuario
                    'comercio': 'NombreComercio',  # Reemplaza esto por el nombre del comercio
                    'provincia': 'NombreProvincia',  # Reemplaza esto por el nombre de la provincia
                    'fecha': 'FechaActual',  # Reemplaza esto por la fecha actual (por ejemplo, "2023-07-24")
                    'link': url,
                    'observacion': 'Observacion'  # Reemplaza esto con una observación opcional
              }

  response = requests.post(GOOGLE_SCRIPT_URL, data=data)
               
  
  return response 
    
if "textoext" not in st.session_state:
    st.session_state.textoext = ""

uploaded_image = st.file_uploader("Selecciona una imagen", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # img = Image.open(uploaded_image)
    # resized_img = img.resize((400, 400))

    # st.image(resized_img, caption="Imagen Subida", use_column_width=True)
    st.sidebar.image(uploaded_image, caption="Imagen subida", use_column_width=True)
    with st.spinner("Procesando......"):
        url = upload_image_to_cloudinary(uploaded_image)
        if url:
            sheets(url)
      
               
        value_from_sheet = get_value_from_google_sheet(url)
        st.session_state.textoext = value_from_sheet
                


if "boton_ask" not in st.session_state:
    st.session_state.boton_ask = False

text_area_textoext = st.text_area("Texto Extraido", st.session_state.textoext, height=400)

# Check if the button is clicked
if text_area_textoext:
    with st.spinner("Procesando....."):
        audio_file = text_to_speech(text_area_textoext)
        st.audio(audio_file, format='audio/mp3')
            # elapsed_time = time.time() - start_time
        os.remove(audio_file)
        prompt = st.text_input("Ingresar Consulta ")
        if prompt:
            generated_text = generate_content(uploaded_image, prompt)
            st.text("Texto Generado:")
            st.write(generated_text)