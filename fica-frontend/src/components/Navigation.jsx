import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-blue-600">FICA</span>
            <span className="text-sm text-gray-500">Portal ETL </span>
          </Link>

          <div className="flex space-x-1">
            <Link
              to="/"
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                isActive('/')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Inicio
            </Link>
            <Link
              to="/upload"
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                isActive('/upload')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              ETL
            </Link>
            <Link
              to="/tables"
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                isActive('/tables')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Tablas
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
