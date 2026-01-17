# 📘 Exam Show API – Questions Output Documentation

*(Based on `QuestionToFront` model)*

## Overview

This endpoint returns the **questions of a specific exam**, prepared for **frontend rendering**.

The returned data:

* Is **already normalized**
* Preserves **attachment indexing**
* May **hide or include answers** depending on exam state

---

## Endpoint

```
GET /api/v0/exam/show?exam_id=EXAMID
```

### Query Parameters

| Name      | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `exam_id` | number | ✅        | Target exam identifier |

---

## Response Type

```ts
list<QuestionToFront>
```

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

| Value | Type            | Description              |
| ----: | --------------- | ------------------------ |
|     0 | MCQ_ONE_ANS     | Single correct answer    |
|     1 | MCQ_MORE_ANS    | Multiple correct answers |
|     2 | WRITTEN_QUETION | Written / open-ended     |
|     3 | COMPLEX         | Mixed content logic      |

---

## Attachments System

### Core Rules

* Attachments are **optional**
* Attachments are **ordered**
* `$ATTACHMENT_INDEX` refers to attachment index
* Indexing is **zero-based**

---

### Attachment Object

```json
{
  "type": "img | video | audio | youtube",
  "link": "string"
}
```

---

## Question Object Structure (Returned)

```ts
interface QuestionToFront {
  question: string
  answers?: string | null
  questionType: number | QuestionType
  ease: number
  choices?: string[] | null
  attachments?: Attachment[] | null
  lecture_id: number
  sectionName?: string | null
}
```

---

## Field Semantics

| Field          | Notes                           |
| -------------- | ------------------------------- |
| `question`     | May contain `$ATTACHMENT_INDEX` |
| `answers`      | Optional (exam-state dependent) |
| `questionType` | Determines rendering logic      |
| `ease`         | Difficulty level                |
| `choices`      | Present **only for MCQ types**  |
| `attachments`  | Media referenced by question    |
| `lecture_id`   | Source lecture                  |
| `sectionName`  | Optional grouping               |

---

## `answers` Visibility Rules

The `answers` field **may be omitted or null**.

| Exam State         | `answers` |
| ------------------ | --------- |
| Before start       | ❌         |
| During exam        | ❌         |
| Review mode        | ✅         |
| Instructor preview | ✅         |

---

## Answers Format (When Present)

| Question Type   | Example       |
| --------------- | ------------- |
| MCQ_ONE_ANS     | `"0"`         |
| MCQ_MORE_ANS    | `"1,3"`       |
| WRITTEN_QUETION | Text          |
| COMPLEX         | Logic-defined |

> MCQ indexing is **zero-based**

---

## ⚠️ Special Language Rule – `$` Handling

### Reserved `$` in `question`

| Syntax | Meaning              |
| ------ | -------------------- |
| `$0`   | Attachment index `0` |
| `#$`   | Literal `$`          |

### Scope

* ✅ Applies **only** inside `question`
* ❌ Not applied to answers or URLs

---

## Example Response

```json
[
  {
    "sectionName": "MCQ",
    "question": "Which element appears in image $0?",
    "questionType": 0,
    "answers": null,
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
    "lecture_id": 12
  },
  {
    "sectionName": "WRITTEN",
    "question": "Explain why the price reached #$100",
    "questionType": 2,
    "answers": null,
    "ease": 3,
    "attachments": [],
    "lecture_id": 12
  }
]
```

---

## ✅ Frontend Rendering Rules (Mandatory)

* Resolve `$ATTACHMENT_INDEX` strictly
* Escape literal `$` using `#$`
* Never assume `answers` exists
* `choices` exist **only for MCQ**
* Preserve attachment order
* MCQ indexing is **zero-based**
