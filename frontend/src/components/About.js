import React from "react";
import "./About.css";

function About({ onNavigate }) {
  const handleStartCreating = () => {
    if (onNavigate) {
      onNavigate("home");
    }
  };

  return (
    <div className="page-container about-page">
      <div className="glass-card">
        <div className="page-header">
          <h1>About GITA</h1>
          <p className="page-subtitle">
            Transforming Videos into Musical Masterpieces
          </p>
        </div>

        <div className="page-content">
          <div className="page-section">
            <h2>Our Mission</h2>
            <p>
              GITA is an innovative AI-powered platform that bridges the gap
              between visual storytelling and musical expression. We believe
              that every video has a unique rhythm and melody waiting to be
              discovered and brought to life.
            </p>
          </div>

          <div className="page-section">
            <h2>How It Works</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🎬</div>
                <h3>Video Analysis</h3>
                <p>
                  Our advanced AI analyzes your video content, detecting visual
                  patterns, emotions, and movement to understand the story
                  you're telling.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🎵</div>
                <h3>Music Generation</h3>
                <p>
                  Using cutting-edge machine learning algorithms, we create
                  original music that perfectly complements your video's mood,
                  tempo, and narrative.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🎨</div>
                <h3>Creative Control</h3>
                <p>
                  Fine-tune your generated music with intuitive controls for
                  tempo, style, instruments, and emotional intensity.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🚀</div>
                <h3>Instant Results</h3>
                <p>
                  Get your custom music track in minutes, not hours. Perfect for
                  content creators, filmmakers, and musicians.
                </p>
              </div>
            </div>
          </div>

          <div className="page-section">
            <h2>Technology</h2>
            <div className="tech-stack">
              <div className="tech-item">
                <h4>Computer Vision</h4>
                <p>Advanced video analysis and scene understanding</p>
              </div>
              <div className="tech-item">
                <h4>Machine Learning</h4>
                <p>Neural networks trained on vast musical datasets</p>
              </div>
              <div className="tech-item">
                <h4>Audio Processing</h4>
                <p>High-quality audio synthesis and mixing</p>
              </div>
              <div className="tech-item">
                <h4>Real-time Processing</h4>
                <p>Optimized algorithms for fast music generation</p>
              </div>
            </div>
          </div>

          {/* <div className="about-section">
            <h2>Our Team</h2>
            <div className="team-grid">
              <div className="team-member">
                <div className="member-avatar">👨‍💻</div>
                <h3>AI Engineers</h3>
                <p>Experts in machine learning and computer vision</p>
              </div>
              <div className="team-member">
                <div className="member-avatar">🎼</div>
                <h3>Music Producers</h3>
                <p>Professional musicians and audio engineers</p>
              </div>
              <div className="team-member">
                <div className="member-avatar">🎬</div>
                <h3>Content Creators</h3>
                <p>Filmmakers and video production specialists</p>
              </div>
            </div>
          </div> */}

          <div className="page-section">
            <h2>Get Started</h2>
            <div className="cta-section">
              <p>
                Ready to transform your videos into musical masterpieces? Upload
                your first video and experience the magic of AI-powered music
                generation.
              </p>
              <button className="cta-button" onClick={handleStartCreating}>
                Start Creating
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;
