import os
import re

def print_leads():
    notes_path = "memory/daily_notes.md"
    
    if not os.path.exists(notes_path):
        print("❌ Error: No se encuentra la base de datos de leads.")
        return

    print("\n" + "="*60)
    print(" 📡 FELIX-Z: RADAR DE PROSPECTOS (ALLHUB) ".center(60, " "))
    print("="*60)

    leads_found = 0
    with open(notes_path, "r", encoding="utf-8") as f:
        content = f.read()
        
        # Expresión regular para capturar los detalles de cada lead
        # [20:15:00] [SALES] Lead L-01 (startup_guy) -> ESPAÑOL. Resonancia: 0.94.
        pattern = r"\[(.*?)\] \[SALES\] Lead (L-\d+) \((.*?)\) -> (.*?)\. Resonancia: (.*?)\."
        matches = re.findall(pattern, content)

        for time, id, user, lang, res in matches:
            leads_found += 1
            res_val = float(res)
            
            # Formato visual según la resonancia
            status_icon = "🔥 CRÍTICO" if res_val > 0.9 else "✅ ALTO"
            
            print(f"🆔 ID: {id} | {status_icon}")
            print(f"👤 Usuario: {user}")
            print(f"🌍 Idioma: {lang}")
            print(f"📊 Resonancia: {res}")
            print(f"📅 Hora: {time}")
            print("-" * 60)

    if leads_found == 0:
        print("\n[!] No se han detectado leads en el último ciclo.")
    else:
        print(f"\n✨ Total de oportunidades detectadas: {leads_found}")
        print("🚀 URL Activa: https://allhub-mvp.vercel.app/")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    print_leads()
