import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Graph from './components/Graph';
import Sidebar from './components/Sidebar';
import SearchBar from './components/SearchBar';
import CategoryToggle from './components/CategoryToggle';
import { useGraphData, useSearchPosts } from './hooks/useGraphData';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [viewMode, setViewMode] = useState('topic');
  const [selectedPost, setSelectedPost] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedNodes, setHighlightedNodes] = useState(new Set());
  const [sidebarWidth, setSidebarWidth] = useState(384); // Default width (w-96 = 384px)

  // Fetch graph data for current view mode
  const { data: graphData, isLoading, error } = useGraphData(viewMode);
  
  // Search posts (only runs if query is not empty)
  const { data: searchResults } = useSearchPosts(searchQuery, viewMode);

  // Update highlighted nodes when search results change
  useEffect(() => {
    if (searchQuery && searchResults && searchResults.results) {
      const ids = new Set(searchResults.results.map(p => p.id));
      setHighlightedNodes(ids);
    } else {
      setHighlightedNodes(new Set());
    }
  }, [searchQuery, searchResults]);

  // Handle search
  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  // Handle view mode change
  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    setSelectedPost(null); // Clear selected post when changing views
  };

  // Handle node click
  const handleNodeClick = (node) => {
    setSelectedPost(node);
  };

  // Handle sidebar close
  const handleCloseSidebar = () => {
    setSelectedPost(null);
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
        <div className="text-red-500 text-xl mb-4">⚠️ Error loading data</div>
        <div className="text-gray-600 mb-4">
          {error.message || 'Failed to connect to the backend server'}
        </div>
        <div className="text-sm text-gray-500">
          Make sure the backend server is running on port 8000
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
        {/* <div className="text-4xl mb-4">🔄</div> */}
        <div className="text-gray-600 text-lg">Loading graph data...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 relative">
        <div className="max-w-full px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            EECS 182/282 Special Participation E Graph Explorer
          </h1>
          <p className="text-sm text-gray-600">
            Explore {graphData?.nodes?.length || 0} student participation posts through interactive graph visualization
          </p>
        </div>
        {/* Info Icon */}
        <div className="absolute top-4 right-6 group">
          <div className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors">
            <span className="text-gray-600 text-sm font-bold">i</span>
          </div>
          {/* Tooltip */}
          <div className="absolute right-0 top-8 w-80 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
            <p className="mb-2">Interactive graph using transformer-based sentence embeddings (all-MiniLM-L6-v2) with cosine similarity for semantic relationships. Employs UMAP for dimensionality reduction to 2D and HDBSCAN for density-based clustering with view-specific embedding fusion.</p>
            <p className="text-xs text-gray-300">Made by Deena Sun, Eric Wang, Celine Tan, and Tvisha Londe!</p>
            <div className="absolute -top-1 right-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="flex flex-wrap items-center gap-4 px-6 py-2">
          <CategoryToggle viewMode={viewMode} onChange={handleViewModeChange} />
          <SearchBar onSearch={handleSearch} />
        </div>
        
        {/* Search Results Info - always reserve space to prevent layout shift */}
        <div className="px-6 pb-3 min-h-[2rem]">
          {searchQuery && searchResults && (
            <div className="text-sm text-gray-600">
              Found {searchResults.count || 0} result(s) for "{searchQuery}"
              {searchResults.count > 0 && ' - highlighted in red on the graph'}
            </div>
          )}
        </div>
      </div>

      {/* Graph Container */}
      <div className="flex-1 relative overflow-hidden">
        {graphData && (
          <Graph
            data={graphData}
            viewMode={viewMode}
            highlightedNodes={highlightedNodes}
            onNodeClick={handleNodeClick}
          />
        )}
        
        {/* Sidebar */}
        {selectedPost && (
          <Sidebar 
            post={selectedPost} 
            onClose={handleCloseSidebar}
            width={sidebarWidth}
            onWidthChange={setSidebarWidth}
          />
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-2 px-6">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <div>
            EECS 182/282 Deep Learning - UC Berkeley
          </div>
          <div>
            {graphData?.nodes?.length || 0} Posts • {graphData?.edges?.length || 0} Connections
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
