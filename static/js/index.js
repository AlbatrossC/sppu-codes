const statsModal = document.getElementById('stats-modal');
const statsButton = document.getElementById('menu-stats');
const closeModalButton = document.getElementById('close-modal'); 

// Function to open the modal
statsButton.addEventListener('click', () => {
    statsModal.classList.remove('hidden');
});

// Function to close the modal
closeModalButton.addEventListener('click', () => {
    statsModal.classList.add('hidden'); 
});

// Close modal when clicking outside of the content
window.addEventListener('click', (event) => {
    if (event.target === statsModal) {
        statsModal.classList.add('hidden'); 
    }
});
