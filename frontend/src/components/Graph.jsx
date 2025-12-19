import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const Graph = ({ data, viewMode, highlightedNodes, onNodeClick }) => {
  const graphRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState(null);

  // Nice palette for clusters
  const clusterColors = [
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
  ];

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

  // Filter data based on selected cluster
  const filteredData = useMemo(() => {
    if (selectedCluster === null) return data;
    
    const nodes = data.nodes.filter(node => node.cluster_id === selectedCluster);
    const nodeIds = new Set(nodes.map(n => n.id));
    // When filtering by cluster, we might want to still show edges? 
    // Usually edges within the cluster are most relevant.
    const edges = data.edges.filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target));
    
    return { ...data, nodes, edges };
  }, [data, selectedCluster]);

  // Reset filter when view mode changes
  useEffect(() => {
    setSelectedCluster(null);
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

  // Get color for node based on cluster and highlight state
  const getNodeColor = useCallback((node) => {
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      return '#FF6B6B'; // Red for highlighted/search results
    }
    if (hoveredNode && node.id === hoveredNode.id) {
      return '#FFA500'; // Orange for hover
    }
    
    const clusterId = node.cluster_id !== undefined ? node.cluster_id : 0;
    if (clusterId === -1) return '#DFE6E9'; // Light gray for noise
    
    return clusterColors[Math.abs(clusterId) % clusterColors.length];
  }, [highlightedNodes, hoveredNode, clusterColors]);

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

  const clusters = useMemo(() => {
    if (!data || !data.cluster_names) return [];
    return Object.entries(data.cluster_names).map(([id, name]) => ({
      id: parseInt(id),
      name
    })).sort((a, b) => a.name.localeCompare(b.name));
  }, [data]);

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
          <h4 className="font-bold text-gray-800">Clusters ({viewMode})</h4>
          {selectedCluster !== null && (
            <button 
              onClick={() => setSelectedCluster(null)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              Reset
            </button>
          )}
        </div>
        
        <div className="space-y-2">
          {clusters.map((cluster) => (
            <div 
              key={cluster.id} 
              className={`flex items-center gap-2 cursor-pointer p-1 rounded transition-colors ${selectedCluster === cluster.id ? 'bg-blue-50 ring-1 ring-blue-200' : 'hover:bg-gray-50'}`}
              onClick={() => setSelectedCluster(selectedCluster === cluster.id ? null : cluster.id)}
            >
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0" 
                style={{ backgroundColor: cluster.id === -1 ? '#DFE6E9' : clusterColors[Math.abs(cluster.id) % clusterColors.length] }}
              ></div>
              <span className={`truncate ${selectedCluster === cluster.id ? 'font-semibold text-blue-800' : 'text-gray-700'}`}>
                {cluster.name}
              </span>
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-3 border-t border-gray-100 text-[10px] text-gray-500 space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#FF6B6B]"></div>
            <span>Search Results / Highlights</span>
          </div>
          <p>• Click cluster to filter</p>
          <p>• Click node for details</p>
        </div>
      </div>
      
      {/* Stats overlay */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg text-sm border border-gray-200">
        <div className="font-bold text-gray-800 mb-1 capitalize">{viewMode} View</div>
        <div className="text-gray-600 font-medium">
          {filteredData.nodes.length} posts
          {selectedCluster !== null && <span className="text-blue-600 ml-1">(filtered)</span>}
        </div>
      </div>
    </div>
  );
};

export default Graph;
