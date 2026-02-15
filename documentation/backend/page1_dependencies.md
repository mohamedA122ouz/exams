# How will dependencies works in the application (classRoom_attachment)?

1. first I will use the following class
```ts
type dependenciesRepo = {
    dependentTable:string; // main table like Attachment
    dependOnTable:string;  // main table depend on this table like exams
    field_value:any; // {ID:<VALUE-ID>,value:} 
}
```

`dependentTable`: is the table that allow to use this dependency rule
`dependOnTable`: is the table that the main or dependent table depend on
`field_value`:will contain a json with the key and the value of the depend on table have like the ID of the table and say the `degree`

the point of the repo is to create a signature of the dependencies to allow checking the values in the AttachmentDependencies and avoid illegal usage

- Giving an example to this:

> having an attachment which need first to pass an exam and get score = 60
> then the value should be like this

```json
{
    "dependentTable":"ClassRoomAttachment",
    "dependOnTable":"Exam",
    "allowed_fields":["ID","TotalMark","Title","CreatedAt","Subject","Duration_min","EndAt"]
},
{
    "dependentTable":"ClassRoomAttachment",
    "dependOnTable":"WatchHistory",
    "allowed_fields":["attachment"]
}
```

now inside `AttachmentDependencies` I can easily do the following

```ts
const jsonDep = [
    {
        dependentTable:"ClassRoomAttachment",
        dependOnTable:"Exam",
        "field_value":{
            "ID":10,
            "TotalMark":69.8,
            "Title":"test123"
        }
    },
    {
        dependentTable:"ClassRoomAttachment",
        dependOnTable:"Exam",
        "field_value":{
            "ID":10,
            "TotalMark":69.8,
            "Title":"test123"
        }
    }
]
```
