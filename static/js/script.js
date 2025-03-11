(function () {
    // Function to load Google Tag Manager asynchronously
    function loadGTM() {
        var script = document.createElement('script');
        script.src = 'https://www.googletagmanager.com/gtag/js?id=G-1R5FFVKTF8';
        script.async = true;

        script.onload = function () {
            window.dataLayer = window.dataLayer || [];
            function gtag() {
                window.dataLayer.push(arguments);
            }
            gtag('js', new Date());
            gtag('config', 'G-1R5FFVKTF8');
        };

        document.head.appendChild(script);
    }

    // Function to load Google Fonts asynchronously
    function loadGoogleFonts() {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Fira+Code&display=swap';
        link.type = 'text/css';
        document.head.appendChild(link);
    }

    // Function to load marked.js asynchronously with a specific version
    function loadMarkedJS() {
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked@4.0.0/marked.min.js';
        script.async = true;
        document.head.appendChild(script);
    }

    // Load Google Tag Manager after a delay or when needed
    setTimeout(loadGTM, 3000); // Delay GTM loading by 3 seconds

    // Load Google Fonts and marked.js only when needed
    document.addEventListener('DOMContentLoaded', function () {
        loadGoogleFonts();
        loadMarkedJS();
    });
})();

// Modal backdrop setup
const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

let GEMINI_API_KEY = ''; // Will be fetched from the server

// Fetch the API key from the server
fetch('/get-api-key')
    .then(response => response.json())
    .then(data => {
        GEMINI_API_KEY = data.api_key;
    })
    .catch(error => {
        console.error('Error fetching API key:', error);
    });

const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent';

// Rate limiting configuration
const RATE_LIMIT_DELAY = 1000; // 1 second delay between API calls
let lastApiCallTime = 0;

// System Instructions
const SYSTEM_INSTRUCTIONS = {
    initial: 'You are an code explanation bot. I will provide you a question for reference and its code. your task is explain it in this format: Prefers code explanations in the following structured format: 1. Understanding the Code – Explanation of key components and their purpose. 2. Main Function Execution Flow – Step-by-step breakdown of how the program runs. 3. Summary – Key features and concepts covered in the code. Note: Break code in several parts and then explain each step in snippet format. Dont write the whole code in the chat. Also note that the explanation should be based on the syllabus of Courses present in SPPU university.',

    followup: 'You are an AI assistant tasked with answering the latest question based on the provided code and conversation history. Focus on the text after "Question:" as the main prompt, ignoring older questions unless directly relevant. Use the conversation history purely for context, and simplify your response when asked a follow up question. (it maybe related to the code and it can be random) by avoiding technical jargon and making it beginner-friendly. If code is provided, break it into smaller parts and explain each step-by-step, but do not repeat the entire code unless explicitly requested. Now, answer the latest question based on the following:'
};

// Conversation memory (supports up to 2 million tokens)
let conversationMemory = [];

