import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  Circle,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

const API = "http://127.0.0.1:5000";

const velacheryBoundary = [
  [12.9882925, 80.2043675],
  [12.9827493, 80.2121543],
  [12.9752934, 80.2129267],
  [12.9694416, 80.213025],
  [12.9674017, 80.2159475],
  [12.9669812, 80.2169979],
  [12.9666744, 80.2177643],
  [12.9662223, 80.2200953],
  [12.9659723, 80.2213847],
  [12.9697391, 80.2256024],
  [12.9739385, 80.2298234],
  [12.977045, 80.2330997],
  [12.9775816, 80.2331133],
  [12.9828771, 80.2334532],
  [12.9834699, 80.2316179],
  [12.9844833, 80.231866],
  [12.9868039, 80.2321656],
  [12.9871525, 80.2294122],
  [12.9875019, 80.2231944],
  [12.9879504, 80.2232194],
  [12.9888375, 80.2232689],
  [12.9904235, 80.2230572],
  [12.9921722, 80.22264],
  [12.9936711, 80.2229825],
  [12.994212, 80.2215117],
  [12.9914316, 80.2203112],
  [12.9934106, 80.2187285],
  [12.9954762, 80.2173514],
  [12.9939944, 80.2146524],
  [12.9882925, 80.2043675],
];

