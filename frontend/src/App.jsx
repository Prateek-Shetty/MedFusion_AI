import {
  useEffect,
  useState,
} from "react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import "./App.css";

import {
  analyzeScan,
  sendChatMessage,
} from "./services/api";


// ============================================================
// HELPERS
// ============================================================
function getPredictionChartData(predictions) {
  if (!predictions || typeof predictions !== "object") {
    return [];
  }

  return Object.entries(predictions)
    .map(([tumorType, value]) => {
      const numericValue = Number(value);

      if (!Number.isFinite(numericValue)) {
        return null;
      }

      const probability =
        numericValue <= 1
          ? numericValue * 100
          : numericValue;

      return {
        tumorType,
        probability: Number(probability.toFixed(2)),
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) =>
        b.probability - a.probability
    );
}
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


// function getNestedValue(
//   object,
//   keys = [],
// ) {
//   let current = object;

//   for (const key of keys) {

//     if (
//       current === null ||
//       current === undefined
//     ) {
//       return undefined;
//     }

//     current = current[key];
//   }

//   return current;
// }


function firstAvailable(
  ...values
) {
  for (const value of values) {

    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      return value;
    }

  }

  return undefined;
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

  const handleFileChange = (
    event
  ) => {

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


    const allowedExtensions = [
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


      if (
        !message ||
        chatLoading
      ) {
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

  const predictionChartData =
  getPredictionChartData(
    model3Result?.predictions
  );


  const model4 =
    pipeline?.model4 || {};


  const model4Result =
    model4?.result || {};


  const measurements =
    model4Result?.measurements || {};


  const segmentation =
    model4Result?.segmentation || {};


  const gemini =
    pipeline?.gemini || {};


  const places =
    pipeline?.places || {};


  // ==========================================================
  // GEMINI STRUCTURED DATA
  // ==========================================================

  const geminiStructured =
    gemini?.structured ||
    gemini?.data ||
    {};


  const geminiSummary =
    geminiStructured?.summary ||
    "";


  const geminiFinding =
    geminiStructured?.finding_explanation ||
    "";


  const geminiNextStep =
    geminiStructured?.next_step ||
    "";


  const geminiSpecialist =
    geminiStructured?.specialist ||
    "";


  const geminiPatientContext =
    geminiStructured?.patient_context ||
    "";


  const geminiGuidance =
    Array.isArray(
      geminiStructured?.supportive_guidance
    )
      ? geminiStructured.supportive_guidance
      : [];


  const geminiSafety =
    geminiStructured?.safety_note ||
    "";


  const hasStructuredGemini =
    Boolean(
      geminiSummary ||
      geminiFinding ||
      geminiNextStep ||
      geminiSpecialist ||
      geminiPatientContext ||
      geminiGuidance.length ||
      geminiSafety
    );


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
  // DERIVED VALUES
  // ==========================================================

  const predictedModality =
    firstAvailable(
      modality?.predicted_modality,
      modality?.prediction,
      modality?.class,
      "Not available"
    );


  const tumorDetected =
    Boolean(
      pipeline?.tumor_detected ??
      model4Result?.tumor_detected ??
      false
    );


  const model2Confidence =
    firstAvailable(
      model2Result?.confidence_percent,
      getConfidencePercent(
        model2Result?.confidence
      ),
      model2Result?.confidence
    );


  const tumorType =
    firstAvailable(
      model3Result?.tumor_type,
      model3Result?.predicted_class,
      model3Result?.prediction,
      "Undetermined"
    );


  const model3Confidence =
    firstAvailable(
      model3Result?.confidence_percent,
      getConfidencePercent(
        model3Result?.confidence
      )
    );


  const tumorArea =
    firstAvailable(
      measurements?.area_pixels,
      measurements?.tumor_area_pixels,
      measurements?.area
    );


  const tumorPercentage =
    firstAvailable(
      measurements?.tumor_percentage,
      measurements?.tumor_percentage_of_image
    );


  const tumorWidth =
    firstAvailable(
      measurements?.width_pixels,
      measurements?.tumor_width_pixels,
      measurements?.width
    );


  const tumorHeight =
    firstAvailable(
      measurements?.height_pixels,
      measurements?.tumor_height_pixels,
      measurements?.height
    );


  const meanSegmentationConfidence =
    firstAvailable(
      measurements?.mean_confidence_percent,
      measurements?.mean_confidence
    );


  const maxSegmentationConfidence =
    firstAvailable(
      measurements?.max_confidence_percent,
      measurements?.max_confidence
    );


  // ==========================================================
  // GEMINI FALLBACK REPORT
  // ==========================================================

  const oldGeminiReport =
    gemini?.report || "";


  const showOldGeminiReport =
    Boolean(
      oldGeminiReport &&
      !hasStructuredGemini
    );


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

                <span>
                  {" "}brain scan{" "}
                </span>

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
                    specialist search on Google Maps.
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
                        ? "Ready for specialist search"
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

      {page === "results" &&
        analysisResult && (

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

                  <span>
                    {" "}Analysis
                  </span>

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
                      {predictedModality}
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
                    tumorDetected
                      ? "overview-alert"
                      : "overview-safe"
                  }`}
                >

                  <div className="overview-icon">

                    {tumorDetected
                      ? "!"
                      : "✓"}

                  </div>

                  <div>

                    <span>
                      DETECTION
                    </span>

                    <strong>

                      {tumorDetected
                        ? "Tumor detected"
                        : "No tumor detected"}

                    </strong>

                    {model2Confidence !==
                      undefined && (

                      <small>

                        Confidence{" "}

                        {formatPercent(
                          model2Confidence
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
                  MODEL 2 CARD
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
                        tumorDetected
                          ? "pill-warning"
                          : "pill-success"
                      }`}
                    >

                      {model2Result?.predicted_class ||
                        (tumorDetected
                          ? "Tumor detected"
                          : "No tumor")}

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
                  MODEL 3 CARD
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
                        {tumorType}
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
                          model3Confidence
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
                                model3Confidence ||
                                0
                              )
                            )
                          )}%`,
                        }}
                      />

                    </div>

                  </div>


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

                    AI classification output only.
                    It is not a confirmed medical diagnosis.

                  </div>

                </div>

              )}


              {/* =================================================
                  MODEL 3 DYNAMIC CHART
              ================================================= */}

              {predictionChartData.length > 0 && (

                <div className="result-section">

                  <div className="result-section-label">
                    MODEL 3 VISUAL ANALYSIS
                  </div>

                  <div className="section-heading-row">

                    <div>

                      <h2>
                        Tumor Type Probability Profile
                      </h2>

                      <p>
                        Dynamic visualization of the probability
                        distribution produced by Model 3.
                      </p>

                    </div>

                    <div className="result-pill pill-success">
                      {predictionChartData.length} classes
                    </div>

                  </div>

                  <div
                    className="prediction-chart-card"
                    role="img"
                    aria-label="Tumor type probability chart"
                  >

                    <ResponsiveContainer
                      width="100%"
                      height={320}
                    >

                      <BarChart
                        data={predictionChartData}
                        margin={{
                          top: 10,
                          right: 20,
                          left: 0,
                          bottom: 55,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                        />

                        <XAxis
                          dataKey="tumorType"
                          angle={-25}
                          textAnchor="end"
                          interval={0}
                          height={70}
                        />

                        <YAxis
                          domain={[0, 100]}
                          tickFormatter={(value) =>
                            `${value}%`
                          }
                          width={55}
                        />

                        <Tooltip
                          formatter={(value) => [
                            `${Number(value).toFixed(2)}%`,
                            "Probability",
                          ]}
                          labelFormatter={(label) =>
                            `Tumor type: ${label}`
                          }
                        />

                        <Bar
                          dataKey="probability"
                          name="Probability"
                          radius={[6, 6, 0, 0]}
                        />

                      </BarChart>

                    </ResponsiveContainer>

                  </div>

                  <div className="result-note">
                    This visualization is generated dynamically
                    from the Model 3 prediction probabilities.
                    It is an AI classification output and is not
                    a confirmed medical diagnosis.
                  </div>

                </div>

              )}


              {/* =================================================
                  MODEL 4 CARD
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
                          tumorArea
                        )}

                        {" "}pixels

                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Image Area
                      </span>

                      <strong>

                        {tumorPercentage !==
                          undefined
                          ? `${Number(
                              tumorPercentage
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
                          tumorWidth
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
                          tumorHeight
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
                          meanSegmentationConfidence
                        )}

                      </strong>

                    </div>


                    <div className="measurement-item">

                      <span>
                        Max Confidence
                      </span>

                      <strong>

                        {formatPercent(
                          maxSegmentationConfidence
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


                  {model4?.experimental && (

                    <div className="result-warning">

                      Model 4A output is experimental for
                      this input modality.

                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  MODEL 4 VISUALIZATION
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
                  GEMINI — SUMMARY CARD
              ================================================= */}

              {gemini && (

                <div className="result-section gemini-section">

                  <div className="result-section-label">
                    GEMINI AI
                  </div>


                  <div className="gemini-header">

                    <div>

                      <h2>
                        AI Analysis Summary
                      </h2>

                      <p>
                        AI-generated interpretation of
                        the pipeline results.
                      </p>

                    </div>


                    {gemini?.model && (

                      <span className="model-badge">
                        {gemini.model}
                      </span>

                    )}

                  </div>


                  {hasStructuredGemini ? (

                    <div className="gemini-card-grid">


                      {/* =================================================
                          SUMMARY
                      ================================================= */}

                      <div className="gemini-result-card gemini-summary-card">

                        <div className="gemini-card-icon">
                          🧠
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            AI SUMMARY
                          </span>

                          <h3>
                            Overall Analysis
                          </h3>

                          <p>
                            {geminiSummary ||
                              "Not available from the current pipeline."}
                          </p>

                        </div>

                      </div>


                      {/* =================================================
                          FINDINGS
                      ================================================= */}

                      <div className="gemini-result-card">

                        <div className="gemini-card-icon">
                          🔬
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            FINDINGS
                          </span>

                          <h3>
                            AI Findings
                          </h3>

                          <p>
                            {geminiFinding ||
                              "Not available from the current pipeline."}
                          </p>

                        </div>

                      </div>


                      {/* =================================================
                          PATIENT CONTEXT
                      ================================================= */}

                      <div className="gemini-result-card">

                        <div className="gemini-card-icon">
                          👤
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            PATIENT CONTEXT
                          </span>

                          <h3>
                            Age & Gender Context
                          </h3>

                          <p>

                            {geminiPatientContext ||
                              `Age: ${age} years · Gender: ${gender}`}

                          </p>

                        </div>

                      </div>


                      {/* =================================================
                          NEXT STEP
                      ================================================= */}

                      <div className="gemini-result-card">

                        <div className="gemini-card-icon">
                          ➜
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            NEXT STEP
                          </span>

                          <h3>
                            Suggested Next Step
                          </h3>

                          <p>

                            {geminiNextStep ||
                              "Not available from the current pipeline."}

                          </p>

                        </div>

                      </div>


                      {/* =================================================
                          SPECIALIST
                      ================================================= */}

                      <div className="gemini-result-card">

                        <div className="gemini-card-icon">
                          👨‍⚕️
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            SPECIALIST
                          </span>

                          <h3>
                            Suggested Specialist
                          </h3>

                          <p>

                            {geminiSpecialist ||
                              "Neurosurgery"}

                          </p>

                        </div>

                      </div>


                      {/* =================================================
                          SUPPORTIVE GUIDANCE
                      ================================================= */}

                      <div className="gemini-result-card">

                        <div className="gemini-card-icon">
                          🌿
                        </div>

                        <div className="gemini-card-content">

                          <span className="gemini-card-label">
                            SUPPORTIVE GUIDANCE
                          </span>

                          <h3>
                            General Guidance
                          </h3>


                          {geminiGuidance.length > 0 ? (

                            <ul className="guidance-list">

                              {geminiGuidance.map(
                                (
                                  item,
                                  index
                                ) => (

                                  <li
                                    key={`${index}-${item}`}
                                  >
                                    {item}
                                  </li>

                                )
                              )}

                            </ul>

                          ) : (

                            <ul className="guidance-list">

                              <li>
                                Discuss the AI-generated findings with a qualified healthcare professional.
                              </li>

                              <li>
                                Keep the scan and report available for professional review.
                              </li>

                              <li>
                                Do not self-medicate based on an AI result.
                              </li>

                            </ul>

                          )}

                        </div>

                      </div>


                      {/* =================================================
                          SAFETY
                      ================================================= */}

                      <div className="gemini-safety-card">

                        <div className="gemini-card-icon">
                          ⚠️
                        </div>

                        <div>

                          <span className="gemini-card-label">
                            IMPORTANT
                          </span>

                          <p>

                            {geminiSafety ||
                              "This is an AI-generated research output and requires review by a qualified healthcare professional."}

                          </p>

                        </div>

                      </div>

                    </div>

                  ) : showOldGeminiReport ? (

                    /* =================================================
                       BACKWARD COMPATIBILITY
                    ================================================= */

                    <div className="gemini-report">

                      {oldGeminiReport}

                    </div>

                  ) : (

                    <div className="unavailable-box">

                      Gemini analysis was not available
                      from the current pipeline.

                    </div>

                  )}

                </div>

              )}


              {/* =================================================
                  PLACES
              ================================================= */}

              <div className="result-section">

                <div className="result-section-label">
                  NEARBY SPECIALIST CARE
                </div>


                <h2>
                  Find Neurosurgery Care
                </h2>


                <p>
                  Search for neurosurgery and
                  specialist hospitals near your
                  provided location.
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

                    Find Neurosurgery Hospitals

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
                      A nearby specialist search could
                      not be generated because no location
                      was provided.
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

                Educational assistant only.
                Not a doctor and not a replacement
                for professional care.

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