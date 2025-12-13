# Exam API v0 documentation

## available endpoints

- Method:`POST`, endpoint:`/api/v0/login`
- Method:`POST`, endpoint:`/api/v0/user/create`
- Method:`GET`, endpoint:`/api/v0/logout/`
- Method:`GET`, endpoint:`/api/v0/terms`
- Method:`POST`, endpoint:`/api/v0/terms/create`
- Method:`GET`, endpoint:`/api/v0/years`
- Method:`POST`, endpoint:`/api/v0/years/create`
- Method:`POST`, endpoint:`/api/v0/subjects/create`
- Method:`GET`, endpoint:`/api/v0/subjects`
- Method:`GET`, endpoint:`/api/v0/lectures`
- Method:`POST`, endpoint:`/api/v0/lectures/create`
- Method:`GET`, endpoint:`/api/v0/questions`
- Method:`POST`, endpoint:`/api/v0/question/create`
- Method:`POST`, endpoint:`/api/v0/questions/create`

## Detailed Method clearification

### Response Logic

if user status `200` then the action is done successfully while if the status is `400` then some field is entered wrongly in frontend or not even provided and the server will return them as a key of the json and specify the error while `500` is faild to finish the action and it is an exception need to be traced in most cases `backend bug`

### login

- Method:`POST`, endpoint:`/api/v0/login`
- Params: `username:string`, `password:string`
- Request Example:

```json
{
    "username":"Mohamed.IT",
    "password":"Password123"
}
```

- Response Example:

| what happen  | status | json                                    |
| ------------ | ------ | --------------------------------------- |
| success      | `200`  | {"login": "successfully done"}          |
| wrong field  | `400`  | {"login": "username/password is wrong"} |
| server error | `500`  | {"fail": "username/password is wrong"}  |

---

### sign-up

- Method:`POST`, endpoint:`/api/v0/user/create`
- Params: `username:string`, `password:string`, `password2:string`, `email:string`, `lastname:string`, `firstname:string`
- Request Example

```json
{
    "username":"Mohamed.IT",
    "password":"Password123",
    "password2":"Password123",
    "email":"test@domainName.topDomain",
    "firstname":"Mohamed",
    "lastname":"Ahmed"
}
```

- Response Details

| what happen  | status | json                                                                                                                                                    |
| ------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| success      | `200`  | `{"success":"signup success"}`                                                                                                                          |
| wrong field  | `400`  | `{"username":"is already exist"}` <br> `{"email":"is Null","lastname":"is Null","firstname":"is Null","password2":"is different the entered password"}` |
| server error | `500`  | `{"fail":"something went wrong"}`                                                                                                                       |


> Notice username could be anything but it must be unique according to the users in the database

---

### logout

- Method:`GET`, endpoint:`/api/v0/logout/`
- Params: -

---

### show terms

- Method:`GET`, endpoint:`/api/v0/terms`
- Params: `year_id:string|number`
- Request Example: `/api/v0/terms?year_id=1`

- Response Details

| what happen  | status | json                              |
| ------------ | ------ | --------------------------------- |
| wrong field  | `400`  | `{"year_id":"cannot be null"}`    |
| server error | `500`  | `{"fail":"something went wrong"}` |

```json
//success reponse | STATUS 200
[
    {
        "ID": 1,
        "Name": "term1",
        "Year_id": 1,
        "User_id": 1
    }
]

```

---

## create term

- Method:`POST`, endpoint:`/api/v0/terms/create`
- Params: `name:string`, `year_id:string|number`
- Request Example:

```json
{
    "name":"term1",
    "year_id":"1"
}
OR
{
    "name":"term1",
    "year_id":1
}
```

- Response Details

| what happen  | status | json                                                                                                                                              |
| ------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| wrong field  | `400`  | `{"name":"term name cannot be null"}` <br> `{"name":"year ID cannot be null"}` <br> `{"name":"year doesn't exist"}` (only one returned at a time) |
| server error | `500`  | `{"fail":"term creation faild"}`                                                                                                                  |

---

## show years

- Method:`GET`, endpoint:`/api/v0/years`
- Params: -

```json
//success response | STATUS:200
[
    {
        "ID": 1,
        "Name": "Year1",
        "User_id": 1
    }
]
```

---

## create year

- Method:`POST`, endpoint:`/api/v0/years/create`
- Params: `name:string`
- Request Example:

```json
{
    "name":"year1"
}
```

- Response Details

| what happen  | status | json                                                                                     |
| ------------ | ------ | ---------------------------------------------------------------------------------------- |
| wrong field  | `400`  | `{"name":"cannot be null"}` <br> `{"name":"cannot create two years with the same name"}` |
| server error | `500`  | `{"fail":"created faild"}`                                                               |

---

## create subject

- Method:`POST`, endpoint:`/api/v0/subjects/create`
- Params: `year_id:string|number`, `term_id:string|number`,`name:string`
- Request Example:

```json
{
    "year_id":1, //could be "1"
    "term_id":1, //could be "1"
    "name":"subject1"
}
```

- Response Details

| what happen  | status | json                                                                                                                                                                                                                   |
| ------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| server error | `200`  | `{"success":"subject created"}`                                                                                                                                                                                        |
| wrong field  | `400`  | `{"term_id":"term Id cannot be null"}` <br> `{"year_id":"cannot year ID be null"}` <br> `{"name":"cannot give null name"}` <br> `{"creation":"faild term is not exist"}` <br> `{"creation":"faild year is not exist"}` |
| server error | `500`  | `{"fail":"faild no reason specified"}`                                                                                                                                                                                 |

---

## show subjects

- Method:`GET`, endpoint:`/api/v0/subjects`
- Params: -

- Response Details

