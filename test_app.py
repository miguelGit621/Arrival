import pytest
from app import GeoAlarm

# Coordenadas de teste (exemplo: Estação da Sé, SP)
TARGET_LAT = -23.550388
TARGET_LON = -46.633911

@pytest.fixture
def alarm():
    """Instancia um alarme com raio de 500 metros (0.5 km)."""
    return GeoAlarm(target_lat=TARGET_LAT, target_lon=TARGET_LON, radius_km=0.5)

def test_far_away_location_does_not_trigger(alarm):
    """Testa se o alarme PERMANECE DESLIGADO quando o usuário está longe."""
    # Coordenada a ~3km de distância (ex: Avenida Paulista)
    current_lat = -23.561414
    current_lon = -46.655881
    
    assert alarm.check_location(current_lat, current_lon) is False

def test_near_location_triggers_alarm(alarm):
    """Testa se o alarme DISPARA quando o usuário entra no raio delimitado."""
    # Coordenada bem próxima da estação (~200 metros)
    current_lat = -23.551000
    current_lon = -46.633500
    
    assert alarm.check_location(current_lat, current_lon) is True

def test_alarm_does_not_trigger_if_inactive(alarm):
    """Testa se o alarme respeita o estado desativado."""
    alarm.is_active = False
    current_lat = -23.551000
    current_lon = -46.633500
    
    assert alarm.check_location(current_lat, current_lon) is False
  
