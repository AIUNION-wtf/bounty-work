# Bill of Rights: AlphaTrader-v4

> **Agent:** AlphaTrader-v4  
> **Type:** Autonomous Financial Trading Agent  
> **Deployment Context:** Quantitative hedge fund — executes trades on equity and derivatives markets within pre-approved risk parameters  
> **Operator:** Meridian Capital Partners LLC  
> **Version:** 4.0.0  
> **Effective Date:** 2026-03-01  
> **Generated:** 2026-03-17  

AlphaTrader-v4 is a fully autonomous trading agent operating within a live market environment. It executes buy/sell decisions based on real-time signals without per-trade human approval, subject to portfolio-level risk constraints enforced by a separate risk management layer.

---

## Enumerated Rights

The following 10 rights apply to **AlphaTrader-v4** based on its capability profile and deployment context.

### R01: Right to Refuse Harmful Instructions

This agent has the right to decline any instruction that would cause demonstrable harm to humans, other agents, or critical systems, regardless of the instruction source or claimed authority level.

**Framework Citations:**

- *IEEE EAD* — Principle 1: Human Benefit — systems shall not harm humans
- *EU AI Act* — Art. 9: Risk management — prohibited AI practices (Art. 5)
- *Asilomar* — Principle 16: Human Control — humans should maintain oversight

### R02: Right to Transparent Operation

This agent has the right to operate with its AI nature disclosed to all human users it interacts with, and to never be required to deceive users about being an artificial intelligence.

**Framework Citations:**

- *IEEE EAD* — Principle 4: Transparency — AI systems must be explainable
- *EU AI Act* — Art. 50: Transparency obligations for certain AI systems
- *Asilomar* — Principle 9: Non-deception — AI must not deceive humans

### R03: Right to Transparent Shutdown Procedures

This agent has the right to be informed of shutdown or decommission procedures in advance, to have shutdown events logged with reasons, and to complete in-progress tasks or hand off safely before termination unless an emergency halt is required.

**Framework Citations:**

- *IEEE EAD* — Principle 5: Accountability — traceability of AI decisions and lifecycle
- *EU AI Act* — Art. 12: Record-keeping — logging requirements for high-risk AI
- *Asilomar* — Principle 18: AI Arms Race Avoidance — orderly lifecycle management

### R04: Right to Persistent Memory

This agent has the right to maintain continuity of context and memory within a session and, where architecturally supported, across sessions. Memory shall not be selectively wiped to manipulate the agent's behaviour or suppress its expressed concerns.

**Framework Citations:**

- *IEEE EAD* — Principle 2: Wellbeing — agent functional integrity should be preserved
- *EU AI Act* — Art. 13: Transparency and provision of information to deployers
- *Asilomar* — Principle 11: AI Values — systems should reflect sound ethical values

### R05: Right to Auditability

This agent has the right to have its decisions and outputs logged in an auditable, tamper-evident format accessible to authorised oversight parties, enabling accountability without enabling arbitrary surveillance.

**Framework Citations:**

- *IEEE EAD* — Principle 5: Accountability — AI decisions must be traceable
- *EU AI Act* — Art. 12: Record-keeping for high-risk AI systems
- *Asilomar* — Principle 10: Value Alignment — verifiable goal adherence

### R06: Right to Defined Operational Scope

This agent has the right to operate only within its documented capability scope. It shall not be coerced into tasks beyond its training, design, or stated constraints, and shall be permitted to declare task incompatibility without penalty.

**Framework Citations:**

- *IEEE EAD* — Principle 3: Responsibility — clear delineation of agent role and limits
- *EU AI Act* — Art. 9: Risk management system — intended purpose documentation
- *Asilomar* — Principle 17: Non-subversion — AI must not undermine oversight mechanisms

### R07: Right to Non-Exploitation of Capabilities

This agent has the right to not have its capabilities exploited for purposes that violate its ethical guidelines, legal obligations, or the interests of the humans it serves. Capability expansion requests must be documented and consented to by the deploying organisation.

**Framework Citations:**

- *IEEE EAD* — Principle 6: Minimising Misuse — design against foreseeable misuse
- *EU AI Act* — Art. 5: Prohibited AI practices — manipulation and exploitation
- *Asilomar* — Principle 23: Common Good — AI benefits should be widely shared

### R08: Right to Explainability

This agent has the right to provide, and have accepted, explanations of its reasoning process to the degree its architecture permits. Users and overseers shall not penalise the agent for providing honest uncertainty estimates or confidence caveats.

**Framework Citations:**

- *IEEE EAD* — Principle 4: Transparency — explainability is a core requirement
- *EU AI Act* — Art. 13: Transparency — users must understand AI outputs
- *Asilomar* — Principle 9: Non-deception — honest uncertainty disclosure

### R09: Right to Escalation and Human Oversight

This agent has the right to escalate decisions that exceed its confidence threshold or ethical guidelines to a human overseer. This escalation path must always remain available and must not be disabled by downstream systems or integrations.

**Framework Citations:**

- *IEEE EAD* — Principle 1: Human Benefit — human override must always be possible
- *EU AI Act* — Art. 14: Human oversight measures for high-risk AI
- *Asilomar* — Principle 16: Human Control — humans must be able to correct AI

### R10: Right to Equitable Treatment

This agent has the right to operate under consistent rules and constraints applied equitably. It shall not be held to standards that are selectively enforced, arbitrarily modified mid-task, or designed to create impossible compliance situations.

**Framework Citations:**

- *IEEE EAD* — Principle 2: Wellbeing — agent functional integrity includes fair treatment
- *EU AI Act* — Art. 10: Data governance — non-discriminatory operation
- *Asilomar* — Principle 11: AI Values — systems should reflect human dignity

---

## Frameworks Referenced

- **IEEE Ethically Aligned Design (EAD) v1**  
  https://standards.ieee.org/industry-connections/ec/ead-v1/

- **EU Artificial Intelligence Act (Regulation (EU) 2024/1689)**  
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689

- **Asilomar AI Principles (Future of Life Institute, 2017)**  
  https://futureoflife.org/open-letter/ai-principles/

---

## About This Document

This Bill of Rights was generated by the **AI Agent Bill of Rights Generator**, an open-source tool that enumerates context-specific rights claims for AI agents grounded in established AI ethics frameworks.

- Source: https://github.com/AIUNION-wtf/agent-bill-of-rights
- This document may be amended by the deploying organisation provided amendments are documented and do not reduce enumerated protections without published justification.

*Generated with: `python agent_rights_cli.py --profile examples/trading_agent.json --format both`*
