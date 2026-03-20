# 📘 Create Exam API – Input Extension (Continuation)

> **This document is a continuation of the existing “Create Exam API – Frontend Documentation”.**
> All previously documented behavior, rules, syntax, and validations remain **exactly the same**.

This section introduces **an additional way to call the same API endpoint**, allowing more flexible exam construction.

---

## ❗ Important Notice

* ✅ **Same API endpoint**
* ✅ **Same request structure**
* ✅ **Same validation rules**
* ✅ **Same question system**
* ❌ **No breaking changes**

Only the **`questions` input mechanism** has been **extended**, not replaced.

---

## What Has Been Extended

Previously, the exam accepted:

* A list of **manually authored questions**

Now, the **same endpoint** also accepts:

1. **Manually authored questions** (unchanged)
2. **Auto-generated question blocks**
3. **Existing questions referenced by ID**

These can now be **combined together** in **one ordered list**.

---

## Hybrid Input List (New Capability)

The questions list can now be **hybrid**:

* Each item in the array is parsed **independently**
* Items may have **different shapes**
* Order is **preserved exactly**

This is **not** a generic array and **not** type-locked.

---

## Canonical Input Shape (Extension)

```ts
questions: Array<
  | QuestionFromFront
  | ExamAutoGenerator
  | number
>
```

> Each array element is resolved **on its own**, not based on the array type.

---

## How the Backend Interprets Each Item

| Item Shape                            | Meaning                                   |
| ------------------------------------- | ----------------------------------------- |
| `number`                              | Reference to an existing question (by ID) |
| Object containing `generatorSettings` | Auto-generated question block             |
| Object containing `question`          | Manually authored question                |

> The order of elements does **not** affect how types are detected.

---

## Existing Behavior (Unchanged)

All previously documented rules still apply:

* Question types and enums
* Attachments system
* `$` escaping rules
* Answer formats
* Validation constraints
* Settings object
* Date formats
* Zero-based indexing

No changes are required for existing frontend implementations.

---

## Auto Generator Block (New Input Option)

### Definition

```ts
class ExamAutoGenerator {
  generatorSettings: AutoGenExamSetting
  questions: QuestionSelector[]
}
```

### Generator Settings

```ts
class AutoGenExamSetting {
  subjectID: string
  yearID: string
  termID: string
  randomization: boolean
}
```

This block instructs the backend to **generate questions dynamically** and insert them **in place** in the exam order.

---

## Existing Question Reference (New Input Option)

Instead of sending a full question object, the frontend may send:

```ts
[number,string] // [question ID, question Section name] 
```

> for more declearation: [<int:ID>,<str:SectionName>,<float:degree>]

The backend will:

* Fetch the question
* Preserve attachments, answers, and metadata
* Insert it in the same position in the exam

---
shareWith example

* CLASSROOM_DEFAULT = 0
* ANY_ONE_WITH_LINK = 1
* PRIVATE = 2
* CLASSROOM_PUBLIC = 3

## Example: Extended Usage (Same Endpoint)

```json
{
  "questions": [
    [25,"MCQ",5],
    {
      "sectionName": "MCQ",
      "question": "Which item costs more than #$100?",
      "questionType": 0,
      "answers": "2",
      "ease": 2,
      "choices": ["Iron", "Gold", "Silver"]
    },
    {
      "generatorSettings": {
        "subjectID": "2",
        "yearID": "2025",
        "termID": "1",
        "randomization": true
      },
      "questions": [
        { "questionType": 0, "count": 5 }
      ]
    }
  ],
  "settings": {
    "Duration_min": 60
  }
}
```

> ✔ Same endpoint
> ✔ Same payload structure
> ✔ Same rules
> ✔ Additional flexibility

---

## Frontend Guidance (Important)

* Validate **each array element independently**
* Do not assume a single schema for the array
* Do not infer type from the first element
* Mixed usage is fully supported

---

## Final Clarification

> **This extension does not change how the API works — it only adds new, optional input forms that can be used alongside the existing ones.**

Existing integrations continue to work without modification.
