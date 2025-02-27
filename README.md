# Zep Query Client

A Streamlit application for querying Zep's graph database with different rerankers and viewing the results side by side.

## Features

- Query Zep's graph database with different rerankers
- Compare results from multiple rerankers side by side
- View both nodes and edges results
- Use OpenAI to generate centroid queries for node_distance reranking
- Customize query parameters such as limit and scope
- Set default Group ID in environment variables
- Secure configuration with `.gitignore` to prevent sensitive data exposure

## Rerankers

- **cross_encoder**: Uses a cross-encoder model for reranking
- **rrf**: Reciprocal Rank Fusion
- **node_distance**: Ranks by distance from a centroid node (requires a centroid node)
- **episode_mentions**: Ranks by episode mentions

## Scopes

- **nodes**: Search for nodes (documents)
- **edges**: Search for edges (facts)
- **both**: Search for both nodes and edges

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables using one of these methods:
   
   **Option 1: Use the setup script (recommended)**
   ```
   python setup_env.py
   ```
   This interactive script will guide you through setting up your `.env` file.
   
   **Option 2: Create the .env file manually**
   Create a `.env` file with your API keys and Group ID (see `.env.example` for reference):
   ```
   ZEP_API_KEY=your_zep_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ZEP_GROUP_ID=your_zep_group_id_here
   ```
   
   > **Security Note**: The `.env` file is included in `.gitignore` to prevent accidentally committing sensitive API keys to your repository.

4. Run the application:
   ```
   streamlit run zep_query_client.py
   ```
   
   Or use the provided shell script:
   ```
   ./run_app.sh
   ```

## Usage

1. The Group ID will be pre-filled if you've set it in your `.env` file, otherwise enter it manually
2. Enter your query
3. Select the mode (Single Reranker or Compare Rerankers)
4. Configure the reranker(s), scope, and limit
5. (Optional) Configure centroid node settings for node_distance reranking
6. Click "Run Queries" to see the results

### Important Note About node_distance Reranker

The `node_distance` reranker requires a centroid node to function properly. When you select this reranker:

1. Make sure to check the "Use Centroid Node" option
2. Either manually enter a centroid query or use the "Generate with OpenAI" option
3. If no centroid node is found, the application will automatically fall back to the `rrf` reranker

## Troubleshooting

If you encounter any issues while using the application, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common problems.