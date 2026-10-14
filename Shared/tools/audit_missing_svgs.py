#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Layer Keyword-Based SVG Validator & Visual Asset Cue Engine.
Audits Core 2 question banks, Core 1A construction units, Core 1B reconstruction
units, and Golden Fixtures (@) to detect, classify, and track missing visual SVG figures.

Generates structured 'visual_asset_cue' objects and exports an authoring manifest
so that downstream authoring pipelines and learners never miss visual context.
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# --- SEMANTIC KEYWORD DEFINITIONS ---

TIER1_FIGURE_INDICATORS = [
    r"\bgiven figure\b",
    r"\bin the figure\b",
    r"\bshown in the figure\b",
    r"\bin the given diagram\b",
    r"\bshown below\b",
    r"\bas shown in\b",
    r"\bas shown\b",
    r"\bgiven below\b",
    r"\bnot drawn to scale\b",
    r"\brefer to the (?:given|following) (?:figure|diagram|pattern|graph)\b",
]

TIER2_LOGICAL_REASONING_CONSTRUCTS = [
    r"\b(?:placement of (?:the )?dots?|dots as in)\b",
    r"\bdot condition\b",
    r"\bdot situation\b",
    r"\b(?:paper|sheet) (?:is )?(?:folded|unfolded|punched|cut)\b",
    r"\bmirror image\b",
    r"\bwater image\b",
    r"\b(?:three )?positions? of a (?:die|dice|cube)\b",
    r"\bembedded (?:figure|in)\b",
    r"\bfigure matrix\b",
    r"\bfigure series\b",
    r"\bgroup the given figures\b",
    r"\bcomplete the (?:given )?pattern\b",
    r"\bcomplete the given figure\b",
]

TIER3_GEOMETRY_AND_DATA = [
    r"\bshaded (?:region|area|portion)\b",
    r"\bvenn diagram\b",
    r"\b(?:bar graph|pie chart|histogram|frequency polygon)\b",
    r"\bwhich of the following (?:figures?|shapes?)\b",
    r"\bfigure [a-d]\b",
    r"\bpattern [a-d]\b",
]

ALL_PATTERNS = TIER1_FIGURE_INDICATORS + TIER2_LOGICAL_REASONING_CONSTRUCTS + TIER3_GEOMETRY_AND_DATA

FALSE_POSITIVE_EXCLUSIONS = [
    r"\bfigure out\b",
    r"\bfigure of speech\b",
]

# Classification of visual demand type
def classify_visual_demand(text: str) -> str:
    text_lower = text.lower()
    if re.search(r"dot", text_lower):
        return "TOPOLOGICAL_DOT_CONFORMANCE"
    elif re.search(r"mirror|water image", text_lower):
        return "MIRROR_WATER_REFLECTION"
    elif re.search(r"die|dice|cube", text_lower):
        return "ORTHOGONAL_CUBE_NET_OR_PROJECTION"
    elif re.search(r"matrix|series|pattern", text_lower):
        return "GEOMETRIC_MATRIX_OR_PATTERN_COMPLETION"
    elif re.search(r"embedded|hidden", text_lower):
        return "SUBGRAPH_ISOMORPHISM_EMBEDDED_FIGURE"
    elif re.search(r"venn", text_lower):
        return "SET_THEORETIC_VENN_DIAGRAM"
    elif re.search(r"paper.*fold|punch", text_lower):
        return "PAPER_FOLDING_AND_SYMMETRY_PUNCH"
    elif re.search(r"bar graph|pie chart|histogram|frequency polygon", text_lower):
        return "STATISTICAL_DATA_GRAPH"
    elif re.search(r"shaded", text_lower):
        return "DECOMPOSED_SHADED_AREA_GEOMETRY"
    elif re.search(r"circle|cyclic|chord", text_lower):
        return "CIRCULAR_ARC_AND_CYCLIC_GEOMETRY"
    elif re.search(r"parallel|transversal|intersect", text_lower):
        return "PARALLEL_TRANSVERSAL_RAY_GEOMETRY"
    elif re.search(r"triangle|quadrilateral|polygon", text_lower):
        return "POLYGONAL_NETWORK_COUNTING_OR_PROOF"
    return "GENERAL_GEOMETRIC_CONSTRUCTION"

def generate_authoring_prompt_cue(qid: str, title: str, demand_type: str, stem: str, options: dict) -> str:
    opts_str = "; ".join(f"{k}: {v}" for k, v in options.items())
    return (
        f"Author an authentic, responsive vector SVG for [{qid}: {title}]. "
        f"Visual Demand: {demand_type}. "
        f"Context from stem: '{stem[:120]}...'. "
        f"Options representation: '{opts_str[:150]}...'. "
        f"Requirements: Clear viewBox, dark/light theme contrast, strict font-size >= 14px on all labels."
    )

