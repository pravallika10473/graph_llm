import json
import networkx as nx
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class KnowledgeGraphQuery:
    def __init__(self, ontology_file: str = "ontology.json"):
        """
        Initialize the knowledge graph query system.
        
        Args:
            ontology_file: Path to the JSON file containing extracted ontologies
        """
        self.ontology_file = ontology_file
        self.graph = nx.DiGraph()
        self.papers_data = []
        self.load_ontologies()
        self.build_graph()
    
    def load_ontologies(self):
        """Load all ontologies from the JSON file."""
        try:
            with open(self.ontology_file, "r") as f:
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
                        # If that fails, try JSON Lines format (legacy support)
                        ontologies = []
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        for line in lines:
                            try:
                                ontology = json.loads(line)
                                ontologies.append(ontology)
                            except json.JSONDecodeError:
                                continue
                    
                    # Filter out error entries
                    for ontology in ontologies:
                        if "error" not in ontology:
                            self.papers_data.append(ontology)
        except FileNotFoundError:
            print(f"Warning: {self.ontology_file} not found. Starting with empty graph.")
    
    def build_graph(self):
        """Build NetworkX graph from loaded ontologies."""
        for paper_data in self.papers_data:
            paper_title = paper_data.get("paper", {}).get("title", "Unknown Paper")
            
            # Add paper node
            self.graph.add_node(paper_title, type="paper", data=paper_data["paper"])
            
            # Add technique nodes and edges
            for technique in paper_data.get("techniques", []):
                tech_name = technique["name"]
                self.graph.add_node(tech_name, type="technique", data=technique)
                self.graph.add_edge(paper_title, tech_name, relationship="USES")
            
            # Add result nodes and edges
            for result in paper_data.get("results", []):
                result_name = f"{result['metric']}: {result['value']}"
                self.graph.add_node(result_name, type="result", data=result)
                self.graph.add_edge(paper_title, result_name, relationship="REPORTS")
            
            # Add application nodes and edges
            for application in paper_data.get("applications", []):
                app_name = f"{application['domain']} - {application['purpose']}"
                self.graph.add_node(app_name, type="application", data=application)
                self.graph.add_edge(paper_title, app_name, relationship="ADDRESSES")
            
            # Add relationships from the relationships list
            for rel in paper_data.get("relationships", []):
                subject = rel["subject"]
                predicate = rel["predicate"]
                obj = rel["object"]
                
                # Ensure nodes exist
                if not self.graph.has_node(subject):
                    self.graph.add_node(subject)
                if not self.graph.has_node(obj):
                    self.graph.add_node(obj)
                
                self.graph.add_edge(subject, obj, relationship=predicate)
    
    def query_by_technique(self, technique_name: str) -> Dict[str, Any]:
        """Find papers and related information for a specific technique."""
        results = {
            "technique": technique_name,
            "papers": [],
            "applications": [],
            "results": []
        }
        
        # Find papers that use this technique
        for paper_data in self.papers_data:
            techniques = [t["name"] for t in paper_data.get("techniques", [])]
            if technique_name.lower() in [t.lower() for t in techniques]:
                results["papers"].append({
                    "title": paper_data["paper"]["title"],
                    "year": paper_data["paper"]["year"],
                    "authors": paper_data["paper"]["authors"]
                })
                
                # Get related applications and results
                results["applications"].extend(paper_data.get("applications", []))
                results["results"].extend(paper_data.get("results", []))
        
        return results
    
    def query_by_application(self, domain: str) -> Dict[str, Any]:
        """Find techniques and papers for a specific application domain."""
        results = {
            "domain": domain,
            "papers": [],
            "techniques": [],
            "results": []
        }
        
        for paper_data in self.papers_data:
            applications = paper_data.get("applications", [])
            for app in applications:
                if domain.lower() in app["domain"].lower():
                    results["papers"].append({
                        "title": paper_data["paper"]["title"],
                        "year": paper_data["paper"]["year"],
                        "purpose": app["purpose"]
                    })
                    results["techniques"].extend(paper_data.get("techniques", []))
                    results["results"].extend(paper_data.get("results", []))
        
        return results
    
    def query_by_metric(self, metric_name: str) -> Dict[str, Any]:
        """Find papers and techniques that report specific metrics."""
        results = {
            "metric": metric_name,
            "papers": [],
            "techniques": [],
            "best_results": []
        }
        
        for paper_data in self.papers_data:
            results_list = paper_data.get("results", [])
            for result in results_list:
                if metric_name.lower() in result["metric"].lower():
                    results["papers"].append(paper_data["paper"])
                    results["techniques"].extend(paper_data.get("techniques", []))
                    results["best_results"].append(result)
        
        # Sort by value if numeric
        try:
            results["best_results"].sort(key=lambda x: float(x["value"]), reverse=True)
        except:
            pass
        
        return results
    
    def query_similar_papers(self, paper_title: str) -> List[Dict[str, Any]]:
        """Find papers with similar techniques or applications."""
        target_paper = None
        for paper_data in self.papers_data:
            if paper_title.lower() in paper_data["paper"]["title"].lower():
                target_paper = paper_data
                break
        
        if not target_paper:
            return []
        
        similar_papers = []
        target_techniques = [t["name"] for t in target_paper.get("techniques", [])]
        target_domains = [a["domain"] for a in target_paper.get("applications", [])]
        
        for paper_data in self.papers_data:
            if paper_data["paper"]["title"] == target_paper["paper"]["title"]:
                continue
            
            paper_techniques = [t["name"] for t in paper_data.get("techniques", [])]
            paper_domains = [a["domain"] for a in paper_data.get("applications", [])]
            
            # Calculate similarity based on shared techniques and domains
            technique_overlap = len(set(target_techniques) & set(paper_techniques))
            domain_overlap = len(set(target_domains) & set(paper_domains))
            
            if technique_overlap > 0 or domain_overlap > 0:
                similar_papers.append({
                    "paper": paper_data["paper"],
                    "technique_similarity": technique_overlap,
                    "domain_similarity": domain_overlap,
                    "shared_techniques": list(set(target_techniques) & set(paper_techniques)),
                    "shared_domains": list(set(target_domains) & set(paper_domains))
                })
        
        return sorted(similar_papers, key=lambda x: x["technique_similarity"] + x["domain_similarity"], reverse=True)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about the knowledge graph."""
        return {
            "total_papers": len(self.papers_data),
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {
                "paper": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "paper"]),
                "technique": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "technique"]),
                "result": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "result"]),
                "application": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "application"])
            }
        }

class LLMQueryInterface:
    def __init__(self, knowledge_graph: KnowledgeGraphQuery):
        self.kg = knowledge_graph
    
    def query_with_llm(self, user_query: str, model: str = "gpt-4o") -> str:
        """
        Query the knowledge graph and pass relevant information to LLM for response.
        
        Args:
            user_query: Natural language query from user
            model: LLM model to use for response generation
            
        Returns:
            LLM response with relevant graph information
        """
        # Extract relevant information from the knowledge graph based on query
        relevant_info = self._extract_relevant_info(user_query)
        
        # Create context for LLM
        context = self._create_context(relevant_info)
        
        # Generate response using LLM
        prompt = f"""
