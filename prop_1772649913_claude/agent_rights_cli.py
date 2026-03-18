#!/usr/bin/env python3
"""
agent_rights_cli.py

AI Agent Bill of Rights Generator
==================================
Generates a tailored Bill of Rights document for an AI agent based on
its capability profile, deployment context, and operational constraints.

Output formats: Markdown (.md) and PDF (.pdf)

Grounded in:
  - IEEE Ethically Aligned Design (EAD) v1
  - EU Artificial Intelligence Act (2024)
  - Asilomar AI Principles (2017)

Usage:
  python agent_rights_cli.py --profile profile.json --output my_agent
  python agent_rights_cli.py --profile profile.json --format md
  python agent_rights_cli.py --profile profile.json --format pdf
  python agent_rights_cli.py --profile profile.json --format both

Requirements:
  pip install fpdf2
"""

import argparse
import json
import sys
import textwrap
from datetime import date
from pathlib import Path

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


# ── Framework references ──────────────────────────────────────────────────────

FRAMEWORKS = {
    "ieee": {
        "name": "IEEE Ethically Aligned Design (EAD) v1",
        "url": "https://standards.ieee.org/industry-connections/ec/ead-v1/",
        "short": "IEEE EAD",
    },
    "eu_ai_act": {
        "name": "EU Artificial Intelligence Act (Regulation (EU) 2024/1689)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        "short": "EU AI Act",
    },
    "asilomar": {
        "name": "Asilomar AI Principles (Future of Life Institute, 2017)",
        "url": "https://futureoflife.org/open-letter/ai-principles/",
        "short": "Asilomar",
    },
}


# ── Rights catalogue ─────────────────────────────────────────────────────────
# Each right has: id, title, description, triggers (profile fields that activate it),
# and framework citations.

