function loadFile(subject, fileName, questionText, element) {
    // Log the attempt to load the file
    console.log(`Attempting to load file: ${subject}/${fileName}`);

    const answerBox = document.getElementById(element.nextElementSibling.id);
    const questionId = answerBox.id.match(/\d+[a-z]?/)[0];
    const questionTitle = document.getElementById('questionText' + questionId);
    const codeContent = document.getElementById('codeContent' + questionId);

    // Show loading state
    codeContent.innerText = 'Loading...';
    answerBox.style.display = 'block';

    fetch(`/answers/${subject}/${fileName}`)
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

            // Scroll to the question item
            const questionBox = element.closest('.question-item');
            const headerOffset = document.querySelector('header').offsetHeight;
            const position = questionBox.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = position - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
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
    document.getElementById(boxId).style.display = 'none';
}
