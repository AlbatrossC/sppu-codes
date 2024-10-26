// static/js/script.js
function loadFile(subject, fileName, questionText, element) {
    const answerBox = document.getElementById(element.nextElementSibling.id);
    const questionTitle = document.getElementById('questionText' + answerBox.id.match(/\d+/)[0]);
    const codeContent = document.getElementById('codeContent' + answerBox.id.match(/\d+/)[0]);

    // Use Flask route to load the file content
    fetch(`/answers/${subject}/${fileName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            questionTitle.innerText = questionText;
            codeContent.innerText = data;
            answerBox.style.display = 'block';

            // Scroll to the question and answer from the position of the "View Answer" link
            const questionBox = element.closest('.question-item'); // Get the question box
            const headerOffset = document.querySelector('header').offsetHeight; // Get header height

            // Calculate the position of the question and answer box
            const position = questionBox.getBoundingClientRect().top + window.pageYOffset; // Get the absolute position
            const offsetPosition = position - headerOffset; // Adjust for header height

            // Smoothly scroll to the position from the "View Answer" link
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        })
        .catch(err => {
            console.error('Error loading file:', err);
            alert('Failed to load the file. Please try again.');
        });
}

function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    const codeText = codeElement.innerText;

    navigator.clipboard.writeText(codeText).then(() => {
        alert('Code copied to clipboard!');
    }, () => {
        alert('Failed to copy code!');
    });
}

function closeBox(boxId) {
    const answerBox = document.getElementById(boxId);
    answerBox.style.display = 'none';
}