const center = [12.9801655, 80.2228506];

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

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

  useEffect(() => {
    loadSites();
  }, []);

  async function loadSites() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API}/api/sites`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      const data = await response.json();

      setSites(data);

      if (data.length > 0) {
        setSelectedSite(data[0]);

        await processSite(data[0].id);
      }
    } catch (err) {
      console.error(err);
      setError(
        "Could not connect to the UrbanSiteVA backend. Make sure Flask is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  }

  async function processSite(siteId) {
    try {
      setProcessing(true);

      await fetch(`${API}/api/sites/${siteId}/process-data`, {
        method: "POST",
      });

      const summaryResponse = await fetch(
        `${API}/api/sites/${siteId}/summary`
      );

      const summaryData = await summaryResponse.json();
      setSummary(summaryData);

      const scoreResponse = await fetch(
        `${API}/api/sites/${siteId}/score`
      );

      const scoreData = await scoreResponse.json();

      if (scoreResponse.ok) {
        setScore(scoreData);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to load site analysis.");
    } finally {
      setProcessing(false);
    }
  }

  async function runPrediction() {
    if (!selectedSite) return;

    try {
      setPrediction(null);

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
        throw new Error(data.error || "Prediction failed");
      }

      setPrediction(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  }

  function handleMapSelect(location) {
    setSelectedLocation(location);
    setPrediction(null);
  }

  const greenPercentage =
    summary?.green_cover?.[0]?.green_percentage ?? 29.37;

  const temperature =
    summary?.climate?.[0]?.temperature ?? 35.58;

  const humidity =
    summary?.climate?.[0]?.humidity ?? 72.06;

  const uhi =
    summary?.climate?.[0]?.uhi_index ?? 2.94;

  const carbon =
    summary?.carbon?.[0]?.carbon_intensity ?? 74.23;

  const categoryInfo = {
    green: {
      title: "Green Cover",
      value: `${greenPercentage.toFixed(2)}%`,
      description: "Vegetation coverage based on NDVI analysis",
      legend: ["Low vegetation", "Medium vegetation", "High vegetation"],
    },
    heat: {
      title: "Surface Temperature",
      value: `${temperature.toFixed(2)}°C`,
      description: "Mean surface temperature",
      legend: ["Cool", "Moderate", "Hot"],
    },
    uhi: {
      title: "Urban Heat Island",
      value: `${uhi.toFixed(2)}°C`,
      description: "Surface UHI intensity",
      legend: ["Low UHI", "Moderate UHI", "High UHI"],
    },
    humidity: {
      title: "Humidity",
      value: `${humidity.toFixed(2)}%`,
      description: "Mean relative humidity",
      legend: ["Low", "Moderate", "High"],
    },
    carbon: {
      title: "Carbon Intensity",
      value: `${carbon.toFixed(2)}`,
      description: "Estimated carbon intensity",
      legend: ["Low emissions", "Moderate emissions", "High emissions"],
    },
  };

  const info = categoryInfo[category];

  function getCircleData() {
    if (category === "green") {
      return [
        [12.978, 80.214, 600, "low"],
        [12.982, 80.220, 700, "medium"],
        [12.977, 80.228, 650, "high"],
        [12.987, 80.224, 600, "medium"],
        [12.971, 80.222, 650, "low"],
        [12.984, 80.231, 500, "high"],
      ];
    }

    if (category === "heat") {
      return [
        [12.978, 80.214, 650, "hot"],
        [12.982, 80.220, 700, "moderate"],
        [12.977, 80.228, 650, "hot"],
        [12.987, 80.224, 600, "moderate"],
        [12.971, 80.222, 650, "hot"],
        [12.984, 80.231, 500, "cool"],
      ];
    }

    if (category === "uhi") {
      return [
        [12.978, 80.214, 650, "high"],
        [12.982, 80.220, 700, "moderate"],
        [12.977, 80.228, 650, "high"],
        [12.987, 80.224, 600, "moderate"],
        [12.971, 80.222, 650, "high"],
        [12.984, 80.231, 500, "low"],
      ];
    }

    if (category === "humidity") {
      return [
        [12.978, 80.214, 650, "medium"],
        [12.982, 80.220, 700, "high"],
        [12.977, 80.228, 650, "high"],
        [12.987, 80.224, 600, "medium"],
        [12.971, 80.222, 650, "low"],
        [12.984, 80.231, 500, "high"],
      ];
    }

    return [
      [12.978, 80.214, 650, "high"],
      [12.982, 80.220, 700, "medium"],
      [12.977, 80.228, 650, "high"],
      [12.987, 80.224, 600, "medium"],
      [12.971, 80.222, 650, "high"],
      [12.984, 80.231, 500, "low"],
    ];
  }

  function getHeatClass(level) {
    if (level === "low" || level === "cool") {
      return "heat-low";
    }

    if (level === "medium" || level === "moderate") {
      return "heat-medium";
    }

    return "heat-high";
  }

  return (
    <div className="app">

      <header className="navbar">
        <div className="logo">UrbanSiteVA</div>

        <div className="backend-status">
          <span></span>
          Backend Online
        </div>
      </header>

      <section className="hero">
        <div>
          <p className="eyebrow">URBAN PLANNING INTELLIGENCE</p>

          <h1>
            Smart Site
            <br />
            Analysis
          </h1>

          <p className="hero-description">
            Explore environmental conditions across Velachery,
            select a location, and evaluate its urban suitability.
          </p>

          <button
            className="explore-btn"
            onClick={() =>
              document
                .getElementById("analysis")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            Explore Analysis ↓
          </button>
        </div>

        <div className="hero-card">
          <div className="hero-card-label">ANALYSIS AREA</div>
          <div className="hero-card-title">Velachery</div>
          <div className="hero-card-text">
            Chennai, Tamil Nadu
          </div>
        </div>
      </section>

      <main id="analysis">

        {loading && (
          <div className="loading">
            Loading Velachery analysis...
          </div>
        )}

        {error && (
          <div className="error">
            ⚠️ {error}
          </div>
        )}

        {!loading && selectedSite && (
          <>
            <section className="section">

              <div className="section-header">
                <div>
                  <p className="eyebrow">ANALYSIS AREA</p>
                  <h2>Velachery</h2>
                  <p className="muted">
                    Select an environmental layer to explore
                    conditions across the area.
                  </p>
                </div>

                <div className="site-badge">
                  {processing ? "Updating..." : "Data Ready"}
                </div>
              </div>

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
                      onClick={() => setCategory(key)}
                    >
                      {item.title}
                    </button>
                  )
                )}

              </div>

              <div className="map-layout">

                <div className="map-wrapper">

                  <MapContainer
                    center={center}
                    zoom={14}
                    scrollWheelZoom={true}
                    className="map"
                  >

                    <TileLayer
                      attribution='&copy; OpenStreetMap contributors'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    <Polygon
                      positions={velacheryBoundary}
                      pathOptions={{
                        color: "#111",
                        weight: 2,
                        fillOpacity: 0.05,
                      }}
                    />

                    {getCircleData().map(
                      ([lat, lon, radius, level], index) => (
                        <Circle
                          key={index}
                          center={[lat, lon]}
                          radius={radius}
                          className={getHeatClass(level)}
                          pathOptions={{
                            className: getHeatClass(level),
                            stroke: false,
                            fillOpacity: 0.35,
                          }}
                        />
                      )
                    )}

                    <MapClickHandler
                      onSelect={handleMapSelect}
                    />

                    {selectedLocation && (
                      <Marker
                        position={[
                          selectedLocation.latitude,
                          selectedLocation.longitude,
                        ]}
                        icon={markerIcon}
                      >
                        <Popup>
                          <strong>Selected Location</strong>
                          <br />
                          Lat:{" "}
                          {selectedLocation.latitude.toFixed(
                            6
                          )}
                          <br />
                          Lon:{" "}
                          {selectedLocation.longitude.toFixed(
                            6
                          )}
                        </Popup>
                      </Marker>
                    )}

                    <Marker
                      position={center}
                      icon={markerIcon}
                    >
                      <Popup>
                        <strong>Velachery</strong>
                        <br />
                        Analysis Area
                      </Popup>
                    </Marker>

                  </MapContainer>

                  <div className="map-overlay-title">
                    <span>{info.title}</span>
                    <strong>{info.value}</strong>
                  </div>

                  <div className="map-instruction">
                    Click anywhere inside the map to select a
                    location
                  </div>

                </div>

                <div className="layer-panel">

                  <p className="eyebrow">SELECTED LAYER</p>

                  <h3>{info.title}</h3>

                  <div className="large-value">
                    {info.value}
                  </div>

                  <p className="muted">
                    {info.description}
                  </p>

                  <div className="legend">

                    {info.legend.map((text, index) => (
                      <div
                        className="legend-item"
                        key={text}
                      >
                        <span
                          className={`legend-dot ${
                            index === 0
                              ? "dot-low"
                              : index === 1
                              ? "dot-medium"
                              : "dot-high"
                          }`}
                        ></span>

                        {text}
                      </div>
                    ))}

                  </div>

                  <div className="layer-note">
                    <strong>2025 environmental data</strong>
                    <p>
                      The visualization represents the
                      processed environmental characteristics
                      of the Velachery study area.
                    </p>
                  </div>

                </div>

              </div>

            </section>

            <section className="section">

              <div className="section-header">
                <div>
                  <p className="eyebrow">SITE SELECTION</p>
                  <h2>Choose a Location</h2>
                  <p className="muted">
                    Click the map to select a potential
                    development location.
                  </p>
                </div>
              </div>

              <div className="selection-card">

                <div className="coordinates-card">

                  <div>
                    <span>LATITUDE</span>

                    <strong>
                      {selectedLocation
                        ? selectedLocation.latitude.toFixed(
                            6
                          )
                        : "Select on map"}
                    </strong>
                  </div>

                  <div>
                    <span>LONGITUDE</span>

                    <strong>
                      {selectedLocation
                        ? selectedLocation.longitude.toFixed(
                            6
                          )
                        : "Select on map"}
                    </strong>
                  </div>

                </div>

                <div className="selection-message">

                  {selectedLocation ? (
                    <>
                      <strong>Location selected</strong>
                      <p>
                        This point can now be evaluated
                        against the environmental indicators.
                      </p>
                    </>
                  ) : (
                    <>
                      <strong>No location selected</strong>
                      <p>
                        Select a point on the Velachery map
                        above.
                      </p>
                    </>
                  )}

                </div>

              </div>

            </section>

            <section className="section">

              <div className="section-header">
                <div>
                  <p className="eyebrow">SUITABILITY ANALYSIS</p>
                  <h2>Site Score</h2>
                </div>

                {score && (
                  <div className="score-badge">
                    {score.rating}
                  </div>
                )}
              </div>

              <div className="score-grid">

                <div className="score-main">

                  <span>OVERALL SUITABILITY</span>

                  <div className="score-number">
                    {score?.score ?? "—"}
                  </div>

                  <p>
                    {score
                      ? "Calculated using the processed environmental indicators."
                      : "Processing site data..."}
                  </p>

                </div>

                <div className="indicator">

                  <span>GREEN COVER</span>

                  <strong>
                    {greenPercentage.toFixed(2)}%
                  </strong>

                  <div className="progress">
                    <div
                      style={{
                        width: `${Math.min(
                          greenPercentage,
                          100
                        )}%`,
                      }}
                    ></div>
                  </div>

                </div>

                <div className="indicator">

                  <span>SURFACE TEMPERATURE</span>

                  <strong>
                    {temperature.toFixed(2)}°C
                  </strong>

                  <div className="indicator-text">
                    Mean surface temperature
                  </div>

                </div>

                <div className="indicator">

                  <span>UHI INTENSITY</span>

                  <strong>
                    {uhi.toFixed(2)}°C
                  </strong>

                  <div className="indicator-text">
                    Surface urban heat island intensity
                  </div>

                </div>

              </div>

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
                        <span>→</span>
                        <p>{recommendation}</p>
                      </div>
                    )
                  )}

                </div>
              )}

            </section>

            <section className="section">

              <div className="section-header">
                <div>
                  <p className="eyebrow">
                    PREDICTION ANALYSIS
                  </p>

                  <h2>What If Green Cover Changes?</h2>

                  <p className="muted">
                    Increase or decrease the proposed green
                    cover and predict the resulting site
                    performance.
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
                      setGreenInput(e.target.value)
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
                  >
                    Run Prediction
                  </button>

                </div>

                {prediction && (
                  <div className="prediction-result">

                    <div>
                      <span>CURRENT SCORE</span>
                      <strong>
                        {prediction.current_score}
                      </strong>
                    </div>

                    <div>
                      <span>PREDICTED SCORE</span>
                      <strong>
                        {prediction.predicted_score}
                      </strong>
                    </div>

                    <div>
                      <span>PREDICTED RATING</span>
                      <strong>
                        {prediction.predicted_rating}
                      </strong>
                    </div>

                    <div>
                      <span>PREDICTED UHI</span>
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
        UrbanSiteVA
      </footer>

    </div>
  );
}

export default App;