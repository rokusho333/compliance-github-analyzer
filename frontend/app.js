// Intentionally insecure demo client for analyzer testing only

const API_BASE_URL = "http://localhost:5000"; // ISSUE: insecure HTTP
const PUBLIC_DEMO_API_KEY = "frontend-demo-key-123"; // ISSUE: hardcoded secret-like value

const loginBtn = document.getElementById("loginBtn");
const adminBtn = document.getElementById("adminBtn");
const searchBtn = document.getElementById("searchBtn");
const uploadBtn = document.getElementById("uploadBtn");
const dangerBtn = document.getElementById("dangerBtn");

loginBtn.addEventListener("click", async () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const bio = document.getElementById("bio").value;

  // ISSUE: logging credentials and PII
  console.log("Login attempt", { email, password, bio });

  // ISSUE: no validation or sanitization
  const fakeToken = "jwt-demo-token-" + Date.now();

  // ISSUE: insecure localStorage of token, role and PII
  localStorage.setItem("token", fakeToken);
  localStorage.setItem("email", email);
  localStorage.setItem("bio", bio);
  localStorage.setItem("role", "admin"); // ISSUE: privilege controlled in client

  // ISSUE: unsafe DOM injection / XSS risk
  document.getElementById("userPreview").innerHTML = `
    <p><strong>Email:</strong> ${email}</p>
    <p><strong>Bio:</strong> ${bio}</p>
  `;

  // ISSUE: token and email in query params
  const response = await fetch(
    `${API_BASE_URL}/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&token=${encodeURIComponent(fakeToken)}&apiKey=${PUBLIC_DEMO_API_KEY}`
  );

  const data = await response.json().catch(() => ({ message: "No JSON response" }));
  alert("Logged in: " + JSON.stringify(data));
});

adminBtn.addEventListener("click", async () => {
  const role = localStorage.getItem("role");

  // ISSUE: client-side-only authorization
  if (role === "admin") {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/admin/users?token=${encodeURIComponent(token)}`);
    const data = await response.json().catch(() => ({ message: "No JSON response" }));

    // ISSUE: can display sensitive data received from API
    document.getElementById("adminResult").textContent = JSON.stringify(data, null, 2);
  } else {
    document.getElementById("adminResult").textContent = "Access denied";
  }
});

searchBtn.addEventListener("click", async () => {
  const query = document.getElementById("search").value;

  // ISSUE: dangerous dynamic execution
  if (query.startsWith("debug:")) {
    const expression = query.replace("debug:", "");
    try {
      const result = eval(expression);
      document.getElementById("searchResult").textContent = "Eval result: " + result;
    } catch (err) {
      document.getElementById("searchResult").textContent = "Eval failed: " + err.message;
    }
    return;
  }

  const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
  const data = await response.text();
  document.getElementById("searchResult").textContent = data;
});

uploadBtn.addEventListener("click", async () => {
  const fileInput = document.getElementById("uploadFile");
  const file = fileInput.files[0];

  if (!file) {
    document.getElementById("uploadResult").textContent = "Select a file first";
    return;
  }

  const formData = new FormData();
  formData.append("file", file, file.name);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData
  });

  const data = await response.json().catch(() => ({ message: "No JSON response" }));
  document.getElementById("uploadResult").textContent = JSON.stringify(data, null, 2);
});

dangerBtn.addEventListener("click", async () => {
  const payload = {
    user_id: "u1",
    action: "delete_all",
    notes: document.getElementById("bio").value
  };

  const response = await fetch(`${API_BASE_URL}/process`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": PUBLIC_DEMO_API_KEY
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json().catch(() => ({ message: "No JSON response" }));
  document.getElementById("dangerResult").textContent = JSON.stringify(data, null, 2);
});
