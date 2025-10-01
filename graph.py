import PyPDF2
import openai
import json
from prompt import extraction_prompt
from dotenv import load_dotenv
import os
import networkx as nx
import matplotlib.pyplot as plt

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_ontology_from_pdf(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    response = openai.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": f"Text: {pdf_text}"}
        ]
    )
    content = response.output_text.strip()
    try:
        ontology = json.loads(content)
    except json.JSONDecodeError:
        ontology = {"error": "Failed to parse JSON from the model response.", "raw_response": content}
    return ontology

def visualize_ontology(json_file, output_img="graph.png"):
    # Load all ontologies and visualize the last one
    ontologies = load_existing_ontologies(json_file)
    if not ontologies:
        print("No valid ontologies found to visualize")
        return
    
    # Use the last ontology for visualization
    ontology = ontologies[-1]
    G = nx.DiGraph()

    def add_nodes_edges(data, parent=None):
        if isinstance(data, dict):
            for key, value in data.items():
                G.add_node(key)
                if parent:
                    G.add_edge(parent, key)
                add_nodes_edges(value, key)
        elif isinstance(data, list):
            for item in data:
                add_nodes_edges(item, parent)
        else:
            if parent:
                G.add_node(str(data))
                G.add_edge(parent, str(data))

    add_nodes_edges(ontology)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10, arrowsize=20)
    plt.title("Ontology Graph Visualization")
    plt.savefig(output_img)
    plt.close()

def load_existing_ontologies(json_file="ontology.json"):
    """Load existing ontologies from JSON file."""
    ontologies = []
    try:
        with open(json_file, "r") as f:
            content = f.read().strip()
            if content:
                # Try to parse as single JSON array first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        ontologies = data
                    else:
                        ontologies = [data]
                except json.JSONDecodeError:
                    # If that fails, try JSON Lines format
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    for line in lines:
                        try:
                            ontologies.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
    except FileNotFoundError:
        pass
    return ontologies

def save_ontologies(ontologies, json_file="ontology.json"):
    """Save ontologies as a valid JSON array."""
    with open(json_file, "w") as f:
        json.dump(ontologies, f, indent=2)

if __name__ == "__main__":
    sample_pdf_path = "papers/googles_neural_machine_translation_system.pdf"
    ontology = extract_ontology_from_pdf(sample_pdf_path)
    
    # Load existing ontologies and add new one
    existing_ontologies = load_existing_ontologies()
    existing_ontologies.append(ontology)
    
    # Save all ontologies as a valid JSON array
    save_ontologies(existing_ontologies)
    
    print(json.dumps(ontology, indent=4))
    visualize_ontology("ontology.json")
