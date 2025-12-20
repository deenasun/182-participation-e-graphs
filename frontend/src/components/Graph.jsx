import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const Graph = ({ data, viewMode, highlightedNodes, onNodeClick }) => {
  const graphRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  // Nice palette for categories
  const categoryColors = [
    '#4ECDC4', // Teal
    '#45B7D1', // Blue
    '#96CEB4', // Green
    '#FFEAA7', // Yellow
    '#A29BFE', // Purple
    '#FD79A8', // Pink
    '#FDCB6E', // Orange
    '#6C5CE7', // Deep Purple
    '#FAB1A0', // Peach
    '#00B894', // Mint
    '#0984E3', // Bright Blue
    '#D63031', // Red
    '#E17055', // Coral
    '#74B9FF', // Sky Blue
    '#55EFC4', // Turquoise
    '#FDCB6E', // Gold
    '#A29BFE', // Lavender
    '#FD79A8', // Rose
  ];

  // Create a mapping from category name to color
  const categoryColorMap = useMemo(() => {
    if (!data || !data.nodes) return new Map();
    
    // Get all unique categories for current view mode
    const categories = new Set();
    data.nodes.forEach(node => {
      if (viewMode === 'topic' && node.topics) {
        node.topics.forEach(topic => categories.add(topic));
      } else if (viewMode === 'tool' && node.tools) {
        node.tools.forEach(tool => categories.add(tool));
      } else if (viewMode === 'llm' && node.llms) {
        node.llms.forEach(llm => categories.add(llm));
      }
    });
    
    // Create color mapping
    const sortedCategories = Array.from(categories).sort();
    const colorMap = new Map();
    sortedCategories.forEach((category, index) => {
      colorMap.set(category, categoryColors[index % categoryColors.length]);
    });
    
    return colorMap;
  }, [data, viewMode, categoryColors]);

  // Update dimensions on window resize
  useEffect(() => {
    const updateDimensions = () => {
      const sidebar = 400; // Account for sidebar when open
      const header = 150; // Account for header/controls
      setDimensions({
        width: window.innerWidth - sidebar,
        height: window.innerHeight - header
      });
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Determine which nodes match the selected category (but keep all nodes visible)
  const matchingNodeIds = useMemo(() => {
    if (selectedCategory === null) return new Set();
    
    const matchingIds = new Set();
    data.nodes.forEach(node => {
      let matches = false;
      if (viewMode === 'topic') {
        matches = node.topics && node.topics.includes(selectedCategory);
      } else if (viewMode === 'tool') {
        matches = node.tools && node.tools.includes(selectedCategory);
      } else { // llm
        matches = node.llms && node.llms.includes(selectedCategory);
      }
      
      if (matches) {
        matchingIds.add(node.id);
      }
    });
    
    return matchingIds;
  }, [data, selectedCategory, viewMode]);

  // Reset filter when view mode changes
  useEffect(() => {
    setSelectedCategory(null);
  }, [viewMode]);

  // Fit graph to view on data change
  useEffect(() => {
    if (graphRef.current && data && data.nodes.length > 0) {
      setTimeout(() => {
        graphRef.current.zoomToFit(400, 50);
      }, 100);
    }
  }, [data, viewMode]);

  // Get color for node based on its primary category and highlight state
  const getNodeColor = useCallback((node) => {
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      return '#FF6B6B'; // Red for highlighted/search results
    }
    if (hoveredNode && node.id === hoveredNode.id) {
      return '#FFA500'; // Orange for hover
    }
    
    // Check if node matches selected category
    const isMatching = selectedCategory === null || matchingNodeIds.has(node.id);
    
    // Get the primary category for this node based on view mode
    let primaryCategory = null;
    if (viewMode === 'topic' && node.topics && node.topics.length > 0) {
      primaryCategory = node.topics[0];
    } else if (viewMode === 'tool' && node.tools && node.tools.length > 0) {
      primaryCategory = node.tools[0];
    } else if (viewMode === 'llm' && node.llms && node.llms.length > 0) {
      primaryCategory = node.llms[0];
    }
    
    // If a category is selected and this node doesn't match, gray it out
    if (!isMatching) {
      return '#D3D3D3'; // Light gray for non-matching nodes
    }
    
    // Return color for the category, or default gray if no category
    if (primaryCategory && categoryColorMap.has(primaryCategory)) {
      return categoryColorMap.get(primaryCategory);
    }
    
    return '#DFE6E9'; // Light gray for uncategorized
  }, [highlightedNodes, hoveredNode, viewMode, categoryColorMap, selectedCategory, matchingNodeIds]);

  // Get node size based on highlight state and impressiveness
  const getNodeSize = useCallback((node) => {
    let baseSize = 4;
    
    // Size based on impressiveness score
    if (node.impressiveness_score) {
      baseSize = 3 + (node.impressiveness_score / 5); // Scale: 3-8
    }
    
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      return baseSize * 2; // Larger for highlighted
    }
    if (hoveredNode && node.id === hoveredNode.id) {
      return baseSize * 1.5; // Slightly larger for hover
    }
    
    // Make non-matching nodes slightly smaller when a category is selected
    const isMatching = selectedCategory === null || matchingNodeIds.has(node.id);
    if (!isMatching) {
      return baseSize * 0.7; // Smaller for non-matching nodes
    }
    
    return baseSize;
  }, [highlightedNodes, hoveredNode, selectedCategory, matchingNodeIds]);

  // Custom node canvas rendering for better performance
  const paintNode = useCallback((node, ctx, globalScale) => {
    const label = node.title;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    
    // Draw node circle
    const size = getNodeSize(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = getNodeColor(node);
    ctx.fill();
    
    // Draw border for highlighted nodes
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
    }
    
    // Draw label on hover or highlight
    if ((hoveredNode && node.id === hoveredNode.id) || 
        (highlightedNodes && highlightedNodes.has(node.id))) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#333';
      
      // Add background for readability
      const textWidth = ctx.measureText(label).width;
      const padding = 4;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(
        node.x - textWidth / 2 - padding,
        node.y + size + 2,
        textWidth + padding * 2,
        fontSize + padding
      );
      
      // Draw text
      ctx.fillStyle = '#333';
      ctx.fillText(label, node.x, node.y + size + fontSize / 2 + 4);
    }
  }, [getNodeColor, getNodeSize, highlightedNodes, hoveredNode]);

  // Handle node click
  const handleNodeClick = useCallback((node) => {
    onNodeClick(node);
  }, [onNodeClick]);

  // Handle node hover
  const handleNodeHover = useCallback((node) => {
    setHoveredNode(node);
  }, []);

  // Prepare graph data with proper source/target IDs
  const graphData = useMemo(() => {
    if (!data || !data.nodes || !data.edges) {
      return { nodes: [], links: [] };
    }

    // Map node IDs for fast lookup
    const nodeMap = new Map(data.nodes.map(node => [node.id, node]));

    // Filter edges to only include those where both nodes exist
    const validLinks = data.edges
      .filter(edge => nodeMap.has(edge.source) && nodeMap.has(edge.target))
      .map(edge => ({
        source: edge.source,
        target: edge.target,
        value: edge.similarity || 0.5
      }));

    return {
      nodes: data.nodes,
      links: validLinks
    };
  }, [data]);

  // Extract unique categories from nodes based on view mode
  const categories = useMemo(() => {
    if (!data || !data.nodes) return [];
    
    const categorySet = new Set();
    data.nodes.forEach(node => {
      if (viewMode === 'topic' && node.topics) {
        node.topics.forEach(topic => categorySet.add(topic));
      } else if (viewMode === 'tool' && node.tools) {
        node.tools.forEach(tool => categorySet.add(tool));
      } else if (viewMode === 'llm' && node.llms) {
        node.llms.forEach(llm => categorySet.add(llm));
      }
    });
    
    // Convert to array and sort
    return Array.from(categorySet).sort().map(category => ({
      name: category,
      color: categoryColorMap.get(category) || '#DFE6E9'
    }));
  }, [data, viewMode, categoryColorMap]);

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500 text-lg">No graph data available</div>
      </div>
    );
  }

  return (
    <div className="relative bg-gray-50">
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        nodeLabel="title"
        nodeCanvasObject={paintNode}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          const size = getNodeSize(node);
          ctx.beginPath();
          ctx.arc(node.x, node.y, size * 1.5, 0, 2 * Math.PI);
          ctx.fill();
        }}
        linkColor={(link) => {
          // Gray out edges that don't connect matching nodes when a category is selected
          if (selectedCategory !== null) {
            // Handle both node objects and string IDs
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            const sourceMatches = matchingNodeIds.has(sourceId);
            const targetMatches = matchingNodeIds.has(targetId);
            if (sourceMatches && targetMatches) {
              return '#99999966'; // Slightly more visible for edges between matching nodes
            }
            return '#99999911'; // Very faint for edges involving non-matching nodes
          }
          return '#99999933'; // Default when no filter
        }}
        linkWidth={(link) => {
          // Make edges between matching nodes slightly thicker when a category is selected
          if (selectedCategory !== null) {
            // Handle both node objects and string IDs
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            const sourceMatches = matchingNodeIds.has(sourceId);
            const targetMatches = matchingNodeIds.has(targetId);
            if (sourceMatches && targetMatches) {
              return 0.8; // Thicker for edges between matching nodes
            }
            return 0.3; // Thinner for edges involving non-matching nodes
          }
          return 0.5; // Default when no filter
        }}
        linkDirectionalParticles={0}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        cooldownTime={500}
        d3VelocityDecay={0.9}
        d3AlphaDecay={0.2}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        enableNodeDrag={true}
        warmupTicks={100}
        cooldownTicks={0}
      />
      
      {/* Legend & Filter */}
      <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg text-sm max-h-[70vh] overflow-y-auto w-64 border border-gray-200">
        <div className="flex justify-between items-center mb-3">
          <h4 className="font-bold text-gray-800 capitalize">Categories ({viewMode})</h4>
          {selectedCategory !== null && (
            <button 
              onClick={() => setSelectedCategory(null)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              Reset
            </button>
          )}
        </div>
        
        <div className="space-y-2">
          {categories.map((category) => (
            <div 
              key={category.name} 
              className={`flex items-center gap-2 cursor-pointer p-1 rounded transition-colors ${selectedCategory === category.name ? 'bg-blue-50 ring-1 ring-blue-200' : 'hover:bg-gray-50'}`}
              onClick={() => setSelectedCategory(selectedCategory === category.name ? null : category.name)}
            >
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0" 
                style={{ backgroundColor: category.color }}
              ></div>
              <span className={`truncate ${selectedCategory === category.name ? 'font-semibold text-blue-800' : 'text-gray-700'}`}>
                {category.name}
              </span>
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-3 border-t border-gray-100 text-[10px] text-gray-500 space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#FF6B6B]"></div>
            <span>Search Results / Highlights</span>
          </div>
          <p>• Click category to highlight</p>
          <p>• Click node for details</p>
        </div>
      </div>
      
      {/* Stats overlay */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg text-sm border border-gray-200">
        <div className="font-bold text-gray-800 mb-1 capitalize">{viewMode} View</div>
        <div className="text-gray-600 font-medium">
          {data.nodes.length} posts
          {selectedCategory !== null && (
            <span className="text-blue-600 ml-1">
              ({matchingNodeIds.size} matching)
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default Graph;