// Generic function to make API requests to Gemini with rate limiting
async function fetchFromGemini(instruction, question, codeText = '') {
    const now = Date.now();
    if (now - lastApiCallTime < RATE_LIMIT_DELAY) {
        await new Promise(resolve => setTimeout(resolve, RATE_LIMIT_DELAY - (now - lastApiCallTime)));
    }
    lastApiCallTime = Date.now();

    // Prepare the request body with the full conversation history
    const requestBody = {
        contents: [{
            parts: [
                { text: instruction },
                { text: codeText ? `Question: ${question}\n\nCode:\n${codeText}` : `Question: ${question}` }
            ]
        }]
    };

    // Add the entire conversation history to the request
    if (conversationMemory.length > 0) {
        requestBody.contents[0].parts.push({ text: `Conversation History:\n${conversationMemory.join('\n')}` });
    }

    try {
        const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status}. Details: ${errorText}`);
        }

        const data = await response.json();
        
        if (!data.candidates?.[0]?.content?.parts?.[0]) {
            throw new Error('Unexpected API response structure');
        }
        
        // Store the response in conversation memory
        const responseText = data.candidates[0].content.parts[0].text;
        conversationMemory.push(`You: ${question}`);
        conversationMemory.push(`Bot: ${responseText}`);
        
        return responseText;
    } catch (error) {
        throw error;
    }
}

// Function to load a file dynamically
async function loadFile(subject, fileName, questionText, element) {
    console.log(`Loading file: ${subject}/${fileName}`);

    const questionItem = element.closest('.question-item');
    if (!questionItem) {
        return;
    }

    const answerBox = questionItem.querySelector('.answer-box');
    if (!answerBox) {
        return;
    }

    const questionId = answerBox.id.match(/\d+[a-z]?/)?.[0];
    if (!questionId) {
        return;
    }

    const questionTitle = document.getElementById('questionText' + questionId);
    const codeContent = document.getElementById('codeContent' + questionId);

    if (!questionTitle || !codeContent) {
        return;
    }

    // Show loading state
    codeContent.innerText = 'Loading...';
    answerBox.style.display = 'block';
    backdrop.style.display = 'block';
    document.body.style.overflow = 'hidden';

    // Ensure modal content wrapper exists
    if (!answerBox.querySelector('.modal-content')) {
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        while (answerBox.children.length > 0) {
            modalContent.appendChild(answerBox.children[0]);
        }
        answerBox.appendChild(modalContent);
    }

    try {
        // Updated URL to include /answers
        const response = await fetch(`/answers/${subject}/${fileName}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        
        questionTitle.innerText = questionText;
        codeContent.innerText = data;
    } catch (err) {
        codeContent.innerText = `Error loading file: ${err.message}`;
        alert(`Failed to load ${fileName}. Error: ${err.message}`);
    }
}

// Function to copy code to clipboard
function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    if (!codeElement) return;
    
    const codeText = codeElement.innerText;
    const copyButton = document.querySelector(`#${elementId}`).parentElement.querySelector('.copy-btn');
    if (!copyButton) return;

    navigator.clipboard.writeText(codeText)
        .then(() => {
            copyButton.classList.add('copied');
            copyButton.innerHTML = 'Copied to Clipboard';
            setTimeout(() => {
                copyButton.classList.remove('copied');
                copyButton.innerHTML = 'Copy Code';
            }, 2000);
        })
        .catch(err => {
            alert('Failed to copy code! Please try selecting and copying manually.');
        });
}