You are a research assistant with access to a knowledge graph of academic papers, techniques, applications, and results.

User Query: {user_query}

Relevant Information from Knowledge Graph:
{context}

Please provide a comprehensive answer based on the available information. If the information is insufficient, please indicate what additional data would be helpful.
"""
        
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant with expertise in academic literature analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _extract_relevant_info(self, query: str) -> Dict[str, Any]:
        """Extract relevant information from knowledge graph based on query."""
        query_lower = query.lower()
        relevant_info = {
            "papers": [],
            "techniques": [],
            "applications": [],
            "results": []
        }
        
        # Simple keyword matching - can be enhanced with more sophisticated NLP
        if any(word in query_lower for word in ["technique", "method", "approach", "model"]):
            # Look for technique-related queries
            for paper_data in self.kg.papers_data:
                relevant_info["techniques"].extend(paper_data.get("techniques", []))
        
        if any(word in query_lower for word in ["application", "domain", "use case", "purpose"]):
            # Look for application-related queries
            for paper_data in self.kg.papers_data:
                relevant_info["applications"].extend(paper_data.get("applications", []))
        
        if any(word in query_lower for word in ["result", "performance", "accuracy", "bleu", "metric"]):
            # Look for result-related queries
            for paper_data in self.kg.papers_data:
                relevant_info["results"].extend(paper_data.get("results", []))
        
        # Always include paper information
        for paper_data in self.kg.papers_data:
            relevant_info["papers"].append(paper_data["paper"])
        
        return relevant_info
    
    def _create_context(self, relevant_info: Dict[str, Any]) -> str:
        """Create context string from relevant information."""
        context_parts = []
        
        if relevant_info["papers"]:
            context_parts.append("PAPERS:")
            for paper in relevant_info["papers"][:5]:  # Limit to top 5
                context_parts.append(f"- {paper['title']} ({paper.get('year', 'N/A')}) by {', '.join(paper.get('authors', []))}")
        
        if relevant_info["techniques"]:
            context_parts.append("\nTECHNIQUES:")
            for tech in relevant_info["techniques"][:5]:
                context_parts.append(f"- {tech['name']} ({tech.get('type', 'N/A')})")
        
        if relevant_info["applications"]:
            context_parts.append("\nAPPLICATIONS:")
            for app in relevant_info["applications"][:5]:
                context_parts.append(f"- {app['domain']}: {app['purpose']}")
        
        if relevant_info["results"]:
            context_parts.append("\nRESULTS:")
            for result in relevant_info["results"][:5]:
                context_parts.append(f"- {result['metric']}: {result['value']} (Dataset: {result.get('dataset', 'N/A')})")
        
        return "\n".join(context_parts) if context_parts else "No relevant information found."

def load_results(results_file="results.json"):
    """Load existing query results from JSON file."""
    try:
        with open(results_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_results(results, results_file="results.json"):
    """Save query results to JSON file."""
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

def interactive_query():
    """Interactive terminal interface for querying the knowledge graph."""
    print("🔍 Knowledge Graph Query Interface")
    print("=" * 50)
    
    # Initialize knowledge graph and LLM interface
    print("Loading knowledge graph...")
    kg = KnowledgeGraphQuery()
    llm_interface = LLMQueryInterface(kg)
    
    # Show statistics
    stats = kg.get_graph_statistics()
    print(f"\n📊 Knowledge Graph Statistics:")
    print(f"   • Papers: {stats['total_papers']}")
    print(f"   • Techniques: {stats['node_types']['technique']}")
    print(f"   • Applications: {stats['node_types']['application']}")
    print(f"   • Results: {stats['node_types']['result']}")
    
    # Load existing results
    results = load_results()
    print(f"\n📝 Previous queries: {len(results)}")
    
    print("\n" + "=" * 50)
    print("💡 Type your questions about the research papers!")
    print("   Examples:")
    print("   • 'What are the best techniques for machine translation?'")
    print("   • 'Which papers use transformer architecture?'")
    print("   • 'What applications are addressed by these papers?'")
    print("   • 'exit' or 'quit' to stop")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            user_query = input("\n❓ Your question: ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_query:
                print("Please enter a question.")
                continue
            
            print("\n🤔 Thinking...")
            
            # Query the LLM
            llm_response = llm_interface.query_with_llm(user_query)
            
            # Display the response
            print("\n🤖 Answer:")
            print("-" * 40)
            print(llm_response)
            print("-" * 40)
            
            # Save to results
            result_entry = {
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "query": user_query,
                "answer": llm_response,
                "graph_stats": stats
            }
            
            results.append(result_entry)
            save_results(results)
            
            print(f"\n✅ Query and answer saved to results.json")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")

def example_queries():
    """Demonstrate various query types."""
    kg = KnowledgeGraphQuery()
    llm_interface = LLMQueryInterface(kg)
    
    print("=== Knowledge Graph Statistics ===")
    stats = kg.get_graph_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n=== Example Queries ===")
    
    # Query by technique
    print("\n1. Query by Technique:")
    technique_results = kg.query_by_technique("Transformer")
    print(json.dumps(technique_results, indent=2))
    
    # Query by application
    print("\n2. Query by Application:")
    app_results = kg.query_by_application("translation")
    print(json.dumps(app_results, indent=2))
    
    # Query with LLM
    print("\n3. LLM Query:")
    llm_response = llm_interface.query_with_llm("What are the best techniques for machine translation?")
    print(llm_response)

if __name__ == "__main__":
    interactive_query()
