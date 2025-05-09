# Foreign Disclosure Analysis Tool for BCH Researchers

This tool analyzes PubMed publications for Boston Children's Hospital (BCH) researchers to identify foreign affiliations and collaborations, with a particular focus on Russia, North Korea, Iran, and China. The analysis results are output to a CSV file with specific fields.

## Overview

The solution uses the Azure OpenAI API and the Clinical Research MCP Server to analyze PubMed publications for foreign disclosure requirements. It processes a list of BCH researchers from a CSV file, queries PubMed for their publications, analyzes the publications for foreign affiliations, and outputs the results to a CSV file.

## System Architecture

```mermaid
graph TD
    A[Researchers CSV] --> B[Main Application]
    B --> C{PubMed Integration}
    C --> |Query| D[Clinical Research MCP Server]
    D --> |Results| C
    C --> |Publications| E[Foreign Affiliation Analysis]
    E --> |Analysis Request| F[Azure OpenAI API]
    F --> |Analysis Results| E
    E --> G[Output Generation]
    G --> H[CSV Output]

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant App as Main Application
    participant CSV as Researchers CSV
    participant MCP as Clinical Research MCP Server
    participant Azure as Azure OpenAI API
    participant Output as CSV Output

    User->>App: Run analysis
    App->>CSV: Load researchers
    CSV-->>App: Researcher data
    loop For each researcher
        App->>MCP: Query PubMed
        MCP-->>App: Publication data
        loop For each publication
            App->>Azure: Analyze foreign affiliations
            Azure-->>App: Analysis results
            App->>App: Process results
        end
    end
    App->>Output: Generate CSV
    Output-->>User: foreign_disclosure_analysis.csv
```

## Features

- Dynamic loading of researcher data from CSV
- PubMed integration via Clinical Research MCP Server
- Foreign affiliation analysis using Azure OpenAI API
- Special flagging for countries of concern (Russia, North Korea, Iran, China)
- Confidence scoring for foreign involvement
- CSV output with detailed information

## Requirements

- Python 3.9+
- Azure OpenAI API access
- Clinical Research MCP Server access

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/BCH-IDHA/foreign-disclosure-analysis.git
   cd foreign-disclosure-analysis
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure the `.env` file with your Azure OpenAI API credentials:
   ```
   AZURE_OPENAI_API_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_API_VERSION=your_api_version
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   AZURE_OPENAI_MODEL=your_model_name
   ```

## Usage

1. Prepare your researchers CSV file with the following format:

   ```
   Researcher last name, Research first name
   Smith, John
   Doe, Jane
   ```

2. Run the analysis:

   ```
   python main.py
   ```

3. Review the output in `foreign_disclosure_analysis.csv`

## Analysis Process

```mermaid
flowchart TD
    A[Start] --> B[Load Researchers]
    B --> C[Process Each Researcher]
    C --> D[Query PubMed for Publications]
    D --> E{Publications Found?}
    E -->|No| J[Next Researcher]
    E -->|Yes| F[Analyze Each Publication]
    F --> G[Extract Foreign Affiliations]
    G --> H[Flag Countries of Concern]
    H --> I[Generate Output Row]
    I --> K{More Publications?}
    K -->|Yes| F
    K -->|No| J
    J --> L{More Researchers?}
    L -->|Yes| C
    L -->|No| M[Generate CSV Output]
    M --> N[End]
```

## Output Format

The output CSV file contains the following columns:

- **publication_name**: The name of the journal where the research was published
- **research_title**: The title of the research publication
- **author_name**: The name of the BCH researcher
- **organization_affiliation**: The organization affiliation (Boston Children's Hospital)
- **countries_of_origin**: Countries of origin/association
- **flagged**: Indicates whether the publication has any countries of concern (Yes/No)
- **flagged_countries**: Lists the specific countries of concern that were flagged
- **confidence_score**: Confidence score (1-10) regarding foreign involvement
- **funding_source**: Funding sources for the research

## Confidence Scoring Algorithm

```mermaid
graph TD
    A[Start: Base Score = 1] --> B{Countries Found?}
    B -->|Yes| C[+3 Points]
    B -->|No| D{Institutions Found?}
    C --> E{Countries of Concern?}
    E -->|Yes| F[+2 Points]
    E -->|No| D
    D -->|Yes| G[+1 Point]
    D -->|No| H{Funding Sources Found?}
    G --> H
    F --> H
    H -->|Yes| I[+1 Point]
    H -->|No| J{International Collaboration Mentioned?}
    I --> J
    J -->|Yes| K[+1 Point]
    J -->|No| L[Calculate Final Score]
    K --> L
    L --> M[Cap at 10 if > 10]
    M --> N[End]
```

## Project Structure

- `main.py`: Main script for the analysis
- `mcp_server_clinical_research.py`: Wrapper for the Clinical Research MCP Server
- `use_mcp_tool.py`: Wrapper for the MCP tool functionality
- `requirements.txt`: Required Python dependencies
- `researchers.csv`: Input file containing BCH researcher names
- `solution-plan.md`: Implementation plan and progress tracking
- `README.md`: Project documentation

## Component Relationships

```mermaid
classDiagram
    class Main {
        +load_researchers()
        +query_pubmed_publications()
        +analyze_foreign_affiliations()
        +generate_output_row()
        +main()
    }

    class MCPServerClinicalResearch {
        +use_pubmed_search()
        +process_pubmed_results()
        +extract_affiliations()
        +extract_funding_info()
    }

    class UseMCPTool {
        +use_mcp_tool()
    }

    class AzureOpenAI {
        +chat.completions.create()
    }

    Main --> MCPServerClinicalResearch : uses
    Main --> AzureOpenAI : uses
    MCPServerClinicalResearch --> UseMCPTool : uses
```

## Development

This application requires access to both the Azure OpenAI API and the Clinical Research MCP Server. It will not run in a simulated or mock mode. If either service is unavailable, the application will fail with appropriate error messages.

### Requirements

1. Valid Azure OpenAI API credentials configured in the .env file
2. Access to the Clinical Research MCP Server
3. Proper network connectivity to both services

The application performs strict validation of these requirements and will not proceed if they are not met.

## License

[Specify your license here]

## Acknowledgments

- Boston Children's Hospital
- Azure OpenAI API
- Clinical Research MCP Server
