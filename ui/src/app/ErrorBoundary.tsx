import React from "react";

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error) {
    console.error("UI crash:", error);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, color: "white", fontFamily: "monospace" }}>
          <h2 style={{ color: "#ff6b6b" }}>❌ UI crashed</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {this.state.error.message}
            {"\n\n"}
            {this.state.error.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}
