# CredX AI - Your Personal Career Trajectory Engine

Ever felt like you're shouting into the void when applying for jobs? You spend hours polishing your resume and sending it out, only to get back a flood of irrelevant listings. We've been there, and we thought: "There has to be a better way."

That’s why we built CredX AI — a hackathon project designed to make the job search feel less like a chore and more like a conversation. Instead of just matching keywords, our engine tries to understand who you are and what you really want in your next role.

## 🚀 The Big Idea

The problem with most job sites is that they're not very smart. They see "JavaScript" on your resume and show you every single job that mentions it. They don’t know if you’re a seasoned pro or just starting out, what you want to earn, or what kind of company culture you’d thrive in.

**Here’s how CredX AI is different:**
- It Actually Reads Your Resume – Upload your resume, and our AI instantly gets a sense of your skills and experience to build your profile. No more endless forms.
- You're in the Driver's Seat – You decide what matters most (salary, job title, location, etc.) by adjusting sliders.
- It Understands What You Mean – Knows that a "Lead Product Designer" is relevant to "UI/UX Design" skills, going beyond simple keyword matching.
- It Tells You Why – Every recommendation comes with a short "Match Story", explaining why the role fits you.

<img src="(https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)" width="100%">

## 🛠️ How We Built It (Hackathon Story)

We wanted to build something powerful yet practical during the hackathon.

### Tech Stack Overview:
- Backend: Python + Flask (simple and fast for building APIs).
- Frontend: Vanilla HTML, CSS, JavaScript (lightweight and responsive).
- AI Magic:
  - Google Gemini 1.5 Flash → Reads resumes, builds profiles, and generates personalized Match Stories.
  - Sentence-Transformers → Local lightweight model for semantic matching (e.g., understanding React ≈ Web Development).
- Data: Pandas for handling job listings in-memory.

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## ⚙️ Run It Yourself

### Requirements
- Python 3.8+
- pip (Python package installer)
- Google Gemini API Key

### 📂 Project Structure

credx-ai/
|-- data/
|   |-- jobs.csv
|-- static/
|   |-- script.js
|   |-- style.css
|-- templates/
|   |-- index.html
|-- app.py
|-- data_handler.py
|-- matching_engine.py
|-- resume_parser.py
|-- semantic_matcher.py
|-- skills_scorer.py
|-- story_generator.py


### 🔧 Installation
1.  **Clone or Create Project Folder**

    cd credx-ai

2.  **Create Virtual Environment**
  
    python -m venv venv

    Activate it:
    - On Windows: `venv\Scripts\activate`
    - On macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies**

    pip install Flask Flask-Cors pandas "sentence-transformers>=2.2.0" torch torchvision torchaudio PyMuPDF "google-generativeai>=0.3.0"
  
    *Note: The first run will download the Sentence-Transformers model (grab a coffee ☕).*

4.  **Add API Key**
    - Open `app.py`
    - Replace the placeholder: `API_KEY = "YOUR_GEMINI_API_KEY"`

5.  **Run the Server**

    python app.py
    The server will start at: http://127.0.0.1:5000

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## 📖 How to Use

### Tell Us About Yourself
- **Upload Resume (PDF):** AI auto-fills your profile.
- **Manual Input:** Enter skills, dream job titles, preferences (comma-separated).

### Set Priorities
- Use sliders under "What Matters Most?" (e.g., salary, job title, location).

### Find Jobs
- Click "Find My Future Job" to get recommendations.

### Check Matches
- A personalized job list appears with short AI-written Match Stories.

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## 🏆 Why CredX AI?

- Smarter job matching.
- Personalized insights.
- Faster, easier, and more human job search.

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## 💡 Future Improvements

- Real-time job scraping from popular job boards.
- More granular cultural and work-style matching.
- Mobile-first redesign for accessibility.

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## Output:
<img width="1902" height="906" alt="Screenshot 2025-08-16 195642" src="https://github.com/user-attachments/assets/5a78ae2a-3cd0-4c20-aaa0-56c712fcc3c7" />

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## Demo Link  
[View Demo](https://drive.google.com/file/d/1PwaxuSsKrxdTDLMEYcITFjXXBiCwXuCN/view?usp=sharing)

<img src="YOUR_IMAGE_URL_GOES_HERE" width="100%">

## 🤝 Contributing

We’d love your feedback and contributions! Feel free to fork this repo, open issues, or submit pull requests.

---

## 📜 License

This project was built for a hackathon — free to use for educational and experimental purposes.
