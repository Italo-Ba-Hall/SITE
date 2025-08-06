import React, { useState, useEffect, useCallback, useMemo } from 'react';

interface Suggestion {
  id: string;
  title: string;
  description: string;
  category: string;
}

interface SuggestionsDropdownProps {
  isVisible: boolean;
  suggestions: Suggestion[];
  isLoading: boolean;
  onSuggestionClick: (suggestion: Suggestion) => void;
  onClose: () => void;
}

const SuggestionsDropdown: React.FC<SuggestionsDropdownProps> = ({
  isVisible,
  suggestions,
  isLoading,
  onSuggestionClick,
  onClose
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Memoize suggestions to prevent unnecessary re-renders
  const memoizedSuggestions = useMemo(() => suggestions, [suggestions]);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.suggestions-dropdown')) {
        onClose();
      }
    };

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onClose]);

  // Memoize click handler to prevent unnecessary re-renders
  const handleSuggestionClick = useCallback((suggestion: Suggestion) => {
    onSuggestionClick(suggestion);
    onClose();
  }, [onSuggestionClick, onClose]);

  if (!isOpen) return null;

  return (
    <div className="suggestions-dropdown fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md">
      <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-2xl backdrop-blur-sm">
        {isLoading ? (
          <div className="p-4 text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-400 mx-auto"></div>
            <p className="text-gray-400 mt-2 text-sm">Analisando sua necessidade...</p>
          </div>
        ) : memoizedSuggestions.length > 0 ? (
          <div className="max-h-64 overflow-y-auto">
            {memoizedSuggestions.map((suggestion) => (
              <button
                key={suggestion.id}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left p-4 hover:bg-gray-800 transition-colors duration-200 border-b border-gray-700 last:border-b-0 focus:outline-none focus:bg-gray-800"
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white font-medium text-sm mb-1">
                      {suggestion.title}
                    </h3>
                    <p className="text-gray-400 text-xs leading-relaxed">
                      {suggestion.description}
                    </p>
                    <span className="inline-block mt-2 px-2 py-1 bg-gray-800 text-green-400 text-xs rounded">
                      {suggestion.category}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="p-4 text-center">
            <p className="text-gray-400 text-sm">Digite mais detalhes para receber sugestões personalizadas</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SuggestionsDropdown; 