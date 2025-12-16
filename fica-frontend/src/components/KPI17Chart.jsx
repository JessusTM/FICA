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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Componente para el KPI 1.7 - Promedio Nota 1er bimestre por quintil de ingreso
 */
const KPI17Chart = ({ data }) => {
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

  const quintiles = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'];
  const promedios = quintiles.map(q => result.value[q] || 0);

  const chartData = {
    labels: quintiles,
    datasets: [
      {
        label: 'Promedio Nota B1',
        data: promedios,
        backgroundColor: [
          'rgba(239, 68, 68, 0.5)',
          'rgba(245, 158, 11, 0.5)',
          'rgba(234, 179, 8, 0.5)',
          'rgba(34, 197, 94, 0.5)',
          'rgba(59, 130, 246, 0.5)',
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(245, 158, 11)',
          'rgb(234, 179, 8)',
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
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
        text: `KPI 1.7 - Promedio Nota B1 por Quintil (Cohorte ${data.cohorte})`,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `Promedio: ${context.parsed.y.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 7,
        title: {
          display: true,
          text: 'Promedio Nota B1',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Quintil de Perfil de Ingreso',
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Promedio Nota Primer Bimestre por Quintil de Ingreso
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Estudiantes válidos: {result.meta?.n_validos || 0}
        </p>
        {result.meta?.n_excluidos > 0 && (
          <p className="text-sm text-orange-600">
            Excluidos: {result.meta.n_excluidos}
          </p>
        )}
      </div>
      <div style={{ height: '300px' }}>
        <Bar data={chartData} options={options} />
      </div>
      {result.meta?.detalles_quintiles && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Detalles por Quintil:</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Quintil</th>
                  <th className="text-right py-2">N</th>
                  <th className="text-right py-2">Promedio</th>
                  <th className="text-right py-2">Mín</th>
                  <th className="text-right py-2">Máx</th>
                  <th className="text-right py-2">Std</th>
                </tr>
              </thead>
              <tbody>
                {quintiles.map(q => {
                  const detalle = result.meta.detalles_quintiles[q];
                  return (
                    <tr key={q} className="border-b">
                      <td className="py-2 font-semibold">{q}</td>
                      <td className="text-right">{detalle?.n || 0}</td>
                      <td className="text-right">{detalle?.promedio?.toFixed(2) || '-'}</td>
                      <td className="text-right">{detalle?.min?.toFixed(2) || '-'}</td>
                      <td className="text-right">{detalle?.max?.toFixed(2) || '-'}</td>
                      <td className="text-right">{detalle?.std?.toFixed(2) || '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default KPI17Chart;

