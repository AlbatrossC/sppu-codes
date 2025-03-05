const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

function loadFile(subject, fileName, questionText, element) {
    console.log(`Attempting to load file: ${subject}/${fileName}`);

    // Find the closest .question-item and locate the answer-box inside it
    const questionItem = element.closest('.question-item');
    if (!questionItem) {
        console.error('Error: Could not find parent .question-item');
        return;
    }

    const answerBox = questionItem.querySelector('.answer-box');
    if (!answerBox) {
        console.error('Error: Could not find .answer-box inside question-item');
        return;
    }

    const questionId = answerBox.id.match(/\d+[a-z]?/);
    if (!questionId) {
        console.error('Error: Could not extract question ID from answer-box ID');
        return;
    }

    const questionTitle = document.getElementById('questionText' + questionId[0]);
    const codeContent = document.getElementById('codeContent' + questionId[0]);

    if (!questionTitle || !codeContent) {
        console.error('Error: Missing question title or code content elements');
        return;
    }

    codeContent.innerText = 'Loading...';
    answerBox.style.display = 'block';
    backdrop.style.display = 'block';
    document.body.style.overflow = 'hidden';

    if (!answerBox.querySelector('.modal-content')) {
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        while (answerBox.children.length > 0) {
            modalContent.appendChild(answerBox.children[0]);
        }
        answerBox.appendChild(modalContent);
    }

    fetch(`/${subject}/${fileName}`)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log('File loaded successfully');
            questionTitle.innerText = questionText;
            codeContent.innerText = data;
        })
        .catch(err => {
            console.error('Error loading file:', err);
            codeContent.innerText = `Error loading file: ${err.message}`;
            alert(`Failed to load ${fileName}. Error: ${err.message}`);
        });
}


function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    const codeText = codeElement.innerText;
    const copyButton = document.querySelector(`#${elementId}`).parentElement.querySelector('.copy-btn');

    navigator.clipboard.writeText(codeText)
        .then(() => {
            // Add a class to the button for styling and animation
            copyButton.classList.add('copied');

            // Change button text to "Copied" and add a checkmark icon
            copyButton.innerHTML = `Copied to Clipboard`;

            // Reset button text and styling after 5 seconds
            setTimeout(() => {
                copyButton.classList.remove('copied');
                copyButton.innerHTML = `Copy Code`;
            }, 5000);
        })
        .catch(err => {
            console.error('Failed to copy code:', err);
            alert('Failed to copy code! Please try selecting and copying manually.');
        });
}

// Function to close the answer box
function closeBox(boxId) {
    const answerBox = document.getElementById(boxId);
    if (answerBox) {
        answerBox.style.display = 'none';
        backdrop.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
}

// Function to close the popup
function closePopup() {
    const popup = document.getElementById('dynamicCopyPopup');
    if (popup) {
        popup.style.display = 'none';
        backdrop.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
}

// Event: Close modal or popup with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const popup = document.getElementById('dynamicCopyPopup');
        if (popup && popup.style.display === 'flex') {
            closePopup();
        } else {
            const visibleModal = document.querySelector('.answer-box[style*="display: block"]');
            if (visibleModal) {
                closeBox(visibleModal.id);
            }
        }
    }
});

// Close answer box by clicking on backdrop
backdrop.addEventListener('click', function() {
    const visibleModal = document.querySelector('.answer-box[style*="display: block"]');
    if (visibleModal) {
        closeBox(visibleModal.id);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // Get the question parameter from URL
    const params = new URLSearchParams(window.location.search);
    const question = params.get("q");
    
    if (!question) return; // Exit if no question parameter
    
    // Find the matching question by URL parameter
    const links = document.querySelectorAll(".question-link");
    
    for (const link of links) {
        if (link.href.includes(`?q=${question}`)) {
            const targetElement = link.closest(".question-item");
            
            if (targetElement) {
                // Highlight with blue border
                targetElement.style.borderColor = "#58a6ff";
                targetElement.style.boxShadow = "0 0 0 3px rgba(88, 166, 255, 0.3)";
                
                // Scroll to the element
                targetElement.scrollIntoView({ behavior: "smooth" });
                
                // Reset highlighting after 3 seconds
                setTimeout(function() {
                    targetElement.style.borderColor = "#333"; // Reset to original border color
                    targetElement.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.4)"; // Reset to original shadow
                }, 3000);
                
                break; // Exit once found
            }
        }
    }
});

function downloadCode(subject, fileName) {
    const filePath = `/${subject}/${fileName}`;
    fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            const blob = new Blob([data], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(err => {
            console.error('Error downloading file:', err);
            alert(`Failed to download ${fileName}. Error: ${err.message}`);
        });
}