import React from 'react';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrar componentes de Chart.js
ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Componente para el KPI 1.2.1 - Correlación PAES/PDT vs Nota 1er bimestre
 */
const KPI121Chart = ({ data }) => {
  if (!data || !data.result) {
    return <div className="text-gray-500">No hay datos disponibles</div>;
  }

  const { result } = data;

  if (result.value === null) {
    return (
      <div className="text-red-500">
        {result.meta?.error || 'Error al cargar datos'}
      </div>
    );
  }

  // Nota: Para un scatter plot real necesitaríamos los puntos individuales
  // Por ahora mostramos un gráfico de línea simple con la correlación
  const chartData = {
    labels: ['Correlación'],
    datasets: [
      {
        label: 'Coeficiente de Correlación',
        data: [{ x: 0, y: result.value }],
        backgroundColor: 'rgba(139, 92, 246, 0.5)',
        borderColor: 'rgb(139, 92, 246)',
        pointRadius: 8,
        pointHoverRadius: 10,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `KPI 1.2.1 - Correlación PAES/PDT vs Nota B1 (Cohorte ${data.cohorte})`,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `Correlación: ${context.parsed.y.toFixed(4)}`;
          },
        },
      },
    },
    scales: {
      y: {
        min: -1,
        max: 1,
        title: {
          display: true,
          text: 'Coeficiente de Correlación',
        },
      },
      x: {
        display: false,
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Correlación PAES/PDT vs Nota Primer Bimestre
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Observaciones: {result.meta?.n || 0}
        </p>
        {result.meta?.distribucion_tipo_prueba && (
          <div className="text-sm text-gray-600 mt-1">
            <span className="font-semibold">Distribución:</span>
            {Object.entries(result.meta.distribucion_tipo_prueba).map(([tipo, count]) => (
              <span key={tipo} className="ml-2">
                {tipo}: {count}
              </span>
            ))}
          </div>
        )}
      </div>
      <div style={{ height: '300px' }}>
        <Scatter data={chartData} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-purple-50 p-3 rounded">
          <span className="font-semibold">Correlación:</span>
          <span className="ml-2">{result.value.toFixed(4)}</span>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <span className="font-semibold">Interpretación:</span>
          <span className="ml-2">
            {Math.abs(result.value) > 0.7 ? 'Fuerte' :
             Math.abs(result.value) > 0.4 ? 'Moderada' : 'Débil'}
          </span>
        </div>
      </div>
      {result.meta?.estadisticas_puntaje_ingreso && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Estadísticas Puntaje de Ingreso:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>Promedio: {result.meta.estadisticas_puntaje_ingreso.promedio?.toFixed(2)}</div>
            <div>Mín: {result.meta.estadisticas_puntaje_ingreso.min?.toFixed(2)}</div>
            <div>Máx: {result.meta.estadisticas_puntaje_ingreso.max?.toFixed(2)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KPI121Chart;

