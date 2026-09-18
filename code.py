import math
import time
import sys
import os
import requests
from geopy.geocoders import Nominatim

class GeoAlarmSound:
    def __init__(self, destination_name: str, target_lat: float, target_lon: float, radius_km: float = 0.5):
        self.destination_name = destination_name
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.radius_km = radius_km
        self.is_active = True

    @staticmethod
    def get_current_location():
        """Obtém a localização aproximada atual baseada no IP público."""
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            if 'latitude' in data and 'longitude' in data:
                return data['latitude'], data['longitude'], f"{data.get('city', '')}, {data.get('region', '')}"
        except Exception as e:
            print(f"⚠️ Erro ao obter localização por IP: {e}")
        return None, None, None

    @staticmethod
    def geocode_address(address: str):
        """Converte um nome de local ou endereço em coordenadas (Latitude, Longitude)."""
        geolocator = Nominatim(user_agent="geo_alarm_app")
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude, location.address
        except Exception as e:
            print(f"⚠️ Erro na busca de endereço: {e}")
        return None, None, None

    def calculate_distance(self, current_lat: float, current_lon: float) -> float:
        """Calcula a distância em quilômetros usando a Fórmula de Haversine."""
        R = 6371.0  # Raio médio da Terra em km
        
        dlat = math.radians(current_lat - self.target_lat)
        dlon = math.radians(current_lon - self.target_lon)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(self.target_lat)) * 
             math.cos(math.radians(current_lat)) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def play_alarm_sound(self):
        """Emite um alerta sonoro contínuo quando o alarme é disparado."""
        print("\n🔊 ********************************** 🔊")
        print("🚨 ALARME DISPARADO! VOCÊ CHEGOU AO SEU DESTINO! 🚨")
        print("🔊 ********************************** 🔊\n")

        # Tenta emitir som conforme o Sistema Operacional
        for _ in range(10):  # Toca 10 vezes
            if os.name == 'nt':  # Windows
                import winsound
                winsound.Beep(2500, 700)  # Frequência: 2500Hz, Duração: 700ms
            else:  # Linux / macOS
                sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(0.5)


def main():
    print("==============================================")
    print("      GPS ALARM - DETECÇÃO & AVISO SONORO     ")
    print("==============================================\n")

    # 1. Obtém localização inicial
    print("🔍 Obter localização atual via IP...")
    curr_lat, curr_lon, city_info = GeoAlarmSound.get_current_location()

    if curr_lat and curr_lon:
        print(f"📍 Sua localização aproximada atual: {city_info} ({curr_lat}, {curr_lon})\n")
    else:
        print("⚠️ Não foi possível obter sua localização por IP.")
        curr_lat = float(input("Digite sua latitude atual: "))
        curr_lon = float(input("Digite sua longitude atual: "))

    # 2. Configura o Destino
    dest_input = input("Digite o nome ou endereço do destino (ex: Estação da Sé, São Paulo): ")
    target_lat, target_lon, full_address = GeoAlarmSound.geocode_address(dest_input)

    if not target_lat:
        print("❌ Não foi possível encontrar o endereço especificado.")
        return

    print(f"🎯 Destino encontrado: {full_address}")
    print(f"   Coordenadas do Destino: ({target_lat}, {target_lon})")

    radius_input = input("Digite o raio do alarme em metros (padrão: 500m): ")
    radius_km = (float(radius_input) / 1000.0) if radius_input.strip() else 0.5

    alarm = GeoAlarmSound(
        destination_name=dest_input,
        target_lat=target_lat,
        target_lon=target_lon,
        radius_km=radius_km
    )

    # 3. Monitoramento e Simulação de Trajeto
    print(f"\n✅ Monitoramento ativo para '{dest_input}' (Raio: {radius_km * 1000}m).")
    print("Insira novas coordenadas de localização conforme se desloca (ou digite 'auto' para checar IP atual novamente, ou 'sair'):\n")

    sim_lat, sim_lon = curr_lat, curr_lon

    while alarm.is_active:
        dist = alarm.calculate_distance(sim_lat, sim_lon)
        print(f"📍 Distância atual até o destino: {round(dist, 3)} km ({round(dist * 1000)} metros)")

        if dist <= alarm.radius_km:
            alarm.play_alarm_sound()
            alarm.is_active = False
            break

        user_cmd = input("\n👉 Digite 'lat, lon' atuais, 'auto' para re-checar IP, ou 'sair': ").strip()

        if user_cmd.lower() == 'sair':
            print("Alarme cancelado.")
            break
        elif user_cmd.lower() == 'auto':
            sim_lat, sim_lon, _ = GeoAlarmSound.get_current_location()
        else:
            try:
                coords = [float(c.strip()) for c in user_cmd.split(',')]
                sim_lat, sim_lon = coords[0], coords[1]
            except (ValueError, IndexError):
                print("⚠️ Entrada inválida! Exemplo: -23.5503, -46.6339")


if __name__ == "__main__":
    main()
    
