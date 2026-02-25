import os
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PolicyDecision:
    allowed: bool
    reasons: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)


class PolicyEngine:
    def __init__(self, notes_path: str = "memory/daily_notes.md"):
        self.notes_path = notes_path

    def count_pending_tasks(self) -> int:
        if not os.path.exists(self.notes_path):
            return 0
        with open(self.notes_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Count explicit TODO markers
        return len(re.findall(r"^\s*-\s*\[TODO\]\s+.+$", content, re.MULTILINE))

    def gate_global(self, e_value: float, pending_tasks: int, is_financial: bool) -> PolicyDecision:
        reasons = []
        required = []

        if e_value > 0.8:
            reasons.append("E > 0.8 (alta entropía).")
            required.append("Solicitar confirmación manual.")

        if pending_tasks > 3:
            reasons.append("Más de 3 tareas pendientes.")
            required.append("Consolidar antes de nuevas acciones.")

        if is_financial:
            reasons.append("Operación financiera requiere aprobación manual.")
            required.append("Bloqueo financiero activo.")

        return PolicyDecision(allowed=(len(reasons) == 0), reasons=reasons, required_actions=required)

    def gate_b2b_leads(
        self,
        resonance: float,
        has_verified_contact: bool,
        rejections_24h: int,
        sector: Optional[str] = None,
    ) -> PolicyDecision:
        reasons = []
        required = []

        if not has_verified_contact:
            reasons.append("Sin contacto verificado.")

        if resonance < 0.75:
            required.append("Solo primer toque; no hacer follow-up.")

        if rejections_24h >= 2:
            reasons.append("2 rechazos en 24h.")
            required.append("Pausar outreach 6h.")

        if sector is not None:
            preferred = {"agencia", "agencias", "saas b2b", "consultora", "consultoras"}
            if sector.strip().lower() not in preferred:
                required.append("Prioridad baja (sector no preferente).")

        return PolicyDecision(allowed=(len(reasons) == 0), reasons=reasons, required_actions=required)

    def gate_microservices(
        self,
        has_budget: bool,
        has_sponsor: bool,
        scope_defined: bool,
        critical_integration: bool,
    ) -> PolicyDecision:
        reasons = []
        required = []

        if not (has_budget or has_sponsor):
            reasons.append("Sin presupuesto ni sponsor.")

        if critical_integration:
            required.append("Discovery pagado obligatorio.")

        if not scope_defined:
            required.append("Exigir definición de alcance (máx 2 interacciones).")

        return PolicyDecision(allowed=(len(reasons) == 0), reasons=reasons, required_actions=required)

    def gate_allhub(
        self,
        hiring_active: bool,
        role: Optional[str],
        onboarding_weeks: Optional[float],
        expressed_interest: bool,
    ) -> PolicyDecision:
        reasons = []
        required = []

        if not hiring_active:
            required.append("Prioridad baja (no hay contratación activa).")

        if role is not None and role.strip().lower() in {"hr director", "people ops"}:
            required.append("Subir prioridad.")

        if onboarding_weeks is not None and onboarding_weeks <= 2:
            reasons.append("Dolor no evidente (onboarding <= 2 semanas).")

        if expressed_interest:
            required.append("Ofrecer piloto 30 días.")

        return PolicyDecision(allowed=(len(reasons) == 0), reasons=reasons, required_actions=required)
