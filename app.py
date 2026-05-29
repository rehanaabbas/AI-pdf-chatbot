import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
import os

# Load environment variables
load_dotenv()

# API key
api_key = os.getenv("GROQ_API_KEY")

# Groq client
client = Groq(api_key=api_key)

# Page config
st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="📚",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #e0f2fe, #f8fafc);
}

h1 {
    text-align: center;
    color: #2563eb;
    font-size: 50px;
}

.chat-user {
    background-color: #dbeafe;
    color: black;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.chat-ai {
    background-color: #ffffff;
    color: black;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border-left: 5px solid #2563eb;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("📚 AI PDF Assistant")

st.markdown(
    "### Upload multiple PDFs and chat with each file separately"
)

# ---------- SESSION STORAGE ----------
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = {}

# ---------- SIDEBAR ----------
with st.sidebar:

    st.header("📂 Uploaded PDFs")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            file_name = uploaded_file.name

            # Avoid reprocessing same PDF
            if file_name not in st.session_state.pdf_data:

                pdf_reader = PdfReader(uploaded_file)

                pdf_text = ""

                for page in pdf_reader.pages:

                    text = page.extract_text()

                    if text:
                        pdf_text += text

                st.session_state.pdf_data[file_name] = {
                    "text": pdf_text,
                    "messages": []
                }

    selected_pdf = st.selectbox(
        "Select PDF",
        options=list(st.session_state.pdf_data.keys())
    ) if st.session_state.pdf_data else None

# ---------- MAIN CHAT AREA ----------
if selected_pdf:

    st.subheader(f"📄 Current File: {selected_pdf}")

    user_question = st.text_input(
        "Ask a question from this PDF"
    )

    if st.button("🚀 Generate Answer"):

        pdf_text = st.session_state.pdf_data[selected_pdf]["text"]

        prompt = f"""
        Answer the question using the PDF content below.

        PDF Content:
        {pdf_text}

        Question:
        {user_question}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content

        # Save conversation
        st.session_state.pdf_data[selected_pdf]["messages"].append(
            {
                "question": user_question,
                "answer": answer
            }
        )

    # Display chat history
    st.markdown("## 💬 Chat History")

    for chat in st.session_state.pdf_data[selected_pdf]["messages"]:

        st.markdown(
            f"""
            <div class="chat-user">
            <b>🧑 You:</b><br>{chat["question"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="chat-ai">
            <b>🤖 AI:</b><br>{chat["answer"]}
            </div>
            """,
            unsafe_allow_html=True
        )

else:

    st.info("👈 Upload and select a PDF to start chatting.")
    