import os
import json
from typing import Annotated
from azure.cosmos import CosmosClient

# Define standalone functions that can be used as tools in Agent Framework

def get_document_by_claim_id(claim_id: Annotated[str, "The claim_id to retrieve"]) -> Annotated[str, "JSON document from Cosmos DB"]:
    """Retrieve a document by its claim_id using a cross-partition query."""
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    key = os.environ.get("COSMOS_KEY")
    database_name = "insurance_claims"
    container_name = "crash_reports"
    
    if not endpoint or not key:
        return "❌ Cosmos DB not configured. Please set COSMOS_ENDPOINT and COSMOS_KEY environment variables."
    
    try:
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Use SQL query to find document by claim_id across all partitions
        query = "SELECT * FROM c WHERE c.claim_id = @claim_id"
        parameters = [{"name": "@claim_id", "value": claim_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
            max_item_count=1
        ))
        
        if not items:
            return f"❌ No document found with claim_id '{claim_id}' in container '{container_name}'."
        
        # Return the first matching document
        document = items[0]
        return json.dumps(document, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Error retrieving document by claim_id '{claim_id}': {str(e)}"

# Export the function
__all__ = ['get_document_by_claim_id']
