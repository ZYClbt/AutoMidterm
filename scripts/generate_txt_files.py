#!/usr/bin/env python3
"""
Read all JSON files from the questions folder and generate three txt files:
1. questions.txt - Contains only questions (with numbering)
2. answers.txt - Contains only answers (with numbering)
3. questions_and_answers.txt - Questions and answers appear adjacent (with numbering)
"""

import json
import argparse
from pathlib import Path


def load_all_questions(questions_dir):
    """Load questions and answers from all JSON files"""
    all_questions = []
    questions_dir = Path(questions_dir)
    
    # Get all JSON files and sort by filename
    json_files = sorted(questions_dir.glob('*.json'))
    
    if not json_files:
        print(f"Error: No JSON files found in {questions_dir} directory")
        return None
    
    print(f"Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract questions and answers
            if "questions" in data:
                for item in data["questions"]:
                    if "question" in item and "answer" in item:
                        all_questions.append({
                            "question": item["question"],
                            "answer": item["answer"],
                            "source": json_file.stem
                        })
            else:
                print(f"Warning: No 'questions' field found in {json_file}")
                
        except json.JSONDecodeError as e:
            print(f"Error: Unable to parse {json_file}: {e}")
        except Exception as e:
            print(f"Error: Error reading {json_file}: {e}")
    
    print(f"Loaded {len(all_questions)} questions in total")
    return all_questions


def generate_txt_files(all_questions, output_dir):
    """Generate three txt files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = output_dir / "questions.txt"
    answers_file = output_dir / "answers.txt"
    qa_file = output_dir / "questions_and_answers.txt"
    
    with open(questions_file, 'w', encoding='utf-8') as fq, \
         open(answers_file, 'w', encoding='utf-8') as fa, \
         open(qa_file, 'w', encoding='utf-8') as fqa:
        
        for idx, item in enumerate(all_questions, start=1):
            question = item["question"]
            answer = item["answer"]
            
            # Write to questions file
            fq.write(f"{idx}. {question}\n\n")
            
            # Write to answers file
            fa.write(f"{idx}. {answer}\n\n")
            
            # Write to questions+answers file
            fqa.write(f"{idx}. {question}\n")
            fqa.write(f"A: {answer}\n\n")
    
    print(f"\nGenerated files:")
    print(f"  - {questions_file}")
    print(f"  - {answers_file}")
    print(f"  - {qa_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate txt files from JSON files')
    parser.add_argument(
        '--questions-dir',
        type=str,
        default='questions',
        help='Directory containing JSON files (default: questions)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='questions_txt',
        help='Output directory for txt files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Load all questions
    all_questions = load_all_questions(args.questions_dir)
    
    if not all_questions:
        print("Error: No questions loaded")
        return
    
    # Generate txt files
    generate_txt_files(all_questions, args.output_dir)
    
    print(f"\nComplete! Processed {len(all_questions)} questions in total")


if __name__ == '__main__':
    main()

