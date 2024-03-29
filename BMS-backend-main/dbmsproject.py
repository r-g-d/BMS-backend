
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import and_, or_, not_
import random
import os

app = Flask(__name__)
CORS(app)
#app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/projectdb'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__='users'
    
    UserID=db.Column(db.Integer,primary_key=True)
    Username=db.Column(db.String(80),unique=True,nullable=False)
    Password=db.Column(db.String(120),unique=False,nullable=False)
    Age=db.Column(db.Integer,unique=False)
    Phone=db.Column(db.String(10),unique=False)
        
    def __repr__(self):
        return f"User('{self.Username}')"
    
    
class Admin(db.Model):
    __tablename__='admins'
    
    AdminID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(120),unique=False,nullable=False)
    Password=db.Column(db.String(120),unique=False,nullable=False)
    
    def __repr__(self):
        return f"Admin('{self.Name}')"
    
    
class Account(db.Model):
    __tablename__='accounts'
    
    AccountNo=db.Column(db.Integer,primary_key=True)
    Type=db.Column(db.String(20),unique=False,nullable=False)
    Balance=db.Column(db.Integer,unique=False,nullable=False,default=0)
    UID=db.Column(db.Integer,db.ForeignKey('users.UserID'),unique=False,nullable=False)
    
    def __repr__(self):
        return f"Account('{self.AccountNo}')"
    
    
class Transaction(db.Model):
    __tablename__='transactions'
    
    
    
    TransactionID=db.Column(db.Integer,primary_key=True)
    FromAccount=db.Column(db.Integer,unique=False,nullable=False)
    ToAccount=db.Column(db.Integer,unique=False,nullable=False)
    AdminID=db.Column(db.Integer,db.ForeignKey('admins.AdminID'),unique=False,default=0)
    Type=db.Column(db.String(20),unique=False,nullable=False)
    Amount=db.Column(db.Integer,unique=False,nullable=False)
    Date=db.Column(db.String(30))
    
    def __repr__(self):
        return f"Transaction('{self.TransactionID}')"
    
    
class LoanRequest(db.Model):
    __tablename__='loanrequest'
    
    UserID=db.Column(db.Integer,db.ForeignKey('users.UserID'),primary_key=True)
    Amount=db.Column(db.Integer,unique=False,nullable=False)
    Duration=db.Column(db.Integer,unique=False,nullable=False)
    FixedAmount=db.Column(db.Float,unique=False,nullable=False)
    Admin=db.Column(db.Integer,db.ForeignKey('admins.AdminID'),unique=False,nullable=False)
    Account=db.Column(db.Integer,unique=False,nullable=False)
    
    def __repr__(self):
        return f"LoanRequest('{self.User}')"
    
    
class Loan(db.Model):
    __tablename__='loans' 
    
    LoanID=db.Column(db.Integer,primary_key=True)
    AmountRemaining=db.Column(db.Float,unique=False,nullable=False)
    TotalAmount=db.Column(db.Integer,unique=False,nullable=False)
    FixedAmount=db.Column(db.Float,unique=False,nullable=False)
    PaymentsRemaining=db.Column(db.Integer,unique=False,nullable=False)
    UserID=db.Column(db.Integer,nullable=False,unique=False)
    StartDate=db.Column(db.DateTime,default=datetime.utcnow)
    Status=db.Column(db.String(12),default='Active')
    
    def __repr__(self):
        return f"Loan('{self.LoanID}')"
    
    
from flask import request, jsonify


# User Login route
@app.route('/api/userlogin', methods=['POST'])
def userlogin():
    data = request.get_json()
    user = User.query.filter_by(UserID=data['UserID']).first()
    if not user:
        return jsonify({'message':'User Does Not Exist'}),401
    if data['Password']!=user.Password:
        return jsonify({'message':'Invalid Credentials'}),401
    accdetails=Account.query.filter_by(UID=data['UserID']).all()
    ser_acc = [makearray_account(account) for account in accdetails]
    loanaccdetails=Account.query.filter(and_(Account.UID==data['UserID'],Account.Type=='Loan')).all()
    ser_loan=[makearray_loan(loanaccount) for loanaccount in loanaccdetails]
    if user and user.Password == data['Password']:
        return jsonify({'AccountNo':ser_acc ,'LoanAccountNo':ser_loan})
    return jsonify({'Accountno':[]}),401

