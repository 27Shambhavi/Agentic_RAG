# 🤖 Agentic RAG Space — Multimodal AI Knowledge Assistant

> An **Agentic Retrieval-Augmented Generation (RAG) system** that intelligently routes user queries across document RAG, Web RAG, general AI, OCR, voice, weather, and conversational capabilities.
> ## 📖 Project Story

This project started as a simple PDF-based RAG assistant and evolved into
an Agentic RAG system capable of intelligently deciding where an answer
should come from.

The system can search across the complete knowledge base instead of being
restricted to the currently selected document. If relevant information is
found in an uploaded document, the answer is generated from that document.
If the knowledge base does not contain the answer, the system can fall back
to web search.

It also supports Web RAG: when a user provides a URL, the webpage is scraped,
chunked, embedded, and stored in the vector database. Follow-up questions
about that webpage can then retrieve the relevant stored chunks instead of
re-scraping or performing unrelated web searches.

The final architecture uses an Agentic routing layer to switch between
Document RAG, Web RAG, Web Search, General AI, OCR, and Weather based on
the user's query and available context.

The main goal was to build a RAG system that is not locked to one document
or one retrieval path, but can dynamically choose the most relevant
knowledge source while maintaining conversational context.

---

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Workflow-purple)](https://langchain-ai.github.io/langgraph/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-000000)](https://www.pinecone.io/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-blue)](https://ai.google.dev/)

> A modular, multimodal AI assistant that intelligently decides whether a question should be answered from a knowledge base, a user-provided webpage, live web search, OCR, weather tools, or general AI.

---

# 🌟 Overview

**Agentic RAG Space** is a modular AI assistant designed to explore how modern AI applications work beyond simply sending every question to an LLM.

The system uses **LangGraph-based agentic orchestration** to analyze the user's request and select the appropriate execution path.

The assistant supports:

- 📄 Multi-document PDF RAG
- 🌐 URL-based Web RAG
- 🔎 Live Web Search
- 🖼️ OCR-based image questions
- 🎙️ Speech-to-Text
- 🔊 Text-to-Speech
- 💬 Conversation history
- 🤖 General AI conversations
- 🌤️ Weather queries
- 📚 Source attribution
- 🧠 Semantic vector retrieval
- ⚡ FastAPI backend
- 🎨 Streamlit frontend

The core design principle is:

```text
                         USER QUERY
                              │
                              ▼
                        🧠 SUPERVISOR
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        KNOWLEDGE RAG      WEB RAG         WEB SEARCH
             │                │                │
             ▼                ▼                ▼
         Pinecone         URL Data        Internet
             │                │
             └────────┬───────┘
                      ▼
                   Gemini
                      │
                      ▼
                Final Response
⭐ If you found this project interesting

Feel free to explore the repository, raise issues, suggest improvements, or build upon the architecture.

Built to understand what happens behind the scenes of modern AI applications. 🚀
