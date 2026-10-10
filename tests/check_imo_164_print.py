#!/usr/bin/env python3
"""Inspect real Chromium-produced held A4 PDFs; not human print certification."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from pypdf import PdfReader

A4_WIDTH, A4_HEIGHT = 595.276, 841.890

def check(folder: Path) -> dict:
    receipt=json.loads((folder/"browser-receipt.json").read_text())
    variant=receipt["variant"]
    print_entry=receipt["print"]
    assert print_entry["status"] == "PENDING_PDF_STRUCTURE_CHECK"
    assert print_entry["state"] == "AFTER_LEARNER_COMMIT_AND_SOLUTION_OPEN"
    assert receipt["refresh"] == "CORE2B_FAILS_CLOSED_AND_REQUIRES_A_NEW_ATTEMPT"
    file=folder/print_entry["path"]
    assert file.read_bytes().startswith(b"%PDF-"), (variant,"pdf magic")
    reader=PdfReader(file)
    assert 1 <= len(reader.pages) <= 20, (variant,len(reader.pages))
    for index,page in enumerate(reader.pages):
        width,height=float(page.mediabox.width),float(page.mediabox.height)
        assert abs(width-A4_WIDTH)<2 and abs(height-A4_HEIGHT)<2, (variant,index,width,height)
    text=" ".join(page.extract_text() or "" for page in reader.pages)
    assert len(text)>100, (variant,"too little extracted text",len(text))
    assert "divisible" in text.lower(), (variant,"math stem absent from print")
    assert "SOF-IMO-G09-" not in text, (variant,"unexpected publisher source content")
    return {"variant":variant,"pages":len(reader.pages),"extracted_chars":len(text),
            "page_format":"A4","status":"STRUCTURE_AND_TEXT_PASS",
            "media_box_points":[A4_WIDTH,A4_HEIGHT],"path":file.name}

def main(argv):
    assert len(argv)==2, "usage: check_imo_164_print.py <five-evidence> <boundary-evidence>"
    out=[check(Path(folder)) for folder in argv]
    assert {x["variant"] for x in out}=={"five","boundary"},out
    for folder,row in zip(argv,out):
        (Path(folder)/"a4-print-validation.json").write_text(json.dumps(row,indent=2)+"\n")
    print("VERIFIED_A4_HELD_PDF",json.dumps(out))
if __name__=="__main__":
    main(sys.argv[1:])
