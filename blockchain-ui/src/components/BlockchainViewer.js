import React, { useEffect, useState } from "react";
import './BlockchainViewer.css'; 

function BlockchainViewer() {
  const [blocks, setBlocks] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/view")
      .then((res) => res.json())
      .then((data) => {
        setBlocks(data);
      })
      .catch((err) => {
        console.error("Error fetching blockchain:", err);
        setError("⚠️ Could not fetch blockchain data.");
      });
  }, []);

  return (
    <div className="viewer-container">
      <h2 className="viewer-title">📦 Blockchain Data</h2>
      {error && <p className="error-text">{error}</p>}
      {blocks.length === 0 && !error && <p className="loading-text">Loading...</p>}
      
      {blocks.map((block, index) => (
        <div
          className="block-card"
          key={block.index}
          style={{
            border: "2px solid #00ffff",
            borderRadius: "12px",
            padding: "20px",
            margin: "30px auto",
            maxWidth: "600px",
            backgroundColor: "#0e1b1f",
            color: "#ffffff",
            boxShadow: "0 0 20px #00ffff88",
            transition: "transform 0.2s",
            transform: index % 2 === 0 ? "rotate(-0.3deg)" : "rotate(0.3deg)"
          }}
        >
          <h3 style={{ textAlign: "center", color: "#00ffff", marginBottom: "16px" }}>
            🔐 Block {block.index}
          </h3>
          <p><strong>⏰ Timestamp:</strong> {block.timestamp}</p>
          <p><strong>📄 Details:</strong> {block.data?.details || block.data}</p>
          <p><strong>📱 Phone Number:</strong> {block.data?.phone_number || "-"}</p>
          <p><strong>🔗 Hash:</strong><br />{block.hash}</p>
          <p><strong>↩️ Previous Hash:</strong><br />{block.previous_hash}</p>
        </div>
      ))}
    </div>
  );
}

export default BlockchainViewer;
