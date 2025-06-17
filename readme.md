# 🐦 X.com (Twitter) Galamsey Tweet Scraper

This Python script is designed to scrape tweets containing the keyword "galamsey" from X.com (formerly Twitter). It utilizes `undetected-chromedriver` and `Selenium` to automate browser interactions, including logging in and scrolling through search results to collect a target number of tweets.

---

## ✨ Features

* **Targeted Scraping**: Collects tweets based on a specific keyword ("galamsey").
* **Persistent Scrolling**: Employs an intelligent scrolling mechanism to load more tweets dynamically.
* **Batch Processing**: Fetches tweets in batches and introduces strategic pauses to prevent rate limiting and ensure more content loads.
* **Login Automation**: Handles X.com login to access search results using securely managed credentials.
* **Data Export**: Saves scraped tweet data (username, content, timestamp, replies, retweets, likes, URL) to a CSV file.
* **Brave Browser Support**: Configured to work specifically with Brave browser for enhanced stealth.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.x**: Download from [python.org](https://www.python.org/).
* **Brave Browser**: Download and install Brave from [brave.com](https://brave.com/).
* **Git**: For cloning the repository.

---

## 🚀 Getting Started

Follow these steps to get the scraper up and running on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone [https://github.com/Daemonlite/Python-selenium-twitter-galamsey-data.git](https://github.com/Daemonlite/Python-selenium-twitter-galamsey-data.git)
cd Python-selenium-twitter-galamsey-data
```
#### 2. Create a .env File with credentials to x
```bash
touch .env
```
#### Fill in X_USERNAME and X_PASSWORD in env variable
