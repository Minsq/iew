# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import sqlite3

from helpers import login_required, sgd, percent,f_datetime, getStatus # apology
import datetime

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import calendar
import json

# Configure application
app = Flask(__name__)

# Upload files into folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["sgd"] = sgd
app.jinja_env.filters["percent"] = percent
app.jinja_env.filters["f_datetime"] = f_datetime

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

TRANS_TYPE = ["INCOME","EXPENSE"]
CATEGORY = ['ALLOWANCE', 'CLOTHES', 'COURSES','CASHBACK', 'DIGITAL AND STREAMING SVC', 'FOOD & DRINKS',
            'ENTERTAINMENT', 'GROCERIES', 'HOBBY', 'HOME SUPPLIES', 'HOUSING', 'INSURANCE', 'MEDICAL', 'MEMBERSHIPS',
            'TRANSPORT', 'UTILITIES', 'TRAVEL', 'SALARY', 'MISC']
STATUS = ["UPCOMING",'PAID',"CANCELLED"]
# if bank_transfer, ignore

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")
# configure sqlite to use pandas package

# https://stackoverflow.com/questions/33691635/how-to-open-sqlite3-installed-by-python-3

@login_required
@app.route("/")
def index():

    return render_template("index.html")

@app.route("/login", methods = ['GET',"POST"])
def login():
    """log user in"""
    # # Forget any user_id
    session.clear()

    #do i need to forget user id here?
    if request.method == "POST":
        username = request.form.get("username")
        # ensure username was submitted
        if not username:
            flash("Username not valid", "error")
            return redirect("/login")
        # Ensure password was submitted
        ## TODO-add more
        elif not request.form.get("password"):
            flash("Password not valid", "error")
            return redirect("/login")

        username = username.strip()
        # Query database for username - another way to write placeholder is :username instead of ?
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Username or password is incorrect", "error")
            return redirect("/login")
            # return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # flash login successful
        flash('You were successfully logged in')

        # Redirect user to home page
        return redirect("/dashboard")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        ### !! ###


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    #"""Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        print(rows)
        # username is blank or username exists
        if not username or len(rows) > 0:
            flash("Username exists", "error")
            return redirect("/register")

        # password is blank or password < 8 chars
        password = request.form.get("password")
        if not password or len(password) < 8:
            flash("Password is invalid")
            return redirect('/register')

        # check for password matches
        confirm_password = request.form.get("confirmation")
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/register")

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)

        """user may now login"""
        flash('Account created successfully. Please login.')
        return render_template("login.html")



