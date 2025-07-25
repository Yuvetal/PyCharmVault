// src/components/AddTransaction.js
import "./AddTransaction.css";
import React, { useState } from "react";
import "../App.css";

const AddTransaction = () => {
  const [txnData, setTxnData] = useState("");
  const [phone, setPhone] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [generatedOtp, setGeneratedOtp] = useState("");
  const [userOtp, setUserOtp] = useState("");
  const [message, setMessage] = useState("");

  const isValidPhoneNumber = (number) => {
    return (
      /^[6-9]\d{9}$/.test(number) // starts with 6-9, only digits, exactly 10 digits
    );
  };

  const handleSendOtp = (e) => {
    e.preventDefault(); // prevent any page reload

    if (!txnData || !phone) {
      setMessage("⚠️ Please enter both transaction and phone number.");
      return;
    }

    if (!isValidPhoneNumber(phone)) {
      setMessage("⚠️ Invalid phone number. Must be 10 digits, start with 6/7/8/9, and contain only digits.");
      return;
    }

    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    setGeneratedOtp(otp);
    setOtpSent(true);
    setMessage(`[MOCK] OTP sent to ${phone}: ${otp}`);
  };

  const handleVerifyAndSubmit = async (e) => {
    e.preventDefault(); // prevent page refresh

    if (userOtp !== generatedOtp) {
      setMessage("❌ Incorrect OTP.");
      return;
    }

    setMessage("⏳ Adding transaction to blockchain...");

    try {
      const response = await fetch("http://localhost:5000/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          details: txnData,
          phone_number: phone,
        }),
      });

      const data = await response.json();

      if (response.ok && data.message) {
        setMessage("✅ Transaction added to blockchain!");

        // Reset after success
        setTxnData("");
        setPhone("");
        setUserOtp("");
        setOtpSent(false);
      } else {
        setMessage("❌ Failed to add transaction.");
      }
    } catch (err) {
      console.error("Error adding transaction:", err);
      setMessage("❌ Error connecting to backend.");
    }
  };

return (
  <div className="transaction-container">
    <h2>📥 Add Blockchain Transaction</h2>

    <form className="transaction-form" onSubmit={handleVerifyAndSubmit}>
      <input
        type="text"
        placeholder="Enter transaction details"
        value={txnData}
        onChange={(e) => setTxnData(e.target.value)}
      />
      <input
        type="text"
        placeholder="Enter phone number"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />
      <button onClick={handleSendOtp}>Send OTP</button>

      {otpSent && (
        <>
          <input
            type="text"
            placeholder="Enter OTP"
            value={userOtp}
            onChange={(e) => setUserOtp(e.target.value)}
          />
          <button class="glow-button"type="submit">Verify & Add</button>
        </>
      )}
    </form>

    <p>{message}</p>
  </div>
);

};

export default AddTransaction;
