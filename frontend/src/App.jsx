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
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-full px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            EECS 182 Participation Post Explorer
          </h1>
          <p className="text-sm text-gray-600">
            Explore {graphData?.nodes?.length || 0} student participation posts through interactive graph visualization
          </p>
        </div>
      </header>

      {/* Controls */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="flex flex-wrap items-center gap-4 px-6 py-2">
          <CategoryToggle viewMode={viewMode} onChange={handleViewModeChange} />
          <SearchBar onSearch={handleSearch} />
        </div>
        
        {/* Search Results Info */}
        {searchQuery && searchResults && (
          <div className="px-6 pb-3">
            <div className="text-sm text-gray-600">
              Found {searchResults.count || 0} result(s) for "{searchQuery}"
              {searchResults.count > 0 && ' - highlighted in red on the graph'}
            </div>
          </div>
        )}
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
          <Sidebar post={selectedPost} onClose={handleCloseSidebar} />
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-2 px-6">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <div>
            EECS 182 - Berkeley • Phase 4 Implementation
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
