import json
from pathlib import Path
import requests
from google import genai
from google.genai import types
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API configuration
# You'll need to set your Gemini API key as an environment variable: GEMINI_API_KEY
# Get your free API key from: https://aistudio.google.com/app/apikey

def read_text_from_file(file_path: str) -> str:
    """
    Reads text content from a file.
    
    :param file_path: Path to the text file
    :return: Content of the text file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""


def check_grammar_with_ai(text: str) -> Dict[str, Any]:
    """
    Uses Google Gemini to analyze grammar and provide corrections.
    
    :param text: The text to analyze
    :return: Dictionary containing grammar analysis results
    """
    try:
        # Initialize Gemini client (API key from environment variable GEMINI_API_KEY)
        client = genai.Client()
        
        # Set up the prompt for grammar analysis
        prompt = f"""
        Analyze the following text for grammar issues and provide corrections:
        
        Text: "{text}"
        
        Please provide your analysis in the following JSON format:
        {{
            "is_grammatically_correct": true/false,  
            "corrected_text": "corrected version of the text",
            "overall_feedback": "general feedback about the grammar and tell the user clearly where the grammar issues are"
        }}
        
        If the text is grammatically correct, set is_grammatically_correct to true and provide the original text as corrected_text.
        Be specific about any grammar issues found.
        """
        
        # Make API call to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Using the latest Gemini model
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for more consistent results
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
            )
        )
        
        # Extract the response content
        response_text = response.text
        
        # Try to parse the JSON response
        try:
            # Clean the response text to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "is_grammatically_correct": False,
                "corrected_text": "",
                "overall_feedback": "Unable to parse AI response. Raw response: " + response_text
            }
            
    except Exception as e:
        return {
            "is_grammatically_correct": False,
            "corrected_text": "",
            "overall_feedback": f"Error analyzing grammar with Gemini: {str(e)}"
        }




def analyze_grammar(text_content: str) -> Dict[str, Any]:
    """
    High-level function: reads text from file, checks grammar with AI, and formats results.
    
    :param file_path: Path to the input text file
    :return: Dict containing text content, grammar analysis, and formatted issues
    """
    if not text_content:
        return {
            "is_grammatically_correct": False,
            "corrected_text": "",
            "overall_feedback": "No text content found in file"
        }
    
    # Check grammar with AI
    grammar_analysis = check_grammar_with_ai(text_content)
    
    # Format issues
    return {
        "is_grammatically_correct": grammar_analysis.get("is_grammatically_correct", False),
        "corrected_text": grammar_analysis.get("corrected_text", ""),
        "overall_feedback": grammar_analysis.get("overall_feedback", "")
    }


if __name__ == "__main__":
    # Example usage
    file_path = "example_text.txt"  # Replace with your text file path
    result = analyze_grammar(file_path)
    
    print("Is Grammatically Correct:", result["is_grammatically_correct"])
    print("Corrected Text:", result["corrected_text"])
    print("Overall Feedback:", result["overall_feedback"])