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
            "model": "google/gemma-3-27b-it:free",
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
st.title("AIChat Image - Gemma 3")

# Sidebar for image upload
with st.sidebar:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # Preview image in the sidebar if uploaded
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image (Sidebar)', use_container_width=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# If an image is uploaded, display it at the top of the chatbot
if uploaded_file is not None:
    # Display the uploaded image at the top of the chatbot
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image (Chatbot)', use_container_width=True)

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
if prompt := st.chat_input("Ask about the image..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if an image is uploaded
    if "image_url" in st.session_state:
        # Show loading spinner while waiting for API response
        with st.spinner("Waiting..."):
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
        st.session_state.messages.append({"role": "assistant", "content": "No image uploaded. Please upload an image first."})
        with st.chat_message("assistant"):
            st.markdown("No image uploaded. Please upload an image first.")
