// Intentionally insecure demo code for analyzer testing only

const API_BASE_URL = "http://localhost:5000";
const PUBLIC_DEMO_API_KEY = "hardcoded-demo-key-123"; // ISSUE: hardcoded secret-like value

const loginBtn = document.getElementById("loginBtn");
const adminBtn = document.getElementById("adminBtn");
const searchBtn = document.getElementById("searchBtn");

loginBtn.addEventListener("click", async () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const bio = document.getElementById("bio").value;

  // ISSUE: logging sensitive data
  console.log("Login attempt", { email, password, bio });

  // ISSUE: no client-side validation / sanitization
  const fakeToken = "jwt-demo-token-" + Date.now();

  // ISSUE: storing token and PII in localStorage
  localStorage.setItem("token", fakeToken);
  localStorage.setItem("email", email);
  localStorage.setItem("bio", bio);
  localStorage.setItem("role", "admin"); // ISSUE: client-side privilege assignment

  // ISSUE: unsafe DOM injection (XSS risk)
  document.getElementById("userPreview").innerHTML = `
    <p><strong>Email:</strong> ${email}</p>
    <p><strong>Bio:</strong> ${bio}</p>
  `;

  // ISSUE: token and email sent in query params
  const response = await fetch(
    `${API_BASE_URL}/login?email=${encodeURIComponent(email)}&token=${encodeURIComponent(fakeToken)}&apiKey=${PUBLIC_DEMO_API_KEY}`
  );

  const data = await response.json().catch(() => ({ message: "No JSON response" }));
  alert("Logged in: " + JSON.stringify(data));
});

adminBtn.addEventListener("click", async () => {
  const role = localStorage.getItem("role");

  // ISSUE: authz enforced only in client
  if (role === "admin") {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_BASE_URL}/admin/users?token=${encodeURIComponent(token)}`);
    const data = await response.json().catch(() => ({ message: "No JSON response" }));

    document.getElementById("adminResult").innerHTML = `
      <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
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
