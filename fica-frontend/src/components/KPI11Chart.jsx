import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Componente para el KPI 1.1 - Desviación promedio de ramos cursados
 */
const KPI11Chart = ({ data }) => {
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
    labels: ['Desviación Promedio', 'Mínima', 'Máxima'],
    datasets: [
      {
        label: 'Desviación de Ramos',
        data: [
          result.value,
          result.meta?.desviaciones_por_estudiante?.min || 0,
          result.meta?.desviaciones_por_estudiante?.max || 0,
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.5)',  // blue
          'rgba(16, 185, 129, 0.5)',  // green
          'rgba(239, 68, 68, 0.5)',   // red
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 1,
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
        text: `KPI 1.1 - Desviación de Ramos (Cohorte ${data.cohorte})`,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Desviación Promedio de Ramos Cursados vs Ideal (8)
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Estudiantes en cohorte: {result.meta?.E || 0}
        </p>
        <p className="text-sm text-gray-600">
          Promedio de ramos: {result.meta?.distribucion_ramos?.promedio?.toFixed(2) || 'N/A'}
        </p>
      </div>
      <div style={{ height: '300px' }}>
        <Bar data={chartData} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <span className="font-semibold">Desviación Promedio:</span>
          <span className="ml-2">{result.value.toFixed(2)}</span>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <span className="font-semibold">Std Dev:</span>
          <span className="ml-2">
            {result.meta?.desviaciones_por_estudiante?.std?.toFixed(2) || 'N/A'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default KPI11Chart;

