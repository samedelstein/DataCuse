/* On-demand local street graph for closure-screening routes. */
window.ACCESS_NETWORK = (() => {
  const roadTypes = new Set(['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'service', 'living_street']);
  const speeds = { motorway: 55, trunk: 45, primary: 35, secondary: 30, tertiary: 27, residential: 22, unclassified: 22, service: 12, living_street: 10 };
  const distance = (a, b) => {
    const y = (a.lat - b.lat) * 111320;
    const x = (a.lon - b.lon) * 111320 * Math.cos(((a.lat + b.lat) / 2) * Math.PI / 180);
    return Math.hypot(x, y);
  };
  const id = (value) => String(value);
  let cachedNetwork = null;

  async function fetchNetwork(origin, destination) {
    if (window.location.protocol === 'file:') {
      throw new Error('Closure comparison requires a web address, not a file:// page. Open this project through its published site or a local web server.');
    }
    const pad = .012;
    const south = Math.min(origin.lat, destination.lat, 43.0411) - pad;
    const north = Math.max(origin.lat, destination.lat, 43.0411) + pad;
    const west = Math.min(origin.lon, destination.lon, -76.1378) - pad;
    const east = Math.max(origin.lon, destination.lon, -76.1378) + pad;
    if (cachedNetwork && south >= cachedNetwork.bounds.south && north <= cachedNetwork.bounds.north && west >= cachedNetwork.bounds.west && east <= cachedNetwork.bounds.east) return cachedNetwork;
    const query = `[out:json][timeout:25];way[highway~"motorway|trunk|primary|secondary|tertiary|residential|unclassified|service|living_street"](${south},${west},${north},${east});out body;>;out skel;`;
    // Use GET rather than POST: public Overpass mirrors are much more likely
    // to permit this from a GitHub Pages/static-site origin without a CORS
    // preflight failure. Try mirrors independently because fetch itself can
    // throw before there is a response object.
    const endpoints = [
      'https://overpass-api.de/api/interpreter',
      'https://overpass.kumi.systems/api/interpreter',
      'https://overpass.private.coffee/api/interpreter'
    ];
    let response = null;
    for (const endpoint of endpoints) {
      try {
        const candidate = await fetch(`${endpoint}?data=${encodeURIComponent(query)}`);
        if (candidate.ok) { response = candidate; break; }
      } catch (_) {
        // Try the next public mirror.
      }
    }
    if (!response) throw new Error('The live street-network service is unavailable. The project map remains available; please try the route comparison again shortly.');
    const raw = await response.json();
    const nodes = new Map(raw.elements.filter((item) => item.type === 'node').map((item) => [id(item.id), { id: id(item.id), lat: item.lat, lon: item.lon }]));
    const ways = raw.elements.filter((item) => item.type === 'way' && roadTypes.has(item.tags?.highway));
    cachedNetwork = { nodes, ways, bounds: { south, north, west, east } };
    return cachedNetwork;
  }

  function buildGraph(network, closure) {
    const edges = new Map();
    const add = (from, to, way) => {
      const a = network.nodes.get(id(from));
      const b = network.nodes.get(id(to));
      const middle = a && b ? { lat: (a.lat + b.lat) / 2, lon: (a.lon + b.lon) / 2 } : null;
      if (!a || !b || (closure && middle && distance(middle, closure) < 58)) return;
      const meters = distance(a, b);
      const seconds = meters / ((speeds[way.tags.highway] || 20) * .44704);
      const edge = { to: id(to), meters, seconds, name: way.tags.name || way.tags.ref || 'local connector' };
      if (!edges.has(id(from))) edges.set(id(from), []);
      edges.get(id(from)).push(edge);
    };
    network.ways.forEach((way) => {
      const oneWay = ['yes', '1', 'true'].includes(way.tags.oneway) || way.tags.highway === 'motorway';
      for (let index = 1; index < way.nodes.length; index += 1) {
        add(way.nodes[index - 1], way.nodes[index], way);
        if (!oneWay) add(way.nodes[index], way.nodes[index - 1], way);
      }
    });
    return edges;
  }

  function closestNode(nodes, point) {
    let best = null;
    let nearest = Infinity;
    nodes.forEach((node) => { const meters = distance(node, point); if (meters < nearest) { best = node.id; nearest = meters; } });
    return best;
  }

  function shortestPath(nodes, edges, start, end) {
    const costs = new Map([[start, 0]]);
    const previous = new Map();
    const queue = [{ node: start, cost: 0 }];
    while (queue.length) {
      queue.sort((a, b) => a.cost - b.cost);
      const current = queue.shift();
      if (current.cost !== costs.get(current.node)) continue;
      if (current.node === end) break;
      (edges.get(current.node) || []).forEach((edge) => {
        const nextCost = current.cost + edge.seconds;
        if (nextCost < (costs.get(edge.to) || Infinity)) {
          costs.set(edge.to, nextCost);
          previous.set(edge.to, { from: current.node, edge });
          queue.push({ node: edge.to, cost: nextCost });
        }
      });
    }
    if (!previous.has(end)) return null;
    const segments = [];
    for (let node = end; node !== start;) { const step = previous.get(node); segments.unshift({ from: step.from, to: node, ...step.edge }); node = step.from; }
    return segments;
  }

  function solve(network, origin, destination, closure = null) {
    const edges = buildGraph(network, closure);
    const start = closestNode(network.nodes, origin);
    const end = closestNode(network.nodes, destination);
    const segments = shortestPath(network.nodes, edges, start, end);
    if (!segments) return null;
    return {
      points: [network.nodes.get(start), ...segments.map((segment) => network.nodes.get(segment.to))],
      segments,
      distance: segments.reduce((sum, segment) => sum + segment.meters, 0),
      seconds: segments.reduce((sum, segment) => sum + segment.seconds, 0)
    };
  }
  async function compare(origin, destination, closure) {
    const network = await fetchNetwork(origin, destination);
    return { open: solve(network, origin, destination), closed: solve(network, origin, destination, closure) };
  }
  return { compare };
})();
