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

  // Filter data based on selected category
  // When a category is selected, show all nodes that have that category in their topics/tools/llms
  const filteredData = useMemo(() => {
    if (selectedCategory === null) return data;
    
    // Filter nodes based on whether they contain the selected category in their relevant array
    let nodes;
    if (viewMode === 'topic') {
      nodes = data.nodes.filter(node => 
        node.topics && node.topics.includes(selectedCategory)
      );
    } else if (viewMode === 'tool') {
      nodes = data.nodes.filter(node => 
        node.tools && node.tools.includes(selectedCategory)
      );
    } else { // llm
      nodes = data.nodes.filter(node => 
        node.llms && node.llms.includes(selectedCategory)
      );
    }
    
    const nodeIds = new Set(nodes.map(n => n.id));
    // When filtering by category, show edges between filtered nodes
    const edges = data.edges.filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target));
    
    return { ...data, nodes, edges };
  }, [data, selectedCategory, viewMode]);

  // Reset filter when view mode changes
  useEffect(() => {
    setSelectedCategory(null);
  }, [viewMode]);

  // Fit graph to view on data change
  useEffect(() => {
    if (graphRef.current && filteredData && filteredData.nodes.length > 0) {
      // Add a small delay to ensure the graph is rendered
      setTimeout(() => {
        graphRef.current.zoomToFit(400, 50);
      }, 100);
    }
  }, [filteredData, viewMode]);

  // Get color for node based on its primary category and highlight state
  const getNodeColor = useCallback((node) => {
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      return '#FF6B6B'; // Red for highlighted/search results
    }
    if (hoveredNode && node.id === hoveredNode.id) {
      return '#FFA500'; // Orange for hover
    }
    
    // Get the primary category for this node based on view mode
    let primaryCategory = null;
    if (viewMode === 'topic' && node.topics && node.topics.length > 0) {
      primaryCategory = node.topics[0];
    } else if (viewMode === 'tool' && node.tools && node.tools.length > 0) {
      primaryCategory = node.tools[0];
    } else if (viewMode === 'llm' && node.llms && node.llms.length > 0) {
      primaryCategory = node.llms[0];
    }
    
    // Return color for the category, or default gray if no category
    if (primaryCategory && categoryColorMap.has(primaryCategory)) {
      return categoryColorMap.get(primaryCategory);
    }
    
    return '#DFE6E9'; // Light gray for uncategorized
  }, [highlightedNodes, hoveredNode, viewMode, categoryColorMap]);

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
    
    return baseSize;
  }, [highlightedNodes, hoveredNode]);

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
  const prepareGraphData = useCallback(() => {
    if (!filteredData || !filteredData.nodes || !filteredData.edges) {
      return { nodes: [], links: [] };
    }

    // Map node IDs for fast lookup
    const nodeMap = new Map(filteredData.nodes.map(node => [node.id, node]));

    // Filter edges to only include those where both nodes exist
    const validLinks = filteredData.edges
      .filter(edge => nodeMap.has(edge.source) && nodeMap.has(edge.target))
      .map(edge => ({
        source: edge.source,
        target: edge.target,
        value: edge.similarity || 0.5
      }));

    return {
      nodes: filteredData.nodes,
      links: validLinks
    };
  }, [filteredData]);

  const graphData = prepareGraphData();

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
        linkColor={() => '#99999933'}
        linkWidth={0.5}
        linkDirectionalParticles={0}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        cooldownTime={3000}
        d3VelocityDecay={0.3}
        d3AlphaDecay={0.02}
        enableZoomInteraction={true}
        enablePanInteraction={true}
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
          <p>• Click category to filter</p>
          <p>• Click node for details</p>
        </div>
      </div>
      
      {/* Stats overlay */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg text-sm border border-gray-200">
        <div className="font-bold text-gray-800 mb-1 capitalize">{viewMode} View</div>
        <div className="text-gray-600 font-medium">
          {filteredData.nodes.length} posts
          {selectedCategory !== null && <span className="text-blue-600 ml-1">(filtered)</span>}
        </div>
      </div>
    </div>
  );
};

export default Graph;