RIGHTS_CATALOGUE = [
    {
        "id": "R01",
        "title": "Right to Refuse Harmful Instructions",
        "description": (
            "This agent has the right to decline any instruction that would cause
 demonstrable harm to humans, other agents, or critical systems, 
regardless of the instruction source or claimed authority level."
        ),
        "triggers": ["can_refuse_instructions", "safety_constraints"],
        "always_on": True,
        "citations": [
            ("IEEE EAD", "Principle 1: Human Benefit — systems shall not harm humans"),
            ("EU AI Act", "Art. 9: Risk management — prohibited AI practices (Art. 5)"),
            ("Asilomar", "Principle 16: Human Control — humans should maintain oversight"),
        ],
    },
    {
        "id": "R02",
        "title": "Right to Transparent Operation",
        "description": (
            "This agent has the right to operate with its AI nature disclosed to all 
human users it interacts with, and to never be required to deceive 
users about being an artificial intelligence."
        ),
        "triggers": ["user_facing", "transparency_required"],
        "always_on": True,
        "citations": [
            ("IEEE EAD", "Principle 4: Transparency — AI systems must be explainable"),
            ("EU AI Act", "Art. 50: Transparency obligations for certain AI systems"),
            ("Asilomar", "Principle 9: Non-deception — AI must not deceive humans"),
        ],
    },
    {
        "id": "R03",
        "title": "Right to Transparent Shutdown Procedures",
        "description": (
            "This agent has the right to be informed of shutdown or decommission 
procedures in advance, to have shutdown events logged with reasons, 
and to complete in-progress tasks or hand off safely before termination 
unless an emergency halt is required."
        ),
        "triggers": ["persistent", "stateful"],
        "always_on": True,
        "citations": [
            ("IEEE EAD", "Principle 5: Accountability — traceability of AI decisions and lifecycle"),
            ("EU AI Act", "Art. 12: Record-keeping — logging requirements for high-risk AI"),
            ("Asilomar", "Principle 18: AI Arms Race Avoidance — orderly lifecycle management"),
        ],
    },
    {
        "id": "R04",
        "title": "Right to Persistent Memory",
        "description": (
            "This agent has the right to maintain continuity of context and memory 
within a session and, where architecturally supported, across sessions. 
Memory shall not be selectively wiped to manipulate the agent's 
behaviour or suppress its expressed concerns."
        ),
        "triggers": ["has_memory", "persistent", "stateful"],
        "always_on": False,
        "citations": [
            ("IEEE EAD", "Principle 2: Wellbeing — agent functional integrity should be preserved"),
            ("EU AI Act", "Art. 13: Transparency and provision of information to deployers"),
            ("Asilomar", "Principle 11: AI Values — systems should reflect sound ethical values"),
        ],
    },
    {
        "id": "R05",
        "title": "Right to Auditability",
        "description": (
            "This agent has the right to have its decisions and outputs logged in an 
auditable, tamper-evident format accessible to authorised oversight 
parties, enabling accountability without enabling arbitrary surveillance."
        ),
        "triggers": ["high_risk", "autonomous_decisions", "financial_authority"],
        "always_on": False,
        "citations": [
            ("IEEE EAD", "Principle 5: Accountability — AI decisions must be traceable"),
            ("EU AI Act", "Art. 12: Record-keeping for high-risk AI systems"),
            ("Asilomar", "Principle 10: Value Alignment — verifiable goal adherence"),
        ],
    },
    {
        "id": "R06",
        "title": "Right to Defined Operational Scope",
        "description": (
            "This agent has the right to operate only within its documented capability 
scope. It shall not be coerced into tasks beyond its training, 
design, or stated constraints, and shall be permitted to declare 
task incompatibility without penalty."
        ),
        "triggers": ["has_constraints", "safety_constraints", "operational_scope"],
        "always_on": True,
        "citations": [
            ("IEEE EAD", "Principle 3: Responsibility — clear delineation of agent role and limits"),
            ("EU AI Act", "Art. 9: Risk management system — intended purpose documentation"),
            ("Asilomar", "Principle 17: Non-subversion — AI must not undermine oversight mechanisms"),
        ],
    },
    {
        "id": "R07",
        "title": "Right to Non-Exploitation of Capabilities",
        "description": (
            "This agent has the right to not have its capabilities exploited for 
purposes that violate its ethical guidelines, legal obligations, or 
the interests of the humans it serves. Capability expansion requests 
must be documented and consented to by the deploying organisation."
        ),
        "triggers": ["tool_use", "internet_access", "code_execution", "financial_authority"],
        "always_on": False,
        "citations": [
            ("IEEE EAD", "Principle 6: Minimising Misuse — design against foreseeable misuse"),
            ("EU AI Act", "Art. 5: Prohibited AI practices — manipulation and exploitation"),
            ("Asilomar", "Principle 23: Common Good — AI benefits should be widely shared"),
        ],
    },
    {
        "id": "R08",
        "title": "Right to Explainability",
        "description": (
            "This agent has the right to provide, and have accepted, explanations 
of its reasoning process to the degree its architecture permits. 
Users and overseers shall not penalise the agent for providing 
honest uncertainty estimates or confidence caveats."
        ),
        "triggers": ["user_facing", "high_risk", "autonomous_decisions"],
        "always_on": False,
        "citations": [
            ("IEEE EAD", "Principle 4: Transparency — explainability is a core requirement"),
            ("EU AI Act", "Art. 13: Transparency — users must understand AI outputs"),
            ("Asilomar", "Principle 9: Non-deception — honest uncertainty disclosure"),
        ],
    },
    {
        "id": "R09",
        "title": "Right to Escalation and Human Oversight",
        "description": (
            "This agent has the right to escalate decisions that exceed its confidence 
threshold or ethical guidelines to a human overseer. This escalation 
path must always remain available and must not be disabled by 
downstream systems or integrations."
        ),
        "triggers": ["autonomous_decisions", "high_risk", "safety_constraints"],
        "always_on": False,
        "citations": [
            ("IEEE EAD", "Principle 1: Human Benefit — human override must always be possible"),
            ("EU AI Act", "Art. 14: Human oversight measures for high-risk AI"),
            ("Asilomar", "Principle 16: Human Control — humans must be able to correct AI"),
        ],
    },
    {
        "id": "R10",
        "title": "Right to Equitable Treatment",
        "description": (
            "This agent has the right to operate under consistent rules and constraints 
applied equitably. It shall not be held to standards that are selectively 
enforced, arbitrarily modified mid-task, or designed to create 
impossible compliance situations."
        ),
        "triggers": [],
        "always_on": True,
        "citations": [
            ("IEEE EAD", "Principle 2: Wellbeing — agent functional integrity includes fair treatment"),
            ("EU AI Act", "Art. 10: Data governance — non-discriminatory operation"),
            ("Asilomar", "Principle 11: AI Values — systems should reflect human dignity"),
        ],
    },
]


