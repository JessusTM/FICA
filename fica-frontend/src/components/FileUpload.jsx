import React, { useState, useRef } from 'react';
import axios from 'axios';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'uploading', 'success', 'error'
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    validateAndSetFile(droppedFile);
  };

  const handleFileInput = (e) => {
    const selectedFile = e.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (file) => {
    if (!file) return;

    // Validate file type
    const validExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      setErrorMessage('Por favor, sube un archivo .xlsx o .xls');
      setFile(null);
      return;
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      setErrorMessage('El archivo es demasiado grande. Tamaño máximo: 50MB');
      setFile(null);
      return;
    }

    setFile(file);
    setErrorMessage('');
    setUploadStatus(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus('uploading');
      setErrorMessage('');

      // Replace with your actual API endpoint
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus('success');
      console.log('Upload successful:', response.data);
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(
        error.response?.data?.message ||
        'Error al subir el archivo. Por favor, intenta de nuevo.'
      );
      console.error('Upload error:', error);
    }
  };

  const handleStartETL = async () => {
    try {
      setUploadStatus('uploading');
      setErrorMessage('');

      // Replace with your actual API endpoint
      const response = await axios.post('/api/etl/start');

      setUploadStatus('success');
      console.log('ETL started:', response.data);
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(
        error.response?.data?.message ||
        'Error al iniciar el proceso ETL. Por favor, intenta de nuevo.'
      );
      console.error('ETL start error:', error);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setUploadStatus(null);
    setErrorMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">

      {/* Drag and Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileInput}
          className="hidden"
        />

        {!file ? (
          <>
            <div className="text-5xl mb-4">📁</div>
            <p className="text-lg text-gray-700 mb-2">
              Arrastra y suelta tu archivo aquí
            </p>
            <p className="text-sm text-gray-500 mb-4">
              o haz clic para seleccionar
            </p>
            <p className="text-xs text-gray-400">
              Formatos soportados: .xlsx, .xls (máx. 50MB)
            </p>
          </>
        ) : (
          <div className="space-y-4">
            <div className="text-5xl">✅</div>
            <div>
              <p className="text-lg font-medium text-gray-800">
                {file.name}
              </p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                resetUpload();
              }}
              className="text-sm text-red-600 hover:text-red-700 underline"
            >
              Eliminar archivo
            </button>
          </div>
        )}
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{errorMessage}</p>
        </div>
      )}

      {/* Action Buttons */}
      {file && uploadStatus !== 'success' && (
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={uploadStatus === 'uploading'}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploadStatus === 'uploading' ? 'Subiendo...' : 'Subir Archivo'}
          </button>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="mt-6 space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-medium">
              ✓ Archivo subido exitosamente
            </p>
          </div>
          <button
            onClick={handleStartETL}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Iniciar Proceso ETL
          </button>
          <button
            onClick={resetUpload}
            className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Subir Otro Archivo
          </button>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
