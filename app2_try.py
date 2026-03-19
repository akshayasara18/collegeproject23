from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import date
from datetime import datetime
import matplotlib
matplotlib.use('Agg')   # For rendering without GUI
import matplotlib.pyplot as plt
import io
from twilio.rest import Client  # <-- Twilio library
import base64


app1_try = Flask(__name__)
app1_try.secret_key = "d5458cee4cc8f5af510fa0cb1488067eb19044a135864efe650f9e6fedd919f6"  


import yagmail  #Mail

EMAIL_USER = "fatimaclg1953@gmail.com"  
EMAIL_APP_PASSWORD = "dbsjfwyvgxhmesiw"  

yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
GOOGLE_FORM_LINK = "https://forms.gle/9gFxA9iqETyGZFvE9"
# ---------------------------
# Twilio Config
# ---------------------------
TWILIO_SID = 'ACb266e6ac862b4ff8819ad0d4696fe5e5'
TWILIO_AUTH_TOKEN = '9d64a12f5675d4674af5804a06d63e6c'

TWILIO_PHONE = '‪‪‪‪+16592013278‬‬'
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ---------------------------
# Database Connection
# ---------------------------
def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            r'SERVER=AKSHAYASARAB\SQLEXPRESS01;'
            'DATABASE=ak;'
            'Trusted_Connection=yes;'
            'UID=admin;'
            'PWD=1953;'
            
        )
        return conn
    except pyodbc.Error as e:
        print("Database connection failed:", e)
        return None
# ---------------------------
# Login Route
# ---------------------------
@app1_try.route('/')
@app1_try.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "Teacher" and password == "1234":
            return redirect(url_for('container'))
        elif username == "Student" and password == "2023":
            return redirect(url_for('student1'))
        elif username == "Admin" and password == "1953":
            return redirect(url_for('container1'))
        
        elif username == "Parent" and password == "fatima":
            return redirect(url_for('student'))
        else:
            return render_template('login1.html', message="Invalid credentials!")

    return render_template('login1.html')
# ---------------------------
# ---------------------------
# Other Dashboard Routes
# ---------------------------
@app1_try.route('/container')
def container():
    return render_template('container.html')

@app1_try.route('/edit')
def edit():
    return render_template('edit.html')

@app1_try.route('/index')
def index():
    return render_template('index.html')
@app1_try.route('/parent')
def parent():
    return render_template('parent.html')
@app1_try.route('/admin')
def admin():
    return render_template('admin.html')

@app1_try.route('/report')
def rep():
    return render_template('report.html')

@app1_try.route('/login1')
def login1():
    return render_template('login1.html')
@app1_try.route('/graph')
def graph():
    return render_template('graph.html')
@app1_try.route('/parent1')
def parent1():
    return render_template('parent1.html')
@app1_try.route('/container1')
def container1():
    return render_template('container1.html')

#-----------------------------------------------------------------------------------
#-----------Admin Login-----------------
# --------------------------
# Student details (admin)
# --------------------------

