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

🌟 Overview

Agentic RAG Space is a modular AI assistant built to explore how modern AI applications work beyond simply sending every question to an LLM.

The system uses LangGraph-based agentic orchestration to analyze the user's request and select the appropriate execution path.

The assistant supports:

📄 Multi-document PDF RAG
🌐 URL-based Web RAG
🔎 Live Web Search
🖼️ OCR-based image questions
🎙️ Speech-to-Text
🔊 Text-to-Speech
💬 Conversation history
🤖 General AI conversations
🌤️ Weather queries
📚 Source attribution
🧠 Semantic vector retrieval
⚡ FastAPI backend
🎨 Streamlit frontend

The core design principle is:

                 USER QUERY
                      │
                      ▼
                🧠 SUPERVISOR
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
       KNOWLEDGE    WEB RAG      WEB SEARCH
          │           │            │
          ▼           ▼            ▼
       Pinecone    URL Data      Internet
          │           │
          └─────┬─────┘
                ▼
             Gemini
                │
                ▼
          Final Response
✨ Key Features
Feature	Description
🧠 Agentic Routing	LangGraph supervisor determines the appropriate execution path
📚 Multi-Document RAG	Searches across the complete knowledge base instead of being restricted to the selected PDF
📄 PDF RAG	Upload and query PDF documents
🌐 Web RAG	Provide a URL and ask questions about that webpage
💾 Persistent Web Knowledge	Webpage content is chunked, embedded and stored in Pinecone
🔎 Live Web Search	Searches the internet when knowledge-base information is insufficient or a current answer is requested
🔗 URL Context Memory	Follow-up questions can continue using the previously supplied webpage
🧮 Semantic Search	Embedding-based similarity retrieval
🤖 Gemini LLM	Context-grounded answer generation
🖼️ OCR	Ask questions about extracted image text
🎙️ Speech-to-Text	Faster-Whisper voice transcription
🔊 Text-to-Speech	pyttsx3 voice responses
💬 Conversation History	Supports contextual follow-up questions
📚 Source Attribution	Returns document/web sources
⚡ FastAPI	REST API backend
🎨 Streamlit	Interactive frontend
🛡️ Error Handling	Validation and graceful fallback across major components
🧠 The Core Problem I Solved

One of the major challenges during development was routing and context management.

Initially, selecting a document could unintentionally make that document the only searchable source.

For example:

Selected:
Ayushman-Bharat.pdf


Question:
"What is the name of the bank?"

Even if the answer existed inside:

Dummy-Bank-Statement.pdf

the system could incorrectly restrict retrieval to the selected PDF.

❌ Old Behavior
Selected PDF
     ↓
Search ONLY selected PDF
     ↓
No answer
     ↓
Wrong fallback / wrong route
✅ Final Behavior
User Question
      ↓
Knowledge Base Search
      ↓
Search across indexed documents
      ↓
Relevant document found?
      │
   ┌──┴──┐
   │     │
  YES    NO
   │     │
   ▼     ▼
 Answer  Web Search

Therefore:

The selected document is a UI/context preference, not a hard boundary on the entire knowledge base.

This allows the assistant to switch naturally between documents.

🔀 Intelligent Query Routing

The system separates knowledge retrieval, Web RAG, and live web search.

📚 Knowledge Base RAG

Used when the answer may exist in the indexed knowledge base.

Question
   ↓
Knowledge RAG
   ↓
Pinecone
   ↓
Relevant document/chunks
   ↓
Gemini
   ↓
Answer

The search is not limited to the currently selected PDF.

🌐 Web RAG

Used when the user explicitly provides a URL.

User URL
   ↓
Web Extraction
   ↓
Cleaning
   ↓
Chunking
   ↓
Embeddings
   ↓
Pinecone
   ↓
Webpage Context
   ↓
Gemini
   ↓
Answer

The URL becomes part of the application's web context so follow-up questions can continue referring to it.

Example:

User:
https://example.com


Assistant:
[Analyzes webpage]


User:
What are the main services?


