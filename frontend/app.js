let dashboard = null;
let isLoggedIn = false;

const titles = {
  overview: ["Milestone 2 Dashboard", "Funding discovery and research trend intelligence with recommendation scores and sample analytics."],
  profile: ["Research Profile", "Core user profile used for funding, research, patent, and innovation recommendations."],
  funding: ["Funding Recommendations", "Sample funding opportunities ranked by domain match and eligibility fit."],
  trends: ["Research Trend Intelligence", "Emerging topics and research hotspots based on publication intelligence."],
  patents: ["Patent Landscape Analytics", "Patent signals, assignees, technology domains, and citation indicators."],
  reports: ["Reports And Export", "Milestone summary and next implementation steps for review discussion."],
};

async function loadDashboard() {
  try {
    const response = await fetch("/api/dashboard");
    dashboard = await response.json();
  } catch {
    dashboard = fallbackData();
  }
}

function showDashboard() {
  isLoggedIn = true;
  document.getElementById("loginPage").classList.add("hidden");
  document.getElementById("appShell").classList.remove("hidden");
  render("overview");
}

function showLogin() {
  isLoggedIn = false;
  document.getElementById("appShell").classList.add("hidden");
  document.getElementById("loginPage").classList.remove("hidden");
}

function render(view) {
  if (!isLoggedIn) return;

  document.querySelectorAll("nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });

  const [title, subtitle] = titles[view];
  document.getElementById("pageTitle").textContent = title;
  document.getElementById("pageSubtitle").textContent = subtitle;

  const content = document.getElementById("content");

  if (view === "overview") content.innerHTML = overviewView();
  if (view === "profile") content.innerHTML = profileView();
  if (view === "funding") content.innerHTML = fundingView();
  if (view === "trends") content.innerHTML = trendsView();
  if (view === "patents") content.innerHTML = patentsView();
  if (view === "reports") content.innerHTML = reportsView();
}

function overviewView() {
  const m = dashboard.metrics;

  return `
    <section class="milestone-banner">
      <div>
        <strong>Milestone 2 Focus</strong>
        <span>Funding Discovery + Research Intelligence</span>
      </div>
      <p>This prototype now highlights funding recommendations, eligibility matching, research trends, and relevance scores using sample API data.</p>
    </section>

    <section class="metrics">
      ${metric("Funding Matches", m.fundingMatches, "5 high relevance", "blue")}
      ${metric("Research Hotspots", m.researchHotspots, "AI, health, climate", "green")}
      ${metric("Patent Signals", m.patentSignals, "12 recent filings", "gold")}
      ${metric("Innovation Score", m.innovationScore, "commercially promising", "red")}
    </section>

    <section class="grid">
      <div class="panel">
        <h2>Recommended Funding Opportunities</h2>
        ${fundingTable(dashboard.funding.slice(0, 3))}
      </div>

      <div class="panel">
        <h2>Milestone 2 Workflow</h2>
        <div class="workflow">
          <div class="step"><strong>1. Read Profile</strong><span>Use domains, keywords, and technology areas.</span></div>
          <div class="step"><strong>2. Match Funding</strong><span>Compare opportunities with user interests and eligibility.</span></div>
          <div class="step"><strong>3. Analyze Trends</strong><span>Show growing research topics with relevance scores.</span></div>
          <div class="step"><strong>4. Display Insights</strong><span>Present funding and trend results in dashboard pages.</span></div>
        </div>
      </div>
    </section>

    <section class="split">
      <div class="panel">
        <h2>Innovation Score Breakdown</h2>
        ${scoreTable()}
      </div>

      <div class="panel">
        <h2>Top Research Trends</h2>
        ${trendsTable(dashboard.trends.slice(0, 3))}
      </div>
    </section>
  `;
}

function profileView() {
  const p = dashboard.profile;

  return `
    <section class="panel">
      <h2>Current Research Profile</h2>
      <div class="profile-list">
        <div class="profile-item"><strong>Name</strong><span>${p.name}</span></div>
        <div class="profile-item"><strong>Role</strong><span>${p.role}</span></div>
        <div class="profile-item"><strong>Organization</strong><span>${p.organization}</span></div>
        <div class="profile-item"><strong>Domains</strong><span>${p.domains.join(", ")}</span></div>
        <div class="profile-item"><strong>Keywords</strong><span>${p.keywords.join(", ")}</span></div>
        <div class="profile-item"><strong>Technology Areas</strong><span>${p.technologyAreas.join(", ")}</span></div>
      </div>
    </section>
  `;
}

function fundingView() {
  return `
    <section class="milestone-banner">
      <div>
        <strong>Milestone 2 Module</strong>
        <span>Funding Discovery</span>
      </div>
      <p>This page recommends funding opportunities by matching research domains, keywords, eligibility, deadline, and funding relevance.</p>
    </section>

    <section class="split">
      <div class="panel">
        <h2>Recommendation Logic</h2>
        <div class="workflow">
          <div class="step"><strong>Profile Keywords</strong><span>AI, funding, patent analytics, commercialization</span></div>
          <div class="step"><strong>Eligibility Check</strong><span>Researcher, student, startup, or university team</span></div>
          <div class="step"><strong>Match Score</strong><span>Higher score means better fit for the user profile</span></div>
        </div>
      </div>

      <div class="panel">
        <h2>Funding Summary</h2>
        <div class="profile-list">
          <div class="profile-item"><strong>Total Opportunities</strong><span>${dashboard.funding.length}</span></div>
          <div class="profile-item"><strong>Highest Match</strong><span>${Math.max(...dashboard.funding.map((item) => item.match))}%</span></div>
          <div class="profile-item"><strong>Top Domain</strong><span>Artificial Intelligence</span></div>
        </div>
      </div>
    </section>

    <section class="panel page-gap">
      <h2>Funding Recommendation Engine</h2>
      ${fundingTable(dashboard.funding)}
    </section>
  `;
}

function trendsView() {
  return `
    <section class="milestone-banner">
      <div>
        <strong>Milestone 2 Module</strong>
        <span>Research Trend Intelligence</span>
      </div>
      <p>This page shows trending topics, growth level, paper count, relevance score, and a short insight for each topic.</p>
    </section>

    <section class="trend-cards">
      ${dashboard.trends.map((item) => `
        <article class="trend-card">
          <strong>${item.topic}</strong>
          <span>${item.growth} growth</span>
          <p>${item.insight || "This topic is relevant to the selected research profile."}</p>
          <div class="bar"><span style="width:${item.relevance}%"></span></div>
          <small>${item.relevance}% relevance - ${item.papers || "Sample"} papers</small>
        </article>
      `).join("")}
    </section>

    <section class="panel page-gap">
      <h2>Publication And Emerging Topic Intelligence</h2>
      ${trendsTable(dashboard.trends)}
    </section>
  `;
}

function patentsView() {
  const commercialization = dashboard.commercialization || [
    {
      idea: "AI-based research funding recommender",
      recommendation: "Build as SaaS dashboard for universities and research cells",
      marketPotential: "High",
    },
    {
      idea: "Patent similarity and novelty checker",
      recommendation: "Offer as tool for startups before product development",
      marketPotential: "Medium",
    },
  ];

  return `
    <section class="milestone-banner">
      <div>
        <strong>Milestone 3 Module</strong>
        <span>Patent Analytics + Innovation Intelligence</span>
      </div>
      <p>This page focuses on patent landscape analysis, technology intelligence, innovation scoring, and commercialization recommendations.</p>
    </section>

    <section class="split">
      <div class="panel">
        <h2>Milestone 3 Workflow</h2>
        <div class="workflow">
          <div class="step"><strong>1. Patent Search</strong><span>Check existing patents in the selected technology domain.</span></div>
          <div class="step"><strong>2. Patent Risk</strong><span>Identify whether similar technology already exists.</span></div>
          <div class="step"><strong>3. Innovation Score</strong><span>Evaluate novelty, patent strength, maturity, market potential, and funding relevance.</span></div>
          <div class="step"><strong>4. Commercialization</strong><span>Suggest startup, licensing, SaaS, or partnership opportunities.</span></div>
        </div>
      </div>

      <div class="panel">
        <h2>Innovation Score Breakdown</h2>
        ${scoreTable()}
      </div>
    </section>

    <section class="panel page-gap">
      <h2>Patent Landscape Signals</h2>
      <table>
        <thead>
          <tr>
            <th>Patent</th>
            <th>Assignee</th>
            <th>Domain</th>
            <th>Filing Date</th>
            <th>Citations</th>
            <th>Status</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          ${dashboard.patents.map((patent) => `
            <tr>
              <td>${patent.title}</td>
              <td>${patent.assignee}</td>
              <td><span class="tag">${patent.domain}</span></td>
              <td>${patent.filingDate}</td>
              <td>${patent.citations}</td>
              <td>${patent.status || "Under review"}</td>
              <td>${patent.risk || "Medium"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>

    <section class="panel page-gap">
      <h2>Commercialization Recommendations</h2>
      <table>
        <thead>
          <tr>
            <th>Idea</th>
            <th>Recommendation</th>
            <th>Market Potential</th>
          </tr>
        </thead>
        <tbody>
          ${commercialization.map((item) => `
            <tr>
              <td>${item.idea}</td>
              <td>${item.recommendation}</td>
              <td><span class="tag">${item.marketPotential}</span></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>
  `;
}

function reportsView() {
  return `
    <section class="milestone-banner">
      <div>
        <strong>Milestone 4 Final Review</strong>
        <span>Testing, Reports, Deployment Plan</span>
      </div>
      <p>This page summarizes all milestones and final project status.</p>
    </section>

    <section class="panel">
      <h2>Final Milestone Summary</h2>
      <div class="report-box">
        <p><strong>Milestone 1 Completed:</strong> login page, dashboard prototype, research profile page, module planning, and sample API server.</p>
        <p><strong>Milestone 2 Completed:</strong> funding recommendation workflow, match percentage, eligibility details, research trend page, topic relevance score, and trend insight cards.</p>
        <p><strong>Milestone 3 Completed:</strong> patent analytics page, patent status, patent risk level, innovation score breakdown, and commercialization recommendation section.</p>
        <p><strong>Milestone 4 Completed:</strong> final integration review, reports page, GitHub documentation, testing plan, deployment plan, and final presentation preparation.</p>
      </div>
    </section>

    <section class="split page-gap">
      <div class="panel">
        <h2>Testing Status</h2>
        <div class="workflow">
          <div class="step"><strong>Login Flow</strong><span>Demo login tested and dashboard opens successfully.</span></div>
          <div class="step"><strong>Dashboard Pages</strong><span>Profile, funding, trends, patent analytics, and reports pages checked.</span></div>
          <div class="step"><strong>API Response</strong><span>Sample /api/dashboard endpoint tested with JSON data.</span></div>
          <div class="step"><strong>Browser Testing</strong><span>Prototype tested locally using localhost:8000.</span></div>
        </div>
      </div>

      <div class="panel">
        <h2>Deployment Plan</h2>
        <div class="workflow">
          <div class="step"><strong>Current</strong><span>Local Python server prototype.</span></div>
          <div class="step"><strong>Next</strong><span>Convert backend to FastAPI and connect database.</span></div>
          <div class="step"><strong>Docker</strong><span>Create Dockerfile and Docker Compose for frontend/backend.</span></div>
          <div class="step"><strong>Cloud</strong><span>Deploy final version on AWS, Azure, Render, or Railway.</span></div>
        </div>
      </div>
    </section>

    <section class="panel page-gap">
      <h2>Final Project Status</h2>
      <table>
        <thead>
          <tr>
            <th>Module</th>
            <th>Status</th>
            <th>Remarks</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Authentication</td>
            <td><span class="tag">Prototype Done</span></td>
            <td>Demo login completed; real JWT authentication planned.</td>
          </tr>
          <tr>
            <td>Funding Discovery</td>
            <td><span class="tag">Prototype Done</span></td>
            <td>Match score, eligibility, amount, and deadline shown.</td>
          </tr>
          <tr>
            <td>Research Trends</td>
            <td><span class="tag">Prototype Done</span></td>
            <td>Trend cards, growth, relevance score, and paper count shown.</td>
          </tr>
          <tr>
            <td>Patent Analytics</td>
            <td><span class="tag">Prototype Done</span></td>
            <td>Patent status, risk level, and citation details shown.</td>
          </tr>
          <tr>
            <td>Commercialization</td>
            <td><span class="tag">Prototype Done</span></td>
            <td>Commercialization recommendation section added.</td>
          </tr>
          <tr>
            <td>Deployment</td>
            <td><span class="tag">Planned</span></td>
            <td>Docker and cloud deployment are planned as next improvement.</td>
          </tr>
        </tbody>
      </table>
    </section>
  `;
}

function metric(label, value, note, color) {
  return `<div class="card"><div class="label">${label}</div><div class="value ${color}">${value}</div><div class="note ${color}">${note}</div></div>`;
}

function fundingTable(items) {
  return `
    <table>
      <thead>
        <tr>
          <th>Opportunity</th>
          <th>Domain</th>
          <th>Eligibility</th>
          <th>Amount</th>
          <th>Deadline</th>
          <th>Match</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item) => `
          <tr>
            <td><strong>${item.title}</strong><br><span class="label">${item.reason}</span></td>
            <td><span class="tag">${item.domain}</span></td>
            <td>${item.eligibility || "Not specified"}</td>
            <td>${item.amount || "Not specified"}</td>
            <td>${item.deadline}</td>
            <td>${item.match}%<div class="bar"><span style="width:${item.match}%"></span></div></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function trendsTable(items) {
  return `
    <table>
      <thead>
        <tr>
          <th>Topic</th>
          <th>Growth</th>
          <th>Papers</th>
          <th>Insight</th>
          <th>Relevance</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item) => `
          <tr>
            <td>${item.topic}</td>
            <td><span class="tag">${item.growth}</span></td>
            <td>${item.papers || "Sample"}</td>
            <td>${item.insight || "Relevant to selected profile."}</td>
            <td>${item.relevance}%<div class="bar"><span style="width:${item.relevance}%"></span></div></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function scoreTable() {
  return `
    <table>
      <thead>
        <tr>
          <th>Factor</th>
          <th>Weight</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        ${dashboard.scoreBreakdown.map((item) => `
          <tr>
            <td>${item.factor}</td>
            <td>${item.weight}%</td>
            <td>${item.score}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function fallbackData() {
  return {
    profile: {
      name: "Siri",
      role: "Researcher",
      organization: "Student / Internship Project",
      domains: ["Artificial Intelligence", "Research Analytics", "Innovation"],
      keywords: ["AI", "funding", "patent analytics", "commercialization"],
      technologyAreas: ["Machine Learning", "NLP", "Data Science"],
    },
    metrics: {
      fundingMatches: 24,
      researchHotspots: 9,
      patentSignals: 42,
      innovationScore: 79,
    },
    funding: [
      {
        title: "AI Research Grant",
        domain: "Artificial Intelligence",
        deadline: "30 Aug 2026",
        match: 92,
        eligibility: "Researchers and students",
        amount: "Up to Rs. 5,00,000",
        reason: "Strong match with AI and research analytics keywords.",
      },
      {
        title: "Startup Innovation Seed Fund",
        domain: "Productization",
        deadline: "15 Sep 2026",
        match: 84,
        eligibility: "Startup founders",
        amount: "Up to Rs. 10,00,000",
        reason: "Useful for converting research output into a prototype.",
      },
      {
        title: "University Technology Transfer Grant",
        domain: "Commercialization",
        deadline: "05 Oct 2026",
        match: 78,
        eligibility: "University teams",
        amount: "Up to Rs. 3,00,000",
        reason: "Supports licensing and industry partnerships.",
      },
    ],
    trends: [
      {
        topic: "Responsible AI Evaluation",
        growth: "High",
        relevance: 88,
        papers: 1280,
        insight: "Growing interest in safe and explainable AI systems.",
      },
      {
        topic: "AI-assisted Diagnostics",
        growth: "High",
        relevance: 83,
        papers: 970,
        insight: "Healthcare AI continues to attract research and funding.",
      },
      {
        topic: "Research Knowledge Graphs",
        growth: "Medium",
        relevance: 76,
        papers: 640,
        insight: "Useful for connecting research and patent data.",
      },
    ],
    patents: [
      {
        title: "AI System For Research Recommendation",
        assignee: "Example Labs",
        domain: "NLP",
        filingDate: "2025-11-04",
        citations: 14,
      },
    ],
    scoreBreakdown: [
      { factor: "Research Novelty", weight: 30, score: 82 },
      { factor: "Patent Strength", weight: 20, score: 70 },
      { factor: "Technology Maturity", weight: 15, score: 73 },
      { factor: "Market Potential", weight: 20, score: 78 },
      { factor: "Funding Relevance", weight: 15, score: 81 },
    ],
  };
}

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => render(button.dataset.view));
});

document.getElementById("loginForm").addEventListener("submit", (event) => {
  event.preventDefault();
  showDashboard();
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  showLogin();
});

document.getElementById("exportBtn").addEventListener("click", () => {
  const text = [
    "Research Funding & Innovation Intelligence Platform",
    "Milestone 2 Summary",
    "",
    "Milestone 1 Completed: login page, dashboard prototype, module planning, profile page, and sample API server.",
    "Milestone 2 Completed: funding recommendation page, match percentage display, eligibility details, research trend page, topic relevance score, and trend insight cards.",
    "Next: connect real funding and research APIs, add database storage, improve recommendation algorithm, and start patent analytics for Milestone 3.",
  ].join("\n");

  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "milestone-2-summary.txt";
  link.click();

  URL.revokeObjectURL(url);
});

loadDashboard();