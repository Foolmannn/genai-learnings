# Pydantic is a data validation and data parsing libraray for python. It ensures that the data you work with is correct, structured, and type - safe
from pydantic import BaseModel,EmailStr

from typing import Optional


# class Student(BaseModel):

#     name: str

# new_student = { 'name':'Suman'}

# student = Student(**new_student)

# print(student)

# print(type(student))

# new_student1 = {'name': 32}

# student1 = Student(**new_student1)

# print(student1)  # this will give error as we have defind the name as string so pydatic throws the error 

# Input should be a valid string [type=string_type, input_value=32, input_type=int] 


# THIS IS WHY PYDATIC IS USED INSTEAD OF JUST TYPEDICT AS IT FORCES TO USE THE PROPER DATAYPE AND FORMAT 


# DEFAULT VALUES    

class Student(BaseModel):

    name: str = 'suman' # default values
    age: Optional[int] = None
    email: EmailStr
new_student = {}

student = Student(**new_student)

print(student.name) # now as the dictation is empty we will get the default values. 

#OPTIONAL VALUES:: 

new_student1 = {'name':'Hari', 'age':22}
# new_student1 = {'name':'Hari', 'age':'22'} # pydantic use type coercing to convert this 22 string to the int as we have defined age as int . 

student1 = Student(**new_student1)
print(new_student1)

new_student2 = {'email':"abcfasdf"}

student2 = Student(**new_student2)

print(new_student2)  # so there are builtin validataion for email and much more 