Assistant:
[Uses the webpage context]
🔎 Live Web Search

Used for requests requiring current information or when the knowledge base cannot answer.

Example:

"Latest AI news today"

Flow:

Question
   ↓
Web Search
   ↓
Search Results
   ↓
Gemini
   ↓
Answer + Sources
🧩 Final Routing Architecture
                         ┌─────────────────┐
                         │    USER QUERY   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    SUPERVISOR   │
                         │     ROUTER      │
                         └────────┬────────┘
                                  │
       ┌──────────────────────────┼─────────────────────────┐
       │                          │                         │
       ▼                          ▼                         ▼
  URL PROVIDED              NORMAL QUERY              SPECIAL QUERY
       │                          │                         │
       ▼                          ▼                         ├── OCR
   WEB RAG                  KNOWLEDGE RAG                  ├── Weather
                                  │                         ├── Greeting
                                  ▼                         └── General
                           Pinecone Search
                                  │
                         ┌────────┴────────┐
                         │                 │
                    Relevant            Not Relevant
                         │                 │
                         ▼                 ▼
                     Gemini           Web Search
                         │                 │
                         └────────┬────────┘
                                  ▼
                           Final Response
🧠 Intent Classification

The classifier is responsible for understanding the user's intent, rather than blindly matching individual keywords.

The important distinction is:

❌ Keyword Detection


"weather" → weather route

versus:

✅ Intent Understanding


"What does the document say about weather-related
leave cancellation?"


→ Document RAG

The final system considers:

Current query
Conversation history
Active URL context
OCR context
Document availability
Explicit web-search requests
User-provided URLs

This prevents one piece of stale context from permanently locking the assistant into a route.

📚 Multi-Document RAG

The knowledge base can contain multiple documents.

Example:

data/documents/


├── Ayushman-Bharat.pdf
├── Dummy-Bank-Statement.pdf
├── employee_handbook.pdf
└── leave_policy.pdf

All documents can be indexed into Pinecone.

Retrieval
User Question
      ↓
Query Embedding
      ↓
Pinecone
      ↓
Search Knowledge Base
      ↓
Relevant Chunks
      ↓
Relevance Check
      ↓
Gemini
      ↓
Grounded Answer
Example
Selected Document:
Ayushman-Bharat.pdf


Question:
"What is the name of the bank?"

The system can still retrieve:

Dummy-Bank-Statement.pdf

if that document contains the relevant information.

This makes the system a true multi-document knowledge assistant rather than a single-document chatbot.

🌐 Persistent Web RAG

A major feature of the project is the ability to turn a user-provided webpage into searchable knowledge.

Web ingestion
                 USER URL
                    │
                    ▼
             URL Validation
                    │
                    ▼
            Web Extraction
                    │
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
   Requests     Playwright     Reader
       │            │             │
       └────────────┼─────────────┘
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
             Persistent Index

Webpage metadata can include:

type
source
url
title
document_id
chunk_index
extraction_method
text

This means the webpage isn't merely scraped once and forgotten.

It becomes searchable vector knowledge.

🔗 Web RAG Follow-Up Context

After a user provides a URL:

URL
 ↓
Scrape
 ↓
Index
 ↓
Pinecone

the system can retain the URL context.

Example:

User:
https://example.com


Assistant:
This webpage describes ...


User:
Who are the main users?


Assistant:
[Retrieves relevant chunks from the stored webpage]

This gives the application conversational Web RAG rather than a one-shot URL summarizer.

🔎 Knowledge RAG → Web Fallback

Another important design decision is that RAG failure does not mean the entire system is broken.

If a normal knowledge-base query cannot find relevant information:

User Question
      ↓
Knowledge RAG
      ↓
Relevant chunks?
   ┌──┴──┐
  YES    NO
   │      │
   ▼      ▼
 Answer  Web Search

For example:

User:
"What happened in today's AI news?"

The system should not search an old PDF.

It should use:

Live Web Search

Similarly, if:

Question
 ↓
Knowledge Base
 ↓
No relevant answer

the system can fall back to web search when appropriate.

