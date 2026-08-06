"use client";

import type { Feature, FeatureCollection, LineString, MultiLineString } from "geojson";
import type * as Leaflet from "leaflet";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Year = 2018 | 2021 | 2022;
type RiskFilter = "top1" | "top5" | "top10" | "top25" | "all" | "lower50";
type Panel = "segment" | "data" | "performance";

type RiskProperties = {
  segmentId: number;
  cityStreetId: number | null;
  street: string;
  roadClass: string | null;
  streetType: string | null;
  lengthFt: number;
  soil: string | null;
  parcelCount: number | null;
  medianBuildYear: number | null;
  oldestBuildYear: number | null;
  pre1940Share: number | null;
  aadt: number | null;
  hydrantDistanceFt: number | null;
  hydrantPsi: number | null;
  hydrantTapIn: number | null;
  pressureZone: string | null;
  score: number;
  rank: number;
  percentile: number;
  recordedBreak: boolean;
  breakCount: number;
  historyGap: boolean;
  breakRatePrev1: number | null;
  breakRatePrev3: number | null;
  breakRateAll: number | null;
  nearbyBreakRatePrev3: number | null;
  yearsSinceBreak: number | null;
  priorFreezeThawDays: number | null;
  relative: Record<string, number | null>;
};

type RiskFeature = Feature<LineString | MultiLineString, RiskProperties>;
type RiskCollection = FeatureCollection<LineString | MultiLineString, RiskProperties> & {
  metadata: {
    targetYear: Year;
    horizon: string;
    question: string;
    segments: number;
    observedBreakSegments: number;
    averagePrecision: number;
    rocAuc: number;
    top10Recall: number;
    top10Lift: number;
    top10Recall95: { lower_95: number; median: number; upper_95: number };
  };
};

const FILTERS: { id: RiskFilter; label: string }[] = [
  { id: "top1", label: "Top 1%" },
  { id: "top5", label: "Top 5%" },
  { id: "top10", label: "Top 10%" },
  { id: "top25", label: "Top 25%" },
  { id: "all", label: "All" },
  { id: "lower50", label: "Lower 50%" },
];

const INPUTS = [
  ["Confirmed breaks", "City records for 2004–2019, 2021, and 2022; points were matched to streets."],
  ["Street segments", "City centerlines define the unit being ranked. Segment length and road class are included."],
  ["Parcel context", "2025 Q3 nearby parcel counts and building-year proxies; these are not pipe ages."],
  ["Soils", "USDA SSURGO soil map units attached to each street segment."],
  ["Traffic", "NYSDOT annual average daily traffic and truck-volume proxies."],
  ["Hydrant context", "A public 2018 layer supplies nearby pressure zone, calculated PSI, elevation, and tap size."],
  ["Weather", "Prior-year NOAA Syracuse temperature, snow, precipitation, and freeze–thaw measures."],
];

const LIMITS = [
  "The public water-main layer has no pipe records, so material, diameter, installation year, condition, and precise pipe geometry are absent.",
  "Confirmed 2020 and 2023–present break outcomes were not publicly available. The 2019 layer is partial.",
  "Some enrichment layers are current or legacy snapshots, not what would truly have been known in each forecast year.",
  "Break points can be assigned to the wrong street near intersections, parallel streets, or imprecise addresses.",
  "The model ranks associations. It does not identify a physical defect or prove that any input caused a break.",
];

function riskColor(rank: number, total: number) {
  const share = rank / total;
  if (share <= 0.01) return "#b93b24";
  if (share <= 0.05) return "#df6c32";
  if (share <= 0.1) return "#e9a33a";
  if (share <= 0.25) return "#dfc16a";
  if (share <= 0.5) return "#78a69a";
  return "#7e98a1";
}

function topLabel(rank: number, total: number) {
  const percent = Math.max(1, Math.ceil((rank / total) * 100));
  return percent <= 50 ? `Top ${percent}%` : `Lower ${100 - percent + 1}%`;
}

function matchesFilter(feature: RiskFeature, filter: RiskFilter, total: number) {
  const share = feature.properties.rank / total;
  if (filter === "all") return true;
  if (filter === "lower50") return share > 0.5;
  return share <= Number(filter.replace("top", "")) / 100;
}

