# Foreign Disclosure Requirements for Government-Funded Research: Implementation Plan

This document outlines the implementation plan for the Python solution that analyzes PubMed publications for foreign disclosure requirements related to Boston Children's Hospital (BCH) researchers.

## Project Overview

The solution analyzes PubMed publications for BCH researchers to identify foreign affiliations and collaborations, with a particular focus on Russia, North Korea, Iran, and China. The analysis results are output to a CSV file with specific fields.

## System Components

### 1. Data Ingestion

- Read researchers.csv file containing BCH researcher names
- Parse and validate researcher data

### 2. PubMed Integration

- Use the Clinical Research MCP Server to query PubMed for each researcher
- Retrieve publication metadata including titles, authors, affiliations, abstracts, and funding information

### 3. Foreign Affiliation Analysis

- Use Azure OpenAI API to analyze publication metadata and abstracts
- Detect mentions of foreign countries, institutions, and collaborations
- Specifically flag Russia, North Korea, Iran, and China affiliations

### 4. Output Generation

- Create a CSV file with the following columns:
  - Publication name
  - Research title
  - Author name (BCH researcher)
  - Organization affiliation
  - Countries of origin/association
  - Confidence score (1-10)
  - Funding source (if known)

## Implementation Progress

### Completed

- [x] Set up project structure
- [x] Create requirements.txt with dependencies
- [x] Implement main.py with core functionality
- [x] Configure Azure OpenAI API connection
- [x] Implement researcher data loading and validation
- [x] Create MCP Server wrapper for PubMed integration
- [x] Test PubMed query functionality
- [x] Implement Azure OpenAI analysis for foreign affiliations
- [x] Test end-to-end workflow with sample data
- [x] Add error handling and logging
- [x] Create documentation for usage

### In Progress

- [ ] Optimize confidence scoring algorithm
- [ ] Refine foreign affiliation detection

### To Do

- [ ] Perform final testing with full dataset
- [ ] Add support for additional data sources beyond PubMed
- [ ] Implement more sophisticated analysis for edge cases

## Usage

1. Ensure all dependencies are installed:

   ```
   pip install -r requirements.txt
   ```

2. Make sure the .env file contains the necessary Azure OpenAI API credentials:

   ```
   AZURE_OPENAI_API_ENDPOINT=<endpoint>
   AZURE_OPENAI_API_KEY=<api_key>
   AZURE_OPENAI_API_VERSION=<api_version>
   AZURE_OPENAI_DEPLOYMENT=<deployment_name>
   AZURE_OPENAI_MODEL=<model_name>
   ```

3. Run the analysis:

   ```
   python main.py
   ```

4. Review the output in foreign_disclosure_analysis.csv

## Next Steps

1. Complete the MCP Server wrapper for PubMed integration
2. Test the solution with a small subset of researchers
3. Refine the analysis based on initial results
4. Run the full analysis on all BCH researchers
