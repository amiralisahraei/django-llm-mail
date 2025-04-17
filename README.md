# Django-based Gmail Categorization App Powered by LLMs

A Django-based web application that fetches, analyzes, and intelligently categorizes Gmail messages using **Large Language Models (LLMs)** for deeper contextual sentiment understanding. This AI-driven app offers a modern interface to explore and filter your inbox based on nuanced sentiment categories.

## 🔍 Key Highlights

- **LLM-Enhanced Email Categorization**
  - Uses transformer-based models for context-aware sentiment analysis
  - Goes beyond basic keyword analysis to detect subtle sentiment and intent
  - Custom or fine-tuned LLM models supported (e.g., DistilBERT, RoBERTa)

- **Seamless Django Integration**
  - Modular architecture for LLM inference pipelines
  - Django views and services designed to interface with local or cloud-hosted LLMs
  - Built-in support for extending with other NLP tasks (e.g., spam detection, topic extraction)

- **User-Friendly Gmail Dashboard**
  - Gmail OAuth2 login
  - Smart email sync with real-time status
  - Interactive dashboard with sentiment filters and insights

## ✨ Features

- **Authentication & Security**
  - Django-powered secure login/signup
  - Per-user Gmail authorization via OAuth2
  - Encrypted token storage

- **Intelligent Email Processing**
  - Gmail API integration
  - LLM-based sentiment and emotion classification
  - Categorization: Positive, Negative, Neutral
  - Scalable pipeline design with pagination (20 emails/page)
  - Filter & explore by sentiment

- **Modern UI/UX**
  - Responsive, minimalist dashboard
  - Collapsible email previews
  - Visual sentiment indicators
  - Error handling and feedback alerts

## 🧠 Technologies

- **Backend**
  - Python 3.8+
  - Django 4.0+
  - Gmail API
  - Google OAuth2
  - SQLite / PostgreSQL

- **AI Layer**
  - HuggingFace Transformers
  - PyTorch or TensorFlow (backend agnostic)
  - Pretrained and fine-tuned LLMs for sentiment analysis

- **Frontend**
  - HTML5/CSS3
  - JavaScript (vanilla or minimal frameworks)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gmail_categorization.git
cd gmail_categorization
```

### 2. Set Up Your Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your Gmail API credentials and Django secret key
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Launch the App
```bash
python manage.py runserver
```

---

## 🔧 Google API Setup

- Create a project in the Google Cloud Console  
- Enable Gmail API  
- Set up OAuth consent screen  
- Create OAuth 2.0 credentials  
- Download and save `client_secrets.json` in the project root  

---

## 📂 Project Structure

```
gmail_categorization/
├── gmail_categorization_app/
│   ├── processing/
│   │   ├── gmail_api.py              # Gmail fetching logic
│   │   ├── load.py                   # Token & Gmail sync utils
│   │   └── sentiment_analysis.py     # LLM integration
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── manage.py
└── README.md
```

---

## ⚙️ Configuration

### `settings.py` Snippet
```python
INSTALLED_APPS = [
    ...
    'gmail_categorization_app',
]

LOGIN_REDIRECT_URL = '/profile/'  
LOGOUT_REDIRECT_URL = '/login/'
```

### Required Environment Variables
```
GROQ_API_KEY=your-api-key
MODEL_NAME=deepseek-r1-distill-llama-70b
```

---

## 🧪 Usage

- Register a user account  
- Authorize Gmail access  
- LLM will analyze synced emails  
- View categorized emails by sentiment  
- Filter by category and browse pages  

---

## 🔐 Security Best Practices

- OAuth2 token encryption  
- CSRF protection  
- Strong password validation  
- Authentication rate limiting  

---

## 🤝 Contributing

- Fork the repo  
- Create a new feature branch  
- Commit your changes  
- Open a Pull Request  

---

## 📜 License

Licensed under the MIT License. See `LICENSE` file.

---

## 👨‍💻 Author

**Your Name**  
📧 your.email@example.com

---

## 🙏 Acknowledgments

- HuggingFace Transformers  
- Gmail API Documentation  
- Django Documentation  
- Open-source contributors