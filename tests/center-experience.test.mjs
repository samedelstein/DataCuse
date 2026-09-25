import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {publicationFiles} from '../scripts/publication-lib.mjs';
import {parseStory,articlePage} from '../scripts/story-lib.mjs';
const root=new URL('../content/5_geographic_center/',import.meta.url);
const script=await fs.readFile(new URL('images/center-game.js',root),'utf8');
function harness(){
  const elements=new Map(),pending=[];
  function element(id){
    if(!elements.has(id)){
      const attrs=new Map();if(['trip','center-marker'].includes(id))attrs.set('hidden','');
      elements.set(id,{id,attrs,dataset:{},style:{},listeners:{},textContent:'',value:'',open:false,hidden:false,
        addEventListener(name,fn){this.listeners[name]=fn;},setAttribute(k,v){attrs.set(k,String(v));},removeAttribute(k){attrs.delete(k);},hasAttribute(k){return attrs.has(k);},toggleAttribute(k,force){if(force)attrs.set(k,'');else attrs.delete(k);},focus(){},scrollIntoView(){}});
    }return elements.get(id);
  }
  const document={getElementById:element,querySelectorAll:()=>[],addEventListener(){}};
  const window={isSecureContext:true,addEventListener(){},removeEventListener(){}};
  const navigator={geolocation:{getCurrentPosition(success,error){pending.push({success,error});}}};
  vm.runInNewContext(script,{document,window,navigator,screen:{orientation:{angle:0}},setInterval:()=>1,clearInterval(){},console});
  const reveal=()=>{element('center-answer').open=true;element('center-answer').listeners.toggle();};
  const key=()=>element('map').listeners.keydown({key:'ArrowUp',preventDefault(){}});
  return {element,pending,reveal,key};
}
test('a guess shows the blue dot without exposing the answer; reveal scores it; reset hides the answer',()=>{
  const h=harness();h.key();
  assert.equal(h.element('trip').hasAttribute('hidden'),false);
  assert.equal(h.element('center-marker').hasAttribute('hidden'),true);
  assert.equal(h.element('route').hasAttribute('hidden'),true);
  h.reveal();assert.match(h.element('guess-score').textContent,/miles/);
  assert.equal(h.element('center-marker').hasAttribute('hidden'),false);
  assert.equal(h.element('route').hasAttribute('hidden'),false);
  const pin=h.element('user-pin').attrs.get('cy');h.key();
  assert.equal(h.element('user-pin').attrs.get('cy'),pin,'revealed guesses stay locked');
  h.element('try-again').onclick();
  assert.equal(h.element('center-answer').open,false);
  assert.equal(h.element('center-marker').hasAttribute('hidden'),true);
  assert.equal(h.element('trip').hasAttribute('hidden'),true);
});
test('location denial and timeout provide a fallback without inventing a position',()=>{
  const h=harness();h.reveal();h.element('locate').listeners.click();h.pending[0].error({code:1});
  assert.match(h.element('error').textContent,/denied/);assert.equal(h.element('locate').disabled,false);
  assert.equal(h.element('trip').hasAttribute('hidden'),true);
  h.element('locate').listeners.click();h.pending[1].error({code:3});assert.match(h.element('error').textContent,/timed out/);
});
test('poor GPS accuracy hides the bearing; clearing discards a late GPS response',()=>{
  const h=harness();h.reveal();h.element('locate').listeners.click();
  h.pending[0].success({coords:{latitude:43.041,longitude:-76.144,accuracy:500}});
  assert.match(h.element('direction').textContent,/reliable direction/);
  assert.equal(h.element('dial').dataset.inactive,'true');
  h.element('locate').listeners.click();h.element('clear').onclick();
  h.pending[1].success({coords:{latitude:43.06,longitude:-76.16,accuracy:5}});
  assert.equal(h.element('distance').textContent,'Where are you?');
  assert.equal(h.element('trip').hasAttribute('hidden'),true);
});
test('same-page story includes bundled script and style assets without a separate app link',async()=>{
  const files=await publicationFiles(fileURLToPath(root));
  assert.ok(files.has('assets/center-game.js'));assert.ok(files.has('assets/center-game.css'));
  assert.ok(files.has('assets/syracuse-balance-point.png'));
  const markdown=files.get('index.md');
  const story=parseStory(markdown.replace('status: draft','status: published'),'syracuse-geographic-center','9999-12-31');
  const html=articlePage(story);
  assert.match(html,/<script src="assets\/center-game.js" defer><\/script>/);
  assert.match(html,/<link rel="stylesheet" href="assets\/center-game.css">/);
  assert.match(html,/<details id="center-answer">/);
  assert.doesNotMatch(html,/center-compass\.html/);
  assert.doesNotMatch(story.summary,/McBride|43\.040/);
  assert.throws(()=>parseStory(markdown.replace('status: draft','status: published').replace('assets/center-game.js','https://example.com/tracker.js'),'syracuse-geographic-center','9999-12-31'),/invalid scripts/);
});
