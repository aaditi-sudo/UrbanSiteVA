import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

const API = "http://127.0.0.1:5000";


// ============================================================
// TAMIL NADU BOUNDARY
// Approximate display boundary for the study region.
// ============================================================

const tamilNaduBoundary = [
  [13.4966, 79.9388],
  [13.3300, 80.1000],
  [13.1000, 80.2500],
  [12.8000, 80.3200],
  [12.4000, 80.1500],
  [12.0000, 79.9000],
  [11.6000, 79.7500],
  [11.1000, 79.7500],
  [10.6000, 79.8000],
  [10.1000, 79.8500],
  [9.6000, 79.9000],
  [9.2000, 79.9500],
  [8.7500, 77.5000],
  [8.8000, 77.1000],
  [9.1000, 77.0000],
  [9.5000, 77.1000],
  [10.0000, 77.3000],
  [10.5000, 77.4000],
  [11.0000, 77.5000],
  [11.5000, 77.3000],
  [12.0000, 77.5000],
  [12.5000, 77.7000],
  [13.0000, 77.8000],
  [13.4966, 79.9388],
];


// ============================================================
// TAMIL NADU MAP CENTER
// ============================================================

const tamilNaduCenter = [11.1271, 78.6569];


// ============================================================
// MARKER ICON
// ============================================================

const markerIcon = new L.Icon({
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});


// ============================================================
// MAP FITTER
// ============================================================

function TamilNaduView() {
  const map = useMap();

  useEffect(() => {
    const bounds = L.latLngBounds(tamilNaduBoundary);

    map.fitBounds(bounds, {
      padding: [20, 20],
    });
  }, [map]);

  return null;
}


// ============================================================
// MAP CLICK HANDLER
// ============================================================

function MapClickHandler({ onSelect }) {
  useMapEvents({
    click(e) {
      onSelect({
        latitude: e.latlng.lat,
        longitude: e.latlng.lng,
      });
    },
  });

  return null;
}


// ============================================================
// HEATMAP DATA
// These are display points distributed across Tamil Nadu.
// ============================================================

const heatPoints = [
  [13.08, 80.27],
  [12.92, 80.12],
  [12.83, 79.70],
  [12.52, 78.21],
  [12.25, 78.05],
  [11.95, 79.82],
  [11.67, 78.14],
  [11.34, 77.72],
  [11.00, 76.96],
  [10.79, 78.70],
  [10.79, 78.69],
  [10.37, 78.82],
  [10.23, 77.48],
  [9.93, 78.12],
  [9.59, 77.96],
  [9.27, 79.31],
  [9.17, 77.87],
  [8.76, 78.13],
  [8.73, 77.71],
];


// ============================================================
// CATEGORY HEAT VALUES
// ============================================================

const categoryHeatValues = {
  green: [
    0.35, 0.45, 0.60, 0.75, 0.55,
    0.80, 0.70, 0.50, 0.65, 0.45,
    0.60, 0.72, 0.50, 0.35, 0.65,
    0.50, 0.70, 0.60, 0.80,
  ],

  heat: [
    0.85, 0.75, 0.65, 0.55, 0.70,
    0.60, 0.80, 0.65, 0.90, 0.75,
    0.80, 0.65, 0.75, 0.90, 0.80,
    0.70, 0.85, 0.75, 0.90,
  ],

  uhi: [
    0.90, 0.85, 0.65, 0.50, 0.70,
    0.75, 0.80, 0.65, 0.95, 0.85,
    0.90, 0.70, 0.75, 0.90, 0.65,
    0.70, 0.85, 0.80, 0.90,
  ],

  humidity: [
    0.80, 0.85, 0.75, 0.65, 0.70,
    0.75, 0.65, 0.70, 0.55, 0.65,
    0.70, 0.75, 0.65, 0.80, 0.75,
    0.85, 0.90, 0.85, 0.90,
  ],

  carbon: [
    0.75, 0.90, 0.70, 0.60, 0.65,
    0.80, 0.85, 0.75, 0.90, 0.85,
    0.75, 0.80, 0.70, 0.65, 0.75,
    0.85, 0.80, 0.75, 0.85,
  ],
};


