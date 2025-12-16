import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Componente para el KPI 1.4 - Estudiantes que aprueban los 8 bimestres sin reprobar ramos
 */
const KPI14Chart = ({ data }) => {
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

  const aprueban = result.meta?.Naprueban_8 || 0;
  const noAprueban = (result.meta?.E || 0) - aprueban;

  const chartData = {
    labels: ['Aprueban 8 Bimestres', 'No Aprueban'],
    datasets: [
      {
        data: [aprueban, noAprueban],
        backgroundColor: [
          'rgba(34, 197, 94, 0.5)',
          'rgba(239, 68, 68, 0.5)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
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
        text: `KPI 1.4 - Aprobación 8 Bimestres (Cohorte ${data.cohorte})`,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            const percentage = ((value / (result.meta?.E || 1)) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Estudiantes que Aprueban 8 Bimestres sin Reprobar
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Total estudiantes en cohorte: {result.meta?.E || 0}
        </p>
      </div>
      <div style={{ height: '300px' }}>
        <Doughnut data={chartData} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="bg-green-50 p-3 rounded">
          <span className="font-semibold">Aprueban:</span>
          <span className="ml-2">{aprueban}</span>
        </div>
        <div className="bg-red-50 p-3 rounded">
          <span className="font-semibold">No Aprueban:</span>
          <span className="ml-2">{noAprueban}</span>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <span className="font-semibold">Tasa:</span>
          <span className="ml-2">{result.meta?.tasa_aprobacion?.toFixed(1)}%</span>
        </div>
      </div>
      {result.meta?.notes && result.meta.notes.length > 0 && (
        <div className="mt-4 bg-yellow-50 p-4 rounded border border-yellow-200">
          <h4 className="font-semibold text-sm mb-2 text-yellow-800">Notas:</h4>
          <ul className="text-sm text-yellow-700 list-disc list-inside">
            {result.meta.notes.map((note, idx) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default KPI14Chart;

