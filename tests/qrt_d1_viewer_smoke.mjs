// Exercise the existing Q003 7x4 administrative viewer without dependencies,
// using a narrow DOM shim: this is not a learner renderer or browser WCAG pass.
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const file='TEST/imo-research/qrt-tiles/q003-model-d2/index.html';
const html=readFileSync(file,'utf8');
const scripts=[...html.matchAll(/<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
assert(scripts.length>=3,'Expected two inert JSON payloads and one UI script');
const js=scripts.at(-1);
new vm.Script(js,{filename:'q003-inline-viewer.js'}); // syntax check

class Element {
  constructor(tag='div'){
    this.tagName=tag;this.children=[];this._text='';this.attrs={};
    this.listeners={};this.dataset={};this.hidden=false;this.className='';
    this.classList={toggle:()=>{}};
  }
  set textContent(v){this._text=String(v);this.children=[]}
  get textContent(){return this._text+this.children.map(x=>typeof x==='string'?x:x.textContent).join('')}
  append(...v){this.children.push(...v)}
  replaceChildren(){this.children=[];this._text=''}
  setAttribute(k,v){this.attrs[k]=v}
  addEventListener(k,fn){this.listeners[k]=fn}
  querySelectorAll(selector){
    if(selector!=='button')throw Error('Unsupported mock selector '+selector);
    const result=[];for(const child of this.children)if(child instanceof Element){
      if(child.tagName==='button')result.push(child);
      result.push(...child.querySelectorAll(selector))
    }
    return result
  }
}
const ids=new Map();
const document={
  createElement:tag=>new Element(tag),
  getElementById:id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id)}
};
const band=html.match(/<script id="band-evidence" type="application\/json">([\s\S]*?)<\/script>/);
const metadata=html.match(/<script id="metadata" type="application\/json">([\s\S]*?)<\/script>/);
assert(band&&metadata,'Expected inert source-safe metadata');
document.getElementById('band-evidence').textContent=band[1];
document.getElementById('metadata').textContent=metadata[1];
const data=JSON.parse(band[1]);assert.equal(data.cells.length,28);
vm.runInNewContext(js,{document,console},{timeout:3000});
const grid=document.getElementById('grid');
const buttons=grid.querySelectorAll('button');
assert.equal(buttons.length,28);
const d1=['RETRIEVE','EXPLAIN','APPLY','MODEL','REPRESENT','SYNTHESIZE','JUSTIFY'];
for(const demand of d1){
 const id='QRT-'+demand+'-D1';const b=buttons.find(x=>x.dataset.cell===id);
 assert(b&&b.listeners.click,'Missing click handler '+id);
 b.listeners.click();
 const pane=document.getElementById('selected-cell-evidence');
 const detail=document.getElementById('d1-detail');
 assert.equal(pane.hidden,false,id+' evidence panel hidden');
 assert.match(document.getElementById('selected-cell-heading').textContent,new RegExp(id));
 assert.match(detail.textContent,/Academic decision: PENDING/);
 assert.match(detail.textContent,/Owner decision: PENDING/);
 assert.match(detail.textContent,/core1\.html/);
 assert.match(detail.textContent,/core2b\.html/);
 assert.match(detail.textContent,/index\.html/);
 const anchors=[];
 (function collect(node){if(typeof node==='string')return;if(node.tagName==='a')anchors.push(node);for(const x of node.children)collect(x)})(detail);
 assert(anchors.some(a=>a.href.endsWith('/d1/'+demand.toLowerCase()+'.tile.v1.json')));
 assert(anchors.some(a=>String(a.href).includes('/actions/runs/')));
 assert(anchors.some(a=>String(a.href).includes('G-IMO-G9-FIVE-CORE-20261012')));
 assert(anchors.some(a=>String(a.href).includes('/TEST/imo-research/qrt-d1/')));
 if(demand==='JUSTIFY')assert(anchors.some(a=>String(a.href).endsWith('/d1/justify-reasoning-probes.v1.json')),'Missing human-only explanation feedback review set');
 const actual=data.cells.find(x=>x.id===id);
 assert.equal(document.getElementById('selected-cell-artifact').href,actual.url);
}
// Switching to Q003/D2 restores existing private-custody handling.
buttons.find(x=>x.dataset.cell==='QRT-MODEL-D2').listeners.click();
assert.equal(document.getElementById('selected-cell-evidence').hidden,true);
assert.match(document.getElementById('selection').textContent,/Q003/);
console.log('QRT 28-cell viewer: seven D1 evidence clicks, six hashes, pinned links and original Q003 selection PASS');
