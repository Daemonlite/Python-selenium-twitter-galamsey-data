import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

import undetected_chromedriver as uc
from decouple import config

def scrape_galamsey_tweets(output_file="galamsey_tweets.csv", min_tweets=1000, batch_size=100, batch_wait_time=15):
    """
    Scrapes tweets containing the keyword "galamsey" from x.com (Twitter)
    and saves them to a CSV file. It attempts to fetch data in batches
    and waits to load more posts to reach the min_tweets target.

    Args:
        output_file (str): The name of the CSV file to save the tweets.
        min_tweets (int): The minimum number of tweets to attempt to scrape.
        batch_size (int): The number of tweets to collect before a longer batch_wait_time.
        batch_wait_time (int): The extended time to wait (in seconds) after each batch.
    """
    # Set up Brave browser options
    options = uc.ChromeOptions()

    # Path to Brave browser (common installation locations)
    # configure for your system
    brave_paths = [
        "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
        f"C:/Users/{os.getlogin()}/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe"
    ]

    # Find Brave browser path
    brave_path = None
    for path in brave_paths:
        if os.path.exists(path):
            brave_path = path
            break

    if not brave_path:
        print("Brave browser not found. Please ensure Brave is installed.")
        return None

    print(f"Brave browser found at: {brave_path}")
    options.binary_location = brave_path

    # Additional options
    # options.add_argument('--headless')  # Comment out if you need to debug visually.
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--incognito') 

    driver = None
    try:
        print("Setting up undetected-chromedriver for Brave...")
        driver = uc.Chrome(options=options, browser_executable_path=brave_path)
        print("Driver initialized successfully")

        # Login to Twitter
        print("Navigating to Twitter login...")
        driver.get("https://x.com/i/flow/login")
        time.sleep(5)

        # Fill in username
        print("Entering username...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                username_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
                )
                username_input.send_keys(config("X_USERNAME"))
                username_input.send_keys(Keys.RETURN)
                time.sleep(5)
                break # Exit loop if successful
            except TimeoutException:
                print(f"Attempt {attempt + 1}: Username input field not found. Retrying...")
                if attempt == max_retries - 1:
                    print("Max retries reached. Please manually log in.")
                    input("Press Enter after logging in manually...")
                    time.sleep(5) # Give browser time to load after manual intervention

        # Handle password or additional verification
        if "login" in driver.current_url or "challenge" in driver.current_url:
            for attempt in range(max_retries):
                try:
                    print("Entering password...")
                    password_input = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
                    )
                    password_input.send_keys(config("X_PASSWORD"))
                    password_input.send_keys(Keys.RETURN)
                    time.sleep(7)
                    break # Exit loop if successful
                except TimeoutException:
                    print(f"Attempt {attempt + 1}: Password field not found. Retrying...")
                    if attempt == max_retries - 1:
                        print("Max retries reached. Please manually complete login.")
                        input("Press Enter after logging in manually...")
                        time.sleep(5) # Give browser time to load after manual intervention

        # Crucial Login Verification
        if "x.com/home" not in driver.current_url and "x.com/search" not in driver.current_url:
            print("\n!!! Login likely failed or requires further manual intervention !!!")
            print(f"Current URL: {driver.current_url}")
            input("Please manually complete Twitter login in the browser window and press Enter here to continue scraping...")
            time.sleep(5)

        # Search for tweets
        print("Searching for galamsey tweets...")
        search_url = "https://x.com/search?q=galamsey&src=typed_query"
        driver.get(search_url)
        time.sleep(7)

        # Initial small scroll to ensure content loads
        driver.execute_script("window.scrollTo(0, 200);")
        time.sleep(2)

        # Scroll and collect tweets
        tweets_data = []
        collected_tweet_ids = set() # To store unique tweet IDs (from URL) and avoid duplicates
        last_position = driver.execute_script("return window.pageYOffset;")
        scrolling = True
        scroll_attempts = 0
        max_scroll_attempts = 500 # Increased max scroll attempts for more data

        while scrolling and len(tweets_data) < min_tweets and scroll_attempts < max_scroll_attempts:
            scroll_attempts += 1

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
                )
            except TimeoutException:
                print("\nNo new tweets loaded after waiting during scroll, stopping.")
                scrolling = False
                break
            except WebDriverException as e:
                print(f"\nWebDriver error during tweet presence check: {e}")
                print("This might indicate Twitter blocking or a network issue.")
                scrolling = False
                break

            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            
            new_tweets_in_batch = 0

            for tweet in tweets:
                try:
                    # Get tweet URL to derive a unique ID
                    tweet_url_element = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                    tweet_full_url = tweet_url_element.get_attribute('href')
                    tweet_id = tweet_full_url.split('/')[-1] if tweet_full_url else None

                    if tweet_id and tweet_id not in collected_tweet_ids:
                        collected_tweet_ids.add(tweet_id)

                        username_element = tweet.find_element(By.XPATH, './/span[contains(text(), "@")]')
                        username = username_element.text if username_element else "N/A"

                        content_element = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                        content = content_element.text if content_element else "N/A"

                        timestamp_element = tweet.find_element(By.XPATH, './/time')
                        timestamp = timestamp_element.get_attribute('datetime') if timestamp_element else "N/A"

                        replies = "0"
                        retweets = "0"
                        likes = "0"

                        try:
                            reply_element = tweet.find_element(By.XPATH, './/div[@data-testid="reply"]')
                            reply_count_span = reply_element.find_element(By.XPATH, './/span[@data-testid="app-text-transition-container"]/span')
                            replies = reply_count_span.text if reply_count_span.text else "0"
                        except NoSuchElementException:
                            pass

                        try:
                            retweet_element = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
                            retweet_count_span = retweet_element.find_element(By.XPATH, './/span[@data-testid="app-text-transition-container"]/span')
                            retweets = retweet_count_span.text if retweet_count_span.text else "0"
                        except NoSuchElementException:
                            pass

                        try:
                            like_element = tweet.find_element(By.XPATH, './/div[@data-testid="like"]')
                            like_count_span = like_element.find_element(By.XPATH, './/span[@data-testid="app-text-transition-container"]/span')
                            likes = like_count_span.text if like_count_span.text else "0"
                        except NoSuchElementException:
                            pass

                        tweet_data = {
                            'username': username,
                            'content': content,
                            'timestamp': timestamp,
                            'replies': replies,
                            'retweets': retweets,
                            'likes': likes,
                            'url': tweet_full_url # Add tweet URL for reference
                        }

                        tweets_data.append(tweet_data)
                        new_tweets_in_batch += 1
                        print(f"Collected {len(tweets_data)} tweets", end='\r')

                    if len(tweets_data) >= min_tweets:
                        scrolling = False
                        break

                except NoSuchElementException:
                    continue
                except Exception as inner_e:
                    print(f"Error processing tweet: {inner_e}")
                    continue

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6) # Short pause after each scroll

            # Check if we've reached the end
            new_position = driver.execute_script("return window.pageYOffset;")
            if new_position == last_position:
                print("\nReached end of page or rate limited/no new content. Unable to scroll further.")
                scrolling = False
            last_position = new_position

            # Batching logic: If we collected a new batch, wait longer
            if new_tweets_in_batch > 0 and (len(tweets_data) % batch_size < new_tweets_in_batch or len(tweets_data) % batch_size == 0):
                if len(tweets_data) < min_tweets: # Only wait if we still need more tweets
                    print(f"\nCollected {len(tweets_data)} tweets. Waiting for {batch_wait_time} seconds to load more...")
                    time.sleep(batch_wait_time)


        # Save to CSV
        if tweets_data:
            keys = tweets_data[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(tweets_data)
            print(f"\nSuccessfully saved {len(tweets_data)} tweets to {output_file}")
        else:
            print("\nNo tweets were collected.")
        return tweets_data

    except Exception as e:
        print(f"\nAn error occurred during scraping: {e}")
        return None
    finally:
        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    print("Checking for package updates...")
    try:
        import subprocess
        subprocess.run(['pip', 'install', '--upgrade', 'undetected-chromedriver', 'selenium'], check=True)
    except Exception as e:
        print(f"Package update check failed: {e} - continuing anyway")

    # Call the scraping function with desired parameters
    # This will try to get 1000 tweets, waiting 15 seconds after every 100 new tweets.
    scrape_galamsey_tweets(min_tweets=1000, batch_size=100, batch_wait_time=15)