@app1_try.route('/stu_det')
def stu_det():
    conn = get_db_connection()
    if not conn:
        return "❌ Database connection failed!"

    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.regno1, s.name1,
               COUNT(a.date) AS total_days,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
               SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_days,
               SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS late_days
        FROM student_reg_crt s
        LEFT JOIN attendance a ON s.regno1 = a.regno1
        GROUP BY s.regno1, s.name1
        ORDER BY s.regno1
    """)

    students = cursor.fetchall()
    conn.close()

    # Ensure the correct variable name is passed
    return render_template("stu_det.html", students=students)

# ---------------------------
# Teacher registration
# ---------------------------
@app1_try.route("/teacher_reg", methods=["GET", "POST"])
def teacher_reg():
    message = None  

    if request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        teacher_name = request.form.get("teacher_name")
        gender = request.form.get("gender")
        department = request.form.get("department")
        email = request.form.get("email")
        phone = request.form.get("phone")
        designation = request.form.get("designation")
        address = request.form.get("address")

        # Validation
        if not teacher_id or not teacher_name:
            message = "⚠ Teacher ID and Name are required!"
        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO Teacher 
                    (TeacherID, TeacherName, Gender, Department, Email, Phone, Designation, Address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (teacher_id, teacher_name, gender, department, email, phone, designation, address))
                conn.commit()
                message = "✅ Teacher details registered successfully!"
            except Exception as e:
                conn.rollback()
                message = f"❌ Error: {e}"
            finally:
                conn.close()

        return render_template("teacher_reg.html", message=message)

    return render_template("teacher_reg.html", message=message)

# --------- Teacher Details ------------

@app1_try.route('/teacher_det')
def teacher_det():
    conn = get_db_connection()
    if not conn:
        return "❌ Database connection failed!"

    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.TeacherID, t.TeacherName, t.Gender, t.Department, t.Designation,
               t.Email, t.Phone, t.Address,
               COUNT(a.date) AS days_marked   -- from attendance
        FROM Teacher t
        LEFT JOIN attendance a ON t.TeacherName = a.TeacherName
        GROUP BY t.TeacherID, t.TeacherName, t.Gender, t.Department, 
                 t.Designation, t.Email, t.Phone, t.Address
        ORDER BY t.TeacherID
    """)

    teachers = cursor.fetchall()
    conn.close()

    return render_template("teacher_det.html", teachers=teachers)

# --------- Manage Attendance -----------

@app1_try.route('/manage_attendance', methods=['GET', 'POST'])
def manage_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()
    records = []
    message = None
    message_type = None   # ✅ success or error
    start_date = ''
    end_date = ''

    if request.method == 'POST':
        # Case 1: Update attendance
        if 'edit_id' in request.form:
            sno = request.form.get('edit_id')
            status = request.form.get('status')
            late_time = request.form.get('late_time') 

            if status != 'Late' or not late_time:
                late_time = '00:00:00.0000000'

            try:
                cursor.execute("""
                    UPDATE attendance
                    SET status = ?, late_time = ?
                    WHERE sno = ?
                """, (status, late_time, sno))
                conn.commit()

                if cursor.rowcount > 0:  # check if any row updated
                    message = "✅ The record has been updated successfully!"
                    message_type = "success"
                else:
                    message = "❌ The record has not updated!"
                    message_type = "error"
            except Exception as e:
                message = f"❌ Error updating record: {str(e)}"
                message_type = "error"

        # Case 2: Filter by date
        elif 'filter' in request.form:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if start_date and end_date:
                query = """
                    SELECT sno, regno1, name1, date, status, late_time, marked_at, TeacherName
                    FROM attendance
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """
                cursor.execute(query, (start_date, end_date))
                records = cursor.fetchall()

    conn.close()
    return render_template(
        'manage_attendance.html',
        records=records,
        message=message,
        message_type=message_type,
        start_date=start_date,   # pass these to template
        end_date=end_date
    )
#------------------------------------------------------------------------------------------------
#-----------Teacher login------------#
# ---------------------------
# Registration
# ---------------------------
@app1_try.route('/register')
def register():
    return render_template("register.html", message="")

@app1_try.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    regno = request.form['regno']
    dept = request.form['dept']
    year = request.form['year']
    blood = request.form['blood']
    phone = request.form['phone']
    email = request.form['email']
    city = request.form['city']
    image = request.files['image']
    image_data = image.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO student_reg_crt
            (name1, regno1, dep1, year1, pic, blood1, phone1, email1, city1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, regno, dept, year, image_data, blood, phone, email, city))
        conn.commit()
        message = "✅ Student details saved successfully!"
    except Exception as e:
        print("Error:", e)
        message = "❌ Failed to save. Check console for error."
    conn.close()

    return render_template("register.html", message=message)
# ---------------------------

