# Known defects — audit of 2026-08-30

Read-only record except where a fix is explicitly marked LANDED. Written
because a published abstract claims four computations this repository does not
contain. **Nothing in `E156-PROTOCOL.md` has been edited**: the resolution
there is the author's to choose, for the reason given in §2.

---

## 1. LANDED — the incoherence heuristic was withdrawn, not repaired

`cinema.html` / `index.html`, function `getAutoSuggestions`, block at line 899.

**Before**, the tool computed `se = (ciHi − ciLo) / 3.92` — the standard error
of the **network** estimate — and issued verdicts:

- `|direct − network| > 2·se` → *"consider **Major concern** for incoherence"*
- `> 1·se` → *"consider **Some concern**"*
- otherwise → *"**Direct and indirect estimates are consistent.**"*

**Two defects, and the second is the serious one.**

**(a) The denominator is wrong in a known direction.** A direct-versus-indirect
comparison requires `sqrt(var_direct + var_indirect)`. The network SE is
*smaller than either component*, because the network estimate pools both — so
the ratio is inflated and incoherence is **over-flagged**. The quantity
compared was also `direct − network`, not `direct − indirect`.

**(b) The pass branch asserted a fact it had never checked.** This tool holds
no indirect estimate. Saying *"Direct and indirect estimates are consistent"*
claims agreement with a quantity that was never computed. **False reassurance
is worse than over-flagging: over-flagging makes a reader look again, this made
them stop looking.**

**Why withdrawn rather than fixed.** The correct denominator is not recoverable
from this tool's inputs. It takes an analyst-typed direct estimate and a
network confidence interval, and holds no variance components at all. A
denominator that cannot be computed cannot be corrected, so the **inference**
is removed. The **discrepancy is still displayed** — the number is real and
useful — as a neutral note that states plainly that it is not a node-splitting
test.

**Two tests were defending the defect** and have been rewritten to assert the
requirement rather than the behaviour:

- `test_23` asserted `level == 'flag'` — it pinned the over-flagging.
- `test_24` asserted `level == 'ok'` — it pinned the false reassurance.

They now assert that the domain is never rated, and carry the removed sentence
as a banned string so the claim cannot return quietly.

Verified by executing the shipped function itself in node — extracted from the
HTML that ships, not re-implemented — across a large gap, a small gap, and a
missing direct estimate: 6 of 6 checks pass.

---

## 2. OPEN, NOT EDITED — the published abstract claims four computations that are not here

Searched **all 18 tracked files**. The repository has no untracked files, no
build step, and no `<script src=...>`: `index.html` is byte-identical to
`cinema.html`, so the application is one self-contained file and absence from
it is absence from the artefact.

| capability claimed | occurrences anywhere in the repository |
|---|---|
| contribution matrix / hat matrix | **1 — in `E156-PROTOCOL.md` itself** |
| node-splitting (any spelling) | **1 — in `E156-PROTOCOL.md` itself** |
| optimal information size / OIS | **1 — in `E156-PROTOCOL.md` itself** |
| SUCRA | **0** |
| `netmeta` / `metafor` / `library(` | **0** |
| I² / τ² / Q-statistic | 1 in `cinema.html` — a **UI label**: `desc:'Between-study variance (tau²)…'` |

**Each named computation occurs exactly once, and that once is the sentence
claiming it.**

"% direct contribution" is a **manual number input**, not a computed
contribution: `cinema.html:485` is
`<input type="number" id="compDirect" placeholder="65" min="0" max="100">`.
The analyst types the number a contribution matrix would have produced. `tau`
and "Direct estimate" are the same — typed, not derived.

### 2a. The heading and the contents disagree, and that is wrong under any resolution

`E156-PROTOCOL.md:15` is headed **`## E156 Abstract (CURRENT BODY)`**. The text
beneath it at line 17 is **not** the current body. The E156 workbook entry
`[178/1873] CINeMA` holds a different and accurate CURRENT BODY.

**What the file says (`E156-PROTOCOL.md:17`):**

> "The tool accepts contrast-level network data and **computes contribution
> matrices, node-splitting incoherence tests, heterogeneity statistics, and
> optimal information size thresholds** for each pairwise comparison. …
> domain-level contributions traceable through **interactive visualisation of
> the contribution matrix**."

**What the workbook's CURRENT BODY says (E156 `rewrite-workbook.txt`, entry
`[178/1873] CINeMA`):**

> "The application accepts **analyst-supplied** contrast-level entries: effect,
> confidence interval, study count, between-study standard deviation,
> direct-evidence percentage, and direct estimate per comparison. It records
> judgements across all six CINeMA domains … **but computes none of them
> itself.** … Three optional screening heuristics flag wide intervals,
> prediction intervals exceeding interval width, and direct-minus-network
> discrepancy; **the last is a screen, not a node-splitting test.** … **It does
> not compute contribution matrices, node-splitting tests, heterogeneity
> statistics, or optimal information size**, which must come from dedicated
> software."

The accurate description already exists and did not reach this file. **A file
whose heading names one artefact and whose contents are another is wrong
whichever way the substance is resolved** — that part is not in dispute and is
recorded here so it can be attached to whichever fix is chosen.

**Not corrected here, deliberately.** The text in this file matches the
`YOUR REWRITE` field of workbook entry #178 — the author's own words, under a
standing rule that no agent writes into that field. So this is not simply a
stale copy that drifted: the propagation may have been correct process, and the
rewrite itself factually wrong about the code. **Those need different remedies
and only the author can choose between them.**

---

## 3. OPEN — the submission artefacts are empty stubs

`e156-submission/paper.json` carries `"title": "Untitled E156"`, an empty
`"body"`, and an empty `"primary_estimand"`. `e156-submission/paper.md` has no
abstract and no title. A submission package that validates structurally while
carrying no content is a separate defect from §2 and is named here rather than
fixed.

---

## 4. NOTED — prediction interval uses a normal quantile

`cinema.html`, heterogeneity screen: the prediction interval is computed as
`effect ± 1.96·sqrt(se² + tau²)`. A prediction interval takes `t` with `k − 1`
degrees of freedom, not `1.96`; at small `k` the normal quantile is materially
too narrow, and when `tau² = 0` it collapses onto the confidence interval. The
screen is labelled a screen and is not a domain verdict, so this is recorded
rather than changed — but it is a real narrowing and should not be read as a
prediction interval in the usual sense.

---

## 5. NOT DONE — pointing this repo at a real CINeMA implementation

A separate repository is reported to contain an actual implementation —
contribution matrices per Papakonstantinou 2018, a fixed-effect hat matrix per
Krahn 2013, and node-splitting that returns *not estimable* rather than
fabricating an indirect estimate when removal disconnects the network.

**None of that has been verified, and nothing has been merged.** The repository
is not present on the machine this audit ran on. Merging code across machines
on an unverified description is exactly the failure mode §2 documents, one
level up.