📄 Document RAG Pipeline
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
    ▼
User Question
    │
    ▼
Query Embedding
    │
    ▼
Semantic Retrieval
    │
    ▼
Relevant Context
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
🧮 Embeddings
🗄️ Vector storage
🔎 Semantic retrieval
🧠 Context construction
🤖 LLM generation
📚 Source tracking
🔎 Pinecone Vector Database

The project uses Pinecone for vector storage and semantic retrieval.

Conceptually:

Vector
   +
Metadata

Metadata can include:

source
document_id
url
title
page
chunk_index
extraction_method
text

This enables the system to:

Search semantically
Identify the original document
Identify webpage sources
Track pages/chunks
Return citations/source information
Filter web knowledge by URL when required
🤖 Gemini LLM

Google Gemini is used as the primary generation model.

The LLM receives:

User Query
      +
Retrieved Context
      +
Conversation History
      ↓
    Gemini
      ↓
Grounded Response

For RAG responses, prompts instruct the model to use the retrieved context and avoid inventing unsupported information.

🌐 Web Extraction Strategy

The Web RAG system is designed to be URL-agnostic rather than being hard-coded for individual websites.

1️⃣ Requests + BeautifulSoup

First extraction method.

Advantages:

Lightweight
Fast
Suitable for static HTML
2️⃣ Playwright

Used when webpages require browser rendering.

Can handle:

JavaScript execution
Dynamic content
Browser contexts
User-agent configuration
Network waiting
Cookie/consent attempts
Lazy-loaded content
Rendered HTML
3️⃣ Generic Reader Fallback

If normal HTTP extraction and browser extraction fail, the system can attempt a generic reader-based extraction.

Important limitation

No scraper can guarantee access to every website.

Potential blockers include:

Authentication
CAPTCHA
Anti-bot systems
Robots/access restrictions
Region restrictions
Highly dynamic applications
Complex user interactions
API-only content
🎙️ Voice Pipeline

The assistant supports voice input through Faster-Whisper.

🎤 User Speech
      ↓
Audio Input
      ↓
FastAPI
      ↓
Temporary Audio File
      ↓
Faster-Whisper
      ↓
Transcript
      ↓
Supervisor
      ↓
Appropriate Agent
      ↓
Answer

This means voice input follows the same routing architecture as text.

For example:

🎙️ Voice
   ↓
"What is the leave policy?"
   ↓
Document RAG

or:

🎙️ Voice
   ↓
"What is the latest AI news?"
   ↓
Web Search
🔊 Text-to-Speech

Generated answers can be converted into audio.

Gemini Response
      ↓
FastAPI
      ↓
pyttsx3
      ↓
WAV
      ↓
Streamlit Audio Player
      ↓
🔊 Voice Response
🖼️ OCR / Image Questions

The system also supports image-based interaction.

🖼️ Image
   ↓
OCR
   ↓
Extracted Text
   ↓
Agent Context
   ↓
User Question
   ↓
Gemini
   ↓
Answer

The assistant can therefore work with information that exists inside an image rather than only typed text.

💬 Conversation History

Recent messages are maintained through Streamlit session state and passed through the backend agent state.

Message 1
   ↓
Message 2
   ↓
Message 3
   ↓
Current Query
   ↓
Supervisor

This enables follow-up questions such as:

User:
What is this webpage about?


Assistant:
...


User:
Who are its main users?


Assistant:
...
🔌 FastAPI Backend

The backend provides REST APIs for the frontend and other clients.

Endpoint	Purpose
POST /api/chat	Main Agentic RAG request
POST /api/voice/transcribe	Speech-to-text
POST /api/voice/speak	Text-to-speech
POST /api/documents/upload	Upload PDF
GET /api/documents/	List documents
GET /api/documents/view/{filename}	View document
POST /api/multimodal/ocr	Extract image text
POST /api/multimodal/ask-image	Ask questions about image content
🎨 Frontend

The frontend uses Streamlit.

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
└── style.css

The frontend communicates with FastAPI through a dedicated API client rather than directly implementing backend business logic.

