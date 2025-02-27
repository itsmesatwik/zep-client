import os
import json
import asyncio
import streamlit as st
import pandas as pd
from zep_cloud.client import AsyncZep
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys
zep_api_key = os.getenv("ZEP_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
default_group_id = os.getenv("ZEP_GROUP_ID", "")  # Get default group ID from env

# Initialize clients
zep_client = AsyncZep(api_key=zep_api_key)
oai_client = AsyncOpenAI(api_key=openai_api_key)

# Set page config
st.set_page_config(
    page_title="Zep Query Client",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title
st.title("Zep Query Client")

# Sidebar
st.sidebar.header("Query Configuration")

# Group ID input
group_id = st.sidebar.text_input("Group ID", value=default_group_id)

# Query input
query = st.sidebar.text_area("Query", value="which products are most relevant to an environmental quality specialist?")

# Mode selection
mode = st.sidebar.radio("Mode", ["Single Reranker", "Compare Rerankers"])

# Reranker selection
reranker_options = ["cross_encoder", "rrf", "node_distance", "episode_mentions"]

if mode == "Single Reranker":
    reranker = st.sidebar.selectbox("Reranker", reranker_options)
    selected_rerankers = [reranker]
else:  # Compare Rerankers
    st.sidebar.subheader("Select Rerankers to Compare")
    selected_rerankers = []
    for reranker in reranker_options:
        if st.sidebar.checkbox(reranker, value=True):
            selected_rerankers.append(reranker)
    
    if not selected_rerankers:
        st.sidebar.warning("Please select at least one reranker.")

# Limit selection
limit = st.sidebar.slider("Result Limit", min_value=1, max_value=20, value=10)

# Scope selection
scope = st.sidebar.radio("Scope", ["nodes", "edges", "both"])

# Centroid node section (for node_distance reranker)
use_centroid = st.sidebar.checkbox("Use Centroid Node", value="node_distance" in selected_rerankers)

centroid_method = st.sidebar.radio(
    "Centroid Query Method", 
    ["Manual", "Generate with OpenAI"], 
    disabled=not use_centroid
)

if centroid_method == "Manual" or not use_centroid:
    centroid_query = st.sidebar.text_area(
        "Centroid Query", 
        value="Environmental monitoring equipment", 
        disabled=not use_centroid
    )
else:
    if st.sidebar.button("Generate Centroid Query", disabled=not use_centroid):
        with st.sidebar:
            with st.spinner("Generating centroid query..."):
                # Create event loop for OpenAI call
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Call OpenAI to generate centroid query
                response = loop.run_until_complete(
                    oai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Identify the type of product that the query is referring to. Return just the product category."},
                            {"role": "user", "content": query}
                        ],
                    )
                )
                
                # Close the event loop
                loop.close()
                
                # Set the centroid query
                centroid_query = response.choices[0].message.content
                st.success(f"Generated centroid query: {centroid_query}")
    else:
        centroid_query = "Environmental monitoring equipment"
        st.sidebar.info("Click 'Generate Centroid Query' to use OpenAI to generate a query based on your main query.")

# Store centroid query in session state
if "centroid_query" not in st.session_state or st.session_state.centroid_query != centroid_query:
    st.session_state.centroid_query = centroid_query

# Run button
run_button = st.sidebar.button("Run Queries")

# Function to run centroid query
async def get_centroid_node(group_id, centroid_query):
    results = await zep_client.graph.search(
        group_id=group_id, 
        query=centroid_query, 
        scope="nodes", 
        limit=1, 
        reranker="rrf"
    )
    if results.nodes:
        return results.nodes[0].uuid_, results.nodes[0].summary
    return None, None

# Function to run search
async def run_search(group_id, query, scope, reranker, limit, center_node_uuid=None):
    search_params = {
        "group_id": group_id,
        "query": query,
        "scope": scope,
        "limit": limit,
        "reranker": reranker
    }
    
    # If reranker is node_distance, center_node_uuid is required
    if reranker == "node_distance":
        if center_node_uuid:
            search_params["center_node_uuid"] = center_node_uuid
        else:
            # If no center_node_uuid is available, fallback to rrf reranker
            st.warning(f"No centroid node found. Falling back to 'rrf' reranker instead of 'node_distance'.")
            search_params["reranker"] = "rrf"
    
    return await zep_client.graph.search(**search_params)

# Function to display node results
def display_node_results(results, title=""):
    if title:
        st.subheader(title)
    
    if not results.nodes:
        st.write("No results found.")
        return
    
    for i, node in enumerate(results.nodes):
        with st.expander(f"Result {i+1}"):
            st.write(node.summary)

