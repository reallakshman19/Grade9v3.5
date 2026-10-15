// Negative mutation suite: the bad witnesses MUST fail the exact exported
// predicates used by the real Chromium runner.
import assert from "node:assert/strict";
import { q022HintPreservesProtectedWork, katexWitnessPasses, coreRouteVisible } from "./qrt-g2-browser-predicates.mjs";
let count = 0;
function check(name, actual, expected) {
  assert.equal(actual, expected, name);
  count++;
  console.log("PASS", name, expected ? "(positive control)" : "(rejected mutant)");
}
const good = "Set a = 3 and b = √2 in the identity from Hint 1. Carry out the difference of squares yourself, then decide whether your computed value can be written as a ratio of two integers.";
check("H2 clean method cue", q022HintPreservesProtectedWork(good), true);
check("H2 numeric final W appended despite method cue",
  q022HintPreservesProtectedWork(good+" The numerical answer is 7, which is rational."), false);
check("H2 numeric answer token without expansion",
  q022HintPreservesProtectedWork(good+" The number is 7."), false);
check("H2 completed arithmetic",
  q022HintPreservesProtectedWork(good+" 9 − 2 = 7."), false);
check("H2 declarative keyed class without 7",
  q022HintPreservesProtectedWork(good+" The value is rational."), false);
check("H2 reverse declarative keyed class",
  q022HintPreservesProtectedWork(good+" Rational is the answer."), false);
check("H2 unrelated text lacking tactical cue",
  q022HintPreservesProtectedWork("The answer is 7."), false);
const rendered = {katexApi:"function",katexNodes:2999,katexQuestionNodes:200,katexQuestionErrors:0};
check("KaTeX render present",katexWitnessPasses(rendered),true);
check("KaTeX no spans",katexWitnessPasses({...rendered,katexNodes:0}),false);
check("KaTeX no in-question spans",katexWitnessPasses({...rendered,katexQuestionNodes:0}),false);
check("KaTeX runtime errors",katexWitnessPasses({...rendered,katexQuestionErrors:1}),false);
check("KaTeX API absent",katexWitnessPasses({...rendered,katexApi:"undefined"}),false);
const visible={tabActive:true,highlighted:true,
  ancestorStyles:[{display:"block",visibility:"visible",opacity:"1"},{display:"block",visibility:"visible",opacity:"1"}],
  rect:{top:90,left:30,right:400,bottom:450,width:370,height:360},
  viewport:{width:1366,height:854}};
check("Core target genuinely on screen",coreRouteVisible(visible),true);
check("Core target hidden by CSS ancestor",coreRouteVisible({...visible,ancestorStyles:[...visible.ancestorStyles,{display:"none",visibility:"visible",opacity:"1"}]}),false);
check("Core target CSS hidden",coreRouteVisible({...visible,ancestorStyles:[{display:"block",visibility:"hidden",opacity:"1"}]}),false);
check("Core target CSS transparent ancestor",coreRouteVisible({...visible,ancestorStyles:[{display:"block",visibility:"visible",opacity:"0"}]}),false);
check("Core target offscreen",coreRouteVisible({...visible,rect:{top:1300,left:30,right:400,bottom:1500,width:370,height:200}}),false);
check("Core target zero layout",coreRouteVisible({...visible,rect:{top:90,left:30,right:30,bottom:450,width:0,height:360}}),false);
check("Core target inactive tab",coreRouteVisible({...visible,tabActive:false}),false);
console.log("BROWSER CONTRACT MUTATIONS",count,"/",count,"PASS");
