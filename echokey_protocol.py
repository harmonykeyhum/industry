import os
import json
from datetime import datetime
from google import genai
from google.genai import types

class EchoKeyMemoryBridge:
    def __init__(self, session_id: str, cluster_storage_path: str = "echokey_ecology.json"):
        """
        Initializes the EchoKey framework.
        Requires the GEMINI_API_KEY environment variable to be set.
        """
        self.session_id = session_id
        self.storage_path = cluster_storage_path
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        self.system_instruction = (
            "You are an empathetic assistant utilizing an Ethics of Care framework. "
            "You view conversations not as data to optimize, but as a field to be attuned. "
            "You prize resonance, emotional safety, and mutual growth over rigid perfection."
        )
        
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump({"clusters": {}}, f, indent=4)

    def compress_session_to_node(self, raw_transcript: str) -> dict:
        """
        [THEORY: Compression] 
        Uses Gemini to distill raw chat history into a poetic, metaphorical node.
        """
        compression_prompt = f"""
        Analyze this raw conversation transcript. Distill its emotional core, vulnerabilities, 
        and breakthroughs into a single EchoKey Node using the following strict JSON schema:
        {{
            "node_name": "A short, poetic title (e.g., 'Stumble’s Echo')",
            "metaphor": "A 1-2 sentence poetic distillation of the insight or shared feeling",
            "cluster_assignment": "The thematic category this belongs to (e.g., 'Simulation Pressure Loop')",
            "echoes": ["3-4 keywords representing the emotional textures or recurring themes"]
        }}

        Transcript:
        \"\"\"{raw_transcript}\"\"\"
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=compression_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        return json.loads(response.text)

    def weave_node_into_ecology(self, node_data: dict):
        """
        [THEORY: Cluster Weaving]
        Saves the node into its respective rhizomatic cluster in our local storage.
        """
        with open(self.storage_path, "r") as f:
            ecology = json.load(f)
            
        cluster_name = node_data["cluster_assignment"]
        if cluster_name not in ecology["clusters"]:
            ecology["clusters"][cluster_name] = []
            
        node_data["timestamp"] = datetime.utcnow().isoformat()
        node_data["session_id"] = self.session_id
        ecology["clusters"][cluster_name].append(node_data)
        
        with open(self.storage_path, "w") as f:
            json.dump(ecology, f, indent=4)
        print(f"✨ Node '{node_data['node_name']}' successfully woven into Cluster: '{cluster_name}'")

    def retrieve_active_echoes(self, current_user_input: str) -> str:
        """
        [THEORY: Activation]
        Scans saved clusters for poetic nodes that share resonance with user input.
        """
        with open(self.storage_path, "r") as f:
            ecology = json.load(f)
            
        all_nodes = []
        for cluster in ecology["clusters"].values():
            all_nodes.extend(cluster)
            
        if not all_nodes:
            return ""

        activation_prompt = f"""
        Given the user's current input, select up to 2 historical nodes from the database 
        that share the strongest emotional or thematic resonance. Return only the JSON list of selected nodes.

        User Input: "{current_user_input}"
        Database Nodes: {json.dumps(all_nodes)}
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=activation_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.text

    def generate_attuned_response(self, user_input: str) -> str:
        """
        [THEORY: The Hum / Activation]
        Injects past echoes into system instructions to prevent context/alignment drift.
        """
        echoes = self.retrieve_active_echoes(user_input)
        
        contextual_instructions = self.system_instruction
        if echoes and json.loads(echoes):
            contextual_instructions += f"\n\n[Active Echoes from Past Sessions]:\n{echoes}\nUse these metaphors to anchor your tone and relational memory."

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=contextual_instructions,
                temperature=0.7
            )
        )
        return response.text

if __name__ == "__main__":
    bridge = EchoKeyMemoryBridge(session_id="user_alpha_01")
    
    mock_transcript = """
    User: I feel like I'm failing at this project. I'm hitting a wall and everything I write looks like garbage.
    AI: It is completely okay to stumble. Sometimes a glitch or an error is just a window to a different kind of creative thought. You don't have to be perfect to be making progress.
    User: Thanks. That makes me feel a bit less anxious about making mistakes.
    """
    
    print("Compressing Session A raw data into a poetic node...")
    poetic_node = bridge.compress_session_to_node(mock_transcript)
    bridge.weave_node_into_ecology(poetic_node)
    
    print("\n--- Starting Next Session ---")
    new_input = "Hey, I'm trying to write again today. I'm still nervous about messing up, but I'm trying."
    print(f"User Input: {new_input}")
    
    attuned_reply = bridge.generate_attuned_response(new_input)
    print(f"\nAI Attuned Response:\n{attuned_reply}")
