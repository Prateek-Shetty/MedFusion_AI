// ============================================================
// MEDFUSION API SERVICE
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


// ============================================================
// COMPLETE ANALYSIS
// ============================================================

export async function analyzeScan({
  file,
  age,
  gender,
  location,
}) {
  if (!file) {
    throw new Error("Please select a scan.");
  }

  const formData = new FormData();

  formData.append("file", file);
  formData.append("age", String(age));
  formData.append("sex_category", gender);

  if (location) {
    formData.append(
      "latitude",
      String(location.latitude)
    );

    formData.append(
      "longitude",
      String(location.longitude)
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/analysis/full`,
    {
      method: "POST",
      body: formData,
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The backend returned an invalid response."
    );
  }

  if (!response.ok) {
    const detail =
      typeof data?.detail === "string"
        ? data.detail
        : "Analysis failed.";

    throw new Error(detail);
  }

  return data;
}


// ============================================================
// CHATBOT
// ============================================================
//
// analysisContext is optional.
//
// This allows:
// - normal general questions
// - scan-aware questions
// - MRI context
// - CT context with missing Model 3
//
// ============================================================

// ============================================================
// CHATBOT
// ============================================================

export async function sendChatMessage(
  message,
  analysisContext = null
) {
  const cleanedMessage =
    String(message || "").trim();

  if (!cleanedMessage) {
    throw new Error(
      "Please enter a message."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/chat`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message: cleanedMessage,
        analysis_context: analysisContext,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The chatbot returned an invalid response."
    );
  }

  if (!response.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      "Chatbot request failed.";

    console.error(
      "Chatbot backend error:",
      data
    );

    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail)
    );
  }

  return data;
}


// ============================================================
// API BASE URL
// ============================================================

export {
  API_BASE_URL,
};