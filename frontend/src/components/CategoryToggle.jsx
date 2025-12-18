import React from 'react';

const CategoryToggle = ({ viewMode, onChange }) => {
  const buttons = [
    { mode: 'topic', label: 'Topic View', color: 'blue' },
    { mode: 'tool', label: 'Tool View', color: 'green' },
    { mode: 'llm', label: 'LLM View', color: 'purple' }
  ];

  return (
    <div className="flex gap-2 p-4">
      {buttons.map(({ mode, label, color }) => (
        <button
          key={mode}
          onClick={() => onChange(mode)}
          className={`px-6 py-3 rounded-lg font-medium transition-all shadow-sm ${
            viewMode === mode
              ? color === 'blue' 
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : color === 'green'
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-purple-500 text-white hover:bg-purple-600'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
};

export default CategoryToggle;
