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

|what happen|status|json|
|---|---|---|
|success|`200`|{"login": "successfully done"}|
|wrong field|`400`|{"login": "username/password is wrong"}|
|server error|`500`|{"fail": "username/password is wrong"}|

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
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"signup success"}` |
| wrong field   | `400`  | `{"username":"is already exist"}` <br> `{"email":"is Null","lastname":"is Null","firstname":"is Null","password2":"is different the entered password"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |


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
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `[{"ID": 1,"Name": "term1","Year_id": 1,"User_id":1}]` |
| wrong field   | `400`  | `{"year_id":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |


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
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"term created successfully"}` |
| wrong field   | `400`  | `{"name":"cannot be null"}` <br> `{"year_id":"cannot be null"}` (only one returned at a time) |
| server error  | `500`  | `{"fail":"something went wrong"}` |

---

### show years

- Method:`GET`, endpoint:`/api/v0/years`
- Params: -

---

### create year

- Method:`POST`, endpoint:`/api/v0/years/create`
- Params: `name:string`
- Request Example:

```json
{
    "name":"year1"
}
```

- Response Details
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"year created successfully"}` |
| wrong field   | `400`  | `{"name":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |

---

### create subject

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
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"subject created successfully"}` |
| wrong field   | `400`  | `{"year_id":"cannot be null"}` <br> `{"term_id":"cannot be null"}` <br> `{"name":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |

---

### show subjects

- Method:`GET`, endpoint:`/api/v0/subjects`
- Params: -

- Response Details
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"subjects retrieved successfully"}` |
| wrong field   | `400`  | none → `None` |
| server error  | `500`  | `{"fail":"something went wrong"}` |

---

### show lectures

- Method:`GET`, endpoint:`/api/v0/lectures`
- Params: `subject_id:string`
- Request Example: `/api/v0/lectures?subject_id=1`

- Response Details
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"lectures retrieved successfully"}` |
| wrong field   | `400`  | `{"subject_id":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |

---

### create lectures

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
| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"lecture created successfully"}` |
| wrong field   | `400`  | `{"name":"cannot be null"}` <br> `{"subject_id":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |


---

### show questions

- Method:`GET`, endpoint:`/api/v0/questions`
- Params: `lecture:string`
- Request Example: `/api/v0/questions?lecture=1`

| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"questions retrieved successfully"}` |
| wrong field   | `400`  | `{"lecture":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |


---

### create question

- Method:`POST`, endpoint:`/api/v0/question/create`
- Params: `text_url:string`, `type:string|number`, `ans:string`, `lecture_id:string`
- Request Example:

```json
{
    "text_url":"How are you?",
    "type":"1",//could be "0","1","2"
    "ans":"fine Thank you",
    "lecture_id":"1"
}
```


| what happen   | status | json |
|---------------|--------|------|
| success       | `200`  | `{"success":"question created successfully"}` |
| wrong field   | `400`  | `{"text_url":"cannot be null"}` <br> `{"type":"cannot be null"}` <br> `{"ans":"cannot be null"}` <br> `{"lecture_id":"cannot be null"}` |
| server error  | `500`  | `{"fail":"something went wrong"}` |


---

### create questions

- Method:`POST`, endpoint:`/api/v0/questions/create`

---
