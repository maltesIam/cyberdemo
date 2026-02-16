import express from "express";
import cors from "cors";
import morgan from "morgan";

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(morgan("dev"));
app.use(express.json());

// Health check
app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "cyberdemo-mock-server" });
});

// SIEM Endpoints (to be implemented)
app.get("/api/siem/alerts", (_req, res) => {
  res.json({ alerts: [], message: "Mock SIEM - Not implemented yet" });
});

// EDR Endpoints (to be implemented)
app.get("/api/edr/hosts/:id", (req, res) => {
  res.json({ hostId: req.params.id, message: "Mock EDR - Not implemented yet" });
});

// Intel Endpoints (to be implemented)
app.get("/api/intel/hash/:sha256", (req, res) => {
  res.json({ hash: req.params.sha256, message: "Mock Intel - Not implemented yet" });
});

app.listen(PORT, () => {
  console.log(`Mock Server running on http://localhost:${PORT}`);
});
