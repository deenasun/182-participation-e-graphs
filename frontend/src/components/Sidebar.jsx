import React, { useState, useRef, useEffect } from 'react';

const Sidebar = ({ post, onClose, width = 384, onWidthChange }) => {
  const [sidebarWidth, setSidebarWidth] = useState(width);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef(null);

  // Update local width when prop changes
  useEffect(() => {
    setSidebarWidth(width);
  }, [width]);

  // Handle resize
  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e) => {
      const newWidth = window.innerWidth - e.clientX;
      // Constrain width between 300px and 80% of window width
      const minWidth = 300;
      const maxWidth = window.innerWidth * 0.8;
      const constrainedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
      setSidebarWidth(constrainedWidth);
      if (onWidthChange) {
        onWidthChange(constrainedWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, onWidthChange]);

  const handleResizeStart = (e) => {
    e.preventDefault();
    e.stopPropagation(); // Prevent overlay click from closing sidebar
    setIsResizing(true);
  };

  if (!post) return null;

  // Helper to render formatted content (markdown-like formatting)
  const renderFormattedContent = (content) => {
    if (!content) return "";
    
    // Split by newlines to preserve paragraph structure
    const lines = content.split('\n');
    
    return lines.map((line, lineIdx) => {
      // Skip empty lines (but preserve them for spacing)
      if (line.trim() === '') {
        return <br key={lineIdx} />;
      }
      
      // Check if line starts with bullet point
      const isBullet = line.trim().startsWith('•');
      const lineContent = isBullet ? line.trim().substring(1).trim() : line;
      
      // Process markdown-style formatting
      const parts = [];
      let remaining = lineContent;
      let key = 0;
      
      // Process links [text](url)
      const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
      let lastIndex = 0;
      let match;
      
      while ((match = linkRegex.exec(remaining)) !== null) {
        // Add text before the link
        if (match.index > lastIndex) {
          const beforeText = remaining.substring(lastIndex, match.index);
          parts.push(...formatText(beforeText, key));
          key += beforeText.length;
        }
        
        // Add the link
        parts.push(
          <a
            key={`link-${key}`}
            href={match[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 hover:underline"
          >
            {match[1]}
          </a>
        );
        key += match[0].length;
        lastIndex = match.index + match[0].length;
      }
      
      // Add remaining text after last link
      if (lastIndex < remaining.length) {
        const afterText = remaining.substring(lastIndex);
        parts.push(...formatText(afterText, key));
      }
      
      // If no links found, format the whole line
      if (parts.length === 0) {
        parts.push(...formatText(lineContent, 0));
      }
      
      return (
        <p key={lineIdx} className={`mb-2 last:mb-0 ${isBullet ? 'ml-4' : ''}`}>
          {isBullet && <span className="mr-2">•</span>}
          {parts}
        </p>
      );
    });
  };
  
  // Helper to format text with bold, italic, underline
  const formatText = (text, startKey) => {
    const parts = [];
    let remaining = text;
    let key = startKey;
    
    // Process bold **text** first (to avoid conflicts with italic)
    const boldRegex = /\*\*([^*]+?)\*\*/g;
    // Process underline __text__
    const underlineRegex = /__([^_]+?)__/g;
    // Process italic *text* (but not **text** - we'll handle this by processing bold first)
    const italicRegex = /(?<!\*)\*([^*]+?)\*(?!\*)/g;
    
    // Collect all matches with their positions
    const matches = [];
    
    let match;
    while ((match = boldRegex.exec(remaining)) !== null) {
      matches.push({ type: 'bold', start: match.index, end: match.index + match[0].length, content: match[1] });
    }
    while ((match = italicRegex.exec(remaining)) !== null) {
      matches.push({ type: 'italic', start: match.index, end: match.index + match[0].length, content: match[1] });
    }
    while ((match = underlineRegex.exec(remaining)) !== null) {
      matches.push({ type: 'underline', start: match.index, end: match.index + match[0].length, content: match[1] });
    }
    
    // Sort matches by position
    matches.sort((a, b) => a.start - b.start);
    
    // Remove overlapping matches (keep first)
    const nonOverlapping = [];
    for (const m of matches) {
      if (nonOverlapping.length === 0 || m.start >= nonOverlapping[nonOverlapping.length - 1].end) {
        nonOverlapping.push(m);
      }
    }
    
    // Build parts
    let lastIndex = 0;
    for (const m of nonOverlapping) {
      // Add text before match
      if (m.start > lastIndex) {
        parts.push(remaining.substring(lastIndex, m.start));
      }
      
      // Add formatted content
      const content = m.content;
      if (m.type === 'bold') {
        parts.push(<strong key={`${key}-${m.start}`}>{content}</strong>);
      } else if (m.type === 'italic') {
        parts.push(<em key={`${key}-${m.start}`}>{content}</em>);
      } else if (m.type === 'underline') {
        parts.push(<u key={`${key}-${m.start}`}>{content}</u>);
      }
      
      lastIndex = m.end;
    }
    
    // Add remaining text
    if (lastIndex < remaining.length) {
      parts.push(remaining.substring(lastIndex));
    }
    
    // If no matches, return the text as-is
    if (parts.length === 0) {
      return [text];
    }
    
    return parts;
  };

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-30 z-40"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div 
        ref={sidebarRef}
        className="fixed right-0 top-0 h-full bg-white shadow-2xl z-50 animate-slide-in flex"
        style={{ width: `${sidebarWidth}px` }}
      >
        {/* Resize Handle */}
        <div
          className="absolute left-0 top-0 bottom-0 w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize transition-colors z-10"
          onMouseDown={handleResizeStart}
          style={{ cursor: 'col-resize' }}
        >
          {/* Wider invisible hit area for easier grabbing */}
          <div 
            className="absolute left-0 top-0 bottom-0 w-4 -translate-x-1.5 cursor-col-resize"
            onMouseDown={handleResizeStart}
          />
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="float-right text-2xl text-gray-500 hover:text-gray-700 transition-colors"
          >
            ✕
          </button>
          
          {/* Post Title */}
          <h2 className="text-2xl font-bold mb-2 pr-8 text-gray-800">{post.title}</h2>
          
          {/* Post Number */}
          {(post.ed_post_number || post.ed_post_id) && (
            <div className="text-sm text-gray-500 mb-2">
              <span className="font-medium">
                Post #{post.ed_post_number || post.ed_post_id}
                {post.ed_post_number && post.ed_post_id && post.ed_post_number !== post.ed_post_id && (
                  <span className="text-gray-400 ml-2">(ID: {post.ed_post_id})</span>
                )}
              </span>
            </div>
          )}
          
          {/* Author and Date */}
          <div className="text-sm text-gray-600 mb-4">
            <p className="font-medium">By {post.author}</p>
            {post.date && (
              <p className="text-gray-500">
                {new Date(post.date).toLocaleDateString()}
              </p>
            )}
          </div>
          
          {/* Impressiveness Score */}
          {post.impressiveness_score !== undefined && (
            <div className="mb-4">
              <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                ⭐ Score: {post.impressiveness_score.toFixed(1)}
              </span>
            </div>
          )}
          
          {/* Categories */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2 text-gray-700">Categories</h3>
            <div className="flex flex-wrap gap-2">
              {post.topics && post.topics.length > 0 && post.topics.map((t, idx) => (
                <span key={`topic-${idx}`} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  📚 {t}
                </span>
              ))}
              {post.tools && post.tools.length > 0 && post.tools.map((t, idx) => (
                <span key={`tool-${idx}`} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                  🛠️ {t}
                </span>
              ))}
              {post.llms && post.llms.length > 0 && post.llms.map((l, idx) => (
                <span key={`llm-${idx}`} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                  🤖 {l}
                </span>
              ))}
            </div>
          </div>
          
          {/* Content */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2 text-gray-700">Content</h3>
            <div className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              {renderFormattedContent(post.content)}
            </div>
          </div>
          
          {/* Attachments */}
          {post.attachment_urls && post.attachment_urls.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2 text-gray-700">Attachments</h3>
              <div className="space-y-2">
                {post.attachment_urls.map((url, idx) => (
                  <a
                    key={idx}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-blue-600 hover:text-blue-800 hover:underline text-sm truncate"
                  >
                    📎 {url.split('/').pop() || `Attachment ${idx + 1}`}
                  </a>
                ))}
              </div>
            </div>
          )}
          
          {/* Links */}
          {(post.github_url || post.website_url || post.linkedin_url) && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2 text-gray-700">Links</h3>
              <div className="flex flex-col gap-2">
                {post.github_url && (
                  <a 
                    href={post.github_url.startsWith('http') ? post.github_url : `https://${post.github_url}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline text-sm flex items-center gap-2"
                  >
                    <span>🐙</span> GitHub
                  </a>
                )}
                {post.website_url && (
                  <a 
                    href={post.website_url.startsWith('http') ? post.website_url : `https://${post.website_url}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline text-sm flex items-center gap-2"
                  >
                    <span>🌐</span> Website
                  </a>
                )}
                {post.linkedin_url && (
                  <a 
                    href={post.linkedin_url.startsWith('http') ? post.linkedin_url : `https://${post.linkedin_url}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline text-sm flex items-center gap-2"
                  >
                    <span>💼</span> LinkedIn
                  </a>
                )}
              </div>
            </div>
          )}
          
          {/* Engagement Metrics */}
          {(post.num_reactions || post.num_replies) && (
            <div className="mb-4 pt-4 border-t border-gray-200">
              <div className="flex gap-4 text-sm text-gray-600">
                {post.num_reactions !== undefined && (
                  <span>👍 {post.num_reactions} reactions</span>
                )}
                {post.num_replies !== undefined && (
                  <span>💬 {post.num_replies} replies</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
