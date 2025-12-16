import React, { useState, useEffect, useRef } from 'react';

function SearchBar({ onSearch, placeholder = 'Buscar...' }) {
  const [searchInput, setSearchInput] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const debounceTimeout = useRef(null);
  const previousSearch = useRef('');

  // Debounce search to avoid too many API calls
  useEffect(() => {
    // Only trigger search if the value actually changed
    if (searchInput === previousSearch.current) {
      return;
    }

    setIsSearching(true);

    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      onSearch(searchInput);
      previousSearch.current = searchInput;
      setIsSearching(false);
    }, 500); // 500ms debounce

    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    };
  }, [searchInput, onSearch]);

  const handleClear = () => {
    setSearchInput('');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>

        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder={placeholder}
          className="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
        />

        <div className="absolute inset-y-0 right-0 pr-3 flex items-center space-x-2">
          {isSearching && (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          )}
          {searchInput && !isSearching && (
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Limpiar búsqueda"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          )}
        </div>
      </div>

      {searchInput && (
        <div className="mt-3 text-sm text-gray-600">
          {isSearching ? (
            <span>Buscando...</span>
          ) : (
            <span>
              Mostrando resultados para: <strong>{searchInput}</strong>
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchBar;
