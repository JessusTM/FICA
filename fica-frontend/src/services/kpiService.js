import apiClient from '../config/api';

/**
 * Obtiene la lista de KPIs disponibles
 */
export const getKPIList = async () => {
  try {
    const response = await apiClient.get('/kpi/list');
    return response.data;
  } catch (error) {
    console.error('Error fetching KPI list:', error);
    throw error;
  }
};

/**
 * Obtiene los datos de un KPI específico
 * @param {string} kpiId - ID del KPI (ej: "1.1", "1.2.1")
 * @param {number} cohorte - Año de la cohorte (opcional, por defecto 2022)
 */
export const getKPIData = async (kpiId, cohorte = 2022) => {
  try {
    const response = await apiClient.get(`/kpi/${kpiId}`, {
      params: { cohorte }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching KPI ${kpiId}:`, error);
    throw error;
  }
};