# #User Account list Route
# @app.route('/api/useraccounts', methods=['GET'])
# def useraccounts():
#     data = request.args.get('UserID')
#     accdetails=Account.query.filter_by(UID=data).all()
#     ser_acc = [makearray_account(account) for account in accdetails]
#     if ser_acc:
#         return jsonify({'Accounts':ser_acc}),201
#     return jsonify({'Accounts':[]}),201    

# Admin Login route
@app.route('/api/adminlogin', methods=['POST'])
def adminlogin():
    data = request.get_json()
    admin = Admin.query.filter_by(AdminID=data['AdminID']).first()
    if not admin:
        return jsonify({'message':'Admin Does Not Exist'}),401
    if data['Password']!=admin.Password:
        return jsonify({'message':'Invalid Credentials'}),401
    # if admin and admin.Password == data['Password']:
    #     return jsonify({'message': 'Login successful', 'AdminID': admin.AdminID})
    # return jsonify({'message': 'Invalid username or password'}), 401
    loanaccdetails=Account.query.filter_by(Type='Loan').all()
    ser_loan=[makearray_loan(loanaccount) for loanaccount in loanaccdetails]
    if admin and admin.Password == data['Password']:
        return jsonify({'LoanAccountNo':ser_loan}),201


#User Details Route
@app.route('/api/userdetails', methods=['GET'])
def userdetails():
    data = request.args.get('UserID')
    udetails = User.query.filter_by(UserID=data).first()
    ser_det= {'UserID':udetails.UserID,'Name':udetails.Username,'Age':udetails.Age,'Phone':udetails.Phone}
    accdetails=Account.query.filter_by(UID=data).all()
    ser_acc = [serialize_account(account) for account in accdetails]
    return jsonify({'Userdetails':ser_det},{'Accounts':ser_acc}),201



#Admin Details Route
@app.route('/api/admindetails', methods=['GET'])
def admindetails():
    data = request.args.get('AdminID')
    admindetails = Admin.query.filter_by(AdminID=data).first()
    ser_det= {'AdminID':admindetails.AdminID,'Name':admindetails.Name}
    return jsonify({'Admindetails':ser_det}),201


#Logout
@app.route('/api/logout',methods=['GET'])
def logout():
    return jsonify({'message':'logged out'}),200




#Transaction History Route
@app.route('/api/transactions',methods=['GET'])
def transactions():
    data=request.args.get('AccountNo')
    if data =='...' or data is None:
        return jsonify({'Transactions':[{'Amount':'...'}]}),201
    from_trans=Transaction.query.filter_by(FromAccount=data).all()
    to_trans=Transaction.query.filter_by(ToAccount=data).all()
    ser_trans_from=[serialize_transaction(transaction) for transaction in from_trans]
    ser_trans_to=[serialize_transaction(transaction) for transaction in to_trans]
    ser_trans_from.extend(ser_trans_to)
    
    ser_trans_from.sort(key=sortfunc)
    if(from_trans or to_trans):
        return jsonify({'Transactions':ser_trans_from})
    return jsonify({'Transactions':[]}),201



#Loan History Route
@app.route('/api/loanhistory',methods=['GET'])
def loanhistory():
    data=request.args.get('LoanID')
    if data is None or data =='...':
        return jsonify({'Loans':[{'TotalAmount':'...'}]}),201
    loans=Loan.query.filter_by(LoanID=data).all()
    
    ser_loans=[serialize_loan(loan) for loan in loans]
    
    if(loans):
        return jsonify({'Loans':ser_loans}),201
    return jsonify({[]}),


# #Admin Loan History Route
# @app.route('/api/adminloanhistory',methods=['GET'])
# def adminloanhistory():
#     data=request .ars.get('LoanID')
    
#     loan=Loan.query.filter_by(LoanID=data).first()
    
#     if not loan:
#         return jsonify({'message':'Invalid LoanID'}),401
    
#     details={'UserID':loan.UserID,'TotalAmount':loan.TotalAmount,'FixedAmount':loan.FixedAmount,'PaymentsRemaining':loan.PaymentsRemaining,
#              'LoanID':loan.LoanID,'Status':loan.Status,'AmountRemaining':loan.AmountRemaining,'StartDate':loan.StartDate}
    
