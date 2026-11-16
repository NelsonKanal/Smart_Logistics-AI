
// ============================================
// SMARTLOGISTICS AI - FRONTEND APPLICATION
// ============================================

// API configuration
const API_BASE = "https://smart-logistics-ai-6hct.onrender.com";

const $ = (selector) => document.querySelector(selector);

// ============================================
// GENERAL HELPERS
// ============================================

const money = (value) =>
  `TZS ${Number(value).toLocaleString("en-TZ")}`;

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function showToast(message) {
  const toast = $("#toast");

  if (!toast) return;

  toast.textContent = message;
  toast.classList.remove("hidden");

  window.clearTimeout(showToast.timer);

  showToast.timer = window.setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}

function setMessage(selector, message, type = "") {
  const element = $(selector);

  if (!element) return;

  element.textContent = message;
  element.className = `message ${type}`.trim();
}

function setLoading(button, loading, loadingText = "Working...") {
  if (!button) return;

  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
  } else {
    button.textContent =
      button.dataset.originalText || button.textContent;

    button.disabled = false;
  }
}

function statusClass(status) {
  if (status === "Delivered") return "delivered";
  if (status === "In Transit") return "transit";
  if (status === "Cancelled") return "cancelled";

  return "";
}

// ============================================
// API REQUEST HANDLER
// ============================================

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  // Attach JWT authentication token
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  const contentType = response.headers.get("content-type");

  const data = contentType?.includes("application/json")
    ? await response.json()
    : await response.text();

  if (response.status === 401) {
    console.error("Authentication required or session expired.");
  }

  if (!response.ok) {
    const detail =
      typeof data === "object"
        ? data.detail
        : data;

    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : detail;

    throw new Error(
      message || `Request failed (${response.status})`
    );
  }

  return data;
}

// ============================================
// AUTHENTICATION
// ============================================

// Login using the FastAPI /auth/login endpoint
async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      password
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  // Save the JWT token and user information
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));

  showToast(`Welcome, ${data.user.full_name}!`);

  return data.user;
}

// Register a new customer
async function registerUser(fullName, email, password) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      full_name: fullName,
      email,
      password
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));

  showToast("Account created successfully.");

  return data.user;
}

// Get current authenticated user
async function getCurrentUser() {
  return await apiRequest("/auth/me");
}

// Logout
function logoutUser() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");

  location.reload();
}

// Make authentication functions available to the HTML interface
window.loginUser = loginUser;
window.registerUser = registerUser;
window.logoutUser = logoutUser;
window.getCurrentUser = getCurrentUser;

// ============================================
// API CONNECTION
// ============================================

async function checkConnection() {
  const status = $("#connection-status");
  const dot = document.querySelector(".sidebar-bottom .status-dot");

  try {
    await apiRequest("/");

    if (status) status.textContent = "Connected";
    if (dot) dot.className = "status-dot online";

    return true;
  } catch (error) {
    if (status) status.textContent = "Disconnected";
    if (dot) dot.className = "status-dot offline";

    return false;
  }
}

// ============================================
// DASHBOARD AND SHIPMENT TABLE
// ============================================

async function loadDashboard() {
  const table = $("#shipment-table");

  if (!table) return;

  if (!localStorage.getItem("access_token")) {
    table.innerHTML = `
      <tr>
        <td colspan="5" class="empty">
          Please log in to view shipment information.
        </td>
      </tr>
    `;

    return;
  }

  try {
    const [shipments, overdue] = await Promise.all([
      apiRequest("/shipments/"),
      apiRequest("/shipments/overdue")
    ]);

    $("#total-shipments").textContent = shipments.length;

    $("#transit-shipments").textContent =
      shipments.filter((s) => s.status === "In Transit").length;

    $("#delivered-shipments").textContent =
      shipments.filter((s) => s.status === "Delivered").length;

    $("#overdue-shipments").textContent = overdue.length;

    const recent = [...shipments].slice(0, 8);

    if (!recent.length) {
      table.innerHTML = `
        <tr>
          <td colspan="5" class="empty">
            No shipments yet. Create your first booking.
          </td>
        </tr>
      `;

      return;
    }

    table.innerHTML = recent.map((shipment) => `
      <tr>
        <td>
          <strong>${escapeHTML(shipment.shipment_id)}</strong>
        </td>

        <td>${escapeHTML(shipment.customer)}</td>

        <td>
          ${escapeHTML(shipment.origin)}
          →
          ${escapeHTML(shipment.destination)}
        </td>

        <td>${money(shipment.price_tzs)}</td>

        <td>
          <span class="status-pill ${statusClass(shipment.status)}">
            ${escapeHTML(shipment.status)}
          </span>
        </td>
      </tr>
    `).join("");

  } catch (error) {
    table.innerHTML = `
      <tr>
        <td colspan="5" class="empty">
          Could not load shipments: ${escapeHTML(error.message)}
        </td>
      </tr>
    `;

    if (error.message.includes("401")) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
  }
}

