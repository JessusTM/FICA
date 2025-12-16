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
 * Componente para el KPI 1.3 - Correlación múltiple (R) de predictores vs Nota B1
 */
const KPI13Chart = ({ data }) => {
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

  const tipoRegresion = result.meta?.tipo_regresion || 'múltiple';
  const tituloGrafica = tipoRegresion === 'simple'
    ? `KPI 1.3 - Correlación Simple (Cohorte ${data.cohorte})`
    : `KPI 1.3 - Correlación Múltiple (Cohorte ${data.cohorte})`;

  const chartData = {
    labels: ['R (Correlación)', 'R²'],
    datasets: [
      {
        label: 'Valores de Correlación',
        data: [
          result.value,
          result.meta?.R2 || 0,
        ],
        backgroundColor: [
          'rgba(249, 115, 22, 0.5)',
          'rgba(245, 158, 11, 0.5)',
        ],
        borderColor: [
          'rgb(249, 115, 22)',
          'rgb(245, 158, 11)',
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
        text: tituloGrafica,
      },
    },
    scales: {
      y: {
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'Coeficiente',
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {tipoRegresion === 'simple'
            ? 'Correlación Simple - Puntaje de Ingreso vs Nota B1'
            : 'Correlación Múltiple - Predictores de Ingreso vs Nota B1'}
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          Observaciones: {result.meta?.n || 0}
        </p>
        <p className="text-sm text-gray-600">
          Tipo de regresión: <span className="font-semibold capitalize">{tipoRegresion}</span>
        </p>
        {result.meta?.predictores && (
          <p className="text-sm text-gray-600">
            Predictores: {result.meta.predictores.join(', ')}
          </p>
        )}
      </div>
      <div style={{ height: '300px' }}>
        <Bar data={chartData} options={options} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-orange-50 p-3 rounded">
          <span className="font-semibold">R (Correlación):</span>
          <span className="ml-2">{result.value.toFixed(4)}</span>
        </div>
        <div className="bg-amber-50 p-3 rounded">
          <span className="font-semibold">R² (Determinación):</span>
          <span className="ml-2">{result.meta?.R2?.toFixed(4) || 'N/A'}</span>
        </div>
      </div>
      {result.meta?.coeficientes && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h4 className="font-semibold text-sm mb-2">Coeficientes de Regresión:</h4>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>β₀ (Intercepto): {result.meta.coeficientes.beta0?.toFixed(4)}</div>
            <div>β₁ (PAES/PDT): {result.meta.coeficientes.beta1_paes_pdt?.toFixed(4)}</div>
            {result.meta.coeficientes.beta2_diagnostico !== undefined && (
              <div>β₂ (Diagnóstico): {result.meta.coeficientes.beta2_diagnostico?.toFixed(4)}</div>
            )}
          </div>
        </div>
      )}
      {result.meta?.notes && result.meta.notes.length > 0 && (
        <div className="mt-4 bg-blue-50 p-4 rounded border border-blue-200">
          <h4 className="font-semibold text-sm mb-2 text-blue-800">Información:</h4>
          <ul className="text-sm text-blue-700 list-disc list-inside">
            {result.meta.notes.map((note, idx) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default KPI13Chart;

