
const getUsers = () =>
  JSON.parse(localStorage.getItem("marketIQUsers") || "[]");

const signup = document.getElementById("signupForm");

if (signup) {
  signup.onsubmit = function(e) {
    e.preventDefault();

    const users = getUsers();
    const email = document.getElementById("email").value.trim().toLowerCase();
    const password = document.getElementById("password").value;

    if (users.some(u => u.email === email)) {
      message.textContent = "Email already registered!";
      return;
    }

    users.push({
      name: document.getElementById("name").value,
      shop: document.getElementById("shop").value,
      email,
      password
    });

    localStorage.setItem("marketIQUsers", JSON.stringify(users));
    alert("Signup successful! Please login.");
    location.href = "login.html";
  };
}

const login = document.getElementById("loginForm");

if (login) {
  login.onsubmit = function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim().toLowerCase();
    const password = document.getElementById("password").value;
    const user = getUsers().find(
      u => u.email === email && u.password === password
    );

    if (!user) {
      document.getElementById("message").textContent =
        "Incorrect email or password!";
      return;
    }

    sessionStorage.setItem("marketIQUser", JSON.stringify(user));
    location.href = "dashboard.html";
  };
}
