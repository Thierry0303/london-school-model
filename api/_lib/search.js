const {
  setCors, geocodePostcode, fetchProperties,
  fetchNearbySchools, calcDistances,
} = require("./_lib/helpers");

module.exports = async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    const {
      postcode,
      radius     = "0.5",
      tenure     = "sale",
      beds_min   = "2",
      ofsted_min = "2",
    } = req.query;

    if (!postcode) return res.status(400).json({ error: "postcode is required" });

    const { lat, lng } = await geocodePostcode(postcode);

    const [rawProperties, schools] = await Promise.all([
      fetchProperties({
        lat, lng,
        radiusMiles:    parseFloat(radius),
        listing_status: tenure,
        beds_min:       parseInt(beds_min),
      }),
      fetchNearbySchools(lat, lng, parseFloat(radius) + 0.5),
    ]);

    const filteredSchools = schools.filter(
      (s) => parseInt(s.rating) <= parseInt(ofsted_min)
    );

    let enrichedProperties;

    if (rawProperties.length && filteredSchools.length) {
      const nearestSchools = filteredSchools.slice(0, 3);
      const distances = await calcDistances(
        rawProperties.map((p) => ({ lat: p.lat, lng: p.lng })),
        nearestSchools.map((s) => ({ lat: s.lat, lng: s.lng }))
      );
      enrichedProperties = rawProperties.map((prop, i) => {
        const schoolsWithDist = nearestSchools.map((school, j) => ({
          ...school,
          walkDistance: distances[i]?.[j]?.distance || "N/A",
          walkTime:     distances[i]?.[j]?.duration  || "N/A",
        }));
        schoolsWithDist.sort((a, b) =>
          (parseFloat(a.walkDistance) || 999) - (parseFloat(b.walkDistance) || 999)
        );
        return { ...prop, nearbySchools: schoolsWithDist };
      });
    } else {
      enrichedProperties = rawProperties.map((prop) => ({
        ...prop,
        nearbySchools: filteredSchools.slice(0, 3),
      }));
    }

    return res.status(200).json({
      meta: {
        postcode, lat, lng,
        radius:       parseFloat(radius),
        total:        enrichedProperties.length,
        schoolsFound: filteredSchools.length,
      },
      properties: enrichedProperties,
      schools:    filteredSchools,
    });

  } catch (err) {
    console.error("[/api/search]", err.message);
    return res.status(500).json({ error: err.message });
  }
};
