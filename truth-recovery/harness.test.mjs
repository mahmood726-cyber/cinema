// truth-recovery/harness.test.mjs
// Known-truth calibration check of CINeMA's COMPUTED domain-rating rules.
// Run: node --test truth-recovery/harness.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { getConfidence, getAutoSuggestions, state } from './engine.mjs';
import {
    comparisonWithImprecision, comparisonWithHeterogeneity,
    comparisonWithIncoherence, TRUTH
} from './dgp-known-truth.mjs';

// 1) IMPRECISION rating tracks truth across precise -> imprecise -> very imprecise.
test('imprecision rating calibrated to CI-width / threshold (linear MD)', () => {
    state.effectMeasure = 'MD';
    state.clinThreshold = 0.5;
    const cases = [1.0, 1.5, 2.5, 4.0]; // widthMultiple
    for (const wm of cases) {
        const comp = comparisonWithImprecision(0.3, 0.5, wm);
        const got = getAutoSuggestions(comp).imp.level;
        assert.equal(got, TRUTH.imprecision(wm),
            `widthMultiple=${wm}: got ${got}, expected ${TRUTH.imprecision(wm)}`);
    }
});

// 2) Precise estimate is NOT downgraded (no false positive).
test('precise estimate is rated ok (no false imprecision downgrade)', () => {
    state.effectMeasure = 'MD';
    state.clinThreshold = 1.0;
    const comp = comparisonWithImprecision(0.5, 1.0, 1.0); // width=1.0 == 1x threshold
    assert.equal(getAutoSuggestions(comp).imp.level, 'ok');
});

// 3) HETEROGENEITY rating tracks truth via prediction-interval inflation.
test('heterogeneity rating calibrated to tau (PI vs CI width)', () => {
    state.effectMeasure = 'MD';
    const se = 0.1;
    // tau=0.05 -> ratio sqrt(1+0.25)=1.12 (ok); tau=0.20 -> sqrt(5)=2.24 (warn);
    // tau=0.30 -> sqrt(10)=3.16 (flag)
    for (const tau of [0.05, 0.20, 0.30]) {
        const comp = comparisonWithHeterogeneity(0.4, se, tau);
        const got = getAutoSuggestions(comp).het.level;
        assert.equal(got, TRUTH.heterogeneity(se, tau),
            `tau=${tau}: got ${got}, expected ${TRUTH.heterogeneity(se, tau)}`);
    }
});

// 4) INCOHERENCE rating tracks truth via direct-vs-network discrepancy.
test('incoherence rating calibrated to direct-network gap in SE units', () => {
    state.effectMeasure = 'MD';
    const se = 0.2;
    for (const sm of [0.5, 1.5, 2.5]) { // SE multiples -> ok / warn / flag
        const comp = comparisonWithIncoherence(0.6, se, sm);
        const got = getAutoSuggestions(comp).inc.level;
        assert.equal(got, TRUTH.incoherence(sm),
            `seMultiple=${sm}: got ${got}, expected ${TRUTH.incoherence(sm)}`);
    }
});

// 5) Overall confidence mapping: downgrade arithmetic is correct (GRADE-style).
test('confidence downgrade mapping (some=-1, major=-2) is correct', () => {
    assert.equal(getConfidence({ wsb: 'no', rb: 'no', ind: 'no', imp: 'no', het: 'no', inc: 'no' }), 'High');
    assert.equal(getConfidence({ imp: 'some' }), 'Moderate');          // 1 downgrade
    assert.equal(getConfidence({ imp: 'major' }), 'Low');              // 2 downgrades
    assert.equal(getConfidence({ imp: 'some', het: 'some' }), 'Low');  // 2 downgrades
    assert.equal(getConfidence({ imp: 'major', het: 'some' }), 'Low'); // 3 (<=3 -> Low)
    assert.equal(getConfidence({ imp: 'major', het: 'major' }), 'Very Low'); // 4
    // A fully clean assessment must never be downgraded.
    assert.equal(getConfidence({}), 'High');
});
