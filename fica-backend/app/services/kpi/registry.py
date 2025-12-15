from typing import Callable, Dict, Any
from sqlalchemy.orm import Session

from app.services.kpi.kpi_1_1 import calculate_kpi_1_1
from app.services.kpi.kpi_1_2_1 import calculate_kpi_1_2_1
from app.services.kpi.kpi_1_2_2 import calculate_kpi_1_2_2
from app.services.kpi.kpi_1_3 import calculate_kpi_1_3
from app.services.kpi.kpi_1_4 import calculate_kpi_1_4
from app.services.kpi.kpi_1_5 import calculate_kpi_1_5
from app.services.kpi.kpi_1_6 import calculate_kpi_1_6
from app.services.kpi.kpi_1_7 import calculate_kpi_1_7
from app.services.kpi.kpi_1_8 import calculate_kpi_1_8


KpiFn = Callable[[Session, int], Dict[str, Any]]

KPI_REGISTRY: Dict[str, KpiFn] = {
    "1.1"   : calculate_kpi_1_1,
    "1.2.1" : calculate_kpi_1_2_1,
    "1.2.2" : calculate_kpi_1_2_2,
    "1.3"   : calculate_kpi_1_3,
    "1.4"   : calculate_kpi_1_4,
    "1.5"   : calculate_kpi_1_5,
    "1.6"   : calculate_kpi_1_6,
    "1.7"   : calculate_kpi_1_7,
    "1.8"   : calculate_kpi_1_8,
}
