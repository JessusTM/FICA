import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ETLStatus() {
  const [status, setStatus] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  const etlSteps = [
    {
      id: 1,
      name: 'Filtrado de Cursos',
      description: 'Eliminando clases de álgebra',
      script: 'delete_algebra_classes.py',
    },
    {
      id: 2,
      name: 'Clasificación por Prueba',
      description: 'Agrupando por PAES/PDT',
      script: 'group_by_test.py',
    },
    {
      id: 3,
      name: 'Asignación de IDs',
      description: 'Generando IDs de estudiantes',
      script: 'group_by_student.py',
    },
    {
      id: 4,
      name: 'Carga a Base de Datos',
      description: 'Poblando tablas de PostgreSQL',
      script: 'populate_database.py',
    },
  ];

  useEffect(() => {
    let interval;

    const fetchStatus = async () => {
      try {
        // Replace with your actual API endpoint
        const response = await axios.get('/api/etl/status');
        setStatus(response.data);

        // Stop polling if ETL is completed or failed
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          setIsPolling(false);
        }
      } catch (error) {
        console.error('Error fetching ETL status:', error);
      }
    };

    if (isPolling) {
      interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds
      fetchStatus(); // Initial fetch
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPolling]);

  // Start polling when component mounts if ETL is running
  useEffect(() => {
    const checkInitialStatus = async () => {
      try {
        const response = await axios.get('/api/etl/status');
        setStatus(response.data);
        if (response.data.status === 'running') {
          setIsPolling(true);
        }
      } catch (error) {
        // ETL not running or endpoint not available
        console.log('No active ETL process');
      }
    };

    checkInitialStatus();
  }, []);

  const getStepStatus = (stepId) => {
    if (!status) return 'pending';

    if (status.currentStep > stepId) return 'completed';
    if (status.currentStep === stepId) {
      if (status.status === 'failed') return 'failed';
      return 'running';
    }
    return 'pending';
  };

  const getStatusIcon = (stepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return <span className="text-green-500 text-2xl">✓</span>;
      case 'running':
        return (
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        );
      case 'failed':
        return <span className="text-red-500 text-2xl">✗</span>;
      default:
        return <span className="text-gray-300 text-2xl">○</span>;
    }
  };

  if (!status || status.status === 'idle') {
    return null; // Don't show if no ETL process has started
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          Estado del Proceso ETL
        </h2>
        {status.status === 'running' && (
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            En Proceso
          </span>
        )}
        {status.status === 'completed' && (
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            Completado
          </span>
        )}
        {status.status === 'failed' && (
          <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            Error
          </span>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progreso</span>
          <span className="text-sm font-medium text-gray-700">
            {Math.round(((status.currentStep - 1) / etlSteps.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{
              width: `${((status.currentStep - 1) / etlSteps.length) * 100}%`,
            }}
          ></div>
        </div>
      </div>

      {/* ETL Steps */}
      <div className="space-y-4">
        {etlSteps.map((step) => {
          const stepStatus = getStepStatus(step.id);
          return (
            <div
              key={step.id}
              className={`flex items-start p-4 rounded-lg border-2 transition-all ${
                stepStatus === 'running'
                  ? 'border-blue-500 bg-blue-50'
                  : stepStatus === 'completed'
                  ? 'border-green-500 bg-green-50'
                  : stepStatus === 'failed'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex-shrink-0 mr-4 mt-1">
                {getStatusIcon(stepStatus)}
              </div>
              <div className="flex-grow">
                <h3 className="font-semibold text-gray-800">
                  {step.id}. {step.name}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {step.description}
                </p>
                <p className="text-xs text-gray-500 mt-1 font-mono">
                  {step.script}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Error Message */}
      {status.status === 'failed' && status.error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 font-medium mb-1">Error:</p>
          <p className="text-red-600 text-sm">{status.error}</p>
        </div>
      )}

      {/* Success Message */}
      {status.status === 'completed' && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-700 font-medium">
            ✓ Proceso ETL completado exitosamente
          </p>
          <p className="text-green-600 text-sm mt-1">
            Los datos han sido cargados a la base de datos PostgreSQL.
          </p>
        </div>
      )}

      {/* Timing Information */}
      {status.startTime && (
        <div className="mt-4 text-xs text-gray-500">
          <p>
            Iniciado: {new Date(status.startTime).toLocaleString()}
          </p>
          {status.endTime && (
            <p>
              Finalizado: {new Date(status.endTime).toLocaleString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default ETLStatus;
