# Protocol Registration: CINeMA-Browser

## Registration Details

| Field | Value |
|---|---|
| **Registration ID** | CIN-2026-001 |
| **Registration Date** | 2026-03-31 |
| **Status** | Complete |
| **Version** | 1.0 |

---

## Title

CINeMA-Browser: A Free Browser-Based Tool for Confidence in Network Meta-Analysis

---

## Authors

Mahmood Alhusseini
London Cardiology Clinic, London, United Kingdom

---

## Objectives

**Primary:** Build a single-file, offline-capable browser tool that fully implements the CINeMA framework for rating confidence in NMA estimates across all six assessment domains (within-study bias, reporting bias, indirectness, imprecision, heterogeneity, incoherence).

**Secondary:**
- Provide evidence-informed auto-suggestions for each domain rating
- Render an interactive force-directed network graph showing treatment connections
- Generate publication-ready traffic-light summary tables
- Enable persistent project storage via localStorage
- Embed three worked clinical examples

---

## Methods

- **Architecture:** Single HTML file (no server, no build step, no dependencies)
- **Visualisation:** Canvas-based force-directed graph (treatments as nodes, comparisons as edges)
- **Domains:** All 6 CINeMA domains with High/Moderate/Low ratings + narrative justification
- **Auto-suggestions:** Rule-based, triggered by study counts, weights, I² values, and comparison type
- **Storage:** localStorage key `cinema_v1_projects`, schema v1 with migration logic
- **Export:** HTML report, CSV summary, narrative paragraph, clipboard copy
- **Examples:** 3 built-in clinical networks (antidepressants, antihypertensives, antiplatelets)

---

## Outcomes

**Primary outcome:** Correct CINeMA domain assessment with traffic-light confidence table matching the published CINeMA methodology (Papakonstantinou 2020).

**Secondary outcomes:**
- Export in 4 formats (HTML, CSV, narrative, clipboard)
- Offline functionality (zero network requests after load)
- Sub-second load time on standard hardware
- Accessible keyboard navigation and ARIA labelling

---

## Timeline

| Milestone | Date | Status |
|---|---|---|
| Protocol registered | 2026-03-31 | Done |
| MVP implementation | 2026-03-31 | Done |
| Safety validation | 2026-03-31 | Done |
| Public release | 2026-03-31 | Done |

---

## Implementation Size

- **Total lines:** 1,670
- **Domains implemented:** 6/6
- **Built-in examples:** 3
- **Export formats:** 4
- **External dependencies:** 0

---

## Validation

| Check | Result |
|---|---|
| Div balance | Pass |
| Script integrity (`</script>` in template literals) | Pass |
| Function uniqueness | Pass |
| Element ID uniqueness | Pass |
| XSS escaping | Pass |

---

## Live URL

**Tool:** https://mahmood726-cyber.github.io/cinema/cinema.html
**Source:** https://github.com/mahmood726-cyber/cinema
**Protocol paper:** https://mahmood726-cyber.github.io/cinema/docs/protocol.html
**Results paper:** https://mahmood726-cyber.github.io/cinema/docs/results.html

---

## References

Papakonstantinou T, Nikolakopoulou A, Rücker G, et al. Estimating the contribution of studies in network meta-analysis: paths, flows and streams. *F1000Research* 2018;7:610.

Nikolakopoulou A, Higgins JPT, Papakonstantinou T, et al. CINeMA: An approach for assessing confidence in the results of a network meta-analysis. *PLOS Medicine* 2020;17(4):e1003082.

---

*Registration format: E156 Micro-Paper Standard*
*Registered: 2026-03-31 by Mahmood Alhusseini*