// ============================================================
// HEATMAP COLORS
// ============================================================

const heatColors = {
  green: {
    low: "#2563eb",
    medium: "#22c55e",
    high: "#facc15",
    extreme: "#ef4444",
  },

  heat: {
    low: "#2563eb",
    medium: "#22c55e",
    high: "#facc15",
    extreme: "#ef4444",
  },

  uhi: {
    low: "#2563eb",
    medium: "#22c55e",
    high: "#facc15",
    extreme: "#ef4444",
  },

  humidity: {
    low: "#facc15",
    medium: "#22c55e",
    high: "#06b6d4",
    extreme: "#2563eb",
  },

  carbon: {
    low: "#22c55e",
    medium: "#facc15",
    high: "#f97316",
    extreme: "#dc2626",
  },
};


// ============================================================
// HEATMAP COMPONENT
// ============================================================

function Heatmap({ category }) {
  const values = categoryHeatValues[category];

  return (
    <>
      {heatPoints.map(([lat, lon], index) => {
        const intensity = values[index];

        let color;

        if (intensity < 0.4) {
          color = heatColors[category].low;
        } else if (intensity < 0.6) {
          color = heatColors[category].medium;
        } else if (intensity < 0.8) {
          color = heatColors[category].high;
        } else {
          color = heatColors[category].extreme;
        }

        return (
          <Marker
            key={`${category}-${index}`}
            position={[lat, lon]}
            interactive={false}
            icon={L.divIcon({
              className: "heatmap-marker",
              html: `
                <div
                  style="
                    width: 150px;
                    height: 150px;
                    border-radius: 50%;
                    transform: translate(-50%, -50%);
                    background: radial-gradient(
                      circle,
                      ${color} 0%,
                      ${color}cc 12%,
                      ${color}88 28%,
                      ${color}44 48%,
                      ${color}22 65%,
                      transparent 78%
                    );
                    filter: blur(2px);
                    opacity: ${0.55 + intensity * 0.35};
                  "
                ></div>
              `,
              iconSize: [150, 150],
              iconAnchor: [75, 75],
            })}
          />
        );
      })}
    </>
  );
}


// ============================================================
// APP
// ============================================================

