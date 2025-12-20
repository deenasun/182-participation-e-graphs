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

  // Helper to strip XML/HTML tags from EdStem content
  const cleanContent = (content) => {
    if (!content) return "";
    // Replace tags with space, then clean up extra whitespace
    return content
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
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
        className="fixed right-0 top-0 h-full bg-white shadow-2xl overflow-y-auto z-50 animate-slide-in"
        style={{ width: `${sidebarWidth}px` }}
      >
        {/* Resize Handle */}
        <div
          className="absolute left-0 top-0 h-full w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize transition-colors z-10"
          onMouseDown={handleResizeStart}
          style={{ cursor: 'col-resize' }}
        >
          {/* Wider invisible hit area for easier grabbing */}
          <div 
            className="absolute left-0 top-0 h-full w-4 -translate-x-1.5 cursor-col-resize"
            onMouseDown={handleResizeStart}
          />
        </div>
        
        <div className="p-6">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="float-right text-2xl text-gray-500 hover:text-gray-700 transition-colors"
          >
            ✕
          </button>
          
          {/* Post Title */}
          <h2 className="text-2xl font-bold mb-2 pr-8 text-gray-800">{post.title}</h2>
          
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
            <div className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              {cleanContent(post.content)}
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
