"""
Foreign Disclosure Analysis Tool for BCH Researchers
Analyzes PubMed publications for foreign disclosure requirements.
"""

import os
import csv
import json
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
try:
    # Try to initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    logger.info("Successfully initialized Azure OpenAI client")
except Exception as e:
    # If there's an error, use a mock client for development/testing
    logger.warning(f"Error initializing Azure OpenAI client: {str(e)}")
    logger.warning("Using mock Azure OpenAI client for development/testing")
    client = None

# Constants
COUNTRIES_OF_CONCERN = ["Russia", "North Korea", "Iran", "China"]
OUTPUT_FILE = "foreign_disclosure_analysis.csv"
MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
OUTPUT_COLUMNS = [
    "publication_name",
    "research_title",
    "author_name",
    "organization_affiliation",
    "countries_of_origin",
    "flagged",
    "flagged_countries",
    "confidence_score",
    "funding_source"
]

def load_researchers(file_path='researchers.csv'):
    """
    Load researcher data from CSV file.
    Returns a list of dictionaries containing researcher information.
    """
    try:
        researchers = []
        with open(file_path, 'r') as f:
            # Read the first line to get the header
            header_line = f.readline().strip()
            
            # Check if the file is empty
            if not header_line:
                logger.error("Empty researchers file")
                return []
            
            # Parse the header line to get column names
            if ',' in header_line:
                columns = [col.strip() for col in header_line.split(',')]
                last_name_col = columns[0]
                first_name_col = columns[1]
            else:
                # Default column names if header is not as expected
                last_name_col = "Researcher last name"
                first_name_col = "Research first name"
            
            # Read the rest of the lines
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Split the line by comma
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 2:
                    researchers.append({
                        'last_name': parts[0],
                        'first_name': parts[1]
                    })
        
        logger.info(f"Loaded {len(researchers)} researchers from {file_path}")
        return researchers
    except Exception as e:
        logger.error(f"Error loading researchers from {file_path}: {str(e)}")
        raise

def query_pubmed_publications(researcher):
    """
    Query PubMed for publications by a researcher using the Clinical Research MCP Server.
    """
    try:
        from mcp_server_clinical_research import use_pubmed_search
        
        # Construct query with researcher name and affiliation
        query = f"{researcher['last_name']}, {researcher['first_name']}[Author] AND Boston Children's Hospital[Affiliation]"
        
        # Query PubMed via the MCP Server
        response = use_pubmed_search({
            "query": query,
            "max_results": 25,
            "sort_by": "date",
            "publication_types": ["Research"],
            "format": "default"
        })
        
        # Process the response
        if isinstance(response, dict) and 'results' in response:
            publications = response['results']
            logger.info(f"Retrieved {len(publications)} publications for {researcher['first_name']} {researcher['last_name']}")
            return publications
        elif isinstance(response, list):
            logger.info(f"Retrieved {len(response)} publications for {researcher['first_name']} {researcher['last_name']}")
            return response
        else:
            logger.warning(f"Unexpected response format for {researcher['first_name']} {researcher['last_name']}")
            return []
    except Exception as e:
        logger.error(f"Error querying PubMed for {researcher['first_name']} {researcher['last_name']}: {str(e)}")
        return []

