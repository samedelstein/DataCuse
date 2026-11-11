import { searchAddresses, lookupPoint, calendar, localDay } from './lib.mjs';

const $ = id => document.getElementById(id);
const storageKey = 'datacuse-pickup-address';
let currentZone, typedAddress = '', savedAddress = '', busy = false;
const dateFormat = new Intl.DateTimeFormat('en-US', {weekday:'short', month:'short', day:'numeric', timeZone:'UTC'});
const formatDate = date => dateFormat.format(new Date(`${date}T12:00:00Z`));
const setStatus = (message = '', error = false) => { $('status').textContent = message; $('status').classList.toggle('error',error); };
function setBusy(value) {
  busy = value;
  for (const id of ['search-button','locate','use-saved','address']) $(id).disabled = value;
  document.querySelectorAll('.candidate').forEach(button => { button.disabled = value; });
  $('search-form').setAttribute('aria-busy',String(value));
}
function resetResult() { $('result').hidden = true; currentZone = null; }
function showSaved() {
  $('saved-address').hidden = !savedAddress;
  $('use-saved').textContent = savedAddress ? `Look up saved address: ${savedAddress}` : '';
}
try { savedAddress = localStorage.getItem(storageKey) || ''; } catch { /* Storage is optional. */ }
showSaved();

async function search() {
  if (busy) return;
  typedAddress = $('address').value.trim();
  resetResult(); $('matches').hidden = true; setBusy(true); setStatus('Finding matching Syracuse addresses…');
  try {
    const candidates = await searchAddresses(typedAddress);
    $('candidate-list').replaceChildren();
    if (!candidates.length) {
      setStatus('No matching Syracuse street address found. Check the street number and spelling, or use your location. You can also open the city map below.',true);
      return;
    }
    for (const candidate of candidates) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'candidate'; button.textContent = candidate.address;
      const note = document.createElement('small'); note.textContent = candidate.score < 100 ? 'Approximate address match — confirm before continuing →' : 'Use this address →';
      button.append(note); button.addEventListener('click',() => find(candidate.lat,candidate.lon,candidate.address));
      $('candidate-list').append(button);
    }
    $('matches').hidden = false;
    setStatus('Choose the matching address to see its collection schedule.');
  } catch (error) { setStatus(error.message,true); }
  finally { setBusy(false); }
}

async function find(lat,lon,label) {
  if (busy) return;
  resetResult(); setBusy(true); setStatus('Checking the city’s collection zones and published dates…');
  try {
    const result = await lookupPoint(lat,lon);
    if (result.status === 'outside-coverage') {
      setStatus('This point is outside the city’s mapped collection zones. Check the address or contact Cityline at 315-448-2489.',true); return;
    }
    if (result.status === 'ambiguous') {
      setStatus('This point touches more than one collection zone. Please confirm your schedule in the city map or call Cityline at 315-448-2489.',true); return;
    }
    render(result,label); $('matches').hidden = true; setStatus(); $('result').focus();
  } catch (error) { setStatus(error.message,true); }
  finally { setBusy(false); }
}

function render(result,label) {
  const zone = result.zones[0]; currentZone = zone;
  $('result-heading').textContent = label;
  $('week-badge').textContent = `Recycling week ${zone.week}`;
  $('zone-note').textContent = `Regular collection day: ${zone.day}. Published dates below include any shifts recorded in the city’s schedule.`;
  let partial = false;
  for (const kind of ['trash','recycling']) {
    const schedule = zone[kind];
    $(kind + '-date').textContent = schedule.next ? `${schedule.next === result.asOf ? 'Today · ' : ''}${formatDate(schedule.next)}` : 'No future date published';
    if (schedule.next) {
      const prior = new Date(`${schedule.next}T12:00:00Z`); prior.setUTCDate(prior.getUTCDate() - 1);
      $(kind + '-setout').textContent = `Set out after 6 p.m. ${formatDate(prior.toISOString().slice(0,10))}.`;
    } else $(kind + '-setout').textContent = 'Check the official schedule or contact Cityline.';
    $(kind + '-coverage').textContent = schedule.publishedThrough ? `City dates published through ${formatDate(schedule.publishedThrough)}, ${schedule.publishedThrough.slice(0,4)}.` : 'The city has not supplied dates for this zone.';
    partial ||= schedule.status !== 'available';
  }
  $('schedule-note').textContent = partial ? 'Some dates are missing, expired, or unreadable in the city source. Only valid published dates are shown. Check the official map before relying on an incomplete schedule.' : 'These are scheduled dates, not a live truck tracker. Check city notices for last-minute changes. Bring carts back by 7 p.m. on collection day.';
  const days = [...new Set([...zone.trash.upcoming,...zone.recycling.upcoming])].sort();
  $('upcoming-rows').replaceChildren();
  for (const day of days) {
    const row = document.createElement('tr'), date = document.createElement('td'), bins = document.createElement('td');
    date.textContent = `${formatDate(day)}, ${day.slice(0,4)}`;
    bins.textContent = [zone.trash.upcoming.includes(day) ? 'Trash' : '',zone.recycling.upcoming.includes(day) ? 'Recycling' : ''].filter(Boolean).join(' + ');
    row.append(date,bins); $('upcoming-rows').append(row);
  }
  $('download').disabled = !days.length;
  $('remember').hidden = !typedAddress;
  $('remember').textContent = 'Remember my address';
  $('retrieved').textContent = `Read from the city’s live map data ${new Date(result.fetchedAt).toLocaleString('en-US',{timeZone:'America/New_York'})} Eastern. Zone ${zone.id}.`;
  $('result').hidden = false;
}

$('search-form').addEventListener('submit',event => { event.preventDefault(); search(); });
$('use-saved').addEventListener('click',() => { $('address').value = savedAddress; search(); });
$('forget').addEventListener('click',() => {
  try { localStorage.removeItem(storageKey); savedAddress = ''; showSaved(); setStatus('Saved address removed from this browser.'); }
  catch { setStatus('Browser storage is unavailable.',true); }
});
$('remember').addEventListener('click',() => {
  try { localStorage.setItem(storageKey,typedAddress); savedAddress = typedAddress; showSaved(); $('remember').textContent = 'Address saved on this device ✓'; }
  catch { setStatus('This browser does not allow local storage. You can still bookmark this page.',true); }
});
$('download').addEventListener('click',() => {
  if (!currentZone) return;
  // Re-filter if this tab has been left open across midnight.
  const zone = structuredClone(currentZone);
  for (const kind of ['trash','recycling']) zone[kind].upcoming = zone[kind].upcoming.filter(date => date >= localDay());
  const url = URL.createObjectURL(new Blob([calendar(zone)],{type:'text/calendar;charset=utf-8'}));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'syracuse-pickup.ics'; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
});
$('locate').addEventListener('click',() => {
  if (busy) return;
  if (!navigator.geolocation) { setStatus('Location is unavailable in this browser. Enter your address instead.',true); return; }
  resetResult(); $('matches').hidden = true; setBusy(true); setStatus('Waiting for your browser’s location permission…');
  navigator.geolocation.getCurrentPosition(position => {
    setBusy(false);
    if (position.coords.accuracy > 100) { setStatus('Your location is too approximate to choose a collection zone reliably. Enter your street address instead.',true); return; }
    typedAddress = ''; find(position.coords.latitude,position.coords.longitude,'Your current location');
  },() => { setBusy(false); setStatus('Location could not be read. Enter your street address instead.',true); },{enableHighAccuracy:true,timeout:15000,maximumAge:0});
});