// Function to close modal boxes
function closeBox(boxId) {
    const box = document.getElementById(boxId);
    if (box) {
        box.classList.remove('split-view');
        box.style.display = 'none';
        backdrop.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Function to close the explanation modal and reset everything
function closeExplanationModal() {
    const explanationModal = document.getElementById('explanationModal');
    if (!explanationModal) return;
    
    // Reset the modal
    explanationModal.classList.remove('split-view');
    explanationModal.style.display = 'none';
    
    // Check if the answer box is still visible
    const answerBox = document.querySelector('.answer-box[style*="display: block"]');
    if (answerBox) {
        // If the answer box is still visible, show the backdrop
        backdrop.style.display = 'block';
    } else {
        // If no answer box is visible, hide the backdrop
        backdrop.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    // Reset the original answer box
    if (answerBox) {
        answerBox.classList.remove('split-view');
        answerBox.style.left = '50%';
        answerBox.style.transform = 'translate(-50%, -50%)';
        answerBox.style.width = '90%';
        answerBox.style.maxWidth = '1200px';
        answerBox.style.height = 'auto';
        answerBox.style.borderRadius = '12px';
    }

    // Clear conversation memory
    conversationMemory = [];

    // Clear the messages container
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
    }
}

// Helper function to create explanation modal if it doesn't exist
function createExplanationModal() {
    let explanationModal = document.getElementById('explanationModal');
    
    if (!explanationModal) {
        explanationModal = document.createElement('div');
        explanationModal.id = 'explanationModal';
        explanationModal.className = 'explanation-modal';
        explanationModal.innerHTML = `
            <div class="modal-content">
                <h3>Code Explanation</h3>
                <div id="messagesContainer" class="messages-container"></div>
                <div class="sticky-bottom">
                    <input type="text" id="furtherQuestionInput" placeholder="Ask a further question about this code...">
                    <button id="askFurtherQuestionBtn">Ask</button>
                    <button class="close-btn" onclick="closeExplanationModal()">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(explanationModal);

        // Add event listener for asking further questions
        document.getElementById('askFurtherQuestionBtn').addEventListener('click', handleFurtherQuestion);

        // Add event listener for Enter key in input field
        const input = document.getElementById('furtherQuestionInput');
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                handleFurtherQuestion();
            }
        });
    }
    
    return explanationModal;
}

// Function to handle further questions
async function handleFurtherQuestion() {
    const input = document.getElementById('furtherQuestionInput');
    const question = input.value.trim();
    if (!question) return;
    
    const codeElement = document.querySelector('.answer-box[style*="display: block"] .code-content');
    const codeText = codeElement ? codeElement.innerText : '';
    const messagesContainer = document.getElementById('messagesContainer');
    
    // Add user question to messages
    messagesContainer.innerHTML += `<div class="message user-message">You: ${question}</div>`;
    
    // Add loading message
    const loadingMsgId = `loading-${Date.now()}`;
    messagesContainer.innerHTML += `<div id="${loadingMsgId}" class="message bot-message">Bot: Processing your question...</div>`;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
        const response = await fetchFromGemini(SYSTEM_INSTRUCTIONS.followup, question, codeText);
        
        // Convert the response to Markdown
        const markdownResponse = marked.parse(response);
        
        const loadingMsg = document.getElementById(loadingMsgId);
        if (loadingMsg) {
            loadingMsg.innerHTML = `Bot: ${markdownResponse}`;
        }
        
        // Store the conversation in memory
        conversationMemory.push(`You: ${question}`);
        conversationMemory.push(`Bot: ${response}`);
    } catch (error) {
        const loadingMsg = document.getElementById(loadingMsgId);
        if (loadingMsg) {
            loadingMsg.innerHTML = `Bot: Error: ${error.message}`;
        }
    }
    
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function explainCode(elementId) {
    const codeElement = document.getElementById(elementId);
    if (!codeElement) return;
    
    const codeText = codeElement.innerText;
    const questionItem = codeElement.closest('.question-item');
    const questionText = questionItem?.querySelector('h1')?.innerText || 'Code analysis';
    
    // Create or get explanation modal
    const explanationModal = createExplanationModal();
    const messagesContainer = document.getElementById('messagesContainer');
    
    // Add loading animation
    messagesContainer.innerHTML = `
        <div class="message bot-message">
            <div class="loading-container">
                <p>Bot: Analyzing code and preparing explanation</p>
                <div class="loading-animation">
                    <div class="dot dot1"></div>
                    <div class="dot dot2"></div>
                    <div class="dot dot3"></div>
                </div>
            </div>
        </div>
    `;
    
    // Reset styles for split view
    const answerBox = codeElement.closest('.answer-box');
    if (answerBox) {
        answerBox.classList.add('split-view');
        answerBox.style.left = '0';
        answerBox.style.transform = 'translateY(-50%)';
        answerBox.style.width = 'calc(50% - 10px)';
        answerBox.style.maxWidth = 'none';
        answerBox.style.height = '100vh';
        answerBox.style.borderRadius = '12px';
        answerBox.style.marginRight = '10px';
    }

    if (explanationModal) {
        explanationModal.classList.add('split-view');
        explanationModal.style.display = 'block';
        explanationModal.style.width = 'calc(50% - 10px)';
        explanationModal.style.left = 'calc(50% + 10px)';
        explanationModal.style.transform = 'translateY(-50%)';
    }

    backdrop.style.display = 'block';
    document.body.style.overflow = 'hidden';

    try {
        const explanation = await fetchFromGemini(SYSTEM_INSTRUCTIONS.initial, questionText, codeText);
        
        // Convert the explanation to Markdown
        const markdownExplanation = marked.parse(explanation);
        
        // Clear loading message
        messagesContainer.innerHTML = '';
        
        // Create a new message for the bot's response
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.innerHTML = `Bot: ${markdownExplanation}`;
        messagesContainer.appendChild(botMessage);
        
        // Store the initial explanation in memory
        conversationMemory.push(`Bot: ${explanation}`);
    } catch (error) {
        messagesContainer.innerHTML = `
            <div class="message bot-message">
                Bot: Error: Unable to fetch explanation. ${error.message}
                <div class="error-help">
                    <p>This might be due to:</p>
                    <ul>
                        <li>Invalid API key</li>
                        <li>API quota exceeded</li>
                        <li>Network connectivity issues</li>
                        <li>The API request being too large</li>
                    </ul>
                    <p>Please check the console for more details.</p>
                </div>
            </div>
        `;
    }

    // Scroll to the bottom of the messages container
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper function to escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Function to download code
async function downloadCode(subject, fileName) {
    try {
        // Updated URL to include /answers
        const response = await fetch(`/answers/${subject}/${fileName}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) {
        alert(`Failed to download ${fileName}. Error: ${err.message}`);
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
            const explanationModal = document.getElementById('explanationModal');
            if (explanationModal && explanationModal.style.display === 'block') {
                closeExplanationModal();
            }
        }
    }
});

