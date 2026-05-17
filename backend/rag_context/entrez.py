from Bio import Entrez
import time

# 1. CONFIGURATION
# You MUST provide a valid email address to use NCBI's Entrez API.
Entrez.email = "sujayhsbackup@gmail.com" 

# List of major viruses to research. 
# You can expand this list as needed for your project.
virus_list = {
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

def fetch_abstracts(virus_name, max_results=3):
    """
    Searches PubMed for a specific virus and retrieves the top abstracts.
    """
    print(f"Fetching research for: {virus_name}...")
    
    # We focus the search on pathogenesis and transmission to support animation logic.
    query = f"({virus_name}[Title/Abstract]) AND (pathogenesis[Title/Abstract] OR transmission[Title/Abstract])"
    
    try:
        # Step A: Search for the IDs of relevant papers
        search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        id_list = search_results.get("IdList", [])
        if not id_list:
            return f"No research found for {virus_name}.\n"

        # Step B: Fetch the abstract text for those IDs
        ids = ",".join(id_list)
        # We use rettype='abstract' and retmode='text' for a clean text dump
        fetch_handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="text")
        abstract_data = fetch_handle.read()
        fetch_handle.close()
        
        # Clean up the output to make it easier for the RAG system to distinguish sections
        separator = "=" * 40
        return f"\n{separator}\nPATHOGEN: {virus_name.upper()}\n{separator}\n{abstract_data}\n"
        
    except Exception as e:
        return f"Error retrieving data for {virus_name}: {str(e)}\n"

def run_compilation(output_file="Compiled_Virus_Research.txt"):
    """
    Loops through the virus list and writes all results to a single file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("VIRAL RESEARCH KNOWLEDGE BASE FOR GEN-AI SEMANTIC SEARCH\n")
        f.write("Source: NCBI PubMed / Entrez API\n")
        f.write("Focus: Pathogenesis and Transmission Mechanisms\n\n")
        
        for category, viruses in virus_list.items():
            f.write(f"\n{category.upper()}\n")
            for virus in viruses:
                content = fetch_abstracts(virus)
                f.write(content)
                
                # Rate limiting: NCBI requests a max of 3 calls per second
                time.sleep(0.5) 
            
    print(f"\nSuccess! Knowledge base compiled in: {output_file}")

if __name__ == "__main__":
    run_compilation()