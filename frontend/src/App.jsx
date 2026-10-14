import { useEffect, useState } from "react";
import "./App.css";

const roles = {
  User: {
    title: "User Dashboard",
    subtitle: "CASE MANAGEMENT",
    description: "Manage and track your case records."
  },
  Lawyer: {
    title: "Lawyer Dashboard",
    subtitle: "LEGAL PROFESSIONAL WORKSPACE",
    description: "Review case records and their available details."
  },
  Admin: {
    title: "Admin Dashboard",
    subtitle: "SYSTEM OVERVIEW",
    description: "Monitor records and prototype capabilities."
  }
};

function PageHeading({ eyebrow, title, description }) {
  return (
    <header className="page-heading">
      <span className="panel-eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </header>
  );
}

function StatCard({ label, value }) {
  return (
    <article className="stat-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

function CaseTable({ cases, onSelect }) {
  if (!cases.length) {
    return (
      <div className="empty-state">
        <p>No cases have been submitted yet.</p>
      </div>
    );
  }

  return (
    <div className="case-table-wrap">
      <table className="case-table">
        <thead>
          <tr>
            <th>Case</th>
            <th>Type</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((item, index) => (
            <tr key={item.id ?? index}>
              <td>{item.title ?? item.case_type ?? `Case ${index + 1}`}</td>
              <td>{item.case_type ?? "General"}</td>
              <td>{item.status ?? "Pending"}</td>
              <td>
                <button className="text-button" onClick={() => onSelect(item)}>
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Dashboard({
  role,
  cases,
  completedCount,
  pendingCount,
  onNew,
  onHistory,
  onAdmin,
  onSelect,
  analytics
}) {
  const config = roles[role];

  const dashboardContent = {
    User: {
      className: "dashboard-user",
      label: "YOUR LEGAL WORKSPACE",
      headline: "Clarity for every case.",
      description:
        "Submit case details, organize your records, and follow your case status from one workspace.",
      action: "Submit a new case",
      actionHandler: onNew,
      sideTitle: "Have a case to submit?",
      sideDescription: "Create a case record and request an experimental model prediction.",
      sideAction: "Create a case",
      sideHandler: onNew
    },
    Lawyer: {
      className: "dashboard-lawyer",
      label: "PROFESSIONAL REVIEW WORKSPACE",
      headline: "Every case, ready for review.",
      description:
        "Inspect submitted case records, review available information, and keep your workflow organized.",
      action: "Review case records",
      actionHandler: onHistory,
      sideTitle: "Ready to review a case?",
      sideDescription: "Open case history to inspect submitted records and predictions.",
      sideAction: "Open case history",
      sideHandler: onHistory
    },
    Admin: {
      className: "dashboard-admin",
      label: "SYSTEM CONTROL CENTER",
      headline: "Your system at a glance.",
      description:
        "Monitor case records and inspect the available dataset statistics.",
      action: "Open admin overview",
      actionHandler: onAdmin,
      sideTitle: "System management",
      sideDescription: "Inspect record totals and model dataset statistics.",
      sideAction: "Open system overview",
      sideHandler: onAdmin
    }
  };

  const content = dashboardContent[role];

  return (
    <section className={`role-dashboard ${content.className}`}>
      <PageHeading
        eyebrow={config.subtitle}
        title={config.title}
        description={config.description}
      />

      <div className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <span className="dashboard-hero-label">{content.label}</span>
          <h2>{content.headline}</h2>
          <p>{content.description}</p>

          <div className="dashboard-hero-actions">
            <button
              className="button dashboard-primary-button"
              onClick={content.actionHandler}
            >
              {content.action} <span aria-hidden="true">→</span>
            </button>
            <button
              className="button dashboard-secondary-button"
              onClick={onHistory}
            >
              View case history
            </button>
          </div>
        </div>

        <div className="dashboard-hero-art" aria-hidden="true">
          <div className="dashboard-orbit dashboard-orbit-one" />
          <div className="dashboard-orbit dashboard-orbit-two" />
          <span className="dashboard-floating-chip chip-top">
            <span className="dashboard-live-dot" />
            CASE WORKSPACE
          </span>
          <span className="dashboard-floating-chip chip-bottom">
            LEXPREDICT
          </span>
        </div>
      </div>

      <div className="dashboard-section-heading">
        <div>
          <h2>Workspace overview</h2>
          <p>A quick summary of the available case records.</p>
        </div>
        <span className="dashboard-period-label">CURRENT RECORDS</span>
      </div>

      <div className="stats-grid dashboard-stats">
        <StatCard label="Total cases" value={cases.length} />
        <StatCard label="Predictions received" value={completedCount} />
        <StatCard label="Pending / failed" value={pendingCount} />
        <StatCard label="Active role" value={role} />
      </div>

      {analytics && (
        <section className="app-content-panel">
          <h2>Model dataset overview</h2>
          <p>Dataset records available to the backend: {analytics.total_cases}</p>
          <p>
            Accepted: {analytics.outcome_counts?.Accepted ?? 0} · Rejected:{" "}
            {analytics.outcome_counts?.Rejected ?? 0} · Other:{" "}
            {analytics.outcome_counts?.Other ?? 0}
          </p>
        </section>
      )}

      <div className="dashboard-lower-grid">
        <section className="dashboard-recent-card">
          <div className="dashboard-section-heading recent-heading">
            <div>
              <h2>
                {role === "User"
                  ? "Your recent cases"
                  : role === "Lawyer"
                    ? "Cases to review"
                    : "Recent case records"}
              </h2>
              <p>Open a record to inspect its available details.</p>
            </div>
            <button className="text-button" onClick={onHistory}>
              View all →
            </button>
          </div>

          <CaseTable cases={cases.slice(0, 4)} onSelect={onSelect} />
        </section>

        <aside className="dashboard-side-card">
          <span className="panel-eyebrow">
            {role === "User"
              ? "GET STARTED"
              : role === "Lawyer"
                ? "REVIEW WORKSPACE"
                : "ADMIN TOOLS"}
          </span>
          <h3>{content.sideTitle}</h3>
          <p>{content.sideDescription}</p>
          <button className="dashboard-side-link" onClick={content.sideHandler}>
            {content.sideAction} <span aria-hidden="true">→</span>
          </button>
          <div className="dashboard-side-divider" />
          <div className="dashboard-side-note">
            <p>
              Predictions are experimental and should not be used to make legal
              decisions.
            </p>
          </div>
        </aside>
      </div>

      <div className="bottom-note">
        <p>
          <strong>Decision-support prototype</strong>
          <br />
          Model output is experimental, has limited test accuracy, and is not
          legal advice. Role selection is not secure authentication.
        </p>
      </div>
    </section>
  );
}

export default function App() {
  const [role, setRole] = useState("User");
  const [cases, setCases] = useState([]);
  const [view, setView] = useState("dashboard");
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseTitle, setCaseTitle] = useState("");
  const [caseType, setCaseType] = useState("Civil");
  const [caseDescription, setCaseDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch("/api/cases")
      .then(response => {
        if (!response.ok) throw new Error("Could not load saved cases.");
        return response.json();
      })
      .then(data => {
        const savedCases = Array.isArray(data) ? data : data.cases ?? [];
        setCases(savedCases.map(item => ({
          ...item,
          status: item.status ?? item.prediction_status ?? "Saved"
        })));
      })
      .catch(err => setError(err.message));
  }, []);
  useEffect(() => {
    fetch("/api/analytics")
      .then(response => {
        if (!response.ok) throw new Error("Could not load dataset statistics.");
        return response.json();
      })
      .then(data => setAnalytics(data))
      .catch(() => setAnalytics(null));
  }, []);

  const completedCount = cases.filter(item => item.predicted_outcome).length;
  const pendingCount = cases.length - completedCount;

  async function createCase(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    const categoryMap = {
      Civil: "civil",
      Criminal: "criminal",
      Family: "civil",
      Property: "civil",
      Other: "Unknown"
    };

    try {
      const response = await fetch("/api/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: caseTitle.trim(),
          case_category: categoryMap[caseType] ?? "civil",
          case_type: caseType.toLowerCase(),
          description: caseDescription.trim(),
          role
        })
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(`Saving case failed (${response.status}). ${details}`);
      }

      const saved = await response.json();
      const completedCase = {
        ...saved,
        status: saved.prediction_status ?? "Prediction received"
      };

      setCases(previous => [
        completedCase,
        ...previous.filter(item => item.id !== completedCase.id)
      ]);
      setSelectedCase(completedCase);
      setCaseTitle("");
      setCaseDescription("");
      setView("detail");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }
  return (
    <main className="app-shell">
      <nav className="app-role-nav">
        <strong>Case Outcome Prediction</strong>
        <div className="app-role-buttons">
          {["User", "Lawyer", "Admin"].map(item => (
            <button
              key={item}
              className={
                role === item
                  ? "button dashboard-primary-button"
                  : "button dashboard-secondary-button"
              }
              onClick={() => {
                setRole(item);
                setView("dashboard");
              }}
            >
              {item}
            </button>
          ))}
        </div>
      </nav>

      {view === "dashboard" && (
        <Dashboard
          role={role}
          cases={cases}
          completedCount={completedCount}
          pendingCount={pendingCount}
          analytics={analytics}
          onNew={() => {
            setError("");
            setView("new");
          }}
          onHistory={() => setView("history")}
          onAdmin={() => setView("admin")}
          onSelect={item => {
            setSelectedCase(item);
            setView("detail");
          }}
        />
      )}

      {view === "new" && (
        <section className="app-content-panel">
          <h1>Submit a case</h1>
          <p>Enter case details to request an experimental model prediction.</p>

          {error && <p role="alert">{error}</p>}

          <form onSubmit={createCase} className="case-form">
            <label>
              Case title
              <input
                required
                value={caseTitle}
                onChange={event => setCaseTitle(event.target.value)}
                placeholder="Enter a case title"
              />
            </label>

            <label>
              Case type
              <select
                value={caseType}
                onChange={event => setCaseType(event.target.value)}
              >
                <option>Civil</option>
                <option>Criminal</option>
                <option>Family</option>
                <option>Property</option>
                <option>Other</option>
              </select>
            </label>

            <label>
              Case description
              <textarea
                required
                rows={5}
                value={caseDescription}
                onChange={event => setCaseDescription(event.target.value)}
                placeholder="Describe the case"
              />
            </label>

            <button
              className="button dashboard-primary-button"
              type="submit"
              disabled={submitting}
            >
              {submitting ? "Requesting prediction..." : "Submit case and predict"}
            </button>

            <button
              className="button dashboard-secondary-button"
              type="button"
              disabled={submitting}
              onClick={() => setView("dashboard")}
            >
              Cancel
            </button>
          </form>
        </section>
      )}

      {view === "history" && (
        <section className="app-content-panel">
          <h1>Case history</h1>
          <p>Records currently remain in browser memory and are lost on refresh.</p>
          <CaseTable
            cases={cases}
            onSelect={item => {
              setSelectedCase(item);
              setView("detail");
            }}
          />
          <button
            className="button dashboard-secondary-button"
            onClick={() => setView("dashboard")}
          >
            Back to dashboard
          </button>
        </section>
      )}

      {view === "admin" && (
        <section className="app-content-panel">
          <h1>System overview</h1>
          <p>Local case records: {cases.length}</p>
          <p>Predictions received: {completedCount}</p>
          <p>Pending or failed: {pendingCount}</p>
          <p>Backend dataset cases: {analytics?.total_cases ?? "Unavailable"}</p>
          <button
            className="button dashboard-secondary-button"
            onClick={() => setView("dashboard")}
          >
            Back to dashboard
          </button>
        </section>
      )}

      {view === "detail" && selectedCase && (
        <section className="app-content-panel">
          <h1>{selectedCase.title || "Case details"}</h1>
          <p>Type: {selectedCase.case_type || "General"}</p>
          <p>Status: {selectedCase.status || "Pending"}</p>
          <p>{selectedCase.description || "No description available."}</p>

          {selectedCase.predicted_outcome ? (
            <>
              <h2>Experimental model prediction</h2>
              <p>
                <strong>Predicted outcome: {selectedCase.predicted_outcome}</strong>
              </p>
              {selectedCase.model_scores && (
                <ul>
                  {Object.entries(selectedCase.model_scores).map(([label, score]) => (
                    <li key={label}>
                      {label}: {(score * 100).toFixed(2)}%
                    </li>
                  ))}
                </ul>
              )}
            </>
          ) : (
            <p role="alert">
              Prediction unavailable: {selectedCase.warning || error || "Please try again."}
            </p>
          )}

          <p>
            <strong>Important:</strong>{" "}
            {selectedCase.warning ||
              "This experimental model has limited accuracy. Its scores are not calibrated confidence estimates and are not legal advice."}
          </p>

          {role === "Lawyer" && (
            <section className="lawyer-preparation-tools">
              <h2>Lawyer Preparation Workspace</h2>
              <p>
                Use these prompts to organize your review. Verify all facts,
                applicable laws, deadlines, and procedures independently.
              </p>

              <h3>1. Case Summary</h3>
              <p>{selectedCase.description || "No case description was provided."}</p>

              <h3>2. Evidence Checklist</h3>
              <ul>
                <li>Verify identity of the parties and their roles.</li>
                <li>Collect relevant agreements, notices, and official documents.</li>
                <li>Organize dated correspondence, messages, and other records.</li>
                <li>Identify potential witnesses and confirm what they personally know.</li>
                <li>Check the authenticity, completeness, and source of each item.</li>
              </ul>

              <h3>3. Questions for the Client</h3>
              <ul>
                <li>What happened, and when did each important event occur?</li>
                <li>Which documents or other records support your account?</li>
                <li>Have you received any notices, claims, or court documents?</li>
                <li>Are there deadlines or upcoming hearings that need verification?</li>
                <li>What outcome are you seeking, and what facts remain uncertain?</li>
              </ul>

              <h3>4. Suggested Next Steps</h3>
              <ol>
                <li>Prepare a timeline based on the client's account and available records.</li>
                <li>List missing evidence and request relevant supporting documents.</li>
                <li>Identify legal questions requiring jurisdiction-specific research.</li>
                <li>Independently verify applicable procedures, limitation periods, and deadlines.</li>
                <li>Discuss possible options and risks with the client after reviewing the evidence.</li>
              </ol>

              <h3>5. Case Review Notes</h3>
              <textarea
                aria-label="Case review notes"
                rows="5"
                placeholder="Record review notes for this session..."
                style={{ width: "100%", boxSizing: "border-box", padding: "10px" }}
              />

              <p>
                <strong>Reminder:</strong> These are general preparation prompts,
                not legal advice or verified case-specific findings. The model's
                prediction is experimental and should not determine legal decisions.
                Notes entered here are not saved to the database.
              </p>
            </section>
          )}
          <button
            className="button dashboard-secondary-button"
            onClick={() => setView("history")}
          >
            Back to history
          </button>
          <button
            className="button dashboard-secondary-button"
            onClick={() => setView("dashboard")}
          >
            Dashboard
          </button>
        </section>
      )}
    </main>
  );
}


