from flask import Flask,render_template,session,request,redirect,url_for,flash
import mysql.connector,hashlib 

mydb = mysql.connector.connect(
  host='localhost',
  user='root',
  password='',
  database = 'PROJECT'
)
mycursor = mydb.cursor(buffered=True)

app = Flask(__name__)

@app.route("/home",methods = ['POST','GET'])
def home():
    if not session.get('login'):
        return render_template('login.html'),401
    else:
        if session.get('isAdmin') :
            return render_template('home.html',username=session.get('username'))
        else :
            return home_student()

@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method=='POST' :
        mycursor.execute("""SELECT * FROM login WHERE username = %s""", (request.form['username'],))
        res = mycursor.fetchall()
        if mycursor.rowcount == 0:
            return home()
        if request.form['password'] != res[0][1]:
            return render_template('login.html')
        else:
            session['login'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            session['isAdmin'] = (request.form['username']=='admin')
            return home()
    return render_template('login.html')

@app.route("/show_update_detail",methods=['POST','GET'])
def show_update_detail():
    if not session.get('login'):
        return redirect( url_for('home') )
    if request.method=='POST':
        if request.form['student_id'] =='':
            return render_template("search_detail.html")

        not_found= False
        mycursor.execute("""Select * from Student Left Join Hostel on Hostel.hostel_id = Student.hostel_id 
                         where student_id = %s""", (request.form['student_id'],))
        res = ()
        warden_list = ()
        warden_found = False
        if mycursor.rowcount > 0:
            res = mycursor.fetchone()
        else:
            not_found = True
        fields = mycursor.column_names
        if not not_found:
            warden_found = True
            warden_list = ()
            try:
                mycursor.execute("Select warden_name from Warden where warden_of = %s", (res[11],))
                warden_list = mycursor.fetchall()
            except:
                warden_found = False
        mycursor.execute("select * from Fines where student_id = %s", (request.form['student_id'],))
        temp = mycursor.fetchone()
        fields = fields + ('fine_amount',)
        if mycursor.rowcount == 0:
            res = res + (0,)
        else:
            res = res + (temp[1],)
        mycursor.execute("Select * from Student where student_id = %s", (request.form['student_id'],))
        upd_res = mycursor.fetchone()
        upd_not_found = False
        upd_fields = mycursor.column_names
        if mycursor.rowcount <= 0:
            upd_not_found = True
        if "show" in request.form:
            return render_template('show_detail.html',res = res,fields = fields, not_found=not_found,warden_list=warden_list,warden_found = warden_found)
        if "update" in request.form:
            return render_template('update_detail.html',res =upd_res,fields = upd_fields, not_found=upd_not_found)
        if "delete" in request.form:
            if not_found:
                return render_template('show_detail.html',res=res,fields=fields,not_found=not_found)
            else:
                mycursor.execute("DELETE FROM Student where student_id = %s", (request.form['student_id'],))
                mydb.commit()
                return render_template("home.html")
        

@app.route("/search_detail",methods = ['POST','GET'])
def search_detail():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('search_detail.html')


@app.route("/add_student",methods = ['POST','GET'])
def add_student():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Student")
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if temp == '':
            temp = None
        val = val + (temp,)

    success = True
    error = False
    try:
        mycursor.execute("""INSERT INTO Student Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", val)
    except:
        print("Error")
        error = True
        success = False 
    mydb.commit()    
    
    return redirect(url_for('add_page', id='student', error=error,success=success))    


@app.route("/add_<id>_page",methods = ['POST','GET'])
def add_page(id):
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from " + id.capitalize()
    mycursor.execute(qry)
    fields = mycursor.column_names

    return render_template('add_page.html',success=request.args.get('success'), error=request.args.get('error'), fields = fields, id= id.encode('ascii','ignore'))

@app.route("/add_room", methods=['POST','GET'])
def add_room():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Room"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()
    for field in fields:
        temp = request.form.get(field)
        if temp == '':
            temp = None
        val = val + (temp,)

    success = True
    error = False
    try:
        mycursor.execute("INSERT INTO Room Values (%s,%s,%s)", val)
    except:
        print("Error : Room not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='room', error=error,success=success))


@app.route("/add_furniture", methods=['POST','GET'])
def add_furniture():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Furniture"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()
    for field in fields:
        temp = request.form.get(field)
        if temp == '':
            temp = None
        val = val + (temp,)

    success = True
    error = False
    try:
        mycursor.execute("INSERT INTO Furniture Values (%s,%s,%s,%s)", val)
    except:
        print("Error : Furniture not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='furniture', error=error,success=success))



@app.route("/add_warden", methods=['POST','GET'])
def add_warden():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Warden"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if temp == '':
            temp = None
        val = val + (temp,)

    success = True
    error = False
    try:
        mycursor.execute("INSERT INTO Warden Values (%s,%s,%s,%s)", val)
    except:
        print("Error : Warden not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='warden', error=error,success=success))


@app.route("/add_hostel", methods=['POST','GET'])
def add_hostel():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Hostel"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()
    for field in fields:
        temp = request.form.get(field)
        if temp == '':
            temp = None
        val = val + (temp,)

    success = True
    error = False
    try:
        mycursor.execute("INSERT INTO Hostel Values (%s,%s)", val)
    except:
        print("Error : Hostel not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='hostel', error=error,success=success))
    

@app.route("/update_details",methods = ['GET','POST'])
def update_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Student")
    fields = mycursor.column_names
    qry = "UPDATE Student SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['student_id','room_no','hostel_id']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE student_id = %s;" %(request.form['student_id'])
    try:
        mycursor.execute(qry)
    except:
        print("update error")
    mydb.commit()
    qry2 = "select * from Student where student_id = %s" %(request.form['student_id'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    return render_template("show_detail.html",res = res,fields=fields,not_found = False)

@app.route("/logout", methods=['POST','GET'])
def logout():
    session['login'] = False
    session['isAdmin'] = False
    return redirect("/login")

@app.route("/search_student_details",methods=['GET','POST'])
def search_student_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Student"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_furniture_details",methods=['GET','POST'])
def search_furniture_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Furniture"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_room_details",methods=['GET','POST'])
def search_room_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Room"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_hostel_details",methods=['GET','POST'])
def search_hostel_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Hostel"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_warden_details",methods=['GET','POST'])
def search_warden_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Warden"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/room_furniture_page", methods=['GET','POST'])
def room_furniture_page():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )
    return render_template('/room_furniture_page.html')

@app.route("/room_furniture", methods=['GET','POST'])
def room_furniture():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )
    qry = "select * from Furniture where hostel_id="+request.form['hostel_id']+" AND room_no="+request.form['room_id']
    mycursor.execute(qry)
    fields = mycursor.column_names
    furniture = mycursor.fetchall()
    
    qry = "select student_id,first_name from Student where hostel_id="+request.form['hostel_id']+" AND room_no="+request.form['room_id']
    print(qry)
    mycursor.execute(qry)
    students = mycursor.fetchall()

    session['fineStu'] = students

    return render_template('/room_furniture.html',fields=fields,furniture=furniture,students=students)

@app.route("/impose_fine", methods=['GET','POST'])
def impose_fine():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )
    students = session.get('fineStu')
    session['fineStu'] = ()
    num = len(students)
    try:
        finePerStu = float(request.form['fine'])//num
    except:
        return redirect( url_for('home') )

    if num==0 or finePerStu==0.0:
        return redirect( url_for('home') )
    
    for student in students:
        mycursor.execute("select fine from Fines where student_id=%s", (student[0],))
        res = mycursor.fetchall()
        if len(res)==0:
            mycursor.execute("insert into Fines values (%s,%s)",(student[0],finePerStu,))
            mydb.commit()
        else:
            mycursor.execute("update Fines set fine=%s where student_id=%s", (res[0][0]+finePerStu, student[0],))
            mydb.commit()

    return redirect( url_for('home') )    

@app.route("/home_student")
def home_student():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "Select * from Student Left Join Hostel on Hostel.hostel_id = Student.hostel_id where student_id = %s" %(session.get('username'))
    print(qry)
    not_found= False
    mycursor.execute(qry)
    res = ()
    warden_list = ()
    warden_found = False
    if mycursor.rowcount > 0:
        res = mycursor.fetchone()
    else:
        not_found = True
    fields = mycursor.column_names
    if not not_found:
        warden_found = True
        warden_list = ()
        try:
            mycursor.execute("Select warden_name from Warden where warden_of = %s", (res[11],))
            warden_list = mycursor.fetchall()
        except:
            warden_found = False

    mycursor.execute("select * from Fines where student_id = %s", (session.get('username'),))
    temp = mycursor.fetchone()
    fields = fields + ('fine_amount',)
    if mycursor.rowcount == 0:
        res = res + (0,)
    else:
        res = res + (temp[1],)
    return render_template('/home_student.html',not_found = not_found, warden_found= warden_found, warden_list = warden_list, res= res,fields = fields)

@app.route('/remove_hostel',methods=['GET','POST'])
def remove_hostel():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_hostel.html')

@app.route('/remove_room',methods=['GET','POST'])
def remove_room():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_room.html')

@app.route('/remove_warden',methods=['GET','POST'])
def remove_warden():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_warden.html')

@app.route('/remove_furniture',methods=['GET','POST'])
def remove_furniture():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_furniture.html')

@app.route('/del_furniture',methods=['GET','POST'])
def del_furniture():
    if not session.get('login'):
        return redirect( url_for('home') )
    try:
        mycursor.execute("delete from Furniture where furniture_id=%s", (request.form['furniture_id'],))
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/del_warden',methods=['GET','POST'])
def del_warden():
    if not session.get('login'):
        return redirect( url_for('home') )
    try:
        mycursor.execute("delete from Warden where warden_id=%s", (request.form['warden_id'],))
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/del_room',methods=['GET','POST'])
def del_room():
    if not session.get('login'):
        return redirect( url_for('home') )
    try:
        mycursor.execute("delete from Room where room_no=%s and hostel_id=%s", (request.form['room_id'], request.form['hostel_id'],))
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/del_hostel',methods=['GET','POST'])
def del_hostel():
    if not session.get('login'):
        return redirect( url_for('home') )
    try:
        mycursor.execute("delete from Hostel where hostel_id=%s",(request.form['hostel_id'],))
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/contact_admin_page',methods=['GET','POST'])
def contact_admin_page():
    print(session.get('isAdmin'))
    if not session.get('login') or session.get('isAdmin'):
        return redirect( url_for('home') )
    return render_template('contact_admin_page.html')

@app.route('/contact_admin',methods=['GET','POST'])
def contact_admin():
    if not session.get('login') or session.get('isAdmin'):
        return redirect( url_for('home') )
    username = session.get('username')
    message = request.form['message']
    
    success = True
    error = False
    try:
        mycursor.execute("insert into Messages (username,message) values (%s,%s)", (username,message,))
    except:
        print("Error")
        error = True
        success = False
    mydb.commit()

    return render_template('contact_admin_page.html',error=error,success=success)


@app.route('/see_messages',methods=['GET','POST'])
def see_messages():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )
    
    qry = "Select * from Messages"
    mycursor.execute(qry)
    msg = mycursor.fetchall()

    return render_template('see_messages.html',msg=msg)

@app.route('/seen_message',methods=['GET','POST'])
def seen_message():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )

    mycursor.execute("delete from Messages where message_id=%s", (request.form['id'],))
    mydb.commit()

    return redirect(url_for('see_messages'))


if __name__ == "__main__":
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
