// SmartLogistics AI frontend configuration
const API_BASE = "https://smart-logistics-ai-6hct.onrender.com";

const $ = (selector) => document.querySelector(selector);

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

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg).join(", ")
      : data.detail;

    throw new Error(detail || `Request failed (${response.status})`);
  }

  return data;
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.remove("hidden");

  // Simple timeout for hiding the notification.
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}

function setMessage(selector, message, type = "") {
  const element = $(selector);
  element.textContent = message;
  element.className = `message ${type}`.trim();
}

function setLoading(button, loading, loadingText = "Working...") {
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

function statusClass(status) {
  if (status === "Delivered") return "delivered";
  if (status === "In Transit") return "transit";
  if (status === "Cancelled") return "cancelled";
  return "";
}

// ------------------------------
// API connection
// ------------------------------

async function checkConnection() {
  const status = $("#connection-status");
  const dot = document.querySelector(".sidebar-bottom .status-dot");

  try {
    await apiRequest("/");
    status.textContent = "Connected";
    dot.className = "status-dot online";
  } catch {
    status.textContent = "Disconnected";
    dot.className = "status-dot offline";
  }
}

// ------------------------------
// Dashboard and shipment table
// ------------------------------

async function loadDashboard() {
  const table = $("#shipment-table");

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
      table.innerHTML =
        '<tr><td colspan="5" class="empty">No shipments yet. Create your first booking.</td></tr>';
      return;
    }

    table.innerHTML = recent.map((shipment) => `
      <tr>
        <td><strong>${escapeHTML(shipment.shipment_id)}</strong></td>
        <td>${escapeHTML(shipment.customer)}</td>
        <td>${escapeHTML(shipment.origin)} → ${escapeHTML(shipment.destination)}</td>
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
          Could not load shipments. Check that the Python API is running.
          ${escapeHTML(error.message)}
        </td>
      </tr>
    `;
  }
}

$("#refresh-shipments").addEventListener("click", async () => {
  await loadDashboard();
  showToast("Dashboard refreshed.");
});

// ------------------------------
// Price estimator
// ------------------------------

$("#pricing-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  const data = Object.fromEntries(new FormData(form).entries());

  data.weight_kg = Number(data.weight_kg);

  setLoading(button, true, "Calculating...");

  const result = $("#quote-result");
  result.classList.add("hidden");

  try {
    const response = await apiRequest("/shipments/quote", {
      method: "POST",
      body: JSON.stringify(data)
    });

    const quote = response.quote;

    result.innerHTML = `
      <p class="eyebrow">ESTIMATED DELIVERY PRICE</p>
      <h3>${escapeHTML(quote.origin)} → ${escapeHTML(quote.destination)}</h3>
      <div class="result-price">${money(quote.price_tzs)}</div>
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
        This is a demonstration estimate, not an official commercial tariff.
        No shipment has been booked.
      </p>
    `;

    result.classList.remove("hidden");
  } catch (error) {
    result.textContent = `Unable to calculate price: ${error.message}`;
    result.classList.remove("hidden");
    showToast(error.message);
  } finally {
    setLoading(button, false);
  }
});

// ------------------------------
// Create a shipment
// ------------------------------

$("#booking-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  const data = Object.fromEntries(new FormData(form).entries());

  data.weight_kg = Number(data.weight_kg);

  setMessage("#booking-message", "");
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

// ------------------------------
// Shipment tracking
// ------------------------------

$("#tracking-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  const shipmentId = new FormData(form).get("shipment_id").trim();

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
          <strong>${escapeHTML(shipment.origin)} → ${escapeHTML(shipment.destination)}</strong>
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
        This shows the saved database record, not a live GPS location.
      </p>
    `;

    result.classList.remove("hidden");
  } catch (error) {
    result.textContent = `Shipment lookup failed: ${error.message}`;
    result.classList.remove("hidden");
  } finally {
    setLoading(button, false);
  }
});

// ------------------------------
// Company-policy RAG assistant
// ------------------------------

function addChatBubble(text, type = "assistant") {
  const messages = $("#chat-messages");
  const bubble = document.createElement("div");

  bubble.className = `chat-bubble ${
    type === "user" ? "user-bubble" : "assistant-bubble"
  }`;

  // Use textContent for user-provided text.
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
    paragraph.textContent = `${source.source}: ${source.text}`;
    sourceBlock.appendChild(paragraph);
  }

  bubble.appendChild(sourceBlock);
}

$("#assistant-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  const question = new FormData(form).get("question").trim();

  if (!question) return;

  addChatBubble(question, "user");
  form.elements.question.value = "";

  setLoading(button, true, "Searching...");

  const bubble = addChatBubble("Searching company documents...");

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
    $("#chat-messages").scrollTop = $("#chat-messages").scrollHeight;
  }
});

// ------------------------------
// Navigation and page startup
// ------------------------------

const pageTitles = {
  dashboard: "Dashboard",
  booking: "Book a shipment",
  pricing: "Price estimator",
  tracking: "Track shipment",
  assistant: "AI assistant"
};

function updateNavigation() {
  const current = location.hash.replace("#", "") || "dashboard";

  $("#page-title").textContent = pageTitles[current] || "Dashboard";

  document.querySelectorAll(".nav-link").forEach((link) => {
    const target = link.getAttribute("href").replace("#", "");
    link.classList.toggle("active", target === current);
  });
}

window.addEventListener("hashchange", updateNavigation);

async function startApp() {
  updateNavigation();
  await checkConnection();
  await loadDashboard();
}

startApp();