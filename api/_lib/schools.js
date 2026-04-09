const { setCors, geocodePostcode, fetchNearbySchools } = require("./_lib/helpers");

module.exports = async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    const { postcode, radius = "1" } = req.query;
    if (!postcode) return res.status(400).json({ error: "postcode is required" });

    const { lat, lng } = await geocodePostcode(postcode);
    const schools = await fetchNearbySchools(lat, lng, parseFloat(radius));

    return res.status(200).json({ schools });
  } catch (err) {
    console.error("[/api/schools]", err.message);
    return res.status(500).json({ error: err.message });
  }
};
