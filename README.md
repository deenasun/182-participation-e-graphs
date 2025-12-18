# EECS 182 Special Participation E Graph

Interactive graph-based website for exploring EECS 182 student participation posts from EdStem. Features real-time search, semantic clustering, and beautiful visualizations.

## Project Overview

This project visualizes student participation posts from EECS 182's EdStem forum using an interactive force-directed graph. It enables students and course staff to explore AI-enhanced learning tools, discover similar posts, and gain visibility for their work.

### Key Features

- **Interactive 2D Force-Directed Graph**: Visualize posts with smooth animations and physics-based layout
- **Three View Modes**: 
  - 📚 Topic View - Semantic topic clusters using BERTopic
  - 🛠️ Tool View - Grouped by tool types (flashcard, quiz, diagram, etc.)
  - 🤖 LLM View - Organized by LLMs used (GPT, Claude, Gemini, etc.)
- **Real-Time Search**: Hybrid keyword + semantic search with result highlighting
- **Post Details**: Click any node to view full content, attachments, and links

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with pgvector
- **Sentence-Transformers** - Embedding generation (all-MiniLM-L6-v2)
- **BERTopic** - Topic modeling
- **UMAP + HDBSCAN** - Dimensionality reduction and clustering

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **react-force-graph-2d** - Graph visualization
- **@tanstack/react-query** - Data fetching

## Project Structure

```
.
├── backend/                  # FastAPI backend
│   ├── main.py              # FastAPI application with endpoints
│   ├── database.py          # Supabase client
│   ├── schemas.py           # Pydantic models
│   ├── db_utils.py          # Database utilities
│   ├── ingestion/           # Data processing pipeline
│   │   ├── embedder.py      # Embedding generation
│   │   ├── categorizer.py   # Topic/tool/LLM extraction
│   │   ├── graph_builder.py # Graph layout computation
│   │   └── pdf_processor.py # PDF text extraction
│   ├── run_ingestion.py     # Standalone ingestion script
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template
│   └── README.md           # Backend documentation
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── CategoryToggle.jsx
│   │   │   ├── Graph.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   └── useGraphData.ts
│   │   ├── types/          # TypeScript definitions
│   │   │   └── index.ts
│   │   ├── utils/          # Utilities
│   │   │   └── api.ts
│   │   ├── App.jsx         # Main application
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   ├── .env.example        # Environment template
│   └── README.md          # Frontend documentation
├── DESIGN_DOC.md          # Complete engineering design
├── PHASE2_IMPLEMENTATION.md
├── PHASE3_IMPLEMENTATION.md
├── PHASE4_IMPLEMENTATION.md
└── README.md              # This file
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account (for database)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Load data into database (one-time)
python db_utils.py load

# Start the API server
./start_server.sh
# Or: python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Default API URL is http://localhost:8000

# Start the development server
./start_dev.sh
# Or: npm run dev
```

The frontend will be available at `http://localhost:5173`


### API Endpoints

**Graph Data:**
- `GET /api/graph-data/{viewMode}` - Get nodes and edges for visualization
  - View modes: `topic`, `tool`, `llm`

**Posts:**
- `GET /api/posts` - Get all posts
- `GET /api/posts/{id}` - Get specific post

**Search:**
- `POST /api/search` - Search posts (JSON body)
- `GET /api/search?q=query` - Search posts (query params)

**Admin:**
- `GET /health` - Health check
- `GET /api/stats` - Database statistics
- `POST /api/refresh` - Trigger data refresh

## Features

### Interactive Graph Visualization

- **Force-directed layout** with D3.js physics
- **Color-coded clusters** (8 distinct colors)
- **Node sizing** based on impressiveness score
- **Search highlighting** in red
- **Hover labels** for post titles
- **Click to explore** post details

### Search & Discovery

- **Keyword search** in titles and content
- **Semantic search** using embeddings (for longer queries)
- **Real-time results** as you type
- **Result highlighting** on the graph
- **Result count** display

### Post Details

- Full post content
- Author and date
- Category tags (topics, tools, LLMs)
- Impressiveness score
- Attachments (PDFs)
- External links (GitHub, website, LinkedIn)
- Engagement metrics (reactions, replies)

### License and Contributions

Created by Deena Sun, Eric Wang, Celine Tan, and Tvisha Londe.

Educational project for EECS 182.
