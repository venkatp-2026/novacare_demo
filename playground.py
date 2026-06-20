"""
PYTHON OBJECT-ORIENTED PROGRAMMING (OOP) MASTER GUIDE
=====================================================

This comprehensive guide covers:
CORE CONCEPTS:
1. Classes & Objects
2. Encapsulation
3. Inheritance
4. Polymorphism
5. Abstraction
6. Class & Static Methods
7. Interfaces

ADVANCED CONCEPTS:
8. Multiple Inheritance & MRO
9. Property Decorators
10. Magic Methods (Dunder Methods)
11. Composition over Inheritance
"""

from abc import ABC, abstractmethod
from datetime import datetime

# ---------------------------------------------------------
# 1. CLASSES & OBJECTS 
# A class is a blueprint; an object is an instance.
# ---------------------------------------------------------

class Patient:
    # Class Attribute (shared by all instances)
    hospital_name = "NovaHealth Medical Center"

    def __init__(self, patient_id, name, age):
        # Instance Attributes (unique to each object)
        self.patient_id = patient_id
        self.name = name
        self.age = age
        
    def display_info(self):
        """Instance Method: uses 'self' to access attributes."""
        return f"ID: {self.patient_id} | Name: {self.name} | Hospital: {self.hospital_name}"

# Creating Objects (Instantiation)
p1 = Patient("P001", "Alice Smith", 30)
p2 = Patient("P002", "Bob Jones", 45)

print("--- Classes & Objects ---")
print(p1.display_info())


# ---------------------------------------------------------
# 2. ENCAPSULATION
# Grouping data (attributes) and methods together while 
# restricting access to some components.
# Usage of _, __ (Protected and Private)
# ---------------------------------------------------------

class MedicalRecord:
    def __init__(self, patient_name, diagnosis):
        self.patient_name = patient_name      # Public
        self._doctor_assigned = "Dr. Nova"    # Protected (Internal use hint)
        self.__diagnosis = diagnosis          # Private (Name mangled)

    def get_diagnosis(self, auth_token):
        """Getter: Controlled access to private data."""
        if auth_token == "HEAL123":
            return self.__diagnosis
        return "Access Denied"

record = MedicalRecord("Alice", "Mild Fever")
print("\n--- Encapsulation ---")
print(f"Public: {record.patient_name}")
print(f"Private (via Getter): {record.get_diagnosis('HEAL123')}")
# print(record.__diagnosis)  # This would throw an AttributeError


# ---------------------------------------------------------
# 3. INHERITANCE
# A child class inherits attributes/methods from a parent class.
# ---------------------------------------------------------

class Staff: # Parent Class
    def __init__(self, name, staff_id):
        self.name = name
        self.staff_id = staff_id

    def work(self):
        return f"{self.name} is performing general duties."

class Doctor(Staff): # Child Class
    def __init__(self, name, staff_id, specialty):
        # super() calls the constructor of the Parent Class
        super().__init__(name, staff_id)
        self.specialty = specialty

    def work(self): # Method Overriding
        return f"Dr. {self.name} is treating patients in {self.specialty}."

doc = Doctor("Sarah", "D404", "Cardiology")
print("\n--- Inheritance ---")
print(doc.work())


# ---------------------------------------------------------
# 4. POLYMORPHISM
# "Many forms" - different classes can have methods with the same name.
# ---------------------------------------------------------

class Nurse(Staff):
    def work(self):
        return f"Nurse {self.name} is assisting patients."

# Same method call 'work()' behaves differently based on object type
staff_list = [Doctor("Smith", "D1", "General"), Nurse("Joy", "N1")]

print("\n--- Polymorphism ---")
for staff in staff_list:
    print(staff.work())


# ---------------------------------------------------------
# 5. ABSTRACTION
# Hiding complex implementation details and showing only 
# the necessary features. Done via Abstract Base Classes (ABC).
# ---------------------------------------------------------

class Equipment(ABC):
    @abstractmethod
    def operate(self):
        """Every piece of equipment must define its own operation."""
        pass

class XRayMachine(Equipment):
    def operate(self):
        return "X-Ray session started. Radiation caution."

class MRI(Equipment):
    def operate(self):
        return "MRI scan started. Please remain still."

print("\n--- Abstraction ---")
# equipment = Equipment() # Error! Cannot instantiate abstract class
mri = MRI()
print(mri.operate())


# ---------------------------------------------------------
# 6. CLASS & STATIC METHODS (DETAILED)
# ---------------------------------------------------------

"""
INSTANCE METHOD: Takes 'self', operates on instance data
CLASS METHOD: Takes 'cls', operates on class-level data, can create alternative constructors
STATIC METHOD: Takes neither, used for utility functions related to the class
"""