// Refresh dashboard
$("#refresh-shipments")?.addEventListener("click", async () => {
  await loadDashboard();
  showToast("Dashboard refreshed.");
});

// ============================================
// PRICE ESTIMATOR
// ============================================

$("#pricing-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');

  const data = Object.fromEntries(
    new FormData(form).entries()
  );

  data.weight_kg = Number(data.weight_kg);

  setLoading(button, true, "Calculating...");

  const result = $("#quote-result");

  if (result) result.classList.add("hidden");

  try {
    const response = await apiRequest("/shipments/quote", {
      method: "POST",
      body: JSON.stringify(data)
    });

    const quote = response.quote;

    result.innerHTML = `
      <p class="eyebrow">ESTIMATED DELIVERY PRICE</p>

      <h3>
        ${escapeHTML(quote.origin)}
        →
        ${escapeHTML(quote.destination)}
      </h3>

      <div class="result-price">
        ${money(quote.price_tzs)}
      </div>

      <div class="result-grid">
        <div class="result-item">
          <span>Parcel weight</span>
          <strong>${escapeHTML(quote.weight_kg)} kg</strong>
        </div>

        <div class="result-item">
          <span>Estimated distance</span>
          <strong>${escapeHTML(quote.distance_km)} km</strong>
        </div>

        <div class="result-item">
          <span>Service</span>
          <strong>${escapeHTML(quote.service)}</strong>
        </div>
      </div>

      <p class="fine-print">
        This is a demonstration estimate, not an official
        commercial tariff. No shipment has been booked.
      </p>
    `;

    result.classList.remove("hidden");

  } catch (error) {
    result.textContent =
      `Unable to calculate price: ${error.message}`;

    result.classList.remove("hidden");

    showToast(error.message);

  } finally {
    setLoading(button, false);
  }
});

// ============================================
// CREATE A SHIPMENT
// ============================================

$("#booking-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');

  const data = Object.fromEntries(
    new FormData(form).entries()
  );

  data.weight_kg = Number(data.weight_kg);

  setMessage("#booking-message", "");

  if (!localStorage.getItem("access_token")) {
    setMessage(
      "#booking-message",
      "Please log in before creating a shipment.",
      "error"
    );

    return;
  }

  setLoading(button, true, "Creating booking...");

  try {
    const shipment = await apiRequest("/shipments/", {
      method: "POST",
      body: JSON.stringify(data)
    });

    setMessage(
      "#booking-message",
      `Booked successfully! Shipment ID: ${shipment.shipment_id}. Estimated price: ${money(shipment.price_tzs)}.`,
      "success"
    );

    form.reset();

    showToast(`Shipment ${shipment.shipment_id} created.`);

    await loadDashboard();

  } catch (error) {
    setMessage("#booking-message", error.message, "error");

  } finally {
    setLoading(button, false);
  }
});

// ============================================
// SHIPMENT TRACKING
// ============================================

$("#tracking-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');

  const shipmentId = new FormData(form)
    .get("shipment_id")
    .trim();

  const result = $("#tracking-result");

  result.classList.add("hidden");

  setLoading(button, true, "Searching...");

  try {
    const shipment = await apiRequest(
      `/shipments/${encodeURIComponent(shipmentId)}`
    );

    result.innerHTML = `
      <p class="eyebrow">SHIPMENT RECORD</p>

      <h3>${escapeHTML(shipment.shipment_id)}</h3>

      <div class="result-grid">
        <div class="result-item">
          <span>Customer</span>
          <strong>${escapeHTML(shipment.customer)}</strong>
        </div>

        <div class="result-item">
          <span>Status</span>
          <strong>
            <span class="status-pill ${statusClass(shipment.status)}">
              ${escapeHTML(shipment.status)}
            </span>
          </strong>
        </div>

        <div class="result-item">
          <span>Route</span>
          <strong>
            ${escapeHTML(shipment.origin)}
            →
            ${escapeHTML(shipment.destination)}
          </strong>
        </div>

        <div class="result-item">
          <span>Estimated delivery</span>
          <strong>${escapeHTML(shipment.expected_delivery)}</strong>
        </div>

        <div class="result-item">
          <span>Price</span>
          <strong>${money(shipment.price_tzs)}</strong>
        </div>

        <div class="result-item">
          <span>Service</span>
          <strong>${escapeHTML(shipment.service)}</strong>
        </div>
      </div>

      <p class="fine-print">
        This shows the saved database record,
        not a live GPS location.
      </p>
    `;

    result.classList.remove("hidden");

  } catch (error) {
    result.textContent =
      `Shipment lookup failed: ${error.message}`;

    result.classList.remove("hidden");

  } finally {
    setLoading(button, false);
  }
});

// ============================================
// COMPANY-POLICY RAG ASSISTANT
// ============================================

