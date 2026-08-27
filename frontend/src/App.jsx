import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");

  const [location, setLocation] = useState(null);
  const [locationStatus, setLocationStatus] = useState("");

  const [loading, setLoading] = useState(false);

  // ============================================================
  // FILE UPLOAD
  // ============================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setPreview(
      URL.createObjectURL(selectedFile)
    );
  };

  // ============================================================
  // LOCATION
  // ============================================================

  const getLocation = () => {
    if (!navigator.geolocation) {
      setLocationStatus(
        "Location services are not supported by this browser."
      );

      return;
    }

    setLocationStatus(
      "Getting your location..."
    );

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });

        setLocationStatus(
          "Location detected successfully."
        );
      },

      () => {
        setLocationStatus(
          "Unable to access your location."
        );
      },

      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  // ============================================================
  // ANALYSIS
  // ============================================================

  const handleAnalyze = async () => {
    if (!file) {
      alert(
        "Please upload an MRI or CT brain scan."
      );

      return;
    }

    if (!age) {
      alert(
        "Please enter your age."
      );

      return;
    }

    if (!gender) {
      alert(
        "Please select your gender."
      );

      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append(
        "file",
        file
      );

      formData.append(
        "age",
        age
      );

      // IMPORTANT:
      // Backend still expects sex_category.
      formData.append(
        "sex_category",
        gender
      );

      if (location) {
        formData.append(
          "latitude",
          location.latitude
        );

        formData.append(
          "longitude",
          location.longitude
        );
      }

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/analysis/full",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Analysis failed."
        );
      }

      console.log(
        "MEDFUSION ANALYSIS RESULT:",
        data
      );

      alert(
        "Analysis completed successfully.\n\nOpen the browser console to view the result."
      );

    } catch (error) {

      console.error(
        "Analysis error:",
        error
      );

      alert(
        error.message ||
        "Something went wrong during analysis."
      );

    } finally {

      setLoading(false);

    }
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="app">

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <nav className="navbar">

        <div className="navbar-inner">

          <div className="logo">

            <div className="logo-icon">
              <span>✚</span>
            </div>

            <div className="logo-text">
              <strong>
                MedFusion
              </strong>

              <span>
                AI
              </span>
            </div>

          </div>

          <div className="nav-status">

            <span className="status-dot"></span>

            AI System Online

          </div>

        </div>

      </nav>

      {/* ======================================================
          HERO
      ====================================================== */}

      <main>

        <section className="hero">

          <div className="hero-content">

            <div className="hero-badge">
              <span>✦</span>
              AI-ASSISTED BRAIN SCAN ANALYSIS
            </div>

            <h1>
              Understand your
              <span> brain scan </span>
              with AI.
            </h1>

            <p>
              MedFusion AI analyzes MRI and CT brain
              scans through a multi-stage machine
              learning pipeline to provide an
              educational analysis.
            </p>

          </div>

        </section>

        {/* ====================================================
            ANALYSIS CARD
        ==================================================== */}

        <section className="analysis-wrapper">

          <div className="analysis-card">

            {/* CARD HEADER */}

            <div className="card-header">

              <div>

                <div className="section-number">
                  STEP 01
                </div>

                <h2>
                  Upload your scan
                </h2>

                <p>
                  Select an MRI or CT brain scan
                  to begin the analysis.
                </p>

              </div>

              <div className="brain-symbol">
                🧠
              </div>

            </div>

            {/* =================================================
                UPLOAD AREA
            ================================================= */}

            <label
              className={`upload-area ${
                preview
                  ? "has-preview"
                  : ""
              }`}
            >

              {preview ? (

                <div className="preview-container">

                  <img
                    src={preview}
                    alt="Selected brain scan"
                    className="scan-preview"
                  />

                  <div className="preview-overlay">

                    <span>
                      Change image
                    </span>

                  </div>

                </div>

              ) : (

                <div className="upload-content">

                  <div className="upload-icon">
                    ↑
                  </div>

                  <h3>
                    Drop your scan here
                  </h3>

                  <p>
                    or click to browse from your device
                  </p>

                  <span className="file-types">
                    JPG · JPEG · PNG · BMP · TIF · TIFF
                  </span>

                </div>

              )}

              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.tif,.tiff"
                onChange={handleFileChange}
                hidden
              />

            </label>

            {/* =================================================
                PATIENT INFORMATION
            ================================================= */}

            <div className="patient-section">

              <div className="section-title">

                <div className="section-number">
                  STEP 02
                </div>

                <h2>
                  Patient information
                </h2>

                <p>
                  Only the basic information required
                  for the analysis is collected.
                </p>

              </div>

              <div className="form-grid">

                {/* AGE */}

                <div className="form-field">

                  <label htmlFor="age">
                    Age
                  </label>

                  <div className="input-wrapper">

                    <input
                      id="age"
                      type="number"
                      min="1"
                      max="120"
                      value={age}
                      onChange={(event) => {
                        const value =
                          event.target.value;

                        if (
                          value === "" ||
                          (
                            Number(value) >= 1 &&
                            Number(value) <= 120
                          )
                        ) {
                          setAge(value);
                        }
                      }}
                      placeholder="Enter age"
                    />

                    <span>
                      years
                    </span>

                  </div>

                </div>

                {/* GENDER */}

                <div className="form-field">

                  <label htmlFor="gender">
                    Gender
                  </label>

                  <select
                    id="gender"
                    value={gender}
                    onChange={(event) =>
                      setGender(
                        event.target.value
                      )
                    }
                  >

                    <option value="">
                      Select gender
                    </option>

                    <option value="Male">
                      Male
                    </option>

                    <option value="Female">
                      Female
                    </option>

                  </select>

                </div>

              </div>

            </div>

            {/* =================================================
                LOCATION
            ================================================= */}

            <div className="location-section">

              <div className="section-title">

                <div className="section-number">
                  STEP 03
                </div>

                <h2>
                  Your location
                </h2>

                <p>
                  Used only to find nearby hospitals
                  with relevant specialist services.
                </p>

              </div>

              <button
                type="button"
                className={`location-button ${
                  location
                    ? "location-success"
                    : ""
                }`}
                onClick={getLocation}
              >

                <span className="location-icon">
                  {location
                    ? "✓"
                    : "⌖"}
                </span>

                <span className="location-text">

                  <strong>
                    {location
                      ? "Location detected"
                      : "Use my location"}
                  </strong>

                  <small>
                    {location
                      ? "Ready for nearby hospital search"
                      : "Allow browser location access"}
                  </small>

                </span>

                <span className="location-arrow">
                  →
                </span>

              </button>

              {locationStatus && (
                <div className="location-message">
                  {locationStatus}
                </div>
              )}

            </div>

            {/* =================================================
                ANALYZE
            ================================================= */}

            <div className="analyze-section">

              <button
                type="button"
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={loading}
              >

                {loading ? (

                  <>
                    <span className="spinner"></span>

                    Running analysis...

                  </>

                ) : (

                  <>
                    Analyze Scan

                    <span className="button-arrow">
                      →
                    </span>
                  </>

                )}

              </button>

              <p className="disclaimer">

                <span>ⓘ</span>

                This is an AI-assisted college project.
                Results are for educational demonstration
                and are not a medical diagnosis.

              </p>

            </div>

          </div>

        </section>

      </main>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer>

        <p>
          MedFusion AI · Brain Scan Analysis
        </p>

        <span>
          Educational Demonstration
        </span>

      </footer>

    </div>
  );
}

export default App;