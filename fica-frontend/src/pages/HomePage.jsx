import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Portal ETL FICA
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            Sistema de procesamiento y análisis de datos académicos
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Link
              to="/upload"
              className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow border-2 border-transparent hover:border-blue-500"
            >
              <div className="mb-4 flex justify-center">
                <img
                  src="/proceso.png"
                  alt="Upload"
                  className="w-16 h-16"
                />
              </div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                Ejecutar
              </h2>
              <p className="text-gray-600">
                Sube el archivo .xlsx fuente y ejecuta el proceso ETL
              </p>
            </Link>

            <Link
              to="/tables"
              className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow border-2 border-transparent hover:border-blue-500"
            >
              <div className="mb-4 flex justify-center">
                <img
                  src="/base-de-datos.png"
                  alt="Tables"
                  className="w-16 h-16"
                />
              </div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                Explorar tablas
              </h2>
              <p className="text-gray-600">
                Examina y explora las tablas generadas en PostgreSQL
              </p>
            </Link>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              ¿Qué se está ejecutando en el proceso ETL?
            </h3>
            <div className="space-y-4 text-gray-600">
              <div className="flex items-start">
                <span className="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">
                  1
                </span>
                <div className="text-left">
                  <p className="font-medium text-gray-800">Filtrado de cursos</p>
                  <p className="text-sm">Se eliminan los ramos de la línea de Álgebra (Introducción al Álgebra, Álgebra, Matemática para la Computación I y II).</p>
                </div>
              </div>
              <div className="flex items-start">
                <span className="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">
                  2
                </span>
                <div className="text-left">
                  <p className="font-medium text-gray-800">Clasificación por prueba realizada</p>
                  <p className="text-sm">Se agrupan las filas según el tipo de prueba rendida por el estudiante</p>
                </div>
              </div>
              <div className="flex items-start">
                <span className="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">
                  3
                </span>
                <div className="text-left">
                  <p className="font-medium text-gray-800">Asignación de identificadores numéricos</p>
                  <p className="text-sm">Se le asignan identificadores únicos a los estudiantes mediante coincidencias entre columnas de resultados, permitiendo vincular registros de un mismo estudiante.</p>
                </div>
              </div>
              <div className="flex items-start">
                <span className="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">
                  4
                </span>
                <div className="text-left">
                  <p className="font-medium text-gray-800">Exportación a PostgreSQL</p>
                  <p className="text-sm">Guarda los datos ya procesados en la base de datos previamente creada</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