class VisualAssetValidator:
    def __init__(self, figures_dir: str = "Mathematics/library/figures"):
        self.figures_dir = Path(figures_dir)
        self.existing_svgs = set()
        if self.figures_dir.exists():
            self.existing_svgs = set(f.name for f in self.figures_dir.glob("*.svg"))
            
        # Also check generate_question_svgs
        self.registered_svg_qids = set()
        try:
            sys.path.append("Mathematics/research")
            import generate_question_svgs
            with open("Mathematics/research/generate_question_svgs.py", "r", encoding="utf-8") as f:
                self.registered_svg_qids = set(re.findall(r"svgs\['([^']+)'\]", f.read()))
        except Exception:
            pass

    def scan_text_for_keywords(self, text: str) -> list[str]:
        matched = []
        text_lower = text.lower()
        for excl in FALSE_POSITIVE_EXCLUSIONS:
            if re.search(excl, text_lower):
                return []
        for pat in ALL_PATTERNS:
            if re.search(pat, text_lower):
                matched.append(pat)
        return matched

    def audit_core2_question_banks(self, bank_paths: list[str]) -> list[dict]:
        cues = []
        for bp in bank_paths:
            p = Path(bp)
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            for q in data.get("questions", []):
                qid = q["id"]
                title = q.get("title", "")
                stem = q.get("stem", "")
                options = q.get("options", {})
                fref = q.get("figure_ref")
                
                full_search_text = f"{stem} " + " ".join(str(v) for v in options.values())
                matched_kws = self.scan_text_for_keywords(full_search_text)
                
                # Check asset presence
                has_svg = False
                source = None
                if fref and fref in self.existing_svgs:
                    has_svg = True
                    source = f"file:{fref}"
                elif qid in self.registered_svg_qids:
                    has_svg = True
                    source = "generate_question_svgs"

                if matched_kws or fref:
                    demand_type = classify_visual_demand(full_search_text)
                    status = "RESOLVED" if has_svg else ("MISSING_FILE" if fref else "MISSING_FIGURE_REF")
                    
                    # Generate standard target file name if missing
                    target_file = fref or f"FIG-{qid}.svg"
                    
                    cue = {
                        "cue_id": f"CUE-{qid}",
                        "target_type": "CORE2_QUESTION",
                        "target_id": qid,
                        "paper": p.stem,
                        "title": title,
                        "topic": q.get("taxonomy", {}).get("topic_label", ""),
                        "visual_demand_type": demand_type,
                        "detected_keywords": matched_kws,
                        "figure_ref": fref,
                        "expected_asset_file": target_file,
                        "cue_status": status,
                        "svg_source": source,
                        "authoring_prompt_cue": generate_authoring_prompt_cue(qid, title, demand_type, stem, options),
                        "render_cue": {
                            "badge_label": "⚠️ VISUAL DIAGRAM REQUIRED" if not has_svg else "✓ FIGURE LINKED",
                            "message": f"Requires {demand_type.replace('_', ' ').title()} visual asset ({target_file})"
                        }
                    }
                    cues.append(cue)
        return cues

    def audit_core1a_units(self, units_dir: str = "Mathematics/units") -> list[dict]:
        cues = []
        u_path = Path(units_dir)
        if not u_path.exists():
            return cues
        for d in sorted(u_path.iterdir()):
            if not d.is_dir():
                continue
            c1a_files = list(d.glob("core1a-*.json"))
            for cf in c1a_files:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pkg_id = data.get("package_id", cf.stem)
                topic = data.get("topic_name", data.get("topic", d.name))
                reps = data.get("representation", [])
                linked_qids = data.get("linked_core2_refs", [])
                
                # Check representations for svg_element_ref
                has_rep_svgs = any(r.get("svg_element_ref") for r in reps)
                
                cues.append({
                    "cue_id": f"CUE-{pkg_id}",
                    "target_type": "CORE1A_UNIT",
                    "target_id": pkg_id,
                    "folder": d.name,
                    "topic": topic,
                    "representation_count": len(reps),
                    "has_representation_svg_refs": has_rep_svgs,
                    "linked_core2_refs": linked_qids,
                    "cue_status": "RESOLVED" if has_rep_svgs else "REPRESENTATION_NOTICE"
                })
        return cues

    def audit_core1b_units(self, units_dir: str = "Mathematics/units") -> list[dict]:
        cues = []
        u_path = Path(units_dir)
        if not u_path.exists():
            return cues
        for d in sorted(u_path.iterdir()):
            if not d.is_dir():
                continue
            c1b_files = list(d.glob("core1b-*.json"))
            for cf in c1b_files:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pkg_id = data.get("package_id", cf.stem)
                topic = data.get("topic", d.name)
                flow = data.get("interactive_tutor_flow", {})
                
                # Scan prompts in stage 1 through 4
                prompts_text = ""
                for stage_key in ["stage_1_predict", "stage_2_attempt", "stage_3_reconstruct", "stage_4_boundary_test"]:
                    stage_obj = flow.get(stage_key, {})
                    if isinstance(stage_obj, dict):
                        prompts_text += " " + str(stage_obj.get("prompt", "")) + " " + str(stage_obj.get("task", ""))
                
                matched = self.scan_text_for_keywords(prompts_text)
                cues.append({
                    "cue_id": f"CUE-{pkg_id}",
                    "target_type": "CORE1B_UNIT",
                    "target_id": pkg_id,
                    "folder": d.name,
                    "topic": topic,
                    "detected_visual_keywords": matched,
                    "requires_visual_inspection": len(matched) > 0,
                    "cue_status": "VISUAL_TUTOR_CONTEXT" if matched else "NO_VISUAL_TRIGGER"
                })
        return cues

    def audit_golden_fixtures(self, golden_dir: str = "golden/units") -> list[dict]:
        cues = []
        g_path = Path(golden_dir)
        if not g_path.exists():
            return cues
        for d in sorted(g_path.iterdir()):
            if not d.is_dir():
                continue
            manifest_file = d / "manifest.json"
            assets_dir = d / "assets"
            has_assets = assets_dir.exists() and len(list(assets_dir.glob("*.svg"))) > 0
            svg_list = [f.name for f in assets_dir.glob("*.svg")] if assets_dir.exists() else []
            
            cues.append({
                "cue_id": f"CUE-GOLDEN-{d.name}",
                "target_type": "GOLDEN_FIXTURE",
                "target_id": d.name,
                "has_svg_assets": has_assets,
                "svg_assets": svg_list,
                "cue_status": "RESOLVED" if has_assets else "NO_ASSETS_DIR"
            })
        return cues

    def run_full_audit(self, bank_pattern: str = "Mathematics/question-bank/*.json"):
        bank_paths = sorted(glob.glob(bank_pattern))
        c2_cues = self.audit_core2_question_banks(bank_paths)
        c1a_cues = self.audit_core1a_units()
        c1b_cues = self.audit_core1b_units()
        golden_cues = self.audit_golden_fixtures()
        
        return {
            "summary": {
                "core2_visual_questions_found": len(c2_cues),
                "core2_resolved_svgs": sum(1 for c in c2_cues if c["cue_status"] == "RESOLVED"),
                "core2_missing_svgs": sum(1 for c in c2_cues if c["cue_status"] != "RESOLVED"),
                "core1a_units_audited": len(c1a_cues),
                "core1b_units_audited": len(c1b_cues),
                "golden_fixtures_audited": len(golden_cues),
            },
            "core2_cues": c2_cues,
            "core1a_cues": c1a_cues,
            "core1b_cues": c1b_cues,
            "golden_cues": golden_cues
        }

