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
 * Componente para el KPI 1.2.2 - Correlación Diagnóstico Matemáticas vs Nota 1er bimestre
 */
const KPI122Chart = ({ data }) => {
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

  const chartData = {
    labels: ['Correlación'],
    datasets: [
      {
        label: 'Coeficiente de Correlación',
        data: [{ x: 0, y: result.value }],
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
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
        text: `KPI 1.2.2 - Correlación Diagnóstico vs Nota B1 (Cohorte ${data.cohorte})`,
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
          Correlación Diagnóstico de Matemáticas vs Nota Primer Bimestre
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Observaciones: {result.meta?.n || 0}
        </p>
      </div>
      <div style={{ height: '300px' }}>
        <Scatter data={chartData} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-green-50 p-3 rounded">
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
      {result.meta?.diagnostico && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Estadísticas Diagnóstico:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>Promedio: {result.meta.diagnostico.promedio?.toFixed(2)}</div>
            <div>Mín: {result.meta.diagnostico.min?.toFixed(2)}</div>
            <div>Máx: {result.meta.diagnostico.max?.toFixed(2)}</div>
          </div>
        </div>
      )}
      {result.meta?.nota_b1 && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Estadísticas Nota B1:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>Promedio: {result.meta.nota_b1.promedio?.toFixed(2)}</div>
            <div>Mín: {result.meta.nota_b1.min?.toFixed(2)}</div>
            <div>Máx: {result.meta.nota_b1.max?.toFixed(2)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KPI122Chart;