#tamil nadu public holidays
# ---------------------------
HOLIDAYS_2025 = {
    "2025-01-01": "New Year's Day",
    "2025-01-14": "Pongal",
    "2025-01-15": "Thiruvalluvar Day",
    "2025-01-16": "Uzhavar Thirunal",
    "2025-01-17": "Pongal Holiday",
    "2025-01-26": "Republic Day",
    "2025-02-11": "Thaipoosam",
    "2025-03-30": "Telugu New Year's Day",
    "2025-03-31": "Ramzan",
    "2025-04-01": "Annual Accounts Closing",
    "2025-04-10": "Mahavir Jayanti",
    "2025-04-14": "Tamil New Year",
    "2025-04-18": "Good Friday",
    "2025-05-01": "May Day",
    "2025-06-07": "Bakrid",
    "2025-07-06": "Muharram",
    "2025-08-15": "Independence Day",
    "2025-08-16": "Krishna Jayanthi",
    "2025-08-27": "Vinayagar Chaturthi",
    "2025-09-05": "Milad-un-Nabi",
    "2025-10-01": "Ayutha Pooja",
    "2025-10-02": "Gandhi Jayanti / Vijaya Dashami",
    "2025-10-20": "Diwali",
    "2025-10-21": "Diwali (Lakshmi Puja)",
    "2025-12-25": "Christmas"
}


# ---------------------------
# Attendance Routes (Mark Attendance)
#---------------------------

