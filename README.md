# 🤖 Agentic RAG Space

### Agentic AI Assistant with Multi-Document RAG, Web RAG, Live Web Search & Multimodal Interaction

<p align="center">

  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit" />
  <img src="https://img.shields.io/badge/LangGraph-Agentic%20AI-purple" />
  <img src="https://img.shields.io/badge/Pinecone-Vector%20DB-black" />
  <img src="https://img.shields.io/badge/Google-Gemini-blue" />

</p>

<p align="center">
  <b>A modular, multimodal AI assistant that intelligently decides whether a question should be answered from a knowledge base, a user-provided webpage, live web search, OCR, weather tools, or general AI.</b>
</p>

---

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


# 🌟 Overview

**Agentic RAG Space** is a modular AI assistant designed to explore how modern AI applications work beyond simply sending every question to an LLM.

The system uses **LangGraph-based agentic orchestration** to understand the user's request and route it to the most appropriate capability.

It supports:

- 📚 Multi-document PDF RAG
- 🌐 URL-based Web RAG
- 🔎 Live Web Search
- 🖼️ OCR / image questions
- 🎙️ Speech-to-Text
- 🔊 Text-to-Speech
- 💬 Conversation history
- 🤖 General AI conversations
- 🌤️ Weather queries
- 📑 Source attribution
- 🧠 Semantic vector retrieval
- ⚡ FastAPI backend
- 🎨 Streamlit frontend

The central idea is simple:

> **Decide first → retrieve/use the right tool → generate the answer.**

---

# ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Agentic Routing** | LangGraph supervisor routes each request to the appropriate capability |
| 📚 **Multi-Document RAG** | Searches across the complete indexed knowledge base |
| 📄 **PDF RAG** | Upload and ask questions about documents |
| 🌐 **Web RAG** | Provide a URL and ask questions about that webpage |
| 💾 **Persistent Web Knowledge** | Web content is chunked, embedded and indexed in Pinecone |
| 🔎 **Live Web Search** | Searches the internet for current information or when knowledge-base retrieval is insufficient |
| 🔗 **Web Context Memory** | Follow-up questions can continue using the previously provided webpage |
| 🧮 **Semantic Search** | Embedding-based vector similarity retrieval |
| 🤖 **Gemini LLM** | Generates grounded responses from retrieved context |
| 🖼️ **OCR** | Extract and query text from images |
| 🎙️ **Speech-to-Text** | Faster-Whisper voice transcription |
| 🔊 **Text-to-Speech** | pyttsx3 voice responses |
| 💬 **Conversation History** | Supports contextual follow-up questions |
| 📚 **Source Tracking** | Displays retrieved document and web sources |
| ⚡ **FastAPI** | REST API backend |
| 🎨 **Streamlit** | Interactive frontend |
| 🛡️ **Error Handling** | Graceful handling of retrieval, LLM, web and voice failures |

---

# 🏗️ System Architecture