function pct(value: number | null, digits = 0) {
  return value === null ? "Not available" : `${(value * 100).toFixed(digits)}%`;
}

function valueOrDash(value: string | number | null, suffix = "") {
  return value === null || value === "" ? "Not available" : `${value}${suffix}`;
}

function relativeText(value: number | null) {
  return value === null ? "Comparison unavailable" : `Higher than ${value}% of segments`;
}

function AppMap({
  data,
  visible,
  selectedId,
  onSelect,
}: {
  data: RiskCollection;
  visible: Set<number>;
  selectedId: number | null;
  onSelect: (feature: RiskFeature, focus?: boolean) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Leaflet.Map | null>(null);
  const layerRef = useRef<Leaflet.GeoJSON | null>(null);
  const leafletRef = useRef<typeof Leaflet | null>(null);

  useEffect(() => {
    let active = true;
    async function initialize() {
      if (!containerRef.current || mapRef.current) return;
      const L = await import("leaflet");
      if (!active || !containerRef.current) return;
      leafletRef.current = L;
      const map = L.map(containerRef.current, {
        zoomControl: false,
        preferCanvas: true,
        minZoom: 11,
        maxZoom: 18,
      }).setView([43.0477, -76.1474], 12.7);
      L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 20,
      }).addTo(map);
      L.control.zoom({ position: "bottomright" }).addTo(map);
      mapRef.current = map;
    }
    initialize();
    return () => {
      active = false;
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const L = leafletRef.current;
    const map = mapRef.current;
    if (!L || !map) {
      const timer = window.setTimeout(() => window.dispatchEvent(new Event("resize")), 100);
      return () => window.clearTimeout(timer);
    }
    if (layerRef.current) map.removeLayer(layerRef.current);
    const filtered: RiskCollection = {
      ...data,
      features: data.features.filter((feature) => visible.has(feature.properties.segmentId)),
    };
    const layer = L.geoJSON(filtered, {
      renderer: L.canvas({ padding: 0.5 }),
      style: (feature) => {
        const properties = (feature as RiskFeature).properties;
        const selected = properties.segmentId === selectedId;
        return {
          color: selected ? "#102f3a" : riskColor(properties.rank, data.metadata.segments),
          weight: selected ? 7 : properties.rank / data.metadata.segments <= 0.1 ? 5 : 3,
          opacity: selected ? 1 : 0.9,
          lineCap: "round",
        };
      },
      onEachFeature: (feature, layerItem) => {
        const riskFeature = feature as RiskFeature;
        const p = riskFeature.properties;
        layerItem.bindTooltip(
          `<strong>${p.street}</strong><br>${topLabel(p.rank, data.metadata.segments)} · ${(p.score * 100).toFixed(1)}% score`,
          { sticky: true, direction: "top" },
        );
        layerItem.on("click", () => onSelect(riskFeature));
      },
    }).addTo(map);
    layerRef.current = layer;
    return () => {
      if (map.hasLayer(layer)) map.removeLayer(layer);
    };
  }, [data, onSelect, selectedId, visible]);

  return <div ref={containerRef} className="map-canvas" aria-label="Interactive map of Syracuse street-segment risk" />;
}

