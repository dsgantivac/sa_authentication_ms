from flask import Flask
from flask import jsonify
from flask import request
import json
import databaseFn
import random
import string
import mysql.connector
import time

import ldap

app = Flask(__name__)
#ldapAdress = "ldap://192.168.99.101:389"
ldapAdress = "ldap://undrive-ldap:389"

databaseConnectionStatus = "is connected"

#def getMysqlConnection():

#db = mysql.connector.connect(user='gantiva', host='0.0.0.0', password='12345678', database='users')
def getMysqlConnection():
    #usersDB
    db = mysql.connector.connect(user='root', host='users-db', password='password', database='users')
    #db =  mysql.connector.connect(user='gantiva', host='0.0.0.0', password='12345678', database='users')
    return db

#try:
db = getMysqlConnection()
cursor = db.cursor()
databaseFn.createDB(cursor)
db.close()
cursor.close()
#except:
#    databaseConnectionStatus = "is not connected sorry :'v"


@app.route("/")
def hello():
    db = getMysqlConnection()
    cursor = db.cursor()
    output_json = "Esta funcando"
    db.close()
    cursor.close()
    return databaseConnectionStatus

#GET REQUEST
@app.route('/Users')
def getUsers():
        db = getMysqlConnection()
        cursor = db.cursor()
        query = "select *from users "
        data = databaseFn.getUsers(cursor,query)
        db.close()
        cursor.close()
        return jsonify(data)

@app.route('/Users/<int:user_id>')
def getUser(user_id):
    db = getMysqlConnection()
    cursor = db.cursor()
    query = "select *from users where user_id = "+str(user_id)
    data = databaseFn.getUsers(cursor,query)
    
    db.close()
    cursor.close()
    return jsonify(data)

#POST REQUEST
@app.route('/Users', methods = ['POST'])
def createUser():
    db = getMysqlConnection()
    cursor = db.cursor()

    content = request.get_json()
    name = content['name']
    email = content['email']
    password = content['password']
    mobil = content['mobil']
    isValid = databaseFn.validateEmail(cursor,email)
    isValid2 =  databaseFn.validateName(cursor,name)
    #print("VALIDATION",isValid,isValid2)
    if isValid and isValid2:
        data = databaseFn.newUser(db,cursor,name,email,password)
        data = databaseFn.generateToken(db,cursor,data["id"],email,mobil)
        db.close()
        cursor.close()
        return jsonify(data)
    elif not isValid2:
        db.close()
        cursor.close()
        return jsonify({"error": "el nombre ya existe"})
    else:
        db.close()
        cursor.close()
        return jsonify({"error": "el correo ya existe"})


#UPDATE REQUEST
@app.route('/Users', methods = ['PUT'])
def updateUser():
    db = getMysqlConnection()
    cursor = db.cursor()
    content = request.get_json()
    user_id = content['id']
    new_name = content['new_name']
    data = databaseFn.updateUser(db,cursor,user_id,new_name)
    db.close()
    cursor.close()
    return jsonify(data)

#DELETE REQUEST
@app.route('/Users', methods = ['DELETE'])
def deleteUser():
    db = getMysqlConnection()
    cursor = db.cursor()
    content = request.get_json()
    email = content['email']
    data = databaseFn.deleteUser(db,cursor,email)
    db.close()
    cursor.close()
    return jsonify(data)


#Token validation
@app.route('/validateToken', methods = ['POST'])
def validateToken():
    db = getMysqlConnection()
    cursor = db.cursor()
    email = request.headers.get("email")
    token = request.headers.get("token")
    mobil = request.headers.get("mobil")
    data = databaseFn.validateToken(cursor,email,token,mobil)
    isUpdated = databaseFn.updateExpiration(cursor,email,mobil)
    if isUpdated:
        data["isUpdated"] = isUpdated
    else:
        data["isUpdated"] = isUpdated
    db.close()
    cursor.close()
    return jsonify(data)

#get tokens
@app.route('/Tokens', methods = ['GET'])
def getTokens():
    db = getMysqlConnection()
    cursor = db.cursor()
    data = databaseFn.getTokens(cursor)
    db.close()
    cursor.close()
    return jsonify(data)


#Session start
@app.route('/Session', methods = ['POST'])
def sessionStart():
    db = getMysqlConnection()
    cursor = db.cursor()
    content = request.get_json()
    email = content['email']
    password = content['password']
    ldapAns = ldapAuthConn(email,password)
    if ldapAns != "true":
        db.close()
        cursor.close()
        return jsonify({"advise":ldapAns})

    mobil = content['mobil']
    flag = databaseFn.validateUser(cursor,email,password)
    if flag:
        data = databaseFn.updateToken(cursor,email,mobil)
        data["ldap"] = ldapAns
        #db.close()
        #cursor.close()
        return jsonify(data)
    else:
        db.close()
        cursor.close()
        return jsonify({"advise":"bad email or password"})

@app.route('/Session', methods = ['DELETE'])
def sessionDelete():
    db = getMysqlConnection()
    cursor = db.cursor()
    content = request.get_json()
    email = content['email']
    mobil = content['mobil']
    isExpired = databaseFn.expireToken(cursor,email,mobil)
    if isExpired:
        db.close()
        cursor.close()
        return jsonify({"advise":"token expirado mi prro"})
    else:
        db.close()
        cursor.close()
        return jsonify({"advise":"token no expirado mi prro"})




@app.route('/ldap',methods = ['POST'])
def ldapAuth():
    db = getMysqlConnection()
    cursor = db.cursor()
    content = request.get_json()
    email = content['email']
    password = content['password']

    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
        con = ldap.initialize(ldapAdress)
        con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        user_dn = "cn="+email+",dc=arqsoft,dc=unal,dc=edu,dc=co"
        user_password = password
        con.simple_bind_s(user_dn,user_password)

        """
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
        con = ldap.initialize("ldaps://192.168.99.101:636")
        con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        #
        user_dn = "cn=David Gantiva,dc=arqsoft,dc=unal,dc=edu,dc=co"
        user_password = "1234"
        con.simple_bind_s(user_dn,user_password)

        #link por si acaso
        https://stackoverflow.com/questions/16051839/how-to-set-lockouttime-and-password-of-a-user-of-active-directory
        https://www.adimian.com/blog/2014/10/basic-ldap-actions-using-python/
        """
        db.close()
        cursor.close()
        return jsonify({"advise":"Funciona mi prro "})
    except ldap.INVALID_CREDENTIALS:
        db.close()
        cursor.close()
        return jsonify({"advise":"invalid credentials"})
    except ldap.SERVER_DOWN:
        db.close()
        cursor.close()
        return jsonify({"advise":"Server down"})

def ldapAuthConn(user_email,user_password):
    db = getMysqlConnection()
    cursor = db.cursor()
    email = user_email
    password = user_password

    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
        con = ldap.initialize(ldapAdress)
        con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        user_dn = "cn="+email+",dc=arqsoft,dc=unal,dc=edu,dc=co"
        user_password = password
        con.simple_bind_s(user_dn,user_password)
        db.close()
        cursor.close()
        return "true"
    except ldap.INVALID_CREDENTIALS:
        db.close()
        cursor.close()
        return "invalid credentials on ldap"
    except ldap.SERVER_DOWN:
        db.close()
        cursor.close()
        return "Ldap server down"




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port = 5005)


