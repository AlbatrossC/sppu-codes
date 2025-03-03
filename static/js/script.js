const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

function loadFile(subject, fileName, questionText, element) {
    console.log(`Attempting to load file: ${subject}/${fileName}`);
    const answerBox = document.getElementById(element.nextElementSibling.id);
    const questionId = answerBox.id.match(/\d+[a-z]?/)[0];
    const questionTitle = document.getElementById('questionText' + questionId);
    const codeContent = document.getElementById('codeContent' + questionId);

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
document.addEventListener('DOMContentLoaded', () => {
    // Function to smoothly scroll to an element
    function scrollToElement(id) {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Handle click events on question links
    document.querySelectorAll('.question-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.id;
            scrollToElement(targetId);
            history.pushState(null, null, `#${targetId}`);
        });
    });

    // Handle initial page load with hash
    if (window.location.hash) {
        setTimeout(() => {
            scrollToElement(window.location.hash.substring(1));
        }, 100);
    }
});
