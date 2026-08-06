import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import RiskExplorer from "./RiskExplorer";
import "./globals.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RiskExplorer />
  </StrictMode>,
);
