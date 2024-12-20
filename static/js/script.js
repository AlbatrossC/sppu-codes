// Create backdrop element
const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

function loadFile(subject, fileName, questionText, element) {
    console.log(`Attempting to load file: ${subject}/${fileName}`);

    const answerBox = document.getElementById(element.nextElementSibling.id);
    const questionId = answerBox.id.match(/\d+[a-z]?/)[0];
    const questionTitle = document.getElementById('questionText' + questionId);
    const codeContent = document.getElementById('codeContent' + questionId);

    // Show loading state
    codeContent.innerText = 'Loading...';
    
    // Show modal and backdrop
    answerBox.style.display = 'block';
    backdrop.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling

    // Wrap content in scrollable container if not already wrapped
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

    navigator.clipboard.writeText(codeText)
        .then(() => {
            alert('Code copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy code:', err);
            alert('Failed to copy code! Please try selecting and copying manually.');
        });
}

function closeBox(boxId) {
    const answerBox = document.getElementById(boxId);
    answerBox.style.display = 'none';
    backdrop.style.display = 'none';
    document.body.style.overflow = ''; // Restore background scrolling
}

// Close modal when clicking backdrop
backdrop.addEventListener('click', function() {
    const visibleModal = document.querySelector('.answer-box[style*="display: block"]');
    if (visibleModal) {
        closeBox(visibleModal.id);
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const visibleModal = document.querySelector('.answer-box[style*="display: block"]');
        if (visibleModal) {
            closeBox(visibleModal.id);
        }
    }
});