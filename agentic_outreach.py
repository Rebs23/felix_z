import argparse
import csv
import os
from datetime import datetime
from typing import Dict, List

from policy_engine import PolicyEngine


def load_leads(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_leads(path: str, leads: List[Dict[str, str]]) -> None:
    if not leads:
        return
    fieldnames = list(leads[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)


def now_ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_message(lead: Dict[str, str]) -> str:
    name = lead.get("name", "").strip() or "there"
    company = lead.get("company", "").strip()
    pain = lead.get("pain", "").strip()
    company_clause = f" at {company}" if company else ""
    pain_clause = f" noticed {pain}" if pain else " noticed support backlog pressure"

    lines = [
        f"Hi {name}, quick note{company_clause}.",
        f"I{pain_clause}.",
        "We deploy an agentic support desk that cuts repetitive tickets and speeds response times.",
        "Open to a 15-min chat this week to see if it fits?",
    ]
    return " ".join(lines)


def append_review(outbox_path: str, lead: Dict[str, str], message: str, actions: List[str]) -> None:
    os.makedirs(os.path.dirname(outbox_path), exist_ok=True)
    with open(outbox_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(f"## Lead {lead.get('id','')}\n")
        f.write(f"Name: {lead.get('name','')}\n")
        f.write(f"Title: {lead.get('title','')}\n")
        f.write(f"Company: {lead.get('company','')}\n")
        f.write("Channel: LinkedIn (manual send)\n")
        f.write("Message:\n")
        f.write(f"\"{message}\"\n")
        if actions:
            f.write("Actions:\n")
            for a in actions:
                f.write(f"- {a}\n")


def append_daily_log(notes_path: str, line: str) -> None:
    os.makedirs(os.path.dirname(notes_path), exist_ok=True)
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write(f"\n- **[{now_ts()}] [SALES]** {line}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leads", default="memory/leads.csv")
    parser.add_argument("--outbox", default="memory/review_queue.md")
    parser.add_argument("--notes", default="memory/daily_notes.md")
    parser.add_argument("--max", type=int, default=10)
    parser.add_argument("--e", type=float, default=0.0)
    parser.add_argument("--mark-queued", action="store_true")
    args = parser.parse_args()

    policy = PolicyEngine(notes_path=args.notes)
    pending = policy.count_pending_tasks()
    global_gate = policy.gate_global(args.e, pending, is_financial=False)
    if not global_gate.allowed:
        print("[POLICY] Acciones bloqueadas por reglas globales.")
        for r in global_gate.reasons:
            print(f"[POLICY] Razón: {r}")
        for a in global_gate.required_actions:
            print(f"[POLICY] Requerido: {a}")
        return

    leads = load_leads(args.leads)
    if not leads:
        print("[LEADS] No se encontraron leads.")
        return

    queued = 0
    for lead in leads:
        if queued >= args.max:
            break

        status = lead.get("status", "").strip().lower()
        if status in {"sent", "queued"}:
            continue

        resonance = float(lead.get("resonance", "0") or 0)
        rejections = int(lead.get("rejections_24h", "0") or 0)
        sector = lead.get("sector", "") or None
        has_verified_contact = bool(lead.get("email", "").strip() or lead.get("linkedin", "").strip())

        gate = policy.gate_b2b_leads(
            resonance=resonance,
            has_verified_contact=has_verified_contact,
            rejections_24h=rejections,
            sector=sector,
        )
        if not gate.allowed:
            append_daily_log(args.notes, f"Lead {lead.get('id','')} bloqueado por policy.")
            continue

        message = build_message(lead)
        append_review(args.outbox, lead, message, gate.required_actions)
        append_daily_log(args.notes, f"Lead {lead.get('id','')} encolado para revisión manual (LinkedIn).")
        if args.mark_queued:
            lead["status"] = "queued"
        queued += 1

    if args.mark_queued:
        save_leads(args.leads, leads)

    print(f"[OUTREACH] Encolados: {queued}")


if __name__ == "__main__":
    main()
