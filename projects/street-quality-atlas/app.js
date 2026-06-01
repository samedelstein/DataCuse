const state = {
  data: null,
  map: null,
  markers: [],
  selectedLotId: null
};

const els = {
  stats: document.querySelector("#streetStats"),
  latest: document.querySelector("#latestStreetCard"),
  featureSummary: document.querySelector("#featureSummary"),
  progressFill: document.querySelector("#progressFill"),
  progressText: document.querySelector("#progressText"),
  search: document.querySelector("#streetSearch"),
  searchResults: document.querySelector("#streetSearchResults"),
  entries: document.querySelector("#streetEntries")
};

fetch("results/street_quality.json")
  .then((response) => response.json())
  .then((data) => {
    state.data = data;
    state.selectedLotId = data.parcels[0]?.lot_id || null;
    render(data);
  })
  .catch((error) => {
    els.entries.innerHTML = `<article class="entry-card loading-card">Street Quality data could not be loaded: ${escapeHtml(error.message)}</article>`;
  });

function render(data) {
  renderStats(data);
  renderLatest(data.parcels[0]);
  renderFeatureSummary(data);
  renderSearchResults(data.parcels);
  renderEntries(data.parcels);
  renderMap(data.parcels);
  els.search.addEventListener("input", () => {
    const query = els.search.value.trim().toLowerCase();
    const filtered = data.parcels.filter((parcel) => {
      return `${parcel.address || ""} ${parcel.lot_id || ""}`.toLowerCase().includes(query);
    });
    renderSearchResults(filtered);
    renderEntries(filtered.length ? filtered : data.parcels);
  });
}

function renderStats(data) {
  const findings = data.totals.objects + data.totals.issues;
  els.stats.innerHTML = `
    <div><strong>${data.totals.images}</strong><span>street-facing views</span></div>
    <div><strong>${findings}</strong><span>cataloged findings</span></div>
    <div><strong>${data.totals.issues}</strong><span>issue boxes</span></div>
  `;
  const analyzed = data.images.filter((image) => image.summary).length;
  const pct = data.totals.images ? Math.round((analyzed / data.totals.images) * 100) : 0;
  els.progressFill.style.width = `${pct}%`;
  els.progressText.innerHTML = `<strong>${analyzed}</strong> of <strong>${data.totals.images}</strong> captured street-facing images analyzed.`;
}

function renderLatest(parcel) {
  if (!parcel) return;
  els.latest.innerHTML = `
    <span>Latest street edge</span>
    <h2>${escapeHtml(titleCase(parcel.address || parcel.lot_id))}</h2>
    <p>${escapeHtml(parcel.summary || "Street-facing captures are ready for review.")}</p>
    <div class="mini-meta">
      <div><strong>${parcel.image_count}</strong><small>views</small></div>
      <div><strong>${parcel.issue_count}</strong><small>issues</small></div>
    </div>
    <p class="sample-note">Generated from the Property Atlas SQLite database and OpenStreetMap-derived street headings.</p>
    <a href="#entries">Review street views</a>
  `;
}

function renderFeatureSummary(data) {
  const counts = new Map();
  data.images.forEach((image) => {
    [...image.objects, ...image.issues].forEach((item) => {
      const label = item.label || item.category;
      if (label) counts.set(label, (counts.get(label) || 0) + 1);
    });
  });
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6);
  els.featureSummary.innerHTML = top.length
    ? top.map(([label, count]) => `<label><input type="checkbox" checked disabled> ${humanLabel(label)} (${count})</label>`).join("")
    : `<label><input type="checkbox" checked disabled> No analyzed features yet</label>`;
}

function renderSearchResults(parcels) {
  els.searchResults.innerHTML = parcels.map((parcel) => `
    <button type="button" class="street-list-button ${parcel.lot_id === state.selectedLotId ? "is-active" : ""}" data-lot-id="${escapeAttr(parcel.lot_id)}">
      <span>${escapeHtml(parcel.address || parcel.lot_id)}</span>
      <small>${escapeHtml(parcel.lot_id)} · ${parcel.image_count} views · ${parcel.issue_count} issues</small>
    </button>
  `).join("") || `<p class="search-empty">No matching captured streets.</p>`;
  els.searchResults.querySelectorAll("button[data-lot-id]").forEach((button) => {
    button.addEventListener("click", () => selectParcel(button.dataset.lotId));
  });
}

function renderEntries(parcels) {
  const images = parcels.flatMap((parcel) => parcel.images.map((image) => ({ ...image, parcel })));
  els.entries.innerHTML = images.map(renderImageCard).join("") || `<article class="entry-card loading-card">No street-facing captures found yet.</article>`;
}

