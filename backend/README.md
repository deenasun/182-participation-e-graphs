# EECS 182 Post Graph - Backend API

FastAPI backend for visualizing and exploring EECS 182 participation posts.

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment (already created)
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install/update dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key

### 3. Load Data (First Time Only)

```bash
# Load processed posts into Supabase
python db_utils.py load

# Verify data was loaded
python db_utils.py stats
```

### 4. Start the Server

```bash
# Easy way - use startup script
./start_server.sh  # On macOS/Linux
# or
start_server.bat  # On Windows

# Or run directly
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── database.py          # Supabase client
├── models.py            # Pydantic models
├── db_utils.py          # Database utilities
├── test_api.py          # API test suite
├── config.py            # Configuration
├── start_server.sh      # Startup script (Unix)
├── start_server.bat     # Startup script (Windows)
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── ingestion/          # Data ingestion pipeline
    ├── __init__.py
    ├── embedder.py
    ├── categorizer.py
    ├── graph_builder.py
    └── pdf_processor.py
```

## API Endpoints

### Health & Info

- `GET /` - Root health check
- `GET /health` - Detailed health check
- `GET /api/stats` - Database statistics

### Posts

- `GET /api/posts` - Get all posts
- `GET /api/posts/{post_id}` - Get specific post

### Graph Data

- `GET /api/graph-data/{view_mode}` - Get graph visualization data
  - View modes: `topic`, `tool`, `llm`

### Search

- `POST /api/search` - Search posts (JSON body)
- `GET /api/search?q=query` - Search posts (URL params)

### Data Management

- `POST /api/refresh` - Trigger data refresh from JSON

## Database Utilities

The `db_utils.py` script provides database management commands:

```bash
# Load data from processed_posts.json
python db_utils.py load

# Show database statistics
python db_utils.py stats

# Clear all data (with confirmation)
python db_utils.py clear
```

## Testing

### Run Test Suite

```bash
# Make sure server is running first
python main.py &

# Run tests
python test_api.py
```

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Get graph data
curl http://localhost:8000/api/graph-data/topic

# Search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "RNN", "view_mode": "topic"}'
```

### Interactive Testing

Open http://localhost:8000/docs in your browser for interactive API documentation.

## Development

### Adding New Endpoints

1. Add Pydantic schemas to `schemas.py`
2. Add database methods to `database.py`
3. Add endpoint to `main.py`
4. Update tests in `test_api.py`

### Code Style

- Use type hints for all functions
- Add docstrings for public methods
- Follow PEP 8 style guide
- Use Pydantic for validation

### Running with Auto-Reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment

### Environment Variables for Production

Update `.env` for production:
- Set `DEBUG=False`
- Use production Supabase credentials
- Set strong `SECRET_KEY`
- Configure appropriate `PORT`

### Render Deployment

See `PHASE3_IMPLEMENTATION.md` for detailed deployment instructions.

## Troubleshooting

### Database Connection Failed

```bash
# Test database connection
python -c "from database import SupabaseClient; db = SupabaseClient(); print(db.get_stats())"
```

If it fails, check:
- `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Database tables are created (see Phase 1 schema)
- pgvector extension is enabled

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Kill the process or use a different port
uvicorn main:app --port 8001
```

### Search Not Working

Ensure sentence-transformers model is downloaded:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Dependencies

Key dependencies:
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Supabase** - Database client
- **Sentence-Transformers** - Embeddings
- **Pydantic** - Data validation

See `requirements.txt` for full list.

## Documentation

- **Phase 3 Implementation:** See `../PHASE3_IMPLEMENTATION.md`
- **Design Doc:** See `../DESIGN_DOC.md`
- **Phase 2 Summary:** See `../PHASE2_IMPLEMENTATION.md`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the implementation documentation
3. Check API interactive docs at `/docs`

## License

Part of EECS 182 course project.
