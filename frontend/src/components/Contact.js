import React from "react";
import "./Contact.css";

function Contact() {
  const handleEmailClick = () => {
    window.location.href = "mailto:kaung.s.hein@sjsu.edu";
  };

  const handleGitHubClick = () => {
    window.open("https://github.com/erik-ksth/gita.git", "_blank");
  };

  const handleLandingPageClick = () => {
    window.open("https://gita.ai", "_blank");
  };

  return (
    <div className="page-container contact-page">
      <div className="glass-card">
        <div className="page-header">
          <h1>Contact Us</h1>
          <p className="page-subtitle">Get in touch with the GITA team</p>
        </div>

        <div className="page-content">
          <div className="page-section">
            <h2>Connect With Us</h2>
            <p>
              Have questions about GITA? Want to collaborate? Need technical
              support? We'd love to hear from you! Reach out through any of the
              channels below.
            </p>
          </div>

          <div className="page-section">
            <h2>Get In Touch</h2>
            <div className="contact-cards">
              <div className="contact-card" onClick={handleEmailClick}>
                <div className="contact-icon">📧</div>
                <h3>Email Us</h3>
                {/* <p className="contact-detail">contact@gita.ai</p> */}
                <p className="contact-description">
                  Send us an email for general inquiries, support, or
                  collaboration opportunities.
                </p>
                <div className="contact-action">
                  <span>Send Email →</span>
                </div>
              </div>

              <div className="contact-card" onClick={handleGitHubClick}>
                <div className="contact-icon">🐙</div>
                <h3>GitHub</h3>
                <p className="contact-description">
                  Check out our open-source code, contribute, or report issues
                  on GitHub.
                </p>
                <div className="contact-action">
                  <span>Visit GitHub →</span>
                </div>
              </div>

              {/* <div className="contact-card" onClick={handleLandingPageClick}>
                <div className="contact-icon">🌐</div>
                <h3>Landing Page</h3>
                <p className="contact-detail">gita.ai</p>
                <p className="contact-description">
                  Visit our main website to learn more about GITA and our mission.
                </p>
                <div className="contact-action">
                  <span>Visit Website →</span>
                </div>
              </div> */}
            </div>
          </div>

          {/* <div className="contact-section">
            <h2>Support & Resources</h2>
            <div className="support-grid">
              <div className="support-item">
                <h4>📚 Documentation</h4>
                <p>Comprehensive guides and API documentation for developers</p>
              </div>
              <div className="support-item">
                <h4>💬 Community</h4>
                <p>Join our community forum to connect with other users</p>
              </div>
              <div className="support-item">
                <h4>🎯 Use Cases</h4>
                <p>Explore how others are using GITA in their projects</p>
              </div>
              <div className="support-item">
                <h4>🚀 Updates</h4>
                <p>Stay updated with the latest features and improvements</p>
              </div>
            </div>
          </div> */}

          {/* <div className="contact-section">
            <h2>Business Inquiries</h2>
            <div className="business-info">
              <p>
                Interested in enterprise solutions, partnerships, or custom integrations? 
                Our business development team is ready to help you explore the possibilities 
                of AI-powered music generation for your organization.
              </p>
              <button className="business-button" onClick={handleEmailClick}>
                Contact Business Team
              </button>
            </div>
          </div> */}
        </div>
      </div>
    </div>
  );
}

export default Contact;
