"""Bundle the guessing experience and compass into the canonical article page."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parent
source=(R/'app-template.html').read_text(encoding='utf-8-sig')
config=(R/'map_config.json').read_text()
core=(R/'compass-core.mjs').read_text(encoding='utf-8-sig').replace('export ','')
map_section=re.search(r'<section aria-label="Choose a starting point on the map">(.*?)</section>',source,re.S).group(1)
map_section=map_section.replace('<h2>Put yourself on the map.</h2>','')
map_section=map_section.replace('__MAP__',(R/'app-map.svg').read_text())
map_section=map_section.replace('<g id="center-marker">','<g id="center-marker" hidden>')
map_section=map_section.replace('<span><i class="swatch"></i>Calculated center</span>','<span id="center-key" hidden><i class="swatch"></i>Calculated center</span>')
map_section=map_section.replace('Your chosen location</span>','<span id="pin-label">Your guess</span></span>')
map_section=map_section.replace('Tap anywhere to drop a pin. Zoom in for a closer look. Keyboard: focus the map and use the arrow keys.','Tap where you think the center is. You can move your guess until you reveal the answer. Keyboard: focus the map and use the arrow keys.')
map_section+='<p id="guess-feedback" role="status">No guess yet. Pick a spot, or open the answer to skip guessing.</p><p id="map-result" hidden></p><button id="try-again" hidden>Guess again</button>'
controls=re.search(r'<section aria-label="Your direction and distance">(.*?)</section>',source,re.S).group(1)
controls=controls.replace('<button id="clear" hidden>Clear location</button>','<button id="pick-origin">Choose a starting point on the map</button><button id="clear" hidden>Clear location</button>')
controls=controls.replace('Your location stays on this page. Or tap the map to choose a starting point.','Your location stays on this page. Distance is straight-line, not walking or driving distance.')
controls+='<p class="note">Bearings are measured from true north. Phone compass readings are approximate; sensor quality and magnetic north can introduce error. This app does not send or save your location, load third-party maps, or use IP-based location. Your browser may use its own location service when you grant permission.</p>'
script=re.search(r'<script>(.*?)</script>',source,re.S).group(1)
script=script.replace('__CORE__',core).replace('__CONFIG__',config)
script=script.replace("$('center-coordinate').textContent=`${config.center.lat.toFixed(5)}, ${config.center.lon.toFixed(5)}`;",'')
script=script.replace("let view=[0,0,900,900], orientationTimer=null;","let view=[0,0,900,900], orientationTimer=null;\nlet revealed=false, guess=null, selectingOrigin=false;")
script=script.replace('function choose(point,kind=', 'function chooseOrigin(point,kind=')
script=script.replace("position={...point,accuracy};source=kind;$('error').textContent='';render();", "position={...point,accuracy};source=kind;$('error').textContent='';$('pin-label').textContent='Your chosen location';render();$('map-result').hidden=false;$('map-result').textContent=`${$('distance').textContent} · ${$('direction').textContent}`;")
script=script.replace("source==='device'?'From your reported location':'From your chosen point'", "source==='device'?'From your reported location':source==='guess'?'From your guess':'From your chosen point'")
script=script.replace('You are within about 100 feet.','This point is within about 100 feet.')
# Keyboard coordinates must use the guess before the reveal, without accessing the answer.
script=script.replace('const point=position?toMap(position):centerPixel;', 'const point=position?toMap(position):guess?toMap(guess):[450,450];')
script=script.replace('let anchor=position?toMap(position):centerPixel;', 'let anchor=position?toMap(position):guess?toMap(guess):[450,450];')
script=script.replace("$('map').setAttribute('viewBox',view.join(' '));mapScale();", "$('map').setAttribute('viewBox',view.join(' '));mapScale();")
# The initial guess does not draw a line to the hidden answer.
extra=r'''
const clearLocation=$('clear').onclick;
$('clear').onclick=()=>{clearLocation();$('map-result').hidden=true;};
function choose(point,kind='pin',accuracy=0){
  if(!revealed){
    guess={lat:point.lat,lon:point.lon};
    const [x,y]=toMap(guess);
    $('trip').removeAttribute('hidden');$('route').setAttribute('hidden','');
    $('user-pin').setAttribute('cx',x);$('user-pin').setAttribute('cy',y);
    $('guess-feedback').textContent='Your pin is down. Move it if you like, then open the answer below.';
    $('pin-label').textContent='Your guess';return;
  }
  if(kind==='pin'&&!selectingOrigin)return;
  $('route').removeAttribute('hidden');
  chooseOrigin(point,kind,accuracy);
}
$('center-answer').addEventListener('toggle',()=>{
  if(!$('center-answer').open || revealed)return;
  revealed=true;selectingOrigin=false;
  $('center-marker').removeAttribute('hidden');$('center-key').hidden=false;$('try-again').hidden=false;
  $('guess-feedback').textContent='Answer revealed. Your guess is now locked.';
  $('map-note').textContent='The rust dot is the calculated center. Open the compass below to choose a starting point or use your location.';
  if(guess){
    const metres=distanceBearing(guess,config.center).distanceMetres;
    const miles=metres/1609.344;
    $('guess-score').textContent=metres<30?'Right on the neighborhood: your guess was within about 100 feet of the calculated center.':`Your guess was ${miles.toFixed(miles<1?2:1)} miles from the calculated center, in a straight line.`;
    const [x,y]=toMap(guess);for(const [key,value] of Object.entries({x1:x,y1:y,x2:centerPixel[0],y2:centerPixel[1]}))$('route').setAttribute(key,value);
    $('route').removeAttribute('hidden');
  } else {$('guess-score').textContent='Here is the calculated center. You can try a guess another time.';}
});
$('center-tool').addEventListener('toggle',()=>{if($('center-tool').open)selectingOrigin=true;if($('center-tool').open && guess && !position){$('route').removeAttribute('hidden');chooseOrigin(guess,'guess');}});
$('pick-origin').onclick=()=>{selectingOrigin=true;$('map-note').textContent='Tap the map to choose a starting point for the compass.';$('map').focus();$('map').scrollIntoView({block:'center',behavior:'auto'});};
$('try-again').onclick=()=>{
  $('clear').onclick();revealed=false;guess=null;selectingOrigin=false;
  $('center-answer').open=false;$('center-tool').open=false;
  $('center-marker').setAttribute('hidden','');$('center-key').hidden=true;$('try-again').hidden=true;$('map-result').hidden=true;
  $('guess-score').textContent='';$('pin-label').textContent='Your guess';
  $('guess-feedback').textContent='Pick a new spot, then reveal the answer again.';
  $('map-note').textContent='Tap where you think the center is. You can move your guess until you reveal the answer.';
  $('reset-map').onclick();$('map').focus();$('center-experience').scrollIntoView({block:'start',behavior:'auto'});
};
'''
# Script executes after the article DOM has loaded, and only mounts its own local UI.
mount="document.getElementById('center-experience').innerHTML="+json.dumps(map_section)+";\ndocument.getElementById('compass-panel').innerHTML="+json.dumps(controls)+";\n"
(R.parent/'images/center-game.js').write_text('(()=>{\n'+mount+script+extra+'\n})();\n',encoding='utf-8')
css=r'''
#center-experience,#center-tool{--paper:#f7f3e8;--ink:#213d32;--muted:#616a5e;--line:#d6d7c9;--rust:#a85632;--teal:#207675;color:var(--ink);font:17px/1.6 Arial,sans-serif}
#center-experience [hidden],#center-tool [hidden]{display:none!important}
#center-answer:not([open]) #compass-panel,#center-tool:not([open]) #compass-panel{display:none}
#center-experience button,#center-tool button{font:inherit;border:1px solid var(--ink);padding:10px 16px;min-height:46px;border-radius:5px;cursor:pointer;background:var(--paper);color:var(--ink)}
#center-experience button:hover,#center-tool button:hover{background:#e6ebdf}#center-tool button:disabled{opacity:.55;cursor:wait}#center-tool button.primary{background:var(--ink);color:var(--paper)}
#center-experience :focus-visible,#center-tool :focus-visible,#center-answer>summary:focus-visible{outline:3px solid #a85632;outline-offset:4px}
#center-experience .map-shell{position:relative;border:1px solid var(--line);background:#f0efe2;border-radius:8px;overflow:hidden}
#map{display:block;width:100%;aspect-ratio:1;cursor:crosshair;touch-action:manipulation}
#map text{font-family:Arial,sans-serif;paint-order:stroke;stroke:#f7f3e8;stroke-width:5;stroke-linejoin:round;fill:#213d32}
#center-experience .map-tools{display:flex;gap:8px;position:absolute;right:12px;top:12px}#center-experience .map-tools button{padding:4px 12px;font-size:20px;min-width:42px}
#center-experience .legend{display:flex;gap:20px;flex-wrap:wrap;font-size:14px;margin:8px 0}#center-experience .swatch{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:7px;background:var(--rust)}#center-experience .swatch.you{background:var(--teal)}
#center-experience .note,#center-tool .note{color:var(--muted);font-size:14px}#guess-feedback{font-weight:bold}#map-result{border-left:3px solid #207675;padding:10px 16px;font-weight:bold}
#center-answer{border-top:1px solid #d6d7c9;border-bottom:1px solid #d6d7c9;margin-top:28px;padding:0 0 16px}
#center-answer>summary{cursor:pointer;padding:20px 14px;font:bold 23px/1.35 Georgia,serif;background:#e6ebdf;color:#213d32;border-radius:5px}
#center-answer[open]>summary{margin-bottom:24px}#guess-score{font:bold 22px/1.45 Georgia,serif;padding:18px;background:#f1e7d8;border-radius:5px;margin-bottom:24px}
#center-tool{border:1px solid var(--line);border-radius:6px;padding:16px;margin:24px 0}#center-tool>summary{font:bold 20px/1.4 Georgia,serif;cursor:pointer}#compass-panel{padding-top:18px}
#center-tool .actions{display:flex;flex-wrap:wrap;gap:10px}#center-tool .result{border-top:1px solid var(--line);margin-top:20px;padding-top:20px}#center-tool .kicker{font-size:12px;font-weight:bold;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}#center-tool .distance{font:48px/1.1 Georgia,serif;margin:10px 0}#center-tool .direction{font-size:24px;margin:12px 0}
#center-tool .dial{width:170px;height:170px;border:1px solid var(--line);border-radius:50%;margin:20px auto;position:relative;background:#efeee1}#center-tool .north{position:absolute;top:7px;width:100%;text-align:center;font-weight:bold}#center-tool .arrow{position:absolute;inset:35px;transform-origin:center;transition:transform .15s linear}#center-tool .arrow svg{width:100%;height:100%}#center-tool .dial[data-inactive="true"] .arrow{visibility:hidden}#center-tool .dial[data-inactive="true"]:after{content:attr(data-message);position:absolute;top:72px;width:100%;text-align:center;font-size:14px;color:var(--muted)}
#center-tool details{border-top:1px solid var(--line);padding:16px 0;margin-top:15px}#center-tool details summary{cursor:pointer;font-weight:bold}#center-tool form{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:15px}#center-tool label{display:block;font-size:14px}#center-tool input{box-sizing:border-box;display:block;width:100%;font:inherit;padding:8px;border:1px solid #869582;border-radius:4px;background:#fffdf7;color:var(--ink)}#center-tool form button{grid-column:1/-1}#error{color:#88381f;font-size:15px}
@media(max-width:600px){#center-answer>summary{font-size:21px}#center-experience .map-tools{right:8px;top:8px}#center-experience .legend{gap:12px}#center-tool .distance{font-size:40px}#center-tool{padding:12px}}
@media(prefers-reduced-motion:reduce){#center-tool .arrow{transition:none}}
'''
(R.parent/'images/center-game.css').write_text(css,encoding='utf-8')
print('Built inline guessing game and compass assets')
