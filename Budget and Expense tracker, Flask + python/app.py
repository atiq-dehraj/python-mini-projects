from flask import Flask, render_template
from flask import request, redirect, url_for
import mysql.connector  # NEW: We import our MySQL translator!

app = Flask(__name__)

@app.route('/')
def home():
    # 1. Open the connection to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="budget_db"
    )
    
    # 2. Create the cursor. 
    # (dictionary=True) is a magic trick! It makes MySQL hand us the data as standard Python dictionaries instead of plain lists.
    cursor = conn.cursor(dictionary=True)

    # 3. Fetch all the saved transactions
    cursor.execute("SELECT * FROM transactions")
    all_transactions = cursor.fetchall() # Grabs every row from the table

    # 4. Use standard Python to calculate the totals!
    total_income = 0
    total_expense = 0

    for row in all_transactions:
        if row['category'] == 'income':
            total_income += float(row['amount'])
        elif row['category'] == 'expense':
            total_expense += float(row['amount'])
            
    current_balance = total_income - total_expense

    # 5. Close the doors
    cursor.close()
    conn.close()

    # 6. Send ALL this data to our HTML template
    return render_template(
        'index.html', 
        transactions=all_transactions,
        income=total_income,
        expense=total_expense,
        balance=current_balance
    )

@app.route('/add', methods=['POST'])
def add_entry():
    # request.form acts like a Python dictionary holding all our HTML data
    # The string inside .get() MUST match the 'name' attribute in the HTML
    description = request.form.get('desc')
    amount = request.form.get('amt')
    entry_type = request.form.get('type')

    conn = mysql.connector.connect(
        host="localhost",
        user="root",       # Default XAMPP username
        password="",       # Default XAMPP password is blank
        database="budget_db"
    ) #this creates bridge between python and XAMPP
    
    # 3. Create a cursor
    cursor = conn.cursor()

    # 4. Write the SQL query using %s placeholders for security
    sql_query = "INSERT INTO transactions (description, amount, category) VALUES (%s, %s, %s)"
    
    # 5. Put our Python variables into a tuple (a fixed list)
    data_values = (description, amount, entry_type)

    # 6. Execute the query and commit (save) the changes
    cursor.execute(sql_query, data_values)
    conn.commit() 

    # 7. Close the doors behind us (good practice!)
    cursor.close()
    conn.close()

    print(f"Success! {description} was saved to the database.")

    # 8. Send the user back to the home page
    return redirect(url_for('home'))

    # The <int:transaction_id> is a dynamic variable! 
# If the URL is /delete/5, Flask passes the number 5 into the function.
@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_entry(transaction_id):
    # 1. Open database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="budget_db"
    )
    cursor = conn.cursor()

    # 2. Write the DELETE query. 
    # WARNING: Never forget the WHERE clause, or you will delete the whole table!
    sql_query = "DELETE FROM transactions WHERE id = %s"
    
    # 3. Execute and commit
    cursor.execute(sql_query, (transaction_id,)) # Notice the comma! (transaction_id,) makes it a valid Python tuple
    conn.commit()

    # 4. Close connection
    cursor.close()
    conn.close()

    # 5. Redirect back home
    return redirect(url_for('home'))

    # Notice we allow BOTH 'GET' and 'POST' methods here!
@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_entry(transaction_id):
    # 1. Open database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="budget_db"
    )
    cursor = conn.cursor(dictionary=True)

    # 2. Check WHICH method the browser is using
    if request.method == 'POST':
        # --- THE USER CLICKED 'SAVE' ---
        # Grab the new data from the form
        new_desc = request.form.get('desc')
        new_amt = request.form.get('amt')
        new_type = request.form.get('type')

        # Write the UPDATE query
        sql_query = "UPDATE transactions SET description = %s, amount = %s, category = %s WHERE id = %s"
        
        # Execute and commit the changes
        cursor.execute(sql_query, (new_desc, new_amt, new_type, transaction_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('home'))

    else:
        # --- THE USER JUST CLICKED 'EDIT' (GET Request) ---
        # Fetch the existing data so we can pre-fill the form
        cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
        transaction_to_edit = cursor.fetchone() # fetchone() grabs just ONE row instead of all of them
        
        cursor.close()
        conn.close()
        
        # We will create this 'edit.html' file next!
        return render_template('edit.html', t=transaction_to_edit)

if __name__ == '__main__':
    app.run(debug=True)