function renderImageCard(image) {
  const issueBoxes = image.issues.slice(0, 4).map((item) => renderBox(item, "issue")).join("");
  const objectBoxes = image.objects.slice(0, 3).map((item) => renderBox(item, "object")).join("");
  const heading = Math.round(Number(image.heading || 0));
  return `
    <article class="entry-card">
      <div class="street-image-wrap">
        <img src="${escapeAttr(image.image_path)}" alt="Street-facing view for ${escapeAttr(image.address || image.lot_id)}">
        ${issueBoxes}${objectBoxes}
      </div>
      <div class="entry-body">
        <span class="direction-pill">Heading ${heading}&deg;</span>
        <h3>${escapeHtml(titleCase(image.address || image.lot_id))}</h3>
        <p>${escapeHtml(image.summary || "Analysis pending for this street-facing capture.")}</p>
        <div class="flag-row">
          <span>Street quality: ${score(image.street_quality)}</span>
          <span>Sidewalk quality: ${score(image.sidewalk_quality)}</span>
          <span>${image.issues.length} issue boxes</span>
          <span>${image.objects.length} objects</span>
        </div>
        <a href="results/">Open exported records</a>
      </div>
    </article>
  `;
}

function renderBox(item, kind) {
  const xmin = item.bbox_xmin;
  const ymin = item.bbox_ymin;
  const xmax = item.bbox_xmax;
  const ymax = item.bbox_ymax;
  if ([xmin, ymin, xmax, ymax].some((value) => value === null || value === undefined || Number.isNaN(Number(value)))) return "";
  const label = item.label || item.category || kind;
  return `<span class="annotation-box ${kind}" style="left:${xmin * 100}%;top:${ymin * 100}%;width:${(xmax - xmin) * 100}%;height:${(ymax - ymin) * 100}%;"><span>${escapeHtml(humanLabel(label))}</span></span>`;
}

function renderMap(parcels) {
  const first = parcels.find((parcel) => parcel.lat && parcel.lon);
  state.map = L.map("streetMap", { scrollWheelZoom: false }).setView(first ? [first.lat, first.lon] : [43.0481, -76.1474], first ? 16 : 12);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(state.map);
  parcels.forEach(addParcelToMap);
  const bounds = state.markers.map((marker) => marker.getLatLng());
  if (bounds.length > 1) state.map.fitBounds(bounds, { padding: [40, 40] });
}

function addParcelToMap(parcel) {
  if (!parcel.lat || !parcel.lon) return;
  const marker = L.circleMarker([parcel.lat, parcel.lon], {
    radius: 9,
    color: "#08111f",
    weight: 2,
    fillColor: "#f76900",
    fillOpacity: 0.95
  }).addTo(state.map);
  marker.bindPopup(`<div class="map-popup"><strong>${escapeHtml(parcel.address || parcel.lot_id)}</strong><span>${escapeHtml(parcel.lot_id)}</span><p>${parcel.image_count} street views · ${parcel.issue_count} issues</p><a href="#entries">View captures</a></div>`);
  marker.on("click", () => selectParcel(parcel.lot_id));
  state.markers.push(marker);
  parcel.images.forEach((image) => addHeadingRay(parcel, image.heading));
}

function addHeadingRay(parcel, heading) {
  const end = endpoint(parcel.lat, parcel.lon, Number(heading || 0), 85);
  L.polyline([[parcel.lat, parcel.lon], end], {
    color: heading > 180 ? "#f76900" : "#28634a",
    weight: 5,
    opacity: 0.75
  }).addTo(state.map).bindTooltip(`${Math.round(heading)}&deg; Street View heading`);
}

function selectParcel(lotId) {
  state.selectedLotId = lotId;
  const parcel = state.data.parcels.find((item) => item.lot_id === lotId);
  if (!parcel) return;
  renderLatest(parcel);
  renderSearchResults(state.data.parcels);
  renderEntries([parcel]);
  if (parcel.lat && parcel.lon) state.map.setView([parcel.lat, parcel.lon], 17);
  document.querySelector("#entries").scrollIntoView({ behavior: "smooth", block: "start" });
}

function endpoint(lat, lon, heading, meters) {
  const radians = heading * Math.PI / 180;
  const dLat = Math.cos(radians) * meters / 111320;
  const dLon = Math.sin(radians) * meters / (111320 * Math.cos(lat * Math.PI / 180));
  return [lat + dLat, lon + dLon];
}

function score(value) {
  return value ? `${value}/5` : "pending";
}

function humanLabel(value) {
  return String(value || "").replace(/_/g, " ");
}

function titleCase(value) {
  return String(value || "").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value);
}