export default function RiskExplorer() {
  const [year, setYear] = useState<Year>(2022);
  const [data, setData] = useState<RiskCollection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskFilter, setRiskFilter] = useState<RiskFilter>("top10");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<"high" | "low" | "street">("high");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [panel, setPanel] = useState<Panel>("segment");

  useEffect(() => {
    const controller = new AbortController();
    // Reset request state when the selected retrospective layer changes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    fetch(`data/streets-risk-${year}.geojson`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`Unable to load ${year} risk data.`);
        return response.json() as Promise<RiskCollection>;
      })
      .then((payload) => {
        setData(payload);
        setSelectedId(payload.features[0]?.properties.segmentId ?? null);
        setLoading(false);
      })
      .catch((reason: Error) => {
        if (reason.name !== "AbortError") {
          setError(reason.message);
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, [year]);

  const filtered = useMemo(() => {
    if (!data) return [];
    const search = query.trim().toUpperCase();
    const rows = data.features.filter(
      (feature) =>
        matchesFilter(feature, riskFilter, data.metadata.segments) &&
        (!search || feature.properties.street.toUpperCase().includes(search)),
    );
    return rows.sort((a, b) => {
      if (sort === "low") return b.properties.rank - a.properties.rank;
      if (sort === "street") return a.properties.street.localeCompare(b.properties.street);
      return a.properties.rank - b.properties.rank;
    });
  }, [data, query, riskFilter, sort]);

  const visible = useMemo(() => new Set(filtered.map((feature) => feature.properties.segmentId)), [filtered]);
  const selected = useMemo(
    () => data?.features.find((feature) => feature.properties.segmentId === selectedId) ?? null,
    [data, selectedId],
  );

  const handleSelect = useCallback((feature: RiskFeature) => {
    setSelectedId(feature.properties.segmentId);
    setPanel("segment");
  }, []);

  useEffect(() => {
    if (filtered.length && !filtered.some((feature) => feature.properties.segmentId === selectedId)) {
      // Keep the detail panel synchronized with the currently visible result set.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedId(filtered[0].properties.segmentId);
    }
  }, [filtered, selectedId]);

  const evidence = useMemo(() => {
    if (!selected) return [];
    const p = selected.properties;
    return [
      {
        title: "Observed break history",
        value: pct(p.breakRateAll),
        note: "Share of complete prior observed years with a matched break",
        relative: p.relative.history,
      },
      {
        title: "Recent nearby breaks",
        value: pct(p.nearbyBreakRatePrev3),
        note: "Average matched breaks within 300 feet across the prior three observed years",
        relative: p.relative.nearby,
      },
      {
        title: "Infrastructure-age context",
        value: valueOrDash(p.medianBuildYear),
        note: "Median year built for nearby parcels—not the pipe installation year",
        relative: p.relative.older_context,
      },
      {
        title: "Segment exposure",
        value: `${Math.round(p.lengthFt).toLocaleString()} ft`,
        note: "Longer segments have more physical opportunity for a recorded event",
        relative: p.relative.length,
      },
      {
        title: "Traffic context",
        value: p.aadt === null ? "Not available" : `${p.aadt.toLocaleString()} vehicles/day`,
        note: "Matched NYSDOT traffic proxy",
        relative: p.relative.traffic,
      },
    ].sort((a, b) => (b.relative ?? -1) - (a.relative ?? -1));
  }, [selected]);

  return (
    <main className="app-shell">
      <header className="site-header">
        <div className="brand-block">
          <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
          <div>
            <p className="eyebrow">Public-data research prototype</p>
            <h1>Syracuse Water Main Risk Explorer</h1>
          </div>
        </div>
        <div className="horizon-card">
          <span>Prediction horizon</span>
          <strong>1 calendar year</strong>
          <small>Retrospective test—not a live 2026 forecast</small>
        </div>
      </header>

      <section className="forecast-strip" aria-label="Forecast framing">
        <div className="year-picker">
          <span>Test year</span>
          {([2018, 2021, 2022] as Year[]).map((option) => (
            <button key={option} className={year === option ? "active" : ""} onClick={() => setYear(option)}>
              {option}
            </button>
          ))}
        </div>
        <p>
          <strong>The question:</strong> Which street segments were most likely to have a recorded main break during {year},
          using earlier observed break history and the available public proxy layers?
        </p>
        <button className="method-link" onClick={() => setPanel("data")}>What went into this? →</button>
      </section>

      <section className="workspace">
        <aside className="results-panel" aria-label="Street results">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Prioritize segments</p>
              <h2>Street rankings</h2>
            </div>
            <span className="count-pill">{filtered.length.toLocaleString()}</span>
          </div>
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search a street" />
          </label>
          <div className="filter-block">
            <span className="control-label">Risk range</span>
            <div className="risk-filters">
              {FILTERS.map((filter) => (
                <button
                  key={filter.id}
                  className={riskFilter === filter.id ? "active" : ""}
                  onClick={() => setRiskFilter(filter.id)}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
          <label className="sort-row">
            <span>Sort</span>
            <select value={sort} onChange={(event) => setSort(event.target.value as typeof sort)}>
              <option value="high">Highest risk first</option>
              <option value="low">Lowest risk first</option>
              <option value="street">Street name</option>
            </select>
          </label>
          <div className="street-list" role="region" aria-label="Scrollable street rankings" tabIndex={0}>
            {filtered.slice(0, 250).map((feature) => {
              const p = feature.properties;
              return (
                <button
                  key={p.segmentId}
                  className={`street-row ${selectedId === p.segmentId ? "selected" : ""}`}
                  onClick={() => handleSelect(feature)}
                >
                  <span className="risk-dot" style={{ background: riskColor(p.rank, data?.metadata.segments ?? 5650) }} />
                  <span className="street-copy">
                    <strong>{p.street}</strong>
                    <small>Segment {p.segmentId} · {topLabel(p.rank, data?.metadata.segments ?? 5650)}</small>
                  </span>
                  <span className="row-score">{(p.score * 100).toFixed(1)}%</span>
                </button>
              );
            })}
            {filtered.length > 250 && <p className="list-note">Showing the first 250 results. Narrow the risk range or search by street.</p>}
            {!loading && filtered.length === 0 && <p className="empty-state">No streets match these filters.</p>}
          </div>
        </aside>

        <div className="map-panel">
          {loading && <div className="map-state"><span className="loader" />Loading street risk…</div>}
          {error && <div className="map-state error">{error}</div>}
          {data && <AppMap data={data} visible={visible} selectedId={selectedId} onSelect={handleSelect} />}
          {data && (
            <div className="map-legend">
              <span>Lower rank</span>
              <i className="legend-gradient" />
              <span>Highest rank</span>
            </div>
          )}
          <div className="map-note">Click a colored street segment to inspect it</div>
        </div>

        <aside className="detail-panel" aria-live="polite">
          <nav className="detail-tabs" aria-label="Detail sections">
            <button className={panel === "segment" ? "active" : ""} onClick={() => setPanel("segment")}>Segment</button>
            <button className={panel === "data" ? "active" : ""} onClick={() => setPanel("data")}>Data & limits</button>
            <button className={panel === "performance" ? "active" : ""} onClick={() => setPanel("performance")}>Test</button>
          </nav>

          {panel === "segment" && selected && data && (
            <div className="detail-content">
              <p className="eyebrow">Selected street segment</p>
              <h2>{selected.properties.street}</h2>
              <p className="segment-id">City segment {selected.properties.segmentId}</p>
              <div className="score-card">
                <div className="score-ring" style={{ "--score-color": riskColor(selected.properties.rank, data.metadata.segments) } as React.CSSProperties}>
                  <strong>{(selected.properties.score * 100).toFixed(1)}%</strong>
                  <span>model score</span>
                </div>
                <div>
                  <span className="rank-badge">{topLabel(selected.properties.rank, data.metadata.segments)}</span>
                  <p>Rank <strong>#{selected.properties.rank.toLocaleString()}</strong> of {data.metadata.segments.toLocaleString()}</p>
                </div>
              </div>
              <div className={`outcome-card ${selected.properties.recordedBreak ? "break" : "no-break"}`}>
                <span>{year} recorded outcome</span>
                <strong>{selected.properties.recordedBreak ? `Break recorded${selected.properties.breakCount > 1 ? ` (${selected.properties.breakCount})` : ""}` : "No matched break recorded"}</strong>
                <small>This outcome was held back for testing; it was not an input to the score.</small>
              </div>
              <div className="section-title">
                <h3>Why it may be worth checking</h3>
                <span>Context, not proof</span>
              </div>
              <p className="helper-copy">These are the segment’s strongest relative context signals among important model inputs. They are not causal explanations.</p>
              <div className="evidence-list">
                {evidence.slice(0, 4).map((item) => (
                  <article key={item.title} className="evidence-card">
                    <div>
                      <span>{item.title}</span>
                      <strong>{item.value}</strong>
                    </div>
                    <div className="percentile-track"><i style={{ width: `${item.relative ?? 0}%` }} /></div>
                    <small>{relativeText(item.relative)} · {item.note}</small>
                  </article>
                ))}
              </div>
              <details className="context-details">
                <summary>View additional segment inputs</summary>
                <dl>
                  <div><dt>Pressure zone</dt><dd>{valueOrDash(selected.properties.pressureZone)}</dd></div>
                  <div><dt>Calculated hydrant PSI</dt><dd>{valueOrDash(selected.properties.hydrantPsi)}</dd></div>
                  <div><dt>Nearest hydrant</dt><dd>{valueOrDash(selected.properties.hydrantDistanceFt, " ft")}</dd></div>
                  <div><dt>Soil map unit</dt><dd>{valueOrDash(selected.properties.soil)}</dd></div>
                  <div><dt>Prior-year freeze–thaw days</dt><dd>{valueOrDash(selected.properties.priorFreezeThawDays)}</dd></div>
                  <div><dt>Years since matched break</dt><dd>{valueOrDash(selected.properties.yearsSinceBreak)}</dd></div>
                </dl>
              </details>
              <div className="warning-box">
                <strong>Why this segment’s answer may be wrong</strong>
                <ul>
                  <li>We do not know the actual main’s age, material, diameter, condition, or replacement status.</li>
                  {selected.properties.historyGap && <li>Its recent-history window crosses missing or partial break-data years.</li>}
                  <li>Parcel, traffic, soil, and hydrant information are proxies and may not describe the buried pipe.</li>
                </ul>
              </div>
            </div>
          )}

          {panel === "data" && (
            <div className="detail-content">
              <p className="eyebrow">Transparent by design</p>
              <h2>Data inputs & limits</h2>
              <p className="lede">The model backs into risk at the street level because the public water-main inventory contains no pipe records.</p>
              <h3 className="subheading">Available inputs</h3>
              <div className="source-list">
                {INPUTS.map(([name, description]) => (
                  <article key={name}><span className="source-check">✓</span><div><strong>{name}</strong><p>{description}</p></div></article>
                ))}
              </div>
              <h3 className="subheading">Reasons to be cautious</h3>
              <ol className="limits-list">
                {LIMITS.map((limit, index) => <li key={limit}><span>{index + 1}</span><p>{limit}</p></li>)}
              </ol>
              <div className="interpret-box"><strong>Best use</strong><p>Prioritize inspection, records review, and field validation. Do not use the score alone to replace a main or declare a street unsafe.</p></div>
            </div>
          )}

          {panel === "performance" && data && (
            <div className="detail-content">
              <p className="eyebrow">Held-out evaluation</p>
              <h2>How the {year} test performed</h2>
              <p className="lede">Every score shown for {year} was generated without using that year’s recorded outcomes.</p>
              <div className="metric-grid">
                <article><strong>{data.metadata.observedBreakSegments}</strong><span>segments with a recorded break</span></article>
                <article><strong>{(data.metadata.top10Recall * 100).toFixed(1)}%</strong><span>of break streets captured in the top 10%</span></article>
                <article><strong>{data.metadata.top10Lift.toFixed(2)}×</strong><span>better concentration than choosing at random</span></article>
                <article><strong>{data.metadata.rocAuc.toFixed(3)}</strong><span>ROC area under the curve</span></article>
              </div>
              <div className="interval-card">
                <span>Uncertainty around top-10% recall</span>
                <strong>{(data.metadata.top10Recall95.lower_95 * 100).toFixed(1)}–{(data.metadata.top10Recall95.upper_95 * 100).toFixed(1)}%</strong>
                <small>95% bootstrap interval</small>
              </div>
              <h3 className="subheading">What “accuracy” means here</h3>
              <p className="body-copy">Breaks are rare, so a simple percent-correct score would be misleading. The useful test is whether a small inspection list contains substantially more future break streets than a random list. Rankings are more trustworthy than the exact percentage shown for any one segment.</p>
              <h3 className="subheading">Time horizon</h3>
              <p className="body-copy">This is a <strong>one-calendar-year model</strong>. The {year} view estimates risk between January 1 and December 31, {year}. It does not estimate lifetime failure risk or provide a current 2026 forecast.</p>
            </div>
          )}
        </aside>
      </section>

      <footer>
        <p><strong>Research prototype.</strong> Built from publicly available City of Syracuse, New York State, USDA, and NOAA data.</p>
        <p>Last model outcome year: 2022 · Prediction unit: street segment · Horizon: one year</p>
      </footer>
    </main>
  );
}
