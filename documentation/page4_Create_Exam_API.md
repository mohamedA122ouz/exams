# 📘 Create Exam API – Frontend Documentation

## Overview

This endpoint creates a complete exam including **questions**, **attachments**, and **exam settings** in a single request.

The application uses a **custom domain language**, therefore some syntax rules **must be respected** when sending question content.

---

## Endpoint

```
POST /api/v0/question/create
```

---

## Triggered Function (Conceptual)

```ts
createExam(payload: CreateExamPayload): Promise<void>
```

Triggered when the frontend submits the exam creation flow.

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

| Value | Type            | Description                        |
| ----- | --------------- | ---------------------------------- |
| 0     | MCQ_ONE_ANS     | Single correct answer              |
| 1     | MCQ_MORE_ANS    | Multiple correct answers           |
| 2     | WRITTEN_QUETION | Open-ended / written               |
| 3     | COMPLEX         | Mixed content (text + attachments) |

---

## Attachments System

### Core Rules

* Attachments can be added **anywhere inside the exam**
* Attachments are **ordered**
* `$i` represents the **index of the attachment** in the attachments array
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

## Question Object Structure

```ts
interface Question {
  sectionName?: string
  question: string
  answers: string
  questionType: QuestionType
  ease: number
  choices?: string[] | null
  attachments?: Attachment[] | null
  lecture_id?: number | null
}
```

---

## Answers Format (By Question Type)

| Question Type   | answers format            |
| --------------- | ------------------------- |
| MCQ_ONE_ANS     | `"0"`                     |
| MCQ_MORE_ANS    | `"0,2"`                   |
| WRITTEN_QUETION | Text                      |
| COMPLEX         | Depends on question logic |

> Answer values always use **zero-based indexing**.

---

## ⚠️ Special Language Rule – `$` Escaping

### Literal `$` Handling

The application language treats `$` as a **special control symbol**
**ONLY inside the `question` field**.

To write a **literal dollar sign** in a question, it **must be escaped using `#`**.

| Input in `question` | Result               |
| ------------------- | -------------------- |
| `$`                 | ❌ Parsed / Converted |
| `#$`                | ✅ Rendered as `$`    |

### Scope

* ✅ Applies **only** to `question`
* ❌ Does **not** apply to `answers`, attachments, or URLs

### Example

```json
{
  "question": "The price is #$20",
  "questionType": 2,
  "answers": "It costs $20"
}
```

---

## Example Request Payload (With Attachments)

```json
{
  "title": "Physics Final Exam",
  "subject_id": 2,
  "questions": [
    {
      "sectionName": "MCQ",
      "question": "Which of the following elements costs more than #$100?",
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
      "lecture_id": null
    },
    {
      "sectionName": "COMPLEX",
      "question": "Watch the video and explain the experiment",
      "questionType": 3,
      "answers": "For every action, there is an equal and opposite reaction",
      "ease": 3,
      "choices": null,
      "attachments": [
        {
          "type": "youtube",
          "link": "https://youtube.com/watch?v=abc123"
        },
        {
          "type": "audio",
          "link": "https://cdn.example.com/explanation.mp3"
        }
      ],
      "lecture_id": null
    }
  ],
  "settings": {
    "Locations": null,
    "PassKey": "kill",
    "PreventOtherTabs": true,
    "Duration_min": 60,
    "AutoCorrect": true,
    "QuestionByQuestion": false,
    "ShareWith": 0,
    "AllowDownload": false,
    "StartAt": "2026-01-05T09:00:00",
    "EndAt": "2026-01-05T10:00:00"
  }
}
```

---

## Frontend Rules Summary (Mandatory)

* Escape `$` as `#$` **only in `question`**
* `choices` must be `null` for `WRITTEN_QUETION`
* `attachments` can exist on **any question**
* Attachment order matters (`$i`)
* Dates must follow **ISO 8601**
* Indexing is **zero-based**