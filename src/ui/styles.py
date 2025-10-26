"""Custom CSS styles for the application."""

def get_custom_css() -> str:
    """Get custom CSS for the application."""
    return """
    <style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Text areas */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        font-size: 16px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Cards */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Audio player */
    audio {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Success messages */
    .stSuccess {
        border-radius: 8px;
        animation: slideIn 0.3s ease;
    }
    
    /* Error messages */
    .stError {
        border-radius: 8px;
        animation: shake 0.3s ease;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* History items */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    </style>
    """

