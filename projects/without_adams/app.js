(() => {
  const data = window.ACCESS_LAB;
  const map = L.map('scenario-map', { zoomControl: true, scrollWheelZoom: false }).setView(data.center, 15);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
  const routeLayer = L.layerGroup().addTo(map);
  const destinationLayer = L.layerGroup().addTo(map);
  const tripLayer = L.layerGroup().addTo(map);
  const projectLayer = L.layerGroup().addTo(map);
  const aadtLayer = L.layerGroup().addTo(map);
  const fireLayer = L.layerGroup().addTo(map);
  const storyLayer = L.layerGroup().addTo(map);
  const mapState = document.getElementById('map-state');
  const mapKicker = document.getElementById('map-kicker');
  const mapDetail = document.getElementById('map-detail');
  let active = data.scenarios[0];

  const routeStyle = (kind) => kind === 'risk'
    ? { color: '#d9523c', weight: 7, opacity: .92, dashArray: '10 8' }
    : { color: '#0e7264', weight: 6, opacity: .9 };

  function drawMap() {
    routeLayer.clearLayers();
    destinationLayer.clearLayers();
    data.destinations.forEach((place) => {
      L.circleMarker(place.point, { radius: 8, color: '#13263d', weight: 2, fillColor: '#f7c948', fillOpacity: 1 })
        .bindTooltip(`<strong>${place.name}</strong><br>${place.type}`).addTo(destinationLayer);
    });
  }

  const storyCopy = {
    grid: { kicker: 'Step 1 · regional change', title: 'The Community Grid replaces the downtown I-81 viaduct with BL-81 on the Almond corridor.', detail: 'This is the future baseline. Before considering Adams, the map must show where the regional through-route and downtown access change.' },
    open: { kicker: 'Step 2 · access baseline', title: 'With Adams open, the medical district keeps a direct east–west public connection.', detail: 'The teal segment identifies the connection that lets city, hospital, transit, and emergency traffic retain another route through the district.' },
    closed: { kicker: 'Step 3 · decision point', title: 'Closing this block removes an east–west link at the center of the medical district.', detail: 'The red segment is the specific proposal: East Adams between Elizabeth Blackwell and Irving. The question is whether alternate routes can reliably absorb the trips it carries.' }
  };

  function setMapStory(story) {
    const content = storyCopy[story];
    storyLayer.clearLayers();
    mapKicker.textContent = content.kicker;
    mapState.textContent = content.title;
    mapDetail.textContent = content.detail;
    document.querySelectorAll('[data-map-story]').forEach((button) => button.setAttribute('aria-selected', String(button.dataset.mapStory === story)));
    if (story === 'open' || story === 'closed') {
      const color = story === 'open' ? '#0e7264' : '#c23f2b';
      const label = story === 'open' ? 'East Adams: public connection retained' : 'Proposed Adams closure';
      L.polyline(data.closure.points, { color, weight: 14, opacity: .96, dashArray: story === 'closed' ? '12 8' : null }).bindTooltip(label, { permanent: true, direction: 'top', className: 'decision-label' }).addTo(storyLayer);
      const endpoints = [
        { point: data.closure.points[0], name: 'Elizabeth Blackwell Street' },
        { point: data.closure.points.at(-1), name: 'Irving Avenue' }
      ];
      endpoints.forEach((endpoint) => L.circleMarker(endpoint.point, { radius: 7, color: '#13263d', weight: 2, fillColor: '#f7c948', fillOpacity: 1 })
        .bindTooltip(endpoint.name, { permanent: true, direction: 'bottom', className: 'endpoint-label' }).addTo(storyLayer));
      const bounds = L.latLngBounds(data.closure.points);
      map.fitBounds(bounds.pad(.7), { padding: [48, 48], maxZoom: 17 });
    } else if (projectLayer.getLayers().length) {
      map.fitBounds(L.featureGroup(projectLayer.getLayers()).getBounds(), { padding: [38, 38] });
    }
  }

  function renderControls() {
    const holder = document.getElementById('scenario-controls');
    holder.innerHTML = data.scenarios.map((scenario) => `<button class="scenario-button ${scenario.id === active.id ? 'is-active' : ''}" type="button" role="radio" aria-checked="${scenario.id === active.id}" data-scenario="${scenario.id}"><span>${scenario.tag}</span>${scenario.label}</button>`).join('');
    holder.querySelectorAll('button').forEach((button) => button.addEventListener('click', () => {
      active = data.scenarios.find((scenario) => scenario.id === button.dataset.scenario);
      render();
    }));
  }

  function renderBrief() {
    document.getElementById('scenario-summary').textContent = active.summary;
    document.getElementById('brief-title').textContent = active.label;
    document.getElementById('brief-description').textContent = active.description;
    document.getElementById('operational-focus').innerHTML = active.focus.map((item) => `<li>${item}</li>`).join('');
    document.getElementById('decision-tests').innerHTML = active.tests.map((item, index) => `<div class="test"><b>${String(index + 1).padStart(2, '0')}</b><span>${item}</span></div>`).join('');
  }

  function renderStatic() {
    document.getElementById('recommendations-grid').innerHTML = data.recommendations.map((item) => `<article><span>${item.number}</span><h3>${item.title}</h3><p>${item.text}</p></article>`).join('');
    document.getElementById('source-table').innerHTML = data.sources.map((source) => `<tr><td><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.name}</a></td><td>${source.use}</td><td>${source.status}</td></tr>`).join('');
  }

  function render() { renderControls(); drawMap(); renderBrief(); }
  const status = document.getElementById('route-status');
  const results = document.getElementById('route-results');
  const directions = document.getElementById('directions');
  const miles = (meters) => (meters / 1609.344).toFixed(1);
  const minutes = (seconds) => Math.max(1, Math.round(seconds / 60));

  async function geocode(query) {
    const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&viewbox=-76.23,43.13,-76.02,42.96&bounded=1&q=${encodeURIComponent(query)}`;
    const response = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('Location search is unavailable.');
    const places = await response.json();
    if (!places.length) throw new Error(`No Syracuse-area match found for “${query}”. Try a street address, landmark, or neighborhood.`);
    return { lon: Number(places[0].lon), lat: Number(places[0].lat), label: places[0].display_name };
  }

  async function getRoute(points) {
    const coordinates = points.map((point) => `${point.lon},${point.lat}`).join(';');
    const providers = ['https://router.project-osrm.org', 'https://routing.openstreetmap.de/routed-car'];
    for (const provider of providers) {
      try {
        const response = await fetch(`${provider}/route/v1/driving/${coordinates}?overview=full&geometries=geojson&steps=true`);
        if (!response.ok) continue;
        const body = await response.json();
        if (body.routes?.length) return body.routes[0];
      } catch (_) {
        // Try the next public routing provider.
      }
    }
    throw new Error('The live routing service is unavailable. Please try again shortly.');
  }

  function routeCoordinates(route) {
    return route.points ? route.points.map((point) => [point.lat, point.lon]) : route.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
  }

  function aadtStyle(value) {
    if (value > 75000) return { color: '#6d287d', weight: 5, opacity: .85 };
    if (value > 25000) return { color: '#c77700', weight: 4, opacity: .85 };
    if (value > 10000) return { color: '#bb9c00', weight: 3, opacity: .85 };
    if (value > 4000) return { color: '#398b52', weight: 2.5, opacity: .8 };
    return { color: '#6eb34b', weight: 2, opacity: .75 };
  }

  async function loadAadt() {
    const params = new URLSearchParams({ f: 'geojson', where: '1=1', outFields: '*', geometry: '-76.17,43.025,-76.10,43.075', geometryType: 'esriGeometryEnvelope', inSR: '4326', spatialRel: 'esriSpatialRelIntersects', outSR: '4326', returnGeometry: 'true' });
    const response = await fetch(`${data.aadtService}?${params}`);
    if (!response.ok) throw new Error('NYSDOT AADT layer is unavailable.');
    const geojson = await response.json();
    L.geoJSON(geojson, { style: (feature) => aadtStyle(Number(feature.properties.AADT)), onEachFeature: (feature, layer) => {
      const value = Number(feature.properties.AADT).toLocaleString();
      const year = feature.properties.Year || feature.properties.YEAR || feature.properties.AADT_YEAR || 'reported by source';
      layer.bindPopup(`<strong>${feature.properties.RoadwayName || feature.properties.ROADWAYNAME || 'NYSDOT roadway'}</strong><br>AADT: ${value}<br>Year: ${year}`);
    }}).addTo(aadtLayer);
  }

  async function loadHistoricFire() {
    const params = new URLSearchParams({ f: 'geojson', where: '1=1', outFields: 'alarmdate,incidenttype,station,compositeaddress', geometry: '-76.17,43.025,-76.10,43.075', geometryType: 'esriGeometryEnvelope', inSR: '4326', spatialRel: 'esriSpatialRelIntersects', outSR: '4326', returnGeometry: 'true', resultRecordCount: '2000', orderByFields: 'alarmdate DESC' });
    const response = await fetch(`${data.fireIncidentsService}?${params}`);
    if (!response.ok) throw new Error('Historic Fire Incidents layer is unavailable.');
    const geojson = await response.json();
    L.geoJSON(geojson, { pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 4, color: '#7c1d1d', weight: 1, fillColor: '#ef4444', fillOpacity: .55 }), onEachFeature: (feature, layer) => {
      const date = feature.properties.alarmdate ? new Date(feature.properties.alarmdate).toLocaleDateString() : 'Date unavailable';
      layer.bindPopup(`<strong>Historic fire incident</strong><br>${date}<br>${feature.properties.incidenttype || 'Type unavailable'}<br>Station: ${feature.properties.station || 'Unavailable'}`);
    }}).addTo(fireLayer);
  }

  function loadProjectCorridors() {
    if (projectLayer.getLayers().length) return;
    // Packaged coordinates ensure the core I-81 / BL-81 map is visible even
    // while a third-party routing endpoint is unavailable.
    const corridorPoints = (points) => points.map(({ lat, lon }) => [lat, lon]);
    L.polyline(corridorPoints(data.projectCorridors.formerI81), { color: '#303944', weight: 11, opacity: .88, dashArray: '12 9' }).bindTooltip('Former I-81 viaduct alignment', { permanent: true, direction: 'top', className: 'project-label' }).addTo(projectLayer);
    L.polyline(corridorPoints(data.projectCorridors.futureBL81), { color: '#d95f02', weight: 6, opacity: .98 }).bindTooltip('City Community Grid: Almond / future BL-81 alignment', { permanent: true, direction: 'top', className: 'project-label' }).addTo(projectLayer);
    L.marker([43.048, -76.1436], { interactive: false, icon: L.divIcon({ className: 'corridor-label former-label', html: 'FORMER I-81' }) }).addTo(projectLayer);
    L.marker([43.0405, -76.1407], { interactive: false, icon: L.divIcon({ className: 'corridor-label future-label', html: 'ALMOND / BL-81' }) }).addTo(projectLayer);
    map.fitBounds(L.featureGroup(projectLayer.getLayers()).getBounds(), { padding: [38, 38] });
  }

  function stepText(step) {
    const road = step.name || 'the next road';
    const modifier = step.maneuver?.modifier ? `${step.maneuver.modifier} ` : '';
    const type = step.maneuver?.type || 'continue';
    if (type === 'depart') return `Start on ${road}`;
    if (type === 'arrive') return 'Arrive at destination';
    if (type === 'roundabout') return `Use the roundabout toward ${road}`;
    return `${type === 'turn' ? 'Turn' : 'Continue'} ${modifier}onto ${road}`;
  }

  function renderTrip(openRoute, detourRoute, origin, destination) {
    tripLayer.clearLayers();
    const openCoords = routeCoordinates(openRoute);
    const detourCoords = detourRoute ? routeCoordinates(detourRoute) : [];
    L.polyline(openCoords, { color: '#2458a6', weight: 6, opacity: .9 }).bindTooltip('Open-network route').addTo(tripLayer);
    if (detourRoute) L.polyline(detourCoords, { color: '#d9523c', weight: 6, opacity: .9, dashArray: '9 8' }).bindTooltip('Closure-detour route').addTo(tripLayer);
    L.circleMarker([origin.lat, origin.lon], { radius: 7, color: '#13263d', fillColor: '#fff', fillOpacity: 1, weight: 3 }).bindTooltip('Start').addTo(tripLayer);
    L.circleMarker([destination.lat, destination.lon], { radius: 7, color: '#13263d', fillColor: '#f7c948', fillOpacity: 1, weight: 3 }).bindTooltip('Destination').addTo(tripLayer);
    map.fitBounds(L.latLngBounds(openCoords.concat(detourCoords)), { padding: [36, 36] });
    const changed = detourRoute && (Math.abs(detourRoute.seconds - openRoute.seconds) > 15 || Math.abs(detourRoute.distance - openRoute.distance) > 35);
    if (!changed) {
      results.innerHTML = `<article class="route-result open-result"><p>Adams open</p><strong>${minutes(openRoute.seconds)} min</strong><span>${miles(openRoute.distance)} mi · local-network free-flow estimate</span></article><article class="route-result no-change-result"><p>Adams closed</p><strong>No change</strong><span>Removing the closure edges does not change the shortest permitted path.</span></article>`;
      directions.innerHTML = `<h3>Your route is not affected by this closure.</h3><p>Removing the proposed Adams block does not change the shortest permitted path in the local street graph. A defensible comparison does not invent a diversion for it.</p>`;
      mapKicker.textContent = 'Personal trip check';
      mapState.textContent = 'Blue line: Adams-open route. The closure model found the same shortest path after the Adams block was removed.';
      mapDetail.textContent = 'This individual trip does not depend on the closure block; that does not answer whether the medical district as a whole has sufficient redundancy.';
      return;
    }
    const addedMinutes = minutes(detourRoute.seconds) - minutes(openRoute.seconds);
    const addedDistance = Number(miles(detourRoute.distance)) - Number(miles(openRoute.distance));
    results.innerHTML = `<article class="route-result open-result"><p>Adams open</p><strong>${minutes(openRoute.seconds)} min</strong><span>${miles(openRoute.distance)} mi · local-network free-flow estimate</span></article><article class="route-result detour-result"><p>Adams closed</p><strong>${minutes(detourRoute.seconds)} min</strong><span>${miles(detourRoute.distance)} mi · Adams closure edges removed</span></article><article class="route-result delta-result"><p>Screening difference</p><strong>${addedMinutes > 0 ? '+' : ''}${addedMinutes} min</strong><span>${addedDistance > 0 ? '+' : ''}${addedDistance.toFixed(1)} mi before traffic effects</span></article>`;
    const grouped = detourRoute.segments.reduce((groups, segment) => { const last = groups.at(-1); if (last && last.name === segment.name) { last.meters += segment.meters; } else groups.push({ name: segment.name, meters: segment.meters }); return groups; }, []);
    directions.innerHTML = `<h3>Adams-closed path</h3><ol>${grouped.filter((segment) => segment.meters > 35).map((segment) => `<li>Continue on ${segment.name} <span>${miles(segment.meters)} mi</span></li>`).join('')}</ol><p>This is a shortest-path screen using the local OSM street graph with the Adams closure edges removed. It is not live navigation, an emergency route, or an intersection-operations model.</p>`;
    mapKicker.textContent = 'Personal trip check';
    mapState.textContent = 'Blue line: Adams-open route. Red dashed line: Adams-closed route with the closure edges removed.';
    mapDetail.textContent = 'This is a free-flow screening comparison. It does not substitute for peak-period traffic operations or emergency-response validation.';
  }

  function renderOpenTrip(route, origin, destination) {
    tripLayer.clearLayers();
    const coords = routeCoordinates(route);
    L.polyline(coords, { color: '#2458a6', weight: 6, opacity: .9 }).bindTooltip('Open-network route').addTo(tripLayer);
    L.circleMarker([origin.lat, origin.lon], { radius: 7, color: '#13263d', fillColor: '#fff', fillOpacity: 1, weight: 3 }).bindTooltip('Start').addTo(tripLayer);
    L.circleMarker([destination.lat, destination.lon], { radius: 7, color: '#13263d', fillColor: '#f7c948', fillOpacity: 1, weight: 3 }).bindTooltip('Destination').addTo(tripLayer);
    map.fitBounds(L.latLngBounds(coords), { padding: [36, 36] });
    const steps = route.legs.flatMap((leg) => leg.steps || []).filter((step) => step.distance > 35);
    results.innerHTML = `<article class="route-result open-result"><p>Adams open</p><strong>${minutes(route.duration)} min</strong><span>${miles(route.distance)} mi · routing-engine free-flow estimate</span></article><article class="route-result no-change-result"><p>Adams closed</p><strong>Pending</strong><span>The closure screen needs its local street graph.</span></article>`;
    directions.innerHTML = `<h3>Adams-open directions</h3><ol>${steps.map((step) => `<li>${stepText(step)} <span>${miles(step.distance)} mi</span></li>`).join('')}</ol><p>The blue line is an available routing-engine result. The red closure-detour line is withheld until the local street graph can remove the actual East Adams block; this avoids presenting an invented detour as an answer.</p>`;
    mapKicker.textContent = 'Personal trip check';
    mapState.textContent = 'Blue line: Adams-open route. Closure comparison temporarily unavailable.';
    mapDetail.textContent = 'The route provider is responding, but the independent street-graph service needed to remove East Adams is not.';
  }

  document.getElementById('route-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const originText = document.getElementById('origin').value.trim();
    const destinationText = document.getElementById('destination').value.trim();
    status.textContent = 'Finding locations and rebuilding the local network with Adams open and closed…'; results.innerHTML = ''; directions.innerHTML = ''; tripLayer.clearLayers();
    let origin;
    let destination;
    try {
      [origin, destination] = await Promise.all([geocode(originText), geocode(destinationText)]);
      const comparison = await window.ACCESS_NETWORK.compare(origin, destination, data.closureMidpoint);
      if (!comparison.open || !comparison.closed) throw new Error('No permitted local-street route was found for one of the scenarios.');
      renderTrip(comparison.open, comparison.closed, origin, destination);
      status.textContent = `Compared Adams-open and Adams-closed networks from ${origin.label} to ${destination.label}.`;
    } catch (error) {
      if (origin && destination) {
        try {
          const openRoute = await getRoute([origin, destination]);
          renderOpenTrip(openRoute, origin, destination);
          status.textContent = 'The local closure-model source is unavailable. Showing the mapped Adams-open route only; no closure detour has been fabricated.';
          return;
        } catch (_) { /* show the original, useful error below */ }
      }
      status.textContent = error.message === 'Failed to fetch'
        ? 'A live map service did not respond. The address or street-network provider may be temporarily unavailable; please try again in a moment.'
        : error.message;
    }
  });
  document.querySelectorAll('[data-destination]').forEach((button) => button.addEventListener('click', () => { document.getElementById('destination').value = button.dataset.destination; document.getElementById('origin').focus(); }));
  const layerStatus = document.getElementById('layer-status');
  document.getElementById('zoom-adams').addEventListener('click', () => setMapStory('closed'));
  document.getElementById('project-corridor-toggle').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const visible = map.hasLayer(projectLayer) && projectLayer.getLayers().length;
    if (visible) { projectLayer.clearLayers(); button.setAttribute('aria-pressed', 'false'); layerStatus.textContent = ''; mapDetail.textContent = 'The regional project layer is hidden. Use the control above to restore it.'; return; }
    layerStatus.textContent = 'Loading road-snapped project corridors…';
    loadProjectCorridors(); button.setAttribute('aria-pressed', 'true'); layerStatus.textContent = 'Dashed gray: former I-81. Orange: future BL-81 / Almond corridor.'; setMapStory('grid');
  });
  document.getElementById('aadt-toggle').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const visible = map.hasLayer(aadtLayer) && aadtLayer.getLayers().length;
    if (visible) { aadtLayer.clearLayers(); button.setAttribute('aria-pressed', 'false'); layerStatus.textContent = ''; return; }
    layerStatus.textContent = 'Loading NYSDOT annual-average traffic counts…';
    try { await loadAadt(); button.setAttribute('aria-pressed', 'true'); layerStatus.textContent = 'AADT layer loaded. Click a segment for its reported count and year.'; }
    catch (error) { layerStatus.textContent = error.message; }
  });
  document.getElementById('fire-toggle').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    if (fireLayer.getLayers().length) { fireLayer.clearLayers(); button.setAttribute('aria-pressed', 'false'); layerStatus.textContent = ''; return; }
    layerStatus.textContent = 'Loading historic Fire Incidents points…';
    try { await loadHistoricFire(); button.setAttribute('aria-pressed', 'true'); layerStatus.textContent = 'Historic Fire Incidents loaded. Source last updated November 2022—do not interpret as current 911 demand.'; }
    catch (error) { layerStatus.textContent = error.message; }
  });
  renderStatic();
  render();
  document.querySelectorAll('[data-map-story]').forEach((button) => button.addEventListener('click', () => setMapStory(button.dataset.mapStory)));
  loadProjectCorridors();
  document.getElementById('project-corridor-toggle').setAttribute('aria-pressed', 'true');
  layerStatus.textContent = 'Dashed gray: former I-81. Orange: future BL-81 / Almond corridor.';
  setMapStory('grid');
  document.getElementById('print-brief').addEventListener('click', () => window.print());
})();
