import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import './ProgressReport.css';
import html2pdf from "html2pdf.js";

const ProgressReport = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser } = useUser();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReportData = async () => {
      try {
        if (location.state?.results) {
          setReportData({
            module: location.state.module,
            mode: location.state.mode,
            isCurrentSession: true,
            timestamp: new Date().toISOString(),
            ...(location.state.results.report || location.state.results)
          });
        } else {
            const response = await fetch(
              `http://localhost:5001/api/progress/${currentUser?.id}`
            );
            
          const data = await response.json();

          setReportData({
            isCurrentSession: false,
            userProgress: data,
            overallProgress: calculateOverallProgress(data)
          });
        }
      } catch (error) {
        console.error('Error loading report:', error);
      } finally {
        setLoading(false);
      }
    };

    loadReportData();
  }, [location, currentUser]);

  const getGrade = (accuracy) => {
    if (accuracy >= 90) return { grade: 'A+', color: '#4CAF50' };
    if (accuracy >= 80) return { grade: 'A', color: '#4CAF50' };
    if (accuracy >= 70) return { grade: 'B', color: '#FF9800' };
    if (accuracy >= 60) return { grade: 'C', color: '#FF9800' };
    if (accuracy >= 50) return { grade: 'D', color: '#F44336' };
    return { grade: 'F', color: '#999' };
  };

  const generateSuggestions = (modules) => {
    const suggestions = [];
    if (!modules) return ["Complete modules to receive suggestions"];

    Object.keys(modules).forEach(module => {
      const m = modules[module];
      if (!m || !m.attempted) {
        suggestions.push(`Try starting the ${module.toUpperCase()} module`);
        return;
      }

      if (m.averageAccuracy >= 85) {
        suggestions.push(`Great performance in ${module.toUpperCase()} — keep it up!`);
      } else if (m.averageAccuracy >= 60) {
        suggestions.push(`Good progress in ${module.toUpperCase()}, practice more`);
      } else {
        suggestions.push(`Focus more on ${module.toUpperCase()} — needs improvement`);
      }
    });

    return suggestions;
  };

  const calculateOverallProgress = (progress = {}) => {
    const modules = ['math', 'spelling', 'reading'];
    let totalPoints = 0;
    let totalAccuracy = 0;
    let attemptedCount = 0;
    const normalized = {};

    modules.forEach(module => {
      const data = progress[module];

        if (!data) {
          normalized[module] = {
            reportsCount: 0,
            totalPoints: 0,
            averageAccuracy: 0,
            attempted: false
          };
          return;
        }

        const points = data.total_points || 0;
        const attempted = data.questions_attempted || 0;
        const correct = data.questions_correct || 0;

        const accuracy = attempted ? Math.round((correct / attempted) * 100) : 0;

        normalized[module] = {
          reportsCount: attempted ? Math.ceil(attempted / 5) : 0,
          totalPoints: points,
          averageAccuracy: accuracy,
          attempted: attempted > 0
        };

      totalPoints += points;
      totalAccuracy += accuracy;
      attemptedCount++;
    });

    const finalAccuracy = attemptedCount
      ? Math.round(totalAccuracy / attemptedCount)
      : 0;

    return {
      normalizedModules: normalized,
      totalPoints,
      averageAccuracy: finalAccuracy,
      grade: getGrade(finalAccuracy).grade
    };
  };

  const getModuleIcon = (module) => {
    if (module === 'math') return '🔢';
    if (module === 'spelling') return '📝';
    if (module === 'reading') return '📖';
    return '🎯';
  };

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

  // UPDATED handlePrint FUNCTION with the 2-line fix
  const handlePrint = () => {
    const content = document.getElementById("print-area");
    if (!content) return alert("Print area not found");

    const clone = content.cloneNode(true);
    
    // remove buttons before printing - FIX (2 lines)
    clone.querySelectorAll(".no-print").forEach(el => el.remove());
    clone.querySelectorAll(".report-actions").forEach(el => el.remove());

    const printWindow = window.open("", "_blank", "width=900,height=650");

    printWindow.document.write(`
      <html>
        <head>
          <title>Progress Report</title>
          <style>
            body{font-family:Arial;padding:20px}
            table{width:100%;border-collapse:collapse}
            th,td{border:1px solid #ccc;padding:8px;text-align:center}
            th{background:#667eea;color:white}
          </style>
        </head>
        <body>${clone.innerHTML}</body>
      </html>
    `);

    printWindow.document.close();
    printWindow.onload = () => {
      printWindow.print();
      printWindow.close();
    };
  };

  const downloadCertificate = () => {

  const element = document.querySelector(".progress-report");

  if (!element) {
    alert("Certificate area not found");
    return;
  }

  // Clone page so we can remove buttons
  const clone = element.cloneNode(true);

  // Remove buttons and actions
  clone.querySelectorAll(".report-actions").forEach(el => el.remove());
  clone.querySelectorAll(".no-print").forEach(el => el.remove());

  const opt = {
    margin: 10,
    filename: "certificate.pdf",
    image: { type: "jpeg", quality: 1 },
    html2canvas: {
      scale: 1.5,
      useCORS: true
    },
    jsPDF: {
      unit: "mm",
      format: "a4",
      orientation: "portrait"
    }
  };

  html2pdf()
  .set(opt)
  .from(clone)
  .toPdf()
  .get('pdf')
  .then(function (pdf) {

    const pages = pdf.internal.getNumberOfPages();

    if (pages > 1) {
      pdf.deletePage(pages);   // removes blank page
    }

  })
  .save();

};

  if (loading) {
    return (
      <div className="progress-report loading">
        <div className="loading-spinner">📊</div>
        <h2>Loading Your Progress Report...</h2>
      </div>
    );
  }

  if (reportData?.isCurrentSession) {
    const accuracy = reportData.accuracy || 0;
    const grade = getGrade(accuracy);

    return (
      <div className="progress-report" id="print-area">
        <div className="report-header card">
          <h1>📊 Session Report</h1>
          <div className="student-info">
            <div><strong>Student:</strong> {currentUser?.name}</div>
            <div><strong>Age:</strong> {currentUser?.age}</div>
            <div><strong>Date:</strong> {formatDate(reportData.timestamp)}</div>
          </div>
        </div>

        <div className="module-performance card">
          <h2>{reportData.module?.toUpperCase()}</h2>

          <div className="performance-grid">
            <div className="performance-card main-score">
              <div className="score-grade">{grade.grade}</div>
              <div className="score-value">{accuracy}%</div>
            </div>

            <div className="performance-card">
              Correct: {reportData.correct_answers || reportData.correct_pronunciations || 0}
            </div>

            <div className="performance-card">
              Points: {reportData.points_earned || 0}
            </div>
          </div>
        </div>

        <div className="report-actions">
          <button onClick={() => navigate('/modules')} className="btn btn-success">Continue</button>
          <button onClick={handlePrint} className="btn">📄 Print</button>
        </div>
      </div>
    );
  }

  const { overallProgress } = reportData || {};
  const modules = overallProgress?.normalizedModules || {};

  return (
    <div className="progress-report" id="print-area">
      <div className="report-header card">
        <h1>📊 Master Learning Report</h1>
        <div className="student-info">
          <div><strong>Student:</strong> {currentUser?.name}</div>
          <div><strong>Age:</strong> {currentUser?.age}</div>
          <div><strong>Generated:</strong> {formatDate(new Date())}</div>
        </div>
      </div>

      {/* Overall Performance section with table */}
      <div className="overall-progress card">
        <h2>📈 Overall Performance</h2>

        <table className="report-table">
          <tbody>
            <tr>
              <th>Total Points</th>
              <td>{overallProgress?.totalPoints || 0}</td>
            </tr>
            <tr>
              <th>Accuracy</th>
              <td>{overallProgress?.averageAccuracy || 0}%</td>
            </tr>
            <tr>
              <th>Grade</th>
              <td>{overallProgress?.grade || "—"}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Module Summary Block with Table */}
      <div className="module-progress-section card">
        <h2>📚 Module Summary</h2>

        <table className="report-table">
          <thead>
            <tr>
              <th>Module</th>
              <th>Reports</th>
              <th>Total Points</th>
              <th>Accuracy</th>
              <th>Grade</th>
            </tr>
          </thead>

          <tbody>
            {['math','spelling','reading'].map(module => {

              const progress = modules[module] || {};
              const grade = getGrade(progress.averageAccuracy || 0);

              return (
                <tr key={module}>
                  <td>{getModuleIcon(module)} {module.toUpperCase()}</td>
                  <td>{progress.attempted ? progress.reportsCount : "-"}</td>
                  <td>{progress.attempted ? progress.totalPoints : "-"}</td>
                  <td>{progress.attempted ? `${progress.averageAccuracy}%` : "-"}</td>
                  <td style={{color:grade.color,fontWeight:"bold"}}>
                    {progress.attempted ? grade.grade : "-"}
                  </td>
                </tr>
              );

            })}
          </tbody>
        </table>

      </div>

      <div className="overall-progress card">
        <h2>🧠 Suggestions to Improve</h2>
        <ul>
          {generateSuggestions(modules).map((tip, i) => (
            <li key={i}>👉 {tip}</li>
          ))}
        </ul>
      </div>

      <div className="certificate-id card">
        <h3>🎓 Certificate ID</h3>
        <p>
          DAL-${Date.now().toString().slice(-6)}
        </p>
      </div>

      <div className="report-actions no-print">
        <button onClick={() => navigate('/modules')} className="btn btn-success">Continue Learning</button>
        <button onClick={handlePrint} className="btn">📄 Print Report</button>
        <button onClick={downloadCertificate} className="btn btn-success">🎓 Download Certificate</button>
      </div>
    </div>
  );
};

export default ProgressReport;