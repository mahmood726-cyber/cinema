// truth-recovery/dgp-known-truth.mjs
// Standalone KNOWN-TRUTH constructors for CINeMA comparison objects.
// Each builder embeds a KNOWN operating characteristic (precise vs imprecise,
// homogeneous vs heterogeneous, coherent vs incoherent) so the repo's
// getAutoSuggestions ratings can be checked against ground truth.

// Build a comparison with a controlled CI width relative to a clinical threshold.
// widthMultiple = (CI width) / threshold. The engine's linear-scale rule:
//   <=2x -> ok, >2x -> warn (Some), >3x -> flag (Major).
export function comparisonWithImprecision(effect, threshold, widthMultiple) {
    const width = widthMultiple * threshold;
    return {
        effect,
        ciLo: effect - width / 2,
        ciHi: effect + width / 2,
        tau: null,
        directEst: null
    };
}

// Build a comparison with KNOWN heterogeneity via tau.
// The engine compares the prediction-interval width to the CI width:
//   PI uses sqrt(se^2 + tau^2) where se = (ciHi-ciLo)/3.92.
// piRange/ciRange = sqrt(se^2+tau^2)/se = sqrt(1 + (tau/se)^2).
//   <=2x -> ok, >2x -> warn, >3x -> flag.
export function comparisonWithHeterogeneity(effect, se, tau) {
    const ciLo = effect - 1.96 * se;
    const ciHi = effect + 1.96 * se;
    return { effect, ciLo, ciHi, tau, directEst: null };
}

// Build a comparison with KNOWN incoherence: direct estimate offset from the
// network estimate by `seMultiple` standard errors.
//   <=1 SE -> ok, >1 SE -> warn, >2 SE -> flag.
export function comparisonWithIncoherence(effect, se, seMultiple) {
    const ciLo = effect - 1.96 * se;
    const ciHi = effect + 1.96 * se;
    // engine recomputes se as (ciHi-ciLo)/3.92 = se (since 2*1.96=3.92)
    const directEst = effect + seMultiple * se;
    return { effect, ciLo, ciHi, tau: null, directEst };
}

// Oracle: what the engine SHOULD return given the construction.
export const TRUTH = {
    imprecision: (widthMultiple) => widthMultiple > 3 ? 'flag' : (widthMultiple > 2 ? 'warn' : 'ok'),
    incoherence: (seMultiple) => seMultiple > 2 ? 'flag' : (seMultiple > 1 ? 'warn' : 'ok'),
    // heterogeneity ratio = sqrt(1 + (tau/se)^2)
    heterogeneity: (se, tau) => {
        const ratio = Math.sqrt(1 + (tau / se) ** 2);
        return ratio > 3 ? 'flag' : (ratio > 2 ? 'warn' : 'ok');
    }
};
