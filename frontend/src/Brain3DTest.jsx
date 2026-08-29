import {
  Suspense,
  useMemo,
  useState,
} from "react";

import {
  Canvas,
} from "@react-three/fiber";

import {
  Environment,
  OrbitControls,
  useGLTF,
} from "@react-three/drei";

import * as THREE from "three";

import "./Brain3DTest.css";


const MODEL_PATH = "/models/brain.glb";


// ============================================================
// BRAIN COLORS
// ============================================================

const BRAIN_COLORS = {
  DeepBlue: "#668ca8",
  Slate: "#71808d",
  Steel: "#7897a8",
  Charcoal: "#626e79",
  Graphite: "#707982",
  Teal: "#628d91",
  MutedRose: "#907e82",
  Medical: "#718fa0",

  DarkBrown: "#735c50",
  Burgundy: "#754b54",
  DarkOlive: "#68705a",
  DarkPurple: "#625a76",
  DeepCyan: "#527f87",
  DarkAmber: "#806b4e",
  Forest: "#526d5d",
  DarkSand: "#807766",
};


// ============================================================
// FORMAT HELPERS
// ============================================================

function formatNumber(
  value,
  suffix = ""
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return `${value}${suffix}`;
  }

  return `${number.toLocaleString(
    undefined,
    {
      maximumFractionDigits: 2,
    }
  )}${suffix}`;
}


function formatPercent(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  return `${number.toFixed(2)}%`;
}


// ============================================================
// ANALYSIS DATA
// ============================================================

function getAnalysisData(
  analysisResult
) {
  const pipeline =
    analysisResult?.pipeline || {};

  const modality =
    pipeline?.modality || {};

  const model2Result =
    pipeline?.model2?.result || {};

  const model3Result =
    pipeline?.model3?.result || {};

  const model4Result =
    pipeline?.model4?.result || {};

  const measurements =
    model4Result?.measurements || {};

  const tumorDetected =
    Boolean(
      pipeline?.tumor_detected ??
      model2Result?.tumor_detected ??
      model4Result?.tumor_detected
    );

  return {
    scanType:
      modality?.predicted_modality ||
      modality?.modality ||
      "Not available",

    tumorDetected,

    tumorType:
      model3Result?.tumor_type ||
      model3Result?.predicted_class ||
      null,

    detectionConfidence:
      model2Result?.confidence_percent ??
      null,

    classificationConfidence:
      model3Result?.confidence_percent ??
      null,

    segmentationConfidence:
      measurements
        ?.mean_confidence_percent ??
      null,

    tumorArea:
      measurements?.area_pixels ??
      null,

    tumorPercentage:
      measurements?.tumor_percentage ??
      null,

    width:
      measurements?.width_pixels ??
      null,

    height:
      measurements?.height_pixels ??
      null,

    boundingBox:
      measurements?.bounding_box ||
      null,

    centroid:
      measurements?.centroid ||
      null,
  };
}


// ============================================================
// IMPORTANT
// ============================================================
// Every brain instance receives its OWN material.
//
// This prevents:
// Normal Brain -> changing Tumor Brain
// Tumor Brain -> changing Normal Brain
//
// GLTF scenes can share materials. We explicitly clone them.
// ============================================================

function prepareBrain(
  scene,
  color,
  opacity
) {
  scene.traverse(
    (object) => {
      if (!object.isMesh) {
        return;
      }

      object.castShadow = true;
      object.receiveShadow = true;


      if (!object.material) {
        return;
      }


      const originalMaterials =
        Array.isArray(
          object.material
        )
          ? object.material
          : [
              object.material,
            ];


      // CRITICAL FIX:
      // Clone every material independently.
      const independentMaterials =
        originalMaterials.map(
          (originalMaterial) => {

            const material =
              originalMaterial.clone();

            material.transparent =
              opacity < 0.99;

            material.opacity =
              opacity;

            material.depthWrite =
              opacity >= 0.75;

            material.roughness =
              0.58;

            material.metalness =
              0.02;


            if (
              material.color
            ) {
              material.color.set(
                color
              );
            }


            if (
              material.emissive
            ) {
              material.emissive.set(
                "#102c3d"
              );

              material.emissiveIntensity =
                0.12;
            }


            material.needsUpdate =
              true;


            return material;
          }
        );


      object.material =
        Array.isArray(
          object.material
        )
          ? independentMaterials
          : independentMaterials[0];
    }
  );


  return scene;
}


