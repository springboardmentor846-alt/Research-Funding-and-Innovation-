import React from "react";

/**
 * Last-resort error fence.
 *
 * The app historically rendered no boundaries, which meant any thrown
 * error inside a route component (Chart.js, a malformed patent object,
 * a stale cache) would unmount the entire tree and leave the user
 * staring at a blank white page. This boundary keeps the route tree
 * alive and shows a recoverable error panel instead.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary caught:", error, info);
    this.setState({ info });
  }

  handleReset = () => {
    this.setState({ error: null, info: null });
  };

  handleReload = () => {
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  render() {
    if (!this.state.error) return this.props.children;

    const message =
      this.state.error?.message ||
      (typeof this.state.error === "string" ? this.state.error : null) ||
      "Something went wrong rendering this page.";

    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
        <div className="max-w-xl w-full card">
          <h1 className="text-xl font-semibold text-red-600 mb-2">
            ⚠ Page error
          </h1>
          <p className="text-sm text-slate-700 mb-3 break-words">
            {message}
          </p>
          {process.env.NODE_ENV !== "production" && this.state.info?.componentStack && (
            <pre className="text-xs bg-slate-100 p-3 rounded overflow-auto max-h-64 text-slate-700">
              {this.state.info.componentStack}
            </pre>
          )}
          <div className="mt-4 flex gap-2">
            <button
              type="button"
              onClick={this.handleReset}
              className="btn-primary"
            >
              Try again
            </button>
            <button
              type="button"
              onClick={this.handleReload}
              className="btn-secondary"
            >
              Reload page
            </button>
          </div>
        </div>
      </div>
    );
  }
}
