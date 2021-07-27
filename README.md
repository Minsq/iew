# IEW - Ink.Eat.Wonder application
#### Video Demo: https://youtu.be/s_citLk3m4I
#### Description: Level up your personal finance by tracking your expenses and paying your bills on time!

## Background
Have been lazy to populate an excel spreadsheet of all the transactions daily and decided to turn that into a coding exercise for more motivation.

In this app, I started developing two main features that I thought was important to me:
1. tracking expenses so that I know where my money goes to every month and
2. scheduling bill payments for things such as maintenance fees, insurance policies, credit card bills etc.


## Tools and frameworks
- Python
    - [Flask](https://flask.palletsprojects.com/en/2.0.x/) for backend
    - [Plotly](https://plotly.com/) for visualizing charts
- SQL
    - [SQLite](https://www.sqlite.org/index.html)
- Javascript/JQuery
- [Bootstrap](https://getbootstrap.com/)

## Usage
This code for this project is divided into 3 parts:
1. Dashboard
2. Keep tabs on income and expenses
3. Schedule bill payments

### Dashboard (dashboard.html)

Provides an overview of when you need to pay your bills and the amount. It also tells you how much you have spent compared to the past month. The same goes for savings.

Over time, you will be able to see a month-on-month comparison between your expenses and income, to know if you're spending more than what you have earned.

Have also include an allocation chart for expenses and income respectively, to understand areas in which you may want to cut down to save up and/or track your sources of income from different avenues.

#### Design considerations
On the visualization aspect, I used the Plotly library instead of Dash (which is also by Plotly).
This allows me to separate the frontend and backend code as the dash framework required the interactive components (dropdowns, html template, etc) to be created in the .py file, which I thought would be confusing.
Hence, to reduce complexity of configuring my the dash app to start within the flask app, I used Plotly, to directly make use of its interactive graphing features.
I ran into a few issues initially, such as having to configure the month-year dropdowns to correctly pull out the relevant data or getting the color of each category to be the same across the different months, which would not be the case if I were to use paid tools like Tableau (oops).
Was happy to learn how to put all the components together :).


### Bill tab (bill.html)

Never forget to pay your bills anymore.

Set up reminders for your payments in advance so that you will know when to pay them. Once you have paid them, don't forget to update them in the setting.

### Expenses tab (expenses.html)

As easy as ABC, input your income and expenditure as your day goes.

You may also upload past transactions using excel for ease of use.


### History tab (history.html)

View all past transactions - both income and expenses in one page. Keep it as a ledger and remember what you have paid for and for what price.

Remember to compare prices and see if you can get a better deal. Save small along the way and it adds up!


#### Design considerations for editing the Expenses and Bill items
Wanted to use AJAX to allow users to edit any incorrect items that they have put through the system. But ran into a few issues.
Therefore, I continued using form action mechanism as a low hanging fruit since it would suffice for specific actions (e.g. "delete" the item or change to "paid" for completed payments).
I will improve by converting this mechanism to AJAX going forward.

## Contact
Feel free to contact me at minsq.ng@gmail.com for any suggestions/improvements :)

Happy coding!!
