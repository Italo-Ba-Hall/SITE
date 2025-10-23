import React, { useEffect } from 'react';
import './FiscalReportPage.css';

/**
 * FiscalReportPage Component
 *
 * Displays the Tax Reform Analysis Report (Reforma Tributária)
 * in an embedded iframe while maintaining Hall-Dev site navigation.
 *
 * Features:
 * - Full-height iframe integration
 * - Maintains site animations (AnimationIntro + BackgroundCanvas)
 * - Preserves Navbar with YouTube button
 * - Seamless navigation experience
 */
const FiscalReportPage: React.FC = () => {
  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);

    // Optional: Track page view for analytics
    document.title = 'HALL-DEV TAX Intelligence | Reforma Tributária 2025';

    return () => {
      // Reset title on unmount
      document.title = 'React App';
    };
  }, []);

  return (
    <div className="fiscal-report-container">
      <iframe
        src="/fiscal-report.html"
        title="Reforma Tributária Brasileira - Análise Estratégica 2025"
        className="fiscal-report-iframe"
        loading="lazy"
        sandbox="allow-scripts allow-same-origin allow-forms"
      />
    </div>
  );
};

export default FiscalReportPage;
