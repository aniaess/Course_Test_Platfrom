const passwordToggle = document.querySelector(".toggle-password");

if (passwordToggle) {
    passwordToggle.addEventListener("click", () => {
        const passwordInput = document.getElementById("password");
        const isVisible = passwordInput.type === "text";

        passwordInput.type = isVisible ? "password" : "text";
        passwordToggle.setAttribute("aria-pressed", String(!isVisible));
        passwordToggle.setAttribute(
            "aria-label",
            isVisible ? "Show password" : "Hide password"
        );
    });
}

const registerForm = document.getElementById("register-form");

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        const message = document.getElementById("register-message");

        message.textContent = "";
        message.className = "";

        if (!name) {
            message.textContent = "Name cannot be empty.";
            message.className = "error-message";
            return;
        }

        if (name.length < 2) {
            message.textContent = "Name is too short.";
            message.className = "error-message";
            return;
        }

        if (name.length > 100) {
            message.textContent = "Name is too long.";
            message.className = "error-message";
            return;
        }

        if (!email) {
            message.textContent = "Email cannot be empty.";
            message.className = "error-message";
            return;
        }

        if (!password) {
            message.textContent = "Password cannot be empty.";
            message.className = "error-message";
            return;
        }

        if (password.length < 8) {
            message.textContent = "Password must be at least 8 characters long.";
            message.className = "error-message";
            return;
        }

        if (password.length > 128) {
            message.textContent = "Password must be at most 128 characters long.";
            message.className = "error-message";
            return;
        }

        const userData = {
            name: name,
            email: email,
            password: password
        };

        console.log("Sending registration request...");

        let response;

        try {
            response = await fetch("/users", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            });
        } catch (error) {
            console.error("Registration request failed:", error);
            message.textContent = "Cannot connect to the server. Please check your connection.";
            message.className = "error-message";
            return;
        }

        console.log("Response status:", response.status);

        const data = await response.json().catch(() => null);

        console.log("Response data:", data);

        if (response.status === 201) {
            message.textContent = "Registration successful!";
            message.className = "success-message";
        } else if (response.status === 409 && data) {
            message.textContent = data.detail;
            message.className = "error-message";
        } else {
            message.textContent = "Something went wrong. Please try again later.";
            message.className = "error-message";
        }
    });
}