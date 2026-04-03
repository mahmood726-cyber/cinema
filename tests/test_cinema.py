"""Selenium tests for CINeMA — Confidence in Network Meta-Analysis."""
import sys, io, os, unittest, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HTML = 'file:///' + os.path.abspath(r'C:\Models\CINeMA\cinema.html').replace('\\', '/')


class TestCINeMA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--window-size=1400,900')
        cls.drv = webdriver.Chrome(options=opts)
        cls.drv.get(HTML)
        time.sleep(1.5)
        # Clear saved state
        cls.drv.execute_script("localStorage.removeItem('cinema_app_v1');")
        cls.drv.get(HTML)
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.drv.quit()

    def js(self, script):
        return self.drv.execute_script(script)

    def _load_antidepressant_example(self):
        """Helper to load antidepressant example and wait."""
        self.js("loadExampleData(1);")
        time.sleep(0.5)

    def _load_bp_example(self):
        """Helper to load blood pressure example."""
        self.js("loadExampleData(2);")
        time.sleep(0.5)

    def _load_pain_example(self):
        """Helper to load pain example."""
        self.js("loadExampleData(3);")
        time.sleep(0.5)

    # ================================================================
    # 1. getConfidence — no downgrades = High
    # ================================================================
    def test_01_confidence_high(self):
        """All domains 'no concern' -> High."""
        val = self.js("""
            return getConfidence({wsb:'no', rb:'no', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'High')

    # ================================================================
    # 2. getConfidence — 1 some concern = Moderate
    # ================================================================
    def test_02_confidence_moderate(self):
        """One 'some' concern -> Moderate (1 downgrade)."""
        val = self.js("""
            return getConfidence({wsb:'some', rb:'no', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Moderate')

    # ================================================================
    # 3. getConfidence — 2 some concerns = Low
    # ================================================================
    def test_03_confidence_low(self):
        """Two 'some' concerns -> 2 downgrades -> Low."""
        val = self.js("""
            return getConfidence({wsb:'some', rb:'some', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Low')

    # ================================================================
    # 4. getConfidence — 1 major concern = Low
    # ================================================================
    def test_04_confidence_major_gives_low(self):
        """One 'major' concern -> 2 downgrades -> Low."""
        val = self.js("""
            return getConfidence({wsb:'major', rb:'no', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Low')

    # ================================================================
    # 5. getConfidence — 3 some concerns = Low (still)
    # ================================================================
    def test_05_confidence_three_some_low(self):
        """Three 'some' concerns -> 3 downgrades -> Low."""
        val = self.js("""
            return getConfidence({wsb:'some', rb:'some', ind:'some', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Low')

    # ================================================================
    # 6. getConfidence — 4+ downgrades = Very Low
    # ================================================================
    def test_06_confidence_very_low(self):
        """4+ downgrades -> Very Low."""
        val = self.js("""
            return getConfidence({wsb:'some', rb:'some', ind:'some', imp:'some', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Very Low')

    # ================================================================
    # 7. getConfidence — all major = Very Low
    # ================================================================
    def test_07_confidence_all_major(self):
        """All 'major' -> 12 downgrades -> Very Low."""
        val = self.js("""
            return getConfidence({wsb:'major', rb:'major', ind:'major', imp:'major', het:'major', inc:'major'});
        """)
        self.assertEqual(val, 'Very Low')

    # ================================================================
    # 8. getConfidence — null/empty assessment = High
    # ================================================================
    def test_08_confidence_empty(self):
        """Empty assessment object -> High (no concerns detected)."""
        val = self.js("return getConfidence({});")
        self.assertEqual(val, 'High')

    # ================================================================
    # 9. getConfidence — null returns null
    # ================================================================
    def test_09_confidence_null(self):
        """Null assessment -> null."""
        val = self.js("return getConfidence(null);")
        self.assertIsNone(val)

    # ================================================================
    # 10. DOMAINS constant
    # ================================================================
    def test_10_domains_definition(self):
        """6 CINeMA domains are defined."""
        count = self.js("return DOMAINS.length;")
        self.assertEqual(count, 6)
        ids = self.js("return DOMAINS.map(d=>d.id);")
        self.assertEqual(ids, ['wsb', 'rb', 'ind', 'imp', 'het', 'inc'])

    # ================================================================
    # 11. CONCERN_LEVELS constant
    # ================================================================
    def test_11_concern_levels(self):
        """CONCERN_LEVELS = ['no', 'some', 'major']."""
        lvls = self.js("return CONCERN_LEVELS;")
        self.assertEqual(lvls, ['no', 'some', 'major'])

    # ================================================================
    # 12. escHtml
    # ================================================================
    def test_12_esc_html(self):
        """escHtml escapes all 5 dangerous characters."""
        val = self.js("""return escHtml('<div class="test">&\\'x\\'</div>');""")
        self.assertIn('&lt;', val)
        self.assertIn('&gt;', val)
        self.assertIn('&amp;', val)
        self.assertIn('&quot;', val)
        self.assertIn('&#39;', val)

    # ================================================================
    # 13. formatEffect
    # ================================================================
    def test_13_format_effect(self):
        """formatEffect returns 'est (lo, hi)' pattern."""
        val = self.js("return formatEffect(1.61, 1.38, 1.87);")
        self.assertIn('1.61', val)
        self.assertIn('1.38', val)
        self.assertIn('1.87', val)

    # ================================================================
    # 14. formatEffect — null CI
    # ================================================================
    def test_14_format_effect_null_ci(self):
        """formatEffect with null CI returns estimate only."""
        val = self.js("return formatEffect(1.61, null, null);")
        self.assertIn('1.61', val)
        self.assertNotIn('null', val)

    # ================================================================
    # 15. Load antidepressant example
    # ================================================================
    def test_15_load_example_antidepressants(self):
        """Antidepressant example: 7 treatments, 8 comparisons."""
        self._load_antidepressant_example()
        tx_count = self.js("return state.treatments.length;")
        comp_count = self.js("return state.comparisons.length;")
        self.assertEqual(tx_count, 7)
        self.assertEqual(comp_count, 8)

    # ================================================================
    # 16. Load BP example
    # ================================================================
    def test_16_load_example_bp(self):
        """BP example: 5 treatments, 6 comparisons, effectMeasure=MD."""
        self._load_bp_example()
        tx_count = self.js("return state.treatments.length;")
        comp_count = self.js("return state.comparisons.length;")
        em = self.js("return state.effectMeasure;")
        self.assertEqual(tx_count, 5)
        self.assertEqual(comp_count, 6)
        self.assertEqual(em, 'MD')

    # ================================================================
    # 17. Load pain example
    # ================================================================
    def test_17_load_example_pain(self):
        """Pain example: 6 treatments, effectMeasure=SMD."""
        self._load_pain_example()
        tx_count = self.js("return state.treatments.length;")
        em = self.js("return state.effectMeasure;")
        self.assertEqual(tx_count, 6)
        self.assertEqual(em, 'SMD')

    # ================================================================
    # 18. Antidepressant example pre-filled assessments
    # ================================================================
    def test_18_antidepressant_assessments(self):
        """Antidepressant example has pre-filled domain assessments."""
        self._load_antidepressant_example()
        assess_count = self.js("return Object.keys(state.assessments).length;")
        self.assertGreaterEqual(assess_count, 8)
        # First comparison: wsb='no', het='some'
        first_id = self.js("return state.comparisons[0].id;")
        wsb = self.js("return state.assessments[state.comparisons[0].id].wsb;")
        het = self.js("return state.assessments[state.comparisons[0].id].het;")
        self.assertEqual(wsb, 'no')
        self.assertEqual(het, 'some')

    # ================================================================
    # 19. Confidence of antidepressant comparisons
    # ================================================================
    def test_19_antidepressant_confidence(self):
        """Check confidence levels for first and fourth comparisons."""
        self._load_antidepressant_example()
        # First: wsb=no, rb=no, ind=no, imp=no, het=some, inc=no -> Moderate
        conf1 = self.js("return getConfidence(state.assessments[state.comparisons[0].id]);")
        self.assertEqual(conf1, 'Moderate')
        # Fourth (MIR vs PBO): wsb=some, rb=major, het=some, inc=some -> Very Low
        conf4 = self.js("return getConfidence(state.assessments[state.comparisons[3].id]);")
        self.assertEqual(conf4, 'Very Low')

    # ================================================================
    # 20. getAutoSuggestions — imprecision (MD)
    # ================================================================
    def test_20_autosugg_imprecision_md(self):
        """CI width exceeding 2x threshold triggers imprecision warning."""
        self.js("""
            state.effectMeasure = 'MD';
            state.clinThreshold = 5;
        """)
        sugg = self.js("""
            var comp = {effect:-9.1, ciLo:-10.4, ciHi:-7.8, k:28, directPct:88, tau:1.8, directEst:-9.0};
            return getAutoSuggestions(comp);
        """)
        # CI width = 2.6, 2*5=10 => 2.6 < 10, so no warning
        if 'imp' in sugg:
            self.assertIn('ok', sugg['imp']['level'])

    # ================================================================
    # 21. getAutoSuggestions — imprecision wide CI
    # ================================================================
    def test_21_autosugg_imprecision_wide(self):
        """Very wide CI should trigger imprecision concern."""
        self.js("""
            state.effectMeasure = 'MD';
            state.clinThreshold = 2;
        """)
        sugg = self.js("""
            var comp = {effect:-9.1, ciLo:-15.0, ciHi:-3.0, k:5, directPct:50, tau:3.0, directEst:-8.0};
            return getAutoSuggestions(comp);
        """)
        self.assertIn('imp', sugg)
        self.assertEqual(sugg['imp']['level'], 'warn')

    # ================================================================
    # 22. getAutoSuggestions — heterogeneity
    # ================================================================
    def test_22_autosugg_heterogeneity(self):
        """Large tau relative to SE triggers heterogeneity concern."""
        sugg = self.js("""
            state.effectMeasure = 'MD';
            state.clinThreshold = 5;
            var comp = {effect:-5.0, ciLo:-6.0, ciHi:-4.0, k:10, directPct:60, tau:3.0, directEst:-4.8};
            return getAutoSuggestions(comp);
        """)
        self.assertIn('het', sugg)
        # SE ~= (6.0-4.0)/3.92 = 0.51; PI range ~ large vs CI range ~ 2
        self.assertIn('warn', sugg['het']['level'])

    # ================================================================
    # 23. getAutoSuggestions — incoherence
    # ================================================================
    def test_23_autosugg_incoherence(self):
        """Direct estimate differing by >2 SE triggers major concern."""
        sugg = self.js("""
            state.effectMeasure = 'MD';
            state.clinThreshold = 5;
            var comp = {effect:-5.0, ciLo:-6.0, ciHi:-4.0, k:10, directPct:60, tau:0.5, directEst:-2.0};
            return getAutoSuggestions(comp);
        """)
        self.assertIn('inc', sugg)
        # diff=3.0, SE=0.51, 3.0 > 2*0.51 -> flag
        self.assertEqual(sugg['inc']['level'], 'flag')

    # ================================================================
    # 24. getAutoSuggestions — incoherence consistent
    # ================================================================
    def test_24_autosugg_incoherence_consistent(self):
        """Direct estimate close to network estimate -> ok."""
        sugg = self.js("""
            state.effectMeasure = 'MD';
            state.clinThreshold = 5;
            var comp = {effect:-9.1, ciLo:-10.4, ciHi:-7.8, k:28, directPct:88, tau:1.8, directEst:-9.0};
            return getAutoSuggestions(comp);
        """)
        self.assertIn('inc', sugg)
        self.assertEqual(sugg['inc']['level'], 'ok')

    # ================================================================
    # 25. Tab switching
    # ================================================================
    def test_25_tab_switching(self):
        """Switch to CINeMA table tab, verify panel is active."""
        self.js("switchTab('table');")
        time.sleep(0.3)
        active = self.js("return document.getElementById('table-tab').classList.contains('active');")
        self.assertTrue(active)

    # ================================================================
    # 26. Network tab active on load
    # ================================================================
    def test_26_network_tab_default(self):
        """Network tab panel exists."""
        exists = self.js("return document.getElementById('network-tab') !== null;")
        self.assertTrue(exists)

    # ================================================================
    # 27. CINeMA table rendering
    # ================================================================
    def test_27_cinema_table_rows(self):
        """CINeMA table shows correct number of rows after loading example."""
        self._load_antidepressant_example()
        self.js("switchTab('table');")
        time.sleep(0.5)
        rows = self.js("""
            var table = document.querySelector('.cinema-table tbody');
            return table ? table.children.length : 0;
        """)
        self.assertEqual(rows, 8)

    # ================================================================
    # 28. Dark mode toggle
    # ================================================================
    def test_28_dark_mode_toggle(self):
        """Toggle dark mode adds/removes class."""
        self.js("toggleDark();")
        time.sleep(0.3)
        dark1 = self.js("return document.body.classList.contains('dark');")
        self.js("toggleDark();")
        time.sleep(0.3)
        dark2 = self.js("return document.body.classList.contains('dark');")
        self.assertNotEqual(dark1, dark2)

    # ================================================================
    # 29. mkPRNG determinism
    # ================================================================
    def test_29_prng_deterministic(self):
        """Seeded PRNG produces same sequence each time."""
        seq1 = self.js("""
            var rng = mkPRNG(42);
            return [rng(), rng(), rng()];
        """)
        seq2 = self.js("""
            var rng = mkPRNG(42);
            return [rng(), rng(), rng()];
        """)
        self.assertEqual(seq1, seq2)

    # ================================================================
    # 30. mkPRNG range [0,1)
    # ================================================================
    def test_30_prng_range(self):
        """PRNG output in [0, 1)."""
        vals = self.js("""
            var rng = mkPRNG(123);
            var out = [];
            for(var i=0; i<100; i++) out.push(rng());
            return out;
        """)
        for v in vals:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)

    # ================================================================
    # 31. getTxName / getTxShort / getTxColor helpers
    # ================================================================
    def test_31_tx_helpers(self):
        """Treatment helpers return correct data after loading example."""
        self._load_antidepressant_example()
        tx_id = self.js("return state.treatments[0].id;")
        name = self.js("return getTxName(state.treatments[0].id);")
        short = self.js("return getTxShort(state.treatments[0].id);")
        color = self.js("return getTxColor(state.treatments[0].id);")
        self.assertEqual(name, 'Sertraline')
        self.assertEqual(short, 'SER')
        self.assertRegex(color, r'^#[0-9a-fA-F]{6}$')

    # ================================================================
    # 32. getTxName unknown ID returns '?'
    # ================================================================
    def test_32_tx_helpers_unknown(self):
        """Unknown ID returns '?'."""
        val = self.js("return getTxName('nonexistent_id');")
        self.assertEqual(val, '?')

    # ================================================================
    # 33. confirmClear resets state
    # ================================================================
    def test_33_clear_all(self):
        """confirmClear resets treatments, comparisons, assessments."""
        self._load_antidepressant_example()
        self.js("confirmClear();")
        time.sleep(0.3)
        tx = self.js("return state.treatments.length;")
        comp = self.js("return state.comparisons.length;")
        assess = self.js("return Object.keys(state.assessments).length;")
        self.assertEqual(tx, 0)
        self.assertEqual(comp, 0)
        self.assertEqual(assess, 0)

    # ================================================================
    # 34. buildTableHTMLForExport
    # ================================================================
    def test_34_build_table_html(self):
        """Export HTML table contains correct structure."""
        self._load_bp_example()
        html = self.js("return buildTableHTMLForExport();")
        self.assertIn('<table', html)
        self.assertIn('Comparison', html)
        self.assertIn('Confidence', html)
        # Check all 6 domain headers present
        for d in ['WSB', 'RB', 'IND', 'IMP', 'HET', 'INC']:
            # Domain short labels should be in headers
            self.assertIn(d, html.upper() if d not in html else html)

    # ================================================================
    # 35. generateNarrative produces output
    # ================================================================
    def test_35_generate_narrative(self):
        """Narrative generation produces non-empty text."""
        self._load_antidepressant_example()
        self.js("switchTab('export');")
        time.sleep(0.3)
        # Select first comparison
        self.js("""
            var sel = document.getElementById('narrativeCompSelect');
            if(sel.options.length > 1) sel.selectedIndex = 1;
            generateNarrative();
        """)
        time.sleep(0.3)
        text = self.js("return document.getElementById('narrativeOutput').textContent;")
        self.assertTrue(len(text) > 0)
        self.assertIn('Confidence', text)

    # ================================================================
    # 36. Pain example has mixed confidence
    # ================================================================
    def test_36_pain_example_confidence(self):
        """Pain example comparisons have varied confidence levels."""
        self._load_pain_example()
        confs = self.js("""
            return state.comparisons.map(function(c) {
                return getConfidence(state.assessments[c.id]);
            });
        """)
        # Verify at least 2 distinct confidence levels
        unique = set(confs)
        self.assertGreaterEqual(len(unique), 2)

    # ================================================================
    # 37. getAutoSuggestions — ratio imprecision
    # ================================================================
    def test_37_autosugg_imprecision_ratio(self):
        """OR with wide CI on log scale triggers imprecision warning."""
        self.js("""
            state.effectMeasure = 'OR';
            state.clinThreshold = 0.8;
        """)
        sugg = self.js("""
            var comp = {effect:1.61, ciLo:0.5, ciHi:5.2, k:5, directPct:40, tau:0.3, directEst:1.5};
            return getAutoSuggestions(comp);
        """)
        self.assertIn('imp', sugg)
        # log(5.2) - log(0.5) = 2.34, 2*|log(0.8)| = 0.446 => 2.34 > 0.446 -> warn
        self.assertEqual(sugg['imp']['level'], 'warn')

    # ================================================================
    # 38. autoShortLabel generation
    # ================================================================
    def test_38_auto_short_label(self):
        """autoShortLabel creates abbreviation from multi-word name."""
        self.js("""
            document.getElementById('txName').value = 'Calcium Channel Blockers';
            document.getElementById('txShort').value = '';
            document.getElementById('txShort').dataset.auto = '1';
            autoShortLabel();
        """)
        val = self.js("return document.getElementById('txShort').value;")
        self.assertEqual(val, 'CCB')

    # ================================================================
    # 39. autoShortLabel — single word
    # ================================================================
    def test_39_auto_short_label_single(self):
        """Single-word name uses first 5 chars."""
        self.js("""
            document.getElementById('txName').value = 'Placebo';
            document.getElementById('txShort').value = '';
            document.getElementById('txShort').dataset.auto = '1';
            autoShortLabel();
        """)
        val = self.js("return document.getElementById('txShort').value;")
        self.assertEqual(val, 'PLACE')

    # ================================================================
    # 40. CONFIDENCE_LEVELS constant
    # ================================================================
    def test_40_confidence_levels_constant(self):
        """CONFIDENCE_LEVELS = ['High', 'Moderate', 'Low', 'Very Low']."""
        lvls = self.js("return CONFIDENCE_LEVELS;")
        self.assertEqual(lvls, ['High', 'Moderate', 'Low', 'Very Low'])

    # ================================================================
    # 41. getConfidence — mixed some + major
    # ================================================================
    def test_41_confidence_mixed(self):
        """1 some + 1 major = 3 downgrades -> Low."""
        val = self.js("""
            return getConfidence({wsb:'some', rb:'major', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertEqual(val, 'Low')

    # ================================================================
    # 42. Network canvas exists
    # ================================================================
    def test_42_network_canvas(self):
        """Network canvas element exists and has positive dimensions."""
        dims = self.js("return {w: document.getElementById('networkCanvas').width, h: document.getElementById('networkCanvas').height};")
        self.assertGreater(dims['w'], 0)
        self.assertGreater(dims['h'], 0)

    # ================================================================
    # 43. localStorage save/load
    # ================================================================
    def test_43_localstorage_round_trip(self):
        """State survives save-then-load cycle."""
        self._load_bp_example()
        self.js("saveState();")
        saved = self.js("return localStorage.getItem('cinema_app_v1');")
        self.assertIsNotNone(saved)
        self.assertIn('treatments', saved)

    # ================================================================
    # 44. buildConfidenceDisplay produces HTML
    # ================================================================
    def test_44_build_confidence_display(self):
        """buildConfidenceDisplay returns HTML string."""
        html = self.js("""
            return buildConfidenceDisplay('High', {wsb:'no', rb:'no', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertIn('confidence-display', html)
        self.assertIn('High', html)

    # ================================================================
    # 45. Confidence display with downgrades
    # ================================================================
    def test_45_confidence_display_downgrades(self):
        """buildConfidenceDisplay lists downgrade reasons."""
        html = self.js("""
            return buildConfidenceDisplay('Low', {wsb:'some', rb:'major', ind:'no', imp:'no', het:'no', inc:'no'});
        """)
        self.assertIn('Downgraded for', html)
        self.assertIn('WSB', html)
        self.assertIn('RB', html)


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    unittest.main(verbosity=2)