function addChatBubble(text, type = "assistant") {
  const messages = $("#chat-messages");

  if (!messages) return null;

  const bubble = document.createElement("div");

  bubble.className = `chat-bubble ${
    type === "user" ? "user-bubble" : "assistant-bubble"
  }`;

  bubble.textContent = text;

  messages.appendChild(bubble);

  messages.scrollTop = messages.scrollHeight;

  return bubble;
}

function addAssistantSources(bubble, sources) {
  if (!sources || sources.length === 0) return;

  const sourceBlock = document.createElement("div");

  sourceBlock.className = "source-block";

  const heading = document.createElement("strong");

  heading.textContent = "Retrieved sources";

  sourceBlock.appendChild(heading);

  for (const source of sources) {
    const paragraph = document.createElement("p");

    paragraph.textContent =
      `${source.source}: ${source.text}`;

    sourceBlock.appendChild(paragraph);
  }

  bubble.appendChild(sourceBlock);
}

$("#assistant-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');

  const question = new FormData(form)
    .get("question")
    .trim();

  if (!question) return;

  if (!localStorage.getItem("access_token")) {
    addChatBubble("Please log in to use the AI assistant.");
    return;
  }

  addChatBubble(question, "user");

  form.elements.question.value = "";

  setLoading(button, true, "Searching...");

  const bubble = addChatBubble(
    "Searching company documents..."
  );

  try {
    const response = await apiRequest("/assistant/ask", {
      method: "POST",
      body: JSON.stringify({ question })
    });

    bubble.textContent = response.answer;

    addAssistantSources(bubble, response.sources);

  } catch (error) {
    bubble.textContent =
      `Unable to search company documents: ${error.message}`;

  } finally {
    setLoading(button, false);

    $("#chat-messages").scrollTop =
      $("#chat-messages").scrollHeight;
  }
});

// ============================================
// NAVIGATION
// ============================================

const pageTitles = {
  dashboard: "Dashboard",
  booking: "Book a shipment",
  pricing: "Price estimator",
  tracking: "Track shipment",
  assistant: "AI assistant"
};

function updateNavigation() {
  const current =
    location.hash.replace("#", "") || "dashboard";

  const pageTitle = $("#page-title");

  if (pageTitle) {
    pageTitle.textContent =
      pageTitles[current] || "Dashboard";
  }

  document.querySelectorAll(".nav-link").forEach((link) => {
    const target = link.getAttribute("href").replace("#", "");

    link.classList.toggle("active", target === current);
  });
}

window.addEventListener("hashchange", updateNavigation);

// ============================================
// APPLICATION STARTUP
// ============================================


async function startApp() {
  updateNavigation();

  await checkConnection();
  await updateAccountInterface();

  if (localStorage.getItem("access_token")) {
    await loadDashboard();
  } else {
    await loadDashboard();
  }
}

startApp();



// ============================================
// LOGIN AND REGISTRATION INTERFACE
// ============================================

async function updateAccountInterface() {
  const status = document.querySelector("#account-status");
  const logoutButton = document.querySelector("#logout-button");
  const token = localStorage.getItem("access_token");

  if (!token) {
    if (status) {
      status.textContent = "You are not logged in. Please log in to book shipments.";
    }

    if (logoutButton) logoutButton.classList.add("hidden");
    return;
  }

  try {
    const user = await getCurrentUser();

    if (status) {
      status.textContent =
        `Logged in as ${user.full_name} (${user.email})`;
    }

    if (logoutButton) logoutButton.classList.remove("hidden");

  } catch (error) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    if (status) {
      status.textContent = "Your session has expired. Please log in again.";
    }

    if (logoutButton) logoutButton.classList.add("hidden");
  }
}

// Login form
document.querySelector("#login-form")?.addEventListener(
  "submit",
  async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const values = Object.fromEntries(new FormData(form));

    setLoading(button, true, "Logging in...");

    try {
      await loginUser(values.email, values.password);

      setMessage("#login-message", "Login successful!", "success");

      await updateAccountInterface();
      await loadDashboard();

      location.hash = "#dashboard";

    } catch (error) {
      setMessage("#login-message", error.message, "error");

    } finally {
      setLoading(button, false);
    }
  }
);

// Registration form
document.querySelector("#register-form")?.addEventListener(
  "submit",
  async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const values = Object.fromEntries(new FormData(form));

    setLoading(button, true, "Creating account...");

    try {
      await registerUser(
        values.full_name,
        values.email,
        values.password
      );

      setMessage(
        "#register-message",
        "Account created and logged in successfully!",
        "success"
      );

      await updateAccountInterface();
      await loadDashboard();

      location.hash = "#dashboard";

    } catch (error) {
      setMessage("#register-message", error.message, "error");

    } finally {
      setLoading(button, false);
    }
  }
);

// Logout
document.querySelector("#logout-button")?.addEventListener(
  "click",
  () => {
    logoutUser();
  }
);
