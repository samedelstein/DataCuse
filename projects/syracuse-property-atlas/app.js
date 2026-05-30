const mapEl = document.getElementById("atlasMap");
const searchInput = document.getElementById("parcelSearch");
const searchResults = document.getElementById("searchResults");
const publishedCount = document.getElementById("publishedCount");
const totalCount = document.getElementById("totalCount");
const statusFilterButtons = Array.from(document.querySelectorAll("[data-status-filter]"));
const layerFilterInputs = Array.from(document.querySelectorAll(".layer-filter input[type='checkbox']"));

const state = {
  map: null,
  layer: null,
  parcels: [],
  markers: new Map(),
  filter: "all",
  layers: new Set(),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function popupHtml(parcel) {
  const status = parcel.published ? "Published" : "Waiting in queue";
  const layers = Object.entries(parcel.layers || {})
    .filter(([, active]) => active)
    .map(([key]) => key.replace("_", " "))
    .join(", ");
  const link = parcel.published && parcel.url
    ? `<a href="${escapeHtml(parcel.url)}">Open property page</a>`
    : "<span>Not published yet</span>";
  return `
    <div class="map-popup">
      <strong>${escapeHtml(parcel.address)}</strong>
      <p>${escapeHtml(parcel.parcel_key || `Parcel ${parcel.id}`)}</p>
      <p>${status}</p>
      ${layers ? `<p>Layers: ${escapeHtml(layers)}</p>` : ""}
      ${link}
    </div>
  `;
}

function markerStyle(parcel) {
  return {
    radius: parcel.published ? 9 : 2.5,
    color: parcel.published ? "#08111f" : "#6f7b85",
    weight: parcel.published ? 3 : 0.5,
    fillColor: parcel.published ? "#f76900" : "#aeb8bf",
    fillOpacity: parcel.published ? 0.98 : 0.2,
    opacity: parcel.published ? 1 : 0.42,
  };
}

function shouldShow(parcel) {
  if (state.filter === "published") return parcel.published;
  if (state.filter === "queued") return !parcel.published;
  if (state.layers.size) {
    const parcelLayers = parcel.layers || {};
    for (const layer of state.layers) {
      if (!parcelLayers[layer]) return false;
    }
  }
  return true;
}

function focusParcel(parcel) {
  const marker = state.markers.get(parcel.id);
  if (!marker) return;
  state.map.setView([parcel.lat, parcel.lon], 18, { animate: true });
  marker.openPopup();
}

function renderSearch(query) {
  const normalized = query.trim().toUpperCase();
  if (!normalized) {
    const label = state.filter === "all" ? "all mapped parcels" : `${state.filter} parcels`;
    searchResults.innerHTML = `<p class="search-empty">Search ${label} by address or parcel ID.</p>`;
    return;
  }

  const matches = state.parcels
    .filter(shouldShow)
    .filter((parcel) => {
      const address = String(parcel.address || "").toUpperCase();
      const key = String(parcel.parcel_key || "").toUpperCase();
      return address.includes(normalized) || key.includes(normalized);
    })
    .slice(0, 40);

  if (!matches.length) {
    searchResults.innerHTML = '<p class="search-empty">No matching parcel found.</p>';
    return;
  }

  searchResults.innerHTML = matches.map((parcel) => `
    <button type="button" data-parcel-id="${parcel.id}">
      <span>${escapeHtml(parcel.address)}</span>
      <small>${escapeHtml(parcel.parcel_key || `Parcel ${parcel.id}`)} · ${parcel.published ? "Published" : "Queued"}</small>
    </button>
  `).join("");
}

function refreshMarkers() {
  if (!state.layer) return;
  state.layer.clearLayers();
  state.markers.clear();
  const bounds = [];

  state.parcels.filter(shouldShow).forEach((parcel) => {
    if (typeof parcel.lat !== "number" || typeof parcel.lon !== "number") return;
    const marker = L.circleMarker([parcel.lat, parcel.lon], markerStyle(parcel))
      .bindPopup(popupHtml(parcel));
    marker.addTo(state.layer);
    state.markers.set(parcel.id, marker);
    bounds.push([parcel.lat, parcel.lon]);
  });

  if (bounds.length) {
    state.map.fitBounds(bounds, { padding: [24, 24], maxZoom: state.filter === "all" ? 13 : 15 });
  }
}

function setStatusFilter(filter) {
  state.filter = filter;
  statusFilterButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.statusFilter === filter);
  });
  refreshMarkers();
  renderSearch(searchInput?.value || "");
}

function syncLayerFilter() {
  state.layers = new Set(layerFilterInputs.filter((input) => input.checked).map((input) => input.value));
  refreshMarkers();
  renderSearch(searchInput?.value || "");
}

async function initAtlas() {
  if (!mapEl || !window.L) return;

  const response = await fetch("data/progress.json");
  const progress = await response.json();
  state.parcels = progress.parcels || [];

  if (publishedCount) publishedCount.textContent = progress.published ?? 0;
  if (totalCount) totalCount.textContent = progress.total ?? state.parcels.length;

  state.map = L.map(mapEl, {
    preferCanvas: true,
    zoomControl: true,
    renderer: L.canvas({ padding: 0.5 }),
  }).setView([43.0481, -76.1474], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(state.map);

  state.layer = L.layerGroup().addTo(state.map);
  refreshMarkers();

  renderSearch("");
}

if (searchInput) {
  searchInput.addEventListener("input", (event) => {
    renderSearch(event.target.value);
  });
}

if (searchResults) {
  searchResults.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-parcel-id]");
    if (!button) return;
    const parcel = state.parcels.find((item) => item.id === Number(button.dataset.parcelId));
    if (parcel) focusParcel(parcel);
  });
}

statusFilterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setStatusFilter(button.dataset.statusFilter || "all");
  });
});

layerFilterInputs.forEach((input) => {
  input.addEventListener("change", syncLayerFilter);
});

initAtlas().catch((error) => {
  if (searchResults) {
    searchResults.innerHTML = `<p class="search-empty">Map data failed to load: ${escapeHtml(error.message)}</p>`;
  }
});
