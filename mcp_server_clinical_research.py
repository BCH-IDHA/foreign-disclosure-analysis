"""
Wrapper for the Clinical Research MCP Server.
Provides functions to interact with PubMed and other clinical research databases.
"""

import logging
import json
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def use_pubmed_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search PubMed for medical and scientific articles using the Clinical Research MCP Server.
    
    Args:
        params: Dictionary containing search parameters:
            - query: Search query (required)
            - max_results: Maximum number of results to return (1-25)
            - sort_by: Sort order for results (relevance, date, journal)
            - date_range: Filter results by publication date
            - publication_types: Filter by publication types
            - fields: Specific fields to search
            - format: Output format for results
            
    Returns:
        List of publication dictionaries containing metadata
    """
    try:
        # Import the MCP tool
        from use_mcp_tool import use_mcp_tool
        
        # Validate required parameters
        if 'query' not in params:
            raise ValueError("Query parameter is required for PubMed search")
        
        # Set default values if not provided
        if 'max_results' not in params:
            params['max_results'] = 10
        
        # Log the search query
        logger.info(f"Searching PubMed with query: {params['query']}")
        
        # Call the MCP server tool
        result = use_mcp_tool(
            server_name="medical-server",
            tool_name="pubmed-search",
            arguments=params
        )
        
        # Process the result
        publications = process_pubmed_results(result)
        
        logger.info(f"Retrieved {len(publications)} publications from PubMed")
        return publications
        
    except Exception as e:
        logger.error(f"Error in PubMed search: {str(e)}")
        # Propagate the error instead of returning an empty list
        raise e

def process_pubmed_results(result: Any) -> List[Dict[str, Any]]:
    """
    Process raw PubMed results into a standardized format.
    
    Args:
        result: Raw result from the MCP server
        
    Returns:
        List of publication dictionaries with standardized fields
    """
    try:
        # If result is a string, try to parse it as JSON
        if isinstance(result, str):
            result = json.loads(result)
        
        # Initialize publications list
        publications = []
        
        # Check if result is a list or has a 'results' field
        items = result if isinstance(result, list) else result.get('results', [])
        
        for item in items:
            # Extract and standardize publication data
            pub = {
                'title': item.get('title', ''),
                'authors': item.get('authors', []),
                'journal': item.get('journal', {}).get('name', '') if isinstance(item.get('journal'), dict) else item.get('journal', ''),
                'publication_date': item.get('publication_date', ''),
                'abstract': item.get('abstract', ''),
                'doi': item.get('doi', ''),
                'pmid': item.get('pmid', ''),
                'affiliations': extract_affiliations(item),
                'funding_info': extract_funding_info(item),
                'keywords': item.get('keywords', []),
                'url': item.get('url', '')
            }
            publications.append(pub)
        
        return publications
    
    except Exception as e:
        logger.error(f"Error processing PubMed results: {str(e)}")
        return []

def extract_affiliations(publication: Dict[str, Any]) -> str:
    """
    Extract affiliations from a publication.
    
    Args:
        publication: Publication data dictionary
        
    Returns:
        String containing all affiliations
    """
    affiliations = []
    
    # Try to extract from different possible structures
    if 'affiliations' in publication:
        if isinstance(publication['affiliations'], list):
            affiliations.extend(publication['affiliations'])
        elif isinstance(publication['affiliations'], str):
            affiliations.append(publication['affiliations'])
    
    # Try to extract from authors if available
    if 'authors' in publication and isinstance(publication['authors'], list):
        for author in publication['authors']:
            if isinstance(author, dict) and 'affiliation' in author:
                if isinstance(author['affiliation'], list):
                    affiliations.extend(author['affiliation'])
                else:
                    affiliations.append(author['affiliation'])
    
    return '; '.join(filter(None, affiliations))

def extract_funding_info(publication: Dict[str, Any]) -> str:
    """
    Extract funding information from a publication.
    
    Args:
        publication: Publication data dictionary
        
    Returns:
        String containing funding information
    """
    funding_info = []
    
    # Try different possible field names
    for field in ['funding', 'funding_info', 'grant_info', 'grants', 'acknowledgments']:
        if field in publication:
            if isinstance(publication[field], list):
                funding_info.extend(publication[field])
            elif isinstance(publication[field], str):
                funding_info.append(publication[field])
            elif isinstance(publication[field], dict):
                for key, value in publication[field].items():
                    funding_info.append(f"{key}: {value}")
    
    return '; '.join(filter(None, funding_info))

def use_clinical_trials_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search ClinicalTrials.gov for information about clinical studies.
    
    Args:
        params: Dictionary containing search parameters
            
    Returns:
        List of clinical trial dictionaries
    """
    try:
        # Import the MCP tool
        from use_mcp_tool import use_mcp_tool
        
        # Call the MCP server tool
        result = use_mcp_tool(
            server_name="medical-server",
            tool_name="clinical-trials-search",
            arguments=params
        )
        
        # Process and return the result
        return result
        
    except Exception as e:
        logger.error(f"Error in clinical trials search: {str(e)}")
        raise e

def use_fda_drug_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search FDA database for drug information and labeling details.
    
    Args:
        params: Dictionary containing search parameters
            
    Returns:
        List of drug information dictionaries
    """
    try:
        # Import the MCP tool
        from use_mcp_tool import use_mcp_tool
        
        # Call the MCP server tool
        result = use_mcp_tool(
            server_name="medical-server",
            tool_name="fda-drug-search",
            arguments=params
        )
        
        # Process and return the result
        return result
        
    except Exception as e:
        logger.error(f"Error in FDA drug search: {str(e)}")
        raise e