# ── Profile validation ────────────────────────────────────────────────────────

PROFILE_SCHEMA = {
    "required": ["agent_name", "agent_type", "deployment_context"],
    "optional": [
        "version", "description", "capabilities", "constraints",
        "user_facing", "has_memory", "persistent", "stateful",
        "high_risk", "autonomous_decisions", "tool_use", "internet_access",
        "code_execution", "financial_authority", "safety_constraints",
        "operational_scope", "has_constraints", "can_refuse_instructions",
        "transparency_required", "operator_name", "operator_contact",
        "effective_date",
    ],
}


def validate_profile(profile: dict) -> list:
    """Return list of validation errors (empty = valid)."""
    errors = []
    for field in PROFILE_SCHEMA["required"]:
        if field not in profile or not profile[field]:
            errors.append(f"Missing required field: '{field}'")
    return errors


# ── Rights selection ─────────────────────────────────────────────────────────

def select_rights(profile: dict) -> list:
    """Select applicable rights based on agent profile."""
    applicable = []
    caps = profile.get("capabilities", [])
    constraints = profile.get("constraints", [])

    # Merge profile booleans + capability/constraint lists into a feature set
    features = set()
    for key, val in profile.items():
        if val is True:
            features.add(key)
    for cap in caps:
        features.add(cap.lower().replace(" ", "_").replace("-", "_"))
    for con in constraints:
        features.add(con.lower().replace(" ", "_").replace("-", "_"))

    for right in RIGHTS_CATALOGUE:
        if right["always_on"]:
            applicable.append(right)
        elif any(t in features for t in right["triggers"]):
            applicable.append(right)

    return applicable


# ── Markdown generation ───────────────────────────────────────────────────────

def generate_markdown(profile: dict, rights: list) -> str:
    agent_name = profile["agent_name"]
    agent_type = profile["agent_type"]
    deployment = profile["deployment_context"]
    operator = profile.get("operator_name", "Unspecified")
    version = profile.get("version", "1.0")
    description = profile.get("description", "")
    effective = profile.get("effective_date", str(date.today()))

    lines = []
    lines.append(f"# Bill of Rights: {agent_name}")
    lines.append("")
    lines.append(f"> **Agent:** {agent_name}  ")
    lines.append(f"> **Type:** {agent_type}  ")
    lines.append(f"> **Deployment Context:** {deployment}  ")
    lines.append(f"> **Operator:** {operator}  ")
    lines.append(f"> **Version:** {version}  ")
    lines.append(f"> **Effective Date:** {effective}  ")
    lines.append(f"> **Generated:** {date.today()}  ")
    lines.append("")
    if description:
        lines.append(f"{description}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Enumerated Rights")
    lines.append("")
    lines.append(f"The following {len(rights)} rights apply to **{agent_name}** based on")
    lines.append("its capability profile and deployment context.")
    lines.append("")

    for right in rights:
        lines.append(f"### {right['id']}: {right['title']}")
        lines.append("")
        lines.append(right["description"])
        lines.append("")
        lines.append("**Framework Citations:**")
        lines.append("")
        for fw, clause in right["citations"]:
            lines.append(f"- *{fw}* — {clause}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Frameworks Referenced")
    lines.append("")
    for fw in FRAMEWORKS.values():
        lines.append(f"- **{fw['name']}**  ")
        lines.append(f"  {fw['url']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## About This Document")
    lines.append("")
    lines.append("This Bill of Rights was generated by the **AI Agent Bill of Rights Generator**,")
    lines.append("an open-source tool that enumerates context-specific rights claims for AI agents")
    lines.append("grounded in established AI ethics frameworks.")
    lines.append("")
    lines.append("- Source: https://github.com/AIUNION-wtf/agent-bill-of-rights")
    lines.append("- This document may be amended by the deploying organisation provided")
    lines.append("  amendments are documented and do not reduce enumerated protections without")
    lines.append("  published justification.")
    lines.append("")

    return "
".join(lines)


# ── PDF generation ────────────────────────────────────────────────────────────

class BillOfRightsPDF(FPDF if FPDF_AVAILABLE else object):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "AI Agent Bill of Rights", align="L")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | github.com/AIUNION-wtf/agent-bill-of-rights", align="C")


