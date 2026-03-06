# How to verify allowed dependencies?

1. Allowed dependencies will be inserted in a different table called `dependenciesRepo` here will insert the basic info needed to verify the dependencies cheching if it is valid or not
2. the main dependencies will saved into a `AttachmentDependencies` table itself which is connected to the `ClassRoomAttachment` table
3. the `AttachmentDependencies` will have a field called `jsonDep` which will include all the details needed to verify

## Example

### Django model definition for `dependenciesRepo`

```py
class dependenciesRepo(models.Model): 
    dependentTable = models.TextField()
    dependOnTable = models.TextField() 
    allowedFields = models.JSONField()
#---------------
```

- definition in TypeScript

```ts
interface dependenciesRepo{
    dependentTable:string;
    dependOnTable:string;
    allowedFields:string[];
}
```

- definition example

```json
[
    {
        "dependentTable":"ClassRoomAttachment",
        "dependOnTable":"Exam",
        "allowedFields":["ID","TotalMark","Title","CreatedAt","Subject","Duration_min","EndAt"]
    },
    {
        "dependentTable":"ClassRoomAttachment",
        "dependOnTable":"WatchHistory",
        "allowedFields":["attachment"]
    }
]
```

### Django model definition `AttachmentDependencies`

```py
class AttachmentDependencies(models.Model):
    ID = models.AutoField(primary_key=True)
    jsonDep = models.JSONField()
    attachment = models.ForeignKey(ClassRoomAttachment,on_delete=models.CASCADE,related_name='dependencies')
#---------------
```

```ts
interface AttachmentDependencies{
    ID:number;
    jsonDep:any; // Will mention the structure of the data in upcoming details
    attachment:number;
}
```

#### What is the structure of jsonDep

it should be look like the following exmple

```json
{
        "dependOnTable":"Exam",
        "conditionsOnFields":{
            "ID":1,
            "TotalMark__gte":60
        }
}
```

so I will depend on the same logic as the python ORM cause it is more than enough, but at the same time I wll never give it to python to handle it avoiding code injection from frontend espcially because this part user will be able to play with to get the customized effect he/she needed, althought that we will give a layer of frontend protection but you know no frontend is safe so backend validation is much important than this in terms of what should I do.

#### What are the method needed in this part??

I guess this part is only need a comparing logical operation like 
`>` , `<` , `<=` , `>=`  

`gt`, `lt`, `lte`, `gte`

- some functions like:
    `in` , `contains` , and the reverse so I guess `not` must be exist