def main():
    parser = argparse.ArgumentParser(description="Multi-Layer Keyword-Based SVG Validator & Visual Cue Engine")
    parser.add_argument("--export-cues", action="store_true", help="Export visual_cues_manifest.json")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if unresolved SVGs exist in Core 2")
    parser.add_argument("--manifest-path", default="Mathematics/research/visual_cues_manifest.json", help="Path for cues manifest output")
    args = parser.parse_args()

    validator = VisualAssetValidator()
    report = validator.run_full_audit()

    print("=== MULTI-LAYER KEYWORD-BASED SVG VALIDATOR & CUE ENGINE ===")
    summ = report["summary"]
    print(f"Core 2 Visual Questions Detected: {summ['core2_visual_questions_found']}")
    print(f"  -> Resolved SVGs: {summ['core2_resolved_svgs']}")
    print(f"  -> Missing SVGs: {summ['core2_missing_svgs']}")
    print(f"Core 1A Units Audited: {summ['core1a_units_audited']}")
    print(f"Core 1B Units Audited: {summ['core1b_units_audited']}")
    print(f"Golden Fixtures Audited: {summ['golden_fixtures_audited']}")
    print("-" * 60)

    # Show missing Core 2 questions
    missing = [c for c in report["core2_cues"] if c["cue_status"] != "RESOLVED"]
    if missing:
        print(f"LIST OF CORE 2 QUESTIONS REQUIRING SVGS ({len(missing)} items):")
        for m in missing[:15]:
            print(f"  [{m['target_id']}] {m['title'][:40]} | {m['visual_demand_type']} | Expected: {m['expected_asset_file']}")
        if len(missing) > 15:
            print(f"  ... and {len(missing) - 15} more.")
    else:
        print("ALL Core 2 visual questions have resolved SVGs!")

    if args.export_cues:
        out_path = Path(args.manifest_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Exported structured visual cue manifest to {out_path} ({out_path.stat().st_size} bytes)")

    if args.strict and summ["core2_missing_svgs"] > 0:
        print(f"\n[FAIL-CLOSED] Strict mode failed: {summ['core2_missing_svgs']} visual questions lack SVG assets.")
        sys.exit(1)

    print("\n[SUCCESS] Visual asset validation completed cleanly.")

if __name__ == "__main__":
    main()
