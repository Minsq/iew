# from flask_wtf import Form
# from wtforms import TextField, SubmitField, TextAreaField
# from wtforms.validators import Length, Email, Required

from wtforms import Form, BooleanField, StringField, PasswordField, validators

CATEGORY = ['ALLOWANCE', 'CLOTHES', 'COURSES', 'CASHBACK', 'DIGITAL AND STREAMING SVC', 'FOOD & DRINKS',
            'ENTERTAINMENT', 'GROCERIES', 'HOBBY', 'HOME SUPPLIES', 'HOUSING', 'INSURANCE', 'MEDICAL', 'MEMBERSHIPS',
            'TRANSPORT', 'UTILITIES', 'TRAVEL', 'SALARY', 'MISC']
STATUS = ["UPCOMING",'PAID',"CANCELLED"]

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=8, max=20)], render_kw={"placeholder": "Username"})
    # email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ], render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})
    # accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class BillForm(Form):
    details = StringField("Payment details", [validators.DataRequired()], render_kw={"placeholder": "Payment Details"})
    deadline = DateField("Payment due", format='%d/%m/%Y',[validators.DataRequired()])
    reminder = DateField("Set reminder", format='%d/%m/%Y',[validators.DataRequired()])
    category = SelectField('Category', choices=CATEGORY, default=1,[validators.DataRequired()])
    status = SelectField('Status', choices=STATUS, default=1,[validators.DataRequired()])
    amount = DecimalField("Amount",[validators.DataRequired()])