// ============================================================
// BRAIN MODEL
// ============================================================

function BrainModel({
  color,
  opacity,
}) {
  const {
    scene,
  } = useGLTF(
    MODEL_PATH
  );


  const preparedScene =
    useMemo(
      () => {
        const clonedScene =
          scene.clone(
            true
          );


        return prepareBrain(
          clonedScene,
          color,
          opacity
        );
      },
      [
        scene,
        color,
        opacity,
      ]
    );


  return (
    <primitive
      object={
        preparedScene
      }
      scale={2.05}
      position={[
        0,
        -1.05,
        0,
      ]}
    />
  );
}


// ============================================================
// TUMOR MARKER
// ============================================================

function TumorMarker({
  position,
  size,
  opacity,
}) {
  const geometry =
    useMemo(
      () => {
        const geo =
          new THREE.IcosahedronGeometry(
            1,
            3
          );


        const attribute =
          geo.attributes.position;

        const vertex =
          new THREE.Vector3();


        for (
          let index = 0;
          index <
          attribute.count;
          index += 1
        ) {
          vertex.fromBufferAttribute(
            attribute,
            index
          );


          const distortion =
            1 +
            0.13 *
              Math.sin(
                vertex.x * 7 +
                vertex.y * 4
              ) +
            0.08 *
              Math.cos(
                vertex.z * 9 +
                vertex.x * 3
              );


          vertex.multiplyScalar(
            distortion
          );


          attribute.setXYZ(
            index,
            vertex.x,
            vertex.y,
            vertex.z
          );
        }


        attribute.needsUpdate =
          true;


        geo.computeVertexNormals();


        return geo;
      },
      []
    );


  if (!position) {
    return null;
  }


  return (
    <group
      position={
        position
      }
    >

      {/* Outer glow */}

      <mesh
        scale={1.4}
      >

        <sphereGeometry
          args={[
            size,
            32,
            32,
          ]}
        />

        <meshBasicMaterial
          color="#ff273c"
          transparent
          opacity={
            opacity * 0.07
          }
          depthWrite={false}
        />

      </mesh>


      {/* Irregular tumor body */}

      <mesh
        geometry={
          geometry
        }
        scale={[
          size * 1.15,
          size * 0.92,
          size,
        ]}
      >

        <meshPhysicalMaterial
          color="#d72d43"
          emissive="#760d1c"
          emissiveIntensity={0.55}
          roughness={0.42}
          metalness={0}
          transmission={0.08}
          thickness={0.28}
          transparent
          opacity={
            opacity
          }
        />

      </mesh>


      {/* Tumor rim */}

      <mesh
        rotation={[
          Math.PI / 2,
          0.25,
          0,
        ]}
        scale={[
          1.12,
          1,
          1,
        ]}
      >

        <torusGeometry
          args={[
            size * 1.12,
            size * 0.025,
            16,
            64,
          ]}
        />

        <meshBasicMaterial
          color="#ff6d78"
          transparent
          opacity={
            opacity * 0.55
          }
        />

      </mesh>


      <pointLight
        color="#ff3344"
        intensity={0.55}
        distance={1.2}
      />

    </group>
  );
}


// ============================================================
// LIGHTING
// ============================================================

function BrainLighting() {
  return (
    <>
      <ambientLight
        intensity={1.65}
      />

      <directionalLight
        position={[
          4,
          6,
          5,
        ]}
        intensity={3.1}
        castShadow
      />

      <directionalLight
        position={[
          -4,
          2,
          -4,
        ]}
        intensity={1.35}
      />

      <pointLight
        position={[
          0,
          2.2,
          2.5,
        ]}
        intensity={1.05}
        distance={8}
      />

      <Environment
        preset="studio"
      />
    </>
  );
}


// ============================================================
// NORMAL BRAIN
// ============================================================

