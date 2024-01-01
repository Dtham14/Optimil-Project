from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, UserLog, MNumber
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import select
import pandas as pd
import csv

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    # the_admin = User(work_center = 55, username='admin', password=generate_password_hash(
    #             'daniel114', method='pbkdf2', salt_length=16), full_name='Daniel Tham', employee_num = 0)
    # db.session.add(the_admin)
    # db.session.commit()
    
    # the_admin_log = UserLog(date = "N/A", full_name = 'Daniel Tham', employee_num = 0,
    #                 clock_in_time = "N/A", clock_out_time = "N/A", hours_clocked = 0, project_num = 0,
    #                 part_num = 0, hours_allocated = 0)
    # db.session.add(the_admin_log)
    # db.session.commit()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
            
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                if check_password_hash(user.password, password) and (user.username == 'admin'):
                    login_user(user, remember=True)
                    return redirect(url_for('auth.admin_portal'))
                else:
                    login_user(user, remember=True)
                    return redirect(url_for('views.employee_portal'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_portal():   
            
    if request.method == 'POST':
        
        if request.form.get('submit_m') != 'submit_m' and request.form.get('timesheet') != 'Download Timesheet and Users' and request.form.get('submit') == 'Submit Info':
            work_center = request.form.get('work_center')
            username = request.form.get('username')
            full_name = request.form.get('full_name')
            employee_num = request.form.get('employee_num')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            user = User.query.filter_by(username=username).first() 
            if user:
                print("Checking Unique Username.....")
            elif len(work_center) < 1 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Please enter work center id.', category='error')
            elif len(username) < 4 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Username must be greater than 3 characters.', category='error')
            elif len(full_name) < 1 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Please enter full name.', category='error')
            elif len(employee_num) < 1 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Please enter employee number.', category='error')    
            elif len(password1) < 7 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Password must be at least 7 characters.', category='error')
            elif password1 != password2 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Passwords don\'t match.', category='error')
            
            if request.form.get('submit') == 'Submit Info' and (len(username) < 4 or len(full_name) < 1 or len(password1) < 7 or password1 != password2 or  len(employee_num) < 1):
                flash('Some fields are empty', category='error')
                return render_template("admin.html", user=current_user)

            else: 
                
                new_user = User(work_center = work_center, username = username, password = generate_password_hash(
                    password1, method = 'pbkdf2', salt_length = 16), full_name = full_name, employee_num = employee_num)
                
                db.session.add(new_user)
                db.session.commit()
                
                new_user_log = UserLog(date = "", full_name = full_name, employee_num = employee_num,
                    clock_in_time = "", clock_out_time = "", hours_clocked = 0, project_num = 0,
                    part_num = 0, hours_allocated = 0)
                
                db.session.add(new_user_log)
                db.session.commit()
                
                flash('Account created!', category='success')
                return render_template("admin.html", user=current_user)
            
        if request.form.get('submit_m') == 'Submit M#' and request.form.get('timesheet') != 'Download Timesheet and Users' and request.form.get('submit') != 'Submit Info':
        
            # query 
            m_num = request.form.get('insert_m')
            next_m_num = MNumber(m_num = m_num)
            db.session.add(next_m_num)
            db.session.commit()
            flash('M# Inserted', category='success')
            return render_template("admin.html", user=current_user)
            
        if request.form.get('timesheet') == 'Download Timesheet and Users' and request.form.get('submit') != 'Submit Info':
        
            # query 
            timesheet_stmt = select('*').select_from(UserLog)
            result = db.session.execute(timesheet_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('timesheet.csv')
            
            users_stmt = select('*').select_from(User)
            result2 = db.session.execute(users_stmt).fetchall()
            df = pd.DataFrame(result2)
            df.to_csv('users.csv')
            
            m_num_stmt = select('*').select_from(MNumber)
            result3 = db.session.execute(m_num_stmt).fetchall()
            df = pd.DataFrame(result3)
            df.to_csv('mnum.csv')
            
            flash('Dowloading Timesheet, User, M#', category='success')
            return render_template("admin.html", user=current_user)
            
        else:
            flash('Something went wrong', category='error')
            return render_template("admin.html", user=current_user) 
            
            
    return render_template("admin.html", user=current_user)    




