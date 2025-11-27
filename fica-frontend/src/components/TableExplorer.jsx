import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchBar from './SearchBar';
import DataTable from './DataTable';

// Table metadata for better display
const tableMetadata = {
    estudiantes: {
      name: 'Estudiantes',
      icon: '/lista-de-tablas.png',
      description: 'Información de estudiantes y sus puntajes',
    },
    semestres: {
      name: 'Semestres',
      icon: '/lista-de-tablas.png',
      description: 'Periodos académicos semestrales',
    },
    bimestres: {
      name: 'Bimestres',
      icon: '/lista-de-tablas.png',
      description: 'Periodos académicos bimestrales',
    },
    asignaturas: {
      name: 'Asignaturas',
      icon: '/lista-de-tablas.png',
      description: 'Información de cursos y módulos',
    },
    rendimiento_ramo: {
      name: 'Rendimiento por ramo',
      icon: '/lista-de-tablas.png',
      description: 'Rendimiento de estudiantes por asignatura',
    },
    paes: {
      name: 'PAES',
      icon: '/lista-de-tablas.png',
      description: 'Resultados de prueba PAES',
    },
    pdt: {
      name: 'PDT',
      icon: '/lista-de-tablas.png',
      description: 'Resultados de prueba PDT',
    },
};

function TableExplorer() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch available tables on mount
  useEffect(() => {
    const fetchTables = async () => {
      try {
        // Replace with your actual API endpoint
        const response = await axios.get('/api/tables');
        setTables(response.data.tables || []);
      } catch (error) {
        console.error('Error fetching tables:', error);
        // Set default tables if API is not available
        setTables(Object.keys(tableMetadata));
      }
    };

    fetchTables();
  }, []);

  // Fetch table data when selection or page changes
  useEffect(() => {
    if (!selectedTable) {
      setTableData(null);
      return;
    }

    const fetchTableData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Replace with your actual API endpoint
        const params = {
          page: currentPage,
          limit: 50,
        };

        if (searchQuery) {
          params.search = searchQuery;
        }

        const response = await axios.get(`/api/tables/${selectedTable}`, { params });

        setTableData(response.data);
        setTotalPages(response.data.totalPages || 1);
      } catch (error) {
        console.error('Error fetching table data:', error);
        setError(
          error.response?.data?.message ||
          'Error al cargar los datos de la tabla'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchTableData();
  }, [selectedTable, currentPage, searchQuery]);

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    setCurrentPage(1);
    setSearchQuery('');
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  return (
    <div className="space-y-6">
      {/* Table Selection */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Selecciona una tabla
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {tables.map((tableName) => {
            const metadata = tableMetadata[tableName] || {
              name: tableName,
              icon: '/lista-de-tablas.png',
              description: '',
            };

            return (
              <button
                key={tableName}
                onClick={() => handleTableSelect(tableName)}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  selectedTable === tableName
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="mb-2">
                  <img
                    src={metadata.icon}
                    alt={metadata.name}
                    className="w-12 h-12"
                  />
                </div>
                <h3 className="font-semibold text-gray-800 text-sm">
                  {metadata.name}
                </h3>
                {metadata.description && (
                  <p className="text-xs text-gray-500 mt-1">
                    {metadata.description}
                  </p>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Search and Data Display */}
      {selectedTable && (
        <>
          <SearchBar
            onSearch={handleSearch}
            placeholder={`Buscar en ${tableMetadata[selectedTable]?.name || selectedTable}...`}
          />

          {loading ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando datos...</p>
            </div>
          ) : error ? (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          ) : tableData ? (
            <DataTable
              data={tableData}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          ) : null}
        </>
      )}

      {!selectedTable && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="mb-4 flex justify-center">
            <img
              src="/lista-de-tablas.png"
              alt="Tablas"
              className="w-24 h-24"
            />
          </div>
          <p className="text-gray-600 text-lg">
            Selecciona una tabla para comenzar
          </p>
        </div>
      )}
    </div>
  );
}

export default TableExplorer;
