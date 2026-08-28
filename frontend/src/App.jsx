import {
  useEffect,
  useState,
} from "react";

import "./App.css";

import {
  analyzeScan,
  sendChatMessage,
} from "./services/api";


// ============================================================
// HELPERS
// ============================================================

function formatPercent(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(2)}%`;
}


function probabilityToPercent(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return null;
  }

  const numericValue = Number(value);

  if (numericValue <= 1) {
    return numericValue * 100;
  }

  return numericValue;
}


function getConfidencePercent(value) {
  return probabilityToPercent(value);
}


function formatNumber(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return Number(value).toLocaleString(
    undefined,
    {
      maximumFractionDigits: 2,
    }
  );
}


// ============================================================
// MAIN APP
// ============================================================

function App() {

  // ==========================================================
  // PAGE
  // ==========================================================

  const [page, setPage] =
    useState("home");


  // ==========================================================
  // FILE
  // ==========================================================

  const [file, setFile] =
    useState(null);

  const [preview, setPreview] =
    useState(null);


  // ==========================================================
  // PATIENT
  // ==========================================================

  const [age, setAge] =
    useState("");

  const [gender, setGender] =
    useState("");


  // ==========================================================
  // LOCATION
  // ==========================================================

  const [location, setLocation] =
    useState(null);

  const [locationStatus, setLocationStatus] =
    useState("");


  // ==========================================================
  // ANALYSIS
  // ==========================================================

  const [loading, setLoading] =
    useState(false);

  const [analysisResult, setAnalysisResult] =
    useState(null);

  const [errorMessage, setErrorMessage] =
    useState("");


  // ==========================================================
  // CHATBOT
  // ==========================================================

  const [chatOpen, setChatOpen] =
    useState(false);

  const [chatInput, setChatInput] =
    useState("");

  const [chatLoading, setChatLoading] =
    useState(false);

  const [chatMessages, setChatMessages] =
    useState([
      {
        role: "assistant",
        text:
          "Hi! I’m the MedFusion AI assistant. You can ask me about MRI, CT, brain tumors, segmentation, WHO grading, or the terms shown in your analysis.",
      },
    ]);


  // ==========================================================
  // CLEANUP PREVIEW URL
  // ==========================================================

  useEffect(() => {

    return () => {

      if (preview) {
        URL.revokeObjectURL(preview);
      }

    };

  }, [preview]);


  // ==========================================================
  // FILE CHANGE
  // ==========================================================

  const handleFileChange = (event) => {

    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) {
      return;
    }


    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/bmp",
      "image/tiff",
    ];

    const allowedExtensions =
      [
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
      ];


    const fileName =
      selectedFile.name.toLowerCase();

    const validType =
      allowedTypes.includes(
        selectedFile.type
      );

    const validExtension =
      allowedExtensions.some(
        (extension) =>
          fileName.endsWith(extension)
      );


    if (
      !validType &&
      !validExtension
    ) {

      setErrorMessage(
        "Unsupported image format. Please use JPG, JPEG, PNG, BMP, TIF, or TIFF."
      );

      return;
    }


    if (preview) {
      URL.revokeObjectURL(preview);
    }


    setFile(selectedFile);

    setPreview(
      URL.createObjectURL(
        selectedFile
      )
    );

    setAnalysisResult(null);

    setErrorMessage("");
  };


  // ==========================================================
  // LOCATION
  // ==========================================================

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

        const detectedLocation = {
          latitude:
            position.coords.latitude,

          longitude:
            position.coords.longitude,
        };


        setLocation(
          detectedLocation
        );

        setLocationStatus(
          "Location detected successfully."
        );
      },


      () => {

        setLocationStatus(
          "Unable to access your location. You can continue without it."
        );
      },


      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }

    );
  };


  // ==========================================================
  // ANALYZE
  // ==========================================================

  const handleAnalyze = async () => {

    setErrorMessage("");


    if (!file) {

      setErrorMessage(
        "Please upload an MRI or CT brain scan."
      );

      return;
    }


    if (!age) {

      setErrorMessage(
        "Please enter your age."
      );

      return;
    }


    if (!gender) {

      setErrorMessage(
        "Please select your gender."
      );

      return;
    }


    setLoading(true);


    try {

      const data =
        await analyzeScan({
          file,
          age,
          gender,
          location,
        });


      console.log(
        "MEDFUSION ANALYSIS RESULT:",
        data
      );


      setAnalysisResult(data);

      // ------------------------------------------------------
      // Move to results page only after successful response.
      // ------------------------------------------------------

      setPage("results");

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

    } catch (error) {

      console.error(
        "Analysis error:",
        error
      );

      setErrorMessage(
        error.message ||
        "Something went wrong during analysis."
      );

    } finally {

      setLoading(false);
    }
  };


  // ==========================================================
  // HOME
  // ==========================================================

  const handleHome = () => {

    setPage("home");

    setChatOpen(false);

    setErrorMessage("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };


  // ==========================================================
  // CHATBOT
  // ==========================================================

  const handleChatSubmit =
    async (event) => {

      event.preventDefault();


      const message =
        chatInput.trim();


      if (!message || chatLoading) {
        return;
      }


      setChatInput("");


      setChatMessages(
        (previous) => [
          ...previous,

          {
            role: "user",
            text: message,
          },
        ]
      );


      setChatLoading(true);


      try {

        const data =
          await sendChatMessage(
            message
          );


        const responseText =
          data?.response ||
          "I could not generate a response.";


        setChatMessages(
          (previous) => [
            ...previous,

            {
              role: "assistant",
              text: responseText,
            },
          ]
        );

      } catch (error) {

        console.error(
          "Chatbot error:",
          error
        );


        setChatMessages(
          (previous) => [
            ...previous,

            {
              role: "assistant",
              text:
                error.message ||
                "The chatbot could not respond right now.",
              error: true,
            },
          ]
        );

      } finally {

        setChatLoading(false);
      }
    };


  // ==========================================================
  // SAFE PIPELINE DATA
  // ==========================================================

  const pipeline =
    analysisResult?.pipeline || {};


  const modality =
    pipeline?.modality || {};


  const model2 =
    pipeline?.model2 || {};

  const model2Result =
    model2?.result || {};


  const model3 =
    pipeline?.model3 || {};

  const model3Result =
    model3?.result || {};


  const model4 =
    pipeline?.model4 || {};

  const model4Result =
    model4?.result || {};


  const measurements =
    model4Result?.measurements || {};


  const segmentation =
    model4Result?.segmentation || {};


  const model5 =
    pipeline?.model5 || {};

  const model5Prediction =
    model5?.prediction || {};


  const gemini =
    pipeline?.gemini || {};


  const places =
    pipeline?.places || {};


  // ==========================================================
  // MODEL 4 IMAGES
  // ==========================================================

  const maskImage =
    segmentation?.mask_png_base64
      ? `data:image/png;base64,${segmentation.mask_png_base64}`
      : null;


  const boundaryImage =
    segmentation?.boundary_png_base64
      ? `data:image/png;base64,${segmentation.boundary_png_base64}`
      : null;


  const overlayImage =
    segmentation?.overlay_png_base64
      ? `data:image/png;base64,${segmentation.overlay_png_base64}`
      : null;


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="app">


      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <nav className="navbar">

        <div className="navbar-inner">

          <button
            type="button"
            className="brand-button"
            onClick={handleHome}
          >

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

          </button>


          <div className="nav-status">

            <span className="status-dot"></span>

            AI System Online

          </div>

        </div>

      </nav>


      {/* ======================================================
          HOME PAGE
      ====================================================== */}

      {page === "home" && (

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
                MedFusion AI analyzes MRI and CT
                brain scans through a multi-stage
                machine learning pipeline to provide
                an educational analysis.
              </p>

            </div>

          </section>


          {/* ==================================================
              ANALYSIS CARD
          ================================================== */}

          <section className="analysis-wrapper">

            <div className="analysis-card">


              {/* HEADER */}

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


              {/* UPLOAD */}

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
                  accept=".jpg,.jpeg,.png,.bmp,.tif,.tiff,image/*"
                  onChange={handleFileChange}
                  hidden
                />

              </label>


              {/* PATIENT */}

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
                    by the current pipeline is collected.
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


              {/* LOCATION */}

              <div className="location-section">

                <div className="section-title">

                  <div className="section-number">
                    STEP 03
                  </div>

                  <h2>
                    Your location
                  </h2>

                  <p>
                    Used only to create a nearby
                    hospital search on Google Maps.
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


              {/* ERROR */}

              {errorMessage && (

                <div className="form-error">
                  <strong>
                    Unable to continue
                  </strong>

                  <span>
                    {errorMessage}
                  </span>
                </div>

              )}


              {/* ANALYZE */}

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

                      Running AI analysis...

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

      )}


      {/* ======================================================
          RESULTS PAGE
      ====================================================== */}

      {page === "results" && analysisResult && (

        <main className="results-page">


          {/* ==================================================
              RESULTS HERO
          ================================================== */}

          <section className="results-hero">

            <div className="results-hero-inner">

              <button
                type="button"
                className="home-button"
                onClick={handleHome}
              >
                ← Home
              </button>


              <div className="results-title">

                <div className="hero-badge">
                  <span>✓</span>
                  ANALYSIS COMPLETE
                </div>

                <h1>
                  Brain Scan
                  <span> Analysis</span>
                </h1>

                <p>
                  Results generated by the MedFusion
                  multi-stage AI pipeline.
                </p>

              </div>

            </div>

          </section>


          {/* ==================================================
              RESULTS
          ================================================== */}

          <section className="results-wrapper">

            <div className="results-card">


              {/* =================================================
                  OVERVIEW
              ================================================= */}

              <div className="overview-grid">


                {/* MODALITY */}

                <div className="overview-card">

                  <div className="overview-icon">
                    ◉
                  </div>

                  <div>

                    <span>
                      SCAN TYPE
                    </span>

                    <strong>
                      {modality?.predicted_modality ||
                        "Not available"}
                    </strong>

                    {modality?.confidence !==
                      undefined && (

                      <small>
                        Confidence{" "}
                        {formatPercent(
                          getConfidencePercent(
                            modality.confidence
                          )
                        )}
                      </small>

                    )}

                  </div>

                </div>


                {/* DETECTION */}

                <div
                  className={`overview-card ${
                    pipeline?.tumor_detected
                      ? "overview-alert"
                      : "overview-safe"
                  }`}
                >

                  <div className="overview-icon">
                    {pipeline?.tumor_detected
                      ? "!"
                      : "✓"}
                  </div>

                  <div>

                    <span>
                      DETECTION
                    </span>

                    <strong>
                      {pipeline?.tumor_detected
                        ? "Tumor detected"
                        : "No tumor detected"}
                    </strong>

                    {model2Result?.confidence !==
                      undefined && (

                      <small>
                        Confidence{" "}
                        {formatPercent(
                          getConfidencePercent(
                            model2Result.confidence
                          )
                        )}
                      </small>

                    )}

                  </div>

                </div>


                {/* PIPELINE */}

                <div className="overview-card">

                  <div className="overview-icon">
                    ✓
                  </div>

                  <div>

                    <span>
                      PIPELINE
                    </span>

                    <strong>
                      {pipeline?.pipeline_status ||
                        "Completed"}
                    </strong>

                    <small>
                      Multi-stage analysis
                    </small>

                  </div>

                </div>

              </div>


              {/* =================================================
                  MODEL 2
              ================================================= */}

              {pipeline?.model2 && (

                <div className="result-section">

                  <div className="result-section-label">
                    MODEL 2
                  </div>

                  <div className="section-heading-row">

                    <div>

                      <h2>
                        Tumor Detection
                      </h2>

                      <p>
                        {model2?.type ||
                          "Tumor detection model"}
                      </p>

                    </div>

                    <div
                      className={`result-pill ${
                        pipeline?.tumor_detected
                          ? "pill-warning"
                          : "pill-success"
                      }`}
                    >
                      {model2Result?.predicted_class ||
                        "Unknown"}
                    </div>

                  </div>


                  {model2Result?.probabilities && (

                    <div className="probability-list">

                      {Object.entries(
                        model2Result.probabilities
                      ).map(
                        ([label, value]) => (

                          <div
                            className="probability-row"
                            key={label}
                          >

                            <div>

                              <span>
                                {label}
                              </span>

                              <div className="probability-bar">

                                <div
                                  className="probability-fill"
                                  style={{
                                    width: `${Math.min(
                                      100,
                                      Math.max(
                                        0,
                                        getConfidencePercent(
                                          value
                                        )
                                      )
                                    )}%`,
                                  }}
                                />

                              </div>

                            </div>

                            <strong>
                              {formatPercent(
                                getConfidencePercent(
                                  value
                                )
                              )}
                            </strong>

                          </div>

                        )
                      )}

                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  MODEL 3
              ================================================= */}

              {pipeline?.model3 && (

                <div className="result-section">

                  <div className="result-section-label">
                    MODEL 3
                  </div>

                  <div className="section-heading-row">

                    <div>

                      <h2>
                        Tumor Type Classification
                      </h2>

                      <p>
                        Most likely tumor type predicted
                        by the classification model.
                      </p>

                    </div>


                    <div className="type-result">

                      <span>
                        Predicted type
                      </span>

                      <strong>
                        {model3Result?.tumor_type ||
                          "Undetermined"}
                      </strong>

                    </div>

                  </div>


                  <div className="confidence-highlight">

                    <div>

                      <span>
                        MODEL CONFIDENCE
                      </span>

                      <strong>
                        {formatPercent(
                          model3Result?.confidence_percent
                        )}
                      </strong>

                    </div>


                    <div className="confidence-track">

                      <div
                        className="confidence-value"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(
                              0,
                              Number(
                                model3Result?.confidence_percent ||
                                0
                              )
                            )
                          )}%`,
                        }}
                      />

                    </div>

                  </div>


                  {/* ALL PREDICTIONS */}

                  {model3Result?.predictions && (

                    <div className="prediction-grid">

                      {Object.entries(
                        model3Result.predictions
                      ).map(
                        ([label, value]) => (

                          <div
                            className="prediction-item"
                            key={label}
                          >

                            <span>
                              {label}
                            </span>

                            <strong>
                              {formatPercent(value)}
                            </strong>

                          </div>

                        )
                      )}

                    </div>

                  )}


                  <div className="result-note">
                    AI classification output only. It is
                    not a confirmed medical diagnosis.
                  </div>

                </div>

              )}


              {/* =================================================
                  MODEL 4
              ================================================= */}

              {pipeline?.model4 && (

                <div className="result-section">

                  <div className="result-section-label">
                    MODEL 4A
                  </div>

                  <div className="section-heading-row">

                    <div>

                      <h2>
                        Tumor Segmentation
                      </h2>

                      <p>
                        Localization and measurement of
                        the predicted tumor region.
                      </p>

                    </div>


                    <div
                      className={`result-pill ${
                        model4Result?.tumor_detected
                          ? "pill-warning"
                          : "pill-success"
                      }`}
                    >
                      {model4Result?.tumor_detected
                        ? "Region detected"
                        : "No region detected"}
                    </div>

                  </div>


                  {/* MEASUREMENTS */}

                  <div className="measurement-grid">


                    <div className="measurement-item">

                      <span>
                        Tumor Area
                      </span>

                      <strong>
                        {formatNumber(
                          measurements?.area_pixels
                        )}
                        {" "}pixels
                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Image Area
                      </span>

                      <strong>
                        {measurements?.tumor_percentage !==
                          undefined
                          ? `${Number(
                              measurements.tumor_percentage
                            ).toFixed(2)}%`
                          : "—"}
                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Width
                      </span>

                      <strong>
                        {formatNumber(
                          measurements?.width_pixels
                        )}
                        {" "}px
                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Height
                      </span>

                      <strong>
                        {formatNumber(
                          measurements?.height_pixels
                        )}
                        {" "}px
                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Mean Confidence
                      </span>

                      <strong>
                        {formatPercent(
                          measurements?.mean_confidence_percent
                        )}
                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Max Confidence
                      </span>

                      <strong>
                        {formatPercent(
                          measurements?.max_confidence_percent
                        )}
                      </strong>

                    </div>

                  </div>


                  {/* BOUNDING BOX */}

                  {measurements?.bounding_box && (

                    <div className="technical-box">

                      <div className="technical-title">
                        Bounding Box
                      </div>

                      <div className="technical-grid">

                        <span>
                          X min:
                          <strong>
                            {" "}
                            {measurements.bounding_box.x_min}
                          </strong>
                        </span>

                        <span>
                          Y min:
                          <strong>
                            {" "}
                            {measurements.bounding_box.y_min}
                          </strong>
                        </span>

                        <span>
                          X max:
                          <strong>
                            {" "}
                            {measurements.bounding_box.x_max}
                          </strong>
                        </span>

                        <span>
                          Y max:
                          <strong>
                            {" "}
                            {measurements.bounding_box.y_max}
                          </strong>
                        </span>

                      </div>

                    </div>

                  )}


                  {/* CENTROID */}

                  {measurements?.centroid && (

                    <div className="technical-box">

                      <div className="technical-title">
                        Tumor Centroid
                      </div>

                      <div className="centroid-value">

                        X:{" "}
                        {measurements.centroid.x}

                        {"   "}

                        Y:{" "}
                        {measurements.centroid.y}

                      </div>

                    </div>

                  )}


                  {/* EXPERIMENTAL WARNING */}

                  {model4?.experimental && (

                    <div className="result-warning">
                      Model 4A output is experimental for
                      this input modality.
                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  MODEL 4 IMAGES
              ================================================= */}

              {(maskImage ||
                boundaryImage ||
                overlayImage) && (

                <div className="result-section">

                  <div className="result-section-label">
                    VISUAL SEGMENTATION
                  </div>

                  <h2>
                    Segmentation Visualizations
                  </h2>

                  <p>
                    The following images are generated
                    directly by Model 4A.
                  </p>


                  <div className="segmentation-grid">


                    {overlayImage && (

                      <div className="segmentation-item">

                        <div className="segmentation-title">
                          Tumor Overlay
                        </div>

                        <img
                          src={overlayImage}
                          alt="Tumor segmentation overlay"
                        />

                      </div>

                    )}


                    {maskImage && (

                      <div className="segmentation-item">

                        <div className="segmentation-title">
                          Binary Mask
                        </div>

                        <img
                          src={maskImage}
                          alt="Tumor segmentation mask"
                        />

                      </div>

                    )}


                    {boundaryImage && (

                      <div className="segmentation-item">

                        <div className="segmentation-title">
                          Tumor Boundary
                        </div>

                        <img
                          src={boundaryImage}
                          alt="Tumor boundary"
                        />

                      </div>

                    )}

                  </div>

                </div>

              )}


              {/* =================================================
                  MODEL 5
              ================================================= */}

              {pipeline?.model5 && (

                <div className="result-section">

                  <div className="result-section-label">
                    MODEL 5
                  </div>

                  <div className="section-heading-row">

                    <div>

                      <h2>
                        WHO Grade
                      </h2>

                      <p>
                        Experimental AI-based WHO grade
                        classification.
                      </p>

                    </div>


                    {model5?.available && (

                      <div className="type-result">

                        <span>
                          Predicted grade
                        </span>

                        <strong>
                          Grade{" "}
                          {model5Prediction?.who_grade}
                        </strong>

                      </div>

                    )}

                  </div>


                  {model5?.available ? (

                    <>

                      <div className="confidence-highlight">

                        <div>

                          <span>
                            MODEL CONFIDENCE
                          </span>

                          <strong>
                            {formatPercent(
                              model5Prediction?.confidence_percent
                            )}
                          </strong>

                        </div>

                      </div>


                      {model5Prediction?.probabilities && (

                        <div className="prediction-grid">

                          {Object.entries(
                            model5Prediction.probabilities
                          ).map(
                            ([label, value]) => (

                              <div
                                className="prediction-item"
                                key={label}
                              >

                                <span>
                                  {label}
                                </span>

                                <strong>
                                  {formatPercent(value)}
                                </strong>

                              </div>

                            )
                          )}

                        </div>

                      )}

                      <div className="result-warning">
                        Experimental AI output. This is not
                        a confirmed pathological WHO grade.
                      </div>

                    </>

                  ) : (

                    <div className="unavailable-box">

                      <strong>
                        WHO Grade unavailable
                      </strong>

                      <p>
                        Model 5 was not executed because
                        its required trained MRI metadata
                        was not supplied.
                      </p>

                      {model5?.missing_features &&
                        model5.missing_features.length > 0 && (

                        <div className="missing-features">

                          <span>
                            Missing metadata:
                          </span>

                          <ul>

                            {model5.missing_features.map(
                              (feature) => (

                                <li key={feature}>
                                  {feature}
                                </li>

                              )
                            )}

                          </ul>

                        </div>

                      )}

                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  GEMINI
              ================================================= */}

              {gemini && (

                <div className="result-section gemini-section">

                  <div className="result-section-label">
                    GEMINI AI
                  </div>

                  <div className="gemini-header">

                    <div>

                      <h2>
                        AI-Generated Report
                      </h2>

                      <p>
                        A concise summary generated from
                        the pipeline outputs.
                      </p>

                    </div>


                    {gemini?.model && (

                      <span className="model-badge">
                        {gemini.model}
                      </span>

                    )}

                  </div>


                  {gemini?.report ? (

                    <div className="gemini-report">

                      {gemini.report}

                    </div>

                  ) : (

                    <div className="unavailable-box">

                      Gemini report was not available.

                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  PLACES
              ================================================= */}

              <div className="result-section">

                <div className="result-section-label">
                  NEARBY CARE
                </div>

                <h2>
                  Find a nearby hospital
                </h2>

                <p>
                  Open Google Maps to search for
                  hospitals near the location you provided.
                </p>


                {places?.maps_search_url ? (

                  <a
                    href={
                      places.maps_search_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="maps-button"
                  >

                    Open Google Maps

                    <span>
                      ↗
                    </span>

                  </a>

                ) : (

                  <div className="unavailable-box">

                    <strong>
                      Location not available
                    </strong>

                    <p>
                      A nearby hospital search could not
                      be generated because no location was
                      provided.
                    </p>

                  </div>

                )}

              </div>


              {/* =================================================
                  IMPORTANT NOTE
              ================================================= */}

              <div className="important-note">

                <strong>
                  Important Note
                </strong>

                <p>
                  MedFusion AI is an educational college
                  project. Its outputs are AI-generated
                  predictions and must not be treated as a
                  confirmed medical diagnosis. Please
                  discuss these findings with a qualified
                  healthcare professional before making any
                  medical decision.
                </p>

              </div>


              {/* =================================================
                  HOME BUTTON
              ================================================= */}

              <button
                type="button"
                className="results-home-button"
                onClick={handleHome}
              >
                ← Start a new analysis
              </button>


            </div>

          </section>


          {/* ==================================================
              CHATBOT
          ================================================== */}

          <button
            type="button"
            className={`chatbot-fab ${
              chatOpen
                ? "chatbot-fab-open"
                : ""
            }`}
            onClick={() =>
              setChatOpen(
                (previous) =>
                  !previous
              )
            }
            aria-label="Open AI chatbot"
          >

            {chatOpen
              ? "×"
              : "💬"}

          </button>


          {chatOpen && (

            <div className="chatbot-window">


              {/* CHAT HEADER */}

              <div className="chatbot-header">

                <div>

                  <strong>
                    MedFusion AI
                  </strong>

                  <span>
                    Separate AI Assistant
                  </span>

                </div>


                <button
                  type="button"
                  onClick={() =>
                    setChatOpen(false)
                  }
                  aria-label="Close chatbot"
                >
                  ×
                </button>

              </div>


              {/* CHAT MESSAGES */}

              <div className="chatbot-messages">

                {chatMessages.map(
                  (message, index) => (

                    <div
                      key={`${message.role}-${index}`}
                      className={`chat-message ${
                        message.role === "user"
                          ? "chat-message-user"
                          : "chat-message-assistant"
                      } ${
                        message.error
                          ? "chat-message-error"
                          : ""
                      }`}
                    >

                      <div className="chat-bubble">
                        {message.text}
                      </div>

                    </div>

                  )
                )}


                {chatLoading && (

                  <div className="chat-message chat-message-assistant">

                    <div className="chat-bubble typing">

                      <span></span>
                      <span></span>
                      <span></span>

                    </div>

                  </div>

                )}

              </div>


              {/* CHAT INPUT */}

              <form
                className="chatbot-input"
                onSubmit={handleChatSubmit}
              >

                <input
                  type="text"
                  value={chatInput}
                  onChange={(event) =>
                    setChatInput(
                      event.target.value
                    )
                  }
                  placeholder="Ask something..."
                  disabled={chatLoading}
                />

                <button
                  type="submit"
                  disabled={
                    chatLoading ||
                    !chatInput.trim()
                  }
                >
                  →
                </button>

              </form>


              <div className="chatbot-disclaimer">
                Educational assistant only. Not a doctor
                and not a replacement for professional care.
              </div>

            </div>

          )}

        </main>

      )}


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