import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [sites, setSites] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/sites")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend connection failed");
        }
        return response.json();
      })
      .then((data) => {
        setSites(data);

        if (data.length > 0) {
          setSelectedSite(data[0]);
        }

        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Could not connect to the UrbanSiteVA backend.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">

      <nav className="navbar">
        <div className="logo">
          🏙️ UrbanSiteVA
        </div>

        <div className="nav-links">
          <span className="active">Dashboard</span>
          <span>Site Analysis</span>
          <span>Recommendations</span>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Backend Online
        </div>
      </nav>

      <section className="hero">
        <div>
          <p className="tag">URBAN PLANNING INTELLIGENCE</p>

          <h1>
            Smart Site Analysis
            <br />
            <span>& Recommendation</span>
          </h1>

          <p className="hero-text">
            Analyze potential urban sites and identify suitable
            locations using data-driven spatial analysis.
          </p>

          <button className="primary-btn">
            Explore Sites ↓
          </button>
        </div>

        <div className="hero-visual">
          <div className="map-circle">
            <div className="map-pin">📍</div>
            <div className="map-line line1"></div>
            <div className="map-line line2"></div>
            <div className="map-line line3"></div>
          </div>
        </div>
      </section>

      <main className="main">

        <div className="section-heading">
          <div>
            <p className="tag">ANALYSIS OVERVIEW</p>
            <h2>Candidate Sites</h2>
          </div>

          <div className="site-count">
            {sites.length} Sites Found
          </div>
        </div>

        {loading ? (
          <div className="message">
            Loading site analysis...
          </div>
        ) : error ? (
          <div className="error-box">
            ⚠️ {error}
            <br />
            Make sure Flask is running on port 5000.
          </div>
        ) : (
          <>
            <div className="content-grid">

              <div className="site-list">

                {sites.map((site, index) => (
                  <div
                    className={
                      selectedSite === site
                        ? "site-card selected"
                        : "site-card"
                    }
                    key={index}
                    onClick={() => setSelectedSite(site)}
                  >
                    <div className="site-number">
                      {String(index + 1).padStart(2, "0")}
                    </div>

                    <div className="site-info">
                      <h3>
                        Candidate Site {index + 1}
                      </h3>

                      <p>
                        Area:{" "}
                        <strong>
                          {site.area ?? "N/A"} m²
                        </strong>
                      </p>

                      {site.latitude !== undefined &&
                        site.longitude !== undefined && (
                          <p className="coordinates">
                            📍 {site.latitude},{" "}
                            {site.longitude}
                          </p>
                        )}
                    </div>

                    <div className="arrow">
                      →
                    </div>
                  </div>
                ))}

                {sites.length === 0 && (
                  <div className="message">
                    No candidate sites available.
                  </div>
                )}

              </div>

            </div>

            {selectedSite && (
              <section className="analysis-panel">

                <div className="panel-header">

                  <div>
                    <p className="tag">
                      SELECTED LOCATION
                    </p>

                    <h2>
                      Site Analysis
                    </h2>
                  </div>

                  <div className="recommended">
                    ★ Recommended Candidate
                  </div>

                </div>

                <div className="stats">

                  <div className="stat">
                    <span>AREA</span>
                    <strong>
                      {selectedSite.area ?? "N/A"}
                    </strong>
                    <small>square metres</small>
                  </div>

                  <div className="stat">
                    <span>LATITUDE</span>
                    <strong>
                      {selectedSite.latitude ?? "N/A"}
                    </strong>
                    <small>location coordinate</small>
                  </div>

                  <div className="stat">
                    <span>LONGITUDE</span>
                    <strong>
                      {selectedSite.longitude ?? "N/A"}
                    </strong>
                    <small>location coordinate</small>
                  </div>

                  <div className="stat score">
                    <span>SITE SCORE</span>
                    <strong>
                      {selectedSite.score ?? "—"}
                    </strong>
                    <small>overall suitability</small>
                  </div>

                </div>

                <div className="map-section">

                  <div className="map-placeholder">

                    <div className="map-grid"></div>

                    <div className="map-marker">
                      📍
                    </div>

                    <div className="map-label">
                      Selected Site
                    </div>

                  </div>

                  <div className="location-details">

                    <p className="tag">
                      LOCATION
                    </p>

                    <h3>
                      Candidate Site
                    </h3>

                    <p>
                      This location has been identified as a
                      potential urban development site based
                      on the available spatial data.
                    </p>

                    <div className="coordinate-box">

                      <div>
                        <span>LAT</span>
                        <strong>
                          {selectedSite.latitude ?? "N/A"}
                        </strong>
                      </div>

                      <div>
                        <span>LON</span>
                        <strong>
                          {selectedSite.longitude ?? "N/A"}
                        </strong>
                      </div>

                    </div>

                  </div>

                </div>

              </section>
            )}

          </>
        )}

      </main>

      <footer>
        <span>UrbanSiteVA</span>
        <span>
          Urban Site Analysis & Recommendation System
        </span>
        <span>VIT • 2026</span>
      </footer>

    </div>
  );
}

export default App;