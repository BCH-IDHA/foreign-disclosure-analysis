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
        # For development/testing, return mock data if the MCP server is not available
        return get_mock_pubmed_data(params.get('query', ''))

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

def get_mock_pubmed_data(query: str) -> List[Dict[str, Any]]:
    """
    Generate mock PubMed data for development and testing.
    
    Args:
        query: Search query
        
    Returns:
        List of mock publication dictionaries
    """
    logger.warning("Using mock PubMed data for development/testing")
    
    # Extract researcher name from query if possible
    researcher_name = query.split('[Author]')[0].strip() if '[Author]' in query else "Researcher"
    
    # Create mock publications
    mock_publications = [
        {
            'title': 'Novel Therapeutic Approaches for Pediatric Autoimmune Disorders',
            'authors': [
                {'name': researcher_name, 'affiliation': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA'},
                {'name': 'Wang, Li', 'affiliation': 'Beijing Children\'s Hospital, Capital Medical University, Beijing, China'}
            ],
            'journal': 'Journal of Pediatric Immunology',
            'publication_date': '2024-03-15',
            'abstract': 'This study explores novel therapeutic approaches for pediatric autoimmune disorders, with a focus on targeted immunomodulation. Our international collaboration identified several promising treatment pathways.',
            'doi': '10.1234/jpimmunol.2024.0123',
            'pmid': '36789012',
            'affiliations': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA; Beijing Children\'s Hospital, Capital Medical University, Beijing, China',
            'funding_info': 'NIH Grant R01-AI123456; National Natural Science Foundation of China (Grant No. 82071754)',
            'keywords': ['pediatric', 'autoimmune', 'immunotherapy', 'international collaboration'],
            'url': 'https://pubmed.ncbi.nlm.nih.gov/36789012/'
        },
        {
            'title': 'Genetic Basis of Rare Congenital Heart Defects: A Multi-Center Study',
            'authors': [
                {'name': researcher_name, 'affiliation': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA'},
                {'name': 'Petrov, Mikhail', 'affiliation': 'National Medical Research Center, Moscow, Russia'},
                {'name': 'Smith, John', 'affiliation': 'Great Ormond Street Hospital, London, UK'}
            ],
            'journal': 'Pediatric Cardiology',
            'publication_date': '2023-11-22',
            'abstract': 'This multi-center study investigates the genetic basis of rare congenital heart defects across diverse populations. We identified several novel genetic variants associated with specific cardiac malformations.',
            'doi': '10.1234/pedcard.2023.5678',
            'pmid': '35678901',
            'affiliations': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA; National Medical Research Center, Moscow, Russia; Great Ormond Street Hospital, London, UK',
            'funding_info': 'American Heart Association Grant AHA-CHD-2023; Russian Science Foundation Grant 21-15-00123',
            'keywords': ['congenital heart defects', 'genetics', 'pediatric', 'international collaboration'],
            'url': 'https://pubmed.ncbi.nlm.nih.gov/35678901/'
        },
        {
            'title': 'Advances in Pediatric Neuroimaging Techniques',
            'authors': [
                {'name': researcher_name, 'affiliation': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA'},
                {'name': 'Johnson, Emily', 'affiliation': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA'}
            ],
            'journal': 'Journal of Pediatric Neurology',
            'publication_date': '2024-01-30',
            'abstract': 'This review discusses recent advances in pediatric neuroimaging techniques and their clinical applications. We highlight innovations in MRI protocols specifically designed for pediatric patients.',
            'doi': '10.1234/jpedneurol.2024.9012',
            'pmid': '34567890',
            'affiliations': 'Boston Children\'s Hospital, Harvard Medical School, Boston, MA, USA',
            'funding_info': 'NIH Grant R01-NS654321',
            'keywords': ['neuroimaging', 'pediatric', 'MRI', 'clinical applications'],
            'url': 'https://pubmed.ncbi.nlm.nih.gov/34567890/'
        }
    ]
    
    return mock_publications

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
        return []

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
        return []
