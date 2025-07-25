import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AddTransaction from "./components/AddTransaction";
import BlockchainViewer from "./components/BlockchainViewer"; // You'll create this next
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <nav style={{ marginBottom: "20px" }}>
          <Link to="/">Add Transaction</Link> |{" "}
          <Link to="/view">View Blockchain</Link>
        </nav>

        <Routes>
          <Route path="/" element={<AddTransaction />} />
          <Route path="/view" element={<BlockchainViewer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

