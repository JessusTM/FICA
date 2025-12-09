import React, { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import ETLStatus from '../components/ETLStatus';
import apiClient from '../config/api';

function UploadPage() {
  const [etlStarted, setEtlStarted] = useState(false);
  const [dbStatus, setDbStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkDatabaseStatus = async () => {
      try {
        const response = await apiClient.get('/database-status');
        setDbStatus(response.data);
      } catch (error) {
        console.error('Error checking database status:', error);
        // Si hay error, permitir la carga por defecto
        setDbStatus({ hasData: false, canRunETL: true });
      } finally {
        setLoading(false);
      }
    };

    checkDatabaseStatus();
  }, []);

  const handleETLStart = () => {
    setEtlStarted(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-600">Verificando estado de la base de datos...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const blockReason = dbStatus?.hasData
    ? `La tabla estudiantes contiene ${dbStatus.studentCount} registros. ${
        dbStatus.lastUpload
          ? `Última carga: ${dbStatus.lastUpload.filename} el ${new Date(dbStatus.lastUpload.date).toLocaleString('es-ES')}`
          : ''
      }`
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Ejecutar ETL
          </h1>
          <p className="text-gray-600 mb-8">
            {dbStatus?.canRunETL
              ? 'Debes subir el archivo .xlsx fuente para iniciar el proceso ETL.'
              : 'La base de datos ya contiene datos procesados.'}
          </p>

          <div className="space-y-6">
            <FileUpload
              onETLStart={handleETLStart}
              isBlocked={!dbStatus?.canRunETL}
              blockReason={blockReason}
            />
            <ETLStatus shouldStartPolling={etlStarted} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