@app1_try.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed!"
    
    cursor = conn.cursor()
    today = date.today().strftime("%Y-%m-%d")
    students = get_students()

    # Fetch teachers for dropdown
    cursor.execute("SELECT TeacherName FROM teacher")
    teachers = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        attendance_date = request.form['attendance_date']
        selected_teacher = request.form['teacher_name']
        selected_day = datetime.strptime(attendance_date, "%Y-%m-%d").strftime("%A")

        # --- Validations ---
        if selected_day == "Sunday":
            return render_template("attendance.html", students=students, teachers=teachers, today=today,
                                   message=f"❌ {attendance_date} is Sunday. Attendance cannot be marked.",
                                   submitted=False)

        if attendance_date in HOLIDAYS_2025:
            return render_template("attendance.html", students=students, teachers=teachers, today=today,
                                   message=f"❌ {attendance_date} is a Holiday ({HOLIDAYS_2025[attendance_date]}).",
                                   submitted=False)

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND TeacherName=?",
                       (attendance_date, selected_teacher))
        if cursor.fetchone()[0] > 0:
            return render_template("attendance.html", students=students, teachers=teachers, today=today,
                                   message=f"⚠ Attendance already marked by {selected_teacher} for {attendance_date}!",
                                   submitted=False)

        # --- Insert Attendance ---
        for regno, student_name in students:
            status = request.form.get(f"status_{regno}", "Present")
            late_time = request.form.get(f"late_time_{regno}", None)
                        # Insert into DB
            cursor.execute("""
                INSERT INTO attendance (regno1, name1, date, status, late_time, TeacherName)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (regno, student_name, attendance_date, status, late_time, selected_teacher))


 
        
 
            # --- Notify if absent ---
            if status == "Absent":
                cursor.execute("SELECT phone1, email1 FROM student_reg_crt WHERE regno1=?", (regno,))
                result = cursor.fetchone()
                phone, email = (result[0], result[1]) if result else (None, None)
                 # ---- Send SMS ----
                if phone:
                     phone = phone.strip().replace(" ", "")
                global TWILIO_PHONE
                if TWILIO_PHONE:
                     TWILIO_PHONE = TWILIO_PHONE.strip().replace(" ", "")
                if phone:
                     try: 
                        clean_twilio_phone = TWILIO_PHONE.strip().replace(" ", "") if TWILIO_PHONE else None
                        client.messages.create(
                            body=f"Alert: {student_name} (Reg No: {regno}) was absent on {attendance_date}.",
                            from_=TWILIO_PHONE,
                            to=phone
                        )
                        print(f"✅ SMS sent to {phone} for {student_name}")
                     except Exception as e:
                        print(f"❌ Failed to send SMS to {phone}: {e}")
               

                if email:
                    try:
                        yag.send(
                            to=email,
                            subject=f"Absence Notification: {student_name}",
                            contents=(
                                f"Dear Student,\n\n"
                                f"{student_name} (Reg No: {regno}) was absent on {attendance_date}.\n"
                                f"Please fill out the Leave Reason Form:\n{GOOGLE_FORM_LINK}\n\n"
                                "— Attendance System"
                            )
                        )
                    except Exception as e:
                        print(f"❌ Email error: {e}")

        conn.commit()
        conn.close()
        return redirect(url_for('attendance', submitted="true",
                                message=f"✅ Attendance saved successfully for {selected_teacher}!"))

    # GET request
    conn.close()
    submitted = request.args.get('submitted')
    message = request.args.get('message')
    return render_template("attendance.html", students=students, teachers=teachers, today=today,
                           message=message, submitted=submitted)
def get_students():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT regno1, name1 FROM student_reg_crt")
    students = cursor.fetchall()
    conn.close()
    return students
# ---------------------------
# Student Report
# ---------------------------
conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        r'SERVER=AKSHAYASARAB\SQLEXPRESS01;'
        'DATABASE=ak;'
        'Trusted_Connection=yes;'
)
        
cursor = conn.cursor()

@app1_try.route('/report', methods=['POST'])
def report():
    regno = request.form.get('regno')   # This comes from the form input

    rows = []
    
    photo_base64 = None
    selected_year = request.form.get('year')
    selected_month = request.form.get('month')


    if not selected_year:
        selected_year = "2025"

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT name1, regno1, date, status
        FROM attendance
        WHERE regno1 = ?
    """
    params = [regno]   # ✅ use regno here

    # 🔎 If year/month selected, filter by them
    if selected_year:
        query += " AND YEAR(date) = ?"
        params.append(int(selected_year))
    if selected_month:
        query += " AND MONTH(date) = ?"
        params.append(int(selected_month))

    query += " ORDER BY date"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # fetch student photo
    cursor.execute("SELECT pic FROM student_reg_crt WHERE regno1 = ?", (regno,))
    photo_row = cursor.fetchone()
    if photo_row and photo_row[0]:
        import base64
        photo_base64 = base64.b64encode(photo_row[0]).decode("utf-8")

    conn.close()

    if not rows:
        return render_template("index.html", student=None, records=None, regno=None, photo=None)

    student_name = rows[0][0]   # name
    regno = rows[0][1]          # regno

    total_days = len(rows)
    present_count = sum(1 for r in rows if r[3] == "Present")
    absent_count = sum(1 for r in rows if r[3] == "Absent")
    late_count = sum(1 for r in rows if r[3] == "Late")
    percentage = round((present_count / total_days) * 100, 2) if total_days > 0 else 0
    first_date = rows[0][2]
    last_date = rows[-1][2]

    half = total_days // 2
    show_alert = absent_count >= half

    return render_template("report.html",
                           student=student_name,
                           regno=regno,
                           records=rows,
                           total_days=total_days,
                           present_count=present_count,
                           absent_count=absent_count,
                           late_count=late_count,
                           percentage=percentage,
                           first_date=first_date,
                           last_date=last_date,
                           show_alert=show_alert,
                           photo=photo_base64,
                           selected_year=int(selected_year) if selected_year else None,
                           selected_month=int(selected_month) if selected_month else None)




@app1_try.route('/index', methods=['POST'])
def index_page():
    month_table = []
    date_table = []
    selected_month = None
    selected_date = None

    # Month-wise report (show correct absent counts)
    if request.method == 'POST' and 'month' in request.form:
        selected_month = int(request.form['month'])
        cursor.execute("""
            WITH WorkDays AS (
                SELECT COUNT(DISTINCT date) AS TotalWorking
                FROM attendance
                WHERE MONTH(date) = ? AND YEAR(date) = YEAR(GETDATE())
            )
            SELECT  
                s.name1 AS name, 
                s.regno1 AS regno,
                w.TotalWorking,
                SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS AbsentCount
            FROM student_reg_crt s
            CROSS JOIN WorkDays w
            LEFT JOIN attendance a 
              ON s.regno1 = a.regno1 
             AND MONTH(a.date) = ?
             AND YEAR(a.date) = YEAR(GETDATE())
            GROUP BY s.name1, s.regno1, w.TotalWorking
            HAVING SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) > 0
            ORDER BY s.name1
        """, (selected_month, selected_month))   # tuple params for both ?
        month_table = cursor.fetchall()

    # Date-wise absentees
    # Date-wise absentees
    if request.method == 'POST' and 'date' in request.form:
        selected_date = request.form['date']  # "YYYY-MM-DD"
        
        cursor.execute("""
            SELECT 
                s.name1 AS name,
                s.regno1 AS regno
            FROM student_reg_crt s
            JOIN attendance a 
                ON s.regno1 = a.regno1
            WHERE CONVERT(date, a.date) = ?
              AND a.status = 'Absent'
            ORDER BY s.name1
        """, (selected_date,))
        
        date_table = cursor.fetchall()

    return render_template(
        'index.html',
        month_table=month_table,
        date_table=date_table,
        selected_month=selected_month,
        selected_date=selected_date
    )
#------------------------
#-Leave Reason displaying
#------------------------

from flask import Flask, render_template
import os
import gspread
from google.oauth2.service_account import Credentials



CREDS_PATH = "credentials.json"# <-- change to your path
SPREADSHEET_NAME = "Contact Infromation (Responses) (Responses)"  # <-- change to your sheet name

def get_sheet_records():
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(f"Service account file not found: {CREDS_PATH}")

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=scope)
    client = gspread.authorize(creds)

    # if you prefer using spreadsheet id:
    # sh = client.open_by_key("PUT_YOUR_SHEET_ID_HERE")
    sh = client.open(SPREADSHEET_NAME)
    ws = sh.sheet1
    records = ws.get_all_records()
    return records


