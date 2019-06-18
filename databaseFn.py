import mysql.connector
import time
import random
import string
from datetime import datetime

token_time = 10080 #in minutes

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def time_between(d1, d2):
    return int(abs((d2 - d1).seconds)/60)


def createDB(cursor):
    sql = """CREATE TABLE IF NOT EXISTS users (
        id INT(11) PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(60) NOT NULL,
        email VARCHAR(60) NOT NULL,
        password VARCHAR(60) NOT NULL
        ); """
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS tokens (
        id INT(11) PRIMARY KEY,
        email VARCHAR(60) NOT NULL,
        token VARCHAR(60) NOT NULL,
        date VARCHAR(60) NOT NULL
        ); """
    cursor.execute(sql)


def validateEmail(cursor,email):
    data = {}
    sql = "select *from users where email LIKE \""+ email+"\";"
    flag = False
    try:

        # Execute the SQL command
        flag = False
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results) >  0:
            return False
        else:
            return True
        # Fetch all the rows in a list of lists.
    except:
        data["advise"] = "No se pudieron obtener los datos"
        #print ("Error: unable to fetch data")
        print(data)
    return flag

def validateName(cursor,name):
    data = {}
    sql = "select *from users where name = \""+ name+"\";"
    flag = False
    try:

        # Execute the SQL command
        flag = False
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)
        print(sql)
        if len(results) >  0:
            return False
        else:
            return True
        # Fetch all the rows in a list of lists.
    except:
        data["advise"] = "No se pudieron obtener los datos"
        #print ("Error: unable to fetch data")
        print(data)
    return flag


def getUsers(cursor,query):
    data = {}
    try:
        # Execute the SQL command
        cursor.execute(query)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            user_id = row[0]
            name = row[1]
            email = row[2]
            password = row[3]
            # Now print fetched result
            data[user_id] = {"name:":name,"email:": email, "password:":password}
            #print("id:",user_id,"name:",name,"email:", email, "password:",password )
    except:
        data["advise"] = "No se pudieron obtener los datos"
        print(data)
    return data

def newUser(db,cursor,name,email,password):
    sql = "insert into users(name,email,password) values (\""+name+"\",\""+email+"\",\""+password+"\");"
    print(sql)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        return {"advise":"operation successfull","id":cursor.lastrowid}
    except:
        # Rollback in case there is any error
        db.rollback()
        return {"advise":"error on insert"}


def updateUser(db,cursor,id,new_name):
    sql = "update users set name = \""+new_name+"\" where id = \""+str(id)+"\";"
    print(sql)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        return {"advise":"operation successfull"}
    except:
        # Rollback in case there is any error
        db.rollback()
        return {"advise":"error on insert"}

def deleteUser(db,cursor,email):
    sql = "DELETE FROM users WHERE email = \""+ email+"\""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        return {"advise":"operation successfull"}
    except:
        # Rollback in case there is any error
        db.rollback()
        return {"advise":"error on insert"}

def generateToken(db,cursor,id,email):
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    print(now)
    token = randomString()
    sql = "insert into tokens(id,email,token,date) values (\""+str(id)+"\",\""+email+"\",\""+token+"\",\""+str(now)+"\");"
    print(sql)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        return {"advise":"operation successfull","id":id,"token":token}
    except:
        # Rollback in case there is any error
        db.rollback()
        return {"advise":"error on insert"}

def validateToken(cursor,email,token):
    query = "select token,date from tokens where email like \""+ email+"\""
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    data = {}
    try:
        # Execute the SQL command
        cursor.execute(query)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            query_token = row[0]
            query_date = row[1]
            d1 = datetime.strptime(query_date, '%Y-%m-%d %H-%M-%S')
            d2 = datetime.strptime(now, '%Y-%m-%d %H-%M-%S')
        if token == query_token:
            if time_between(d1,d2) >= token_time:
                data["advise"] = "Token Expired"
            else:
                data["advise"] = "Token accepted"
                data["time"] = time_between(d1,d2)
        else:
            data["advise"] = "Token error"

    except:
        data["advise"] = "No se pudieron obtener los datos"
        print(data)
        return data

#    return {"token":query_token,"date":d1,"now":d2,"between":time_between(d1,d2)}
    return data

def getTokens(cursor):
    query = "select * from tokens"
    data = {}
    try:
        # Execute the SQL command
        cursor.execute(query)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            user_id = row[0]
            email = row[1]
            token = row[2]
            date = row[3]
            # Now print fetched result
            data[user_id] = {"id:":user_id,"email:": email, "token:":token,"date":date}
            #print("id:",user_id,"name:",name,"email:", email, "password:",password )
    except:
        data["advise"] = "No se pudieron obtener los datos"
        print(data)
    return data


def updateToken(cursor,email):
    data = {}
    token = randomString()
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    query = "update tokens set token = \""+token+"\" , date = \""+str(now)+"\" where TRIM(email) LIKE \""+email+"\";"
    query2 = "select name from users where email LIKE \""+ email+"\";"
    print(query)
    # Execute the SQL command
    try:
        cursor.execute(query)
        cursor.execute(query2)
        results = cursor.fetchall()
        for row in results:
            name = row[0]
        # Fetch all the rows in a list of lists.
        data = {"advise":"token updated","token":token,"email":email,"name":name}
        return data
    except:
        data["advise"] = "No se pudieron obtener los datos"
        print(data)
        return data

def updateExpiration(cursor,email):
    data = {}
    token = randomString()
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    query = "update tokens set date = \""+str(now)+"\" where TRIM(email) LIKE \""+email+"\";"
    # Execute the SQL command
    try:
        cursor.execute(query)
        #data = {"advise":"token updated","token":token,"email":email,"name":name}
        return True
    except:
        data["advise"] = "No se pudieron obtener los datos"
        print(data)
        return False

def expireToken(cursor,email):
    data = {}
    init_data = datetime.strptime("2019-01-01 00-00-00", '%Y-%m-%d %H-%M-%S')

    query = "update tokens set date = \""+str(init_data)+"\" where TRIM(email) LIKE \""+email+"\";"
    # Execute the SQL command
    try:
        cursor.execute(query)
        #data = {"advise":"token updated","token":token,"email":email,"name":name}
        return True
    except:
        data["advise"] = "No se pudo expirar el token"
        print(data)
        return False



def validateUser(cursor,email,password):
    query = "select password from users where  TRIM(email) LIKE \""+email+"\";"
    data = {}
    try:
        # Execute the SQL command
        cursor.execute(query)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            user_password = row[0]
            #print("id:",user_id,"name:",name,"email:", email, "password:",password )
        if user_password == password:
            return True
        else:
            return False
    except:
        print("error en la queru validate user")
        return False