function ReferenceBrain({
  color,
  opacity,
  autoRotate,
  resetToken,
}) {
  return (
    <Canvas
      shadows
      camera={{
        position: [
          0,
          0.1,
          4.6,
        ],
        fov: 42,
      }}
      dpr={[
        1,
        1.75,
      ]}
    >

      <color
        attach="background"
        args={[
          "#06111d",
        ]}
      />

      <BrainLighting />

      <Suspense
        fallback={null}
      >

        <BrainModel
          color={
            color
          }
          opacity={
            opacity
          }
        />

      </Suspense>


      <OrbitControls
        key={
          resetToken
        }
        makeDefault
        enableDamping
        dampingFactor={0.08}
        minDistance={2.2}
        maxDistance={7}
        rotateSpeed={0.65}
        zoomSpeed={0.8}
        autoRotate={
          autoRotate
        }
        autoRotateSpeed={0.65}
      />

    </Canvas>
  );
}


// ============================================================
// TUMOR BRAIN
// ============================================================

function InteractiveBrain({
  color,
  opacity,
  autoRotate,
  tumorVisible,
  tumorPosition,
  tumorSize,
  tumorOpacity,
  tumorLocked,
  onTumorPlace,
  resetToken,
}) {
  const {
    scene,
  } = useGLTF(
    MODEL_PATH
  );


  // ==========================================================
  // CRITICAL FIX
  // ==========================================================
  // This scene gets completely independent materials from
  // the normal brain.
  // ==========================================================

  const preparedScene =
    useMemo(
      () => {
        const clonedScene =
          scene.clone(
            true
          );


        return prepareBrain(
          clonedScene,
          color,
          opacity
        );
      },
      [
        scene,
        color,
        opacity,
      ]
    );


  const handleBrainClick =
    (event) => {
      event.stopPropagation();


      if (
        tumorLocked
      ) {
        return;
      }


      if (
        !event.point
      ) {
        return;
      }


      onTumorPlace([
        event.point.x,
        event.point.y,
        event.point.z,
      ]);
    };


  return (
    <Canvas
      shadows
      camera={{
        position: [
          0,
          0.1,
          4.6,
        ],
        fov: 42,
      }}
      dpr={[
        1,
        1.75,
      ]}
    >

      <color
        attach="background"
        args={[
          "#06111d",
        ]}
      />

      <BrainLighting />


      <Suspense
        fallback={null}
      >

        <primitive
          object={
            preparedScene
          }
          scale={2.05}
          position={[
            0,
            -1.05,
            0,
          ]}
          onPointerDown={
            handleBrainClick
          }
        />


        {tumorVisible && (
          <TumorMarker
            position={
              tumorPosition
            }
            size={
              tumorSize
            }
            opacity={
              tumorOpacity
            }
          />
        )}

      </Suspense>


      <OrbitControls
        key={
          resetToken
        }
        makeDefault
        enableDamping
        dampingFactor={0.08}
        minDistance={2.2}
        maxDistance={7}
        rotateSpeed={0.65}
        zoomSpeed={0.8}
        autoRotate={
          autoRotate
        }
        autoRotateSpeed={0.65}
      />

    </Canvas>
  );
}


// ============================================================
// DATA CARD
// ============================================================

