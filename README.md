# transcript_selenium_spider
### Usage
1. Create config.py
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
self_user_id = 12345678  
```
2. Run spider.py
