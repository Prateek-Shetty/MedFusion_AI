# Model 5 — Clinical Decision Support & Reporting System

## 1. Overview

Model 5 is the clinical decision-support and structured reporting component of the project.

Its purpose is to take validated clinical information and outputs from Model 4A and produce structured, rule-based clinical reporting information.

Model 5 is **not an autonomous diagnostic or prescription system**.

The intended architecture is:

MRI
→ Model 4A
→ Tumor segmentation and measurements
→ Model 5
→ Clinical rules + structured report
→ [Later] Gemini API
→ Natural-language report

---

## 2. Model 5 Responsibilities

Model 5 currently provides:

- Clinical feature engineering
- Experimental WHO-grade classification
- Clinical knowledge/rules layer
- Deterministic rule engine
- Structured clinical-style reporting
- Specialist recommendation categories
- Recommended next-step categories
- Follow-up categories
- Safety and limitation statements

---

## 3. Experimental WHO-Grade Classifier

### Model

`models/Model5_WHO_Grade_Classifier.joblib`

### Target

WHO grade:

- Grade I
- Grade II
- Grade III

### Features used

- Age
- Sex category
- Voxel X resolution
- Voxel Y resolution
- Slice thickness
- MRI field strength
- Field-strength category
- Resolution category
- Slice-thickness category

### Training data

The available BraTS-MEN-RT clinical metadata contained:

- 570 records
- 271 records with available WHO grade

Distribution:

- WHO Grade I: 169
- WHO Grade II: 85
- WHO Grade III: 17

### Validation

The classifier was evaluated using stratified cross-validation.

Observed performance:

- Accuracy: approximately 54.61%
- Balanced accuracy: approximately 40.01%
- Macro F1: approximately 39.41%

### Important status

The classifier was assessed as:

**INSUFFICIENT**

Therefore, it must **not** be presented as a reliable clinical predictor.

It is retained only as an experimental/research component.

---

## 4. Clinical Knowledge / Rules Layer

The deterministic knowledge base is:

`knowledge/model5_clinical_rules_v1.json`

This layer contains structured clinical reporting rules and tumor-specific information used by the Model 5 rule engine.

It is intentionally separated from the experimental WHO-grade classifier.

---

## 5. Rule Engine

The rule engine converts validated inputs into structured outputs such as:

### Recommendation category

Examples:

- `segmented_tumor_present`
- `no_segmented_tumor_detected`

### Recommended specialist categories

Depending on validated tumor context and segmentation findings, the system may provide categories such as:

- Neurosurgery
- Neuro-oncology
- Endocrinology
- Neuroradiology

### Recommended next steps

Examples include:

- Specialist review
- Clinical neurological evaluation
- Radiology review
- Endocrine evaluation
- Clinical and radiological correlation

### Follow-up

Follow-up remains clinician-determined.

The system does not independently determine a patient-specific follow-up schedule.

---

## 6. Model 4A Integration

Model 5 is designed to consume Model 4A-derived measurements such as:

- Tumor detected
- Tumor area
- Tumor area percentage
- Tumor width
- Tumor height
- Bounding box
- Centroid
- Boundary pixels
- Segmentation confidence

The actual Model 4A → Model 5 input pipeline is intentionally deferred to the final application integration phase.

---

## 7. Safety Restrictions

The following are intentionally disabled:

- Autonomous diagnosis
- Autonomous prescription
- Medication generation
- Drug dosage generation
- Drug frequency generation
- Drug duration generation
- Autonomous treatment planning
- Unsupported emergency classification

The system must not transform:

- Tumor type → medication
- Tumor size → medication
- WHO grade → medication
- MRI measurements → medication

without validated treatment/prescription data.

---

## 8. Prescription Capability

A validated prescription dataset was not available in the datasets audited during development.

Therefore Model 5 does **not** contain a trained prescription model.

Specifically, it does not predict:

- Specific medication
- Drug dosage
- Drug frequency
- Drug duration

This is intentional and should remain documented as a project limitation.

---

## 9. Gemini Integration

Gemini is **not embedded into the trained Model 5 model**.

Gemini integration is planned for the final application layer.

The relevant files are:

`knowledge/model5_gemini_report_contract_v1.json`

`knowledge/model5_gemini_system_prompt_v1.txt`

The planned architecture is:

Model 4A
→ Model 5 structured output
→ Gemini
→ Human-readable report

Gemini should only receive validated structured information.

It must not invent:

- Patient history
- Pathology
- Laboratory results
- Imaging findings
- Diagnosis
- Medication
- Dosage
- Treatment decisions

---

## 10. Reports and Results

Important generated files include:

### Model evaluation

`results/model5_who_grade_test_predictions.csv`

`results/model5_feature_importance.csv`

`results/model5_step8b_cv_fold_results.csv`

`results/model5_step8b_cv_summary.csv`

`results/model5_step8b_oof_predictions.csv`

### Rule-engine testing

`results/step9a_rules_validation.json`

`results/step9b_sample_structured_reports.json`

`results/step9b_rule_engine_test_results.csv`

### End-to-end reporting

`results/step10_gemini_input_payload.json`

`reports/step10_structured_report.json`

---

## 11. Auditing

Model 5 contains audit records documenting:

- Project initialization
- Clinical rules
- Rule-engine tests
- Gemini contract
- End-to-end integration
- Model validation

These files are stored under:

`audit/`

They should be retained for reproducibility and project documentation.

---

## 12. Important Limitation

Model 5 is a **research prototype**.

It should not be used as a standalone clinical decision-maker.

Model 4A segmentation does not establish a definitive diagnosis.

Tumor type must come from an established/validated source rather than being assumed solely from segmentation.

All clinical interpretation and decisions require qualified healthcare-professional review.

---

## 13. Final Model 5 Architecture

```text
                 MRI
                  |
                  v
              MODEL 4A
                  |
                  v
       Tumor Segmentation
                  |
                  v
       Tumor Measurements
                  |
                  v
              MODEL 5
        +-------------------+
        | Clinical Features |
        | Rule Engine        |
        | Knowledge Base     |
        | Reporting Layer    |
        +---------+----------+
                  |
                  v
        Structured Report
                  |
                  v
        [Future Application]
                  |
                  v
               Gemini
                  |
                  v
       Human-readable Report
```

---

## 14. Project Status

### Completed

- Project initialization
- Dataset and clinical-label audit
- Clinical metadata acquisition
- Clinical feature engineering
- WHO-grade classifier training
- Cross-validation
- Clinical knowledge base
- Rule engine
- Safety validation
- Structured report generation
- Gemini input/output contract
- End-to-end rule/report testing
- Final Model 5 packaging

### Deferred

- Model 4A live integration
- Real-image end-to-end testing
- Gemini API integration
- Final application/UI

These belong to the final system implementation phase.

---

## 15. Main Model File

The trained Model 5 classifier is:

`models/Model5_WHO_Grade_Classifier.joblib`

Remember that this classifier is experimental and has insufficient performance for clinical prediction.

The deterministic knowledge/rules layer is equally important for the reporting component.

---

## 16. Version

Model 5:

**Clinical Decision Support + Reporting System**

Current rule/knowledge version:

**v1.0**

Status:

**Research / Prototype — Clinician Review Required**
