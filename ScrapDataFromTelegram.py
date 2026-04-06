#Code to Scrap data from telegram group

#pip install asyncio (py library to alow concurrent asynchronous programming)
#pip install telethon (py library to access telegram API)

#References: 
'''
1) https://proxy-seller.com/blog/how-to-scrape-telegram-channel-data-using-python/
2) https://medium.com/@ishitagopal/collecting-messages-from-telegram-using-telegrams-api-and-python-5d7e4a9286b2
'''

from telethon.sync import TelegramClient  # 'sync' version avoids needing manual async loops — friendlier for beginners
from telethon.tl.types import PeerChannel  # helps identify a Telegram entity by its ID
import pandas as pd # pandas: used to organise scraped messages into a neat table, then export to CSV
from datetime import datetime # datetime: used to handle and format message timestamps
import json 

# os + pathlib: helps manage file/folder paths safely across Windows, Mac, Linux
import os
from pathlib import Path

# Import API ID, Hash 
# config: your own file (config.py) that stores your secret API credentials
# NEVER hardcode API keys directly in your script!
from config import Config

# ============================================================
# STEP 1 — LOAD YOUR TELEGRAM API CREDENTIALS
# ============================================================
# These values come from https://my.telegram.org
# You must have already created an app there to get these
# Retrieve Telegram credentials from config.py
telegram_api_id = Config.api_id # A number, e.g. 1234567
telegram_api_hash = Config.api_hash # A string, e.g. 'abc123def456...'

# The session name 'anon' creates a local file 'anon.session'
# This file saves your login so you don't need to re-authenticate every run
client = TelegramClient('anon', telegram_api_id, telegram_api_hash)

'''with TelegramClient('anon', api_id, api_hash) as client:
   client.loop.run_until_complete(client.send_message('me', 'hello'))'''

# ============================================================
# STEP 2 — DEFINE THE TARGET GROUP NAME
# ============================================================
# This is the exact name of the Telegram group you want to scrape
# Change this if your group name is different
 
TARGET_GROUP_NAME = "automateData"

# ============================================================
# STEP 3 — DEFINE WHERE TO SAVE THE OUTPUT CSV FILE
# ============================================================
# Path().resolve() gets the folder where this .py file lives
# The output file will be saved right next to your script
 
OUTPUT_FILE = Path(__file__).resolve().parent / "scraped_messages.csv"

# ============================================================
# STEP 4 — MAIN SCRAPING FUNCTION
# ============================================================
 
def scrape_group_messages():
    """
    Connects to Telegram, finds the target group,
    scrapes all messages, and saves them to a CSV file.
    """
 
    # 'with client:' automatically starts AND stops the Telegram connection safely
    with client:
 
        # --- 4a. Confirm login ---
        # get_me() fetches YOUR Telegram account info to confirm you're logged in
        me = client.get_me()
        print(f"✅ Logged in as: {me.first_name} (@{me.username})")
        print("-" * 50)
 
 
        # --- 4b. Find the target group ---
        # iter_dialogs() loops through ALL your Telegram chats (groups, DMs, channels)
        # We search for the one whose name matches TARGET_GROUP_NAME
 
        print(f"🔍 Searching for group: '{TARGET_GROUP_NAME}'...")
        target_group = None  # We'll store the found group here
 
        for dialog in client.iter_dialogs():
            # dialog.name is the display name of each chat
            if dialog.name == TARGET_GROUP_NAME:
                target_group = dialog  # Found it! Save and stop searching
                break
 
        # If we looped through everything and didn't find it, stop the program
        if target_group is None:
            print(f"❌ Group '{TARGET_GROUP_NAME}' not found.")
            print("   Make sure the group name is spelled exactly as it appears in Telegram.")
            return  # Exit the function early — nothing to scrape
 
 
        # --- 4c. Confirm group was found ---
        print(f"✅ Found group: '{target_group.name}' (ID: {target_group.id})")
        print("-" * 50)
        print("📥 Scraping messages... (this may take a moment)")
 
 
        # --- 4d. Scrape all messages from the group ---
        # iter_messages() fetches messages one by one from newest to oldest
        # limit=None means fetch ALL messages (no cap)
 
        messages_data = []  # Empty list — we'll add each message as a dictionary
 
        for message in client.iter_messages(target_group, limit=None):
 
            # Some messages are system events (e.g. "User joined") with no text
            # We skip those and only keep real text messages
            if message.text:
 
                # Build a clean dictionary for each message
                messages_data.append({
                    "message_id" : message.id,                          # Unique ID of the message
                    "date"       : message.date.strftime("%Y-%m-%d"),   # Date in YYYY-MM-DD format
                    "time"       : message.date.strftime("%H:%M:%S"),   # Time in HH:MM:SS format
                    "sender_id"  : message.sender_id,                   # Telegram user ID of sender
                    "message"    : message.text.strip(),                 # The actual message text (stripped of whitespace)
                })
 
 
        # --- 4e. Check if any messages were found ---
        if not messages_data:
            print("⚠️  No text messages found in this group.")
            return

        # ============================================================
        # STEP 5 — CONVERT TO DATAFRAME AND EXPORT TO CSV
        # ============================================================
 
        # pandas DataFrame = a table with rows and columns (like Excel)
        # We pass our list of dictionaries — each dict becomes one row
        df = pd.DataFrame(messages_data)
 
        # Sort by date + time so oldest messages appear first
        df = df.sort_values(by=["date", "time"]).reset_index(drop=True)
 
        # Save to CSV file — index=False means don't write row numbers
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        # utf-8-sig encoding ensures special characters (emoji, non-English) display correctly in Excel

        # ============================================================
        # STEP 6 — PRINT SUMMARY
        # ============================================================
 
        print(f"\n✅ Done! {len(df)} messages scraped.")
        print(f"📄 Saved to: {OUTPUT_FILE}")
        print("\n--- Preview (first 5 messages) ---")
        print(df.head().to_string(index=False))  # Print a quick preview in the terminal
 
 
# ============================================================
# ENTRY POINT — This block runs the script when executed directly
# ============================================================
# '__main__' check ensures this only runs when YOU run this file,
# not when it's imported by another script
 
if __name__ == "__main__":
    scrape_group_messages()
    
''' #Selecting a Telegram Channel or Group (pinpoint data collection source channel/group)
async def main():
   me = await client.get_me()
   username = me.username
   print(username)
   print(me.phone)
   
   async for dialog in client.iter_dialogs():
       print(dialog.name, 'has ID - ', dialog.id)


with client:
   client.loop.run_until_complete(main()) '''