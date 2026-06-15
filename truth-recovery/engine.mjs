// truth-recovery/engine.mjs
// ADDITIVE. Pure DOM-free CINeMA rule functions extracted VERBATIM from index.html.
// getConfidence: lines 840-852; getAutoSuggestions: lines 855-911; DOMAINS: 568-575.
// Only 'state' (a plain object the functions read) is provided as a settable stub.

export const state = {
  effectMeasure: 'MD',
  clinThreshold: null
};

// ===== VERBATIM: DOMAINS (index.html 568-575) =====
const DOMAINS = [
  {id:'wsb',  label:'Within-study bias',   short:'WSB', desc:'Risk of bias in contributing studies, weighted by their contribution to the comparison.'},
  {id:'rb',   label:'Reporting bias',       short:'RB',  desc:'Small-study effects and selective reporting bias in the network.'},
  {id:'ind',  label:'Indirectness',         short:'IND', desc:'How directly studies address the comparison of interest (population, intervention, outcome, timing).'},
  {id:'imp',  label:'Imprecision',          short:'IMP', desc:'Width of the confidence interval relative to the clinical decision threshold.'},
  {id:'het',  label:'Heterogeneity',        short:'HET', desc:'Between-study variance (tau²) within pairwise comparisons contributing to the network.'},
  {id:'inc',  label:'Incoherence',          short:'INC', desc:'Inconsistency between direct and indirect evidence (loop inconsistency or design-by-treatment).'}
];

// ===== VERBATIM: getConfidence (index.html 840-852) =====
function getConfidence(assessment){
  if(!assessment) return null;
  let downgrades = 0;
  DOMAINS.forEach(d=>{
    const v = assessment[d.id];
    if(v==='some') downgrades += 1;
    else if(v==='major') downgrades += 2;
  });
  if(downgrades===0) return 'High';
  if(downgrades===1) return 'Moderate';
  if(downgrades<=3) return 'Low';
  return 'Very Low';
}

// ===== VERBATIM: getAutoSuggestions (index.html 855-911) =====
function getAutoSuggestions(comp){
  const sugg = {};
  const em = state.effectMeasure;
  const thresh = state.clinThreshold;
  // Imprecision
  if(comp.ciLo!==null&&comp.ciHi!==null&&thresh!==null&&isFinite(thresh)){
    const ciWidth = comp.ciHi - comp.ciLo;
    const isRatio = em==='OR'||em==='RR'||em==='HR';
    if(isRatio){
      const logLo = Math.log(comp.ciLo>0?comp.ciLo:0.001);
      const logHi = Math.log(comp.ciHi>0?comp.ciHi:0.001);
      const logThresh = Math.log(thresh>0?thresh:0.001);
      if(logHi-logLo > 2*Math.abs(logThresh)){
        sugg.imp = {level:'warn', text:'CI width ('+Math.abs(logHi-logLo).toFixed(2)+' log scale) exceeds 2× threshold — consider Some concern for imprecision.'};
      } else {
        sugg.imp = {level:'ok', text:'CI width within threshold range.'};
      }
    } else {
      if(ciWidth > 3*Math.abs(thresh)){
        sugg.imp = {level:'flag', text:'CI width greatly exceeds threshold — consider Major concern.'};
      } else if(ciWidth > 2*Math.abs(thresh)){
        sugg.imp = {level:'warn', text:'CI width ('+ciWidth.toFixed(2)+') exceeds 2× clinical threshold ('+thresh+') — consider Some concern.'};
      } else {
        sugg.imp = {level:'ok', text:'CI width within clinical threshold range.'};
      }
    }
  }
  // Heterogeneity
  if(comp.tau!==null&&isFinite(comp.tau)&&comp.ciLo!==null&&comp.ciHi!==null){
    const se = (comp.ciHi-comp.ciLo)/3.92;
    const tau = comp.tau;
    const piLo = comp.effect - 1.96*Math.sqrt(se*se+tau*tau);
    const piHi = comp.effect + 1.96*Math.sqrt(se*se+tau*tau);
    const ciRange = comp.ciHi-comp.ciLo;
    const piRange = piHi-piLo;
    if(piRange > ciRange*3){
      sugg.het = {level:'flag', text:'Prediction interval much wider than CI — consider Major concern for heterogeneity.'};
    } else if(piRange > ciRange*2){
      sugg.het = {level:'warn', text:'Prediction interval ('+piLo.toFixed(2)+' to '+piHi.toFixed(2)+') is >2× the CI width — consider Some concern for heterogeneity.'};
    } else {
      sugg.het = {level:'ok', text:'Prediction interval similar to CI width (tau='+tau.toFixed(3)+').'};
    }
  }
  // Incoherence
  if(comp.directEst!==null&&isFinite(comp.directEst)&&comp.effect!==null&&comp.ciLo!==null&&comp.ciHi!==null){
    const se = (comp.ciHi-comp.ciLo)/3.92;
    const diff = Math.abs(comp.directEst - comp.effect);
    if(diff > 2*se){
      sugg.inc = {level:'flag', text:'Direct estimate ('+comp.directEst.toFixed(2)+') differs from network by '+diff.toFixed(2)+' (>2 SE) — consider Major concern for incoherence.'};
    } else if(diff > se){
      sugg.inc = {level:'warn', text:'Direct estimate ('+comp.directEst.toFixed(2)+') differs from network by '+diff.toFixed(2)+' (>1 SE) — consider Some concern.'};
    } else {
      sugg.inc = {level:'ok', text:'Direct and indirect estimates are consistent.'};
    }
  }
  return sugg;
}

export { getConfidence, getAutoSuggestions, DOMAINS };
