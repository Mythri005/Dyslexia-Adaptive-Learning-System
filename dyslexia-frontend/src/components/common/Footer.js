import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>© {new Date().getFullYear()} Dyslexia Adaptive Learning System. Helping every child learn better.</p>
      </div>
    </footer>
  );
};

export default Footer;