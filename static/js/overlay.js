// JavaScript to dynamically add styles and the GIF overlay
document.addEventListener("DOMContentLoaded", () => {
    // Create and inject styles
    const style = document.createElement("style");
    style.textContent = `
        #gif-overlay {
            position: fixed;
            bottom: 0;
            right: 0;
            z-index: 9999; /* Ensures it's on top of other elements */
            width: 150px; /* Adjust width as needed */
            height: auto; /* Maintain aspect ratio */
        }
    `;
    document.head.appendChild(style);

    // Create and inject the GIF overlay
    const gifOverlay = document.createElement("img");
    gifOverlay.id = "gif-overlay";
    gifOverlay.src = "static/gifs/sunflower-pvz.gif"; // Adjust the path if needed
    gifOverlay.alt = "GIF";
    document.body.appendChild(gifOverlay);
});
