import React, { useState, useEffect } from 'react';
import apiClient from '../config/api';
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
  gold_kpi_b1_student: {
    name: 'KPI B1 - Estudiantes',
    icon: '/base-de-datos.png',
    description: 'Datos agregados para KPIs del primer bimestre',
  },
  gold_kpi_student_ramos: {
    name: 'KPI - Total Ramos',
    icon: '/base-de-datos.png',
    description: 'Total de ramos cursados por estudiante',
  },
  gold_kpi_student_aprueba8: {
    name: 'KPI - Aprueba 8 Ramos',
    icon: '/base-de-datos.png',
    description: 'Indicador de estudiantes que aprueban 8+ ramos',
  },
};

function TableExplorer() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loadingTables, setLoadingTables] = useState(true);
  const [tablesError, setTablesError] = useState(null);

  // Fetch available tables on mount
  useEffect(() => {
    const fetchTables = async () => {
      setLoadingTables(true);
      setTablesError(null);
      try {
        const response = await apiClient.get('/tables');
        setTables(response.data.tables || []);
      } catch (error) {
        console.error('Error fetching tables:', error);
        setTablesError(error.response?.data?.detail || error.response?.data?.message || 'No se pudieron cargar las tablas');
        setTables([]);
      } finally {
        setLoadingTables(false);
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
        const params = {
          page: currentPage,
          limit: 50,
        };

        const response = await apiClient.get(`/tables/${selectedTable}`, { params });

        // Transform backend response to match DataTable expected format
        const transformedData = {
          columns: response.data.columns || [],
          rows: response.data.data || [],
          totalCount: response.data.totalRecords || 0,
        };

        setTableData(transformedData);
        setTotalPages(response.data.totalPages || 1);
      } catch (error) {
        console.error('Error fetching table data:', error);
        setError(
          error.response?.data?.detail ||
          error.response?.data?.message ||
          'Error al cargar los datos de la tabla'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchTableData();
  }, [selectedTable, currentPage]);

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage) => {
    console.log('Changing to page:', newPage, 'Current:', currentPage);
    setCurrentPage(newPage);
  };

  return (
    <div className="space-y-6">
      {/* Loading Tables State */}
      {loadingTables ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando tablas disponibles...</p>
        </div>
      ) : tables.length === 0 ? (
        /* No Tables Available - Blocked State */
        <div className="bg-white rounded-lg shadow-md p-12 text-center border-2 border-red-200">
          <div className="mb-6 flex justify-center">
            <svg
              className="w-24 h-24 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-3">
            No hay datos disponibles
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Las tablas de la base de datos están vacías.
            Debes ejecutar el proceso ETL para cargar los datos desde el archivo CSV.
          </p>
          {tablesError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg max-w-md mx-auto">
              <p className="text-red-700 text-sm">{tablesError}</p>
            </div>
          )}
          <a
            href="/upload"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir a ejecutar ETL
          </a>
        </div>
      ) : (
        /* Normal State - Tables Available */
        <>
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

          {/* Data Display */}
          {selectedTable && (
            <>

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
        </>
      )}
    </div>
  );
}

export default TableExplorer;
