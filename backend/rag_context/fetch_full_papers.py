from Bio import Entrez
import os
import re
import time
import xml.etree.ElementTree as ET

# 1. CONFIGURATION
# You MUST provide a valid email address to use NCBI's Entrez API.
Entrez.email = "sujayhsbackup@gmail.com"  # Replace with your actual email

# For IBM Watsonx access (if needed in future scripts):
# IBM_WATSONX_API_KEY = "your_ibm_watsonx_api_key_here"  # Replace with your IBM Watsonx API key
# IBM_WATSONX_URL = "your_ibm_watsonx_url_here"  # Replace with your IBM Watsonx service URL

# Output directory for category files
OUTPUT_DIR = "virus_papers_output"

# For IBM Watsonx access (if needed in future scripts):
# IBM_WATSONX_API_KEY = "your_ibm_watsonx_api_key_here"  # Replace with your IBM Watsonx API key
# IBM_WATSONX_URL = "your_ibm_watsonx_url_here"  # Replace with your IBM Watsonx service URL

# Categorized list of major viruses to research.
# This will create one output file per category (e.g., "Respiratory_Viruses.txt").
virus_categories = {
    "Respiratory Viruses": [
        "SARS-CoV-2", "SARS-CoV", "MERS-CoV", "Influenza A virus", "Influenza B virus",
        "Respiratory Syncytial Virus (RSV)", "Human Rhinovirus", "Adenovirus",
        "Human Metapneumovirus", "Parainfluenza virus",
    ],

    "Gastrointestinal (Enteric) Viruses": [
        "Norovirus", "Rotavirus", "Sapovirus", "Astrovirus", "Hepatitis A virus",
        "Hepatitis E virus", "Poliovirus",
    ],

    "Bloodborne & Sexually Transmitted": [
        "Human immunodeficiency virus 1 (HIV-1)", "Human immunodeficiency virus 2 (HIV-2)",
        "Hepatitis B virus", "Hepatitis C virus", "Hepatitis D virus",
        "Human Papillomavirus (HPV)", "Herpes Simplex Virus 1 (HSV-1)", "Herpes Simplex Virus 2 (HSV-2)",
    ],

    "Vector-borne (Mosquito, Tick, etc.)": [
        "Zika virus", "Dengue virus", "West Nile virus", "Yellow Fever virus",
        "Chikungunya virus", "Japanese Encephalitis virus", "Rift Valley fever virus",
        "Tick-borne encephalitis virus",
    ],

    "Viral Hemorrhagic Fevers": [
        "Ebola virus", "Marburg virus", "Lassa mammarenavirus",
        "Crimean-Congo hemorrhagic fever virus", "Hantavirus",
    ],

    "Childhood & Exanthematous": [
        "Measles virus", "Mumps virus", "Rubella virus", "Varicella-Zoster Virus (VZV)",
        "Epstein-Barr Virus (EBV)", "Cytomegalovirus (CMV)", "Roseolovirus",
    ],

    "Zoonotic & Emerging": [
        "Rabies virus", "Monkeypox virus (Mpox)", "Nipah virus", "Hendra virus",
        "Variola virus", "Camelpox virus",
    ],
}

def fetch_full_papers(virus_name, max_results=10):
    """
    Searches PubMed Central (PMC) for a specific virus and retrieves the full text of open access papers.
    """
    print(f"Fetching full papers for: {virus_name}...")

    # We focus the search on pathogenesis and transmission to support animation logic.
    # Add "open access[filter]" to get full text available papers.
    query = f"({virus_name}[Title/Abstract]) AND (pathogenesis[Title/Abstract] OR transmission[Title/Abstract]) AND open access[filter]"

    try:
        # Step A: Search for the IDs of relevant papers in PMC
        search_handle = Entrez.esearch(db="pmc", term=query, retmax=max_results, sort="relevance")
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results.get("IdList", [])
        if not id_list:
            return f"No open access full text research found for {virus_name}.\n"

        # Step B: Fetch the full text XML for those IDs
        ids = ",".join(id_list)
        fetch_handle = Entrez.efetch(db="pmc", id=ids, rettype="full", retmode="xml")
        xml_data = fetch_handle.read()
        fetch_handle.close()

        # Parse the XML to extract full text
        root = ET.fromstring(xml_data)
        full_texts = []

        # PMC XML structure: each article is under <article>
        for article in root.findall(".//article"):
            title = article.find(".//article-title")
            title_text = title.text if title is not None else "No Title"

            # Extract body text
            body = article.find(".//body")
            if body is not None:
                body_text = ET.tostring(body, encoding='unicode', method='text')
            else:
                body_text = "No full text body available."

            full_texts.append(f"Title: {title_text}\n\n{body_text}\n")

        # Combine all papers for this virus
        separator = "=" * 80
        combined = f"\n{separator}\nPATHOGEN: {virus_name.upper()}\n{separator}\n" + "\n\n".join(full_texts)
        return combined + "\n"

    except Exception as e:
        return f"Error retrieving data for {virus_name}: {str(e)}\n"

def _sanitize_filename(name: str) -> str:
    """Make a filesystem-safe filename from a category name."""
    sanitized = re.sub(r"[^0-9A-Za-z_-]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized or "category"


def run_compilation(output_dir=OUTPUT_DIR, per_category=True):
    """Loops through the virus categories and writes full paper texts to separate files."""
    os.makedirs(output_dir, exist_ok=True)

    header = (
        "VIRAL RESEARCH KNOWLEDGE BASE FOR GEN-AI SEMANTIC SEARCH\n"
        "Source: NCBI PubMed Central (PMC) / Entrez API\n"
        "Focus: Full Text of Open Access Papers on Pathogenesis and Transmission Mechanisms\n\n"
    )

    if per_category:
        for category, viruses in virus_categories.items():
            out_path = os.path.join(output_dir, f"{_sanitize_filename(category)}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(header)
                for virus in viruses:
                    content = fetch_full_papers(virus)
                    f.write(content)
                    time.sleep(0.5)
            print(f"Saved category file: {out_path}")

    else:
        # Fallback: single file containing everything
        out_path = os.path.join(output_dir, "Compiled_Full_Virus_Papers.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(header)
            for viruses in virus_categories.values():
                for virus in viruses:
                    content = fetch_full_papers(virus)
                    f.write(content)
                    time.sleep(0.5)
        print(f"\nSuccess! Full knowledge base compiled in: {out_path}")


if __name__ == "__main__":
    run_compilation()

if __name__ == "__main__":
    run_compilation()