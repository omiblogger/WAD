from pydantic import Field, BaseModel

# class Car:
#     def __init__(self, brand):
#         self.brand = brand

#     def drive(self):
#         return f"{self.brand} is driving"

# car1 = Car("BMW")
# car2 = Car("Tata")

# print(car1.brand)     # BMW
# print(car2.drive())   # Tata is driving


# Exercise 1 — Class & Object

# Student naam ki class bana. Constructor mein name aur marks le. Ek object create karke dono values print kar.

class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

stu1 = Student("Om", 99)
stu2 = Student("Priya", 95)

print(stu1.name, stu1.marks)  # Om 99


# Exercise 2 — Pydantic Validation

# EMIRequest ka object bana with principal=-100. Observe kar ki validation error mein kya aata hai.

class EMIRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    years: int = Field(gt = 0, le= 50)

loan = EMIRequest(
    principal = -50000,
    annual_rate = 8.5,
    years = 20
)

print(f"Loan principal is {loan.principal}, and For {loan.years} years.")

# Exercise 3 — Function Calling

# /search mein retrieve(request.question) ko retrieve(request.question, limit=2) kar. Swagger se test kar ki maximum 2 documents milte hain ya nahi.