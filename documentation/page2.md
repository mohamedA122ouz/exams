# **Question Parser Specification – Full Technical Documentation**

**Version:** 1.0  
**Author:** Mohamed  
**Purpose:** Define the standard syntax, escape rules, attachment structure, and parsing workflow for a flexible question-representation format used in exams, tests, and AI-assisted generation.

---

# **1. Introduction**

This document describes the syntax and rules for the **Custom Question Markup Language (CQML)**, a compact but expressive format for defining:

* Questions and sub-questions
* Attachments (images, audio, video, URLs)
* Multiple-choice options
* Answer definitions
* Orientation and layout rules
* Escape sequences to prevent syntax conflicts

CQML allows users to create highly flexible question structures using a lightweight text grammar.
This grammar is designed to be parsed by a deterministic parser that converts CQML into an HTML TEXT.

---

# **2. Core Concepts**

CQML uses a combination of:

* **Tilde separators (`~`)**
* **Attachment tokens (`<TYPE>@<VALUE>`)**
* **Choice tokens (`CHOICE@<VALUE>`)**
* **Escape sequences (`#@`, `#~`)**

This creates a compact, safe, and predictable grammar.

---

# **3. Syntax Overview**

### **3.1 Question Structure**

A question may consist of multiple sequential segments:

```
<segment> ~ <segment> ~ <segment> ...
```

Each segment may be:

* A text block
* An attachment (`IMAGE@…`, `AUDIO@…`, etc.)
* Another question part

Example:

```
What do you see?
~IMAGE@https://example.com/cat.png
~Describe it in one sentence.
```

---

# **4. Attachments**

Attachments follow the format:

```
<TYPE>@<VALUE>
```

### **Supported Attachment Types**

| <TYPE>    | Meaning                             | Example                            |
| ------- | ----------------------------------- | ---------------------------------- |
| `IMAGE` | Image file / URL                    | `IMAGE@https://img.com/a.png`      |
| `AUDIO` | Audio clip                          | `AUDIO@https://site.com/sound.mp3` |
| `VIDEO` | Video file / link                   | `VIDEO@https://site.com/video.mp4` |
| `URL`   | External link (YouTube, docs, etc.) | `URL@https://youtube.com/x`        |

### **4.1 Attachment Orientation**

CQML allows questions and attachments to be arranged flexibly:

#### **Attachment after question**

```
What is shown in this image?
~IMAGE@https://hips.hearstapps.com/hmg-prod/images/sacred-birma-cat-in-interior-royalty-free-image-1718202855.jpg?crop=0.672xw:1.00xh;0.163xw,0
~
Explain.
```

#### **Attachment before question**

```
IMAGE@https://hips.hearstapps.com/hmg-prod/images/sacred-birma-cat-in-interior-royalty-free-image-1718202855.jpg?crop=0.672xw:1.00xh;0.163xw,0
~What is shown in this image?
```

#### **Multiple attachments**

```
Look at the following:
~IMAGE@url1
~IMAGE@url2
~VIDEO@url3
~What do these represent?
```

---

# **5. Multiple-Choice Questions**

### **5.1 Choice Syntax**

Each choice is written as:

```
CHOICE@<TEXT>
```

Example:

```
CHOICE@Red
CHOICE@Blue
CHOICE@Green
```

### **5.2 Answer Syntax**

The correct option is marked using:

```
ANSWER@<choice-text>
```

Example:

```
ANSWER@Blue
```

### **5.3 Full MCQ Example**

```
What is the capital of Japan?
CHOICE@Tokyo
CHOICE@Osaka
CHOICE@Kyoto
ANSWER@Tokyo
```

### **5.4 Parser Validation Rules**

1. The answer **must match** one of the CHOICE@ entries.
2. Choices must be collected **in order of appearance**.
3. Only one ANSWER@ entry is permitted.
4. Additional text after ANSWER@ is optional but ignored.

### **5.5 Using MCQ Inside Multi-Segment Questions**