function DataCard({
  label,
  value,
  accent = "",
}) {
  return (
    <div
      className={
        `brain-data-card ${accent}`
      }
    >

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


// ============================================================
// MAIN PAGE
// ============================================================

function App({
  analysisResult = null,
  onBack,
}) {
  const data =
    getAnalysisData(
      analysisResult
    );


  // ==========================================================
  // NORMAL BRAIN STATE
  // ==========================================================

  const [
    normalColor,
    setNormalColor,
  ] = useState(
    BRAIN_COLORS.DeepBlue
  );


  const [
    normalOpacity,
    setNormalOpacity,
  ] = useState(
    0.88
  );


  const [
    normalAutoRotate,
    setNormalAutoRotate,
  ] = useState(
    false
  );


  const [
    normalResetToken,
    setNormalResetToken,
  ] = useState(
    0
  );


  // ==========================================================
  // TUMOR BRAIN STATE
  // ==========================================================

  const [
    tumorBrainColor,
    setTumorBrainColor,
  ] = useState(
    BRAIN_COLORS.DeepBlue
  );


  const [
    tumorBrainOpacity,
    setTumorBrainOpacity,
  ] = useState(
    0.88
  );


  const [
    tumorVisible,
    setTumorVisible,
  ] = useState(
    data.tumorDetected
  );


  const [
    tumorPosition,
    setTumorPosition,
  ] = useState([
    0.55,
    0.25,
    0.15,
  ]);


  const [
    tumorSize,
    setTumorSize,
  ] = useState(
    0.24
  );


  const [
    tumorOpacity,
    setTumorOpacity,
  ] = useState(
    0.82
  );


  const [
    tumorLocked,
    setTumorLocked,
  ] = useState(
    false
  );


  const [
    tumorAutoRotate,
    setTumorAutoRotate,
  ] = useState(
    false
  );


  const [
    tumorResetToken,
    setTumorResetToken,
  ] = useState(
    0
  );


  // ==========================================================
  // NORMAL ACTIONS
  // ==========================================================

  const resetNormalView =
    () => {
      setNormalResetToken(
        (value) =>
          value + 1
      );
    };


  // ==========================================================
  // TUMOR ACTIONS
  // ==========================================================

  const autoPlaceTumor =
    () => {
      if (
        tumorLocked
      ) {
        return;
      }


      setTumorPosition([
        0.55,
        0.25,
        0.15,
      ]);


      setTumorVisible(
        true
      );
    };


  const clearTumor =
    () => {
      if (
        tumorLocked
      ) {
        return;
      }


      setTumorVisible(
        false
      );
    };


  const resetTumorView =
    () => {
      setTumorResetToken(
        (value) =>
          value + 1
      );
    };


  // ==========================================================
  // STATUS
  // ==========================================================

  const tumorStatus =
    data.tumorDetected
      ? "Region detected"
      : "No region detected";


  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <main className="brain-page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="brain-header">

        <div className="brain-brand">

          <div className="brain-logo">
            ✚
          </div>

          <div>

            <div className="brain-brand-name">
              MedFusion <span>AI</span>
            </div>

            <div className="brain-brand-subtitle">
              3D Brain Visualization
            </div>

          </div>

        </div>


        <div className="brain-header-center">

          <div className="brain-kicker">
            INTERACTIVE VISUALIZATION
          </div>

          <h1>
            Explore the Brain in 3D
          </h1>

          <p>
            Visualize anatomy alongside
            the AI analysis.
          </p>

        </div>


        <button
          type="button"
          className="back-results-button"
          onClick={() =>
            onBack?.()
          }
        >
          ← Back to Results
        </button>

      </header>


      {/* ======================================================
          INTRO
          ====================================================== */}

      <section className="brain-intro">

        <div className="intro-icon">
          ◈
        </div>


        <div>

          <div className="brain-kicker">
            INTERACTIVE 3D BRAIN EXPLORER
          </div>

          <h2>
            Explore anatomy and visualize
            the reported region
          </h2>

          <p>
            Rotate, zoom, change appearance
            and adjust transparency independently
            on each brain.
          </p>

        </div>


        <div className="intro-warning">

          <span>
            ⓘ
          </span>

          <p>
            The red lesion is an illustrative
            educational marker. It is not a
            3D reconstruction of the patient's
            actual tumor.
          </p>

        </div>

      </section>


      {/* ======================================================
          BRAIN VIEWERS
          ====================================================== */}

      <section className="brain-viewers">


        {/* ====================================================
            NORMAL BRAIN
            ==================================================== */}

        <article className="brain-card">

          <div className="brain-card-header">

            <div>

              <span className="brain-label">
                REFERENCE ANATOMY
              </span>

              <h2>
                Normal Brain
              </h2>

              <p>
                Anatomical reference model
              </p>

            </div>


            <span className="brain-chip">
              Reference
            </span>

          </div>


          <div className="brain-canvas">

            <ReferenceBrain
              color={
                normalColor
              }
              opacity={
                normalOpacity
              }
              autoRotate={
                normalAutoRotate
              }
              resetToken={
                normalResetToken
              }
            />


            <div className="viewer-controls">

              <span>
                🖱 Drag
              </span>

              <span>
                ↕ Scroll
              </span>

              {normalAutoRotate && (
                <span>
                  ◌ Auto
                </span>
              )}

            </div>

          </div>


          {/* ==================================================
              NORMAL CONTROLS
              ================================================== */}

          <div className="reference-controls">

            <div className="control-heading">

              <div>

                <span className="brain-label">
                  VIEW CONTROLS
                </span>

                <h3>
                  Reference appearance
                </h3>

              </div>


              <button
                type="button"
                className="small-control"
                onClick={
                  resetNormalView
                }
              >
                Reset View
              </button>

            </div>


            <div className="color-row">

              <span>
                Brain tone
              </span>


              <div className="color-options">

                {Object.entries(
                  BRAIN_COLORS
                ).map(
                  ([
                    name,
                    color,
                  ]) => (

                    <button
                      key={
                        name
                      }
                      type="button"
                      className={
                        `color-option ${
                          normalColor ===
                          color
                            ? "selected"
                            : ""
                        }`
                      }
                      onClick={() =>
                        setNormalColor(
                          color
                        )
                      }
                      title={
                        name
                      }
                      aria-label={
                        `Use ${name} brain tone`
                      }
                    >

                      <span
                        style={{
                          backgroundColor:
                            color,
                        }}
                      />

                      {name}

                    </button>

                  )
                )}

              </div>

            </div>


            <div className="control-row">

              <div>

                <span>
                  Brain transparency
                </span>

                <small>
                  {Math.round(
                    normalOpacity *
                      100
                  )}%
                </small>

              </div>


              <input
                type="range"
                min="0.45"
                max="1"
                step="0.01"
                value={
                  normalOpacity
                }
                onChange={(
                  event
                ) =>
                  setNormalOpacity(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>


            <div className="reference-action-row">

              <button
                type="button"
                className={
                  `secondary-control ${
                    normalAutoRotate
                      ? "control-active"
                      : ""
                  }`
                }
                onClick={() =>
                  setNormalAutoRotate(
                    (value) =>
                      !value
                  )
                }
              >
                {normalAutoRotate
                  ? "◉ Auto Rotate On"
                  : "○ Auto Rotate Off"}
              </button>


              <button
                type="button"
                className="secondary-control"
                onClick={
                  resetNormalView
                }
              >
                Reset Position
              </button>

            </div>

          </div>

        </article>


        {/* ====================================================
            TUMOR BRAIN
            ==================================================== */}

        <article className="brain-card tumor-card">

          <div className="brain-card-header">

            <div>

              <span className="brain-label red-label">
                AI VISUALIZATION
              </span>

              <h2>
                Brain with Tumor
              </h2>

              <p>
                Interactive illustrative region
              </p>

            </div>


            <span className="brain-chip red-chip">
              ● AI Region
            </span>

          </div>


          <div className="brain-canvas">

            <InteractiveBrain
              color={
                tumorBrainColor
              }
              opacity={
                tumorBrainOpacity
              }
              autoRotate={
                tumorAutoRotate
              }
              tumorVisible={
                tumorVisible
              }
              tumorPosition={
                tumorPosition
              }
              tumorSize={
                tumorSize
              }
              tumorOpacity={
                tumorOpacity
              }
              tumorLocked={
                tumorLocked
              }
              onTumorPlace={
                setTumorPosition
              }
              resetToken={
                tumorResetToken
              }
            />


            {tumorVisible && (
              <div className="tumor-floating-label">

                <span>
                  ●
                </span>

                Illustrative lesion

              </div>
            )}


            {tumorLocked && (
              <div className="lock-floating-label">
                🔒 Marker locked
              </div>
            )}


            <div className="viewer-controls">

              <span>
                🖱 Drag
              </span>

              <span>
                ↕ Scroll
              </span>

              {!tumorLocked && (
                <span>
                  Click brain → move marker
                </span>
              )}

            </div>

          </div>


          {/* ==================================================
              TUMOR CONTROLS
              ================================================== */}

          <div className="tumor-controls">

            <div className="control-heading">

              <div>

                <span className="brain-label red-label">
                  TUMOR VISUALIZATION
                </span>

                <h3>
                  Interactive Marker
                </h3>

              </div>


              <button
                type="button"
                className={
                  `toggle ${
                    tumorVisible
                      ? "toggle-active"
                      : ""
                  }`
                }
                onClick={() =>
                  setTumorVisible(
                    (value) =>
                      !value
                  )
                }
                aria-label="Toggle tumor marker"
              >

                <span />

              </button>

            </div>


            {/* =================================================
                INDEPENDENT BRAIN APPEARANCE
                ================================================= */}

            <div className="tumor-appearance">

              <div className="appearance-title">

                <span className="brain-label red-label">
                  BRAIN APPEARANCE
                </span>

                <span>
                  Independent controls
                </span>

              </div>


              <div className="color-options tumor-color-options">

                {Object.entries(
                  BRAIN_COLORS
                ).map(
                  ([
                    name,
                    color,
                  ]) => (

                    <button
                      key={
                        `tumor-${name}`
                      }
                      type="button"
                      className={
                        `color-option tumor-color-option ${
                          tumorBrainColor ===
                          color
                            ? "selected"
                            : ""
                        }`
                      }
                      onClick={() =>
                        setTumorBrainColor(
                          color
                        )
                      }
                      title={
                        name
                      }
                      aria-label={
                        `Use ${name} tumor brain tone`
                      }
                    >

                      <span
                        style={{
                          backgroundColor:
                            color,
                        }}
                      />

                      {name}

                    </button>

                  )
                )}

              </div>


              <div className="control-row tumor-brain-opacity">

                <div>

                  <span>
                    Brain transparency
                  </span>

                  <small>
                    {Math.round(
                      tumorBrainOpacity *
                        100
                    )}%
                  </small>

                </div>


                <input
                  type="range"
                  min="0.45"
                  max="1"
                  step="0.01"
                  value={
                    tumorBrainOpacity
                  }
                  onChange={(
                    event
                  ) =>
                    setTumorBrainOpacity(
                      Number(
                        event.target.value
                      )
                    )
                  }
                />

              </div>

            </div>


            {/* =================================================
                LOCK
                ================================================= */}

            <div className="lock-row">

              <div>

                <strong>
                  Marker position
                </strong>

                <small>
                  {tumorLocked
                    ? "Position locked"
                    : "Click the brain to reposition"}
                </small>

              </div>


              <button
                type="button"
                className={
                  `lock-button ${
                    tumorLocked
                      ? "locked"
                      : ""
                  }`
                }
                onClick={() =>
                  setTumorLocked(
                    (value) =>
                      !value
                  )
                }
              >

                {tumorLocked
                  ? "🔒 Release"
                  : "🔓 Lock Position"}

              </button>

            </div>


            {/* =================================================
                TUMOR OPACITY
                ================================================= */}

            <div className="control-row">

              <div>

                <span>
                  Marker opacity
                </span>

                <small>
                  {Math.round(
                    tumorOpacity *
                      100
                  )}%
                </small>

              </div>


              <input
                type="range"
                min="0.2"
                max="1"
                step="0.01"
                value={
                  tumorOpacity
                }
                onChange={(
                  event
                ) =>
                  setTumorOpacity(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>


            {/* =================================================
                TUMOR SIZE
                ================================================= */}

            <div className="control-row">

              <div>

                <span>
                  Marker size
                </span>

                <small>
                  {tumorSize.toFixed(
                    2
                  )}
                </small>

              </div>


              <input
                type="range"
                min="0.12"
                max="0.48"
                step="0.01"
                value={
                  tumorSize
                }
                onChange={(
                  event
                ) =>
                  setTumorSize(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>


            {/* =================================================
                MARKER ACTIONS
                ================================================= */}

            <div className="tumor-action-row">

              <button
                type="button"
                className="secondary-control"
                onClick={
                  clearTumor
                }
                disabled={
                  tumorLocked
                }
              >
                Clear Marker
              </button>


              <button
                type="button"
                className="primary-control"
                onClick={
                  autoPlaceTumor
                }
                disabled={
                  tumorLocked
                }
              >
                ✦ Auto Place
              </button>

            </div>


            {/* =================================================
                TUMOR VIEW ACTIONS
                ================================================= */}

            <div className="reference-action-row">

              <button
                type="button"
                className={
                  `secondary-control ${
                    tumorAutoRotate
                      ? "control-active-red"
                      : ""
                  }`
                }
                onClick={() =>
                  setTumorAutoRotate(
                    (value) =>
                      !value
                  )
                }
              >

                {tumorAutoRotate
                  ? "◉ Auto Rotate On"
                  : "○ Auto Rotate Off"}

              </button>


              <button
                type="button"
                className="secondary-control"
                onClick={
                  resetTumorView
                }
              >
                Reset View
              </button>

            </div>


            <p className="click-help">

              {tumorLocked
                ? "Release the marker to choose another position."
                : "Click directly on the brain surface to reposition the marker."}

            </p>

          </div>

        </article>

      </section>


      {/* ======================================================
          PIPELINE OUTPUT
          ====================================================== */}

      <section className="brain-analysis">

        <div className="analysis-heading">

          <div>

            <span className="brain-label">
              PIPELINE OUTPUT
            </span>

            <h2>
              Current AI Analysis
            </h2>

            <p>
              Read-only information from
              the MedFusion analysis pipeline.
            </p>

          </div>


          <div className="analysis-status">

            <span />

            Read-only analysis

          </div>

        </div>


        <div className="brain-data-grid">

          <DataCard
            label="Scan Type"
            value={
              data.scanType
            }
            accent="blue"
          />


          <DataCard
            label="Detection"
            value={
              tumorStatus
            }
            accent={
              data.tumorDetected
                ? "red"
                : "green"
            }
          />


          <DataCard
            label="Tumor Type"
            value={
              data.tumorType ||
              "Not classified"
            }
            accent="purple"
          />


          <DataCard
            label="Detection Confidence"
            value={
              formatPercent(
                data.detectionConfidence
              )
            }
            accent="green"
          />


          <DataCard
            label="Classification Confidence"
            value={
              formatPercent(
                data.classificationConfidence
              )
            }
            accent="blue"
          />


          <DataCard
            label="Segmentation Confidence"
            value={
              formatPercent(
                data.segmentationConfidence
              )
            }
            accent="green"
          />


          <DataCard
            label="Tumor Area"
            value={
              formatNumber(
                data.tumorArea,
                " px"
              )
            }
            accent="cyan"
          />


          <DataCard
            label="Image Coverage"
            value={
              formatPercent(
                data.tumorPercentage
              )
            }
            accent="cyan"
          />


          <DataCard
            label="Width"
            value={
              formatNumber(
                data.width,
                " px"
              )
            }
            accent="blue"
          />


          <DataCard
            label="Height"
            value={
              formatNumber(
                data.height,
                " px"
              )
            }
            accent="blue"
          />

        </div>


        {(data.boundingBox ||
          data.centroid) && (

          <div className="technical-info">

            <div>

              <span>
                TECHNICAL INFORMATION
              </span>

              <strong>
                Segmentation geometry
              </strong>

            </div>


            {data.boundingBox && (
              <div className="technical-value">

                Bounding box:

                {" "}

                ({data.boundingBox.x_min},

                {" "}

                {data.boundingBox.y_min})

                {" → "}

                ({data.boundingBox.x_max},

                {" "}

                {data.boundingBox.y_max})

              </div>
            )}


            {data.centroid && (
              <div className="technical-value">

                Centroid:

                {" "}

                X {data.centroid.x}

                {" · "}

                Y {data.centroid.y}

              </div>
            )}

          </div>
        )}

      </section>


      {/* ======================================================
          INFORMATION
          ====================================================== */}

      <section className="brain-bottom-grid">

        <div className="bottom-card">

          <div className="bottom-icon">
            ◇
          </div>

          <div>

            <span className="brain-label">
              INTERACTION
            </span>

            <h3>
              Explore the anatomy
            </h3>

            <p>
              Rotate, zoom, change the brain
              appearance and adjust transparency.
              The two visualization panels operate
              independently.
            </p>

          </div>

        </div>


        <div className="bottom-card">

          <div className="bottom-icon red-bottom-icon">
            ●
          </div>

          <div>

            <span className="brain-label red-label">
              VISUALIZATION NOTE
            </span>

            <h3>
              Illustrative lesion marker
            </h3>

            <p>
              The irregular red marker provides
              an intuitive educational representation
              of a reported region. It should not be
              interpreted as a reconstructed tumor volume.
            </p>

          </div>

        </div>

      </section>


      {/* ======================================================
          FOOTER
          ====================================================== */}

      <footer className="brain-footer">

        <span>
          MedFusion AI · 3D Brain Visualization
        </span>

        <span>
          Educational demonstration · Not a medical device
        </span>

      </footer>

    </main>
  );
}


// ============================================================
// PRELOAD
// ============================================================

useGLTF.preload(
  MODEL_PATH
);


export default App;