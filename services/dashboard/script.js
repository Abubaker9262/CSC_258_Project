/*
Description:
This JavaScript code acts as the frontend controller for the live trends dashboard, responsible for fetching, processing, 
and displaying real-time data from the backend API. It communicates with the storage service through REST endpoints to retrieve the latest 
trend snapshots and example posts. The loadTrends function asynchronously fetches data using fetch and ensures both API calls are completed
efficiently using Promise.all. It also prevents caching issues by appending timestamps to requests, ensuring fresh data is always retrieved. 
The code processes API responses and extracts the most recent snapshot using a helper function, maintaining compatibility with different payload formats.
It dynamically updates the DOM by rendering trend rankings, frequency bars, and example posts with contextual information. 
Error handling is implemented to manage failed API calls and provide user feedback. Additionally, helper functions like formatTimestamp and escapeHtml
improve data presentation and security by formatting time and preventing HTML injection. The dashboard automatically refreshes at regular intervals,
ensuring continuous real-time updates. Overall, this script enables an interactive and responsive visualization layer for the distributed Kafka-based data pipeline.
*/

const API_BASE_URL = window.DASHBOARD_API_BASE_URL || "http://localhost:5001"; // Sets the API base URL, using a custom browser value if available, otherwise localhost
const TREND_DATA_URL = `${API_BASE_URL}/api/latest-trends`; // Builds the API endpoint URL for latest trend data
const EXAMPLE_POSTS_URL = `${API_BASE_URL}/api/latest-examples`; // Builds the API endpoint URL for latest example posts
const REFRESH_MS = 5000; // Sets dashboard refresh interval to 5 seconds

async function loadTrends() { // Defines async function to load trend and example data
  const status = document.getElementById("status"); // Gets the status message element from the page

  try { // Starts error-handling block
    const [trendResponse, exampleResponse] = await Promise.all([ // Fetches trends and examples at the same time
      fetch(`${TREND_DATA_URL}?t=${Date.now()}`), // Fetches trend data with timestamp to avoid caching
      fetch(`${EXAMPLE_POSTS_URL}?t=${Date.now()}`), // Fetches example post data with timestamp to avoid caching
    ]);

    if (!trendResponse.ok) { // Checks if trend API response failed
      throw new Error(`trends HTTP ${trendResponse.status}`); // Throws error with trend HTTP status
    }

    if (!exampleResponse.ok) { // Checks if examples API response failed
      throw new Error(`examples HTTP ${exampleResponse.status}`); // Throws error with examples HTTP status
    }

    const trendPayload = await trendResponse.json(); // Converts trend response into JSON
    const examplePayload = await exampleResponse.json(); // Converts example response into JSON

    const latest = latestSnapshotFrom(trendPayload); // Extracts latest trend snapshot
    const latestExamples = latestSnapshotFrom(examplePayload); // Extracts latest example snapshot

    if (!latest) { // Checks if no trend snapshot exists
      status.textContent = "No trend snapshots saved yet."; // Shows no-data message
      return; // Stops function execution
    }

    renderSnapshot(latest); // Displays latest trend snapshot on dashboard
    renderExamples(latestExamples); // Displays latest example posts on dashboard

    status.textContent = "Live"; // Updates status to live
  } catch (error) { // Handles any error from fetch/parsing/rendering
    status.textContent = `Could not load trend data: ${error.message}`; // Shows error message on dashboard
  }
}

function latestSnapshotFrom(payload) { // Defines helper function to get latest snapshot
  if (Array.isArray(payload)) { // Checks if payload is an array
    return payload.length > 0 ? payload[payload.length - 1] : null; // Returns last item if array has data, otherwise null
  }

  if (payload && typeof payload === "object") { // Checks if payload is a valid object
    return payload; // Returns object directly
  }

  return null; // Returns null for invalid/empty payload
}

function renderSnapshot(snapshot) { // Defines function to render trend snapshot
  document.getElementById("postsProcessed").textContent = // Gets posts processed element and sets its text
    snapshot.posts_processed ?? 0; // Uses posts_processed value or 0 if missing

  document.getElementById("lastUpdated").textContent = // Gets last updated element and sets its text
    formatTimestamp(snapshot.timestamp); // Formats snapshot timestamp

  const trends = snapshot.trends || []; // Gets trends list or empty list
  const maxCount = Math.max(...trends.map((trend) => trend.count), 1); // Finds highest count for bar scaling

  const trendList = document.getElementById("trendList"); // Gets trend list container
  trendList.innerHTML = ""; // Clears old trends before rendering new ones

  trends.forEach((trend, index) => { // Loops through each trend
    const row = document.createElement("div"); // Creates a new row element
    row.className = "trend-row"; // Assigns CSS class to row

    const width = Math.max((trend.count / maxCount) * 100, 4); // Calculates bar width percentage

    row.innerHTML = ` 
      <div class="rank">${index + 1}</div>
      <div class="term">${escapeHtml(trend.term)}</div>
      <div class="bar-wrap">
        <div class="bar" style="width: ${width}%"></div>
      </div>
      <div class="count">${trend.count}</div>
    `; // Creates HTML for rank, term, bar, and count

    trendList.appendChild(row); // Adds row to trend list
  });
}

function renderExamples(snapshot) { // Defines function to render example posts
  const exampleList = document.getElementById("exampleList"); // Gets example list container
  exampleList.innerHTML = ""; // Clears old examples

  if (!snapshot || !Array.isArray(snapshot.examples) || snapshot.examples.length === 0) { // Checks if examples are missing or empty
    exampleList.innerHTML = `<div class="empty-state">No example posts saved yet.</div>`; // Shows empty message
    return; // Stops function
  }

  for (const item of snapshot.examples) { // Loops through example items
    const examplePost = item.example_post || {}; // Gets example post object or empty object
    const card = document.createElement("article"); // Creates article card element
    card.className = "example-card"; // Assigns CSS class to card

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
    `; // Creates HTML for example post card

    exampleList.appendChild(card); // Adds card to example list
  }
}

function formatTimestamp(timestamp) { // Defines timestamp formatting function
  if (!timestamp) { // Checks if timestamp is missing
    return "Unknown"; // Returns fallback text
  }

  return new Date(timestamp).toLocaleTimeString(); // Converts timestamp to local time string
}

function escapeHtml(value) { // Defines helper to escape unsafe HTML characters
  return String(value) // Converts value to string
    .replaceAll("&", "&amp;") // Escapes ampersand
    .replaceAll("<", "&lt;") // Escapes less-than
    .replaceAll(">", "&gt;") // Escapes greater-than
    .replaceAll('"', "&quot;") // Escapes double quote
    .replaceAll("'", "&#039;"); // Escapes single quote
}

loadTrends(); // Loads data immediately when page opens
setInterval(loadTrends, REFRESH_MS); // Reloads data every 5 seconds
