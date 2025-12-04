from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, ExpenseForm, BudgetForm
from app.models import User, Expense, Category, Budget
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from datetime import datetime
import csv
from io import StringIO

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/dashboard")
@login_required
def dashboard():
    # Total spending per month (current month)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    total_spending = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.extract('month', Expense.date) == current_month,
        func.extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    # Calculate total budget for current month
    total_budget = db.session.query(func.sum(Budget.amount)).filter(
        Budget.user_id == current_user.id,
        Budget.month == current_month,
        Budget.year == current_year
    ).scalar() or 0
    
    # Compare spending vs budget per category
    categories = Category.query.all()
    budget_vs_spending = []
    
    for category in categories:
        spending = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == category.id,
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=category.id,
            month=current_month,
            year=current_year
        ).first()
        
        budget_amount = budget.amount if budget else 0
        remaining = budget_amount - spending
        
        # Calculate percentage used
        percent_used = (spending / budget_amount * 100) if budget_amount > 0 else 0
        
        # Alerts: Over budget or 90%+ used
        alert = budget_amount > 0 and spending > budget_amount
        warning = budget_amount > 0 and not alert and percent_used >= 90
        
        budget_vs_spending.append({
            'category': category.name,
            'spending': spending,
            'budget': budget_amount,
            'remaining': remaining,
            'percent_used': percent_used,
            'alert': alert,
            'warning': warning
        })

    return render_template('dashboard.html', title='Dashboard', 
                           total_spending=total_spending,
                           total_budget=total_budget,
                           budget_vs_spending=budget_vs_spending,
                           current_month_name=datetime.now().strftime('%B'),
                           current_year=current_year)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route("/expenses", methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    # Set default value for date
    if request.method == 'GET':
        form.date.data = datetime.now().date()
    
    if form.validate_on_submit():
        expense = Expense(amount=form.amount.data, 
                          category_id=form.category.data, 
                          description=form.description.data, 
                          date=form.date.data, 
                          author=current_user)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added!', 'success')
        return redirect(url_for('main.expenses'))
        
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).paginate(page=page, per_page=5)
    return render_template('expenses.html', title='Expenses', form=form, expenses=expenses)

@main.route("/budgets", methods=['GET', 'POST'])
@login_required
def budgets():
    form = BudgetForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    # Set default values for month and year
    if request.method == 'GET':
        form.month.data = datetime.now().month
        form.year.data = datetime.now().year
    
    if form.validate_on_submit():
        # Check if budget exists, update if so
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category.data,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_budget:
            existing_budget.amount = form.amount.data
            flash('Budget updated!', 'info')
        else:
            budget = Budget(amount=form.amount.data, 
                            category_id=form.category.data, 
                            month=form.month.data, 
                            year=form.year.data, 
                            user=current_user)
            db.session.add(budget)
            flash('Budget set!', 'success')
            
        db.session.commit()
        return redirect(url_for('main.budgets'))
        
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template('budgets.html', title='Budgets', form=form, budgets=budgets)

@main.route("/budget/delete/<int:budget_id>")
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash('You do not have permission to delete this budget.', 'danger')
        return redirect(url_for('main.budgets'))
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted!', 'success')
    return redirect(url_for('main.budgets'))

@main.route("/expense/delete/<int:expense_id>")
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('You do not have permission to delete this expense.', 'danger')
        return redirect(url_for('main.expenses'))
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted!', 'success')
    return redirect(url_for('main.expenses'))

@main.route("/reports")
@login_required
def reports():
    """Display reports page with download options"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get all expenses for current user
    total_expenses = Expense.query.filter_by(user_id=current_user.id).count()
    total_budgets = Budget.query.filter_by(user_id=current_user.id).count()
    
    # Monthly summary
    monthly_spending = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.extract('month', Expense.date) == current_month,
        func.extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    monthly_budget = db.session.query(func.sum(Budget.amount)).filter(
        Budget.user_id == current_user.id,
        Budget.month == current_month,
        Budget.year == current_year
    ).scalar() or 0
    
    return render_template('reports.html', 
                          title='Reports',
                          total_expenses=total_expenses,
                          total_budgets=total_budgets,
                          monthly_spending=monthly_spending,
                          monthly_budget=monthly_budget,
                          current_month=current_month,
                          current_year=current_year)

@main.route("/reports/download/budget-spending")
@login_required
def download_budget_spending():
    """Download budget vs spending report as CSV"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get budget vs spending data
    categories = Category.query.all()
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Category', 'Budget', 'Spending', 'Remaining', 'Percent Used', 'Status'])
    
    # Write data
    for category in categories:
        spending = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == category.id,
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=category.id,
            month=current_month,
            year=current_year
        ).first()
        
        budget_amount = budget.amount if budget else 0
        remaining = budget_amount - spending
        percent_used = (spending / budget_amount * 100) if budget_amount > 0 else 0
        
        # Determine status
        if budget_amount > 0 and spending > budget_amount:
            status = 'Over Budget'
        elif budget_amount > 0 and percent_used >= 90:
            status = 'Warning (90%+)'
        elif budget_amount > 0:
            status = 'OK'
        else:
            status = 'No Budget Set'
        
        writer.writerow([
            category.name,
            f'{budget_amount:.2f}',
            f'{spending:.2f}',
            f'{remaining:.2f}',
            f'{percent_used:.1f}%',
            status
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=budget_spending_{current_month}_{current_year}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main.route("/reports/download/expenses")
@login_required
def download_expenses():
    """Download all expenses as CSV"""
    # Get all expenses for current user
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Date', 'Category', 'Description', 'Amount'])
    
    # Write data
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category.name,
            expense.description or '',
            f'{expense.amount:.2f}'
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=expenses_all.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main.route("/init_db")
def init_db():
    # Helper to create default categories
    if Category.query.count() == 0:
        categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Rent', 'Other']
        for name in categories:
            db.session.add(Category(name=name))
        db.session.commit()
        return "Default categories created!"
    return "Categories already exist."
