import os
import json
import asyncio
from zep_cloud.client import AsyncZep
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys
zep_api_key = os.getenv("ZEP_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize clients
zep_client = AsyncZep(api_key=zep_api_key)
oai_client = AsyncOpenAI(api_key=openai_api_key)

# Test group ID - replace with your own
GROUP_ID = "YOUR_GROUP_ID"  # Replace with your group ID

# Test query
QUERY = "which products are most relevant to an environmental quality specialist?"

async def test_search():
    print(f"Testing search with query: {QUERY}")
    
    # Test cross_encoder reranker with nodes scope
    print("\n=== Testing cross_encoder reranker with nodes scope ===")
    results = await zep_client.graph.search(
        group_id=GROUP_ID, 
        query=QUERY, 
        scope="nodes", 
        limit=3, 
        reranker="cross_encoder"
    )
    
    if results.nodes:
        print(f"Found {len(results.nodes)} nodes")
        for i, node in enumerate(results.nodes):
            print(f"\nNode {i+1}:")
            print(f"Summary: {node.summary[:200]}...")
    else:
        print("No nodes found")
    
    # Test rrf reranker with edges scope
    print("\n=== Testing rrf reranker with edges scope ===")
    results = await zep_client.graph.search(
        group_id=GROUP_ID, 
        query=QUERY, 
        scope="edges", 
        limit=3, 
        reranker="rrf"
    )
    
    if results.edges:
        print(f"Found {len(results.edges)} edges")
        for i, edge in enumerate(results.edges):
            print(f"\nEdge {i+1}:")
            print(f"Fact: {edge.fact}")
    else:
        print("No edges found")
    
    # Test centroid node for node_distance reranker
    print("\n=== Testing centroid node for node_distance reranker ===")
    
    # First get centroid node
    centroid_query = "Environmental monitoring equipment"
    centroid_results = await zep_client.graph.search(
        group_id=GROUP_ID, 
        query=centroid_query, 
        scope="nodes", 
        limit=1, 
        reranker="rrf"
    )
    
    if centroid_results.nodes:
        centroid_node_uuid = centroid_results.nodes[0].uuid_
        print(f"Found centroid node: {centroid_node_uuid}")
        print(f"Centroid summary: {centroid_results.nodes[0].summary[:200]}...")
        
        # Now search with node_distance reranker
        print("\n=== Testing node_distance reranker ===")
        try:
            results = await zep_client.graph.search(
                group_id=GROUP_ID,
                query=QUERY,
                scope="nodes",
                limit=3,
                reranker="node_distance",
                center_node_uuid=centroid_node_uuid,
            )
            
            if results.nodes:
                print(f"Found {len(results.nodes)} nodes")
                for i, node in enumerate(results.nodes):
                    print(f"\nNode {i+1}:")
                    print(f"Summary: {node.summary[:200]}...")
            else:
                print("No nodes found")
        except Exception as e:
            print(f"Error using node_distance reranker: {e}")
            print("Falling back to rrf reranker...")
            
            results = await zep_client.graph.search(
                group_id=GROUP_ID,
                query=QUERY,
                scope="nodes",
                limit=3,
                reranker="rrf"
            )
            
            if results.nodes:
                print(f"Found {len(results.nodes)} nodes with fallback reranker")
                for i, node in enumerate(results.nodes):
                    print(f"\nNode {i+1}:")
                    print(f"Summary: {node.summary[:200]}...")
            else:
                print("No nodes found with fallback reranker")
    else:
        print("Could not find centroid node. Skipping node_distance reranker test.")
        print("Testing with rrf reranker instead...")
        
        results = await zep_client.graph.search(
            group_id=GROUP_ID,
            query=QUERY,
            scope="nodes",
            limit=3,
            reranker="rrf"
        )
        
        if results.nodes:
            print(f"Found {len(results.nodes)} nodes with rrf reranker")
            for i, node in enumerate(results.nodes):
                print(f"\nNode {i+1}:")
                print(f"Summary: {node.summary[:200]}...")
        else:
            print("No nodes found with rrf reranker")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_search()) 