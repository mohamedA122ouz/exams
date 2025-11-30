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

---

### show subjects

- Method:`GET`, endpoint:`/api/v0/subjects`
- Params: -

---

### show lectures

- Method:`GET`, endpoint:`/api/v0/lectures`
- Params: `subject_id:string`
- Request Example: `/api/v0/lectures?subject_id=1`

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

---

### show questions

- Method:`GET`, endpoint:`/api/v0/questions`
- Params: `lecture:string`
- Request Example: `/api/v0/questions?lecture=1`

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

---

### create questions

- Method:`POST`, endpoint:`/api/v0/questions/create`

---