class Facility:
    count = 0
    all_facilities = []  # Class variable to track all facilities

    def __init__(self, name, location):
        self.name = name  # Instance variable
        self.location = location
        Facility.count += 1
        Facility.all_facilities.append(self)

    # Instance Method
    def display(self):
        """Operates on this specific facility instance."""
        return f"{self.name} in {self.location}"

    # Class Method - Alternative Constructor
    @classmethod
    def from_string(cls, facility_string):
        """Creates a Facility from a formatted string 'Name-Location'."""
        name, location = facility_string.split('-')
        return cls(name, location)  # Returns a new instance

    # Class Method - Access Class Data
    @classmethod
    def get_total_facilities(cls):
        """Accesses class variables, not instance ones."""
        return f"Total NovaHealth sites: {cls.count}"

    # Static Method - Utility Function
    @staticmethod
    def generic_health_tip():
        """No access to cls or self. Just a helper function."""
        return "Reminder: Drink 8 glasses of water daily."
    
    @staticmethod
    def validate_location(location):
        """Utility to validate location format."""
        return len(location) > 2 and location.isalpha()

print("\n--- Class & Static Methods (Detailed) ---")
f1 = Facility("Main Hospital", "Boston")
f2 = Facility.from_string("Clinic-NewYork")  # Using class method constructor
print(f1.display())
print(f2.display())
print(Facility.get_total_facilities())
print(Facility.generic_health_tip())
print(f"Is 'LA' valid? {Facility.validate_location('LA')}")


# ---------------------------------------------------------
# 7. INTERFACES (Using ABC)
# ---------------------------------------------------------

"""
An INTERFACE defines a contract: any class implementing it MUST provide 
specific methods. Python uses Abstract Base Classes (ABC) for this.
"""

class PaymentProcessor(ABC):
    """Interface: All payment processors must implement these methods."""
    
    @abstractmethod
    def process_payment(self, amount):
        pass
    
    @abstractmethod
    def refund(self, transaction_id):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via Credit Card"
    
    def refund(self, transaction_id):
        return f"Refunding transaction {transaction_id}"

class InsuranceClaimProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} insurance claim"
    
    def refund(self, transaction_id):
        return f"Reversing claim {transaction_id}"

print("\n--- Interfaces ---")
cc_processor = CreditCardProcessor()
print(cc_processor.process_payment(150.00))
# payment = PaymentProcessor()  # Error! Cannot instantiate abstract class


# ---------------------------------------------------------
# 8. MULTIPLE INHERITANCE & METHOD RESOLUTION ORDER (MRO)
# ---------------------------------------------------------

"""
Multiple Inheritance: A class can inherit from multiple parent classes.
MRO: Determines the order Python searches for methods in the inheritance hierarchy.
Use ClassName.mro() or ClassName.__mro__ to see the order.
"""

class Person:
    def __init__(self, name):
        self.name = name
    
    def introduce(self):
        return f"I'm {self.name}"

class Employee:
    def __init__(self, employee_id):
        self.employee_id = employee_id
    
    def work_info(self):
        return f"Employee ID: {self.employee_id}"

class Specialist:
    def __init__(self, specialization):
        self.specialization = specialization
    
    def specialty_info(self):
        return f"Specialization: {self.specialization}"

# Multiple Inheritance
class MedicalStaff(Person, Employee, Specialist):
    def __init__(self, name, employee_id, specialization, department):
        Person.__init__(self, name)
        Employee.__init__(self, employee_id)
        Specialist.__init__(self, specialization)
        self.department = department
    
    def full_profile(self):
        return f"{self.introduce()} | {self.work_info()} | {self.specialty_info()} | Dept: {self.department}"

print("\n--- Multiple Inheritance ---")
staff = MedicalStaff("Dr. Chen", "EMP789", "Neurology", "Brain Center")
print(staff.full_profile())
print(f"MRO: {[cls.__name__ for cls in MedicalStaff.mro()]}")


# ---------------------------------------------------------
# 9. PROPERTY DECORATORS (@property, @setter, @deleter)
# ---------------------------------------------------------

"""
Properties allow you to use getter/setter logic with attribute-like access.
Benefits: Validation, computed attributes, backward compatibility.
"""

