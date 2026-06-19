import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.core.logger import setup_logger

# Load environment variables from the .env file
load_dotenv()

logger = setup_logger("LLMClient")

class OpticLLM:
    def __init__(self, temperature=0.1):
        """
        Initializes the connection to the Gemini API securely using .env variables.
        """
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite")
        
        if not self.api_key:
            logger.error("🚨 GOOGLE_API_KEY is missing! Ensure it is set in your .env file.")
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        logger.info(f"🧠 Booting LLM Engine: {self.model_name}")
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=temperature,
            google_api_key=self.api_key
        )

    def analyze(self, user_prompt: str, system_prompt: str = None) -> str:
        """
        Sends prompts to the LLM and guarantees a clean primitive string output,
        handling both raw strings and content block lists gracefully.
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
            
        messages.append(HumanMessage(content=user_prompt))
        
        try:
            response = self.llm.invoke(messages)
            raw_content = response.content
            
            # DEFENSIVE PROGRAMMING: Flatten list-based content blocks into a string
            if isinstance(raw_content, list):
                extracted_texts = []
                for block in raw_content:
                    if isinstance(block, dict) and "text" in block:
                        extracted_texts.append(block["text"])
                    else:
                        extracted_texts.append(str(block))
                return "".join(extracted_texts)
                
            return str(raw_content)
            
        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            return f"Error: {e}"

if __name__ == "__main__":
    try:
        agent = OpticLLM()
        test_system_prompt = "You are a senior DevOps engineer."
        test_user_prompt = "Say 'Hello World' if the client refactor is successful."
        
        print("\nTesting safe block-flattening logic...")
        print("-" * 40)
        answer = agent.analyze(user_prompt=test_user_prompt, system_prompt=test_system_prompt)
        print(f"Result Type: {type(answer)}")
        print(f"Result Value: {answer}")
        print("-" * 40)
    except ValueError:
        print("Test aborted: Fix your .env file first.")