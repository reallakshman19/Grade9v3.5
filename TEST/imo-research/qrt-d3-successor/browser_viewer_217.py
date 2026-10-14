#!/usr/bin/env python3
"""#217: Verify 7x4 administrative viewer routes to the seven truthful D3 tiles."""
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "build/imo182-qrt/d3-successor/m3"
DEMANDS = ["RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY"]
ROLES = ["core1","core1a","core1b","core2a","core2b"]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

def main():
    idx=json.loads((OUT/"index.v1.json").read_text())
    assert idx["academic_and_owner"]=="PENDING"
    assert len(idx["cells"])==7
    for d in DEMANDS:
        row=json.loads((OUT/"tiles"/(d.lower()+".json")).read_text())
        assert row["cell_id"]=="QRT-"+d+"-D3"
        assert row["owner"]["qrt_decision_id"] is None
        assert all(row["review"][a]["qualified_verdict"]=="PENDING"
                   for a in ["H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3"])
        assert len(row["blueprints"])==5
        assert (OUT/"reviewer-packets"/(d.lower()+".md")).exists()
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        base=f"http://127.0.0.1:{server.server_port}"
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(viewport={"width":1280,"height":800})
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            response=page.goto(base+"/build/imo182-qrt/d3-successor/m3/index.html",wait_until="load")
            assert response and response.status==200
            assert page.locator("button[data-cell]").count()==7
            assert page.locator("#matrix tr").count()==7
            assert page.locator("#matrix td").count()==28
            assert page.locator("a[href*='/issues/200']").count()>0
            assert page.locator("a[href*='/issues/201']").count()>0
            assert page.locator("a[href*='/issues/203']").count()>0
            for d in DEMANDS:
                cell=f"QRT-{d}-D3"
                page.locator(f'button[data-cell="{cell}"]').click()
                assert page.locator("#selected").inner_text()==cell
                assert page.locator(f'button[data-cell="{cell}"]').get_attribute("aria-pressed")=="true"
                assert page.locator("#asks span").count()==12
                assert page.locator("#roles .role").count()==5
                assert page.locator("#decision").inner_text().find("PENDING")>=0
                json_path=page.locator("#links a").filter(has_text="Protocol JSON").first
                packet=page.locator("#links a").filter(has_text="Unsigned academic").first
                for elem in (json_path,packet):
                    href=elem.get_attribute("href")
                    target=page.request.get(base+"/build/imo182-qrt/d3-successor/m3/"+href)
                    assert target.status==200,(cell,href,target.status)
                if d in ("RETRIEVE","MODEL"):
                    assert page.locator("#status").inner_text().find("HOLD")>=0
                    assert page.locator("#roles a").count()==0
                else:
                    assert page.locator("#roles a").count()==5
                    for role in ROLES:
                        path=page.locator("#roles a").filter(has_text=role.upper()).first.get_attribute("href")
                        r=page.request.get(base+"/build/imo182-qrt/d3-successor/m3/"+path)
                        assert r.status==200,(cell,path,r.status)
            assert not errors,errors
            page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print("M3 28/28 matrix cells routable (21 external band issues), seven D3 tiles selectable, 5 actual native role links per nonheld D3, held links disabled; QRT PENDING")

if __name__=="__main__":
    main()
