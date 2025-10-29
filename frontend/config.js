// API Configuration
// This will automatically detect the correct API URL based on the environment
const getApiUrl = () => {
    // If running on localhost, use localhost backend
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000/api';
    }
    
    // In production/EC2, use the same host but port 8000
    // This works because both frontend (port 3000) and backend (port 8000) are on the same EC2 instance
    const protocol = window.location.protocol; // http: or https:
    const hostname = window.location.hostname; // EC2 public IP or domain
    return `${protocol}//${hostname}:8000/api`;
};

const API_URL = getApiUrl();
