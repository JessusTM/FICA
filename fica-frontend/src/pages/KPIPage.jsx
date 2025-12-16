import React, { useState, useEffect } from 'react';
import { getKPIList, getKPIData } from '../services/kpiService';
import KPI11Chart from '../components/KPI11Chart';
import KPI121Chart from '../components/KPI121Chart';
import KPI122Chart from '../components/KPI122Chart';
import KPI13Chart from '../components/KPI13Chart';
import KPI14Chart from '../components/KPI14Chart';
import KPI15Chart from '../components/KPI15Chart';
import KPI16Chart from '../components/KPI16Chart';
import KPI17Chart from '../components/KPI17Chart';
import KPI18Chart from '../components/KPI18Chart';

const KPIPage = () => {
  const [kpiList, setKpiList] = useState([]);
  const [selectedKPIs, setSelectedKPIs] = useState(['1.1', '1.2.1']); // KPIs por defecto
  const [cohorte, setCohorte] = useState(2022);
  const [kpiData, setKpiData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar lista de KPIs disponibles al montar el componente
  useEffect(() => {
    const fetchKPIList = async () => {
      try {
        const data = await getKPIList();
        setKpiList(data.kpis || []);
      } catch (err) {
        console.error('Error loading KPI list:', err);
      }
    };

    fetchKPIList();
  }, []);

  // Cargar datos de los KPIs seleccionados
  useEffect(() => {
    const fetchKPIData = async () => {
      if (selectedKPIs.length === 0) return;

      setLoading(true);
      setError(null);

      try {
        const dataPromises = selectedKPIs.map(kpiId =>
          getKPIData(kpiId, cohorte)
        );
        const results = await Promise.all(dataPromises);

        const dataMap = {};
        results.forEach(result => {
          dataMap[result.kpi_id] = result;
        });

        setKpiData(dataMap);
      } catch (err) {
        setError('Error al cargar los datos de KPI: ' + err.message);
        console.error('Error loading KPI data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchKPIData();
  }, [selectedKPIs, cohorte]);

  const handleKPIToggle = (kpiId) => {
    setSelectedKPIs(prev => {
      if (prev.includes(kpiId)) {
        return prev.filter(id => id !== kpiId);
      } else {
        return [...prev, kpiId];
      }
    });
  };

  const handleCohorteChange = (e) => {
    const value = Number.parseInt(e.target.value, 10);
    if (!Number.isNaN(value)) {
      setCohorte(value);
    }
  };

  const renderKPIChart = (kpiId) => {
    const data = kpiData[kpiId];

    if (!data) {
      return <div className="text-gray-500">Cargando...</div>;
    }

    switch (kpiId) {
      case '1.1':
        return <KPI11Chart data={data} />;
      case '1.2.1':
        return <KPI121Chart data={data} />;
      case '1.2.2':
        return <KPI122Chart data={data} />;
      case '1.3':
        return <KPI13Chart data={data} />;
      case '1.4':
        return <KPI14Chart data={data} />;
      case '1.5':
        return <KPI15Chart data={data} />;
      case '1.6':
        return <KPI16Chart data={data} />;
      case '1.7':
        return <KPI17Chart data={data} />;
      case '1.8':
        return <KPI18Chart data={data} />;
      default:
        return (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">KPI {kpiId}</h3>
            <pre className="bg-gray-50 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Indicadores de Desempeño (KPI)
        </h1>
        <p className="text-gray-600">
          Visualización de indicadores clave de desempeño académico
        </p>
      </div>

      {/* Panel de control */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Selector de Cohorte */}
          <div>
            <label htmlFor="cohorte-input" className="block text-sm font-medium text-gray-700 mb-2">
              Cohorte
            </label>
            <input
              id="cohorte-input"
              type="number"
              value={cohorte}
              onChange={handleCohorteChange}
              min="2000"
              max="2100"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Selector de KPIs */}
          <div>
            <div className="block text-sm font-medium text-gray-700 mb-2">
              KPIs a Visualizar
            </div>
            <div className="grid grid-cols-3 gap-2">
              {kpiList.map(kpiId => (
                <button
                  key={kpiId}
                  onClick={() => handleKPIToggle(kpiId)}
                  className={`px-3 py-2 text-sm rounded-md transition-colors ${
                    selectedKPIs.includes(kpiId)
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  KPI {kpiId}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Botón de actualizar */}
        <div className="mt-4">
          <button
            onClick={() => setSelectedKPIs([...selectedKPIs])}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Cargando...' : 'Actualizar Datos'}
          </button>
        </div>
      </div>

      {/* Mensaje de error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Gráficas de KPIs */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Cargando datos de KPI...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {selectedKPIs.map(kpiId => (
            <div key={kpiId}>
              {renderKPIChart(kpiId)}
            </div>
          ))}
        </div>
      )}

      {selectedKPIs.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          Selecciona al menos un KPI para visualizar
        </div>
      )}
    </div>
  );
};

export default KPIPage;