# Function to display edge results
def display_edge_results(results, title=""):
    if title:
        st.subheader(title)
    
    if not results.edges:
        st.write("No results found.")
        return
    
    for i, edge in enumerate(results.edges):
        st.write(f"{i+1}. {edge.fact}")

# Main content
if run_button and group_id and selected_rerankers:
    # Check if node_distance is selected but centroid is not enabled
    if "node_distance" in selected_rerankers and not use_centroid:
        st.error("The 'node_distance' reranker requires a centroid node. Please enable 'Use Centroid Node' option.")
    else:
        # Run the queries
        with st.spinner("Running queries..."):
            # Create event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get centroid node if needed
            center_node_uuid = None
            centroid_summary = None
            if use_centroid and "node_distance" in selected_rerankers:
                center_node_uuid, centroid_summary = loop.run_until_complete(
                    get_centroid_node(group_id, st.session_state.centroid_query)
                )
                if center_node_uuid:
                    st.success(f"Found centroid node: {center_node_uuid}")
                    if centroid_summary:
                        with st.expander("Centroid Node Summary"):
                            st.write(f"**Query:** {st.session_state.centroid_query}")
                            st.write(f"**Summary:** {centroid_summary}")
                else:
                    st.error("Could not find centroid node. The 'node_distance' reranker will fall back to 'rrf'.")
            
            # Single reranker mode
            if mode == "Single Reranker":
                # Create columns for side-by-side display
                if scope == "both":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Nodes Results")
                        node_results = loop.run_until_complete(
                            run_search(group_id, query, "nodes", selected_rerankers[0], limit, center_node_uuid)
                        )
                        display_node_results(node_results)
                    
                    with col2:
                        st.subheader("Edges Results")
                        edge_results = loop.run_until_complete(
                            run_search(group_id, query, "edges", selected_rerankers[0], limit, center_node_uuid)
                        )
                        display_edge_results(edge_results)
                else:
                    results = loop.run_until_complete(
                        run_search(group_id, query, scope, selected_rerankers[0], limit, center_node_uuid)
                    )
                    if scope == "nodes":
                        display_node_results(results)
                    else:  # scope == "edges"
                        display_edge_results(results)
            
            # Compare rerankers mode
            else:
                if scope == "both":
                    # First display nodes comparison
                    st.header("Nodes Comparison")
                    cols = st.columns(len(selected_rerankers))
                    
                    for i, reranker in enumerate(selected_rerankers):
                        with cols[i]:
                            st.subheader(f"{reranker}")
                            node_results = loop.run_until_complete(
                                run_search(group_id, query, "nodes", reranker, limit, 
                                        center_node_uuid if reranker == "node_distance" else None)
                            )
                            display_node_results(node_results)
                    
                    # Then display edges comparison
                    st.header("Edges Comparison")
                    cols = st.columns(len(selected_rerankers))
                    
                    for i, reranker in enumerate(selected_rerankers):
                        with cols[i]:
                            st.subheader(f"{reranker}")
                            edge_results = loop.run_until_complete(
                                run_search(group_id, query, "edges", reranker, limit,
                                        center_node_uuid if reranker == "node_distance" else None)
                            )
                            display_edge_results(edge_results)
                else:
                    # Display comparison for the selected scope
                    cols = st.columns(len(selected_rerankers))
                    
                    for i, reranker in enumerate(selected_rerankers):
                        with cols[i]:
                            st.subheader(f"{reranker}")
                            results = loop.run_until_complete(
                                run_search(group_id, query, scope, reranker, limit,
                                        center_node_uuid if reranker == "node_distance" else None)
                            )
                            if scope == "nodes":
                                display_node_results(results)
                            else:  # scope == "edges"
                                display_edge_results(results)
            
            # Close the event loop
            loop.close()
else:
    if not group_id and run_button:
        st.warning("Please enter a Group ID.")
    elif not selected_rerankers and run_button:
        st.warning("Please select at least one reranker.")
    elif not run_button:
        st.info("Configure your query parameters and click 'Run Queries' to see results.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This application allows you to query Zep's graph database with different rerankers and view the results side by side.
    
    **Rerankers:**
    - **cross_encoder**: Uses a cross-encoder model for reranking
    - **rrf**: Reciprocal Rank Fusion
    - **node_distance**: Ranks by distance from a centroid node (requires centroid node)
    - **episode_mentions**: Ranks by episode mentions
    
    **Scopes:**
    - **nodes**: Search for nodes (documents)
    - **edges**: Search for edges (facts)
    - **both**: Search for both nodes and edges
    """
) 