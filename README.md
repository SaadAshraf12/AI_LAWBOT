

## 🧠 Voice-Enabled RAG System for Pakistani Law 

This project is a **Retrieval-Augmented Generation (RAG) system** that allows users to query **Pakistani laws** (specifically the Pakistan Penal Code, 1860) using their **voice**, and receive voice-based responses.

### 🔍 Key Features

* **Deepgram Speech-to-Text (STT)** for converting user voice input into text.
* **LangChain-powered RAG pipeline** using OpenAI’s GPT for intelligent legal question answering.
* **Deepgram Text-to-Speech (TTS)** for converting answers back into voice.
* **Legal dataset** scraped from [pakistani.org](https://www.pakistani.org/pakistan/legislation/1860/actXLVof1860.html).
* **Natural conversation experience** for querying complex legal information in Urdu or English.

### 🛠 Tech Stack

* Python, LangChain
* GPT API (OpenAI)
* Deepgram API (STT + TTS)
* FAISS vector store
* Web scraping (BeautifulSoup)
* Optional: Streamlit or CLI for user interaction

### 🗣 Example Queries

* "What is the punishment for theft under Pakistani law?"
* "Explain Section 302 of the Pakistan Penal Code."

### 📌 Use Case

Ideal for **law students**, **lawyers**, **civic education platforms**, or **legal aid tools** seeking quick and accurate information about Pakistani criminal law using natural voice-based interactions.