#     return jsonify({'details':details}),201



#User Transaction Payment Route
@app.route('/api/userpayment',methods=['POST'])
def userpayment():
        data = request.get_json()
        fromacc=Account.query.filter_by(AccountNo=data['FromAccount']).first()
        toacc=Account.query.filter_by(AccountNo=data['ToAccount']).first()
        
        if fromacc==None or toacc==None:
            return jsonify({'message':'Invalid Account Number'}),404
        
        amount=data['Amount']
        balance=fromacc.Balance
    
        if int(amount)>balance:
            return jsonify({'message':'Insufficient Balance'}),404
        
        tid=random.randint(100000,900000)
        
        flag=Account.query.filter_by(AccountNo=tid).first()
        
        while(flag):
            tid=random.randint(100000,900000)
            flag=Account.query.filter_by(AccountNo=tid).first()
            
        
        now=str(datetime.now().replace(second=0,microsecond=0))
        print(now)
        trans=Transaction(
                                TransactionID=tid,
                                FromAccount=data['FromAccount'],
                                ToAccount=data['ToAccount'],
                                AdminID=1,
                                Type='Saving',
                                Amount=data['Amount'],
                                Date=now
                         )
        
        db.session.add(trans)
        db.session.commit()
        
        fromacc.Balance=fromacc.Balance-int(amount)
        db.session.commit()
        toacc.Balance=toacc.Balance+int(amount)
        db.session.commit()
        
        return jsonify({'message':'Transaction Complete'}),200


#Admin Transaction Payment Route
@app.route('/api/adminpayment',methods=['POST'])
def adminpayment():
        data = request.get_json()
        fromacc=Account.query.filter_by(AccountNo=data['FromAccount']).first()
        toacc=Account.query.filter_by(AccountNo=data['Toaccount']).first()
        
        if fromacc==None or toacc==None:
            return jsonify({'message':'Invalid Account Number'}),404
        
        amount=data['Amount']
        admin=data['AdminID']
        balance=fromacc.Balance
        
    
        if amount>balance:
            return jsonify({'message':'Insufficient Balance'}),404
        
        tid=random.randint(100000,900000)
        
        flag=Account.query.filter_by(AccountNo=tid).first()
        
        while(flag):
            tid=random.randint(100000,900000)
            flag=Account.query.filter_by(AccountNo=tid).first()
            
        
        now=str(datetime.now().replace(second=0,microsecond=0))
        print(now)
        trans=Transaction(
                                TransactionID=tid,
                                FromAccount=data['FromAccount'],
                                Toaccount=data['ToAccount'],
                                AdminID=admin,
                                Type=data['Type'],
                                Amount=data['Amount'],
                                Date=now
                         )
        
        db.session.add(trans)
        db.session.commit()
        
        fromacc.Balance=fromacc.Balance-amount
        db.session.commit()
        toacc.Balance=toacc.Balance+amount
        db.session.commit()
        
        return jsonify({'message':'Transaction Complete'}),200


#Check User Details Route
@app.route('/api/checkuser',methods=['GET'])
def checkuser():  
    data=request.args.get('UserID')
    useracc= User.query.filter_by(UserID=data).first()
    
    if not useracc:
        return jsonify({'message':'User Not Found'}),404
    
    ser_det= {'UserID':useracc.UserID,'Name':useracc.Username,'Age':useracc.Age,'Phone':useracc.Phone}
    accdetails=Account.query.filter_by(UID=data).all()
    ser_acc = [serialize_account(account) for account in accdetails]
    return jsonify({'Userdetails':ser_det}),201


#Create User Route 
@app.route('/api/createuser',methods=['POST'])
def createuser():
        data = request.get_json()
        
        #uid=random.randint(100000,900000)
        
        uflag=User.query.filter_by(UserID=data['UserID']).first()
        aflag=Account.query.filter_by(AccountNo=data['AccountNo']).first()
        
        if uflag:
            return jsonify({'message':'UserID Already Exists'}),401
        if aflag:
            return jsonify({'message':'Account Number Already Exists'}),401
        
        newuser=User(
                                UserID=data['UserID'],
                                Username=data['Username'],
                                Password=data['Password'],
                                Age=data['Age'],
                                Phone=data['Phone']
                         )
        
        db.session.add(newuser)
        db.session.commit()
        
        newacc=Account(
                                AccountNo=data['AccountNo'],
                                Type=data['Type'],
                                Balance=0,
                                UID=data['UserID']
        )
        
        db.session.add(newacc)
        db.session.commit()
        


        return jsonify({'message':'User Created Successfully'}),200
    
 
    
#Delete User Route
@app.route('/api/deleteuser',methods=['POST'])
def deleteuser():
        data = request.get_json()
        
        uid=User.query.filter_by(UserID=data['UserID']).first()
        
        if not uid:
            return jsonify({'message':'User Not Found'}),401
        
        loans=Loan.query.filter_by(User=data['UserID']).all()
        
        if loans:
            return jsonify({'message':'User has unclosed Loans.Failed to delete user'}),401

        accdetails=Account.query.filter_by(UID=data['UserID']).all()
        for account in accdetails:
            db.session.delete(account)
            db.session.commit()
            
        db.session.delete(uid)
        db.session.commit()
        
        return jsonify({'message':'User and their accounts deleted successfully'}),200
    
    
#Withdraw Route
@app.route('/api/withdraw',methods=['POST'])
def withdraw():
    data = request.get_json()
    
    acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
    
    if not acc:
        return jsonify({'message':'Invalid Account Number'}),403
    
    if int(data['Amount'])>acc.Balance:
        return jsonify({'message':'Insufficient Balance'}),403
    
    acc.Balance=acc.Balance-int(data['Amount'])
    db.session.commit()
    
    return jsonify({'message':'Withdrawal Successful'}),201


#Deposit Route
@app.route('/api/deposit',methods=['POST'])
def deposit():
    data = request.get_json()
    
    acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
    
    if not acc:
        return jsonify({'message':'Invalid Account Number'}),401
    
    acc.Balance=acc.Balance+int(data['Amount'])
    db.session.commit()
    
    return jsonify({'message':'Deposit Successful'}),201


#Loan Apply Route
@app.route('/api/loanapply',methods=['POST'])
def loanapply():
    data = request.get_json()
    
    uid=LoanRequest.query.filter_by(UserID=data['UserID']).first()
    
    if uid:
        return jsonify({'message':'User has a pending loan request'}),401
    
    acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
    
    if int(acc.UID)!=int(data['UserID']):
        return jsonify({'message':'Account Number not of Current User'}),401
    
    req = LoanRequest(
                            UserID=data['UserID'],
                            Amount=data['TotalAmount'],
                            Duration=data['NumberofPayments'],
                            FixedAmount=data['FixedAmount'],
                            Admin=0,
                            Account=data['AccountNo']       
                    )
    
    db.session.add(req)
    db.session.commit()
    
    return jsonify({'message':'Loan Application Submitted'}),201


#Loan Approve Route
@app.route('/api/loanapprove',methods=['POST','GET'])
def loanapprove():
    
    if request.method=='GET':
        requests=LoanRequest.query.all()
        if requests is None:
            return jsonify({}),201
        ser_reqs=[serialize_request(req) for req in requests]
        return jsonify({'requests':ser_reqs}),201
    
    if request.method=='POST':
        data = request.get_json()
        
        if data['Reply']=='No':
            loanreq=LoanRequest.query.filter_by(UserID=data['UserID']).first()
            db.session.delete(loanreq)
            db.session.commit()
            return jsonify({'message':'Loan Request Rejected'}),201
        
        if data['Reply']=='Yes':
            
            loanid=random.randint(100000,900000)
            
            flag=Loan.query.filter_by(LoanID=loanid).first()
            
            while flag:
                 loanid=random.randint(100000,900000)
                 flag=Loan.query.filter_by(LoanID=loanid).first()
                 
            now=str(datetime.now().replace(second=0,microsecond=0))
            
            newloan=Loan(
                            LoanID=loanid,
                            AmountRemaining=data['AmountRemaining'],
                            TotalAmount=data['TotalAmount'],
                            FixedAmount=data['FixedAmount'],
                            PaymentsRemaining=data['PaymentsRemaining'],
                            UserID=data['UserID'],
                            StartDate=now,
                            Status='Active'
                        )
            
            db.session.add(newloan)
            db.session.commit()
            
            acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
            acc.Balance=acc.Balance + data['TotalAmount']
            db.session.commit()
            
            loanreq=LoanRequest.query.filter_by(UserID=data['UserID']).first()
            db.session.delete(loanreq)
            db.session.commit()
            
            return jsonify({'message':'Loan Approved Successfully'}),201
        
        
        
        