🏗️ Final Project Architecture
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
│   ├── 📁 documents/
│   ├── 📁 images/
│   └── 📁 audio/
│
├── 📄 .env
├── 📄 .gitignore
├── 📄 requirements.txt
├── 📄 README.md
└── 📄 ...

🔐 .env, generated audio, temporary files and other sensitive/runtime-generated data should remain excluded from Git.

🛠️ Technology Stack
Layer	Technology
🐍 Language	Python
🎨 Frontend	Streamlit
⚡ Backend	FastAPI
🧠 Agent Orchestration	LangGraph
🤖 LLM	Google Gemini
🗄️ Vector Database	Pinecone
🔎 Retrieval	Semantic Vector Search
📄 Document Processing	Python PDF/document loaders
🌐 HTTP	Requests
🧹 HTML Parsing	BeautifulSoup
🌐 Browser Automation	Playwright
🎙️ Speech Recognition	Faster-Whisper
🔊 TTS	pyttsx3
📦 Validation	Pydantic
💬 State	LangGraph + Streamlit Session State
🎨 Styling	CSS
🔧 Version Control	Git / GitHub
🚀 Getting Started
1️⃣ Clone the repository
git clone https://github.com/27Shambhavi/Agentic_RAG.git
cd Agentic_RAG
2️⃣ Create virtual environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3️⃣ Install dependencies
pip install -r requirements.txt

If Playwright is required:

playwright install chromium
🔐 Environment Variables

Create:

.env

in the project root.

Example:

GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index

Never commit API keys.

Your .gitignore should contain:

.env
.env.*
.venv/
__pycache__/
*.pyc


data/audio/
data/images/


.streamlit/
▶️ Running the Application
Start FastAPI
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000
Start Streamlit

Open another terminal:

streamlit run frontend/streamlit_app.py

Then open the Streamlit URL shown in the terminal.

🧪 Example Workflows
📄 Example 1 — Multi-Document RAG

Suppose the knowledge base contains:

Ayushman-Bharat.pdf
Dummy-Bank-Statement.pdf
Employee-Handbook.pdf

Currently selected:

Ayushman-Bharat.pdf

User asks:

"What is the name of the bank?"

The system can still search:

Knowledge Base
      ↓
Dummy-Bank-Statement.pdf
      ↓
Relevant Chunk
      ↓
Gemini
      ↓
People's Trust Bank
🌐 Example 2 — Web RAG

User:

https://en.wikipedia.org/wiki/Artificial_intelligence

Then:

"What is this webpage about?"

Flow:

URL
 ↓
Extraction
 ↓
Chunking
 ↓
Embedding
 ↓
Pinecone
 ↓
Retrieval
 ↓
Gemini
 ↓
Answer
🔎 Example 3 — Live Web Search

User:

What is the latest AI news today?

Flow:

Supervisor
   ↓
Web Search
   ↓
Search Engine
   ↓
Results
   ↓
Gemini
   ↓
Answer + Sources
🎙️ Example 4 — Voice

User speaks:

"What is machine learning?"

Flow:

🎤 Voice
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
🔊 Audio
🛡️ Error Handling

The application handles common failures such as:

Empty queries
Invalid URLs
Failed webpage extraction
Unsupported audio
Empty audio
Failed vector retrieval
Missing API keys
Invalid backend responses
LLM generation failures
TTS failures
Insufficient RAG context
Missing webpage context
Temporary file cleanup

Debug logs are also included across:

Frontend
   ↓
FastAPI
   ↓
Supervisor
   ↓
Agent Node
   ↓
Retriever
   ↓
Pinecone
   ↓
Gemini

This made debugging routing and state-management issues significantly easier during development.

🎯 Design Principles
1. 🧩 Modular

Each capability is separated into its own module.

2. 🧠 Agentic

The application dynamically selects the appropriate processing path.

3. 📚 Retrieval-Grounded

RAG answers are generated using retrieved context.

4. 🌐 Context-Aware

Previous webpage context and conversation history can influence follow-up requests.

5. 🔄 Flexible Routing

