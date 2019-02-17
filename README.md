# transcript-selenium-spider
### Usage
1. If you are not using Windows, download the chromedriver from <https://sites.google.com/a/chromium.org/chromedriver/downloads> and place it to project directory

2. Create config.py in project directory
```
student_id = 'YOUR STUDENT ID'
password = 'YOUR PASSWORD'

# The browser window will not be displayed when True
headless = False  # True or False

# Check interval(second)
interval = 60 * 5

# Start the telegram bot when True
start_bot = False

# Start a conversation with the @BotFather and create a bot using the "/newbot" command
telegram_bot_token = 'TOKEN'

# Send '/start' to the bot in telegram to get your user id
my_user_id = 12345678  
```
3. Run spider.py

# Disclaimer
transcript_selenium_spider is intended for academic purposes. Use at your own risk.
