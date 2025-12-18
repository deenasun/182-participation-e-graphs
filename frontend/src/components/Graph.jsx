import React, { useRef, useEffect, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const Graph = ({ data, viewMode, highlightedNodes, onNodeClick }) => {
  const graphRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  const [hoveredNode, setHoveredNode] = useState(null);

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

  // Fit graph to view on data change
  useEffect(() => {
    if (graphRef.current && data && data.nodes.length > 0) {
      // Add a small delay to ensure the graph is rendered
      setTimeout(() => {
        graphRef.current.zoomToFit(400, 50);
      }, 100);
    }
  }, [data, viewMode]);

  // Get color for node based on cluster and highlight state
  const getNodeColor = useCallback((node) => {
    if (highlightedNodes && highlightedNodes.has(node.id)) {
      return '#FF6B6B'; // Red for highlighted/search results
    }
    if (hoveredNode && node.id === hoveredNode.id) {
      return '#FFA500'; // Orange for hover
    }
    
    // Color by cluster with nice palette
    const colors = [
      '#4ECDC4', // Teal
      '#45B7D1', // Blue
      '#96CEB4', // Green
      '#FFEAA7', // Yellow
      '#DFE6E9', // Gray
      '#A29BFE', // Purple
      '#FD79A8', // Pink
      '#FDCB6E', // Orange
    ];
    
    const clusterId = node.cluster_id !== undefined ? node.cluster_id : 0;
    return colors[Math.abs(clusterId) % colors.length];
  }, [highlightedNodes, hoveredNode]);

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

  const graphData = prepareGraphData();

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
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg text-sm">
        <h4 className="font-semibold mb-2">Legend</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#FF6B6B]"></div>
            <span>Search Result</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#4ECDC4]"></div>
            <span>Cluster Color</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-600">
          <p>• Click node to view details</p>
          <p>• Scroll to zoom</p>
          <p>• Drag to pan</p>
        </div>
      </div>
      
      {/* Stats overlay */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg text-sm">
        <div className="font-semibold mb-1">{viewMode.toUpperCase()} View</div>
        <div className="text-gray-600">
          {data.nodes.length} posts • {data.edges.length} connections
        </div>
      </div>
    </div>
  );
};

export default Graph;