@app1_try.route('/leave_report')
def leave_report():
    try:
        rows = get_sheet_records()
        
    except Exception as e:
        return f"<h3>Error</h3><pre>{e}</pre>", 500

    return render_template('leave_report.html', data=rows)







#----------------
#Line Graph
#----------------

@app1_try.route('/linegraph')
def linegraph():
    cursor = conn.cursor()
    
    # Fetch absent count per student
    cursor.execute("""
        SELECT regno1, name1, COUNT(*) AS absent_days
        FROM attendance
        WHERE status = 'Absent'
        GROUP BY regno1, name1
        ORDER BY regno1
    """)
    rows = cursor.fetchall()

    regnos = [row.regno1 for row in rows]
    names = [row.name1 for row in rows]
    absents = [row.absent_days for row in rows]

    # Shorten register numbers for graph and display
    short_regnos = [r[-3:] for r in regnos]

    # Identify highest leave student
    max_index = absents.index(max(absents))
    highest_name = names[max_index]               # name of highest leave
    highest_regno = short_regnos[max_index]       # shortened reg no for display
    highest_value = absents[max_index]

    # Plot graph
    plt.figure(figsize=(12,6)) 
    plt.plot(regnos, absents, marker='o', linestyle='-', linewidth=2)
    plt.scatter([regnos[max_index]], [highest_value], color='red', s=120, label='Highest Leave')
    plt.xlabel("Register Number", fontsize=12)
    plt.ylabel("No. of Leaves Taken", fontsize=12)
    plt.title("Students Leave Record", fontsize=14)
    plt.xticks(rotation=60, fontsize=10)  # horizontal labels
    plt.legend()
    plt.tight_layout() 

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    # Pass all variables to template
    return render_template("linegraph.html",
                           graph_url=graph_url,
                           rows=rows,
                           highest_name=highest_name,
                           highest_regno=highest_regno,
                           highest_value=highest_value)
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# ----------------
# Parent Login
# ----------------
conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        r'SERVER=AKSHAYASARAB\SQLEXPRESS01;'
        'DATABASE=ak;'
        'Trusted_Connection=yes;'
)
        
cursor = conn.cursor()

