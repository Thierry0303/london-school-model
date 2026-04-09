const axios = require("axios");
const { setCors } = require("../_lib/helpers");

const ZOOPLA_BASE = "https://api.zoopla.co.uk/api/v1";

module.exports = async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    const { id } = req.query;
    if (!id) return res.status(400).json({ error: "id is required" });

    const { data } = await axios.get(`${ZOOPLA_BASE}/property_listings.json`, {
      params: {
        api_key:    process.env.ZOOPLA_API_KEY,
        listing_id: id,
      },
    });

    return res.status(200).json(data.listing?.[0] || {});
  } catch (err) {
    console.error("[/api/property]", err.message);
    return res.status(500).json({ error: err.message });
  }
};
