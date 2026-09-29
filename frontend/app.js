alert("APP.JS WORKS!");

const registerForm = document.getElementById("register-form");

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

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

        const userData = {
            name: name,
            email: email,
            password: password
        };

        console.log("Sending registration request...");

        const response = await fetch("/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        console.log("Response status:", response.status);

        const data = await response.json();

        console.log("Response data:", data);

        if (response.status === 201) {
            message.textContent = "Registration successful!";
            message.className = "success-message";
        } else if (response.status === 409) {
            message.textContent = data.detail;
            message.className = "error-message";
        }
    });
}