@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method=="GET":
        return render_template("expenses.html", cat = CATEGORY, typ = TRANS_TYPE)
    else:
        button = request.form["submit-button"] #name
        ### 1. add button clicked
        if button == "addButton": #value
            list_of_info = ["trans_date","trans_type","category","item","amount"]
            dict_of_info = {}

            ### check inputs
            for inp in list_of_info:
                dict_of_info[inp] = request.form.get(inp)
                # print(request.form.get(inp))
                # check for non-null values, except for description
                if dict_of_info[inp] == "":
                    flash("Invalid input values found", "error")
                    return redirect("/expenses")

            if dict_of_info['trans_type'] not in TRANS_TYPE or dict_of_info['category'] not in CATEGORY:
                flash("Invalid input values found", "error")
                return redirect("/expenses")

            # print("Before", dict_of_info)
            ### update values
            if dict_of_info['trans_type'] == "INCOME":
                dict_of_info['trans_type'] = 1
                dict_of_info['amount'] = float(dict_of_info['amount']) * 1
            else:
                dict_of_info['trans_type'] = -1
                dict_of_info['amount'] = float(dict_of_info['amount']) * -1

            # print("After", dict_of_info)
            ### add inputs to db
            # db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
            db.execute("INSERT INTO expenses (users_id , date , in_out, category , item , amount) VALUES (?, ?, ?, ?, ?, ?)", session['user_id'], dict_of_info[list_of_info[0]], dict_of_info[list_of_info[1]],
                                                                            dict_of_info[list_of_info[2]], dict_of_info[list_of_info[3]],
                                                                            dict_of_info[list_of_info[4]])

            flash("Transaction added successfully")
            return redirect("/expenses")

        ### 2. upload button clicked
        else:
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

            ### check if file is submitted
            if "file" not in request.files:
                flash("No file submitted", "error")
                return redirect("/expenses")

            file = request.files['file']
            # If filename is empty, return error
            if file.filename == '':
                flash('File needs a name', "error")
                return redirect("/expenses")

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                if df.shape[0] == 0:
                    flash("File has no rows", "error")
                    return redirect("/expenses")

                # append data into db
                list_of_info = ["trans_date","trans_type","category","item","amount"]

                if len(df.columns) != len(list_of_info):
                    flash("Need to provide data in this format: transaction date, transaction type, category, item, amount", "error")
                    return redirect("/expenses")

                df.columns = list_of_info
                df['trans_date'] = pd.to_datetime(df['trans_date']).apply(lambda x: str(x)[:10])
                # print(df.head())
                #capitalize the item col
                df["trans_type"] = df["trans_type"].apply(lambda x: str(x).upper())
                df["category"] = df["category"].apply(lambda x: str(x).upper())
                df["item"] = df["item"].apply(lambda x: str(x).capitalize())

                # check if category are appropriate
                unique_cat = df['category'].unique()
                for u_cat in unique_cat:
                    if u_cat not in CATEGORY:
                        flash(f"You have used a category that is not allowed: {u_cat}", "error")
                        return redirect("/expenses")

                for ind, row in df.iterrows():
                    if row['trans_type'] == "INCOME":
                        row['trans_type'] = 1
                        row['amount'] = float(row['amount']) * 1
                    else:
                        row['trans_type'] = -1
                        row['amount'] = float(row['amount']) * -1

                    db.execute("INSERT INTO expenses (users_id , date , in_out, category , item , amount) VALUES (?, ?, ?, ?, ?, ?)", session['user_id'], row["trans_date"], row["trans_type"],row["category"], row["item"], row["amount"])

                flash("Transactions uploaded successfully")
                return redirect("/history")

            flash("Something happened..", "error")
            return redirect("/expenses")


@app.route("/history")
@app.route('/history/<action>/<item_id>', methods=['GET', 'POST'])
@login_required
def history(action=None, item_id=None):

    if request.method == "POST":
        if action == "delete":

            # delete row
            db.execute("""DELETE FROM expenses WHERE id=?;""", item_id)

            flash("item deleted successfully")

            return redirect(url_for('history'))

    """Show history of transactions"""
    holdings = db.execute("""SELECT *
                            FROM expenses
                            WHERE users_id = ?;""", session['user_id'])
    df = pd.DataFrame(holdings)
    if len(df) == 0:
        holdings = []
    else:
        df['in_out'] = df['in_out'].apply(lambda x: "EXPENSE" if x == -1 else "INCOME")
        df['date'] = pd.to_datetime(df['date'])
        df['date'] =df['date'].dt.date
        df = df.sort_values("date", ascending=False)
        # print(df.head())
        holdings = df.to_dict('records')
        # for holding in holdings:
        #     if holding["in_out"] == -1:
        #         holding["in_out"] = "EXPENSE"
        #     else:
        #         holding["in_out"] = "INCOME"


    return render_template("history.html", transactions=holdings)


