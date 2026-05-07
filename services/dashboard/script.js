const API_BASE_URL = window.DASHBOARD_API_BASE_URL || "http://localhost:5001";
const TREND_DATA_URL = `${API_BASE_URL}/api/latest-trends`;
const EXAMPLE_POSTS_URL = `${API_BASE_URL}/api/latest-examples`;
const REFRESH_MS = 5000;

async function loadTrends() {
  const status = document.getElementById("status");

  try {
    const [trendResponse, exampleResponse] = await Promise.all([
      fetch(`${TREND_DATA_URL}?t=${Date.now()}`),
      fetch(`${EXAMPLE_POSTS_URL}?t=${Date.now()}`),
    ]);

    if (!trendResponse.ok) {
      throw new Error(`trends HTTP ${trendResponse.status}`);
    }

    if (!exampleResponse.ok) {
      throw new Error(`examples HTTP ${exampleResponse.status}`);
    }

    const trendPayload = await trendResponse.json();
    const examplePayload = await exampleResponse.json();

    const latest = latestSnapshotFrom(trendPayload);
    const latestExamples = latestSnapshotFrom(examplePayload);

    if (!latest) {
      status.textContent = "No trend snapshots saved yet.";
      return;
    }

    renderSnapshot(latest);
    renderExamples(latestExamples);

    status.textContent = "Loaded latest snapshot";
  } catch (error) {
    status.textContent = `Could not load trend data: ${error.message}`;
  }
}

function latestSnapshotFrom(payload) {
  if (Array.isArray(payload)) {
    return payload.length > 0 ? payload[payload.length - 1] : null;
  }

  if (payload && typeof payload === "object") {
    return payload;
  }

  return null;
}

function renderSnapshot(snapshot) {
  document.getElementById("postsProcessed").textContent =
    snapshot.posts_processed ?? 0;

  document.getElementById("lastUpdated").textContent =
    formatTimestamp(snapshot.timestamp);

  const trends = snapshot.trends || [];
  const maxCount = Math.max(...trends.map((trend) => trend.count), 1);

  const trendList = document.getElementById("trendList");
  trendList.innerHTML = "";

  for (const trend of trends) {
    const row = document.createElement("div");
    row.className = "trend-row";

    const width = Math.max((trend.count / maxCount) * 100, 4);

    row.innerHTML = `
      <div class="term">${escapeHtml(trend.term)}</div>
      <div class="bar-wrap">
        <div class="bar" style="width: ${width}%"></div>
      </div>
      <div class="count">${trend.count}</div>
    `;

    trendList.appendChild(row);
  }
}

function renderExamples(snapshot) {
  const exampleList = document.getElementById("exampleList");
  exampleList.innerHTML = "";

  if (!snapshot || !Array.isArray(snapshot.examples) || snapshot.examples.length === 0) {
    exampleList.innerHTML = `<div class="empty-state">No example posts saved yet.</div>`;
    return;
  }

  for (const item of snapshot.examples) {
    const examplePost = item.example_post || {};
    const card = document.createElement("article");
    card.className = "example-card";

    card.innerHTML = `
      <div class="example-header">
        <span class="example-term">${escapeHtml(item.term)}</span>
        <span class="example-count">${item.count}</span>
      </div>
      <p class="example-text">${escapeHtml(examplePost.text || "No post text saved.")}</p>
      <div class="example-meta">
        <span>${escapeHtml(examplePost.author || "unknown author")}</span>
        <span>${escapeHtml(formatTimestamp(examplePost.timestamp))}</span>
      </div>
    `;

    exampleList.appendChild(card);
  }
}

function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "Unknown";
  }

  return new Date(timestamp).toLocaleTimeString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadTrends();
setInterval(loadTrends, REFRESH_MS);
