#!/usr/bin/env python3
"""
Setup Environment Variables for Zep Query Client

This script helps you set up your environment variables for the Zep Query Client.
It will create a .env file with your Zep API key, OpenAI API key, and Zep Group ID.
"""

import os
import sys

def create_env_file():
    """Create a .env file with user-provided values."""
    print("Setting up environment variables for Zep Query Client...")
    
    # Check if .env file already exists
    if os.path.exists(".env"):
        overwrite = input(".env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != "y":
            print("Setup cancelled. Existing .env file was not modified.")
            return
    
    # Get Zep API key
    zep_api_key = input("Enter your Zep API key: ")
    while not zep_api_key:
        print("Zep API key is required.")
        zep_api_key = input("Enter your Zep API key: ")
    
    # Get OpenAI API key (optional)
    openai_api_key = input("Enter your OpenAI API key (press Enter to skip): ")
    
    # Get Zep Group ID
    zep_group_id = input("Enter your Zep Group ID: ")
    while not zep_group_id:
        print("Zep Group ID is required.")
        zep_group_id = input("Enter your Zep Group ID: ")
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"ZEP_API_KEY={zep_api_key}\n")
        if openai_api_key:
            f.write(f"OPENAI_API_KEY={openai_api_key}\n")
        else:
            f.write("# OPENAI_API_KEY=your_openai_api_key_here\n")
        f.write(f"ZEP_GROUP_ID={zep_group_id}\n")
    
    print("\n.env file created successfully!")
    print("You can now run the Zep Query Client with:")
    print("  streamlit run zep_query_client.py")

if __name__ == "__main__":
    create_env_file() 