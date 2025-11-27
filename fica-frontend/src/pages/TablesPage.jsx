import React from 'react';
import TableExplorer from '../components/TableExplorer';

function TablesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Data Explorer
          </h1>
          <p className="text-gray-600 mb-8">
            Explora y busca en las tablas de la base de datos
          </p>

          <TableExplorer />
        </div>
      </div>
    </div>
  );
}

export default TablesPage;
