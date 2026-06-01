const sample = {
  address: "1301-03 SPRING ST",
  parcel: "002-22-090",
  lat: 43.07141351984553,
  lon: -76.15863026243572,
  headings: [298.83175629418724, 118.83175629418724]
};

const map = L.map("streetMap", { scrollWheelZoom: false }).setView([sample.lat, sample.lon], 17);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

const marker = L.circleMarker([sample.lat, sample.lon], {
  radius: 9,
  color: "#08111f",
  weight: 2,
  fillColor: "#f76900",
  fillOpacity: 0.95
}).addTo(map);
marker.bindPopup(`<div class="map-popup"><strong>${sample.address}</strong><span>${sample.parcel}</span><p>Street Quality sample</p><a href="#entries">View captures</a></div>`);

function endpoint(lat, lon, heading, meters) {
  const radians = heading * Math.PI / 180;
  const dLat = Math.cos(radians) * meters / 111320;
  const dLon = Math.sin(radians) * meters / (111320 * Math.cos(lat * Math.PI / 180));
  return [lat + dLat, lon + dLon];
}

sample.headings.forEach((heading) => {
  const end = endpoint(sample.lat, sample.lon, heading, 85);
  L.polyline([[sample.lat, sample.lon], end], {
    color: heading > 180 ? "#f76900" : "#28634a",
    weight: 5,
    opacity: 0.85
  }).addTo(map).bindTooltip(`${Math.round(heading)}° Street View heading`);
});