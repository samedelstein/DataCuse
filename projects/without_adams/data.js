window.ACCESS_LAB = {
  center: [43.0414, -76.1365],
  destinations: [
    { name: 'Upstate ED', type: 'Emergency department', point: [43.0410, -76.1372] },
    { name: 'Crouse Health', type: 'Hospital / ED access', point: [43.0442, -76.1361] },
    { name: 'Syracuse VA Medical Center', type: 'Hospital access', point: [43.0425, -76.1332] },
    { name: 'Downtown / BL-81', type: 'Network gateway', point: [43.0379, -76.1440] }
  ],
  routes: [
    { id: 'adams', name: 'East Adams Street', points: [[43.0402,-76.1469],[43.0406,-76.1425],[43.0409,-76.1391],[43.0411,-76.1365],[43.0416,-76.1331]], role: 'east–west hospital and city connection' },
    { id: 'harrison', name: 'Harrison Street', points: [[43.0426,-76.1461],[43.0429,-76.1427],[43.0433,-76.1395],[43.0436,-76.1365],[43.0440,-76.1330]], role: 'parallel east–west relief route' },
    { id: 'irving', name: 'Irving Avenue', points: [[43.0387,-76.1367],[43.0410,-76.1367],[43.0445,-76.1360],[43.0474,-76.1355]], role: 'hospital frontage and I-690 approach' },
    { id: 'crouse', name: 'Crouse Avenue', points: [[43.0391,-76.1401],[43.0426,-76.1391],[43.0457,-76.1380],[43.0488,-76.1371]], role: 'parallel north–south access route' },
    { id: 'almond', name: 'Almond / BL-81', points: [[43.0345,-76.1453],[43.0380,-76.1439],[43.0418,-76.1427],[43.0462,-76.1414]], role: 'Community Grid gateway' }
  ],
  // City Streets centerline: E Adams Street between Elizabeth Blackwell
  // Street (-76.1391026) and Irving Avenue (-76.1366438). This is not the
  // nearby Marshall, Waverly, or Harrison alignment.
  closure: { points: [[43.04267448,-76.13910263],[43.04267402,-76.13783637],[43.04266629,-76.13664380]], name: 'Proposed East Adams closure: Elizabeth Blackwell Street to Irving Avenue' },
  closureMidpoint: { lon: -76.1378, lat: 43.04267 },
  detourWaypoints: [
    { lon: -76.1391, lat: 43.0432 },
    { lon: -76.1360, lat: 43.0437 }
  ],
  projectCorridors: {
    formerI81: [
      { lon: -76.14231, lat: 43.03685 }, { lon: -76.14212, lat: 43.03942 },
      { lon: -76.14257, lat: 43.04445 }, { lon: -76.14245, lat: 43.04768 },
      { lon: -76.14434, lat: 43.05093 }, { lon: -76.15060, lat: 43.05253 }
    ],
    futureBL81: [
      { lon: -76.14154, lat: 43.03751 }, { lon: -76.14172, lat: 43.03791 },
      { lon: -76.14202, lat: 43.03860 }, { lon: -76.14222, lat: 43.03992 },
      { lon: -76.14230, lat: 43.04052 }, { lon: -76.14233, lat: 43.04197 },
      { lon: -76.14227, lat: 43.04435 }, { lon: -76.14206, lat: 43.05332 }
    ]
  },
  aadtService: 'https://gis.dot.ny.gov/hostingny/rest/services/Roadways/Traffic_Monitoring/FeatureServer/1/query',
  fireIncidentsService: 'https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Fire_Incidents/FeatureServer/0/query',
  scenarios: [
    {
      id: 'open', label: 'Community Grid + Adams open', tag: 'Future network',
      summary: 'The Community Grid is in place and East Adams remains publicly connected between downtown, Upstate, Crouse, the VA, and University Hill.',
      description: 'This is the future-network baseline: Business Loop 81 runs on the Almond corridor while East Adams remains an east–west medical-district connection.',
      riskRoutes: [], openRoutes: ['adams','harrison','irving','crouse','almond'],
      focus: ['Protect the Upstate ED approach without blocking general or emergency circulation.', 'Design a secure hospital connection that does not sever the public street network.', 'Use the future Adams complete-street project to add transit, walking, and cycling capacity.'],
      tests: ['Emergency vehicles retain at least two independently usable approaches.', 'Peak queues do not block ED driveways, fire routes, or crosswalks.', 'The facility design meets trauma, security, and patient-transfer needs without a public-network break.']
    },
    {
      id: 'close', label: 'Community Grid + Adams closure', tag: 'Hospital proposal',
      summary: 'The Community Grid is in place, but the Adams block from Elizabeth Blackwell to Irving is closed for the Upstate expansion.',
      description: 'Only trips whose normal path crosses that block should divert—primarily to the Harrison Street connection. Trips that do not use the block should not be assigned a detour.',
      riskRoutes: ['adams'], openRoutes: ['harrison','irving','crouse','almond'],
      focus: ['Test every approach in the AM, PM, event, snow, and construction conditions—not daily averages alone.', 'Protect Crouse/VA access from queues created by diverted traffic.', 'Treat a new or relocated fire/EMS facility as a coverage decision supported by response reliability, not simply proximity.'],
      tests: ['Independent emergency review finds no unacceptable reliability loss.', 'Calibrated intersection and queue analysis clears all critical hospital approaches.', 'Signed detours, signal priority, and incident plans work before permanent closure.']
    },
    {
      id: 'protected', label: 'Expansion + protected crossing', tag: 'Design alternative',
      summary: 'The Upstate expansion proceeds while Adams retains an emergency-capable public crossing through a protected design.',
      description: 'This tests a design alternative: separate hospital operations from through movement while retaining the network connection required by public access and emergency redundancy.',
      riskRoutes: [], openRoutes: ['adams','harrison','irving','crouse','almond'],
      focus: ['Define who can use the connection and how emergency priority works before design approval.', 'Preserve ADA, transit, walking, cycling, and apparatus clearances—not just car movement.', 'Use access controls that are legible during a crash, power loss, snow emergency, or construction phase.'],
      tests: ['Public and emergency operating rules are enforceable and fail-safe.', 'The design preserves redundant movement for Crouse, Upstate, VA, and fire/EMS.', 'An independent constructability review proves the connection can remain usable through construction.']
    }
  ],
  recommendations: [
    { number: '01', title: 'Lock emergency redundancy first', text: 'Map apparatus-compatible routes, test them with Fire/EMS, and require two independent approaches to each ED before any street action.' },
    { number: '02', title: 'Build a hospital-access signal package', text: 'Coordinate signal timing, emergency preemption, queue detection, curb controls, and wayfinding across Adams, Harrison, Irving, Crouse, and Almond.' },
    { number: '03', title: 'Protect Crouse and VA access', text: 'Treat Irving and its cross-streets as a shared medical-district corridor with explicit driveway, transit, loading, and emergency reliability targets.' },
    { number: '04', title: 'Use a phased, reversible decision', text: 'Start with a monitored pilot or construction-stage operating plan; publish observed queues, travel-time reliability, and access failures before permanence.' }
  ],
  sources: [
    { name: 'NYSDOT I-81 Viaduct Project', url: 'https://webapps.dot.ny.gov/i-81-viaduct-project', use: 'Construction contracts, Community Grid context, Crouse/Irving work', status: 'Primary source — refresh per phase' },
    { name: 'City of Syracuse Community Grid Vision Plan', url: 'https://www.syr.gov/Projects/Active-Projects/Infrastructure-Overview/I-81-Viaduct-Project/Community-Grid-Vision-Plan', use: 'Adams/Harrison complete-street and access vision', status: 'Primary planning source' },
    { name: 'City Community Grid Streets — Almond', url: 'https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Community_Grid_Streets_(CG)/FeatureServer/5', use: 'Published Almond Street / future BL-81 alignment shown on the map', status: 'Geometry snapshot — verify when City republishes' },
    { name: 'NYSDOT Traffic Data Viewer', url: 'https://data.ny.gov/Transportation/NYS-Traffic-Data-Viewer/7wmy-q6mb', use: 'AADT/ADT and count-location discovery', status: 'Required before numeric model' },
    { name: 'SMTC Traffic Counts', url: 'https://smtcmpo.org/data/traffic-counts/', use: 'Regional counts and model coordination', status: 'Required before numeric model' },
    { name: 'City of Syracuse Open Data', url: 'https://data.syr.gov/', use: 'Road centerlines, facilities, aggregate public-safety data where releasable', status: 'Verify license, vintage, and privacy rules' }
  ]
};