// Close modals by clicking on backdrop
backdrop.addEventListener('click', function() {
    const visibleModal = document.querySelector('.answer-box[style*="display: block"]');
    if (visibleModal) {
        closeBox(visibleModal.id);
    }
    const explanationModal = document.getElementById('explanationModal');
    if (explanationModal && explanationModal.style.display === 'block') {
        closeExplanationModal();
    }
});

// Highlight and scroll to questions based on URL parameters
document.addEventListener("DOMContentLoaded", function() {
    // Check for URL parameters
    const params = new URLSearchParams(window.location.search);
    const question = params.get("q");
    
    if (question) {
        const links = document.querySelectorAll(".question-link");
        
        for (const link of links) {
            if (link.href.includes(`?q=${question}`)) {
                const targetElement = link.closest(".question-item");
                
                if (targetElement) {
                    // Highlight and scroll to target element
                    targetElement.style.borderColor = "#58a6ff";
                    targetElement.style.boxShadow = "0 0 0 3px rgba(88, 166, 255, 0.3)";
                    targetElement.scrollIntoView({ behavior: "smooth" });
                    
                    // Reset styles after delay
                    setTimeout(function() {
                        targetElement.style.borderColor = "#333";
                        targetElement.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.4)";
                    }, 3000);
                    break;
                }
            }
        }
    }
});

// Add responsive handlers for window resizing
window.addEventListener('resize', () => {
    const explanationModal = document.getElementById('explanationModal');
    const visibleAnswerBox = document.querySelector('.answer-box[style*="display: block"]');
    
    if (explanationModal && explanationModal.style.display === 'block' && visibleAnswerBox) {
        if (window.innerWidth < 768) {
            // On small screens, disable split view
            explanationModal.classList.remove('split-view');
            visibleAnswerBox.classList.remove('split-view');
            explanationModal.style.width = '90%';
            visibleAnswerBox.style.width = '90%';
        } else {
            // On larger screens, enable split view
            explanationModal.classList.add('split-view');
            visibleAnswerBox.classList.add('split-view');
        }
    }
});

// highlightQuestion function to highlight the question based on the URL path
const highlightQuestion = () => {
    const path = window.location.pathname; // e.g., "/iotl/blinking-led"
    const questionId = path.split('/').pop(); // e.g., "blinking-led"
    const questionElement = document.getElementById(questionId);

    if (questionElement) {
        // Add a CSS class to highlight the question
        questionElement.classList.add('highlighted-question');

        // Use Intersection Observer to scroll into view only when the element is in the viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Smooth scroll to the question
                    entry.target.scrollIntoView({ behavior: 'smooth', block: 'start' });

                    // Stop observing after scrolling
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 }); // Trigger when 50% of the element is visible

        observer.observe(questionElement);
    }
};

// Call the function to highlight the question on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(highlightQuestion, 0);
});
