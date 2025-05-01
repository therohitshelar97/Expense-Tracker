import os

os.add_dll_directory('C:\\Users\\rohid\\OneDrive\\Desktop\\DB2\\Flask-Application-With-IBM-Cloud-DB2-database\\myenv\\Lib\\site-packages\\clidriver\\bin') 

import ibm_db
import ibm_db_dbi
from flask import *
import os
from groq import Groq
from datetime import datetime


app = Flask(__name__)


# Connection parameters
dsn_hostname = "ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
dsn_uid = "fbn36940"
dsn_pwd = "4kcejnT4VVNrzHi9"
dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"
dsn_port = "31505"
dsn_protocol = "TCPIP"
dsn_security = "SSL"

#Create database connection
#DO NOT MODIFY THIS CELL. Just RUN it with Shift + Enter
dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security)

try:
    conn = ibm_db.connect(dsn, "", "")
    print ("Connected to database: ", dsn_database, "as user: ", dsn_uid, "on host: ", dsn_hostname)

except:
    print ("Unable to connect: ", ibm_db.conn_errormsg() )

@app.route('/')
def Index():
    return render_template("index.html")

@app.route('/',methods=['POST'])
def Exp_Enter():
    desc = request.form.get('desc')
    amt = float(request.form.get('amt'))
    
    try:
        amount = amt
        description = desc
        # show_summary()
    except ValueError:
        print("Invalid amount. Try again.")

        # Set your Groq API key
    GROQ_API_KEY = "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"

    # Initialize client
    client = Groq(api_key=GROQ_API_KEY)

    # In-memory store
    expenses = []
    category_totals = {}

    # Categories
    categories = ["Food", "Rent", "Travel", "Entertainment", "Utilities", "Shopping", "Other"]

    # Classifier using Groq
    
    prompt = f"""Classify the following expense description into one of these categories: {', '.join(categories)}.\n
    Description: "{description}"\nCategory:"""

    chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",  # or use Gemma / LLaMA3 depending on what you prefer
        )

        # return chat_completion.choices[0].message.content.strip()

    # Log expense
    
    category = chat_completion.choices[0].message.content.strip()
    expenses.append({
            "description": description,
            "amount": amount,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })

    # Update total
    category_totals[category] = category_totals.get(category, 0) + amount
    print(f"Logged ₹{amount} for '{description}' under category: {category}")
    
    
    id=1 
    description = expenses[0]['description']
    amount = expenses[0]['amount']
    category1 = expenses[0]['category']
    time = expenses[0]['timestamp']


   

    insert = "insert into expense(id, amount, category, description, time1) values ('{}','{}','{}','{}','{}') ".format(id,amount,category,description,time)
    ibm_db.exec_immediate(conn, insert)

    
    # Suggest if overspending
    selectQuery = "select * from expense"
    selectStmt = ibm_db.exec_immediate(conn, selectQuery)
    rows = []  
    row = ibm_db.fetch_assoc(selectStmt)
    while row:  # Loop until no more rows are returned
        rows.append(row)  # Append the current row (as a dictionary)
        row = ibm_db.fetch_assoc(selectStmt)  # Fetch the next row

    data = rows
    total_amt=0
    for amt in data:
        total_amt=total_amt+amt['AMOUNT']
    if total_amt > 5000:
            warning = f"You are spending a lot on {category}. Consider cutting down."

            
    return render_template("index.html",amt=amount,cat=category1,desc=description,t=time,war=warning,total_amount=total_amt)
    # return redirect(url_for('Index'),exp=expenses)

@app.route('/history')
def History():
    selectQuery = "select * from expense"
    selectStmt = ibm_db.exec_immediate(conn, selectQuery)
    rows = []  
    row = ibm_db.fetch_assoc(selectStmt)
    while row:  # Loop until no more rows are returned
        rows.append(row)  # Append the current row (as a dictionary)
        row = ibm_db.fetch_assoc(selectStmt)  # Fetch the next row

    data = rows
    total_amt=0
    for amt in data:
        total_amt=total_amt+amt['AMOUNT']
    print(total_amt)
    # if total_amt > 5000:
    #         warning = f"You are spending a lot on {cat}. Consider cutting down."
    # print(data)
    return render_template('history.html',data=data,total_amount=total_amt)

if __name__=='__main__':
    app.run(debug=True)
