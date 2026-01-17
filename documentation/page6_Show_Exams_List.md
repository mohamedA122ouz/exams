# 📘 Exams API – Exams List Documentation

## Overview

This endpoint returns a **list of exams metadata** available to the user.

It is used for:

* Exam dashboards
* Exam selection screens
* Instructor / student exam listings

❗ This endpoint **does NOT return questions**
Questions are fetched via:

```
GET /api/v0/exam/show?exam_id=EXAMID
```

---

## Endpoint

```
GET /api/v0/exams
```

---

## Response Shape

```ts
{
  list: ExamSummary[]
}
```

---

## Exam Object Structure

```ts
interface ExamSummary {
  ID: number
  Title: string
  CreatedAt: string          // ISO 8601
  Subject_id: number
  Owner_id: number
  PreventOtherTabs: boolean
  Duration_min: number
  AutoCorrect: boolean
  QuestionByQuestion: boolean
  ShareWith: number
  AllowDownLoad: boolean
  StartAt: string | null     // ISO 8601 or null
  EndAt: string | null       // ISO 8601 or null
}
```

---

## Field Semantics

| Field                | Description                     |
| -------------------- | ------------------------------- |
| `ID`                 | Unique exam identifier          |
| `Title`              | Exam title                      |
| `CreatedAt`          | Exam creation timestamp         |
| `Subject_id`         | Associated subject              |
| `Owner_id`           | Exam creator                    |
| `PreventOtherTabs`   | Tab-switch prevention flag      |
| `Duration_min`       | Exam duration in minutes        |
| `AutoCorrect`        | Enable automatic correction     |
| `QuestionByQuestion` | Sequential question mode        |
| `ShareWith`          | Sharing scope (enum-based)      |
| `AllowDownLoad`      | Allow exam download             |
| `StartAt`            | Scheduled start time (nullable) |
| `EndAt`              | Scheduled end time (nullable)   |

---

## Time Fields Rules

| Field       | Behavior                    |
| ----------- | --------------------------- |
| `CreatedAt` | Always present              |
| `StartAt`   | `null` → no scheduled start |
| `EndAt`     | `null` → no scheduled end   |

All dates follow **ISO 8601** format.

---

## Example Response

```json
{
  "list": [
    {
      "Title": "English Exam1",
      "ID": 9,
      "CreatedAt": "2026-01-13T05:51:57.363Z",
      "Subject_id": 1,
      "Owner_id": 1,
      "PreventOtherTabs": true,
      "Duration_min": 60,
      "AutoCorrect": true,
      "QuestionByQuestion": false,
      "ShareWith": 0,
      "AllowDownLoad": false,
      "StartAt": null,
      "EndAt": null
    },
    {
      "Title": "fda",
      "ID": 10,
      "CreatedAt": "2026-01-17T15:03:47.412Z",
      "Subject_id": 1,
      "Owner_id": 1,
      "PreventOtherTabs": true,
      "Duration_min": 60,
      "AutoCorrect": true,
      "QuestionByQuestion": false,
      "ShareWith": 0,
      "AllowDownLoad": true,
      "StartAt": "2026-01-17T13:00:00Z",
      "EndAt": "2026-01-17T14:00:00Z"
    }
  ]
}
```

---

## ✅ Frontend Usage Rules

* Use `ID` when navigating to:

  ```
  /api/v0/exam/show?exam_id=ID
  ```
* Do **not** expect questions here
* Treat `StartAt` / `EndAt` as optional
* Dates are **UTC ISO strings**
* Rendering logic must handle `null` schedule values

---

## 🔗 Endpoint Relationship Summary

| Endpoint                       | Purpose                    |
| ------------------------------ | -------------------------- |
| `/api/v0/exams`                | List exams (metadata only) |
| `/api/v0/exam/show?exam_id=ID` | Fetch exam questions       |
