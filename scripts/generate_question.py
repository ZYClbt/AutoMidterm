#!/usr/bin/env python3
"""
Script to generate midterm exam questions for cognitive and reasoning course (and potentially any other courses)
Generates questions and answers based on course PDF files
"""

import os
import json
import argparse
from pathlib import Path
from openai import OpenAI
import PyPDF2
import sys


def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None


def load_prompt_template(prompt_path):
    """Load prompt template"""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return None


# Supported models and their context length information
MODEL_INFO = {
    "gpt-5": {
        "name": "gpt-5",
        "context": "200k+ tokens",
        "description": "Latest model with enhanced reasoning and multimodal processing"
    },
    "gpt-4o": {
        "name": "gpt-4o",
        "context": "128k tokens",
        "description": "Currently recommended, balanced performance and cost"
    },
    "gpt-4-turbo": {
        "name": "gpt-4-turbo",
        "context": "128k tokens",
        "description": "High-performance model"
    },
    "gpt-4o-mini": {
        "name": "gpt-4o-mini",
        "context": "128k tokens",
        "description": "More economical option"
    }
}


def generate_questions(lecture_content, num_questions, prompt_template, api_key, model="gpt-4o"):
    """Generate questions and answers using OpenAI API"""
    client = OpenAI(api_key=api_key)
    
    # Display model information being used
    if model in MODEL_INFO:
        info = MODEL_INFO[model]
        print(f"Using model: {info['name']} (Context: {info['context']})")
    
    # Build complete prompt
    prompt = prompt_template.format(num_questions=num_questions) + "\n\n" + lecture_content
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful teaching assistant that generates exam questions based on lecture content. Always respond with valid JSON format containing a 'questions' array."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            response_format={"type": "json_object"}  # Ensure JSON format response
        )
        
        result = response.choices[0].message.content
        questions_data = json.loads(result)
        
        # Validate JSON format
        if "questions" not in questions_data:
            print("Warning: Returned JSON format is incorrect, missing 'questions' field")
            # If returned data is a questions array, convert to standard format
            if isinstance(questions_data, list):
                questions_data = {"questions": questions_data}
            else:
                return None
        
        return questions_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        if 'result' in locals():
            print(f"Returned content: {result[:500]}...")  # Print first 500 characters for debugging
        return None
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


def process_lecture(pdf_path, num_questions, prompt_template, api_key, output_dir, model="gpt-4o"):
    """Process a single lecture PDF file"""
    print(f"Processing: {pdf_path}")
    
    # Extract PDF text
    lecture_content = extract_text_from_pdf(pdf_path)
    if not lecture_content:
        print(f"Unable to extract PDF content: {pdf_path}")
        return False
    
    print(f"Extracted {len(lecture_content)} characters of text content")
    
    # Generate questions
    print(f"Generating {num_questions} questions...")
    questions_data = generate_questions(lecture_content, num_questions, prompt_template, api_key, model)
    
    if not questions_data:
        print(f"Failed to generate questions: {pdf_path}")
        return False
    
    # Save as JSON file
    pdf_name = Path(pdf_path).stem
    output_path = Path(output_dir) / f"{pdf_name}.json"
    
    # Ensure output directory exists
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved questions to: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate midterm exam questions for cognitive and reasoning course')
    parser.add_argument(
        '--num-questions',
        type=int,
        default=20,
        help='Number of questions to generate per lecture (default: 5)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key (if not provided, will read from OPENAI_API_KEY environment variable)'
    )
    parser.add_argument(
        '--slices-dir',
        type=str,
        default='slices',
        help='Directory containing PDF files (default: slices)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='questions',
        help='Output directory for JSON files (default: questions)'
    )
    parser.add_argument(
        '--prompt-file',
        type=str,
        default='scripts/prompt.txt',
        help='Prompt template file (default: scripts/prompt.txt)'
    )
    parser.add_argument(
        '--lecture',
        type=str,
        help='Process only the specified lecture file (e.g., Lecture.01.Introduction.EECS.pdf)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-5',
        choices=list(MODEL_INFO.keys()),
        help='Model to use (default: gpt-4o). Options: gpt-5 (latest, 200k+ tokens), gpt-4o (recommended, 128k tokens), gpt-4-turbo (128k tokens), gpt-4o-mini (economical, 128k tokens)'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: Please provide OpenAI API key (via --api-key argument or set OPENAI_API_KEY environment variable)")
        sys.exit(1)
    
    # Load prompt template
    prompt_template = load_prompt_template(args.prompt_file)
    if not prompt_template:
        print(f"Error: Unable to load prompt file: {args.prompt_file}")
        sys.exit(1)
    
    # Get PDF file list
    slices_dir = Path(args.slices_dir)
    if not slices_dir.exists():
        print(f"Error: slices directory does not exist: {args.slices_dir}")
        sys.exit(1)
    
    if args.lecture:
        # Process only the specified lecture
        pdf_path = slices_dir / args.lecture
        if not pdf_path.exists():
            print(f"Error: File does not exist: {pdf_path}")
            sys.exit(1)
        pdf_files = [pdf_path]
    else:
        # Process all PDF files
        pdf_files = sorted(slices_dir.glob('*.pdf'))
    
    if not pdf_files:
        print(f"Error: No PDF files found in {args.slices_dir} directory")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files")
    print(f"Each lecture will generate {args.num_questions} questions")
    
    # Display model information
    if args.model in MODEL_INFO:
        info = MODEL_INFO[args.model]
        print(f"Using model: {info['name']} - {info['description']} (Context: {info['context']})\n")
    else:
        print(f"Using model: {args.model}\n")
    
    # Process each PDF file
    success_count = 0
    for pdf_path in pdf_files:
        if process_lecture(pdf_path, args.num_questions, prompt_template, api_key, args.output_dir, args.model):
            success_count += 1
        print()  # Empty line separator
    
    print(f"Complete! Successfully processed {success_count}/{len(pdf_files)} files")


if __name__ == '__main__':
    main()

