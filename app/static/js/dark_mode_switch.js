
    const toggleButton = document.getElementById('mode-toggle'); // This is now the checkbox input
    const body = document.body;

    // Check for saved dark mode preference and apply on page load
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        toggleButton.checked = true; // Set the toggle switch to 'on' if dark mode is active
    }

    toggleButton.addEventListener('change', () => { // Listen for 'change' event for checkboxes
        body.classList.toggle('dark-mode');

        // Save preference to local storage based on the checkbox's checked state
        if (toggleButton.checked) { // Check if the toggle is currently on
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });
