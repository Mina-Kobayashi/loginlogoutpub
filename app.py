from flask import Flask,  render_template,  session, redirect, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime






app = Flask(__name__)
app.secret_key = b'.'


engine = create_engine('postgresql:')



Base = declarative_base()

#message_dataをデータベース(practice)につなげる tableの名前は message
class Msgdata(Base):
    __tablename__ = "message"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(255))
    sesid = Column(String(255))
    date = Column(DateTime(), default=datetime.now)

    def __init__(self,  message, sesid, date):
        self.message = message
        self.sesid = sesid
        self.date = date



class Login(Base):
    __tablename__ = "logindata"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    nameid = Column(String(255))
    pswd = Column(String(255))

    def __init__(self,  nameid, pswd):
        self.nameid = nameid
        self.pswd = pswd



Base.metadata.create_all(engine)



member_data = {}


@app.route('/', methods=['GET'])
def index():

    if 'login' in session and session['login']:
        msg = "Welcome back!" + "　" + session['id']
        Session = sessionmaker(bind=engine)
        ses = Session()
        msgdatas = ses.query(Msgdata).all()
        ses.close()
        return render_template('messages.html', title='Message Page', message=msg, msgdatas=msgdatas)
    else:
        return redirect('/login')

@app.route('/', methods=['POST'])
def form():
    message = request.form.get('comment')
    sesid = session['id']
    date = datetime.now()

    msgdata = Msgdata(message=message, sesid=sesid, date=date)
    Session = sessionmaker(bind=engine)
    ses = Session()
    ses.add(msgdata)
    ses.commit()
    msgdatas = ses.query(Msgdata).all()
    ses.close()
    msg = "Welcome back!" + "　" + session['id']


    return render_template('messages.html', title='Message Page', msgdatas=msgdatas, message=msg)



#login page access
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html', title='Login Page', message='IDとPasswordを入力してね！', id='')

# login form sended.

@app.route('/login', methods=['POST'])
def login_post():
    #member_data辞書を使ってloginlogout処理
    global member_data
    id = request.form.get('id')
    pswd = request.form.get('pass')


    if id in member_data:
        if pswd == member_data[id]:
            session['login'] = True
        else:
            session['login'] = False
    else:
        member_data[id] = pswd
        session['login'] = True
    session['id'] = id

    #DB:practice table:logindata へ　id（nameidとして） pswd(pswd)　をコミット
    logindata = Login(nameid=id, pswd=pswd)
    Session = sessionmaker(bind=engine)
    ses = Session()
    ses.add(logindata)
    ses.commit()
    ses.close()


    if session['login']:
        return redirect('/')
    else:
        return render_template('login.html', title='Login しなおしてね！', message="passwordがちがうよ！", id=id)




#logout

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('id', None)
    session.pop('login')
    return redirect('/login')





if __name__ == '__main__':
    app.run(debug=True)