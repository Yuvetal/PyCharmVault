import React, { useEffect, useState } from "react";

function BlockchainViewer() {
  const [blocks, setBlocks] = useState([]);
  const [error, setError] = useState("");

useEffect(() => {
  fetch("http://localhost:5000/view")
    .then((res) => res.json())
    .then((data) => {
      setBlocks(data); // ✅ No .chain needed
    })
    .catch((err) => {
      console.error("Error fetching blockchain:", err);
      setError("⚠️ Could not fetch blockchain data.");
    });
}, []);



  return (
    <div className="App">
      <h2>📦 Blockchain Data</h2>
      {error && <p>{error}</p>}
      {blocks.length === 0 && !error && <p>Loading...</p>}
      {blocks.map((block) => (
        <div
          key={block.index}
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            margin: "10px auto",
            width: "80%",
            borderRadius: "10px",
            textAlign: "left",
          }}
        >
          <p><strong>🔢 Index:</strong> {block.index}</p>
          <p><strong>⏰ Timestamp:</strong> {block.timestamp}</p>
          <p><strong>📄 Details:</strong> {block.data?.details || block.data}</p>
          <p><strong>📱 Phone Number:</strong> {block.data?.phone_number || "-"}</p>
          <p><strong>🔗 Hash:</strong> {block.hash}</p>
          <p><strong>↩️ Previous Hash:</strong> {block.previous_hash}</p>
        </div>
      ))}
    </div>
  );
}

export default BlockchainViewer;
