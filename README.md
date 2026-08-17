# 🤖 Agentic RAG Space — Multimodal AI Knowledge Assistant

> An **Agentic Retrieval-Augmented Generation (RAG) system** that intelligently routes user queries across document RAG, Web RAG, general AI, OCR, voice, weather, and conversational capabilities.

---

## 🌟 Overview

**Agentic RAG Space** is a modular AI assistant designed to go beyond a traditional chatbot.

Instead of sending every question through the same pipeline, the system uses an **agentic routing architecture built with LangGraph**. A supervisor analyzes the user's intent and routes the request to the most appropriate capability.

The system can work with:

- 📄 Uploaded PDF documents
- 🌐 Arbitrary webpages/URLs
- 🖼️ Images and OCR
- 🎙️ Voice input
- 🔊 Voice responses
- 💬 Conversational history
- 🤖 General AI questions
- 🌤️ Weather-related queries
- 🔎 Retrieved sources and metadata

The goal is to combine **RAG, agentic orchestration, multimodal interaction, and production-style API architecture** into a single extensible AI assistant.

---

# ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Agentic Routing** | LangGraph-based supervisor routes requests to the appropriate agent |
| 📄 **Document RAG** | Ask questions about uploaded PDF documents |
| 🌐 **Dynamic Web RAG** | Provide a URL and retrieve information from the webpage |
| 🔎 **Semantic Retrieval** | Uses embeddings and Pinecone for vector similarity search |
| 🤖 **Gemini LLM** | Generates context-aware responses |
| 🖼️ **OCR** | Extract and query text from images |
| 🎙️ **Speech-to-Text** | Converts recorded voice into text using Faster-Whisper |
| 🔊 **Text-to-Speech** | Converts assistant responses into audio using pyttsx3 |
| 💬 **Conversation History** | Maintains recent conversational context |
| 📚 **Source Tracking** | Displays retrieved document/web sources |
| 🧩 **Modular Architecture** | Separate frontend, API, agents, RAG and speech layers |
| ⚡ **FastAPI Backend** | REST API layer for the AI system |
| 🎨 **Streamlit Frontend** | Interactive user interface |
| 🛡️ **Fallback Web Extraction** | Requests → Playwright → generic reader fallback |

---

# 🏗️ High-Level Architecture

