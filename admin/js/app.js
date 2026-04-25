let authHeader = "";

// Login
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  authHeader = "Basic " + btoa(username + ":" + password);

  try {
    const res = await fetch("/api/stats", { headers: { Authorization: authHeader } });
    if (res.ok) {
      document.getElementById("login-screen").style.display = "none";
      document.getElementById("dashboard").style.display = "block";
      localStorage.setItem("auth", authHeader);
      refreshData();
    } else {
      showError("Invalid credentials");
    }
  } catch {
    showError("Connection failed. Is the server running?");
  }
});

// Check saved auth
(function checkAuth() {
  const saved = localStorage.getItem("auth");
  if (saved) {
    authHeader = saved;
    fetch("/api/stats", { headers: { Authorization: authHeader } })
      .then((res) => {
        if (res.ok) {
          document.getElementById("login-screen").style.display = "none";
          document.getElementById("dashboard").style.display = "block";
          refreshData();
        }
      })
      .catch(() => {});
  }
})();

function showError(msg) {
  const el = document.getElementById("login-error");
  el.textContent = msg;
  el.style.display = "block";
}

function logout() {
  localStorage.removeItem("auth");
  location.reload();
}

// Data
async function refreshData() {
  await Promise.all([loadStats(), loadUsers()]);
}

async function loadStats() {
  try {
    const res = await fetch("/api/stats", { headers: { Authorization: authHeader } });
    const data = await res.json();

    document.getElementById("total-users").textContent = data.users.total;
    document.getElementById("premium-users").textContent = data.users.premium;
    document.getElementById("active-today").textContent = data.users.active_today;
    document.getElementById("total-requests").textContent = data.usage.total_requests.toLocaleString();
    document.getElementById("total-tokens").textContent = data.usage.total_tokens.toLocaleString();
    document.getElementById("total-cost").textContent = "$" + data.usage.total_cost.toFixed(2);

    // Usage by feature
    const grid = document.getElementById("usage-grid");
    if (data.usage.by_feature.length === 0) {
      grid.innerHTML = '<p class="loading">No usage data yet</p>';
    } else {
      const featureIcons = {
        chat: "💬",
        image: "🎨",
        tts: "🔊",
        summarize: "📝",
        translate: "🌐",
        code: "💻",
      };

      grid.innerHTML = data.usage.by_feature
        .map(
          (f) => `
        <div class="usage-card">
          <h3>${featureIcons[f.feature] || "📊"} ${f.feature.charAt(0).toUpperCase() + f.feature.slice(1)}</h3>
          <div class="stat"><span class="stat-name">Requests</span><span>${f.count.toLocaleString()}</span></div>
          <div class="stat"><span class="stat-name">Tokens</span><span>${f.tokens.toLocaleString()}</span></div>
          <div class="stat"><span class="stat-name">Est. Cost</span><span>$${f.cost.toFixed(4)}</span></div>
        </div>
      `
        )
        .join("");
    }
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

async function loadUsers() {
  try {
    const res = await fetch("/api/users", { headers: { Authorization: authHeader } });
    const users = await res.json();

    const tbody = document.getElementById("users-table");
    if (users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="loading">No users yet</td></tr>';
      return;
    }

    tbody.innerHTML = users
      .map(
        (u) => `
      <tr>
        <td>${u.telegram_id}</td>
        <td>${u.username ? "@" + u.username : "-"}</td>
        <td>${[u.first_name, u.last_name].filter(Boolean).join(" ") || "-"}</td>
        <td>${u.language.toUpperCase()}</td>
        <td><span class="badge ${u.is_premium ? "badge-premium" : "badge-free"}">${u.is_premium ? "Premium" : "Free"}</span></td>
        <td>${u.total_requests}</td>
        <td><span class="badge ${u.is_banned ? "badge-banned" : "badge-active"}">${u.is_banned ? "Banned" : "Active"}</span></td>
        <td>
          ${
            u.is_banned
              ? `<button class="action-btn success" onclick="toggleBan(${u.telegram_id}, false)">Unban</button>`
              : `<button class="action-btn danger" onclick="toggleBan(${u.telegram_id}, true)">Ban</button>`
          }
          ${
            u.is_premium
              ? `<button class="action-btn" onclick="togglePremium(${u.telegram_id}, false)">Remove Premium</button>`
              : `<button class="action-btn success" onclick="togglePremium(${u.telegram_id}, true)">Give Premium</button>`
          }
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load users:", err);
  }
}

async function toggleBan(telegramId, ban) {
  const endpoint = ban ? "ban" : "unban";
  await fetch(`/api/users/${telegramId}/${endpoint}`, {
    method: "POST",
    headers: { Authorization: authHeader },
  });
  refreshData();
}

async function togglePremium(telegramId, add) {
  if (add) {
    const expires = new Date();
    expires.setMonth(expires.getMonth() + 1);
    await fetch(`/api/users/${telegramId}/premium`, {
      method: "POST",
      headers: { Authorization: authHeader, "Content-Type": "application/json" },
      body: JSON.stringify({ expiresAt: expires.toISOString() }),
    });
  } else {
    await fetch(`/api/users/${telegramId}/remove-premium`, {
      method: "POST",
      headers: { Authorization: authHeader },
    });
  }
  refreshData();
}

// Tabs
function showTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((t) => t.classList.remove("active"));

  event.target.classList.add("active");
  document.getElementById("tab-" + name).classList.add("active");
}
