import React from 'react';

const Tooltip = ({ children, text }) => {
  return (
    <div className="relative flex items-center group">
      {children}
      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block p-2 text-xs text-white whitespace-nowrap bg-gray-800 rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-100 z-50">
        {text}
      </span>
    </div>
  );
};

export default Tooltip;