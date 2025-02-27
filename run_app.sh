#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    echo "Would you like to run the setup script to create it? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        python setup_env.py
        if [ ! -f .env ]; then
            echo "Setup was cancelled or failed. Please create a .env file manually."
            echo "You can use .env.example as a template."
            exit 1
        fi
    else
        echo "Please create a .env file with your API keys and Group ID."
        echo "You can use .env.example as a template."
        exit 1
    fi
fi

# Check if ZEP_GROUP_ID is set in .env
if ! grep -q "ZEP_GROUP_ID" .env; then
    echo "Warning: ZEP_GROUP_ID is not set in your .env file."
    echo "You will need to enter your Group ID manually each time you run the application."
    echo "Would you like to add it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Enter your Zep Group ID:"
        read -r group_id
        echo "ZEP_GROUP_ID=$group_id" >> .env
        echo "ZEP_GROUP_ID has been added to your .env file."
    fi
fi

# Run the Streamlit app
echo "Starting Zep Query Client..."
streamlit run zep_query_client.py 