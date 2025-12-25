# 🤖 Physical AI RAG Chatbot

An AI-powered interactive textbook for Physical AI & Humanoid Robotics with an integrated RAG (Retrieval-Augmented Generation) chatbot. Built for the GIAIC Hackathon 2024.

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)]([YOUR_VERCEL_URL](https://physical-ai-textbook-rag.vercel.app/))


## 🎯 Overview

This project combines a comprehensive Physical AI textbook with an intelligent chatbot that can answer questions about the content in real-time. Users can learn about robotics, humanoid systems, and physical AI concepts while getting instant answers from an AI assistant trained on the book's content.

## 🏗️ System Architecture

![Physical AI RAG Chatbot - System Architecture](./architecture-diagram.png)

### Architecture Components

**Frontend (Vercel)**
- **Docusaurus Static Site**: Full textbook with chapters on Physical AI concepts
- **RagChat Component**: Floating chat widget (💬) in the bottom-right corner
- **Features**: Input validation, answer display with sources, error handling, retry logic

**Backend (Railway.app)**
- **FastAPI Server**: REST API with `/ask` endpoint
- **RAG Agent**: Orchestrates the retrieval and generation pipeline
- **CORS Middleware**: Enables cross-origin requests from frontend

**AI Services**
- **Cohere API**: Generates query embeddings (embed-english-v3)
- **Qdrant Cloud**: Vector database for semantic search
- **OpenRouter API (LLM)**: Generates contextual answers with citations

## 🚀 Features

- ✅ **Interactive Textbook**: Comprehensive Physical AI & Humanoid Robotics content
- ✅ **AI-Powered Chat**: Ask questions and get instant answers
- ✅ **Source Citations**: Every answer includes references to source material
- ✅ **Semantic Search**: Find relevant content using vector embeddings
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Error Handling**: Robust retry logic and user-friendly error messages

## 🎬 How It Works

1. **User asks a question** in the chat widget (e.g., "What is Physical AI?")
2. **Frontend sends request** to FastAPI backend via POST /ask
3. **Backend validates** the query
4. **Cohere generates** a vector embedding for the query
5. **Qdrant searches** for the top-5 most similar content chunks
6. **Backend formats** the retrieved context
7. **OpenRouter LLM generates** a comprehensive answer using the context
8. **Response includes**: Answer text, source URLs, and matched chunks
9. **Frontend displays** the answer with clickable sources

## 📚 Tech Stack

### Frontend
- **Framework**: Docusaurus 2.4.3
- **Language**: React + JavaScript
- **Styling**: Custom CSS
- **HTTP Client**: Axios
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.14
- **Server**: Uvicorn
- **Validation**: Pydantic
- **Deployment**: Railway

### AI Services
- **Embeddings**: Cohere (embed-english-v3, 1024 dimensions)
- **Vector DB**: Qdrant Cloud (cosine similarity search)
- **LLM**: OpenRouter API (text generation with citations)

### DevOps
- **Version Control**: GitHub
- **CI/CD**: Automatic deployment via Vercel + Railway
- **Environment Management**: dotenv

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.14+ (for backend)
- API Keys: Cohere, Qdrant, OpenRouter

### Local Development

#### 1. Clone the Repository
```bash
git clone https://github.com/AiWithAadil/physical-ai-textbook-rag.git
cd physical-ai-textbook-rag
```

#### 2. Setup Backend
```bash
cd HackathonGIAIC/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_key
COHERE_API_KEY=your_cohere_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
EOF

# Run server
uvicorn agent:app --reload
```

Backend runs at: `http://localhost:8000`

#### 3. Setup Frontend
```bash
cd HackathonGIAIC/physical-ai

# Install dependencies
npm install

# Update backend URL in src/components/RagChat/RagChat.jsx
# Change: backendUrl = 'http://localhost:8000'

# Run development server
npm start
```

Frontend runs at: `http://localhost:3000`

## 📁 Project Structure

```
physical-ai-textbook-rag/
├── HackathonGIAIC/
│   ├── backend/                  # FastAPI backend
│   │   ├── agent.py              # Main RAG agent
│   │   ├── main.py               # Embedding pipeline
│   │   ├── src/
│   │   │   ├── services/         # Cohere, Qdrant services
│   │   │   ├── models/           # Pydantic models
│   │   │   └── utils/            # Helper functions
│   │   └── requirements.txt
│   │
│   └── physical-ai/              # Docusaurus frontend
│       ├── docs/                 # Textbook content
│       ├── src/
│       │   ├── components/
│       │   │   └── RagChat/      # Chat widget
│       │   └── theme/            # Custom layout
│       ├── docusaurus.config.js
│       └── package.json
│
├── architecture-diagram.png      # System architecture
└── README.md
```

## 🔑 Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
PORT=8000
```

## 🚀 Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Import repository in Vercel
3. Set root directory: `HackathonGIAIC/physical-ai`
4. Deploy automatically

### Backend (Railway)
1. Create new project in Railway
2. Connect GitHub repository
3. Set root directory: `HackathonGIAIC/backend`
4. Add environment variables
5. Set start command: `uvicorn agent:app --host 0.0.0.0 --port $PORT`
6. Deploy


## 📊 Data Flow

```
User Query → Frontend Validation → POST /ask
    ↓
Backend RAG Agent
    ↓
Step 1: Cohere Embedding (Query → Vector)
    ↓
Step 2: Qdrant Search (Top-5 Similar Chunks)
    ↓
Step 3: OpenRouter LLM (Context + Query → Answer)
    ↓
Response: {answer, sources, matched_chunks, metadata}
    ↓
Frontend Display (Answer + Citations)
```

## 🎓 Book Content

The textbook covers:
- **Part 1: Foundations** - What is Physical AI, Perception, Decision-Making, Actuation
- **Part 2: Practical Systems** - Computer Vision, Mobile Robotics, Manipulation, Sensor Networks
- **Part 3: Advanced Topics** - Learning Systems, Safety & Robustness, Real-World Integration, Case Studies
- **Appendices** - Tools & Setup, Glossary, References

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Aadil** - [GitHub](https://github.com/AiWithAadil)

## 🙏 Acknowledgments

- Built for the **GIAIC Hackathon 2024**
- Inspired by **Panaversity's** Physical AI curriculum
- Special thanks to the open-source community

---

⭐ **Star this repo** if you find it helpful!
