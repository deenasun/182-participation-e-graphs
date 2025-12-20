# EECS 182 Participation Post Graph - Frontend

This is the React-based frontend for the EECS 182 Participation Post Graph application. It provides an interactive graph visualization of student participation posts with semantic search, clustering, and detailed post information.

## Features

- **Interactive Force-Directed Graph**: Visualize 130+ student posts with force-directed layout
- **Multiple View Modes**: 
  - Topic View 📚 - Clustered by semantic topics
  - Tool View 🛠️ - Grouped by tool types
  - LLM View 🤖 - Organized by LLMs used
- **Real-Time Search**: Hybrid keyword and semantic search with result highlighting
- **Post Details Sidebar**: Click any node to view full post content, attachments, and links
- **Responsive Design**: Works on desktop and tablet devices
- **Beautiful UI**: Modern design with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **react-force-graph-2d** - Graph visualization
- **@tanstack/react-query** - Data fetching and caching
- **Axios** - HTTP client

## Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000 (see `backend/README.md`)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update the API URL in `.env` if needed:
```env
VITE_API_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Building for Production

Build the production bundle:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── CategoryToggle.jsx   # View mode switcher
│   │   ├── Graph.jsx            # Force-directed graph
│   │   ├── SearchBar.jsx        # Search input
│   │   └── Sidebar.jsx          # Post details panel
│   ├── hooks/               # Custom React hooks
│   │   └── useGraphData.ts      # Data fetching hooks
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/               # Utility functions
│   │   └── api.ts               # API client
│   ├── App.jsx              # Main app component
│   ├── App.css              # App styles
│   ├── index.css            # Global styles
│   └── main.jsx             # Entry point
├── public/                  # Static assets
├── .env                     # Environment variables
├── .env.example             # Environment template
├── package.json             # Dependencies
├── tailwind.config.js       # Tailwind configuration
├── postcss.config.js        # PostCSS configuration
└── vite.config.js           # Vite configuration
```

## Key Components

### Graph Component

The main visualization component using `react-force-graph-2d`:

- **Node Coloring**: Color-coded by cluster ID
- **Node Sizing**: Based on impressiveness score
- **Highlighting**: Red for search results, orange for hover
- **Interactions**: Click to view details, scroll to zoom, drag to pan
- **Labels**: Show on hover or highlight

### Sidebar Component

Displays detailed information about a selected post:

- Post title, author, and date
- Category tags (topics, tools, LLMs)
- Full content with scrollable view
- Attachments and external links
- Engagement metrics (reactions, replies)
- Impressiveness score

### CategoryToggle Component

Switch between three view modes:
- Topic View (blue) - Semantic topic clusters
- Tool View (green) - Tool type grouping
- LLM View (purple) - LLM usage organization

### SearchBar Component

Real-time search functionality:
- Types automatically search as you type
- Keyword matching in titles and content
- Semantic similarity search (for queries > 2 words)
- Clear button to reset search
- Result count display

## API Integration

The frontend connects to the backend API at `VITE_API_URL`:

**Endpoints Used:**
- `GET /api/graph-data/{viewMode}` - Fetch graph nodes and edges
- `POST /api/search` - Search posts
- `GET /api/posts/{id}` - Get post details
- `GET /api/stats` - Get database statistics
- `GET /health` - Health check

See `src/utils/api.ts` for full API client implementation.

## State Management

Uses React Query for server state:
- Automatic caching with 5-minute stale time
- Background refetching
- Error handling and retries
- Loading states

Local state managed with React hooks:
- Selected post
- Current view mode
- Search query
- Highlighted nodes

## Styling

Tailwind CSS with custom configuration:

**Color Palette:**
- Primary: Teal (#4ECDC4)
- Secondary: Blue (#45B7D1)
- Cluster colors: 8 distinct colors for different clusters

**Responsive Design:**
- Desktop-first approach
- Sidebar at 400px width
- Graph adjusts to window size
- Mobile support (landscape recommended)

## Performance Optimizations

1. **React Query Caching**: Reduces redundant API calls
2. **Canvas Rendering**: Graph uses canvas for smooth 60fps
3. **Memoization**: useCallback/useMemo for expensive computations
4. **Lazy Loading**: Components load on demand
5. **Debounced Search**: Prevents excessive API calls while typing

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `VITE_API_URL=https://your-api.onrender.com`
4. Deploy

### Netlify

1. Push code to GitHub
2. Import project in Netlify
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Environment variables: `VITE_API_URL=https://your-api.onrender.com`

### Manual Deployment

```bash
# Build production bundle
npm run build

# Upload dist/ folder to your hosting provider
```

## Troubleshooting

### "Failed to connect to backend"

- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `.env`
- Verify CORS is enabled in backend

### Graph not displaying

- Check browser console for errors
- Ensure graph data is being fetched (Network tab)
- Try refreshing the page

### Search not working

- Backend must be running
- Check that search endpoint returns results
- Clear browser cache and try again

### Styling issues

- Run `npm install` to ensure Tailwind is installed
- Check that `postcss.config.js` exists
- Verify Tailwind directives in `index.css`

## Browser Support

- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

When adding new features:
1. Create new components in `src/components/`
2. Add type definitions in `src/types/index.ts`
3. Use React Query hooks for data fetching
4. Follow Tailwind CSS for styling
5. Test on different view modes

## License

Part of EECS 182 course project at UC Berkeley.

## Related Documentation

- [Backend README](../backend/README.md)
- [Design Document](../DESIGN_DOC.md)
- [Phase 2 Implementation](../PHASE2_IMPLEMENTATION.md)
- [Phase 3 Implementation](../PHASE3_IMPLEMENTATION.md)
