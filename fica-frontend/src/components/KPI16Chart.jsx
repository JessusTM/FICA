import React from 'react';
import { Pie } from 'react-chartjs-2';
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
 * Componente para el KPI 1.6 - Distribución por quintiles del perfil de ingreso
 */
const KPI16Chart = ({ data }) => {
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
  const porcentajes = quintiles.map(q => result.value[q] || 0);

  const chartData = {
    labels: quintiles,
    datasets: [
      {
        label: 'Distribución por Quintil (%)',
        data: porcentajes,
        backgroundColor: [
          'rgba(239, 68, 68, 0.5)',    // Q1 - Rojo
          'rgba(245, 158, 11, 0.5)',   // Q2 - Naranja
          'rgba(234, 179, 8, 0.5)',    // Q3 - Amarillo
          'rgba(132, 204, 22, 0.5)',   // Q4 - Verde claro
          'rgba(34, 197, 94, 0.5)',    // Q5 - Verde
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(245, 158, 11)',
          'rgb(234, 179, 8)',
          'rgb(132, 204, 22)',
          'rgb(34, 197, 94)',
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
        position: 'right',
      },
      title: {
        display: true,
        text: `KPI 1.6 - Distribución por Quintiles (Cohorte ${data.cohorte})`,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: ${value.toFixed(2)}%`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Distribución por Quintiles del Perfil de Ingreso
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Estudiantes válidos: {result.meta?.E || 0}
        </p>
        {result.meta?.E_excluidos > 0 && (
          <p className="text-sm text-orange-600">
            Excluidos: {result.meta.E_excluidos}
          </p>
        )}
      </div>
      <div style={{ height: '300px' }}>
        <Pie data={chartData} options={options} />
      </div>
      {result.meta?.distribucion_absoluta && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Distribución Absoluta:</h4>
          <div className="grid grid-cols-5 gap-2 text-sm">
            {quintiles.map(q => (
              <div key={q} className="text-center">
                <div className="font-semibold">{q}</div>
                <div>{result.meta.distribucion_absoluta[q] || 0}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      {result.meta?.indice_ingreso && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Estadísticas Índice de Ingreso:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>Promedio: {result.meta.indice_ingreso.promedio?.toFixed(2)}</div>
            <div>Mín: {result.meta.indice_ingreso.min?.toFixed(2)}</div>
            <div>Máx: {result.meta.indice_ingreso.max?.toFixed(2)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KPI16Chart;

