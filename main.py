from flask import Flask,render_template,session,request,redirect,url_for
import mysql.connector

mydb = mysql.connector.connect(
  host='localhost',
  user='admin',
  password='ifixit',
  database = 'PROJECT'
)
mycursor = mydb.cursor()

app = Flask(__name__)

@app.route("/home",methods = ['POST','GET'])
def home():
    if not session.get('login'):
        return render_template('login.html'),401
    else:
        return render_template('home.html',username=session.get('username'))

@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method=='POST' :
        query = """SELECT * FROM login WHERE username = '%s'""" %(request.form['username'])
        mycursor.execute(query)
        res = mycursor.fetchall()
        if mycursor.rowcount == 0:
            return home()
        if request.form['password'] != res[0][1]:
            return render_template('login.html')
        else:
            session['login'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return redirect(url_for('home',username = session.get('username')))
    return render_template('login.html')

@app.route("/show_update_detail",methods=['POST','GET'])
def show_detail():
    if(request.method=='POST'):
        qry = "SELECT * from Student where student_id = %s" %(request.form['student_id'])
        mycursor.execute(qry)
        not_found = False
        res = mycursor.fetchone()
        print(mycursor.rowcount)
        if mycursor.rowcount == -1:
            not_found = True
        fields = mycursor.column_names

        if "show" in request.form:
            return render_template('show_detail.html',res = res,fields = fields, not_found=not_found)
        if "update" in request.form:
            return render_template('update_detail.html',res = res,fields = fields, not_found=not_found)

@app.route("/search_detail",methods = ['POST','GET'])
def search_detail():
    return render_template('search_detail.html')

@app.route("/logout", methods=['POST','GET'])
def logout():
    session['login'] = False
    return redirect("/login")

if __name__ == "__main__":
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
