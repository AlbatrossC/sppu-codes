document.addEventListener("DOMContentLoaded", () => {
    // Create and inject styles with performance optimization
    const style = document.createElement("style");
    style.textContent = `
        #gif-overlay {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            width: 150px;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        #gif-overlay:hover {
            transform: scale(1.05);
            opacity: 0.9;
        }
    `;
    document.head.appendChild(style);

    // Create and inject the GIF overlay with error handling
    const gifOverlay = document.createElement("img");
    gifOverlay.id = "gif-overlay";
    gifOverlay.src = "static/gifs/sunflower-pvz.gif";
    gifOverlay.alt = "Sunflower GIF";
    
    // Add error handling for image loading
    gifOverlay.onerror = () => {
        console.warn('Failed to load GIF overlay');
        gifOverlay.remove();
    };

    // Append after a short delay to prevent potential blocking
    setTimeout(() => {
        document.body.appendChild(gifOverlay);
    }, 1000);
});