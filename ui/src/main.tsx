import { createRoot } from "react-dom/client";
import App from "./app/App";
import "./styles/index.css";
import { ErrorBoundary } from "./app/ErrorBoundary";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element '#root' not found. Check index.html");
}

createRoot(rootElement).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);