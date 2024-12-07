// Variable to store the popup element reference
let popup = null;
let isPopupVisible = false;

// A flag to track if the event listeners are already set
let isListenersActive = false;

// Function to fetch the content of answer.txt
async function fetchAnswerText() {
    const answerFilePath = chrome.runtime.getURL("answer.txt");
    try {
        const response = await fetch(answerFilePath);
        if (!response.ok) {
            throw new Error(`Failed to fetch answer.txt: ${response.statusText}`);
        }
        return await response.text();
    } catch (error) {
        console.error("Error reading answer.txt:", error);
        return "Error loading answer.";
    }
}

// Function to ensure the key event listeners are active
function setupKeyEvents() {
    // If listeners are not active, set them
    if (!isListenersActive) {
        // Handle keydown event
        document.addEventListener('keydown', async function(event) {
            if (event.key === '=' && !isPopupVisible) {
                // If '=' is pressed and popup is not visible, show the popup
                const content = await fetchAnswerText();
                showPopup(content);
            }
        });

        // Handle keyup event
        document.addEventListener('keyup', function(event) {
            if (event.key === '=') {
                // If '=' is released, hide the popup
                hidePopup();
            }
        });

        // Mark listeners as active
        isListenersActive = true;
    }
}

// Function to show the popup with specified text
function showPopup(text) {
    if (!popup) {
        // Create the popup element only once
        popup = document.createElement('div');
        popup.style.position = 'fixed';
        popup.style.bottom = '10px';
        popup.style.right = '10px';
        popup.style.backgroundColor = 'cream';
        popup.style.padding = '10px';
        popup.style.borderRadius = '50%';
        popup.style.textAlign = 'center';
        popup.style.zIndex = '10000';
        popup.style.transition = 'opacity 0.5s, visibility 0.5s';
        popup.style.opacity = 0;  // Start with invisible
        popup.style.visibility = 'hidden';  // Hidden initially
        document.body.appendChild(popup);
    }

    popup.innerText = text;  // Set popup text

    // Make the popup visible with fade-in
    setTimeout(() => {
        popup.style.opacity = 1;
        popup.style.visibility = 'visible';  // Ensure it's visible
    }, 0);

    isPopupVisible = true;  // Mark the popup as visible
}

// Function to hide the popup
function hidePopup() {
    if (popup && isPopupVisible) {
        // Fade out the popup and hide it
        popup.style.opacity = 0;
        popup.style.visibility = 'hidden';
        isPopupVisible = false;  // Mark the popup as hidden
    }
}

// Start by ensuring the key events are always active
setupKeyEvents();

// Optionally, recheck the popup and event listeners after a short interval
setInterval(setupKeyEvents, 1000);  // Recheck every 1 second to ensure the listeners are active
