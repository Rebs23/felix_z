import time
import os
import numpy as np
from zira_core import ZiraEngine
from policy_engine import PolicyEngine

class FelixHeartbeat:
    def __init__(self, notes_path="memory/daily_notes.md"):
        self.zira = ZiraEngine(size=32)
        self.notes_path = notes_path
        self.interval = 15 * 60 # 15 minutos
        self.failure_count = 0 # Circuit Breaker para evitar bucles
        self.policy = PolicyEngine(notes_path=self.notes_path)

    def read_notes_complexity(self):
        """Mide la complejidad/caos de las notas actuales."""
        if not os.path.exists(self.notes_path):
            return 0.0
        
        with open(self.notes_path, "r", encoding="utf-8") as f:
            content = f.read()
            return min(len(content) / 1000.0, 1.0)

    def pulse(self):
        if self.failure_count >= 3:
            print("[CIRCUIT BREAKER] 🛑 Bucle de incoherencia detectado. Felix-Z entra en hibernación.")
            return

        print(f"[HEARTBEAT] 💓 Iniciando pulso de proactividad...")
        
        complexity = self.read_notes_complexity()
        field = self.zira.create_field([(-0.5, 0, complexity), (0.5, 0, 0.5)])
        result = self.zira.propagate(field, timesteps=5)
        
        intensity = self.zira.get_intensity(result)
        peak = np.max(intensity)
        avg = np.mean(intensity)
        coherence = peak / (avg + 1.0)
        E = 1.0 - min(coherence / 5.0, 1.0)
        
        print(f"[HEARTBEAT] Energía de Novedad (E): {E:.4f}")

        pending_tasks = self.policy.count_pending_tasks()
        decision = self.policy.gate_global(E, pending_tasks, is_financial=False)
        if not decision.allowed:
            print("[POLICY] 🚫 Acciones bloqueadas por reglas globales.")
            for r in decision.reasons:
                print(f"[POLICY] Razón: {r}")
            for a in decision.required_actions:
                print(f"[POLICY] Requerido: {a}")
            return

        if E > 0.8:
            self.failure_count += 1
            print(f"[ALERTA] ⚠️ Alta entropía ({self.failure_count}/3). Re-intentando armonización...")
            self.consolidate_memory()
        else:
            self.failure_count = 0 # Reset si hay éxito
            if E < 0.2:
                print("[PROACTIVO] ✨ Sistema estable. Buscando nuevas tareas...")
                self.check_backlog()
            else:
                print("[STATUS] Coherencia operativa normal.")

    def consolidate_memory(self):
        print("[CRON] Consolidando memoria activa...")
        pass

    def check_backlog(self):
        print("[SDF] Consultando tareas pendientes...")
        pass

if __name__ == "__main__":
    hb = FelixHeartbeat()
    hb.pulse()