class Patient:
    def __init__(self, name, age):
        self._name = name
        self._age = age
        self._temperature = 98.6  # Fahrenheit
    
    # Getter: Read-only computed property
    @property
    def name(self):
        """Access via patient.name (no parentheses)."""
        return self._name.title()
    
    # Setter: Validation logic
    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Name must be a non-empty string")
        self._name = value
    
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if value < 0 or value > 150:
            raise ValueError("Invalid age")
        self._age = value
    
    # Computed property (read-only)
    @property
    def temperature_celsius(self):
        """Auto-convert Fahrenheit to Celsius."""
        return round((self._temperature - 32) * 5/9, 2)
    
    @property
    def is_adult(self):
        """Derived property."""
        return self._age >= 18
    
    # Deleter
    @age.deleter
    def age(self):
        print("Age cannot be deleted, resetting to 0")
        self._age = 0

print("\n--- Property Decorators ---")
patient = Patient("john doe", 25)
print(f"Name (titled): {patient.name}")  # Getter with formatting
patient.age = 30  # Setter with validation
print(f"Age: {patient.age}, Adult: {patient.is_adult}")
print(f"Temp in Celsius: {patient.temperature_celsius}°C")


# ---------------------------------------------------------
# 10. MAGIC METHODS (Dunder Methods)
# ---------------------------------------------------------

"""
Magic methods let you define custom behavior for built-in operations.
Common ones: __str__, __repr__, __len__, __add__, __eq__, __lt__, __getitem__
"""

class Appointment:
    def __init__(self, patient_name, doctor_name, date, duration_minutes):
        self.patient_name = patient_name
        self.doctor_name = doctor_name
        self.date = date
        self.duration_minutes = duration_minutes
    
    # String representation for users
    def __str__(self):
        return f"Appointment: {self.patient_name} with {self.doctor_name} on {self.date}"
    
    # String representation for developers
    def __repr__(self):
        return f"Appointment('{self.patient_name}', '{self.doctor_name}', '{self.date}', {self.duration_minutes})"
    
    # Length
    def __len__(self):
        return self.duration_minutes
    
    # Addition: Combine appointments
    def __add__(self, other):
        total_duration = self.duration_minutes + other.duration_minutes
        return f"Combined duration: {total_duration} minutes"
    
    # Equality
    def __eq__(self, other):
        return self.date == other.date and self.patient_name == other.patient_name
    
    # Less than (for sorting)
    def __lt__(self, other):
        return self.duration_minutes < other.duration_minutes

print("\n--- Magic Methods ---")
apt1 = Appointment("Alice", "Dr. Smith", "2026-06-21", 30)
apt2 = Appointment("Bob", "Dr. Jones", "2026-06-21", 45)

print(f"str: {str(apt1)}")
print(f"repr: {repr(apt1)}")
print(f"len: {len(apt1)} minutes")
print(f"Addition: {apt1 + apt2}")
print(f"Equality: apt1 == apt2? {apt1 == apt2}")
print(f"Comparison: apt1 < apt2? {apt1 < apt2}")

# Bonus: __getitem__ for indexing
class Schedule:
    def __init__(self):
        self.appointments = []
    
    def add(self, appointment):
        self.appointments.append(appointment)
    
    def __getitem__(self, index):
        """Enables schedule[0] syntax."""
        return self.appointments[index]
    
    def __len__(self):
        return len(self.appointments)

schedule = Schedule()
schedule.add(apt1)
schedule.add(apt2)
print(f"\nFirst appointment via indexing: {schedule[0]}")
print(f"Total appointments: {len(schedule)}")


# ---------------------------------------------------------
# 11. COMPOSITION OVER INHERITANCE
# ---------------------------------------------------------

"""
Composition: Building complex objects by combining simpler ones (HAS-A relationship).
Often more flexible than inheritance (IS-A relationship).
"""

# Using Composition
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
    
    def start(self):
        return f"Engine with {self.horsepower}HP started"

class GPS:
    def navigate(self, destination):
        return f"Navigating to {destination}"

# Ambulance HAS-A Engine and HAS-A GPS
class Ambulance:
    def __init__(self, vehicle_id, horsepower):
        self.vehicle_id = vehicle_id
        self.engine = Engine(horsepower)  # Composition
        self.gps = GPS()  # Composition
    
    def dispatch(self, location):
        return f"Ambulance {self.vehicle_id}: {self.engine.start()} | {self.gps.navigate(location)}"

print("\n--- Composition ---")
ambulance = Ambulance("AMB-001", 250)
print(ambulance.dispatch("123 Emergency St"))

# Contrast with Inheritance
class Vehicle:
    def move(self):
        return "Vehicle moving"

class EmergencyVehicle(Vehicle):  # IS-A relationship
    def sound_siren(self):
        return "Siren: WEE-WOO"

print("\nInheritance: EmergencyVehicle IS-A Vehicle")
ev = EmergencyVehicle()
print(f"{ev.move()} | {ev.sound_siren()}")

print("\n" + "="*60)
print("SUMMARY: Run this file to see all OOP concepts in action!")
print("="*60)
 