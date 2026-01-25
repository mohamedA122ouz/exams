# 📘 Classes API – Create & List ClassRooms Documentation

## Overview

These endpoints manage **ClassRooms** for the authenticated user.

They are used for:

* Class dashboards
* Instructor class management
* Class discovery (if not hidden from search)

There are **two main operations**:

* Create a new ClassRoom
* List existing ClassRooms

---

## Endpoints

### Create ClassRoom

```
POST /classes/create
```

### List ClassRooms

```
GET /classes
```

---

## 1️⃣ Create ClassRoom

### Overview

Creates a **new ClassRoom** owned by the authenticated user.

This endpoint accepts **configuration and payment rules** that control access to the class.

---

### Endpoint

```
POST /classes/create
```

---

### Request Shape

```ts
ClassRoomFromFrontend
```

---

### Request Body Structure

```ts
interface ClassRoomFromFrontend {
  title: string
  HideFromSearch: boolean
  paymentAmount: number
  PaymentExpireInterval_MIN: number
  PaymentAccessMaxCount: number
}
```

---

### Field Semantics

| Field                       | Description                                       |
| --------------------------- | ------------------------------------------------- |
| `title`                     | ClassRoom title                                   |
| `HideFromSearch`            | If `true`, class will not appear in public search |
| `paymentAmount`             | Required payment amount to access the class       |
| `PaymentExpireInterval_MIN` | Payment validity duration in **minutes**          |
| `PaymentAccessMaxCount`     | Maximum allowed accesses per payment              |

---

### Validation Rules

* `paymentAmount` must be `>= 0`
* `PaymentExpireInterval_MIN` must be `> 0`
* `PaymentAccessMaxCount` must be `>= 1`
* All fields are **required**

---

### Example Request

```json
{
  "title": "Algorithms 101",
  "HideFromSearch": false,
  "paymentAmount": 150,
  "PaymentExpireInterval_MIN": 1440,
  "PaymentAccessMaxCount": 3
}
```

---

### Response

Returns a **ClassRoom object** or a standardized API response via `ResponseHelper`.

```json
{
  "success": true,
  "data": {
    "ID": 12
  }
}
```

*(Exact response shape depends on `ResponseHelper` implementation)*

---

## 2️⃣ List ClassRooms

### Overview

Returns a **list of ClassRooms** accessible to the authenticated user.

Used for:

* Instructor dashboards
* Class selection screens
* Class management pages

---

### Endpoint

```
GET /classes
```

---

### Response Shape

```ts
{
  list: ClassRoomSummary[]
}
```

---

### ClassRoom Object Structure

```ts
interface ClassRoomSummary {
  ID: number
  Title: string
  Owner_id: number
  HideFromSearch: boolean
  PaymentAmount: number
  PaymentExpireInterval_MIN: number
  PaymentAccessMaxCount: number
  CreatedAt: string   // ISO 8601
}
```

---

### Field Semantics

| Field                       | Description                  |
| --------------------------- | ---------------------------- |
| `ID`                        | Unique ClassRoom identifier  |
| `Title`                     | ClassRoom title              |
| `Owner_id`                  | Class owner (creator)        |
| `HideFromSearch`            | Visibility in public search  |
| `PaymentAmount`             | Required payment amount      |
| `PaymentExpireInterval_MIN` | Payment validity in minutes  |
| `PaymentAccessMaxCount`     | Max access count per payment |
| `CreatedAt`                 | Creation timestamp           |

---

### Time Fields Rules

| Field       | Behavior       |
| ----------- | -------------- |
| `CreatedAt` | Always present |

All dates follow **ISO 8601** format (UTC).

---

### Example Response

```json
{
  "list": [
    {
      "ID": 5,
      "Title": "Math Basics",
      "Owner_id": 1,
      "HideFromSearch": false,
      "PaymentAmount": 100,
      "PaymentExpireInterval_MIN": 60,
      "PaymentAccessMaxCount": 2,
      "CreatedAt": "2026-01-20T10:15:30.000Z"
    },
    {
      "ID": 6,
      "Title": "Advanced Physics",
      "Owner_id": 1,
      "HideFromSearch": true,
      "PaymentAmount": 200,
      "PaymentExpireInterval_MIN": 1440,
      "PaymentAccessMaxCount": 5,
      "CreatedAt": "2026-01-22T08:42:10.000Z"
    }
  ]
}
```

---

## ✅ Frontend Usage Rules

* Use `ID` for navigation to class details
* Handle hidden classes (`HideFromSearch`) properly
* Treat all date fields as **UTC ISO strings**
* Do not assume public visibility unless explicitly allowed

---

## 🔗 Endpoint Relationship Summary

| Endpoint          | Purpose                |
| ----------------- | ---------------------- |
| `/classes/create` | Create a new ClassRoom |
| `/classes`        | List ClassRooms        |
