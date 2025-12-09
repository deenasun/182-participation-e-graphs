# Project Structure

```
.
├── backend/                # Flask API backend
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── index.html        # Main HTML entry point
│   ├── package.json      # Node dependencies
│   ├── vite.config.js    # Vite configuration
│   └── src/
│       ├── main.jsx      # React entry point
│       ├── App.jsx       # Main App component
│       ├── App.css       # App styles
│       ├── index.css     # Global styles
│       └── components/   # React components
│           ├── Header.jsx
│           ├── ItemsList.jsx
│           └── ItemCard.jsx
└── README.md
```

## Setup Instructions

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask server:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000` and will automatically open in your browser.

## API Endpoints

- `GET /` - Welcome message
- `GET /api/items` - Get all items
- `GET /api/items/<id>` - Get a specific item
