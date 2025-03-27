import streamlit as st
import requests
import json
from PIL import Image
import io
import base64

# Set your OpenRouter API key here
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# Function to send image to OpenRouter API and get response
def get_image_description(image_url, prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "AI Image to Text App",  # Optional. Site title for rankings on openrouter.ai.
        },
        data=json.dumps({
            #google/gemini-2.5-pro-exp-03-25:free
            "model": "google/gemini-2.0-pro-exp-02-05:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
        })
    )
    # Debugging: Print API response and status code
    print("API Response:", response.json())
    print("Status Code:", response.status_code)
    return response.json()

# Streamlit app
st.title("AI-Image - Gemini Pro-2-5")

# Sidebar for image upload
with st.sidebar:
    st.header("Upload Gambar")
    uploaded_file = st.file_uploader("Pilih file gambar...", type=["jpg", "jpeg", "png"])

# Main window for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# If an image is uploaded, display it
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Gambar.', use_container_width=True)

    # Convert image to URL
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    image_url = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

    # Save image URL in session state
    st.session_state.image_url = image_url
else:
    # Clear image URL if no image is uploaded
    if "image_url" in st.session_state:
        del st.session_state.image_url

# Chat input for additional questions
if prompt := st.chat_input("Tanyakan terkait gambar..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if an image is uploaded
    if "image_url" in st.session_state:
        # Show loading spinner while waiting for API response
        with st.spinner("Berpikir..."):
            # Get image description from OpenRouter API
            response = get_image_description(st.session_state.image_url, prompt)
            if "choices" in response:
                description = response["choices"][0]["message"]["content"]
            else:
                description = "Failed to get description from the API."
                if "error" in response:
                    description += f" Error: {response['error']}"

        # Add assistant message to chat
        st.session_state.messages.append({"role": "assistant", "content": description})
        with st.chat_message("assistant"):
            st.markdown(description)
    else:
        # If no image is uploaded, just echo the prompt
        st.session_state.messages.append({"role": "assistant", "content": prompt})
        with st.chat_message("assistant"):
            st.markdown(prompt)
