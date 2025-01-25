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

    navigator.clipboard.writeText(codeText)
        .then(() => {
            showPopup();
        })
        .catch(err => {
            console.error('Failed to copy code:', err);
            alert('Failed to copy code! Please try selecting and copying manually.');
        });
}

function showPopup() {
    const gifs = [
        "/static/gifs/DisappointedWorldCup.gif",
        "/static/gifs/SuperBowlNoGIFbyNFL.gif",
        "/static/gifs/TheOfficeDisappointed.gif",
        "/static/gifs/WellDoneReactionGIF.gif",
    ];
    const messages = [
        "You copied the code. Mast! Now, understand it before you start pretending to be a coder.",
        "You copied the code. Now, how about actually using your brain and figuring it out?",
        "Code copy karayla kay? Mast! Aata samjun ghe, tyachya aadi code copy karun apna 'coder' banu nako.",
        "Copying without understanding? You’re just making your learning harder.",
        "You’re not learning if you don’t understand the code. Stop copying like a robot."
    ];

    // Randomize GIF and message
    const randomGif = gifs[Math.floor(Math.random() * gifs.length)];
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];

    let popup = document.getElementById('dynamicCopyPopup');
    if (!popup) {
        popup = document.createElement('div');
        popup.id = 'dynamicCopyPopup';
        popup.className = 'popup-container';
        popup.innerHTML = `
            <div class="popup">
                <img src="${randomGif}" alt="Success" class="popup-gif">
                <h2>Code Copied !!</h2>
                <p class="popup-message">${randomMessage}</p>
                <div class="progress-bar"></div>
            </div>
        `;
        document.body.appendChild(popup);
    } else {
        popup.querySelector('.popup-gif').src = randomGif;
        popup.querySelector('.popup-message').innerText = randomMessage;
    }

    popup.style.display = 'flex';

    // Reset and start progress bar animation
    const progressBar = popup.querySelector('.progress-bar');
    progressBar.style.width = '100%';
    progressBar.style.transition = 'none';
    setTimeout(() => {
        progressBar.style.transition = 'width 5s linear';
        progressBar.style.width = '0%';
    }, 50);

    setTimeout(() => {
        popup.style.display = 'none';
    }, 5000);
}

function closeBox(boxId) {
    const answerBox = document.getElementById(boxId);
    answerBox.style.display = 'none';
    backdrop.style.display = 'none';
    document.body.style.overflow = '';
}

function closePopup() {
    const popup = document.getElementById('dynamicCopyPopup');
    if (popup) {
        popup.style.display = 'none';
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
