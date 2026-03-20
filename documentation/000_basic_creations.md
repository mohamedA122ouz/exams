# Create Basic Navigations
- ## Create User
- endpoint: `api/user/create`
- body: <<userCredentials:body>> // I am using python approach in url <<int:pk>>
  
  ```ts
  type userCredentials = {
    username:string
    password:string
    password2:string
    email:string
    lastname:string
    firstname:string
  }
  ```
- ### Exmple
  
  ```json
  {
    "username":"Mohamed.Ahmed",
    "password":"Password@123",
    "password2":"Password@123",
    "email":"test@gmail.com",
    "lastname":"Ahmed",
    "firstname":"Mohamed"
  }
  ```
- ## Create Year
- ## Create Term
- ## Create Subject
- ## Create Lectures