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

## P2 (Minor) — all fixed 2026-04-03

### P2-1: `formatEffect` has duplicated branches
**Status:** FIXED — Removed dead code; collapsed to single branch returning `eff.toFixed(2)` with optional CI.

### P2-2: `Math.random()` used in ID generation
**Status:** FIXED — Replaced with deterministic counter (`nextId()` function using incrementing `_idCounter`).

### P2-3: Network graph simulation runs 120 frames regardless
**Status:** FIXED — Added convergence detection: stops early when total kinetic energy < 0.01.

### P2-4: Missing `aria-label` on dark mode toggle
**Status:** FIXED — Added `aria-label="Toggle dark mode"` to `#darkBtn`.

### P2-5: No keyboard navigation for treatment/comparison pills
**Status:** FIXED — Added `focus-visible` outline style for `.pill-remove` buttons.

---

**Summary:** 2 P0 fixed, 4 P1 found (2 fixed, 2 noted), 5 P2 fixed