@app1_try.route('/student', methods=['POST'])
def student():
    regno = request.form.get('regno')   # This comes from the form input

    rows = []
    
    photo_base64 = None
    selected_year = request.form.get('year')
    selected_month = request.form.get('month')


    if not selected_year:
        selected_year = "2025"

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT name1, regno1, date, status
        FROM attendance
        WHERE regno1 = ?
    """
    params = [regno]   # ✅ use regno here

    # 🔎 If year/month selected, filter by them
    if selected_year:
        query += " AND YEAR(date) = ?"
        params.append(int(selected_year))
    if selected_month:
        query += " AND MONTH(date) = ?"
        params.append(int(selected_month))

    query += " ORDER BY date"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # fetch student photo
    cursor.execute("SELECT pic FROM student_reg_crt WHERE regno1 = ?", (regno,))
    photo_row = cursor.fetchone()
    if photo_row and photo_row[0]:
        import base64
        photo_base64 = base64.b64encode(photo_row[0]).decode("utf-8")

    conn.close()

    if not rows:
        return render_template("parent.html", student=None, records=None, regno=None, photo=None)

    student_name = rows[0][0]   # name
    regno = rows[0][1]          # regno

    total_days = len(rows)
    present_count = sum(1 for r in rows if r[3] == "Present")
    absent_count = sum(1 for r in rows if r[3] == "Absent")
    late_count = sum(1 for r in rows if r[3] == "Late")
    percentage = round((present_count / total_days) * 100, 2) if total_days > 0 else 0
    first_date = rows[0][2]
    last_date = rows[-1][2]

    half = total_days // 2
    show_alert = absent_count >= half

    return render_template("student.html",
                           student=student_name,
                           regno=regno,
                           records=rows,
                           total_days=total_days,
                           present_count=present_count,
                           absent_count=absent_count,
                           late_count=late_count,
                           percentage=percentage,
                           first_date=first_date,
                           last_date=last_date,
                           show_alert=show_alert,
                           photo=photo_base64,
                           selected_year=int(selected_year) if selected_year else None,
                           selected_month=int(selected_month) if selected_month else None)


#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------


#--------------
#Student Login
#--------------
@app1_try.route('/student1', methods=["GET", "POST"])
def student1():
    regno = request.form.get('regno')   # This comes from the form input

    rows = []
    
    photo_base64 = None
    selected_year = request.form.get('year')
    selected_month = request.form.get('month')


    if not selected_year:
        selected_year = "2025"

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT name1, regno1, date, status
        FROM attendance
        WHERE regno1 = ?
    """
    params = [regno]   # ✅ use regno here

    # 🔎 If year/month selected, filter by them
    if selected_year:
        query += " AND YEAR(date) = ?"
        params.append(int(selected_year))
    if selected_month:
        query += " AND MONTH(date) = ?"
        params.append(int(selected_month))

    query += " ORDER BY date"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # fetch student photo
    cursor.execute("SELECT pic FROM student_reg_crt WHERE regno1 = ?", (regno,))
    photo_row = cursor.fetchone()
    if photo_row and photo_row[0]:
        import base64
        photo_base64 = base64.b64encode(photo_row[0]).decode("utf-8")

    conn.close()

    if not rows:
        return render_template("parent1.html", student=None, records=None, regno=None, photo=None)

    student_name = rows[0][0]   # name
    regno = rows[0][1]          # regno

    total_days = len(rows)
    present_count = sum(1 for r in rows if r[3] == "Present")
    absent_count = sum(1 for r in rows if r[3] == "Absent")
    late_count = sum(1 for r in rows if r[3] == "Late")
    percentage = round((present_count / total_days) * 100, 2) if total_days > 0 else 0
    first_date = rows[0][2]
    last_date = rows[-1][2]

    half = total_days // 2
    show_alert = absent_count >= half

    return render_template("student1.html",
                           student=student_name,
                           regno=regno,
                           records=rows,
                           total_days=total_days,
                           present_count=present_count,
                           absent_count=absent_count,
                           late_count=late_count,
                           percentage=percentage,
                           first_date=first_date,
                           last_date=last_date,
                           show_alert=show_alert,
                           photo=photo_base64,
                           selected_year=int(selected_year) if selected_year else None,
                           selected_month=int(selected_month) if selected_month else None)




#----------------------------------------------------------------------------------------------


# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == "__main__":
    app1_try.run(debug=True)