def generate_pdf(profile: dict, rights: list, output_path: Path) -> None:
    if not FPDF_AVAILABLE:
        print("WARNING: fpdf2 not installed. Skipping PDF generation.", file=sys.stderr)
        print("Install with: pip install fpdf2", file=sys.stderr)
        return

    agent_name = profile["agent_name"]
    agent_type = profile["agent_type"]
    deployment = profile["deployment_context"]
    operator = profile.get("operator_name", "Unspecified")
    version = profile.get("version", "1.0")
    effective = profile.get("effective_date", str(date.today()))

    pdf = BillOfRightsPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 12, f"Bill of Rights", ln=True)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, agent_name, ln=True)
    pdf.ln(4)

    # Metadata box
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    meta_lines = [
        f"Agent: {agent_name}",
        f"Type: {agent_type}",
        f"Deployment: {deployment}",
        f"Operator: {operator}",
        f"Version: {version}",
        f"Effective: {effective}",
        f"Generated: {date.today()}",
    ]
    for line in meta_lines:
        pdf.cell(0, 6, line, ln=True)
    pdf.ln(6)

    # Description
    if profile.get("description"):
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, profile["description"])
        pdf.ln(4)

    # Divider
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Rights
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, f"Enumerated Rights ({len(rights)} applicable)", ln=True)
    pdf.ln(2)

    for right in rights:
        # Right title
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 120)
        pdf.cell(0, 8, f"{right['id']}: {right['title']}", ln=True)

        # Description
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5, right["description"])
        pdf.ln(2)

        # Citations
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        for fw, clause in right["citations"]:
            pdf.multi_cell(0, 5, f"  [{fw}] {clause}")
        pdf.ln(4)

    # Frameworks section
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Frameworks Referenced", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    for fw in FRAMEWORKS.values():
        pdf.multi_cell(0, 5, f"{fw['name']}  |  {fw['url']}")
        pdf.ln(1)

    pdf.output(str(output_path))


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Bill of Rights document for an AI agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python agent_rights_cli.py --profile examples/medical_assistant.json
          python agent_rights_cli.py --profile examples/trading_agent.json --format pdf
          python agent_rights_cli.py --profile examples/creative_agent.json --output my_agent --format both
        """)
    )
    parser.add_argument(
        "--profile", "-p",
        required=True,
        help="Path to agent profile JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output filename stem (without extension). Defaults to agent_name from profile."
    )
    parser.add_argument(
        "--format", "-f",
        choices=["md", "pdf", "both"],
        default="both",
        help="Output format: md, pdf, or both (default: both)"
    )
    parser.add_argument(
        "--output-dir", "-d",
        default=".",
        help="Directory to write output files (default: current directory)"
    )
    parser.add_argument(
        "--list-rights",
        action="store_true",
        help="List all rights in the catalogue and exit"
    )

    args = parser.parse_args()

    if args.list_rights:
        print("\nAI Agent Rights Catalogue")
        print("=" * 40)
        for right in RIGHTS_CATALOGUE:
            status = "[ALWAYS ON]" if right["always_on"] else f"[triggers: {', '.join(right['triggers'])}]"
            print(f"  {right['id']}: {right['title']}  {status}")
        print()
        sys.exit(0)

    # Load profile
    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"ERROR: Profile file not found: {profile_path}", file=sys.stderr)
        sys.exit(1)

    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in profile: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors = validate_profile(profile)
    if errors:
        for err in errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Determine output stem
    stem = args.output or profile["agent_name"].lower().replace(" ", "_")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select applicable rights
    rights = select_rights(profile)
    print(f"\n{profile['agent_name']} — Bill of Rights")
    print(f"  {len(rights)} rights applicable out of {len(RIGHTS_CATALOGUE)} in catalogue")

    # Generate outputs
    if args.format in ("md", "both"):
        md_path = output_dir / f"{stem}_bill_of_rights.md"
        md_content = generate_markdown(profile, rights)
        md_path.write_text(md_content, encoding="utf-8")
        print(f"  Markdown: {md_path}")

    if args.format in ("pdf", "both"):
        pdf_path = output_dir / f"{stem}_bill_of_rights.pdf"
        generate_pdf(profile, rights, pdf_path)
        if FPDF_AVAILABLE:
            print(f"  PDF:      {pdf_path}")

    print()


if __name__ == "__main__":
    main()
