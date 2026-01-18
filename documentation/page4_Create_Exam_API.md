# 📘 Create Question API – Frontend Documentation

*(Updated for `QuestionFromFront` model)*

## Overview

This endpoint creates **questions** sent from the frontend and prepares them for **database insertion** or **round-trip back to the frontend**.

The system uses a **custom domain language**, therefore some syntax rules **must be respected**, especially inside the `question` field.

---

## Endpoint

```
POST /api/v0/question/create
```

---

## Triggered Function (Conceptual)

```ts
createQuestion(payload: QuestionFromFront[]): Promise<void>
```

Triggered when the frontend submits one or more questions.

---

## Question Types (Strict Enum)

```ts
enum QuestionType {
  MCQ_ONE_ANS = 0,
  MCQ_MORE_ANS = 1,
  WRITTEN_QUETION = 2,
  COMPLEX = 3
}
```

| Value | Type            | Description                              |
| ----: | --------------- | ---------------------------------------- |
|     0 | MCQ_ONE_ANS     | Single correct answer                    |
|     1 | MCQ_MORE_ANS    | Multiple correct answers                 |
|     2 | WRITTEN_QUETION | Open-ended / written answer              |
|     3 | COMPLEX         | Mixed content (text + attachments logic) |

---

## Attachments System

### Core Rules

* Attachments are **optional**
* Attachments are **ordered**
* `$ATTACHMENT_INDEX` inside `question` refers to the attachment index
* Indexing is **zero-based**
* Attachments are **typed**

---

### Attachment Object

```json
{
  "type": "img | video | audio | youtube",
  "link": "string"
}
```

---

### Supported Attachment Types

| type    | Description  |
| ------- | ------------ |
| img     | Image        |
| video   | Video file   |
| audio   | Audio file   |
| youtube | YouTube link |

---

## Question Object Structure (Final Model)

```ts
interface QuestionFromFront {
  question: string            // may contain $ATTACHMENT_INDEX
  answers: string
  questionType: number | QuestionType
  ease: number
  choices?: string[] | null
  attachments?: Attachment[] | null
  lecture_id: number
  sectionName?: string | null
  degree?: number | null
}
```

---

## Field Rules (Important)

| Field          | Required | Notes                           |
| -------------- | -------- | ------------------------------- |
| `question`     | ✅        | Supports `$ATTACHMENT_INDEX`    |
| `answers`      | ✅        | Format depends on question type |
| `questionType` | ✅        | Enum value or enum reference    |
| `ease`         | ✅        | Difficulty level                |
| `lecture_id`   | ✅        | **Required** (not optional)     |
| `choices`      | ❌        | Required **only for MCQ types** |
| `attachments`  | ❌        | Optional                        |
| `sectionName`  | ❌        | Optional grouping label         |
| `degree`       | ❌        | Question grade / weight         |

---

## Answers Format (By Question Type)

| Question Type   | `answers` format |
| --------------- | ---------------- |
| MCQ_ONE_ANS     | `"0"`            |
| MCQ_MORE_ANS    | `"0,2"`          |
| WRITTEN_QUETION | Free text        |
| COMPLEX         | Depends on logic |

> All MCQ answers use **zero-based indexing**

---

## ⚠️ Special Language Rule – `$` Handling

### `$` Control Symbol

Inside the `question` field, `$` is **reserved**.

* `$ATTACHMENT_INDEX` → attachment placeholder
* Literal `$` **must be escaped**

---

### Escaping Literal `$`

| Input | Result              |
| ----- | ------------------- |
| `$`   | ❌ Parsed as control |
| `#$`  | ✅ Rendered as `$`   |

---

### Scope

* ✅ Applies **only** to `question`
* ❌ Does NOT apply to `answers`, URLs, or attachments

---

### Example

```json
{
  "question": "The price is #$20",
  "questionType": 2,
  "answers": "It costs $20",
  "ease": 1,
  "lecture_id": 5
}
```

---

## Example Request Payload (Aligned)

```json
[
  {
    "sectionName": "MCQ",
    "question": "Which element costs more than #$100?",
    "questionType": 0,
    "answers": "2",
    "ease": 2,
    "choices": [
      "Oxygen",
      "Nitrogen",
      "Helium",
      "Hydrogen"
    ],
    "attachments": [
      {
        "type": "img",
        "link": "https://cdn.example.com/helium.png"
      }
    ],
    "lecture_id": 12,
    "degree": 2
  },
  {
    "sectionName": "COMPLEX",
    "question": "Watch attachment $0 and explain the experiment",
    "questionType": 3,
    "answers": "For every action there is an equal and opposite reaction",
    "ease": 3,
    "attachments": [
      {
        "type": "youtube",
        "link": "https://youtube.com/watch?v=abc123"
      }
    ],
    "lecture_id": 12,
    "degree": 5
  }
]
```

---

## ✅ Frontend Rules Summary (Mandatory)

* Escape `$` as `#$` **only inside `question`**
* Use `$ATTACHMENT_INDEX` to reference attachments
* `lecture_id` is **mandatory**
* `choices` must be `null` for `WRITTEN_QUETION`
* Attachment order matters
* MCQ indexing is **zero-based**
* `degree` represents question weight
