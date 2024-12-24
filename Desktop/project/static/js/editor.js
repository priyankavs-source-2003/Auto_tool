function runCode() {
    const editor = ace.edit("editor");
    const code = editor.getValue();
    console.log("Executing Code:", code);

    // Backend API call to execute the code
    fetch("/execute_code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: code }),
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById("output").innerText = "Output: " + data.output;
        })
        .catch(error => {
            console.error("Error executing code:", error);
            document.getElementById("output").innerText = "Error: Unable to execute code.";
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/python");
});

// Utility function to validate JSON
function isValidJSON(jsonString) {
    try {
        JSON.parse(jsonString);
        return true;
    } catch (e) {
        return false;
    }
}

async function addProblem() {
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const testCases = document.getElementById("test-cases").value;

    if (!isValidJSON(testCases)) {
        alert("Test cases must be valid JSON.");
        return;
    }

    try {
        const response = await fetch("/add_problem", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, description, testCases }),
        });

        if (response.ok) {
            alert("Problem added successfully!");
            document.getElementById("add-problem-form").reset();
        } else {
            alert("Failed to add problem.");
        }
    } catch (error) {
        console.error("Error adding problem:", error);
        alert("An error occurred. Please try again.");
    }
}

function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const USER_CREDENTIALS = [
        { email: "user1@example.com", password: "user123" },
        { email: "user2@example.com", password: "user456" },
    ];

    // Check admin credentials
    if (email === "admin@example.com" && password === "admin123") {
        window.location.href = "/admin_dashboard"; // Redirect to Flask route for admin dashboard
        return;
    }

    // Check user credentials
    const isUser = USER_CREDENTIALS.some(
        user => user.email === email && user.password === password
    );

    if (isUser) {
        window.location.href = "/question_selector"; // Redirect to Flask route for user environment
    } else {
        alert("Invalid email or password!");
    }
}
