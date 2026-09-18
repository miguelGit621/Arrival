import math
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from plyer import gps, notification, vibration, tts
from geopy.geocoders import Nominatim


class MobileGeoAlarm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        
        self.target_lat = None
        self.target_lon = None
        self.radius_km = 0.5
        self.is_active = False

        # Interface do App
        self.add_widget(Label(text="📍 Alarme de Geolocalização", font_size='22sp', bold=True))

        self.input_destination = TextInput(
            hint_text="Digite o endereço ou local de destino",
            multiline=False, size_hint_y=None, height=100
        )
        self.add_widget(self.input_destination)

        self.input_radius = TextInput(
            hint_text="Raio do alarme em metros (padrão: 500)",
            text="500", multiline=False, size_hint_y=None, height=100
        )
        self.add_widget(self.input_radius)

        self.btn_start = Button(
            text="Ativar Alarme GPS", background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=None, height=120
        )
        self.btn_start.bind(on_press=self.toggle_alarm)
        self.add_widget(self.btn_start)

        self.lbl_status = Label(
            text="Status: Aguardando configuração...",
            font_size='16sp', halign='center'
        )
        self.add_widget(self.lbl_status)

    def geocode_destination(self, address_text):
        """Converte texto do endereço em coordenadas (Latitude / Longitude)."""
        try:
            geolocator = Nominatim(user_agent="mobile_geo_alarm_app")
            location = geolocator.geocode(address_text)
            if location:
                return location.latitude, location.longitude, location.address
        except Exception as e:
            print(f"Erro ao buscar endereço: {e}")
        return None, None, None

    def toggle_alarm(self, instance):
        if not self.is_active:
            address = self.input_destination.text.strip()
            if not address:
                self.lbl_status.text = "⚠️ Por favor, digite um destino!"
                return

            self.lbl_status.text = "🔍 Buscando localização do destino..."
            lat, lon, full_addr = self.geocode_destination(address)

            if not lat:
                self.lbl_status.text = "❌ Destino não encontrado."
                return

            self.target_lat = lat
            self.target_lon = lon
            
            try:
                self.radius_km = float(self.input_radius.text) / 1000.0
            except ValueError:
                self.radius_km = 0.5

            # Inicia escuta do hardware de GPS do celular
            try:
                gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
                gps.start(minTime=3000, minDistance=5)  # Atualiza a cada 3 segundos ou 5 metros
                self.is_active = True
                self.btn_start.text = "Desativar Alarme"
                self.btn_start.background_color = (0.8, 0.2, 0.2, 1)
                self.lbl_status.text = f"✅ Monitorando GPS!\nDestino: {full_addr[:40]}..."
            except Exception as e:
                self.lbl_status.text = f"⚠️ Erro ao acessar GPS: {e}\n(Permissão concedida?)"
        else:
            self.stop_alarm()

    def stop_alarm(self):
        """Para o GPS e desativa o monitoramento."""
        try:
            gps.stop()
        except Exception:
            pass
        self.is_active = False
        self.btn_start.text = "Ativar Alarme GPS"
        self.btn_start.background_color = (0.2, 0.7, 0.3, 1)
        self.lbl_status.text = "Status: Alarme desativado."

    def calculate_distance(self, current_lat, current_lon):
        """Calcula a distância até o destino em km (Haversine)."""
        R = 6371.0
        dlat = math.radians(current_lat - self.target_lat)
        dlon = math.radians(current_lon - self.target_lon)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(self.target_lat)) *
             math.cos(math.radians(current_lat)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def on_gps_location(self, **kwargs):
        """Callback acionado automaticamente a cada atualização real do GPS do celular."""
        current_lat = kwargs.get('lat')
        current_lon = kwargs.get('lon')

        if not current_lat or not current_lon:
            return

        dist_km = self.calculate_distance(current_lat, current_lon)
        dist_m = round(dist_km * 1000)

        self.lbl_status.text = f"📍 Distância atual: {dist_m} metros"

        # Dispara aviso sonoro e vibratório ao entrar no raio
        if dist_km <= self.radius_km:
            self.trigger_alert()

    def on_gps_status(self, general_status, status_message):
        print(f"Status do GPS: {general_status} - {status_message}")

    def trigger_alert(self):
        """Emite vibração, notificação no celular e voz ao chegar."""
        self.lbl_status.text = "🚨 VOCÊ CHEGOU AO DESTINO! ACORDE!"
        
        # 1. Notificação nativa no topo da tela do celular
        try:
            notification.notify(
                title="Chegou ao destino!",
                message="Você está dentro do raio do seu ponto de desembarque!"
            )
        except Exception:
            pass

        # 2. Vibra o celular por 3 segundos
        try:
            vibration.vibrate(3)
        except Exception:
            pass

        # 3. Síntese de Voz (Fala pelo alto-falante)
        try:
            tts.speak("Atenção! Você está chegando ao seu destino. Hora de descer!")
        except Exception:
            pass

        self.stop_alarm()


class GeoAlarmMobileApp(App):
    def build(self):
        return MobileGeoAlarm()


if __name__ == '__main__':
    GeoAlarmMobileApp().run()
