# **Exam and Question Parser – Technical Documentation**

- [**Exam and Question Parser – Technical Documentation**](#exam-and-question-parser--technical-documentation)
  - [**1. Introduction**](#1-introduction)
  - [**2. Input Format**](#2-input-format)
    - [**2.1 Segment Types**](#21-segment-types)
    - [**2.2 Reserved Characters and Escaping**](#22-reserved-characters-and-escaping)
  - [**3. Examples of Input**](#3-examples-of-input)
    - [**Single-choice MCQ**](#single-choice-mcq)
    - [**Multi-answer MCQ**](#multi-answer-mcq)
    - [**Written question**](#written-question)
  - [**4. Function Behavior**](#4-function-behavior)
    - [**4.1 Parsing Flow**](#41-parsing-flow)
  - [**5. Output Structure**](#5-output-structure)
  - [**6. Multi-choice Rules**](#6-multi-choice-rules)
  - [**7. Attachments**](#7-attachments)
  - [**8. Escaping**](#8-escaping)
  - [**9. Error Handling**](#9-error-handling)
  - [**10. Usage Example**](#10-usage-example)


**Function:** `ExamAndQuestionParser(examText: str) -> list[AnsParserOutput]`  
**Author:** Mohamed  
**Version:** 2.0  
**Purpose:** Converts a text-based exam specification into a structured list of questions, including multiple-choice (single or multi-answer) and written questions, with HTML-ready rendering and answer mapping.  

---

## **1. Introduction**

`ExamAndQuestionParser` is a Python function that parses a custom exam markup language and generates a structured, machine-readable output for each question. It supports:

* Multi-segment questions (text + attachments)
* Multiple-choice questions (single or multi-answer)
* Written/free-text questions
* Embedded attachments (images, audio, video, YouTube links)
* Escaped syntax for reserved characters

This parser is designed for use in backend exam systems, automated grading pipelines, or AI-assisted exam generation.

---

## **2. Input Format**

The parser accepts a single string, `examText`, which contains one or more questions. Each question is separated by a **semicolon (`;`)**, and each segment of a question is separated by a **tilde (`~`)**.

### **2.1 Segment Types**

* **Text segments**: Any text not containing `@` is treated as plain text.
* **Choices**: Use `CHOICE@<option text>`.
* **Answers**: Use `ANS@<index>` (comma-separated for multi-answer MCQs).
* **Attachments**:

  * `IMAGE@<url>`
  * `AUDIO@<url>`
  * `VIDEO@<url>`
  * `YOUTUBE@<url>`

### **2.2 Reserved Characters and Escaping**

To prevent parsing conflicts, reserved symbols can be escaped:

| Literal | Escape Sequence |
| ------- | --------------- |
| `~`     | `#~`            |
| `@`     | `#@`            |
| `;`     | `#;`            |

The parser automatically replaces these sequences internally and restores the original characters in the output.

---

## **3. Examples of Input**

### **Single-choice MCQ**

```text
Hello How are?
~CHOICE@Fine, thank you
~CHOICE@Fine, and how are you
~CHOICE@I don't know life feels complicated these days
~ANS@0;
```

### **Multi-answer MCQ**

```text
Hello world!
~CHOICE@A keyword
~CHOICE@A regular string
~CHOICE@A personal info
~ANS@0,1,2;
```

### **Written question**

```text
How to save people from AI;
ANS@12345678910~write from 1 to 10 like this 1....10 without any separators between numbers
```

---

## **4. Function Behavior**

### **4.1 Parsing Flow**

1. **Split questions** by `;` (semicolon).
2. **Escape processing**: Converts `#~`, `#@`, `#;` into unique temporary tokens.
3. **Split segments** by `~`.
4. **Process segments**:

   * Text → wrapped in `<p>` tags
   * Attachments → converted to HTML `<img>`, `<audio>`, `<video>`, `<iframe>` (for YouTube)
   * Choices → stored in list; `ANS@` processed as multi- or single-choice
5. **Generate HTML** for the question:

   * Multi-choice:

     * Single-answer → `<input type='radio'>`
     * Multi-answer → `<input type='checkbox'>`
   * Written question → `<textarea>`
6. **Restore escaped characters** and semicolons.

---

## **5. Output Structure**

The function returns a **list of `AnsParserOutput` dictionaries**:

```python
class AnsParserOutput(TypedDict):
    answers: str           # Raw answer string from `ANS@`, e.g., "0,2"
    questions: str         # HTML-rendered question including choices or textarea
    questionType: Literal[0, 1, 2]  # MCQ or Written question
```

* **`answers`**: For MCQs, contains index(es) of correct choices. For written questions, contains the expected string/answer.
* **`questions`**: HTML content ready for rendering in a web frontend.
* **`questionType`**:

  * `MCQ` → multiple-choice
  * `WRITTEN_QUESTION` → free-text answer

---

## **6. Multi-choice Rules**

* **ANS@** must come after all `CHOICE@` entries.
* **Multiple answers**: comma-separated indices (e.g., `ANS@0,2`).
* If indices exceed the number of choices or are not numeric, the parser treats the question as **written**.

---

## **7. Attachments**

* Supports images, audio, video, and YouTube URLs.
* Automatically distinguishes between uploaded attachments and external URLs.
* Converts YouTube URLs to embeddable `<iframe>` format.

---

## **8. Escaping**

* `#~` → `~`
* `#@` → `@`
* `#;` → `;`

This allows the use of reserved symbols inside question text or choice text without breaking the parser.

---

## **9. Error Handling**

The parser raises exceptions for:

* `Answer cannot be in the middle of choices it must be at the end`
* Malformed or invalid `ANS@` values (non-numeric indices for MCQ)
* Other invalid segment types or unexpected syntax

---

## **10. Usage Example**

```python
exam_text = """
Hello How are?
~CHOICE@Fine
~CHOICE@Not fine
~ANS@0;
Tell me your favorite programming language
~ANS@Python
"""

parsed_questions = ExamAndQuestionParser(exam_text)

for q in parsed_questions:
    print(q["questions"])
    print("Answer:", q["answers"])
    print("Type:", q["questionType"])
```
