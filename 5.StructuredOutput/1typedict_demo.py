from typing import TypedDict

class Person(TypedDict):

    name : str
    age :str

new_person: Person = { 'name':'Suman' , 'age':'22'}  # when we hover over the age or name it gives us the type 
new_person1: Person = { 'name':'Suman' , 'age':22}  # this will also work as type doesnot verify at runtime it is just suggession 

print(new_person)
print(new_person1) 


# this is helpful to create the structed output 