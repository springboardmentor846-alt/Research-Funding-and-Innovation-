function SummaryCards({ summary }) {
  return (
    <div className="summary">

      <div className="card">
        <h4>Total Funding</h4>
        <p>{summary.total_funding}</p>
      </div>

      <div className="card">
        <h4>Publications</h4>
        <p>{summary.total_publications}</p>
      </div>

      <div className="card">
        <h4>Patents</h4>
        <p>{summary.total_patents}</p>
      </div>

      <div className="card">
        <h4>Innovation Score</h4>
        <p>95%</p>
      </div>

    </div>
  );
}

export default SummaryCards;