import time
import os
import random
from datetime import datetime
from heartbeat_zira import FelixHeartbeat
from google_places_leads import search_leads, save_to_csv
from gmail_outreach import send_outreach_email

# CONFIGURACIÓN DE GIRA MUNDIAL
CITIES = [
    "London, UK", "Berlin, Germany", "New York, USA", 
    "San Francisco, USA", "Tokyo, Japan", "Singapore", "Sydney, Australia"
]

class NightWatch:
    def __init__(self):
        self.hb = FelixHeartbeat()
        self.places_requests_today = 0
        self.max_places = 200
        self.start_date = datetime.now().date()

    def run_forever(self):
        print("🚀 FELIX-Z: INICIANDO GUARDIA NOCTURNA GLOBAL")
        print("------------------------------------------")
        
        while True:
            # Resetear cuota si es un nuevo día
            if datetime.now().date() > self.start_date:
                print("☀️ Nuevo día detectado. Reseteando cuota de Google Places.")
                self.places_requests_today = 0
                self.start_date = datetime.now().date()

            # 1. LATIDO: Verificar estado del sistema
            self.hb.pulse()

            # 2. BÚSQUEDA: ¿Places o Free?
            if self.places_requests_today < self.max_places:
                city = random.choice(CITIES)
                print(f"🌍 Felix está en {city}. Buscando leads premium...")
                query = f"SaaS startups in {city}"
                leads = search_leads(query)
                save_to_csv(leads)
                self.places_requests_today += len(leads)
                print(f"📊 Cuota Places hoy: {self.places_requests_today}/{self.max_places}")
            else:
                print("🌙 Cuota de Places agotada. Entrando en 'Modo Free' (LinkedIn/Web)...")
                # Aquí podrías añadir lógica de scraping gratuito
                time.sleep(600) # Descansa más en modo free

            # 3. ACCIÓN: Procesar y Enviar
            # (Simplificado: toma los últimos leads nuevos y envía)
            # Nota: En una versión real, aquí filtraríamos por resonancia > 0.8
            
            print("⏳ Esperando 15 minutos para el próximo pulso...")
            time.sleep(900) # Espera 15 min entre latidos

if __name__ == "__main__":
    watch = NightWatch()
    watch.run_forever()
