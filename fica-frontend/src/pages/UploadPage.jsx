import React from 'react';
import FileUpload from '../components/FileUpload';
import ETLStatus from '../components/ETLStatus';

function UploadPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Ejecutar ETL
          </h1>
          <p className="text-gray-600 mb-8">
              Debes subir el archivo .xlsx fuente para iniciar el proceso ETL.
          </p>

          <div className="space-y-6">
            <FileUpload />
            <ETLStatus />
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