function App() {
  const [sites, setSites] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);

  const [category, setCategory] = useState("green");

  const [summary, setSummary] = useState(null);
  const [score, setScore] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const [selectedLocation, setSelectedLocation] = useState(null);

  const [greenInput, setGreenInput] = useState(40);

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");

  const [locationLoading, setLocationLoading] = useState(false);


  // ============================================================
  // LOAD SITE
  // ============================================================

  useEffect(() => {
    loadSites();
  }, []);


  async function loadSites() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API}/api/sites`);

      if (!response.ok) {
        throw new Error("Could not connect to backend.");
      }

      const data = await response.json();

      if (!data || data.length === 0) {
        throw new Error(
          "No Tamil Nadu site was returned by the backend."
        );
      }

      const tamilNaduSite =
        data.find(
          (site) =>
            site.name?.toLowerCase() === "tamil nadu"
        ) || data[0];

      setSites([tamilNaduSite]);
      setSelectedSite(tamilNaduSite);

      await processSite(tamilNaduSite.id);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to load Tamil Nadu site."
      );
    } finally {
      setLoading(false);
    }
  }


  // ============================================================
  // PROCESS SITE
  // ============================================================

  async function processSite(siteId) {
    try {
      setProcessing(true);
      setError("");

      // Process environmental data
      const processResponse = await fetch(
        `${API}/api/sites/${siteId}/process-data`,
        {
          method: "POST",
        }
      );

      if (!processResponse.ok) {
        const data = await processResponse.json().catch(() => ({}));

        throw new Error(
          data.error ||
            "Environmental data processing failed."
        );
      }


      // Load summary
      const summaryResponse = await fetch(
        `${API}/api/sites/${siteId}/summary`
      );

      if (!summaryResponse.ok) {
        throw new Error(
          "Could not load environmental summary."
        );
      }

      const summaryData =
        await summaryResponse.json();

      setSummary(summaryData);


      // Load score
      const scoreResponse = await fetch(
        `${API}/api/sites/${siteId}/score`
      );

      if (!scoreResponse.ok) {
        const data =
          await scoreResponse.json().catch(() => ({}));

        throw new Error(
          data.error ||
            "Could not calculate site score."
        );
      }

      const scoreData =
        await scoreResponse.json();

      setScore(scoreData);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to process site data."
      );
    } finally {
      setProcessing(false);
    }
  }


  // ============================================================
  // LOCATION SELECTION
  // ============================================================

  async function handleMapSelect(location) {
    const { latitude, longitude } = location;

    setSelectedLocation({
      ...location,
      name: "Finding location...",
    });

    setPrediction(null);
    setLocationLoading(true);

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`,
        {
          headers: {
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Location lookup failed");
      }

      const data = await response.json();

      const address = data.address || {};

      const name =
        address.city ||
        address.town ||
        address.municipality ||
        address.county ||
        address.state_district ||
        "Selected Location";

      const district =
        address.state_district ||
        address.county ||
        "";

      setSelectedLocation({
        ...location,
        name:
          district && district !== name
            ? `${name}, ${district}`
            : name,
      });

    } catch (err) {
      console.error(err);

      setSelectedLocation({
        ...location,
        name: "Selected Tamil Nadu Location",
      });
    } finally {
      setLocationLoading(false);
    }
  }


  // ============================================================
  // PREDICTION
  // ============================================================

  async function runPrediction() {
    if (!selectedSite) {
      setError("Tamil Nadu site is not loaded.");
      return;
    }

    try {
      setPrediction(null);
      setError("");

      const response = await fetch(
        `${API}/api/sites/${selectedSite.id}/simulate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            green_percentage: Number(greenInput),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Prediction failed."
        );
      }

      setPrediction(data);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Prediction could not be completed."
      );
    }
  }


  // ============================================================
  // ENVIRONMENT VALUES
  // ============================================================

  const greenPercentage =
    summary?.green_cover?.[0]?.green_percentage ??
    null;

  const temperature =
    summary?.climate?.[0]?.temperature ??
    null;

  const humidity =
    summary?.climate?.[0]?.humidity ??
    null;

  const uhi =
    summary?.climate?.[0]?.uhi_index ??
    null;

  const carbon =
    summary?.carbon?.[0]?.carbon_intensity ??
    null;


  // ============================================================
  // CATEGORY INFORMATION
  // ============================================================

  const categoryInfo = {
    green: {
      title: "Green Cover",
      value:
        greenPercentage !== null
          ? `${Number(greenPercentage).toFixed(2)}%`
          : "—",
      description:
        "Vegetation coverage derived from NDVI analysis.",
      legend: [
        ["Low vegetation", "#2563eb"],
        ["Moderate vegetation", "#22c55e"],
        ["High vegetation", "#facc15"],
        ["Very high vegetation", "#ef4444"],
      ],
    },

    heat: {
      title: "Surface Temperature",
      value:
        temperature !== null
          ? `${Number(temperature).toFixed(2)}°C`
          : "—",
      description:
        "Mean surface temperature across the study region.",
      legend: [
        ["Cool", "#2563eb"],
        ["Moderate", "#22c55e"],
        ["Warm", "#facc15"],
        ["Hot", "#ef4444"],
      ],
    },

    uhi: {
      title: "Urban Heat Island",
      value:
        uhi !== null
          ? `${Number(uhi).toFixed(2)}°C`
          : "—",
      description:
        "Surface urban heat island intensity.",
      legend: [
        ["Low UHI", "#2563eb"],
        ["Moderate UHI", "#22c55e"],
        ["High UHI", "#facc15"],
        ["Very high UHI", "#ef4444"],
      ],
    },

    humidity: {
      title: "Humidity",
      value:
        humidity !== null
          ? `${Number(humidity).toFixed(2)}%`
          : "—",
      description:
        "Mean relative humidity across the study region.",
      legend: [
        ["Low", "#facc15"],
        ["Moderate", "#22c55e"],
        ["High", "#06b6d4"],
        ["Very high", "#2563eb"],
      ],
    },

    carbon: {
      title: "Carbon Intensity",
      value:
        carbon !== null
          ? Number(carbon).toFixed(2)
          : "—",
      description:
        "Estimated carbon intensity of the study region.",
      legend: [
        ["Low emissions", "#22c55e"],
        ["Moderate", "#facc15"],
        ["High", "#f97316"],
        ["Very high", "#dc2626"],
      ],
    },
  };


  const info = categoryInfo[category];


  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="app">

      {/* NAVBAR */}

      <header className="navbar">
        <div className="logo">
          UrbanSiteVA
        </div>

        <div className="backend-status">
          <span className="status-dot"></span>
          Backend Online
        </div>
      </header>


      {/* HERO */}

      <section className="hero">

        <div>
          <p className="eyebrow">
            URBAN PLANNING INTELLIGENCE
          </p>

          <h1>
            Smart Site
            <br />
            Analysis
          </h1>

          <p className="hero-description">
            Explore environmental conditions across
            Tamil Nadu, select a location, and evaluate
            its urban suitability.
          </p>

          <button
            className="explore-btn"
            onClick={() =>
              document
                .getElementById("analysis")
                ?.scrollIntoView({
                  behavior: "smooth",
                })
            }
          >
            Explore Analysis ↓
          </button>
        </div>


        <div className="hero-card">

          <div className="hero-card-label">
            ANALYSIS REGION
          </div>

          <div className="hero-card-title">
            Tamil Nadu
          </div>

          <div className="hero-card-text">
            Tamil Nadu, India
          </div>

        </div>

      </section>


      <main id="analysis">

        {/* LOADING */}

        {loading && (
          <div className="loading">
            Loading Tamil Nadu environmental analysis...
          </div>
        )}


        {/* ERROR */}

        {error && (
          <div className="error">
            ⚠️ {error}
          </div>
        )}


        {!loading && (
          <>

            {/* ================================================= */}
            {/* ENVIRONMENTAL MAP */}
            {/* ================================================= */}

            <section className="section">

              <div className="section-header">

                <div>

                  <p className="eyebrow">
                    ANALYSIS REGION
                  </p>

                  <h2>
                    Tamil Nadu
                  </h2>

                  <p className="muted">
                    Explore environmental conditions
                    across the Tamil Nadu study region.
                  </p>

                </div>

                <div className="site-badge">
                  {processing
                    ? "Processing..."
                    : "Data Ready"}
                </div>

              </div>


              {/* CATEGORY BUTTONS */}

              <div className="category-buttons">

                {Object.entries(categoryInfo).map(
                  ([key, item]) => (

                    <button
                      key={key}
                      className={
                        category === key
                          ? "category active"
                          : "category"
                      }
                      onClick={() =>
                        setCategory(key)
                      }
                    >
                      {item.title}
                    </button>

                  )
                )}

              </div>


              <div className="map-layout">

                {/* MAP */}

                <div className="map-wrapper">

                  <MapContainer
                    center={tamilNaduCenter}
                    zoom={7}
                    minZoom={6}
                    maxZoom={12}
                    scrollWheelZoom={true}
                    className="map"
                  >

                    <TileLayer
                      attribution="&copy; OpenStreetMap contributors"
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />


                    <TamilNaduView />


                    {/* HEATMAP */}

                    <Heatmap
                      category={category}
                    />


                    {/* LOCATION CLICK */}

                    <MapClickHandler
                      onSelect={handleMapSelect}
                    />


                    {/* SELECTED LOCATION */}

                    {selectedLocation && (
                      <Marker
                        position={[
                          selectedLocation.latitude,
                          selectedLocation.longitude,
                        ]}
                        icon={markerIcon}
                      >
                        <Popup>

                          <div className="popup-content">

                            <strong>
                              {selectedLocation.name}
                            </strong>

                            <hr />

                            <span>
                              Latitude
                            </span>

                            <b>
                              {selectedLocation.latitude.toFixed(
                                6
                              )}
                            </b>

                            <span>
                              Longitude
                            </span>

                            <b>
                              {selectedLocation.longitude.toFixed(
                                6
                              )}
                            </b>

                          </div>

                        </Popup>
                      </Marker>
                    )}

                  </MapContainer>


                  {/* MAP TITLE */}

                  <div className="map-overlay-title">

                    <span>
                      {info.title}
                    </span>

                    <strong>
                      {info.value}
                    </strong>

                  </div>


                  {/* INSTRUCTION */}

                  <div className="map-instruction">

                    {locationLoading
                      ? "Finding location..."
                      : "Click anywhere inside Tamil Nadu to select a potential development location."}

                  </div>


                  {/* MAP LABEL */}

                  <div className="map-scale-label">
                    TAMIL NADU · ENVIRONMENTAL MAP
                  </div>

                </div>


                {/* LAYER PANEL */}

                <div className="layer-panel">

                  <p className="eyebrow">
                    SELECTED LAYER
                  </p>

                  <h3>
                    {info.title}
                  </h3>

                  <div className="large-value">
                    {info.value}
                  </div>

                  <p className="muted">
                    {info.description}
                  </p>


                  {/* CLEAR LEGEND */}

                  <div className="legend">

                    {info.legend.map(
                      ([text, color]) => (

                        <div
                          className="legend-item"
                          key={text}
                        >

                          <span
                            className="legend-dot"
                            style={{
                              backgroundColor:
                                color,
                            }}
                          />

                          {text}

                        </div>

                      )
                    )}

                  </div>


                  <div className="layer-note">

                    <strong>
                      2025 environmental data
                    </strong>

                    <p>
                      The map visualizes spatial
                      environmental indicators
                      used for urban site suitability
                      assessment.
                    </p>

                  </div>

                </div>

              </div>

            </section>


            {/* ================================================= */}
            {/* LOCATION SELECTION */}
            {/* ================================================= */}

            <section className="section">

              <div className="section-header">

                <div>

                  <p className="eyebrow">
                    SITE SELECTION
                  </p>

                  <h2>
                    Choose a Location
                  </h2>

                  <p className="muted">
                    Select a point inside Tamil Nadu
                    to identify a potential development
                    location.
                  </p>

                </div>

              </div>


              <div className="selection-card">

                <div className="coordinates-card">

                  <div>
                    <span>
                      LOCATION
                    </span>

                    <strong>
                      {selectedLocation
                        ? selectedLocation.name
                        : "Select on map"}
                    </strong>
                  </div>


                  <div>
                    <span>
                      LATITUDE
                    </span>

                    <strong>
                      {selectedLocation
                        ? selectedLocation.latitude.toFixed(
                            6
                          )
                        : "—"}
                    </strong>
                  </div>


                  <div>
                    <span>
                      LONGITUDE
                    </span>

                    <strong>
                      {selectedLocation
                        ? selectedLocation.longitude.toFixed(
                            6
                          )
                        : "—"}
                    </strong>
                  </div>

                </div>


                <div className="selection-message">

                  {selectedLocation ? (
                    <>
                      <strong>
                        ✓ Location selected
                      </strong>

                      <p>
                        {selectedLocation.name}
                      </p>

                      <small>
                        {selectedLocation.latitude.toFixed(
                          6
                        )}
                        {" · "}
                        {selectedLocation.longitude.toFixed(
                          6
                        )}
                      </small>
                    </>
                  ) : (
                    <>
                      <strong>
                        No location selected
                      </strong>

                      <p>
                        Click a location on the
                        Tamil Nadu map above.
                      </p>
                    </>
                  )}

                </div>

              </div>

            </section>


            {/* ================================================= */}
            {/* SITE SCORE */}
            {/* ================================================= */}

            <section className="section">

              <div className="section-header">

                <div>

                  <p className="eyebrow">
                    SUITABILITY ANALYSIS
                  </p>

                  <h2>
                    Site Score
                  </h2>

                </div>


                {score && (
                  <div className="score-badge">
                    {score.rating}
                  </div>
                )}

              </div>


              <div className="score-grid">

                <div className="score-main">

                  <span>
                    OVERALL SUITABILITY
                  </span>

                  <div className="score-number">
                    {score
                      ? score.score
                      : "—"}
                  </div>

                  <p>
                    {score
                      ? "Calculated using environmental indicators."
                      : "Processing site data..."}
                  </p>

                </div>


                <div className="indicator">

                  <span>
                    GREEN COVER
                  </span>

                  <strong>
                    {greenPercentage !== null
                      ? `${Number(
                          greenPercentage
                        ).toFixed(2)}%`
                      : "—"}
                  </strong>

                  <div className="progress">

                    <div
                      style={{
                        width:
                          greenPercentage !== null
                            ? `${Math.min(
                                Number(
                                  greenPercentage
                                ),
                                100
                              )}%`
                            : "0%",
                      }}
                    />

                  </div>

                </div>


                <div className="indicator">

                  <span>
                    SURFACE TEMPERATURE
                  </span>

                  <strong>
                    {temperature !== null
                      ? `${Number(
                          temperature
                        ).toFixed(2)}°C`
                      : "—"}
                  </strong>

                  <div className="indicator-text">
                    Mean surface temperature
                  </div>

                </div>


                <div className="indicator">

                  <span>
                    UHI INTENSITY
                  </span>

                  <strong>
                    {uhi !== null
                      ? `${Number(
                          uhi
                        ).toFixed(2)}°C`
                      : "—"}
                  </strong>

                  <div className="indicator-text">
                    Surface urban heat island intensity
                  </div>

                </div>

              </div>


              {/* RECOMMENDATIONS */}

              {score?.recommendations?.length > 0 && (

                <div className="recommendations">

                  <p className="eyebrow">
                    RECOMMENDATIONS
                  </p>

                  {score.recommendations.map(
                    (recommendation, index) => (

                      <div
                        className="recommendation"
                        key={index}
                      >

                        <span>
                          →
                        </span>

                        <p>
                          {recommendation}
                        </p>

                      </div>

                    )
                  )}

                </div>

              )}

            </section>


            {/* ================================================= */}
            {/* PREDICTION */}
            {/* ================================================= */}

            <section className="section">

              <div className="section-header">

                <div>

                  <p className="eyebrow">
                    PREDICTION ANALYSIS
                  </p>

                  <h2>
                    What If Green Cover Changes?
                  </h2>

                  <p className="muted">
                    Modify proposed green cover and
                    predict the resulting site performance.
                  </p>

                </div>

              </div>


              <div className="prediction-card">

                <div className="prediction-input">

                  <label>
                    Proposed Green Cover
                  </label>

                  <div className="slider-value">
                    {greenInput}%
                  </div>

                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={greenInput}
                    onChange={(e) =>
                      setGreenInput(
                        Number(e.target.value)
                      )
                    }
                  />

                  <div className="slider-labels">
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                  </div>


                  <button
                    className="predict-btn"
                    onClick={runPrediction}
                    disabled={!score}
                  >
                    {prediction
                      ? "Run Again"
                      : "Run Prediction"}
                  </button>

                </div>


                {/* PREDICTION RESULT */}

                {prediction && (

                  <div className="prediction-result">

                    <div>

                      <span>
                        CURRENT SCORE
                      </span>

                      <strong>
                        {prediction.current_score}
                      </strong>

                    </div>


                    <div>

                      <span>
                        PREDICTED SCORE
                      </span>

                      <strong>
                        {prediction.predicted_score}
                      </strong>

                    </div>


                    <div>

                      <span>
                        PREDICTED RATING
                      </span>

                      <strong>
                        {prediction.predicted_rating}
                      </strong>

                    </div>


                    <div>

                      <span>
                        PREDICTED UHI
                      </span>

                      <strong>
                        {Number(
                          prediction.predicted_uhi
                        ).toFixed(2)}
                        °C
                      </strong>

                    </div>

                  </div>

                )}

              </div>

            </section>

          </>
        )}

      </main>


      <footer>
        UrbanSiteVA · Tamil Nadu Environmental Intelligence
      </footer>

    </div>
  );
}

export default App;