# Question Payload – Frontend Documentation

This document describes the structure, rules, and expected behavior of the **Question object sent from the frontend** to the backend.

The payload is used for:

* Creating questions in the **Question Bank**
* Creating questions inside an **Exam**

---

## 1. Question Object Structure

```ts
QuestionFromFront {
  answers: string
  question: string
  questionType: number
  ease: number
  choices?: string[] | null
  attachments?: Attachments[] | null
  lecture_id: number
  sectionName?: string | null
}
```

---

## 2. Field-by-Field Explanation

### 2.1 `question` (string) ✅ **Most Important**

The question text **supports a very simple templating language** to reference attachments.

#### Attachment Reference Syntax

* `$<index>` → refers to an attachment by its index
* Indexing starts from **0**

Example:

```txt
What is shown in the image $0 ?
```

This means:

* `$0` → first attachment
* `$1` → second attachment, etc.

#### Escaping `$`

If you want to **use `$` as a literal character** and NOT as an attachment reference:

* Use `#$`

Example:

```txt
The price is #$100
```

Backend interpretation:

```txt
The price is $100
```

⚠️ **Important Rules**

* `$` is only special inside `question`
* `#$` escapes `$`
* Any `$<number>` that doesn’t match an attachment index may cause validation errors

---

### 2.2 `attachments` (optional)

```ts
attachments?: Attachments[] | null
```

* Can be `null` if the question has no attachments
* Attachment order matters → it must match `$index` references in `question`
* Example:

```ts
attachments = [image1, image2]
```

Then:

* `$0` → image1
* `$1` → image2

---

### 2.3 `questionType` (number)

```ts
enum QuestionType {
  MCQ_ONE_ANS = 0,
  MCQ_MORE_ANS = 1,
  WRITTEN_QUETION = 2,
  COMPLEX = 3
}
```

| Type | Meaning                                  |
| ---- | ---------------------------------------- |
| `0`  | MCQ – one correct answer                 |
| `1`  | MCQ – multiple correct answers           |
| `2`  | Written (text answer)                    |
| `3`  | Complex (open-ended / custom evaluation) |

---

### 2.4 `choices` (optional)

```ts
choices?: string[] | null
```

| Question Type | Choices Required |
| ------------- | ---------------- |
| MCQ_ONE_ANS   | ✅ Yes            |
| MCQ_MORE_ANS  | ✅ Yes            |
| WRITTEN       | ❌ No (`null`)    |
| COMPLEX       | ❌ No (`null`)    |

Example:

```ts
choices = ["A", "B", "C", "D"]
```

---

### 2.5 `answers` (string)

The `answers` field is **always a string** to support all question types.

#### MCQ – One Answer

* String representing **choice index**

Example:

```txt
"2"
```

→ Correct answer is `choices[2]`

#### MCQ – Multiple Answers

* Comma-separated indices

Example:

```txt
"0,2,3"
```

→ Correct answers: `choices[0]`, `choices[2]`, `choices[3]`

#### Written / Complex Questions

* The **expected correct text**

Example:

```txt
"Newton's Second Law"
```

⚠️ **Do not send arrays or numbers** — backend expects a string.

---

### 2.6 `ease` (number)

```ts
enum QuestionEase {
  EASY = 0,
  MEDIUM = 1,
  HARD = 2
}
```

| Value | Meaning |
| ----- | ------- |
| `0`   | Easy    |
| `1`   | Medium  |
| `2`   | Hard    |

---

### 2.7 `lecture_id` (number)

* Identifies **which lecture this question belongs to**
* Required for:

  * Question Bank
  * Exams
* Used for categorization, filtering, and analytics

---

### 2.8 `sectionName` (optional)

```ts
sectionName?: string | null
```

#### Purpose

* Used **only for exam questions**
* Groups questions under a section title

Example:

```txt
"Choose the correct answer"
```

#### Rules

* **Question Bank** → `null`
* **Exam Question** → string

---

## 3. Common Use Cases

### 3.1 Question Bank (No Exam)

```json
{
  "question": "What is 2 + 2?",
  "questionType": 0,
  "choices": ["3", "4", "5"],
  "answers": "1",
  "ease": 0,
  "attachments": null,
  "lecture_id": 5,
  "sectionName": null
}
```

---

### 3.2 Exam Question with Section

```json
{
  "question": "Refer to image $0 and answer the question",
  "questionType": 1,
  "choices": ["A", "B", "C"],
  "answers": "0,2",
  "ease": 1,
  "attachments": [/* image */],
  "lecture_id": 3,
  "sectionName": "Multiple Choice Questions"
}
```

---

### 3.3 Written Question with `$` Literal

```json
{
  "question": "The price is #$50",
  "questionType": 2,
  "choices": null,
  "answers": "50",
  "ease": 0,
  "attachments": null,
  "lecture_id": 7,
  "sectionName": null
}
```

---

## 4. Validation Summary (Frontend Checklist)

✅ `$index` matches attachments
✅ Use `#$` to escape `$`
✅ `answers` is always a string
✅ `choices` required only for MCQ
✅ `sectionName` only for exams
✅ `ease` uses enum values
✅ `questionType` matches payload structure
