const axios = require("axios");
const fs = require("fs");
const path = require("path");

const MAPS_BASE   = "https://maps.googleapis.com/maps/api";
const OFSTED_BASE = "https://api.ofsted.gov.uk/v1";

const _cache = new Map();

let schoolsData = {};
try {
  const schoolsPath = path.join(__dirname, "../../schools.json");
  const rawData = fs.readFileSync(schoolsPath, "utf8");
  const schools = JSON.parse(rawData);
  schools.forEach(s => {
    schoolsData[s.name] = s;
  });
  console.log(`Loaded ${Object.keys(schoolsData).length} schools from schools.json`);
} catch (e) {
  console.error("Could not load schools.json:", e.message);
}

function cacheGet(key) {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expires) { _cache.delete(key); return null; }
  return entry.value;
}

function cacheSet(key, value, ttlSeconds = 300) {
  _cache.set(key, { value, expires: Date.now() + ttlSeconds * 1000 });
}

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function ofstedLabel(rating) {
  const map = { 1: "Outstanding", 2: "Good", 3: "Requires improvement", 4: "Inadequate" };
  return map[parseInt(rating)] || "Not rated";
}

async function geocodePostcode(postcode) {
  const key = `geo:${postcode}`;
  const cached = cacheGet(key);
  if (cached) return cached;
  const { data } = await axios.get(`${MAPS_BASE}/geocode/json`, {
    params: { address: `${postcode}, London, UK`, key: process.env.GOOGLE_MAPS_API_KEY },
  });
  if (!data.results.length) throw new Error(`Could not geocode: ${postcode}`);
  const { lat, lng } = data.results[0].geometry.location;
  const result = { lat, lng, formatted: data.results[0].formatted_address };
  cacheSet(key, result, 3600);
  return result;
}

async function fetchNearbySchools(lat, lng, radiusMiles = 1) {
  const key = `schools:${lat.toFixed(4)}:${lng.toFixed(4)}:${radiusMiles}`;
  const cached = cacheGet(key);
  if (cached) return cached;
  
  const { data } = await axios.get(`${OFSTED_BASE}/inspections`, {
    params: { lat, lon: lng, distance: Math.ceil(radiusMiles * 1609), phase: "primary,secondary", rows: 10 },
  }).catch(() => ({ data: { result: [] } }));
  
  const schools = (data.result || []).map((s) => {
    const schoolName = s.SCHNAME || s.name;
    const enrichment = schoolsData[schoolName] || {};
    const indData = enrichment.independent_data || {};
    
    return {
      urn: s.urn, 
      name: schoolName,
      rating: s.OFSTEDRATING || s.overallEffectiveness,
      ratingLabel: ofstedLabel(s.OFSTEDRATING || s.overallEffectiveness),
      address: s.STREET ? `${s.STREET}, ${s.TOWN}` : s.address,
      lat: parseFloat(s.lat || s.GEOG_L), 
      lng: parseFloat(s.lon || s.GEOG_E),
      phase: s.PHASE || s.phase, 
      lastInspection: s.INSPDATE || s.inspectionDate,
      independent_data: indData
    };
  });
  
  cacheSet(key, schools);
  return schools;
}

async function calcDistances(origins, destinations) {
  if (!origins.length || !destinations.length) return [];
  const { data } = await axios.get(`${MAPS_BASE}/distancematrix/json`, {
    params: {
      origins:      origins.map((o) => `${o.lat},${o.lng}`).join("|"),
      destinations: destinations.map((d) => `${d.lat},${d.lng}`).join("|"),
      mode: "walking", key: process.env.GOOGLE_MAPS_API_KEY,
    },
  });
  return data.rows.map((row) =>
    row.elements.map((el) =>
      el.status === "OK"
        ? { distance: el.distance.text, duration: el.duration.text }
        : { distance: "N/A", duration: "N/A" }
    )
  );
}

module.exports = { setCors, ofstedLabel, geocodePostcode, fetchNearbySchools, calcDistances };