#User Pay Loan Route
@app.route('/api/userpayloan',methods=['GET','POST'])
def userpayloan():  
    
    if request.method=='GET':
        
        uid=request.args.get('UserID')
        lid=request.args.get('LoanID')
        
        
        
        flags=Loan.query.filter_by(UserID=uid).all()
        if not flags:
            return jsonify({'message':'User Has No Active Loans'}),401
        print(lid)
        found=0
        print("hi")
        for items in flags:
            print(items.LoanID)
            if items.LoanID==int(lid):
                found=1
                loan=items
                break
            
        
        if found==0:
            return jsonify({'message':'LoanID Not Associated with Current User'}),401
        
        if loan:
        
            ser_loan={'LoanID':loan.LoanID,'TotalAmount':loan.TotalAmount,'FixedAmount':loan.FixedAmount,'PaymentsRemaining':loan.PaymentsRemaining,'Status':loan.Status}
            if loan.Status=='Closed' or loan.PaymentsRemaining==0:
                return jsonify({'Loan':ser_loan,'message':'Loan Already Closed'}),201
            
            return jsonify({'Loan':ser_loan}),201
        
        
    if request.method=='POST':
        data = request.get_json()
        
        acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
        
        if acc.UID!=int(data['UserID']):
            return jsonify({'message':'Account does not belong to current User'}),401
        
        
        if acc.Balance<int(data['FixedAmount']):
            return jsonify({'message':'Account has Insufficient Balance'}),401
        
        loan=Loan.query.filter_by(LoanID=data['LoanID']).first()
        
        if loan.PaymentsRemaining<1:
            return jsonify({'message':'Loan Already Closed'}),401
        
        acc.Balance=acc.Balance-int(data['FixedAmount'])
        db.session.commit()
        
        loan.AmountRemaining=loan.AmountRemaining-int(data['FixedAmount'])
        db.session.commit()
        loan.PaymentsRemaining=loan.PaymentsRemaining-1
        db.session.commit()
        if loan.PaymentsRemaining<=0:
            loan.Status='Closed'
            db.session.commit()
            
        if loan.Status=='Closed':
            return jsonify({'message':'Loan Payment Successful.Loan Closed'}),201
        
        return jsonify({'message':'Loan Payment Successful'}),201
    
    
    
#Admin Pay Loan Route
@app.route('/api/adminpayloan',methods=['GET','POST'])
def adminpayloan():  
    
    if request.method=='GET':
        
        #uid=request.args.get('UserID')
        lid=request.args.get('LoanID')
        
        # flags=Loan.query.filter_by(UserID=uid).all()
        # if not flags:
        #     return jsonify({'message':'User Has No Active Loans'}),401
        # print(lid)
        # found=0
        # print("hi")
        # for items in flags:
        #     print(items.LoanID)
        #     if items.LoanID==int(lid):
        #         found=1
        #         loan=items
        #         break
        
        # if found==0:
        #     return jsonify({'message':'LoanID Not Associated with Current User'}),401
        
        loan=Loan.query.filter_by(LoanID=lid).first()
        
        if not loan:
            return jsonify({'message':'Inavlid LoanID'}),401

        
        ser_loan={'LoanID':loan.LoanID,'TotalAmount':loan.TotalAmount,'FixedAmount':loan.FixedAmount,'PaymentsRemaining':loan.PaymentsRemaining,'Status':loan.Status}
        if loan.Status=='Closed' or loan.PaymentsRemaining==0:
            return jsonify({'Loan':ser_loan,'message':'Loan Already Closed'}),201
            
        return jsonify({'Loan':ser_loan}),201
        
        
    if request.method=='POST':
        data = request.get_json()
        
        acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
        
        # if acc.UID!=int(data['UserID']):
        #     return jsonify({'message':'Account does not belong to current User'}),401
        
        
        if acc.Balance<int(data['FixedAmount']):
            return jsonify({'message':'Account has Insufficient Balance'}),401
        
        loan=Loan.query.filter_by(LoanID=data['LoanID']).first()
        
        if loan.PaymentsRemaining<1:
            return jsonify({'message':'Loan Already Closed'}),401
        
        acc.Balance=acc.Balance-int(data['FixedAmount'])
        db.session.commit()
        
        loan.AmountRemaining=loan.AmountRemaining-int(data['FixedAmount'])
        db.session.commit()
        loan.PaymentsRemaining=loan.PaymentsRemaining-1
        db.session.commit()
        if loan.PaymentsRemaining<=0:
            loan.Status='Closed'
            db.session.commit()
            
        if loan.Status=='Closed':
            return jsonify({'message':'Loan Payment Successful.Loan Closed'}),201
        
        return jsonify({'message':'Loan Payment Successful'}),201
    
    
    
