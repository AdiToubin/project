# Flask MVC Application

A Flask-based web application following the MVC (Model-View-Controller) architecture pattern, ready for cloud deployment.

## 📁 Project Structure

```
project/
├── app.py               ← Application server (Flask)
├── model/
│   └── logic.py         ← Core logic layer (processing / calculations)
├── static/              ← Frontend assets (CSS, JS)
│   ├── style.css
│   └── app.js
├── templates/           ← HTML views
│   └── index.html
├── requirements.txt     ← Python dependencies
├── Procfile            ← Cloud deployment configuration
├── runtime.txt         ← Python version specification
└── README.md
```

## 🚀 Cloud Deployment Options

### Option 1: Render (Recommended)

1. **Create a Render account** at [render.com](https://render.com)

2. **Connect your GitHub repository**:
   - Go to Dashboard → New → Web Service
   - Connect your GitHub account and select this repository

3. **Configure the service**:
   - **Name**: Choose a name for your app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or paid for production)

4. **Environment Variables** (optional):
   - `SECRET_KEY`: Your secret key for session management

5. **Deploy**: Click "Create Web Service"

Your app will be available at: `https://your-app-name.onrender.com`

### Option 2: Railway

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository

3. **Configuration** (automatic detection):
   - Railway will auto-detect Python and use the Procfile
   - Add environment variables in Settings if needed

4. **Generate domain**:
   - Go to Settings → Generate Domain

Your app will be deployed automatically with CI/CD enabled.

### Option 3: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   ```

Your app will be available at: `https://your-app-name.herokuapp.com`

## 💻 Local Development

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory (not committed to git):

```env
SECRET_KEY=your-secret-key-here
PORT=5000
```

### Python Version

The application requires Python 3.10+. The version is specified in [runtime.txt](runtime.txt).

## 📡 API Endpoints

- `GET /` - Main application page
- `GET /health` - Health check endpoint
- `POST /api/calculate` - Perform calculations
  ```json
  {
    "num1": 10,
    "num2": 5,
    "operation": "add"
  }
  ```
- `POST /api/process` - Process data
  ```json
  {
    "data": "your data here"
  }
  ```

## 🏗️ MVC Architecture

- **Model** ([model/logic.py](model/logic.py)): Business logic and data processing
- **View** ([templates/](templates/)): HTML templates for rendering
- **Controller** ([app.py](app.py)): Flask routes and request handling

## 🔄 CI/CD Setup

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml` for automated testing and deployment.

### Auto-Deploy on Git Push

Most cloud platforms (Render, Railway, Heroku) support auto-deploy:
- Every push to `main` branch triggers automatic deployment
- Configure in your cloud platform's dashboard

## 📝 Development Notes

- The app uses `gunicorn` as the production WSGI server
- Static files are served from the `static/` directory
- Templates use Jinja2 templating engine
- CORS is not enabled by default (add `flask-cors` if needed)

## 🛡️ Security Considerations

- **Never commit** `.env` files or secrets to git
- Set `SECRET_KEY` as environment variable in production
- Use HTTPS in production (automatic on most cloud platforms)
- Review and update dependencies regularly

## 📦 Adding Dependencies

1. Install the package:
   ```bash
   pip install package-name
   ```

2. Update requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

## 🚧 Troubleshooting

### Port Issues
- Ensure the `PORT` environment variable is set correctly
- Cloud platforms usually set this automatically

### Module Not Found
- Verify all dependencies are in [requirements.txt](requirements.txt)
- Run `pip install -r requirements.txt`

### Static Files Not Loading
- Check file paths in templates use `url_for('static', filename='...')`
- Ensure static files exist in the `static/` directory

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**Ready to deploy!** Choose your preferred cloud platform above and follow the deployment steps.