```text
                              ┌─────────────────────────┐
                              │        USER             │
                              │                         │
                              │  Text / Voice / Image   │
                              │  PDF / URL / Question   │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │      STREAMLIT UI        │
                              │       FRONTEND           │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │       FASTAPI            │
                              │        BACKEND           │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │       LANGGRAPH          │
                              │     AGENTIC GRAPH        │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │       SUPERVISOR         │
                              │   INTENT / ROUTER        │
                              └────────────┬────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
      ┌────────────────┐          ┌────────────────┐          ┌────────────────┐
      │  KNOWLEDGE RAG │          │    WEB RAG     │          │   WEB SEARCH   │
      └───────┬────────┘          └───────┬────────┘          └───────┬────────┘
              │                           │                           │
              ▼                           ▼                           ▼
      ┌────────────────┐          ┌────────────────┐          ┌────────────────┐
      │   Pinecone     │          │ URL Extraction │          │ Search Engine  │
      │ Vector Search  │          │ + Web Indexing │          │    Results     │
      └───────┬────────┘          └───────┬────────┘          └───────┬────────┘
              │                           │                           │
              │                           ▼                           │
              │                    ┌────────────────┐                 │
              │                    │    Pinecone    │                 │
              │                    │ Web Vector DB  │                 │
              │                    └───────┬────────┘                 │
              │                           │                           │
              └───────────────────────────┼───────────────────────────┘
                                          │
                                          ▼
                                ┌────────────────────┐
                                │   RETRIEVED        │
                                │     CONTEXT        │
                                └─────────┬──────────┘
                                          │
                                          ▼
                                ┌────────────────────┐
                                │   GOOGLE GEMINI    │
                                │        LLM         │
                                └─────────┬──────────┘
                                          │
                                          ▼
                                ┌────────────────────┐
                                │  ANSWER + SOURCES  │
                                └─────────┬──────────┘
                                          │
                         ┌────────────────┴────────────────┐
                         │                                 │
                         ▼                                 ▼
                  ┌──────────────┐                  ┌──────────────┐
                  │  Streamlit   │                  │   pyttsx3    │
                  │     Text     │                  │    Audio     │
                  └──────────────┘                  └──────────────┘

🧠 Agentic Routing Architecture

The core principle of the application is:

                    USER QUERY
                        │
                        ▼
                  ┌───────────┐
                  │ SUPERVISOR│
                  └─────┬─────┘
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Knowledge RAG     Web RAG        Web Search
        │               │                │
        │               │                │
        ▼               ▼                ▼
     Pinecone        URL Data       Internet
        │               │                │
        └───────────────┼────────────────┘
                        │
                        ▼
                     Gemini
                        │
                        ▼
                 FINAL RESPONSE
Additional specialized routes include:

Supervisor
    │
    ├── 📚 RAG
    ├── 🌐 Web RAG
    ├── 🔎 Web Search
    ├── 🖼️ OCR
    ├── 🌤️ Weather
    ├── 👋 Greeting
    └── 🤖 General AI

The supervisor does not answer the user.

Its responsibility is to determine:

Which capability should handle this request?

🔀 Query Routing

The system distinguishes between different types of requests.

User Request	Route
Hi, how are you?	👋 Greeting
Explain machine learning	🤖 General AI
What is the leave policy in the documents?	📚 Knowledge RAG
https://example.com summarize this	🌐 Web RAG
What does this image say?	🖼️ OCR
What is the weather in Delhi?	🌤️ Weather
What is the latest AI news?	🔎 Web Search
Voice question about a PDF	🎙️ → 📚 RAG
Voice question about a webpage	🎙️ → 🌐 Web RAG
📚 Multi-Document RAG

The knowledge base can contain multiple documents.

Example:

data/documents/


├── Ayushman-Bharat.pdf
├── Dummy-Bank-Statement.pdf
├── employee_handbook.pdf
└── leave_policy.pdf

All documents can be indexed into Pinecone.

The important design decision is:

Selecting a PDF in the UI does not permanently restrict the knowledge base to that PDF.

The selected document acts as a UI/context preference, while the knowledge base can still search across all indexed documents.

🔎 Multi-Document Retrieval
                         USER QUESTION
                               │
                               ▼
                       Query Embedding
                               │
                               ▼
                     ┌─────────────────┐
                     │    PINECONE     │
                     │ KNOWLEDGE BASE  │
                     └────────┬────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       Document A        Document B       Document C
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                       Relevant Chunks
                              │
                              ▼
                       Relevance Check
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  FOUND               NOT FOUND
                    │                   │
                    ▼                   ▼
                  Gemini            Web Search
                    │
                    ▼
             Grounded Answer
📄 Document RAG Pipeline

The document pipeline follows a standard Retrieval-Augmented Generation architecture.

PDF Upload
    │
    ▼
Document Loader
    │
    ▼
Text Extraction
    │
    ▼
Chunking
    │
    ▼
Embedding Generation
    │
    ▼
Pinecone
    │
    │
    │       USER QUESTION
    │            │
    │            ▼
    │       Query Embedding
    │            │
    └────────────┤
                 ▼
          Similarity Search
                 │
                 ▼
          Relevant Chunks
                 │
                 ▼
         Context Construction
                 │
                 ▼
              Gemini
                 │
                 ▼
          Answer + Sources
Document RAG capabilities
📄 PDF upload
📑 Text extraction
✂️ Chunking
🧮 Embedding generation
🗄️ Pinecone vector storage
🔎 Semantic retrieval
🧠 Context construction
🤖 LLM generation
📚 Source tracking
🌐 Web RAG

Web RAG is completely separate from normal Web Search.

When the user provides a URL:

USER URL
   │
   ▼
URL Validation
   │
   ▼
URL Normalization
   │
   ▼
Web Extraction
   │
   ├──────────────┐
   │              │
   ▼              ▼
Requests      Playwright
   │              │
   └──────┬───────┘
          │
          ▼
   Generic Reader
      Fallback
          │
          ▼
    Clean Content
          │
          ▼
       Chunking
          │
          ▼
      Embeddings
          │
          ▼
       Pinecone
          │
          ▼
  Semantic Retrieval
          │
          ▼
       Gemini
          │
          ▼
    Answer + Sources
🔗 Web RAG Context Persistence

A major part of the architecture is maintaining the URL context.

Example:

USER
│
├── https://example.com
│
▼
WEB RAG
│
├── Extract webpage
├── Chunk content
├── Generate embeddings
└── Store/index in Pinecone
│
▼
Assistant Answer

Then the user can ask:

"What are the main services?"

The system can reuse the active webpage context.

Previous URL
     │
     ▼
Web Context
     │
     ▼
Follow-up Question
     │
     ▼
Web Retrieval
     │
     ▼
Gemini
     │
     ▼
Answer

This creates a conversational Web RAG experience rather than a one-time URL summarizer.

🔎 Web RAG Retrieval

Web vectors contain metadata that identifies their original webpage.

Example metadata:

type
source
url
title
document_id
chunk_index
extraction_method
text

Retrieval can use the URL metadata to keep webpage questions grounded in the appropriate web content.

User Question
      │
      ▼
Query Embedding
      │
      ▼
Pinecone
      │
      ├── URL Metadata
      │
      ▼
Top-K Relevant Chunks
      │
      ▼
Relevance Check
      │
      ▼
Gemini
      │
      ▼
Final Answer
🔎 Live Web Search

Normal Web Search is different from Web RAG.

Web RAG
User URL
   ↓
Scrape
   ↓
Index
   ↓
Retrieve
   ↓
Answer
Live Web Search
User Question
   ↓
Search Engine
   ↓
Search Results
   ↓
Gemini
   ↓
Answer + Sources

Live Web Search is useful for:

Current information
Latest news
Recent events
Real-time information
Questions not answered by the knowledge base
🔄 RAG → Web Search Fallback

If a normal knowledge-base query does not produce sufficiently relevant information, the system can fall back to live Web Search.

                     USER QUESTION
                           │
                           ▼
                     KNOWLEDGE RAG
                           │
                           ▼
                    Pinecone Search
                           │
                    ┌──────┴──────┐
                    │             │
                  FOUND        NOT FOUND
                    │             │
                    ▼             ▼
                  Gemini      WEB SEARCH
                    │             │
                    └──────┬──────┘
                           ▼
                    FINAL ANSWER

This avoids forcing every query through the web.

🧮 Vector Database

The project uses Pinecone as the vector database.

The system stores:

Vector
   +
Metadata

Metadata may include:

source
document_id
url
title
page
chunk_index
extraction_method
text

This allows the application to:

Perform semantic search
Identify source documents
Track webpage URLs
Track pages/chunks
Return source information
Filter or scope retrieval when necessary
🤖 LLM Layer

The application uses Google Gemini for response generation.

For grounded RAG responses:

USER QUESTION
      +
RETRIEVED CONTEXT
      +
CONVERSATION HISTORY
      │
      ▼
    GEMINI
      │
      ▼
GROUNDED RESPONSE

The prompts instruct the model to:

Answer the user's question directly
Use retrieved context for RAG requests
Avoid unsupported facts
Respect the current context
Avoid exposing internal system architecture
🧠 Intent Classification

Intent classification is used to understand what the user is trying to accomplish.

The system considers:

Current query
Conversation history
Active webpage context
OCR context
Document availability
Explicit web-search requests
User-provided URLs

The system is designed around intent rather than simple keyword matching.

For example:

"What is the weather policy mentioned in the document?"

should not automatically become a weather request just because the word weather appears.

The actual intent is:

Question about document
        ↓
Document RAG

This distinction is important for reliable agentic routing.

🎙️ Voice Assistant

The application supports a complete voice interaction pipeline.

                 🎤 USER SPEAKS
                       │
                       ▼
                Streamlit Audio
                       │
                       ▼
                    FastAPI
                       │
                       ▼
                Faster-Whisper
                       │
                       ▼
                    Transcript
                       │
                       ▼
                  Supervisor
                       │
          ┌────────────┼─────────────┐
          │            │             │
          ▼            ▼             ▼
        RAG         Web RAG      Web Search
          │            │             │
          └────────────┼─────────────┘
                       │
                       ▼
                    Gemini
                       │
                       ▼
                  Text Answer
                       │
                       ▼
                    pyttsx3
                       │
                       ▼
                  🔊 Voice Output

The voice pipeline uses the same agentic routing system as typed questions.

🔊 Text-to-Speech

After the assistant generates a response:

Gemini Response
      │
      ▼
FastAPI /voice/speak
      │
      ▼
pyttsx3
      │
      ▼
WAV File
      │
      ▼
Streamlit Audio Player
      │
      ▼
🔊 Assistant Voice
🖼️ OCR / Image Questions

The system also supports image-based interaction.

        🖼️ IMAGE
            │
            ▼
           OCR
            │
            ▼
      Extracted Text
            │
            ▼
      Agent Context
            │
            ▼
      User Question
            │
            ▼
          Gemini
            │
            ▼
          Answer

This allows users to ask questions about information contained inside images.

💬 Conversation History

Conversation history is maintained through Streamlit session state and passed through the backend agent state.

Message 1
    │
    ▼
Message 2
    │
    ▼
Message 3
    │
    ▼
Current Question
    │
    ▼
Supervisor

Example:

User:
What is this webpage about?


Assistant:
The webpage explains ...


User:
Who are its main users?


Assistant:
Based on the webpage ...

The history allows the system to understand follow-up questions.

🔌 Backend API

The backend is implemented using FastAPI.

Endpoint	Purpose
POST /api/chat	Main Agentic RAG request
POST /api/voice/transcribe	Speech-to-text
POST /api/voice/speak	Text-to-speech
POST /api/documents/upload	Upload PDF
GET /api/documents/	List available documents
GET /api/documents/view/{filename}	View document
POST /api/multimodal/ocr	Extract text from image
POST /api/multimodal/ask-image	Ask questions about image content
🎨 Frontend

The frontend is built using Streamlit.

frontend/
│
├── components/
│   ├── chat.py
│   ├── sidebar.py
│   ├── sources.py
│   └── voice_input.py
│
├── utils/
│   └── api_client.py
│
├── streamlit_app.py
│
└── style.css

The frontend communicates with FastAPI through a dedicated API client.

This keeps:

UI Logic
   ≠
Backend Logic

and makes the application easier to maintain.

📁 Final Project Structure
Agentic_RAG/
│
├── 📁 app/
│   │
│   ├── 📁 agents/
│   │   ├── classifier.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── supervisor.py
│   │
│   ├── 📁 api/
│   │   └── 📁 routes/
│   │       ├── chat.py
│   │       └── voice.py
│   │
│   ├── 📁 rag/
│   │   ├── document_rag.py
│   │   ├── loaders.py
│   │   ├── pinecone_client.py
│   │   ├── retriever.py
│   │   ├── web_chunker.py
│   │   ├── web_indexer.py
│   │   ├── web_loader.py
│   │   ├── web_playwright.py
│   │   ├── web_rag.py
│   │   ├── web_retriever.py
│   │   └── web_scraper.py
│   │
│   ├── 📁 llm/
│   │   └── gemini.py
│   │
│   ├── 📁 speech/
│   │   ├── stt.py
│   │   └── tts.py
│   │
│   └── 📁 tools/
│       ├── weather_tool.py
│       └── web_search_tool.py
│
├── 📁 frontend/
│   │
│   ├── 📁 components/
│   │   ├── chat.py
│   │   ├── sidebar.py
│   │   ├── sources.py
│   │   └── voice_input.py
│   │
│   ├── 📁 utils/
│   │   └── api_client.py
│   │
│   ├── streamlit_app.py
│   └── style.css
│
├── 📁 data/
│   ├── documents/
│   ├── images/
│   └── audio/
│
├── 📄 .env
├── 📄 .gitignore
├── 📄 requirements.txt
├── 📄 README.md
└── 📄 ...

Note: .env, temporary audio files, generated files and sensitive runtime data should not be committed to GitHub.

🛠️ Technology Stack
Layer	Technology
🐍 Programming Language	Python
🎨 Frontend	Streamlit
⚡ Backend	FastAPI
🧠 Agent Orchestration	LangGraph
🤖 LLM	Google Gemini
🗄️ Vector Database	Pinecone
🔎 Retrieval	Semantic Vector Search
📄 Document Processing	PDF / Document Loaders
🌐 HTTP Requests	Requests
🧹 HTML Parsing	BeautifulSoup
🌐 Browser Automation	Playwright
🎙️ Speech Recognition	Faster-Whisper
🔊 Text-to-Speech	pyttsx3
📦 Validation	Pydantic
💬 State Management	LangGraph + Streamlit Session State
🎨 Styling	CSS
🔧 Version Control	Git / GitHub
🚀 Getting Started
1. Clone the Repository
git clone https://github.com/27Shambhavi/Agentic_RAG.git
cd Agentic_RAG
2. Create a Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt

If Playwright is required:

playwright install chromium
🔐 Environment Variables

Create a .env file in the project root.

Example:

GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index

Never commit API keys to GitHub.

Recommended .gitignore entries:

.env
.env.*
.venv/
__pycache__/
*.pyc


.streamlit/


data/audio/
data/images/


*.wav
*.mp3
*.m4a
▶️ Running the Application
Start FastAPI
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000
Start Streamlit

Open another terminal:

streamlit run frontend/streamlit_app.py

Then open the Streamlit URL shown in the terminal.

🧪 Example Usage
📄 Document RAG

Upload multiple documents:

Ayushman-Bharat.pdf
Dummy-Bank-Statement.pdf
Employee-Handbook.pdf
Leave-Policy.pdf

Ask:

What is the name of the bank?

The system searches the knowledge base and retrieves the relevant document even if another document is currently selected.

Question
   ↓
Supervisor
   ↓
Knowledge RAG
   ↓
Pinecone
   ↓
Relevant Document
   ↓
Gemini
   ↓
Answer + Sources
🌐 Web RAG

Enter:

https://en.wikipedia.org/wiki/Artificial_intelligence

Then ask:

What is this webpage about?

The system:

URL
 ↓
Web Extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
Pinecone
 ↓
Retrieval
 ↓
Gemini
 ↓
Answer
🔎 Live Web Search

Ask:

What is the latest AI news today?

The system:

Question
 ↓
Supervisor
 ↓
Web Search
 ↓
Search Results
 ↓
Gemini
 ↓
Answer + Sources
🎙️ Voice

Speak:

What is machine learning?

The system:

Voice
 ↓
Faster-Whisper
 ↓
Transcript
 ↓
Supervisor
 ↓
General AI
 ↓
Gemini
 ↓
Answer
 ↓
pyttsx3
 ↓
Audio Response
🛡️ Error Handling

The application includes validation and error handling for:

Empty user queries
Invalid URLs
Failed webpage extraction
Unsupported audio formats
Empty audio files
Failed vector retrieval
Missing API keys
Invalid backend responses
LLM generation failures
TTS failures
Insufficient RAG context
Missing webpage context
Temporary file cleanup

Debug logging is available across the main pipeline:

Frontend
   ↓
FastAPI
   ↓
Supervisor
   ↓
Agent Node
   ↓
Retriever / Tool
   ↓
Pinecone / Search
   ↓
Gemini
   ↓
Final Response
🔍 Important Architectural Decisions
1. Selected Document ≠ Knowledge Base Restriction

Selecting a document in the UI does not mean:

❌ Search ONLY this PDF forever

Instead:

✅ Selected PDF = current UI/context preference


✅ Knowledge Base = searchable collection of indexed documents

This allows the assistant to switch between documents naturally.

2. Web RAG ≠ Web Search

These are intentionally separate.

Web RAG
User URL
   ↓
Extract
   ↓
Index
   ↓
Retrieve
   ↓
Answer
Web Search
Question
   ↓
Search Internet
   ↓
Search Results
   ↓
Answer
3. URL Context Should Persist

When a user provides a URL, the system stores the webpage context so follow-up questions can continue using that webpage.

URL
 ↓
Web RAG
 ↓
Stored Web Context
 ↓
Follow-up
 ↓
Web Retrieval
 ↓
Answer
4. RAG and Web Search Can Switch

The user is not permanently locked into one route.

The application can move between:

📚 Knowledge RAG
      ↓
🌐 Web RAG
      ↓
🔎 Web Search
      ↓
🤖 General AI

depending on the current request and context.

🎯 Design Principles
🧩 Modular

Each major capability is isolated into its own module.

🧠 Agentic

The system dynamically selects the appropriate processing path.

📚 Retrieval-Grounded

RAG answers are generated using retrieved context.

🔄 Context-Aware

Conversation history and webpage context can be reused for follow-up questions.

🌐 URL-Agnostic

Web extraction uses multiple generic strategies instead of hard-coded website-specific logic.

🎙️ Multimodal

The assistant supports:

Text
PDF
Web
Image
Voice
🚀 Extensible

New tools and agents can be added to the LangGraph workflow without redesigning the complete application.

📊 Current Capabilities
Capability	Status
Streamlit Frontend	✅
FastAPI Backend	✅
LangGraph Agent Architecture	✅
Supervisor Routing	✅
Intent Classification	✅
Multi-Document RAG	✅
Pinecone Retrieval	✅
Gemini Generation	✅
Web RAG	✅
Persistent Web Indexing	✅
URL-Based Web Retrieval	✅
Live Web Search	✅
Conversation History	✅
OCR Pipeline	✅
Faster-Whisper STT	✅
pyttsx3 TTS	✅
Source Rendering	✅
Requests Extraction	✅
BeautifulSoup Parsing	✅
Playwright Fallback	✅
Generic Reader Fallback	✅
Error Handling	✅
Debug Logging	✅
⚠️ Web RAG Limitations

Web RAG depends on the accessibility and structure of the target webpage.

Some websites may not be extractable because of:

🔐 Authentication/login requirements
🤖 CAPTCHA
🛡️ Strong anti-bot protection
🚫 Robots/access restrictions
🌍 Region restrictions
⚡ Highly dynamic client-side applications
🖱️ Complex user interaction
🔌 API-only content

Multiple extraction strategies improve coverage, but 100% webpage coverage cannot be guaranteed.

🔮 Future Improvements

Potential future improvements include:

🔄 Streaming LLM responses
🧠 Long-term conversation memory
⚡ Redis-based session management
🔎 Hybrid keyword + semantic retrieval
🏆 Advanced reranking
🌍 Better multilingual voice support
🎙️ GPU-based Faster-Whisper inference
🔊 Higher-quality neural TTS
🔐 Authentication and user management
⚙️ Background document/web indexing
🐳 Docker deployment
☁️ Cloud deployment
📊 Observability and tracing
🧪 Automated RAG evaluation datasets
📈 Retrieval quality metrics
🧠 Agent execution tracing
🌐 Improved webpage extraction
💡 What I Built

This project was developed as a practical exploration of how modern AI applications are built beyond simply calling an LLM API.

Instead of:

User → LLM → Answer

the system follows:

                    RAW INPUT
                        │
                        ▼
                 PREPROCESSING
                        │
                        ▼
                INTENT ANALYSIS
                        │
                        ▼
                  SUPERVISOR
                        │
                        ▼
                  AGENT ROUTING
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
      RAG            WEB RAG        WEB SEARCH
        │               │                │
        └───────────────┼────────────────┘
                        │
                        ▼
                    RETRIEVAL
                        │
                        ▼
                 CONTEXT BUILDING
                        │
                        ▼
                     GEMINI
                        │
                        ▼
                SOURCE ATTRIBUTION
                        │
                        ▼
                  FINAL RESPONSE
🧠 Key Learning

One of the biggest lessons from building this project was:

A powerful LLM is not enough. Correct routing, state management, retrieval and context handling are equally important.

The application therefore separates:

🧠 Decision
    ↓
🔀 Routing
    ↓
🔎 Retrieval / Tool Execution
    ↓
📚 Context Construction
    ↓
🤖 LLM Generation
    ↓
📑 Source Attribution
    ↓
💬 Final Response

This separation makes the application easier to debug, extend and maintain.

📚 Learning Outcomes

Through this project, I worked with:

Agentic workflow design
LangGraph
RAG architecture
Vector databases
Embeddings
Semantic search
Prompt engineering
LLM integration
Intent classification
State management
FastAPI
Streamlit
PDF processing
Web scraping
Browser automation
Speech recognition
Text-to-speech
OCR
API integration
Error handling
Debugging
Git/GitHub project management

Most importantly, this project helped me understand the behind-the-scenes architecture of an AI assistant — how raw inputs are transformed into structured context, routed through specialized capabilities, retrieved when necessary, passed to an LLM, and finally returned to the user through text or voice.

📌 Project Summary

Agentic RAG Space is a modular, multimodal AI assistant built using:

🐍 Python
⚡ FastAPI
🎨 Streamlit
🧠 LangGraph
🤖 Google Gemini
🗄️ Pinecone
🎙️ Faster-Whisper
🔊 pyttsx3
🌐 Requests
🧹 BeautifulSoup
🌐 Playwright

The assistant intelligently routes user requests across:

📚 Multi-Document RAG
🌐 Web RAG
🔎 Live Web Search
🖼️ OCR
🌤️ Weather
🤖 General AI
👋 Conversational Requests
🎙️ Voice Interaction

The result is a flexible AI system capable of combining Agentic AI + RAG + Vector Search + Web Intelligence + Multimodal Processing + Voice Interaction in one modular application.

👩‍💻 Author
Shambhavi Jha

🎓 B.Tech — Computer Science Engineering
📊 Specialization: Data Science

Areas of Interest
🤖 Artificial Intelligence
🧠 Machine Learning
✨ Generative AI
🔤 Large Language Models
📚 Retrieval-Augmented Generation
🔀 Agentic AI
📊 Data Science
⚙️ Backend Engineering
⭐ Final Note

This project was built as a hands-on exploration of Agentic RAG architecture and modern AI application development.

The goal was not just to make a chatbot work, but to understand and implement the complete flow:

                    ┌─────────────────────┐
                    │       USER          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    SUPERVISOR       │
                    │   INTENT ROUTER     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   📚 KNOWLEDGE             🌐 WEB RAG           🔎 WEB SEARCH
       RAG                      │                      │
        │                       │                      │
        ▼                       ▼                      ▼
    Pinecone              Web Extraction          Search API
        │                       │                      │
        └───────────────┬───────┴──────────────────────┘
                        │
                        ▼
                  🧠 CONTEXT
                        │
                        ▼
                 🤖 GEMINI LLM
                        │
                        ▼
               📑 SOURCES + ANSWER
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
          💬 TEXT UI          🔊 VOICE

Built with the goal of understanding what happens behind the scenes of modern AI systems. 🚀