#Create Admin Route
@app.route('/api/createadmin',methods=['POST'])
def createadmin(): 
    data = request.get_json()
    
    if data['MasterKey']!='1029384756':
        return jsonify({'message':'Inavlid Master Key'}),401
    
    flag=Admin.query.filter_by(AdminID=data['AdminID']).first()
    
    if flag:
        return jsonify({'message':'Given AdminID already exists'}),401
    
    newadmin=Admin(
                        Name=data['Name'],
                        AdminID=data['AdminID'],
                        Password=data['Password']
                  )
    
    db.session.add(newadmin)
    db.session.commit()
    
    return jsonify({'message':'New Admin Created Successfully'}),201


#Create Account Route
@app.route('/api/createaccount',methods=['POST'])
def createaccount():
    data = request.get_json()
    
    user=User.query.filter_by(UserID=data['UserID']).first()
    acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
    
    if not user:
        return jsonify({'message':'Given UserID does not exist'}),401
    
    if acc:
        return jsonify({'message':'Given Account Number already exists'}),401
        
    
    newacc=Account(
                        AccountNo=data['AccountNo'],
                        Type=data['Type'],
                        Balance=0,
                        UID=data['UserID']
    )
    
    db.session.add(newacc)
    db.session.commit()
    
    return jsonify({'message':'Account Created Successfully'}),201




#Close Account Route
@app.route('/api/closeaccount',methods=['POST'])
def closeaccount():
    data = request.get_json()
    
    acc=Account.query.filter_by(AccountNo=data['AccountNo']).first()
    
    if not acc:
        return jsonify({'message':'Account Does Not Exist'}),401
    
    db.session.delete(acc)
    db.session.commit()
    
    return jsonify({'messsage':'Account Closed Successfully'}),201
    
    

def serialize_account(account):
    return {
                'AccountNo':account.AccountNo,
                'Type':account.Type,
                'Balance':account.Balance       
            }

def makearray_account(account):
    return account.AccountNo

def makearray_loan(account):
    return account.AccountNo    
    
def serialize_transaction(trans):
    return {
                'TransactionID':trans.TransactionID,
                'FromAccount':trans.FromAccount,
                'ToAccount':trans.ToAccount,
                'Type':trans.Type,
                'Amount':trans.Amount,
                'Date':trans.Date
    }
    
def serialize_loan(loan):
    return {
                'LoanID':loan.LoanID,
                'AmountRemaining':loan.AmountRemaining,
                'TotalAmount':loan.TotalAmount,
                'FixedAmount':loan.FixedAmount,
                'PaymentsRemaining':loan.PaymentsRemaining,
                'UserID':loan.UserID,
                'StartDate':loan.StartDate,
                'Status':loan.Status
    }
    
def serialize_request(req):
    return {
                'UserID':req.UserID,
                'Amount':req.Amount,
                'Duration':req.Duration,
                'FixedAmount':req.FixedAmount,
                'Admin':req.Admin,
                'Account':req.Account
    }
    
def sortfunc(x):
    return{
           x['Date']
    }



@app.route('/')
def index():
    return "<h1 style='color : red'>hello world</h1>"

def initialize_database():
    with app.app_context():
        try:
            db.create_all()
            def_admin = Admin(AdminID='007', Name='Master', Password='password')
            db.session.add(def_admin)
            db.session.commit()
            print("Database initialized.")
        except Exception as e:
            print(f"An error occurred while initializing the database: {e}")
            


if __name__=="__main__":
    initialize_database()
    app.run()
    