@app.route("/dashboard")
@login_required
def dashboard():
### assume default 50 30 20 - NEEDs/WANTs/SAVINGs
    ### BILL REMINDERS ###

    rows_bills = db.execute("SELECT * FROM bills where users_id = ? AND status = ?",session['user_id'],"UPCOMING")
    num_of_bills = len(rows_bills) #number of upcoming payments

    overview = {}
    overview['num_upcoming_bills'] =  num_of_bills
    #default values for displays
    overview["total_upcoming_payment"] = 0
    overview["num_reminder"] =  0
    overview['next_payment_date'] =  '-'
    overview['next_payment_amount'] = 0
    overview['month_spent'] ='-'
    overview['lat_month_expenses'] = 0
    overview['lat_month_expenses_change'] = 0
    overview['month_saved'] = "-"
    overview['amount_saved_overspent'] = 0
    overview['on_track_for_savings']  = '-'

    #default values for graphing
    graphJSON = {}
    graphJSON_expenses = {}

    total_upcoming_payment = 0
    if num_of_bills > 0:

        today = datetime.date.today()
        def getStatus(row):
            reminder = row['reminder'].date()
            deadline = row['deadline'].date()

            if (reminder - today).days <= 0:
                return "REMINDER"
            elif (deadline - today).days < 0:
                return "OVERDUE"
            else:
                return "NOT YET"
        df_bills = pd.DataFrame(rows_bills)

        df_bills['reminder']  = pd.to_datetime(df_bills['reminder'])
        df_bills['deadline']  = pd.to_datetime(df_bills['deadline'])
        df_bills['payment status'] = df_bills.apply(getStatus, axis=1)

        total_upcoming_payment = df_bills['amount'].sum()
        overview["total_upcoming_payment"] = total_upcoming_payment

        # only take those that are reminder/overdue
        # df_bills = df_bills[df_bills['payment status']!="NOT YET"]

        num_reminder = df_bills[df_bills['payment status']=="REMINDER"].shape[0]
        next_payment_date = df_bills['deadline'].min().date()

        overview["num_reminder"] = num_reminder
        overview['next_payment_date'] = datetime.datetime.strftime(next_payment_date, "%d %b %Y")
        print(next_payment_date)

        print(df_bills)
        overview['next_payment_amount'] = df_bills[df_bills['deadline'].astype(str)==str(next_payment_date)]["amount"].sum()



        # print(total_upcoming_payment, next_payment)
        # print(rows_bills)



    ### EXPENSES ###
    rows = db.execute("SELECT * FROM expenses where users_id = ?", session['user_id'])
    # rows

    if len(rows) > 0:

        df = pd.DataFrame(rows)

        ### 1. trend analysis
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(["date"],inplace=True) #ascending=False # from early to later dates

        df['in_out'] = df['in_out'].apply(lambda x: "INCOME" if x == 1 else "EXPENSE")
        df['amount'] = df['amount'].apply(lambda x: abs(x))

        ######################################################################################################
        ################################ OVERVIEW FOR EXPENSES DATA ##########################################
        ######################################################################################################

        df_expenses = df[df['in_out'] == "EXPENSE"]
        if len(df_expenses) > 0:

            df_expenses_month = df_expenses.set_index('date').groupby([pd.Grouper(freq='M')])['amount'].sum().reset_index()
            df_expenses_month.set_index('date',inplace=True)
            # df_expenses_month = df_expenses_month.tail(2)

            df_expenses_month['pct_change'] = df_expenses_month.pct_change()
            df_expenses_month = df_expenses_month.reset_index()

            lat_date_expenses = df_expenses_month.tail(1)["date"].iloc[0].date()
            lat_month_expenses = df_expenses_month.tail(1)["amount"].iloc[0]
            lat_month_expenses_change= df_expenses_month.tail(1)["pct_change"].iloc[0]

            overview['month_spent'] = datetime.datetime.strftime(lat_date_expenses, "%b %Y")
            overview['lat_month_expenses'] = lat_month_expenses
            overview['lat_month_expenses_change'] = lat_month_expenses_change

        ### 3. compare diff btw savings vs expenses and abs amount
        per_month = df.set_index('date').groupby([pd.Grouper(freq='M'),"in_out"])['amount'].sum().reset_index()
        # per_month['difference'] = per_month['expense']

        per_month_compare = per_month.pivot(index='date', columns='in_out', values='amount').reset_index()

        if "INCOME" in per_month_compare.columns:
            #default everyone wants to save 30% of their income
            per_month_compare['Savings'] = 0.3 * per_month_compare['INCOME']
            per_month_compare['Amount Saved/Overspent'] = per_month_compare['Savings']  - per_month_compare['EXPENSE']
            per_month_compare['On track for savings'] =  per_month_compare['Amount Saved/Overspent'].apply(lambda x: "Yes" if x>0 else "No")

            overview['month_saved'] = datetime.datetime.strftime(per_month_compare.tail(1)['date'].iloc[0].date(), "%b %Y")
            overview['amount_saved_overspent'] = per_month_compare.tail(1)['Amount Saved/Overspent'].iloc[0]
            overview['on_track_for_savings']  = per_month_compare.tail(1)['On track for savings'].iloc[0]


        ######################################################################################################
        ################################ CHARTING ############################################################
        ######################################################################################################

        #use the per_month df above
        x = per_month.date
        y = per_month.amount
        # print(per_month)
        # print(x)
        fig = px.bar(per_month, x=x, y=y, color="in_out",barmode='group',
                        color_discrete_map={'INCOME': '#00CC96',
                                                   'EXPENSE': '#EF553B'})
        # print(fig)
        # add buttons
        fig.update_layout(xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"))
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        ### 2. expenses allocation
        # get_expenses = df[df['in_out']=="EXPENSE"]
        # # Use `hole` to create a donut-like pie chart
        # fig_expenses = go.Figure(data=[go.Pie(labels=get_expenses["category"], values=get_expenses['amount'], hole=.3)])
        # graphJSON_expenses = json.dumps(fig_EXPENSEs, cls=plotly.utils.PlotlyJSONEncoder)

        per_month_year = df.set_index('date').groupby([pd.Grouper(freq='M'),"in_out","category"])['amount'].sum().reset_index()
        per_month_year["month_year"] =  per_month_year['date'].apply(lambda x: str(calendar.month_abbr[x.month]) +" "+ str(x.year))

        # get_expenses = per_month_year[per_month_year['in_out']=="EXPENSE"]
        # get_income = per_month_year[per_month_year['in_out']=="INCOME"]


        labels = per_month_year['month_year'].unique().tolist()[::-1]
        # create date for plotting
        dfs = {}
        dfs["All"] = pd.pivot_table(per_month_year,
                                            values='amount',
                                            index=['category'],
                                            columns=['in_out'],
                                            aggfunc=np.sum)

        for label in labels:
            dfs[label]=pd.pivot_table(per_month_year[per_month_year['month_year']==label],
                                            values='amount',
                                            index=['category'],
                                            columns=['in_out'],
                                            aggfunc=np.sum)
        # find row and column unions
        common_cols = []
        common_rows = []
        for key in dfs.keys():
            common_cols = sorted(list(set().union(common_cols,list(dfs[key]))))
            common_rows = sorted(list(set().union(common_rows,list(dfs[key].index))))

        # find dimensionally common dataframe
        df_common = pd.DataFrame(np.nan, index=common_rows, columns=common_cols)

        # reshape each dfs[df] into common dimensions
        dfc={}
        for df_item in dfs: #for each label df_item
            df1 = dfs[df_item].copy()
            s=df_common.combine_first(df1)
            df_reshaped = df1.reindex_like(s)
            ## force INCOME/EXPENSE col if not added
            if "INCOME" not in df_reshaped.columns:
                df_reshaped['INCOME'] = 0
            elif "EXPENSE" not in df_reshaped.columns:
                df_reshaped['EXPENSE'] = 0
            dfc[df_item]=df_reshaped

        # update labels
        labels = ['All'] + labels

        # Create subplots: use 'domain' type for Pie subplot
        fig_pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        fig_pie.add_trace(go.Pie(name="EXPENSE"), 1, 1)
        fig_pie.add_trace(go.Pie(name="INCOME"), 1, 2)
        # fig_pie.add_trace(go.Pie(labels = get_expenses["category"], values = get_expenses['amount'], name="EXPENSE"), 1, 1)
        # fig_pie.add_trace(go.Pie(labels = get_income["category"], values = get_income['amount'], name="INCOME"), 1, 2)

        colors =['aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'purple', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'crimson', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'chartreuse','cyan']

        color_map = dict(zip(CATEGORY,colors))

        # menu setup
        updatemenu= []

        # buttons for menu 1, names
        buttons=[]

        # create traces for each month year and All:
        # build argVals for buttons and create buttons
        for key in dfc.keys(): #for each Month year
            argList = []
            argLabel = []
            for col in dfc[key]:

                #print(dfc[key][col].values)
                argList.append(dfc[key][col].values) #get col values for each color by letter
                argLabel.append(dfc[key].index)
                #get colors
                argColors = np.array([''] * len(dfc[key].index), dtype = object)
                for i in dfc[key].index:
        #             print(i,color_map[i])
                    argColors[np.where(dfc[key].index == i)] = color_map[i]

            #store the data in a list of dictionary
            argVals = [ {'values':argList, 'labels':argLabel, "marker" : {'colors': argColors}}]
        #     print(argVals)
            buttons.append(dict(method='update',
                                label=key,
                                visible=True,
                                args=argVals))
        # some adjustments to the updatemenus into list of dictionaries
        updatemenu=[]
        your_menu=dict()
        updatemenu.append(your_menu)

        updatemenu[0]['buttons']=buttons
        updatemenu[0]['active']=-1 #cannot auto render the 'all' graph
        updatemenu[0]['direction']='down'
        updatemenu[0]['showactive']=True

        fig_pie.update_layout(showlegend=True, updatemenus=updatemenu)
        fig_pie.update_layout(yaxis=dict(range=[0,df['amount'].max()+0.4]))

        # title
        fig_pie.update_layout(
            title=dict(
                text= "<i>Expenses vs Income</i>",
                font={'size':18},
                y=0.9,
                x=0.5,
                xanchor= 'center',
                yanchor= 'top'))

        # button annotations
        # fig_pie.update_layout(
        #     annotations=[
        #         dict(text="<i>Month Year</i>", x=-0.19, xref="paper", y=1.1, yref="paper",
        #             align="left", showarrow=False, font = dict(size=16, color = '#512889')),
        #     ])


        # add annotations and dropdowns
        fig_pie.update_layout(annotations = [ dict(text="<i>Month Year</i>", x=-0.19, xref="paper", y=1.1, yref="paper",
                            align="left", showarrow=False, font = dict(size=16, color = '#512889')),
                     dict(text='EXPENSE', x=0.16, y=0.5, font_size=20, showarrow=False),
                     dict(text='INCOME', x=0.84, y=0.5, font_size=20, showarrow=False)])

        # Use `hole` to create a donut-like pie chart
        fig_pie.update_traces(hole=.3, hoverinfo="label+value+percent+name")

        graphJSON_expenses = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)

    ######################################################################################################
    ################################ render template for dashboard #######################################
    ######################################################################################################

    return render_template("dashboard.html", overview=overview,graphJSON=graphJSON, graphJSON_expenses=graphJSON_expenses)


@app.route("/bills", methods =["POST","GET"])
@app.route('/bills/<action>/<item_id>', methods = ['GET', 'POST'])
@login_required
def bill(action=None, item_id=None):
    if request.method == "POST":
        if action == "delete":

            db.execute("DELETE FROM bills WHERE id = ?", item_id)
            flash("Bill deleted successfully")

        elif action == "paid":
            db.execute("UPDATE bills SET status = ? WHERE id = ?", "PAID", item_id)
            flash("Bill updated successfully")
        else:
            button = request.form["submit-button"]
            if button == "addBills":
                # print("hi")
                list_of_info = ['due_date',"reminder_date",'item','category','status','amount']
                dict_of_info = {}

                ### check inputs
                for inp in list_of_info:
                    dict_of_info[inp] = request.form.get(inp)
                    print(dict_of_info[inp])
                    # print(request.form.get(inp))
                    # check for non-null values, except for description
                    if dict_of_info[inp] == "":
                        flash("Invalid input values found", "error")
                        return redirect("/bills")
                if dict_of_info['status'] not in STATUS or dict_of_info['category'] not in CATEGORY:
                    flash("Invalid input values found", "error")
                    return redirect("/bills")


                db.execute("INSERT INTO bills (users_id, deadline, reminder, details, category, status, amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                                session['user_id'], dict_of_info[list_of_info[0]], dict_of_info[list_of_info[1]],
                                                dict_of_info[list_of_info[2]], dict_of_info[list_of_info[3]],
                                                dict_of_info[list_of_info[4]],dict_of_info[list_of_info[5]])

                flash("Bill reminder added successfully")
        return redirect("/bills")
    else:

        holdings = db.execute("""SELECT *
                            FROM bills
                            WHERE users_id = ?;""", session['user_id'])

        if len(holdings) == 0:
            holdings = []
        else:
            df_bills = pd.DataFrame(holdings)

            df_bills['reminder']  = pd.to_datetime(df_bills['reminder'])
            df_bills['deadline']  = pd.to_datetime(df_bills['deadline'])
            df_bills['payment_status'] = df_bills.apply(getStatus, axis=1)

            holdings = df_bills.to_dict('records')

        return render_template("bill.html", holdings=holdings, cat=CATEGORY)



