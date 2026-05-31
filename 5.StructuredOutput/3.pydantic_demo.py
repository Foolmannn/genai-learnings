# Pydantic is a data validation and data parsing libraray for python. It ensures that the data you work with is correct, structured, and type - safe
from pydantic import BaseModel,EmailStr,Field

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
    # cgpa:float = Field(gt=0,lt=10)
    cgpa:float = Field(gt=0,lt=10, default=5 , description="A decimal value representing the cgpa of the students") # we can add default parameter too, and custom descriptions tooo this help LLM to be sure and enough knowledge 
new_student = {}

# student = Student(**new_student)

# print(student.name) # now as the dictation is empty we will get the default values. 

#OPTIONAL VALUES:: 

# new_student1 = {'name':'Hari', 'age':22}
# new_student1 = {'name':'Hari', 'age':'22'} # pydantic use type coercing to convert this 22 string to the int as we have defined age as int . 

# student1 = Student(**new_student1)
# print(new_student1)

# new_student2 = {'email':"abcfasdf",'cgpa':5}
# new_student2 = {'email':"abc@gmail.com",'cgpa':15}  Input should be less than 10 [type=less_than, input_value=15, input_type=int]

# So this is how we can use the field functions to add the contraints 
new_student2 = {'email':"abc@gmail.com",'cgpa':5}

student2 = Student(**new_student2)

# print(new_student2)  # so there are builtin validataion for email and much more 

# WE CAN SAVE THIS PYDANTIC OBJECT AS THE DICTIONARY 

student_dict = dict(student2)
print(student_dict)

print(student_dict['age'])


# WE CAN SAVE THIS A JSON TOO 

student_json = student2.model_dump_json()

print(student_json)