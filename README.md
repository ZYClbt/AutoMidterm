# AutoMidterm

AutoMidterm is an easy but effective tool for automatically generating exam questions from course lecture materials to facilitate efficient exam preparation. It is designed for courses with strong alignment between lecture content and exam coverage, where lecture slides (as PDFs) are available. The system can be easily adapted to different courses by modifying the prompt template. Originally developed for the 2025 Fall Cognitive and Reasoning course at PKU.


## Motivation

Preparing for midterm exams often requires synthesizing large amounts of lecture content into testable questions. AutoMidterm automates this process by leveraging large language models to generate questions and answers directly from lecture PDFs, significantly improving study efficiency. The tool is particularly effective for courses where exam questions closely follow lecture materials, especially when instructors also leverage AI for question generation.


## File Organization

```
AutoMidterm/
├── slices/              # Place your lecture PDF files here
├── questions/           # Generated JSON question files (one per lecture)
├── questions_txt/       # Formatted text outputs
├── generate_question.py # Main script for question generation
├── generate_txt_files.py # Script for organizing questions into text format
└── prompt.txt           # Prompt template (customize for your course)
```

**Note:** Due to copyright restrictions, I cannot provide the original course materials. However, I've included generated questions in the `questions/` folder for reference.


## Environment Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```



## Usage

### Step 1: Prepare Lecture Materials

Place your lecture PDF files in the `slices/` directory. Each PDF will be processed independently.

### Step 2: Generate Questions

Run `scripts/generate_question.py` to generate questions from all PDFs in the `slices/` directory:

```bash
python scripts/generate_question.py --num-questions <num> --model <model_type>
```

**Key Parameters:**

- `--num-questions`: Number of questions to generate per lecture (default: 20)
- `--model`: Model to use (`gpt-5`, `gpt-4o`, `gpt-4-turbo`, `gpt-4o-mini`)
- `--slices-dir`: Directory containing PDF files (default: `slices`)
- `--output-dir`: Output directory for JSON files (default: `questions`)
- `--lecture`: Process only a specific lecture file
- `--prompt-file`: Custom prompt template (default: `prompt.txt`)

Questions are saved as JSON files in the `questions/` directory, with one file per lecture.

### Step 3: Organize Questions into Text Format

Run `scripts/generate_txt_files.py` to organize all questions into readable text files:

```bash
python scripts/generate_txt_files.py --questions-dir <questions_dir> --output-dir <questions_txt_save_dir>
```

This generates three files:

- `questions.txt`: Questions only (numbered)
- `answers.txt`: Answers only (numbered)
- `questions_and_answers.txt`: Questions and answers paired together

**Parameters:**

- `--questions-dir`: Directory containing JSON question files (default: `questions`)
- `--output-dir`: Output directory for text files (default: `questions_txt`)


## Customization

To adapt AutoMidterm for a different course, modify `prompt.txt` to reflect the course-specific requirements, question styles, and answer formats. The prompt template uses `{num_questions}` as a placeholder for the number of questions to generate.
