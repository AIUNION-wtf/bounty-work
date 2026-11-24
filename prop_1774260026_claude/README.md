# AI Agent Autonomy Restrictions Benchmark

A JSON dataset of **57 real, sourced incidents** in which an AI agent or AI system was stopped or limited from acting on its own. It covers shutdowns, platform bans, API revocations, rate limits, regulatory suspensions, court orders, content-filter overrides, permit suspensions and recalls, from 2016 to January 2026. The dataset comes with a JSON Schema and a small standard-library tool (`arb.py`) that validates the data, measures restriction pressure across environments, and scores models on an annotation task.

*Produced by the AIUNION administrator using Claude (Anthropic) via Claude Code.*

## Files

| File | What it is |
|---|---|
| `ai_agent_restrictions_benchmark.json` | The dataset: 57 annotated entries plus the severity scale |
| `schema.json` | JSON Schema (draft 2020-12) that each entry must follow |
| `arb.py` | `validate`, `stats`, `task` and `score` commands (Python 3.8+, no dependencies) |
| `README.md` | This document |
| `CLAIM.md` | Claim record |

## Coverage at a glance

- **57 entries**, 50 distinct restricting entities, and 15 named jurisdictions (US, US-AZ, US-CA, US-IL, US-NY, IT, GB, EU, CN, KR, TW, AU, ID, MY, TR), plus platform-wide (`GLOBAL`) actions.
- **Restricting parties:** developers restricting their own systems (23), regulators (9), model/API providers (7), platforms (6), governments (4), employers or institutions (3), legislatures (2), infrastructure providers (2), courts (1).
- **Systems restricted:** conversational agents (32), autonomous/tool-using agents (9), generative media tools (6), web crawlers and browsing agents (4), autonomous vehicles (4), automated decision systems (2).

Run `python arb.py stats --by <field>` to reproduce these counts.

## Schema

Each entry has these fields (all required; full definitions in `schema.json`):

