# Truth-Recovery Validation - cinema (CINeMA)

Date: 2026-06-15. Additive only; no app code modified.

## Verdict: PASS - genuine COMPUTED rule engine (not a pure manual-rating UI). The imprecision / heterogeneity / incoherence domain suggestions track known truth.

CINeMA rates confidence in NMA estimates across 6 domains. The repo's index.html / cinema.html (1679 lines) contains getAutoSuggestions(), which COMPUTES domain-level concern flags from the data (CI width, tau, direct-vs-network gap) - so this is testable, not just a dropdown UI. The user still sets final ratings, but the computed suggestion rule is the testable operating characteristic.

## What was tested (functions extracted VERBATIM from index.html)
getAutoSuggestions (index.html 855-911) and getConfidence (840-852).

### 1. Imprecision (CI width vs clinical threshold, linear scale)
Rule: width<=2x threshold -> ok; >2x -> Some; >3x -> Major. Built comparisons at width multiples {1.0, 1.5, 2.5, 4.0}. Engine returned ok/ok/warn/flag = matches truth. PASS.

### 2. No false downgrade
Precise estimate (width == 1x threshold) -> ok (no spurious imprecision concern). PASS.

### 3. Heterogeneity (prediction-interval inflation from tau)
PI uses sqrt(se^2+tau^2); ratio = sqrt(1+(tau/se)^2); >2 -> Some, >3 -> Major. se=0.1, tau in {0.05,0.20,0.30} -> ratios 1.12/2.24/3.16 -> ok/warn/flag = matches truth. PASS.

### 4. Incoherence (direct vs network gap in SE units)
|direct-network| > 1 SE -> Some, > 2 SE -> Major. se=0.2, gaps {0.5,1.5,2.5} SE -> ok/warn/flag = matches truth. PASS.

### 5. Confidence downgrade arithmetic
some=-1, major=-2; High=0, Moderate=1, Low=2-3, Very Low=4+. All mappings verified including clean assessment -> High (never falsely downgraded). PASS.

## Results: 5/5 assertions pass.

## Findings
- getAutoSuggestions is a correct, calibrated computed rule: it fires Some/Major concern when truly imprecise / heterogeneous / incoherent and stays ok when precise / homogeneous / coherent. No false positives at the boundaries tested.
- Heterogeneity logic correctly derives the prediction interval from tau and SE and compares PI to CI width - methodologically sound.
- NOTE (not a bug, a design choice worth flagging): the getConfidence downgrade boundary is non-standard vs GRADE/CINeMA convention. It maps 2 OR 3 downgrades both to "Low", and only 4+ to "Very Low". Standard CINeMA/GRADE typically treats 3+ downgrades as Very Low. The current thresholds (downgrades<=3 -> Low) are internally consistent but more lenient than convention at the 3-downgrade point.
- The thresholds (2x/3x for imprecision, 2x/3x PI ratio for heterogeneity, 1/2 SE for incoherence) are heuristic suggestion aids, not formal CINeMA inference - which the UI presents as "consider Some/Major concern", appropriately advisory.

## Recommendation
Keep - the computed rule engine is correct and calibrated. Consider aligning the getConfidence boundary with GRADE convention (3+ downgrades -> Very Low) if the intent is to mirror standard CINeMA reporting; document the heuristic thresholds as suggestion aids in the methods note.
