from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
import os
import base64
from dotenv import load_dotenv
import sys
import json

# Load environment variables from .env file
load_dotenv()

# Configuration
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "GPT4-Vision")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
max_tokens = 1000  # Define max_tokens constant

# Print debug information about the configuration
print(f"Debug - API Key loaded: {api_key[:5]}...{api_key[-5:]}")
print(f"Debug - Endpoint: {endpoint}")
print(f"Debug - Deployment: {deployment}")
print(f"Debug - API Version: {api_version}")

if not all([api_key, endpoint, deployment]):
    print("Error: Azure OpenAI configuration not found in environment variables!")
    print("Please make sure you have created a .env file in the project root with your Azure OpenAI configuration:")
    print("AZURE_OPENAI_API_KEY=your_api_key_here")
    print("AZURE_OPENAI_ENDPOINT=your_endpoint_here")
    print("AZURE_OPENAI_DEPLOYMENT=your_deployment_here")
    print("AZURE_OPENAI_API_VERSION=2024-12-01-preview (optional)")
    sys.exit(1)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint,
)

# Print additional debug information about the client
print(f"Debug - Client initialized with:")
print(f"  - API Key (first/last 5): {api_key[:5]}...{api_key[-5:]}")
print(f"  - API Version: {api_version}")
print(f"  - Azure Endpoint: {endpoint}")
print(f"  - Deployment: {deployment}")

app = FastAPI(
    title="Style-Finder API",
    description="API for analyzing fashion outfits from images.",
    version="0.1.0",
)

# --- CORS Middleware ---
# This allows the frontend (running on a different port) to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def analyze_image_with_gpt4v(image_content: bytes) -> dict:
    """
    Send the image to GPT-4V for analysis and get fashion insights.
    """
    try:
        # Convert image to base64
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        print(f"Debug - Using deployment: {deployment}")
        print(f"Debug - Using endpoint: {endpoint}")
        print(f"Debug - API version: {api_version}")
        print(f"Debug - Client configuration:")
        print(f"  - base_url: {client.base_url}")
        
        # Prepare the messages with a more structured prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this outfit and provide a structured response with the following:
1. Description: Overall style and vibe
2. Color Tones: Main colors and their combinations
3. Core Apparel: Main clothing pieces
4. Accessories: Any accessories or additional items
5. Fashion Tips: Styling suggestions and recommendations
6. Similar Items: Suggest 3 similar items that could be found on Nordstrom, including name, brief description, and estimated price range"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        print("Debug - Attempting to create chat completion...")
        print("Debug - Request configuration:")
        print(f"  - model: {deployment}")
        print(f"  - max_tokens: {max_tokens}")
        print(f"  - messages: [user message with text and image]")
        
        # Make the API call with the required parameters
        response = client.chat.completions.create(
            model=deployment,  # Use the deployment name as the model
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Extract the raw response
        result = response.choices[0].message.content
        print(f"Debug - Raw GPT response: {result}")
        
        # Initialize the response structure
        analysis = {
            'description': '',
            'colorTones': '',
            'coreApparel': '',
            'accessories': ''
        }
        fashion_tips = []
        suggested_items = []
        
        # Split into sections by markdown headers
        sections = result.split('###')
        
        for section in sections:
            if not section.strip():
                continue
                
            # Clean up the section
            section = section.strip()
            
            # Extract the section title and content
            lines = section.split('\n')
            title = lines[0].strip().lower()
            content = '\n'.join(lines[1:]).strip()
            
            # Remove any remaining markdown formatting
            content = content.replace('*', '').replace('---', '').strip()
            
            # Parse each section based on its title
            if 'description' in title or '1.' in title:
                analysis['description'] = content
            elif 'color' in title or '2.' in title:
                analysis['colorTones'] = content
            elif 'core' in title or 'apparel' in title or '3.' in title:
                analysis['coreApparel'] = content
            elif 'accessories' in title or '4.' in title:
                analysis['accessories'] = content
            elif 'fashion tips' in title or '5.' in title:
                # Split tips into a list
                tips = [tip.strip('- ').strip() for tip in content.split('\n') if tip.strip().startswith('-')]
                fashion_tips = tips
            elif 'similar items' in title or '6.' in title:
                # Parse suggested items
                items = []
                current_item = {}
                
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                        if current_item:
                            items.append(current_item)
                        # Extract name more safely
                        name = line.split('.')[1].strip()  # Remove the number
                        if '**' in name:
                            name = name.split('**')[1].strip()  # Extract from bold if present
                        else:
                            name = name.strip()  # Just clean up whitespace
                            
                        current_item = {
                            'name': name,
                            'description': '',
                            'imageUrl': f"https://www.nordstrom.com/s/{name.lower().replace(' ', '-')}",
                            'productUrl': f"https://www.nordstrom.com/s/{name.lower().replace(' ', '-')}"
                        }
                    elif line.startswith('-'):
                        line = line.strip('- ').strip()
                        if 'Price Range' in line or 'Estimated Price' in line or 'price range' in line.lower():
                            continue
                        if 'Description:' in line:
                            current_item['description'] = line.split('Description:')[1].strip()
                        else:
                            current_item['description'] = line
                
                if current_item:
                    items.append(current_item)
                suggested_items = items
        
        # Create the final response
        response_data = {
            'analysis': analysis,
            'fashionTips': fashion_tips,
            'suggestedItems': suggested_items
        }
        
        print(f"Debug - Parsed response: {response_data}")
        return response_data
        
    except Exception as e:
        print(f"Debug - API call error details: {str(e)}")
        print(f"Debug - API error type: {type(e)}")
        print(f"Debug - Full API error: {e.__dict__}")
        raise HTTPException(
            status_code=500,
            detail=f"API call failed: {str(e)}"
        )

@app.post("/api/analyze")
async def analyze_outfit(file: UploadFile = File(...)):
    """
    Endpoint to analyze an outfit image using GPT-4V and return fashion insights.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    # Read the image content
    image_contents = await file.read()
    
    # Get analysis from GPT-4V
    analysis = analyze_image_with_gpt4v(image_contents)
    
    return analysis

@app.get("/")
def read_root():
    return {"message": "Welcome to the Style-Finder API"}

# To run this app:
# uvicorn src.backend.main:app --reload 