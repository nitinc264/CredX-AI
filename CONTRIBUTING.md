# Contributing to CredX AI

First off, thank you for considering contributing to CredX AI! We're thrilled you're interested in helping make the job search more human. This project started at a hackathon, and we'd love your help to grow it into something even more powerful.

Whether you're fixing a bug, improving documentation, or building a new feature, your contribution is valuable.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

## 🤝 Code of Conduct

To ensure this is a welcoming space for everyone, please follow these simple guidelines:
* **Be Respectful:** Treat everyone with respect. Healthy debate is welcome, but kindness is required.
* **Be Constructive:** All feedback should be given in a way that helps the project improve.
* **Be Patient:** This is a volunteer-driven project. We'll get back to you as soon as we can.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

## 🤔 How You Can Contribute

There are many ways to contribute, and all are welcome!

* 🐞 **Reporting Bugs:** If you find something that isn't working as expected, please [open a new issue](https://github.com/nitinrc264/credx-ai/issues/new) and describe the bug with as much detail as possible.
* 💡 **Suggesting Enhancements:** Have a great idea? We want to hear it! Please [open an issue](https://github.com/nitinrc264/credx-ai/issues/new) to suggest a new feature or improvement.
* 📝 **Improving Documentation:** If you find parts of the `README.md` or other docs that are unclear, or if you want to add more examples, feel free to suggest changes.
* 🧑‍💻 **Working on New Features:** We have a list of ideas we'd love help with! This is a great place to start.

### 🚀 Feature Ideas (Where to Start)

We've already listed some "Future Improvements" in our `README.md`. These are fantastic places to pick up your first task:

* **Real-time job scraping:** Build a scraper (e.g., using Scrapy or BeautifulSoup) to pull in live jobs from a site like LinkedIn, Indeed, or others.
* **Cultural/Work-Style Matching:** Add new fields to the user profile and job data to match on things like "remote-first," "fast-paced startup," or "work-life balance."
* **Mobile-First Redesign:** Our current HTML/CSS is functional, but it could be much more responsive and accessible on mobile devices.
* **Code Cleanup:** As a hackathon project, some code could be refactored for clarity or performance.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

## Getting Started: Your First Contribution

Ready to make a change? Here's the step-by-step process.

### Step 1: Set Up Your Environment

Follow the installation instructions from the `README.md` to get the project running locally.

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** to your local machine:
  	```bash
  	git clone [https://github.com/YOUR_USERNAME/credx-ai.git](https://github.com/YOUR_USERNAME/credx-ai.git)
  	cd credx-ai
  	```
3.  **Create a Virtual Environment:**
  	```bash
  	python -m venv venv
  	```
4.  **Activate it:**
  	* On Windows: `venv\Scripts\activate`
  	* On macOS/Linux: `source venv/bin/activate`
5.s**Install Dependencies:**
  	```bash
  	pip install Flask Flask-Cors pandas "sentence-transformers>=2.2.0" torch torchvision torchaudio PyMuPDF "google-generativeai>=0.3.0"
  	```
6.s**Add Your API Key:**
  	* Open `app.py`.
  	* Replace `API_KEY = "YOUR_GEMINI_API_KEY"` with your actual Google Gemini API key.
7.s**Run the Server:**
  	```bash
  	python app.py
  	```
  	You should now be able to access the app at `http://127.0.0.1:5000`.

### Step 2: Find Something to Work On

* Look for issues labeled **"good first issue"** for tasks we've identified as great for new contributors.
* If you're working on one of the **"Future Improvements,"** please [open a new issue](https://github.com/nitinrc264/credx-ai/issues/new) first to let us know. This helps us avoid duplicated work.
* Once you're ready to start, assign the issue to yourself or leave a comment.

### Step 3: Make Your Changes (The Git Workflow)

1.  **Create a new branch** for your feature or bugfix. This keeps your changes organized.
  	```bash
  	# Use a descriptive branch name
  	git checkout -b feature/add-job-scraper
  	# or
  	git checkout -b fix/resume-parser-bug
  	```
2.s**Write your code!** Make your changes and test them locally to make sure everything still works.
3.s**Commit your changes** with a clear and concise message.
  	```bash
  	git add .
  	git commit -m "feat: Add initial job scraping module"
  	```

### Step 4: Submit a Pull Request (PR)

1.  **Push your branch** to your fork on GitHub:
  	```bash
  	git push origin feature/add-job-scraper
  	```
2.  **Open a Pull Request** on the original `credx-ai` repository.
3.  In your PR description, please provide:
  	* **A clear description** of what you changed.
  	* **A link to the issue** it solves (e.g., `Fixes #42`).
  	* **Any screenshots or GIFs** if you made changes to the UI.

We'll review your PR as soon as we can, provide feedback, and get it merged.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

## 📂 A Quick Look at the Codebase

To help you find your way around, here's what the key files do:

* `app.py`: The main **Flask server**. This handles API routes and serves the frontend.
* `data_handler.py`: Responsible for loading and managing the `jobs.csv` file with Pandas.
* `matching_engine.py`: The core logic that combines all other modules to find and rank job matches.
* `resume_parser.py`: Uses `PyMuPDF` to read the uploaded PDF resume.
* `semantic_matcher.py`: Uses `sentence-transformers` to find semantically similar job titles.
* `skills_scorer.py`: Calculates the skill-based match score.
* `story_generator.py`: Uses the **Gemini API** to generate the personalized "Match Story."
* `templates/index.html`: The main frontend file.
* `static/`: Contains the `style.css` and `script.js` for the frontend.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

## ❓ Questions?

If you're stuck or have any questions, please don't hesitate to **open an issue** and tag one of the project maintainers. We're here to help!

Thank you for helping build CredX AI!