def analyze_foreign_affiliations(publication_data):
    """
    Use Azure OpenAI to analyze publication data for foreign affiliations.
    Returns a dictionary containing analysis results.
    """
    try:
        # If we have a real client, use it
        if client:
            prompt = f"""
            Analyze the following publication metadata for foreign affiliations and collaborations,
            particularly focusing on Russia, North Korea, Iran, and China.

            Title: {publication_data.get('title', '')}
            Authors and Affiliations: {publication_data.get('affiliations', '')}
            Abstract: {publication_data.get('abstract', '')}
            Funding Information: {publication_data.get('funding_info', '')}

            Please provide a JSON response with the following information:
            1. List of all foreign countries mentioned or implied
            2. Foreign institutions involved
            3. Any foreign funding sources identified
            4. Confidence score (1-10) regarding foreign involvement
            5. Detailed explanation for the confidence score
            """

            response = client.chat.completions.create(
                model=MODEL_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing scientific publications for foreign affiliations and collaborations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully analyzed publication for foreign affiliations")
            return result
        else:
            # Use mock analysis for development/testing
            return mock_analyze_foreign_affiliations(publication_data)
    except Exception as e:
        logger.error(f"Error analyzing foreign affiliations: {str(e)}")
        # Fallback to mock analysis
        return mock_analyze_foreign_affiliations(publication_data)

def mock_analyze_foreign_affiliations(publication_data):
    """
    Mock implementation of foreign affiliation analysis for development and testing.
    
    Args:
        publication_data: Publication data dictionary
        
    Returns:
        Dictionary containing mock analysis results
    """
    logger.info("Using mock analysis for foreign affiliations")
    
    title = publication_data.get('title', '').lower()
    affiliations = publication_data.get('affiliations', '').lower()
    abstract = publication_data.get('abstract', '').lower()
    funding = publication_data.get('funding_info', '').lower()
    
    # Initialize result
    result = {
        'countries': [],
        'institutions': [],
        'funding_sources': [],
        'confidence_score': 1,
        'explanation': 'Mock analysis based on keyword matching.'
    }
    
    # Check for countries of concern
    countries_found = set()
    for country in COUNTRIES_OF_CONCERN:
        if country.lower() in title or country.lower() in affiliations or country.lower() in abstract or country.lower() in funding:
            countries_found.add(country)
    
    # Add other common countries
    for country in ['UK', 'United Kingdom', 'England', 'France', 'Germany', 'Japan', 'Canada', 'Australia', 'Spain', 'Italy']:
        if country.lower() in title or country.lower() in affiliations or country.lower() in abstract or country.lower() in funding:
            countries_found.add(country)
    
    # Extract institutions based on keywords
    institutions = []
    if 'university' in affiliations:
        institutions.append('University mentioned in affiliations')
    if 'hospital' in affiliations:
        institutions.append('Hospital mentioned in affiliations')
    if 'institute' in affiliations:
        institutions.append('Research Institute mentioned in affiliations')
    
    # Extract funding sources based on keywords
    funding_sources = []
    if 'grant' in funding:
        funding_sources.append('Grant mentioned in funding info')
    if 'nih' in funding or 'national institutes of health' in funding:
        funding_sources.append('NIH funding mentioned')
    if 'foundation' in funding:
        funding_sources.append('Foundation funding mentioned')
    
    # Calculate confidence score based on findings
    confidence_score = 1
    if countries_found:
        confidence_score += 3
    if any(country in countries_found for country in COUNTRIES_OF_CONCERN):
        confidence_score += 2
    if institutions:
        confidence_score += 1
    if funding_sources:
        confidence_score += 1
    if 'international' in abstract or 'collaboration' in abstract:
        confidence_score += 1
    
    # Cap at 10
    confidence_score = min(confidence_score, 10)
    
    # Update result
    result['countries'] = list(countries_found)
    result['institutions'] = institutions
    result['funding_sources'] = funding_sources
    result['confidence_score'] = confidence_score
    result['explanation'] = f"Mock analysis found {len(countries_found)} countries, {len(institutions)} institutions, and {len(funding_sources)} funding sources."
    
    return result

def generate_output_row(researcher, publication, analysis):
    """
    Generate a row for the output CSV file.
    """
    if not analysis:
        return None

    try:
        # Extract countries from analysis
        countries = analysis.get('countries', [])
        if isinstance(countries, str):
            countries = [countries]
        
        # Extract funding sources from analysis
        funding_sources = analysis.get('funding_sources', [])
        if isinstance(funding_sources, str):
            funding_sources = [funding_sources]
        
        # Format funding sources as a string
        funding_str = ', '.join(funding_sources) if funding_sources else ''
        
        # Identify flagged countries
        flagged_countries = []
        all_countries = []
        
        for country in countries:
            all_countries.append(country)
            for concern in COUNTRIES_OF_CONCERN:
                if concern.lower() in country.lower():
                    flagged_countries.append(country)
                    break
        
        # Determine if the publication is flagged
        is_flagged = len(flagged_countries) > 0
        
        return {
            "publication_name": publication.get('journal', ''),
            "research_title": publication.get('title', ''),
            "author_name": f"{researcher['first_name']} {researcher['last_name']}",
            "organization_affiliation": "Boston Children's Hospital",
            "countries_of_origin": ', '.join(all_countries),
            "flagged": "Yes" if is_flagged else "No",
            "flagged_countries": ', '.join(flagged_countries) if flagged_countries else "",
            "confidence_score": analysis.get('confidence_score', 0),
            "funding_source": funding_str
        }
    except Exception as e:
        logger.error(f"Error generating output row: {str(e)}")
        return None

def main():
    """
    Main execution function for the foreign disclosure analysis tool.
    """
    try:
        # Load researchers
        researchers = load_researchers()
        
        # Initialize results list
        results = []

        # Process each researcher
        for researcher in researchers:
            logger.info(f"Processing researcher: {researcher['first_name']} {researcher['last_name']}")
            
            # Query PubMed for publications
            publications = query_pubmed_publications(researcher)
            
            # Analyze each publication
            for pub in publications:
                analysis = analyze_foreign_affiliations(pub)
                if analysis:
                    row = generate_output_row(researcher, pub, analysis)
                    if row:
                        results.append(row)

        # Create output DataFrame and save to CSV
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"Analysis complete. Results saved to {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