| what happen  | status | json                              |
| ------------ | ------ | --------------------------------- |
| wrong field  | `400`  | none → `None`                     |
| server error | `500`  | `{"fail":"something went wrong"}` |

```json
//success reponse | STATUS 200
[
    {
        "ID": 1,
        "Name": "advanced OOP 1",
        "User_id": 1,
        "Term_id": 1,
        "Year_id": 1
    },
    {
        "ID": 2,
        "Name": "advanced OOP 2",
        "User_id": 1,
        "Term_id": 1,
        "Year_id": 1
    }
]
```

---

## show lectures

- Method:`GET`, endpoint:`/api/v0/lectures`
- Params: `subject_id:string`
- Request Example: `/api/v0/lectures?subject_id=1`

- Response Details

| what happen  | status | json                              |
| ------------ | ------ | --------------------------------- |
| wrong field  | `400`  | `{"subject_id":"cannot be null"}` |
| server error | `500`  | `{"fail":"something went wrong"}` |

```json
//success reponse | STATUS 200
[
    {
        "ID": 1,
        "Name": "lec1",
        "Subject_id": 1,
        "User_id": 1
    }
]
```

---

## create lectures

- Method:`POST`, endpoint:`/api/v0/lectures/create`
- Params: `name:string`, `subject_id:string|number`
- Request Example:

```json
{
    "name":"lecture1",
    "subject_id":1// could be "1"
}
```

- Response Details

| what happen  | status | json                                                                                                                                                                        |
| ------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| success      | `200`  | `{"success":"successful"}`                                                                                                                                                  |
| wrong field  | `400`  | `{"name":"cannot give null name"}` <br> `{"subject_id":"cannot be null"}` <br> `{"subject":"is not found"}` <br> `{"name":"cannot create two lectures with the same name"}` |
| server error | `500`  | `{"fail":"no lecture created"}`                                                                                                                                             |


---

## show questions

- Method:`GET`, endpoint:`/api/v0/questions`
- Params: `lecture:string`
- Request Example: `/api/v0/questions?lecture_id=1`

| what happen  | status | json                              |
| ------------ | ------ | --------------------------------- |
| wrong field  | `400`  | `{"lecture_id":"cannot be null"}` |
| server error | `500`  | `{"fail":"something went wrong"}` |

```json
//success reponse | STATUS 200
[
    {
        "ID": 1,
        "Name": "lec1",
        "Subject_id": 1,
        "User_id": 1
    }
]
```

---

## create question

- Method:`POST`, endpoint:`/api/v0/question/create`
- Params: `text_url:string`, `type:string|number`, `ans:string`, `lecture_id:string`
- Request Example:

```json
{
    "text_url":"How are you?",
    "type":"1",//could be "0","1","2" and below will understand
    "ans":"fine Thank you",
    "lecture_id":"1"
}
```

> MCQ = "0"
> WRITTEN_QUETION = "1"
> COMPLEX = "2"

| what happen  | status | json                                                                                                                                                                                                            |
| ------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| success      | `200`  | `{"success":"creation success"}`                                                                                                                                                                                |
| wrong field  | `400`  | `{"text_url":"cannot be null"}` <br> `{"type":"cannot be null"}` <br> `{"ans":"cannot be null"}` <br> `{"lecture_id":"cannot be null"}` <br> `{"lecture":"lecture not found"}` <br> `{"type":"must be number"}` |
| server error | `500`  | `{"fail":"creation faild"}`                                                                                                                                                                                     |

---

## create questions

Got it! I can rewrite your documentation so that it matches the current endpoint and the new input format. Here’s a cleaned-up and accurate version:

---

## Create Questions

* **Method:** `POST`
* **Endpoint:** `/api/v0/questions/create`

### Request Body

```ts
enum QuestionType {
    MCQ_ONE_ANS = 0,
    MCQ_MORE_ANS = 1,
    WRITTEN_QUESTION = 2,
    COMPLEX = 3,
}
enum Ease {
    EASY = 0,
    MEDIUM = 1,
    HARD = 2,
}
// Question input
interface QuestionInput {
    answers: string;
    question: string;
    questionType: QuestionType;
    ease: Ease;
    choices: string[] | null;
    attachments: null |
        {
            type: "img" | "audio" | "video" | "youtube";
            link: string;
        };
    lecture_id: number;
}

// Request body
interface RequestType {
    editor_input: QuestionInput[];
}

```

```json
//RequestType - 
{
    "editor_input": [
        {
            "answers": "string",
            "question": "string",
            "questionType": 0,
            "ease": 0,
            "choices": ["string1", "string2"],  // or null
            "attachments": {                   // or null
                "type": "img|audio|video|youtube",
                "link": "string"
            },
            "lecture_id": 1
        }
    ]
}
```

* **Field explanations:**

  * `answers` → the correct answer(s) as a string.
  * `question` → the text of the question.
  * `questionType` → integer representing question type (0 to 3).
  * `ease` → integer representing difficulty (0 to 2).
  * `choices` → array of choices for multiple-choice questions or `null`.
  * `attachments` → optional attachment object or `null`. Object has `type` and `link`.
  * `lecture_id` → ID of the lecture the question belongs to.

---

### Responses

| Scenario      | Status | JSON Example |
| ------------- | ------ | -------------|
| Success       | `200`  | `{"success":"questions list created successfully"}` |
| Invalid input | `400`  | `{"editor_input":"cannot be null or empty"}` <br> `{"questionType":"must be 0-3"}` <br> `{"ease":"must be 0-2"}` <br> `{"lecture_id":"cannot be null"}` <br> `{"answers":"cannot be null"}` <br> `{"question":"cannot be null"}` |
| Server error  | `500`  | `{"fail":"questions list failed to be created"}` |

---