The user can switch between:

PDF A
   ↓
PDF B
   ↓
Web
   ↓
Web Search
   ↓
General AI

without being permanently locked into one route.

6. 🌐 URL-Agnostic

Web RAG uses multiple generic extraction strategies instead of website-specific scraping rules.

7. 🎙️ Multimodal

Supports:

Text
PDF
Web
Image
Voice
8. 🚀 Extensible

New agents and tools can be added to the LangGraph workflow without redesigning the entire application.

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
URL-Specific Web Retrieval	✅
Live Web Search	✅
Conversation History	✅
OCR	✅
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

Web RAG depends on whether the target webpage can be accessed and extracted.

Some websites may prevent extraction through:

🔐 Authentication
🤖 CAPTCHA
🛡️ Anti-bot systems
🚫 Access restrictions
🌍 Region restrictions
⚡ Highly dynamic applications
🖱️ Complex user interactions
🔌 API-only content

Multiple extraction strategies improve coverage, but 100% webpage accessibility cannot be guaranteed.

🔮 Future Improvements

Potential improvements include:

🔄 Streaming LLM responses
🧠 Long-term conversation memory
⚡ Redis session management
🔎 Hybrid keyword + semantic retrieval
🏆 Advanced reranking
🌍 Better multilingual support
🎙️ GPU-based Whisper inference
🔊 Neural TTS
🔐 Authentication and user management
⚙️ Background indexing
🐳 Docker deployment
☁️ Cloud deployment
📊 Observability and tracing
🧪 Automated RAG evaluation
📈 Retrieval quality metrics
🧠 Agent execution tracing
🌐 Improved webpage extraction
💡 What I Built & Learned

This project was built as a practical exploration of modern AI application architecture.

The goal was not simply:

User → LLM → Answer

Instead, I designed a complete pipeline:

                   RAW INPUT
                       │
                       ▼
                PREPROCESSING
                       │
                       ▼
               INTENT ANALYSIS
                       │
                       ▼
                AGENT ROUTING
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       RAG          WEB RAG      WEB SEARCH
          │            │            │
          └────────────┼────────────┘
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
                 FINAL ANSWER

The project helped me understand the practical challenges behind:

Agentic AI
Intent classification
State management
RAG architecture
Vector databases
Embeddings
Semantic retrieval
Prompt engineering
Web extraction
LLM integration
FastAPI
Streamlit
Voice processing
OCR
Error handling
Production-style debugging
🧠 Most Important Learning

The biggest architectural lesson from this project was:

Routing and state management are just as important as the LLM itself.

A powerful LLM cannot fix an incorrectly routed request.

The final system therefore separates:

🧠 Decision
      ↓
🔀 Routing
      ↓
🔎 Retrieval / Tool
      ↓
📚 Context
      ↓
🤖 Generation

This separation makes the system easier to debug, extend and maintain.

📌 Project Summary

Agentic RAG Space is a modular multimodal AI assistant built using LangGraph, FastAPI, Streamlit, Google Gemini and Pinecone.

It intelligently routes requests across:

📚 Multi-Document RAG
🌐 Web RAG
🔎 Live Web Search
🖼️ OCR
🌤️ Weather
🤖 General AI
👋 Conversation
🎙️ Voice

The system supports cross-document semantic retrieval, persistent indexing of user-provided webpages, conversational Web RAG, voice interaction, OCR and source attribution.

The project demonstrates how an AI assistant can be designed as a collection of specialized components rather than a single LLM call.

👩‍💻 Author
Shambhavi Jha

🎓 B.Tech — Computer Science Engineering
📊 Specialization: Data Science

Areas of Interest
🤖 Artificial Intelligence
🧠 Machine Learning
✨ Generative AI
🔤 Large Language Models
📚 RAG
🔀 Agentic AI
📊 Data Science
⚙️ Backend Engineering
⭐ If you found this project interesting

Feel free to explore the repository, raise issues, suggest improvements, or build upon the architecture.

Built to understand what happens behind the scenes of modern AI applications. 🚀
