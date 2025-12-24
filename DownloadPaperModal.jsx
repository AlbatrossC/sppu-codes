import React, { useState } from "react";

const SUBJECT_NAME = "SUBJECT_NAME"; // Replace with dynamic value as needed

export default function DownloadPaperModal() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        style={{
          background: "#27ae60",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          padding: "12px 28px",
          fontSize: "1rem",
          cursor: "pointer",
          fontWeight: 600,
          boxShadow: "0 2px 8px rgba(39,174,96,0.08)",
          transition: "background 0.2s"
        }}
        onClick={() => setOpen(true)}
      >
        Download Paper
      </button>
      {open && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.18)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div style={{
            background: "#fff",
            borderRadius: "12px",
            minWidth: "320px",
            maxWidth: "90vw",
            padding: "32px 24px 24px 24px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
            position: "relative"
          }}>
            <button
              onClick={() => setOpen(false)}
              style={{
                position: "absolute",
                top: 16,
                right: 16,
                background: "none",
                border: "none",
                fontSize: "1.3rem",
                color: "#888",
                cursor: "pointer"
              }}
              aria-label="Close"
            >×</button>
            <h2 style={{
              margin: 0,
              marginBottom: "24px",
              fontWeight: 700,
              fontSize: "1.25rem",
              color: "#222"
            }}>
              Download "{SUBJECT_NAME}" Papers
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
              <a
                href="#"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  background: "#f5f5f5",
                  borderRadius: "6px",
                  padding: "12px 18px",
                  textDecoration: "none",
                  color: "#222",
                  fontWeight: 500,
                  transition: "background 0.18s"
                }}
                download
              >
                <span role="img" aria-label="zip">🗜️</span>
                Insem Paper (.zip)
              </a>
              <a
                href="#"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  background: "#f5f5f5",
                  borderRadius: "6px",
                  padding: "12px 18px",
                  textDecoration: "none",
                  color: "#222",
                  fontWeight: 500,
                  transition: "background 0.18s"
                }}
                download
              >
                <span role="img" aria-label="zip">🗜️</span>
                Endsem Paper (.zip)
              </a>
              <a
                href="#"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  background: "#f5f5f5",
                  borderRadius: "6px",
                  padding: "12px 18px",
                  textDecoration: "none",
                  color: "#222",
                  fontWeight: 500,
                  transition: "background 0.18s"
                }}
                download
              >
                <span role="img" aria-label="zip">🗜️</span>
                All Papers (.zip)
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
