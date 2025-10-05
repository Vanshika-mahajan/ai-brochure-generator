# AI-Powered Brochure Generator 🚀

This project is a full-stack web application that automatically generates a professional company brochure from a single URL. It intelligently scrapes, analyzes, and summarizes website content using AI and NLP models, then assembles it into a downloadable PDF.



## Features ✨

-   **Intelligent Web Crawling:** Navigates websites to find and scrape content from key pages (e.g., "About Us", "Services").
-   **AI Content Classification:** Uses a Hugging Face Zero-Shot model to understand the purpose of each page.
-   **Automated Summarization & QA:** Leverages NLP models to create concise summaries and extract key offerings.
-   **Image & Logo Detection:** Automatically identifies and extracts the company logo and other relevant images.
-   **Dynamic PDF Generation:** Assembles all extracted data into a clean, professional PDF brochure.
-   **Robust Fallback System:** If intelligent classification fails, it defaults to using all scraped text to ensure a brochure is always created.
-   **Web Interface:** Simple and clean front end built with Flask to provide a user-friendly experience.

## Tech Stack 🛠️

-   **Backend:** Python, Flask
-   **AI / NLP:** Hugging Face Transformers (Summarization, Question-Answering, Zero-Shot Classification)
-   **Web Scraping:** BeautifulSoup, Requests
-   **PDF Generation:** ReportLab
-   **Frontend:** HTML, CSS, JavaScript

## Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

-   Python 3.8+
-   Git

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