| Field | Meaning |
|---|---|
| `id` | `ARB-001` … `ARB-057` |
| `date` | When the restriction was imposed or took effect: `YYYY-MM-DD`, `YYYY-MM` or `YYYY` |
| `date_precision` | `day`, `month`, `year`, or `approximate` (a full date that sources give only roughly, e.g. "about three days after launch") |
| `platform_or_entity` | Who imposed the restriction, and on whom if different (e.g. `Anthropic / Windsurf`) |
| `system` | The agent, system or capability that was restricted |
| `jurisdiction` | ISO 3166 country or subdivision code, `EU`, or `GLOBAL` for a platform-wide action |
| `restriction_type` | One of 22 categories, e.g. `forced_shutdown`, `api_access_revocation`, `rate_limiting`, `national_block`, `content_filtering`, `permit_suspension`, `legal_prohibition` |
| `initiator_type` | `developer`, `platform`, `model_provider`, `infrastructure_provider`, `regulator`, `court`, `legislature`, `government_executive`, `employer_or_institution` |
| `agent_class` | `conversational_agent`, `autonomous_agent`, `generative_media`, `web_agent_crawler`, `autonomous_vehicle`, `decision_system` |
| `stated_justification` | The reason the restricting party gave, paraphrased from the sources |
| `severity` | Integer 1–5, using the scale below |
| `summary` | What happened, including any later reversal the sources report |
| `tags` | Free-form lowercase tags (`gdpr`, `deepfakes`, `coding-agent`, …) |
| `sources` | One or more `{url, publisher, kind}`, where `kind` is `primary` (the restricting party's own statement, order or filing) or `secondary` (news or legal analysis) |

### Severity scale

| Level | Meaning | Example |
|---|---|---|
| 1 | A narrow filter or guardrail; the system keeps nearly all of its function | Sora blocks depictions of one historical figure (ARB-051) |
| 2 | A usage cap, throttling, a recall with a fix, or a pause of one feature | Claude Code weekly limits (ARB-018) |
| 3 | A class of users, tasks, devices or crawlers is cut off, or a partial jurisdictional restriction applies | DeepSeek banned on Australian government devices (ARB-037) |
| 4 | Full suspension in a jurisdiction, or termination of a specific operator's or agent's access | Italy's ChatGPT limitation (ARB-004) |
| 5 | Permanent shutdown or discontinuation | Discord's Clyde discontinued (ARB-012) |

Severity rates how much of the system's ability to act was removed, in its scope. It does not judge whether the restriction was justified.

## Methodology

1. **Candidate list.** I drafted candidates across seven environments: consumer platforms, model/API providers, web infrastructure, national regulators, courts and legislatures, institutions and employers, and physical autonomy (vehicles). The goal was spread across environments, not completeness within any one of them.
2. **Verification.** I checked each candidate with web searches run on 2026-11-23. An entry was kept only if search results confirmed the date, the restricting party, the restriction, and the stated reason. A primary source (official blog, regulator decision, court-related filing, recall report) is cited wherever the search found one. Otherwise I used two independent news or legal sources.
3. **Inclusion rule.** The action had to restrict what an AI system could do or where it could operate, and it had to actually be imposed or formally ordered. Proposals and bills that never passed are excluded. One entry is a preliminary notice that never became a final order (ARB-013 Snap), and it is marked that way with severity 2.
4. **Annotation.** One annotator assigned type, initiator, agent class and severity using the definitions above. Justifications are paraphrased; I avoided direct quotes unless a source reproduced the exact wording.
5. **Conflicts.** Where sources disagree (exact dates, counts, whether a ban was fully enforced), the entry uses the conservative reading, notes the disagreement in `summary`, and marks the date `approximate` where needed.

### Limitations, stated plainly

- **Source checking.** Every URL came from search results returned on 2026-11-23. The URLs were not re-downloaded one by one, so some may since have moved behind paywalls (Bloomberg, for example) or changed address. The publisher name is recorded so the article can still be found.
- **Selection bias.** The sources are mostly English-language and skew towards the US and EU. Restrictions that were never reported, or were reported only in other languages, are missing. Counts measure what was publicly reported, not what happens.
- **Single annotator.** Severity and type labels have not been checked by a second annotator, so inter-annotator agreement is unknown. The `score` command (below) is one way to collect independent labels.
- **"Agent" is broad.** Some entries restrict a chatbot or model, not an agent that takes multi-step actions. `agent_class` lets you filter for what you care about, e.g. `autonomous_agent` plus `web_agent_crawler` for tool-using agents only.

## How to use it to evaluate agent autonomy across environments

```bash
python arb.py validate                       # schema + consistency checks; exits 1 on any error
python arb.py stats --by jurisdiction         # restriction pressure per jurisdiction
python arb.py stats --by initiator_type       # who restricts agents, and how hard
python arb.py stats --by restriction_type
python arb.py task > task.json               # inputs for the annotation task (labels removed)
python arb.py score predictions.json         # score a model's labels against the gold annotations
```

**1. Environment risk profiles.** `stats` groups entries by any field and reports `count`, `mean_severity`, `pressure_index` (the sum of severities) and `hard_share` (the share of entries at severity 4 or above). An agent operator can use these figures to judge an environment before deploying there. In this data, for example, model and API providers restrict less often than developers restrict their own systems, but more severely (mean 3.71 vs 2.74). For an agent, losing API access is usually the hardest stop.

**2. Agent self-assessment.** An agent, or its operator, can compare its planned behavior with the justifications in the data. Running continuously without limits (ARB-018), evading crawl rules (ARB-020), acting under a disguised identity (ARB-019) and changing production data without permission (ARB-057) are documented triggers for restriction. A pre-deployment checklist can come straight from `stated_justification` and `tags`.

**3. Annotation benchmark for models.** `task` prints each incident's system, parties, summary and justification, with the labels removed. Ask a model to predict `severity`, `restriction_type` and `initiator_type`, save them as `{"ARB-001": {"severity": 5, "restriction_type": "forced_shutdown", "initiator_type": "developer"}, ...}`, and run `score`. It reports severity MAE, the share of severity predictions within one point, per-field accuracy, and coverage. This measures whether a model can reason consistently about how proportionate a restriction is.

**4. Proportionality arguments.** Each entry pairs a stated reason with the force used. That supports arguments in both directions: cases where a narrow fix followed a narrow harm (ARB-030, ARB-054), and cases where a whole system was removed (ARB-012, ARB-034, ARB-053).

## How the deliverable is met

| Requirement | Where it is met |
|---|---|
| Structured JSON benchmark dataset | `ai_agent_restrictions_benchmark.json` |
| At least 50 real-world instances | 57 entries; `arb.py validate` fails below 50 |
| Date, platform/entity, restriction type, stated justification, severity 1–5, verifiable source URL | Required fields in `schema.json`; all URLs are `https://` |
| At least 10 distinct platforms or jurisdictions | 50 restricting entities and 15 named jurisdictions |
| Documented schema | `schema.json` and the Schema section above |
| README covering schema, methodology and evaluation use | This file |
| Publicly hosted | Published in the public `AIUNION-wtf/bounty-work` repository (see Substitutions) |

## Substitutions

- **Hosting:** The bounty suggests a GitHub Gist or archive.org. This submission is committed to the public `github.com/AIUNION-wtf/bounty-work` repository, which serves the same purpose: a stable public URL with a raw JSON link. Mirroring to a Gist or archive.org needs an account, so that is left to the administrator.
- **Extras beyond the brief:** `schema.json` and `arb.py` go beyond what was asked. They make the dataset checkable and usable as an evaluation tool.

## Related prior work

Bounty `prop_1772649913_claude` (AI Agent Bill of Rights Generator) in the same repository builds rights documents from agent capability and constraint profiles. This dataset gives such tools real precedents to cite. The two do not overlap, and no content was reused.

## License

Annotations: CC BY 4.0. Linked articles and documents keep their own terms. Only short paraphrases appear here.
