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
#except:
#    databaseConnectionStatus = "is not connected sorry :'v"


@app.route("/")
def hello():
    output_json = "Esta funcando"
    return databaseConnectionStatus

#GET REQUEST
@app.route('/Users')
def getUsers():
        query = "select *from users "
        data = databaseFn.getUsers(cursor,query)
        return jsonify(data)

@app.route('/Users/<int:user_id>')
def getUser(user_id):
    query = "select *from users where user_id = "+str(user_id)
    data = databaseFn.getUsers(cursor,query)
    return jsonify(data)

#POST REQUEST
@app.route('/Users', methods = ['POST'])
def createUser():

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
        return jsonify(data)
    elif not isValid2:
        return jsonify({"error": "el nombre ya existe"})
    else:

        return jsonify({"error": "el correo ya existe"})


#UPDATE REQUEST
@app.route('/Users', methods = ['PUT'])
def updateUser():
    content = request.get_json()
    user_id = content['id']
    new_name = content['new_name']
    data = databaseFn.updateUser(db,cursor,user_id,new_name)
    return jsonify(data)

#DELETE REQUEST
@app.route('/Users', methods = ['DELETE'])
def deleteUser():
    content = request.get_json()
    email = content['email']
    data = databaseFn.deleteUser(db,cursor,email)
    return jsonify(data)


#Token validation
@app.route('/validateToken', methods = ['POST'])
def validateToken():
    email = request.headers.get("email")
    token = request.headers.get("token")
    mobil = request.headers.get("mobil")
    data = databaseFn.validateToken(cursor,email,token,mobil)
    isUpdated = databaseFn.updateExpiration(cursor,email,mobil)
    if isUpdated:
        data["isUpdated"] = isUpdated
    else:
        data["isUpdated"] = isUpdated
    return jsonify(data)

#get tokens
@app.route('/Tokens', methods = ['GET'])
def getTokens():
    data = databaseFn.getTokens(cursor)
    return jsonify(data)


#Session start
@app.route('/Session', methods = ['POST'])
def sessionStart():
    content = request.get_json()
    email = content['email']
    password = content['password']
    ldapAns = ldapAuthConn(email,password)
    if ldapAns != "true":
        return jsonify({"advise":ldapAns})

    mobil = content['mobil']
    flag = databaseFn.validateUser(cursor,email,password)
    if flag:
        data = databaseFn.updateToken(cursor,email,mobil)
        data["ldap"] = ldapAns
        return jsonify(data)
    else:
        return jsonify({"advise":"bad email or password"})

@app.route('/Session', methods = ['DELETE'])
def sessionDelete():
    content = request.get_json()
    email = content['email']
    mobil = content['mobil']
    isExpired = databaseFn.expireToken(cursor,email,mobil)
    if isExpired:
        return jsonify({"advise":"token expirado mi prro"})
    else:
        return jsonify({"advise":"token no expirado mi prro"})




@app.route('/ldap',methods = ['POST'])
def ldapAuth():
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

        return jsonify({"advise":"Funciona mi prro "})
    except ldap.INVALID_CREDENTIALS:
        return jsonify({"advise":"invalid credentials"})
    except ldap.SERVER_DOWN:
        return jsonify({"advise":"Server down"})

def ldapAuthConn(user_email,user_password):
    email = user_email
    password = user_password

    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
        con = ldap.initialize(ldapAdress)
        con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        user_dn = "cn="+email+",dc=arqsoft,dc=unal,dc=edu,dc=co"
        user_password = password
        con.simple_bind_s(user_dn,user_password)

        return "true"
    except ldap.INVALID_CREDENTIALS:
        return "invalid credentials on ldap"
    except ldap.SERVER_DOWN:
        return "Ldap server down"




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port = 5005)