```text
                         ┌──────────────────────────┐
                         │      STREAMLIT UI         │
                         │        FRONTEND           │
                         └────────────┬─────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │                                 │
                   TEXT                              VOICE
                     │                                 │
                     │                          Faster-Whisper
                     │                                 │
                     └────────────────┬────────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │        FASTAPI            │
                         │         BACKEND           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       LANGGRAPH            │
                         │      AGENTIC GRAPH         │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │  SUPERVISOR  │
                              │   / ROUTER   │
                              └───────┬──────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
      ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
      │ Document RAG│          │   Web RAG   │          │ General AI  │
      └──────┬──────┘          └──────┬──────┘          └─────────────┘
             │                        │
             ▼                        ▼
        PDF Loader              URL Extraction
             │                        │
             ▼                 ┌──────┼────────┐
        Chunking               │      │        │
             │             Requests Playwright Reader
             │                 │      │        │
             │                 └──────┼────────┘
             │                        ▼
             │                    Chunking
             │                        │
             └────────────┬───────────┘
                          ▼
                    ┌────────────┐
                    │ Embeddings │
                    └─────┬──────┘
                          ▼
                    ┌────────────┐
                    │  Pinecone  │
                    │ Vector DB   │
                    └─────┬──────┘
                          │
                          ▼
                  Relevant Context
                          │
                          ▼
                    ┌──────────┐
                    │  Gemini  │
                    │   LLM    │
                    └────┬─────┘
                         │
                         ▼
                  Final Response
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
          Text UI                pyttsx3
                                     │
                                     ▼
                                  🔊 Audio
🧠 Agentic RAG Architecture

The central design principle is route first, answer second.

The supervisor does not directly answer the user. It determines which capability should process the request.

User Query
    │
    ▼
Supervisor
    │
    ├── Greeting ───────► Greeting Node
    │
    ├── General ────────► General AI Node
    │
    ├── Document ───────► Document RAG Node
    │
    ├── Web ────────────► Web RAG Node
    │
    ├── OCR ────────────► OCR Node
    │
    └── Weather ────────► Weather Node

This allows the application to be extended with additional agents without rewriting the complete system.

🔀 Query Routing

Examples of how requests are handled:

User Request	Route
Hi, how are you?	👋 Greeting
Explain machine learning	🤖 General AI
What does my uploaded PDF say about leave policy?	📄 Document RAG
https://example.com — summarize this	🌐 Web RAG
What is this image saying?	🖼️ OCR
What's the weather today?	🌤️ Weather
Voice question about a PDF	🎙️ → 📄 Document RAG
Voice question about a webpage	🎙️ → 🌐 Web RAG
📄 Document RAG

The document pipeline follows a standard retrieval-augmented generation architecture.

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
Embeddings
    │
    ▼
Pinecone
    │
    ▼
User Query
    │
    ▼
Query Embedding
    │
    ▼
Similarity Search
    │
    ▼
Relevant Chunks
    │
    ▼
Gemini
    │
    ▼
Answer + Sources
Document RAG capabilities
PDF upload
Document indexing
Text extraction
Chunking
Embedding generation
Pinecone vector storage
Semantic retrieval
Context construction
LLM generation
Source tracking
🌐 Dynamic Web RAG

One of the major components of the project is URL-based RAG.

The user can provide a webpage URL and ask questions about the content.

User URL
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
   ├── Requests + BeautifulSoup
   │
   ├── If unsuccessful
   │        ▼
   │    Playwright
   │
   └── If unsuccessful
            ▼
       Generic Reader
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
🔧 Web Extraction Strategy

The system is designed to be URL-agnostic, rather than being customized for individual websites.

1. Requests + BeautifulSoup

Used as the first extraction method because it is lightweight and fast.

2. Playwright

Used for webpages that require JavaScript rendering or dynamically generated content.

Additional browser handling includes:

JavaScript execution
Browser context configuration
User-agent configuration
Network-idle waiting
Cookie/consent handling attempts
Lazy-loading support through scrolling
Rendered body extraction
HTML fallback
3. Generic Reader Fallback

If direct HTTP extraction and browser rendering fail, the system attempts a generic reader-based extraction method.

This avoids hard-coding logic for specific websites.

Important: No scraper can guarantee access to every website. Pages protected by authentication, CAPTCHA, aggressive anti-bot systems, restricted APIs, or highly interactive client-side applications may still be inaccessible.

🔎 Web RAG Retrieval

Web content is indexed with metadata such as:

type
source
url
title
document_id
method
page
chunk_index
text

The retrieval process can restrict results to the current webpage URL.

User Question
      │
      ▼
Query Embedding
      │
      ▼
Pinecone
      │
      ├── URL Metadata Filter
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

The LLM is instructed to answer from the retrieved webpage context instead of relying on unrelated outside knowledge.

🧮 Vector Database

The project uses Pinecone as the vector database.

Stored information
Vector
   +
Metadata

Metadata can include:

source
URL
document ID
title
page
chunk index
extraction method
original text

This allows the application to perform semantic retrieval while retaining source information for the frontend.

🤖 LLM Layer

The project uses Google Gemini for response generation.

Gemini is used after retrieval rather than blindly answering every RAG question from general model knowledge.

For RAG requests:

User Query
     +
Retrieved Context
     +
Conversation History
     ↓
   Gemini
     ↓
Grounded Response

The prompts also contain restrictions designed to reduce unsupported answers.

🎙️ Voice Assistant

The application supports a complete voice interaction pipeline.

Speech → Text
🎤 User Speaks
      ↓
Streamlit Audio Input
      ↓
FastAPI
      ↓
Temporary Audio File
      ↓
Faster-Whisper
      ↓
Transcript
      ↓
Agentic Router
      ↓
Appropriate Agent
Technology
Faster-Whisper
Whisper Base model
CPU inference
INT8 computation
Voice Activity Detection
🔊 Text → Speech

After the assistant generates an answer:

Gemini Response
      ↓
FastAPI /voice/speak
      ↓
pyttsx3
      ↓
WAV File
      ↓
Streamlit Audio Player
      ↓
🔊 Assistant Voice

This allows voice input to participate in the same Agentic RAG pipeline as typed input.

🖼️ OCR / Multimodal Processing

The system also supports image-based interaction.

Image
  ↓
OCR
  ↓
Extracted Text
  ↓
Agent Context
  ↓
User Question
  ↓
LLM
  ↓
Answer

This allows users to provide information that is not originally available as typed text.

💬 Conversation History

The frontend maintains conversation messages through Streamlit session state.

Recent conversation history is passed into the backend and agent state.

Message 1
   ↓
Message 2
   ↓
Message 3
   ↓
Current Query
   ↓
Agent

This enables follow-up questions such as:

User:
What is this webpage about?

Assistant:
...

User:
Who are its main users?

Assistant:
...
🔌 Backend API

The backend is implemented using FastAPI.

Main endpoints
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

The frontend is built with Streamlit and separated into reusable components.

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

The frontend communicates with the backend through a dedicated API client instead of directly implementing backend logic.

🧩 Backend Structure
app/
│
├── agents/
│   ├── classifier.py
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   └── supervisor.py
│
├── api/
│   └── routes/
│       ├── chat.py
│       └── voice.py
│
├── rag/
│   ├── document_rag.py
│   ├── loaders.py
│   ├── web_chunker.py
│   ├── web_indexer.py
│   ├── web_loader.py
│   ├── web_playwright.py
│   ├── web_rag.py
│   ├── web_retriever.py
│   └── web_scraper.py
│
└── speech/
    ├── stt.py
    └── tts.py

🛠️ Technology Stack

Layer	Technology
Programming Language	Python
Frontend	Streamlit
Backend	FastAPI
Agent Orchestration	LangGraph
LLM	Google Gemini
Vector Database	Pinecone
Embeddings	Project embedding model
PDF Processing	Python PDF/document loaders
Web Requests	Requests
HTML Parsing	BeautifulSoup
Dynamic Web Automation	Playwright
Speech Recognition	Faster-Whisper
Text-to-Speech	pyttsx3
API Validation	Pydantic
HTTP Communication	REST / Requests
State	LangGraph State + Streamlit Session State
Styling	CSS
Version Control	Git / GitHub
📁 Project Structure
Rag_Agentic_space/
│
├── app/
│   │
│   ├── agents/
│   │   ├── classifier.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── supervisor.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py
│   │       └── voice.py
│   │
│   ├── rag/
│   │   ├── document_rag.py
│   │   ├── loaders.py
│   │   ├── web_chunker.py
│   │   ├── web_indexer.py
│   │   ├── web_loader.py
│   │   ├── web_playwright.py
│   │   ├── web_rag.py
│   │   ├── web_retriever.py
│   │   └── web_scraper.py
│   │
│   └── speech/
│       ├── stt.py
│       └── tts.py
│
├── frontend/
│   │
│   ├── components/
│   │   ├── chat.py
│   │   ├── sidebar.py
│   │   ├── sources.py
│   │   └── voice_input.py
│   │
│   ├── utils/
│   │   └── api_client.py
│   │
│   ├── streamlit_app.py
│   └── style.css
│
├── data/
│   ├── documents/
│   ├── images/
│   └── audio/
│
├── .gitignore
├── requirements.txt
└── README.md

Runtime-generated files such as audio recordings, local documents, images, environment files and other sensitive/generated data should be excluded from version control where appropriate.

🚀 Getting Started
1. Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Rag_Agentic_space
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

Do not commit .env to GitHub.

Make sure .gitignore contains:

.env
.env.*
▶️ Running the Application
Start FastAPI
uvicorn app.main:app --reload

The backend will typically run at:

http://127.0.0.1:8000
Start Streamlit

In another terminal:

streamlit run frontend/streamlit_app.py

The Streamlit interface will then be available through the local Streamlit URL shown in the terminal.

🧪 Example Usage
📄 Document RAG
Upload:
employee_handbook.pdf

Ask:
"What is the leave policy?"

The system:

Question
 ↓
Supervisor
 ↓
Document RAG
 ↓
Pinecone
 ↓
Relevant PDF chunks
 ↓
Gemini
 ↓
Answer + Sources
🌐 Web RAG

Enter:

https://en.wikipedia.org/wiki/Artificial_intelligence

Then ask:

"What is this webpage about?"

The system dynamically:

URL
 ↓
Requests
 ↓
Playwright if required
 ↓
Reader fallback if required
 ↓
Content extraction
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
🎙️ Voice

Speak:

"What is machine learning?"

The system:

Voice
 ↓
Faster-Whisper
 ↓
Text
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
Audio response
🛡️ Error Handling

The project includes validation and error handling across multiple layers.

Examples include:

Empty user queries
Invalid URLs
Unsupported audio formats
Empty audio files
Failed webpage extraction
Insufficient webpage content
Failed vector retrieval
Invalid backend responses
Failed LLM generation
Failed TTS generation
Temporary file cleanup
Missing/invalid context

The application also includes structured debugging logs to trace requests across the frontend, API, agent, retrieval and speech layers.

🔍 Design Principles
1. Modular

Each major capability has its own module.

2. Agentic

The system dynamically chooses the appropriate processing path.

3. Retrieval-Grounded

RAG responses are generated using retrieved context rather than relying solely on the LLM.

4. Multimodal

The system supports:

Text
PDF
Web
Image
Voice
5. Extensible

New agents can be added to the LangGraph architecture without redesigning the entire application.

6. URL-Agnostic Web RAG

Web extraction is designed around multiple generic extraction methods instead of website-specific rules.

📊 Current Capabilities
Capability	Status
Streamlit frontend	✅
FastAPI backend	✅
LangGraph agent architecture	✅
Supervisor routing	✅
Document RAG	✅
Pinecone retrieval	✅
Gemini generation	✅
Dynamic Web RAG	✅
Requests web extraction	✅
BeautifulSoup parsing	✅
Playwright fallback	✅
Generic reader fallback	✅
URL-specific vector filtering	✅
Conversation history	✅
OCR pipeline	✅
Faster-Whisper STT	✅
pyttsx3 TTS	✅
Source rendering	✅
Modular API client	✅
Error handling/debug logging	✅
⚠️ Web RAG Limitations

Web RAG depends on the accessibility and structure of the target webpage.

Some websites may not be extractable because of:

Authentication/login requirements
CAPTCHA
Strong anti-bot protection
Robots/access restrictions
Highly dynamic client-side applications
Content loaded only after complex user interaction
Region restrictions
API-only content

The system therefore uses multiple generic extraction strategies, but 100% webpage coverage cannot be guaranteed.

🔮 Future Improvements

Potential future improvements include:

Streaming LLM responses
Better persistent conversation memory
Redis-based session management
More advanced reranking
Hybrid keyword + semantic retrieval
Better multilingual voice support
GPU-based Faster-Whisper inference
Higher-quality neural TTS
Authentication and user management
Background document/web indexing
Celery or task-queue based processing
Docker deployment
Cloud deployment
Observability and tracing
Automated evaluation datasets
RAG evaluation metrics
Agent execution tracing
Better webpage-specific content extraction without hard-coding websites

🎯 What I Built

This project was developed as a practical exploration of how modern AI systems are constructed beyond simply calling an LLM API.

The main focus was understanding the complete pipeline:

Raw Input
    ↓
Preprocessing
    ↓
Intent Classification
    ↓
Agent Routing
    ↓
Retrieval / Tool Execution
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Source Attribution
    ↓
Final Response

The project combines Agentic AI + RAG + Vector Search + Multimodal Processing + Voice + Web Intelligence into one modular application.

👩‍💻 Learning Outcomes

Through this project, I worked with:

Agentic workflow design
LangGraph
RAG architecture
Vector databases
Embeddings
Semantic search
Prompt engineering
LLM integration
FastAPI API development
Streamlit application development
PDF processing
Web scraping
Browser automation
Speech recognition
Text-to-speech
OCR
API integration
State management
Error handling
Debugging distributed application flows
Git/GitHub project management

Most importantly, the project helped me understand the "behind the scenes" of an AI application—how raw inputs are transformed into structured context, routed through specialized components, retrieved when necessary, passed to an LLM, and finally returned to the user through text or voice.

📌 Project Summary

Agentic RAG Space is a modular, multimodal AI assistant built using LangGraph, FastAPI, Streamlit, Gemini and Pinecone. It intelligently routes user requests across document RAG, dynamic Web RAG, general AI, OCR, weather and conversational capabilities. The system supports both text and voice interaction, uses Faster-Whisper for speech recognition and pyttsx3 for speech synthesis, and employs multiple generic web extraction strategies including Requests, BeautifulSoup, Playwright and a reader fallback.

👩‍💻 Author

Shambhavi Jha

B.Tech — Computer Science Engineering
Specialization: Data Science

Interested in:

Artificial Intelligence
Machine Learning
Generative AI
LLMs
RAG
Agentic AI
Data Science
Backend Engineering
