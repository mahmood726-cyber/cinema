# CINeMA Code Review Findings

**Date:** 2026-04-03
**File:** cinema.html (1,670 lines)
**Tests:** 45/45 PASS

## P0 (Critical)

### P0-1: CSV export lacks formula injection sanitization
**Lines:** 1215-1238 (`downloadCSV`)
CSV values wrapped in double quotes but no check for cells starting with `=`, `+`, `@`, `\t`, `\r`. User-entered treatment names or footnotes could inject spreadsheet formulas.
**Status:** FIXED

### P0-2: Missing closing `</html>` tag
**Line:** 1669
File ends with `</script></body>` but no `</html>`.
**Status:** FIXED

## P1 (Important)

### P1-1: Imprecision auto-suggestion logic order bug
**Lines:** 868-876
The `ciWidth > 3*thresh` (Major concern) check comes AFTER `ciWidth > 2*thresh` (Some concern), so CI widths exceeding 3x threshold are classified as "Some concern" instead of "Major concern".
**Status:** FIXED

### P1-2: Modal keyboard listener not removed on overlay click
**Lines:** 641-645
Clicking modal overlay closes modal but does not call `removeEventListener('keydown', handleModalKey)`. Listener accumulates.
**Status:** FIXED

### P1-3: `parseFloat(x) || 0` for k studies drops valid zero
**Line:** 727
`parseInt(document.getElementById('compK').value)||0` is correct for k (0 studies is meaningful). No issue here, but `directPct` on line 728 uses `parseFloat(...) || null` which would drop 0% direct contribution. 0% is a valid value meaning "entirely indirect."
**Status:** Noted (low impact)

### P1-4: No validation that CI lower < CI upper
**Lines:** 718-740
`addComparison` does not validate that `ciLo < ciHi`. Reversed CIs would produce incorrect auto-suggestions (SE calculation, PI computation).
**Status:** Noted

## P2 (Minor)

### P2-1: `formatEffect` has duplicated branches
**Lines:** 814-819
The `if(em==='OR'||em==='RR'||em==='HR')` branch and `else` branch produce identical output. Dead code.

### P2-2: `Math.random()` used in ID generation
**Lines:** 678, 731
Treatment and comparison IDs use `Math.random()` instead of seeded PRNG. Not used for reproducible outputs so acceptable, but inconsistent with the seeded PRNG pattern established at line 541.

### P2-3: Network graph simulation runs 120 frames regardless
**Line:** 1507
Force-directed layout always runs 120 iterations. Could detect convergence and stop early for performance.

### P2-4: Missing `aria-label` on dark mode toggle
**Line:** 245
`#darkBtn` has title but no aria-label for screen readers.

### P2-5: No keyboard navigation for treatment/comparison pills
**Lines:** 762-767
Pill remove buttons lack keyboard focus indicators.

---

**Summary:** 2 P0 fixed, 4 P1 found (1 fixed), 5 P2 found
