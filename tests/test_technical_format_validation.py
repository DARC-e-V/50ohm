from __future__ import annotations

import unittest
import csv
import json
import tempfile
import subprocess
from pathlib import Path

from tools.technical_format_validation import (
    classify_pair,
    localized_math_label_relation,
    same_measurement_with_bit_capitalization,
    technical_signature,
)
from tools.apply_canonical_technical_format_review import apply_review
from tools.validate_canonical_technical_format import validate, write_decisions_csv, write_review_csv
from tools.validate_canonical_technical_format import _git_snapshot
from tools.technical_markup_repairs import plan_markup_repairs

TEST_TMP = Path(__file__).resolve().parents[2] / "tmp" / "technical-format-tests"
TEST_TMP.mkdir(parents=True, exist_ok=True)


class TechnicalFormatValidationTests(unittest.TestCase):
    def test_swapped_technical_regions_are_not_proposed_as_positional_fixes(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory) / "canonical"
            body = root / "sections" / "swap"
            body.mkdir(parents=True)
            (body / "body.de.md").write_text("$R_L$ $U_L$ $A=1$", encoding="utf-8")
            (body / "body.fr.md").write_text("$U_L$ $R_L$ $A=2$", encoding="utf-8")
            report = validate(root, "de", ["de", "fr"])
            self.assertEqual(report["correction_proposals"], [])
            self.assertEqual(len(report["manual_review_cases"]), 1)

    def test_identical_latex_payload_matches(self) -> None:
        source = technical_signature(r"Wert $P=\qty{10}{\watt}$.")
        target = technical_signature(r"Valeur $P=\qty{10}{\watt}$.")
        self.assertEqual(classify_pair(source, target), "match")

    def test_translated_prose_length_does_not_change_region_alignment(self) -> None:
        source = technical_signature(r"Wert $P=\qty{10}{\watt}$.")
        target = technical_signature(r"Puissance électrique $P=\qty{10}{\watt}$.")
        self.assertEqual(classify_pair(source, target), "match")

    def test_format_only_difference_is_reported(self) -> None:
        source = technical_signature("Leistung 20dB")
        target = technical_signature("Potenza 20 dB")
        self.assertEqual(classify_pair(source, target), "technical_format_mismatch")

    def test_decimal_separator_difference_is_format_not_value_difference(self) -> None:
        source = technical_signature(r"Frequenz $f=3.0\,\mathrm{MHz}$")
        target = technical_signature(r"Fréquence $f=3,0\,\mathrm{MHz}$")
        self.assertEqual(classify_pair(source, target), "technical_format_mismatch")

    def test_equivalent_fraction_syntax_is_normalized_to_german_format(self) -> None:
        source = technical_signature(r"Wert $x=\frac{5}{8}$")
        target = technical_signature(r"Valeur $x=5/8$")
        self.assertEqual(classify_pair(source, target), "technical_format_mismatch")

    def test_equivalent_unit_macro_alias_is_normalized_to_german_format(self) -> None:
        source = technical_signature(r"Wert $d=\qty{630}{\meter}$")
        target = technical_signature(r"Valeur $d=\qty{630}{\m}$")
        self.assertEqual(classify_pair(source, target), "technical_format_mismatch")

    def test_bit_unit_capitalization_is_preserved_by_locale(self) -> None:
        source = technical_signature("16 Bit")
        target = technical_signature("16 bit")
        self.assertEqual(classify_pair(source, target), "technical_format_mismatch")
        self.assertTrue(same_measurement_with_bit_capitalization("16 Bit", "16 bit"))

    def test_translated_formula_label_is_preserved_while_german_markup_is_proposed(self) -> None:
        relation = localized_math_label_relation(r"u_\mathrm{ZF}(t)", r"u_\text{FI}(t)")
        self.assertIsNotNone(relation)
        self.assertEqual(relation["proposed_text"], r"u_\mathrm{FI}(t)")
        source = technical_signature(r"Signal $u_\mathrm{ZF}(t)$")
        target = technical_signature(r"Segnale $u_\text{FI}(t)$")
        self.assertEqual(classify_pair(source, target), "localized_label_markup_mismatch")

        source = technical_signature(r"Frequenz $f_\mathrm{ZF}$")
        target = technical_signature(r"Fréquence $f_\mathrm{FI}$")
        self.assertEqual(classify_pair(source, target), "localized_formula_label")

    def test_same_payload_with_split_math_regions_is_reported_for_review(self) -> None:
        source = technical_signature(r"Wert $P=\qty{10}{\watt}$.")
        target = technical_signature(r"Valeur $P=$\qty{10}{\watt}.")
        self.assertEqual(classify_pair(source, target), "same_technical_tokens_different_boundaries")

    def test_math_payload_offsets_exclude_delimiters(self) -> None:
        result = technical_signature(r"Value $P=10$ here")
        region = result["regions"][0]
        self.assertEqual(region["text"], "P=10")
        self.assertEqual(region["payload_start"], 7)
        self.assertEqual(region["payload_end"], 11)

    def test_changed_quantity_is_a_technical_mismatch(self) -> None:
        source = technical_signature(r"$P=\qty{10}{\watt}$")
        target = technical_signature(r"$P=\qty{100}{\watt}$")
        self.assertEqual(classify_pair(source, target), "technical_token_mismatch")

    def test_delimiter_type_difference_is_visible_even_when_tokens_match(self) -> None:
        source = technical_signature(r"$f=\qty{7}{\mega\hertz}$")
        target = technical_signature(r"\(f=\qty{7}{\mega\hertz}\)")
        self.assertEqual(classify_pair(source, target), "same_technical_tokens_different_boundaries")

    def test_unmatched_math_delimiter_is_reported(self) -> None:
        result = technical_signature(r"Tension $\qty{8}{\volt}")
        self.assertEqual(result["syntax_findings"][0]["code"], "unmatched_math_delimiter")

    def test_nested_math_delimiter_is_reported_as_malformed(self) -> None:
        result = technical_signature(r"Value $\(\qty{8}{\volt}$")
        self.assertEqual(result["syntax_findings"][0]["code"], "nested_math_delimiter")

    def test_html_math_span_and_raw_measurement_are_detected(self) -> None:
        result = technical_signature(
            '<p>Fréquence <span class="math inline">\\qty{145,9}{\\mega\\hertz}</span>; 7 MHz.</p>'
        )
        self.assertEqual(len(result["regions"]), 2)
        self.assertIn(r"\qty", result["technical_tokens"])
        self.assertIn("145,9", result["technical_tokens"])
        self.assertIn("7", result["technical_tokens"])

    def test_script_content_is_not_compared_as_course_notation(self) -> None:
        result = technical_signature('<script>const value = "$P=10$";</script><p>$U=5$</p>')
        self.assertEqual(result["technical_tokens"], ["U", "=", "5"])

    def test_proposal_is_reviewable_and_apply_is_hash_checked(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory) / "canonical"
            body = root / "sections" / "test"
            body.mkdir(parents=True)
            (body / "body.de.md").write_text("German $P=10$", encoding="utf-8")
            (body / "body.fr.md").write_text("Français $P=100$", encoding="utf-8")

            report = validate(root, "de", ["de", "fr"])
            self.assertEqual(report["summary"]["critical_proposal_count"], 1)
            review_csv = Path(directory) / "review.csv"
            write_review_csv(report, review_csv)
            with review_csv.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["german_text"], "P=10")
            self.assertEqual(rows[0]["current_text"], "P=100")

            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps(report), encoding="utf-8")
            decisions_path = Path(directory) / "decisions.csv"
            write_decisions_csv(report, decisions_path)
            with decisions_path.open(encoding="utf-8-sig", newline="") as stream:
                decisions = list(csv.DictReader(stream))
            decisions[0]["decision"] = "apply"
            with decisions_path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=decisions[0].keys())
                writer.writeheader()
                writer.writerows(decisions)
            applied_manifest = Path(directory) / "applied.json"
            dry_run = apply_review(manifest_path, decisions_path, root, applied_manifest, apply=False)
            self.assertEqual(dry_run["mode"], "dry_run")
            self.assertEqual((body / "body.fr.md").read_text(encoding="utf-8"), "Français $P=100$")

            applied = apply_review(manifest_path, decisions_path, root, applied_manifest, apply=True)
            self.assertEqual(applied["mode"], "applied")
            self.assertEqual((body / "body.fr.md").read_text(encoding="utf-8"), "Français $P=10$")

    def test_format_equivalence_must_apply_the_german_form(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory) / "canonical"
            body = root / "sections" / "fraction"
            body.mkdir(parents=True)
            (body / "body.de.md").write_text(r"Wert $x=\frac{5}{8}$", encoding="utf-8")
            (body / "body.fr.md").write_text(r"Valeur $x=5/8$", encoding="utf-8")

            report = validate(root, "de", ["de", "fr"])
            self.assertEqual(report["summary"]["format_review_count"], 1)
            self.assertEqual(
                report["correction_proposals"][0]["proposed_text"],
                r"Valeur $x=\frac{5}{8}$",
            )
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps(report), encoding="utf-8")
            decisions_path = Path(directory) / "decisions.csv"
            write_decisions_csv(report, decisions_path)
            with decisions_path.open(encoding="utf-8-sig", newline="") as stream:
                decisions = list(csv.DictReader(stream))
            self.assertEqual(decisions[0]["decision"], "apply")
            decisions[0]["decision"] = "keep"
            with decisions_path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=decisions[0].keys())
                writer.writeheader()
                writer.writerows(decisions)

            with self.assertRaisesRegex(ValueError, "must apply the German reference form"):
                apply_review(
                    manifest_path,
                    decisions_path,
                    root,
                    Path(directory) / "applied.json",
                    apply=False,
                )

    def test_numeric_and_physical_indices_are_not_translated_labels(self) -> None:
        for source, target in [(r"R_{\mathrm{1}}", r"R_{\mathrm{2}}"), (r"U_{\mathrm{C}}", r"U_{\mathrm{E}}")]:
            self.assertIsNone(localized_math_label_relation(source, target))
            self.assertEqual(classify_pair(technical_signature(f"${source}$"), technical_signature(f"${target}$")), "technical_token_mismatch")

    def test_isolated_commands_and_missing_braces_are_reported(self) -> None:
        self.assertEqual(technical_signature(r"Valeur \alpha")["regions"][0]["text"], r"\alpha")
        self.assertTrue(technical_signature(r"$\qty{10}{\watt$")["syntax_findings"])

    def test_reordered_dipole_values_keep_their_meaning_while_units_are_fixed(self) -> None:
        source = r"Bei $\qty{630}{\meter}$ ist die Länge $\qty{315}{\meter}$."
        target = r"Lunghezza $\qty{315}{\m}$ a $\qty{630}{\m}$."
        repaired, operations = plan_markup_repairs(source, target, "it")
        self.assertEqual(repaired, r"Lunghezza $\qty{315}{\meter}$ a $\qty{630}{\meter}$.")
        self.assertEqual(len(operations), 2)
        self.assertEqual(classify_pair(technical_signature(source), technical_signature(target)), "same_technical_tokens_different_order")

    def test_plain_source_measurement_removes_target_only_math(self) -> None:
        for source, target, expected in [
            (r"<b>50 Hz / 100 Hz</b><p>$\qty{50}{\hertz}$ et $\qty{100}{\hertz}$</p>",
             r"<b>$\qty{50}{\hertz}$ / $\qty{100}{\hertz}$</b><p>$\qty{50}{\hertz}$ et $\qty{100}{\hertz}$</p>",
             r"<b>50 Hz / 100 Hz</b><p>$\qty{50}{\hertz}$ et $\qty{100}{\hertz}$</p>"),
            ("Strom 0,5 Ampere", r"Courant $\qty{0,5}{\ampere}$", "Courant 0,5 ampère"),
            ("360° entspricht", r"$\qty{360}{\degree}$ correspond", "360° correspond"),
        ]:
            repaired, _ = plan_markup_repairs(source, target, "fr")
            self.assertEqual(repaired, expected)

    def test_real_astro_blocker_shapes_are_repaired_without_changing_prose(self) -> None:
        cases = [
            (r"Dämpfung ($\unit{\dB}$); $\sqrt{2} = 1,41$", r"Atténuation (\unit{\dB}); \sqrt{2} = 1,41", r"Atténuation ($\unit{\dB}$); $\sqrt{2} = 1,41$"),
            (r"$\qty{145,9}{\mega\hertz}\cdot 4 = \qty{583,6}{\mega\hertz}$", r"Fréquence (\qty{145,9}{\mega\hertz} \cdot 4 = \qty{583,6}{\mega\hertz})", r"Fréquence ($\qty{145,9}{\mega\hertz}\cdot 4 = \qty{583,6}{\mega\hertz}$)"),
            (r"$\qty{8}{\volt}$ an $R_1$; $\qty{4}{\volt}$ an $R_2$", r"($\qty{8}{\volt}) su $R_1$; ($\qty{4}{\volt}) su $R_2$", r"($\qty{8}{\volt}$) su $R_1$; ($\qty{4}{\volt}$) su $R_2$"),
            (r"$a =\log_{10} (b)$, falls $b=10^{a}$", r"a = \log_{10} (b), se b=10^{a}", r"$a =\log_{10} (b)$, se $b=10^{a}$"),
            (r"$P_\mathrm{Sender}=\qty{10}{\watt}$", r"<span class=\"math inline\">P_\mathrm{trasmettitore}=\qty{10}{\watt}</span>", r"$P_\mathrm{trasmettitore}=\qty{10}{\watt}$"),
            (r"$\lambda / 2$ et $\lambda$", "λ/2 et ($\nlambda$)", r"$\lambda / 2$ et ($\lambda$)"),
        ]
        # The HTML fixture contains actual attribute quotes, not escaped TeX quotes.
        for source, target, expected in cases:
            target = target.replace(r'\"', '"')
            with self.subTest(target=target):
                repaired, operations = plan_markup_repairs(source, target, "it")
                self.assertEqual(repaired, expected)
                self.assertTrue(operations)
                self.assertEqual(plan_markup_repairs(source, repaired, "it"), (repaired, []))

    def test_extra_unpaired_formula_occurrences_are_not_wrapped(self) -> None:
        source = r"$\qty{8}{\volt}$"
        target = r"\qty{8}{\volt} puis \qty{8}{\volt}"
        self.assertEqual(plan_markup_repairs(source, target, "fr"), (target, []))

    def test_markup_import_replays_plan_and_rejects_changed_values(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory) / "canonical"
            body = root / "sections/test"
            body.mkdir(parents=True)
            (body / "body.de.md").write_text(r"$\qty{8}{\volt}$")
            target = body / "body.fr.md"
            target.write_text(r"Tension \qty{8}{\volt}")
            report = validate(root, "de", ["de", "fr"], markup_only=True)
            manifest = Path(directory) / "plan.json"
            decisions = Path(directory) / "decisions.csv"
            manifest.write_text(json.dumps(report))
            write_decisions_csv(report, decisions)
            audit = Path(directory) / "applied.json"
            apply_review(manifest, decisions, root, audit, apply=False)
            self.assertEqual(target.read_text(), r"Tension \qty{8}{\volt}")
            report["correction_proposals"][0]["proposed_text"] = r"Tension $\qty{80}{\volt}$"
            manifest.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "cannot be reproduced"):
                apply_review(manifest, decisions, root, audit, apply=True)
            self.assertEqual(target.read_text(), r"Tension \qty{8}{\volt}")

    def test_git_snapshot_detects_changes_when_called_from_canonical_directory(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            canonical = root / "canonical"
            canonical.mkdir()
            (canonical / "body.de.md").write_text("source")
            snapshot = _git_snapshot(canonical)
            self.assertFalse(snapshot["canonical_worktree_clean"])
            self.assertTrue(snapshot["canonical_worktree_status"])


if __name__ == "__main__":
    unittest.main()
