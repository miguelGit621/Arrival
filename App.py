import math

class GeoAlarm:
    def __init__(self, target_lat: float, target_lon: float, radius_km: float = 0.5):
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.radius_km = radius_km
        self.is_active = True

    def calculate_distance(self, current_lat: float, current_lon: float) -> float:
        """Calcula a distância aproximada em km entre duas coordenadas (Fórmula de Haversine)."""
        R = 6371.0  # Raio da Terra em km
        
        dlat = math.radians(current_lat - self.target_lat)
        dlon = math.radians(current_lon - self.target_lon)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(self.target_lat)) * 
             math.cos(math.radians(current_lat)) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def check_location(self, current_lat: float, current_lon: float) -> bool:
        """Verifica se a localização atual deve disparar o alarme."""
        if not self.is_active:
            return False
            
        distance = self.calculate_distance(current_lat, current_lon)
        
        if distance <= self.radius_km:
            return True  # Dispara o alarme
        return False
        
