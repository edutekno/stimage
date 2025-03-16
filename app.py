import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

# Konfigurasi OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# Fungsi untuk mengkonversi gambar ke base64
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Fungsi untuk mendapatkan respons dari AI
def get_ai_response(message, image=None):
    messages = [
        {
            "role": "user",
            "content": []
        }
    ]
    
    # Tambahkan teks jika ada
    if message:
        messages[0]["content"].append({
            "type": "text",
            "text": message
        })
    
    # Tambahkan gambar jika ada
    if image:
        base64_image = image_to_base64(image)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
    
    # Jika tidak ada input
    if not message and not image:
        return "Please provide text or an image."

    # Panggil API
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AI Chat with Image",
            },
            model="google/gemma-3-27b-it:free",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Inisialisasi state chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inisialisasi state untuk gambar yang diupload
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Sidebar untuk upload dan preview gambar
with st.sidebar:
    st.title("Upload Image")
    uploaded_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.session_state.uploaded_image = Image.open(uploaded_file)
        #st.success("Image uploaded successfully!")
        st.image(st.session_state.uploaded_image, caption="Uploaded Image", use_column_width=True)

# UI Streamlit utama
st.title("AI Playground - Gemma 3")

# Area chat
chat_container = st.container()

# Tampilkan pesan di chat
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message and message["image"]:
                st.image(message["image"], width=300)

# Input pengguna dengan st.chat_input
user_input = st.chat_input("Type your message here...")

# Proses input ketika pengguna menekan Enter
if user_input:
    # Tampilkan pesan user
    user_message = {"role": "user", "content": user_input, "image": None}
    if st.session_state.uploaded_image:
        user_message["image"] = st.session_state.uploaded_image
    
    st.session_state.messages.append(user_message)
    
    # Dapatkan respons AI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            image_to_process = st.session_state.uploaded_image if st.session_state.uploaded_image else None
            response = get_ai_response(user_input, image_to_process)
            st.write(response)
    
    # Tambahkan respons ke history
    st.session_state.messages.append({"role": "assistant", "content": response, "image": None})
    
    # Reset gambar yang diupload setelah dikirim
    st.session_state.uploaded_image = None
    
    # Rerun untuk memperbarui tampilan
    st.rerun()

# Styling tambahan
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .stForm {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: white;
        padding: 10px;
        border-top: 1px solid #eee;
    }
    .stContainer {
        margin-bottom: 100px;
    }
    </style>
    """, unsafe_allow_html=True)
