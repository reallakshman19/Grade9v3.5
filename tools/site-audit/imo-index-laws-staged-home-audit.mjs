/** Browser-only functional check of held, authoring-approved IMO Index Laws staging.
 * This is not academic, screen-reader, learner or release approval.
 */
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, sep, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('../../public/', import.meta.url)));
const mime = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8',
 '.css':'text/css; charset=utf-8', '.svg':'image/svg+xml' };
const server = createServer(async (req,res)=>{
 try {
  const url = new URL(req.url || '/', 'http://localhost');
  const pathname = decodeURIComponent(url.pathname);
  const path = resolve(root, '.' + pathname, pathname.endsWith('/') ? 'index.html' : '');
  if (path !== root && !path.startsWith(root + sep)) { res.writeHead(403); res.end(); return; }
  if (!(await stat(path)).isFile()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, {'content-type':mime[extname(path)] || 'application/octet-stream'});
  res.end(await readFile(path));
 } catch { res.writeHead(404); res.end(); }
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const addr=server.address();
const base='http://127.0.0.1:'+addr.port;
const errors=[];
let browser;
try {
 browser=await chromium.launch({headless:true});
 const passes=[];
 for(const width of [320,390,768,1280]){
  const page=await browser.newPage({viewport:{width,height:850}});
  const onError=e=>errors.push('viewport='+width+': '+e.message);
  page.on('pageerror',onError);
  await page.goto(base+'/mathematics/index.html');
  const entry=page.locator('a[data-imo-staging="NS-INDEX-LAWS-ACADEMIC-HOLD"]');
  if(await entry.count()!==1) throw new Error('Missing staged hub entry at '+width);
  await entry.click();
  if(!(await page.locator('h1').innerText()).includes('Number Systems')) throw new Error('Wrong topic route');
  if(await page.locator('[data-imo-release="ACADEMIC_HOLD"]').count()!==1) throw new Error('Topic missing hold');
  await page.locator('a[href="index-laws/index.html"]').click();
  if(!(await page.locator('h1').innerText()).includes('Index Laws'))throw new Error('Wrong subtopic route');
  if(await page.locator('[data-imo-core-action-state="ALL_HELD"]').count()!==1)throw new Error('Core roles not held');
  if(await page.locator('a[href*="core1a.html"],a[href*="core2.html"],a[href*="core2a.html"],a[href*="/test/"]').count())throw new Error('Leaking held product hyperlink');
  const roleText=await page.locator('[data-imo-core-action-state="ALL_HELD"]').innerText();
  for(const role of ['Core1A','Core2A','Core2'])if(!roleText.includes(role))throw new Error('Missing role: '+role);
  const scroll=await page.evaluate(()=>document.documentElement.scrollWidth);
  if(scroll>width+1)throw new Error('Horizontal overflow '+scroll+' > '+width);
  await page.reload();
  if(await page.locator('[data-imo-core-action-state="ALL_HELD"]').count()!==1)throw new Error('Deep-link reload lost hold');
  const returnLink=page.locator('a[href="../index.html"]').last();
  await returnLink.focus();
  await page.keyboard.press('Enter');
  if(!(await page.locator('h1').innerText()).includes('Number Systems'))throw new Error('Keyboard return failed');
  await page.goto(base+'/mathematics/imo-grade9/index.html');
  const imo=page.locator('a[href="../number-systems/index-laws/index.html"]');
  if(await imo.count()!==1)throw new Error('Missing IMO index route');
  await imo.click();
  if(await page.locator('[data-imo-release="ACADEMIC_HOLD"]').count()!==1)throw new Error('IMO route bypassed hold');
  passes.push({width,hub_to_topic:true,topic_to_subtopic:true,imo_to_subtopic:true,held:true,keyboard:true,horizontal_overflow:false});
  await page.close();
 }
 if(errors.length)throw new Error('Browser JS page errors: '+JSON.stringify(errors));
 console.log(JSON.stringify({result:'PASS',scope:'STAGED_STATUS_ONLY_NOT_RELEASE',chromium:true,scenarios:passes,page_errors:errors.length}));
} finally { await browser?.close();await new Promise(r=>server.close(r));}
