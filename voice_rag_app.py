
import os
import time
import tempfile
import pickle
import streamlit as st
from dotenv import load_dotenv
import requests
import pygame
import sounddevice as sd
import scipy.io.wavfile

from deepgram import DeepgramClient, PrerecordedOptions
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# === ENV CONFIG ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

VECTOR_DIR = "vectorstore"

# === AUDIO SETUP ===
DURATION = 5
SAMPLE_RATE = 16000

def record_audio(duration=DURATION):
    st.info("🎙️ Recording... Speak now.")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    scipy.io.wavfile.write(wav_path, SAMPLE_RATE, audio)
    return wav_path

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        response = deepgram.listen.rest.v("1").transcribe_file(
            source={"buffer": audio_file, "mimetype": "audio/wav"},
            options=PrerecordedOptions(model="nova-3", smart_format=True, language="en")
        )
    transcript = response.results.channels[0].alternatives[0].transcript.strip()
    return transcript

def speak_text(text):
    try:
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "application/json"}
        json_data = {"text": text}
        response = requests.post(url, headers=headers, json=json_data, timeout=30)

        if response.status_code == 200:
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            with open(audio_path, "wb") as f:
                f.write(response.content)

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            time.sleep(0.3)
            try:
                os.unlink(audio_path)
            except PermissionError:
                pass
        else:
            st.error(f"TTS failed: {response.status_code} {response.text}")
    except Exception as e:
        if "[WinError 32]" not in str(e):
            st.error(f"TTS error: {e}")
        st.info("🔊 Audio playback complete.")

# === CUSTOM PROMPT TEMPLATE FOR LEGAL DOMAIN ===
LEGAL_PROMPT_TEMPLATE = """
You are a legal assistant specializing in the Pakistan Penal Code of 1860.
Use only the content provided in the retrieved context to answer questions.

If the answer is not available in the context, say "I don’t know".

Always:
- Be concise.
- Explain legal concepts in plain English.
- Mention relevant section numbers if applicable.

Context:
{context}

Chat History:
{chat_history}

Question:
{question}

Answer:
"""

from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

prompt = PromptTemplate(
    input_variables=["context", "question", "chat_history"],
    template=LEGAL_PROMPT_TEMPLATE
)

# === RAG CHAIN ===
def get_rag_chain(db):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
    retriever = db.as_retriever(search_kwargs={"k": 5})
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        output_key="answer" 
    )

# === STREAMLIT UI ===
st.set_page_config(page_title="🎙️ Voice RAG Legal Chatbot", layout="centered")
st.title("⚖️ Voice RAG Chatbot (Pakistan Penal Code)")

voice_mode = st.checkbox("🎤 Use Microphone", value=True)
reset_chat = st.button("🔄 Reset Chat")

if reset_chat:
    for key in ["rag_chain", "db"]:
        st.session_state.pop(key, None)

if "rag_chain" not in st.session_state:
    with st.spinner("Loading legal knowledge base..."):
        db = FAISS.load_local(
            VECTOR_DIR,
            OpenAIEmbeddings(),
            index_name="index",  # must match saved name
            allow_dangerous_deserialization=True
        )
        rag_chain = get_rag_chain(db)
        st.session_state.db = db
        st.session_state.rag_chain = rag_chain

rag_chain = st.session_state.get("rag_chain", None)

# === ASK A QUESTION ===
query = None
if rag_chain:
    if voice_mode:
        if st.button("🎙️ Record"):
            audio_path = record_audio()
            query = transcribe_audio(audio_path)
            st.write(f"🗣️ You asked: `{query}`")
    else:
        query = st.text_input("Ask a legal question:")

    if query:
        with st.spinner("Thinking like a lawyer..."):
            result = rag_chain({"question": query})
            answer = result['answer']
            sources = result.get("source_documents", [])

            st.markdown("### 🧠 Answer")
            st.write(answer)
            speak_text(answer)

            if sources:
                st.markdown("### 📖 Source Chunks")
                for doc in sources:
                    source_name = os.path.basename(doc.metadata.get("source", "")) or "PDF"
                    st.code(f"{doc.page_content}\n\n(Source: {source_name})")