```
Look at the image:
~IMAGE@https://site.com/japan.png
~Which city is this?
CHOICE@Tokyo
CHOICE@Nagoya
CHOICE@Fukuoka
ANSWER@Tokyo
```

---

# **6. Escape Sequence Rules**

CQML uses symbols like `~` and `@` for syntax.
To allow these characters to appear as normal text, they must be escaped.

### **6.1 Escape Sequences**

| Literal Needed | CQML Input | Meaning         |
| -------------- | ---------- | --------------- |
| `~`            | `#~`       | Literal tilde   |
| `@`            | `#@`       | Literal at-sign |

### **6.2 Why Escaping is Required?**

The parser treats:

* `~` as a separator
* `@` as an attachment/choice operator

So they must be escaped when used in normal text.

### **6.3 Escape Algorithm**

**Step 1 – Generate Random Unique Tokens**

Example:

```
TILDA_RNG = "78$451%88"
AT_RNG    = "93!aa12&7"
```

**Step 2 – Preprocess input**

* Replace all `#~` with `78$451%88`
* Replace all `#@` with `93!aa12&7`

**Step 3 – Parse normally**

* Interpret true `~` separators
* Interpret `@` in tokens like `IMAGE@…`, `CHOICE@…`

**Step 4 – Restore escaped characters**

* Replace `78$451%88` with `~`
* Replace `93!aa12&7` with `@`

This ensures no collision between syntax and literal characters.

---

# **7. Full Example With Escaping, Attachments, Choices**

### **CQML Input**

```
hello#~ are you there?
~IMAGE@https://test.com/image.jpg
~what is the name of this sign '#@' ?
CHOICE@One
CHOICE@Two
CHOICE@Three
ANSWER@One
```

### **Final Parsed JSON**

```json
{
  "question": "hello~ are you there?",
  "attachments": [
    { "type": "IMAGE", "value": "https://test.com/image.jpg" }
  ],
  "continuation": "what is the name of this sign '@' ?",
  "choices": ["One", "Two", "Three"],
  "answer": "One"
}
```

---

# **8. Multi-Part Complex Example**

### **CQML Input**

```
You will see a video and answer the following:
~VIDEO@https://example.com/vid.mp4
~Describe what the speaker is doing.
~Now choose the correct action.
CHOICE@Running
CHOICE@Walking
CHOICE@Jumping
ANSWER@Walking
```

### **Parsed Structure**

```json
{
  "segments": [
    "You will see a video and answer the following:",
    { "type": "VIDEO", "value": "https://example.com/vid.mp4" },
    "Describe what the speaker is doing.",
    "Now choose the correct action."
  ],
  "choices": ["Running", "Walking", "Jumping"],
  "answer": "Walking"
}
```

---

# **9. Error Handling Rules**

The parser must throw descriptive errors:

| Error                     | Condition                                         |
| ------------------------- | ------------------------------------------------- |
| `MissingANSWER`           | No `ANSWER@` found for MCQ                        |
| `InvalidAnswerReference`  | `ANSWER@text` does not match any `CHOICE@`        |
| `MalformedAttachment`     | A segment contains `TYPE@` with missing value     |
| `UnknownType`             | Attachment uses undefined type                    |
| `UnescapedReservedSymbol` | Literal `@` or `~` found in text without escaping |

---

# **10. Recommended Parser Output Structure**

The standard output should be:

```json
{
  "question": "string",
  "segments": [ ... ],
  "attachments": [ { "type": "...", "value": "..." } ],
  "choices": [ "...", "...", ... ],
  "answer": "string"
}
```

Or more compact:

```json
{
  "type": "question",
  "parts": [...],
  "choices": [...],
  "answer": "..."
}
```

---

# **11. Future Extensions (Optional)**

* **Randomized choice ordering**
* **Grouped attachments**
* **Weighted choices**
* **Timed question elements**
* **Nested questions inside questions**
* **AI-assisted distractor generation**
* **Styling markup (bold/italic)**

