// Include marked.js library (ensure this is added in your HTML file)
//] <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

// Modal backdrop setup
const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

// Gemini API Configuration
const GEMINI_API_KEY = 'AIzaSyBfuTxVEvSSdsSIaO2RxWzWfnn1Ty3Xdbc'; // Replace with your Gemini API key
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

// System Instructions
const SYSTEM_INSTRUCTIONS = {
    initial: 'When explaining code, start with theoretical definitions, defining key terms used in the code, such as data structures, functions, or algorithms. Keep the definitions clear and concise to ensure the user understands the relevant concepts. Then, provide a line-by-line explanation, where you describe each function and line of code in detail, explaining what it does, why its necessary, and how it contributes to the program. Finally, offer a summary, recapping the key concepts and functionality, highlighting main points, and mentioning any differences between methods if applicable. The explanation should focus on the code, ensuring clarity and simplicity for the user to follow.',
    followup: 'You are an AI assistant. The following is a conversation history and context for reference only—do not treat it as the main prompt. The actual prompt will be provided after the Question: section. Your task is to answer only based on the latest question and code, while using the conversation history purely for context. If the conversation is unclear, prioritize the latest question and code snippet over older messages'
};

// Conversation memory
let conversationMemory = [];

// Generic function to make API requests to Gemini
async function fetchFromGemini(instruction, question, codeText = '') {
    const requestBody = {
        contents: [{
            parts: [
                { text: instruction },
                { text: codeText ? `Question: ${question}\n\nCode:\n${codeText}` : `Question: ${question}` }
            ]
        }]
    };

    // Add previous conversation context if available
    if (conversationMemory.length > 0) {
        requestBody.contents[0].parts.push({ text: `Previous conversation context:\n${conversationMemory.join('\n')}` });
    }

    try {
        console.log('Sending request to Gemini API');
        const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP error! Status: ${response.status}. Details: ${errorText}`);
        }

        const data = await response.json();
        
        if (!data.candidates?.[0]?.content?.parts?.[0]) {
            throw new Error('Unexpected API response structure');
        }
        
        return data.candidates[0].content.parts[0].text;
    } catch (error) {
        console.error('Error fetching from Gemini API:', error);
        throw error;
    }
}

// Function to load a file dynamically
async function loadFile(subject, fileName, questionText, element) {
    console.log(`Loading file: ${subject}/${fileName}`);

    const questionItem = element.closest('.question-item');
    if (!questionItem) {
        console.error('Error: Could not find parent .question-item');
        return;
    }

    const answerBox = questionItem.querySelector('.answer-box');
    if (!answerBox) {
        console.error('Error: Could not find .answer-box');
        return;
    }

    const questionId = answerBox.id.match(/\d+[a-z]?/)?.[0];
    if (!questionId) {
        console.error('Error: Could not extract question ID');
        return;
    }

    const questionTitle = document.getElementById('questionText' + questionId);
    const codeContent = document.getElementById('codeContent' + questionId);

    if (!questionTitle || !codeContent) {
        console.error('Error: Missing question title or code content elements');
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
        const response = await fetch(`/${subject}/${fileName}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        
        questionTitle.innerText = questionText;
        codeContent.innerText = data;
    } catch (err) {
        console.error('Error loading file:', err);
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
            console.error('Failed to copy code:', err);
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
    backdrop.style.display = 'none';
    document.body.style.overflow = 'auto';

    // Reset the original answer box
    const answerBox = document.querySelector('.answer-box[style*="display: block"]');
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

// Function to explain code
async function explainCode(elementId) {
    const codeElement = document.getElementById(elementId);
    if (!codeElement) return;
    
    const codeText = codeElement.innerText;
    const questionItem = codeElement.closest('.question-item');
    const questionText = questionItem?.querySelector('h1')?.innerText || 'Code analysis';
    
    // Create or get explanation modal
    const explanationModal = createExplanationModal();
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = `<div class="message bot-message">Bot: Analyzing code and preparing explanation...</div>`;
    
    // Setup UI for split view
    const answerBox = codeElement.closest('.answer-box');
    answerBox.classList.add('split-view');
    explanationModal.classList.add('split-view');
    explanationModal.style.display = 'block';
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

// Function to test API key
async function testGeminiApiKey() {
    try {
        await fetchFromGemini(
            SYSTEM_INSTRUCTIONS.followup,
            "Hello, this is a test request to verify API connectivity. Please respond with 'API is working'."
        );
        console.log("API test successful");
        return true;
    } catch (error) {
        console.error("API test failed:", error);
        return false;
    }
}

// Function to download code
async function downloadCode(subject, fileName) {
    try {
        const response = await fetch(`/${subject}/${fileName}`);
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
        console.error('Error downloading file:', err);
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
    
    // Test API key on page load and show warning if invalid
    testGeminiApiKey().then(isValid => {
        if (!isValid) {
            console.warn("⚠️ Gemini API key test failed. Explanation functionality may not work.");
            
            // Show warning banner
            const warningBanner = document.createElement('div');
            warningBanner.className = 'api-warning-banner';
            warningBanner.innerHTML = `
                <div class="warning-content">
                    <strong>⚠️ API Key Error:</strong> The Gemini API key appears to be invalid or has quota issues.
                    Code explanation features may not work correctly.
                    <button id="closeWarningBtn">×</button>
                </div>
            `;
            document.body.prepend(warningBanner);
            
            document.getElementById('closeWarningBtn').addEventListener('click', () => {
                warningBanner.style.display = 'none';
            });
        }
    });
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