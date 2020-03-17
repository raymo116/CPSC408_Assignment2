'''
A simple SQLite CRUD application running through python

@name: Assignment 2.py
@author: Matt Raymond
@email: raymo116@mail.chapman.edu
@id: 2270559
@date: 03/16/2020
@version: 1.0
'''

########################################################################################################################
# IMPORTS ##############################################################################################################
########################################################################################################################

import sqlite3
import pandas as pd
import re

########################################################################################################################


########################################################################################################################
# GLOBAL VARIABLES #####################################################################################################
########################################################################################################################

# Set up database connection
conn = sqlite3.connect("StudentDB.sqlite")
c = conn.cursor()  # allows python code to execute in datagrip


########################################################################################################################


########################################################################################################################
# FUNCTION DECLARATIONS ################################################################################################
########################################################################################################################

# Checks to see if a given student id exists in the database
def IDExists(intID: int):
    c.execute("select count(*) from Student where StudentId = ?", (intID,))
    return (c.fetchall()[0][0]) == 1


# Creates a new student in the database with the given information
def createNewStudent(intID: int, strFName: str, strLastName: str, fltGPA: float, strMajor: str, strAdvisor: str):
    try:
        if not IDExists(intID):
            c.execute(
                "insert into Student (StudentId, FirstName, LastName, GPA, Major, FacultyAdvisor, isDeleted) values(?,?,?,?,?,?,?)",
                (intID, strFName, strLastName, fltGPA, strMajor, strAdvisor, False,))
            conn.commit()
            print("Update successful")
        else:
            print("That student ID is already taken")
    except Exception as e:
        print("There was a problem creating the student:", e)


# Soft deletes a student from the database
def removeStudent(intID: int):
    try:
        if IDExists(intID):
            c.execute("update Student set isDeleted = 1 where StudentId = ?", (intID,))
            conn.commit()
            print("Removal successful")
        else:
            print("That student doesn't exist")
    except Exception as e:
        print("there was an error deleting the student:", e)


# Updates a student's information
def updateStudent(intID: int, strMajor: str, strAdvisor: str):
    try:
        if IDExists(intID):
            c.execute("update Student set Major = ?, FacultyAdvisor = ? where StudentId = ?",
                      (strMajor, strAdvisor, intID,))
            conn.commit()
            print("Update successful")
        else:
            print("That student doesn't exist")
    except Exception as e:
        print("there was an error updating the student:", e)


# Searches for a given student in the database. If no fields are given, it returns everyone
def searchStudent(strMajor: str = None, fltGPA: float = None, strAdvisor: str = None):
    try:
        # Sets up a query string to append to
        queryString = "select StudentId, FirstName, LastName, GPA, Major, FacultyAdvisor from Student where isDeleted = 0"
        # Sets up a query object to append to
        queryObject = ()

        # Checks if each variable is null
        if strMajor is not None:
            # If not, it appends that search term to the end
            queryString += " and lower(Major) like ?"
            # And adds a query object
            queryObject += ('%' + strMajor.lower() + '%',)
        if fltGPA is not None:
            queryString += " and GPA is ?"
            queryObject += (fltGPA,)
        if strAdvisor is not None:
            queryString += " and lower(FacultyAdvisor) like ?"
            queryObject += ('%' + strAdvisor.lower() + '%',)

        # Executes the query
        c.execute(queryString, queryObject)
        df = pd.DataFrame(c.fetchall())

        # If anything is returned
        if not df.empty:
            # Assign column headers and print
            df.columns = ['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor']
            print(df)
        else:
            print("There are no such students in the database")
    except Exception as e:
        print("there was an error:", e)


# User interface for creating a student
def askCreate():
    while True:
        try:
            strInput = input("Enter an ID, First Name, Last Name, GPA, Major, "
                             + "and faculty adviser with comma delineation:\n")

            # Breaks anywhere there's a space, removing whitespace along with it
            pattern = re.compile(r"^\s+|\s*,\s*|\s+$")
            split = [x for x in pattern.split(strInput) if x]

            # If there are the right number of parameters
            if len(split) == 6:
                # Cast the parameters
                split[0] = int(split[0])
                split[3] = float(split[3])

                # Check to make sure the names are propper strings
                if split[1].isalpha() and split[2].isalpha() and split[4].isalpha():
                    # Perform the operation
                    createNewStudent(split[0], split[1], split[2], split[3], split[4], split[5])
                    return

        except Exception as e:
            print(e)

        print("That was not a valid input. Please try again")


# User interface for soft deleting a student
def askRemove():
    try:
        strInput = input("Enter an the ID of a student that you want to delete:\n")
        removeStudent(int(strInput))
        return

    except Exception as e:
        print(e)

    print("That was not a valid input. Please try again")


# User interface for updating a student
def askUpdate():
    while True:
        try:
            strInput = input("Enter the id of a student that you want to update, as well as the new values "
                             + "for their major and faculty advisor. Delineate with commas:\n")

            # Breaks anywhere there's a space, removing whitespace along with it
            pattern = re.compile(r"^\s+|\s*,\s*|\s+$")
            split = [x for x in pattern.split(strInput) if x]

            # Checks to make sure that we have the correct number of parameters
            if len(split) == 3:
                # Casts the variable
                split[0] = int(split[0])

                # Checks to make sure that it's alpha
                if split[1].isalpha() and split[2].isalpha():
                    # Performs action
                    updateStudent(split[0], split[1], split[2])
                    return

        except Exception as e:
            print(e)

        print("That was not a valid input. Please try again")


# User interface for searching for a student
def askSearch():
    while True:
        try:
            strInput = input(
                "Enter the major, GPA, and/or faculty adviser of a student to search for them.\n"
                + "Delineate with commas and put stars in fields you don't want to search on "
                + "(e.g. ., ., Rene German):\n")

            # Breaks anywhere there's a space, removing whitespace along with it
            pattern = re.compile(r"^\s+|\s*,\s*|\s+$")
            split = [x for x in pattern.split(strInput) if x]

            # Replaces all of the stars with Nones
            split = [None if x == "*" else x for x in split]

            #  Checks to make sure that we have the correct number of parameters
            if (len(split) == 3):
                if (split[1] is not None):
                    # Casts the parameter if it can
                    split[1] = float(split[1])

                # Performs the operation
                searchStudent(split[0], split[1], split[2])
                return

        except Exception as e:
            print(e)

        print("That was not a valid input. Please try again")


# Main Menu
def askFunction():
    while True:
        #  Print the menu
        print("\n\n\n\n")
        print("This is a database. Cool. You know the drill. Choose")
        print("0) View Students in the database")
        print("1) Create a new student")
        print("2) Update a student record")
        print("3) Search a specific Student")
        print("4) Remove a specific Student")
        print("q) Quit")

        # Get input
        strInput = input("")
        print("\n\n\n")

        # Choose which operation to perform
        if strInput == "0":
            searchStudent()
        elif strInput == "1":
            askCreate()
        elif strInput == "2":
            askUpdate()
        elif strInput == "3":
            askSearch()
        elif strInput == "4":
            askRemove()
        elif strInput == "q":
            print("Adios")
            return
        else:
            print("That was not a valid option.")


########################################################################################################################


########################################################################################################################
# MAIN #################################################################################################################
########################################################################################################################

if __name__ == "__main__":
    askFunction()
