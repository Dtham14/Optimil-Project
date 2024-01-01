from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserLog, MNumber
from . import db
import json
from sqlalchemy.sql import select, update
import time 
from datetime import datetime, timedelta
import pandas as pd

views = Blueprint('views', __name__)
    
@views.route('/employee', methods=['GET', 'POST'])
@login_required
def employee_portal():
    
    if request.method == 'POST':
        
        # Gets the current day
        now = datetime.now()
        current_time_in = now.strftime("%d-%m-%Y %H:%M:%S")
        current_date = now.strftime("%d-%m-%Y")
        
        # Testing different days
        other_date = datetime.today() + timedelta(days=2)
        # today_date_time = today_date_time_og.strftime("%d-%m-%Y %H:%M:%S")
        # current_date = other_date.strftime("%d-%m-%Y")
        
        # Clock In 
        if request.form.get('clock_in') == 'Clock In' and request.form.get('clock_out') != 'Clock Out' and request.form.get('submit') != 'Submit Info':
            
            # checks if user clocked in already 
            check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]
            
            # checks for no prior clock in
            if result_date == "":

                # adds current time into row if no clock in time
                stmt = select(UserLog.date).where(UserLog.employee_num == current_user.employee_num)
                res = db.session.execute(stmt)
                for row in res:
                    res = row[0]
                stmt2 = update(UserLog).where(UserLog.date == res).values({"clock_in_time": current_time_in})
                db.session.execute(stmt2)
                db.session.commit()
                    
                flash('You have been clocked in.', category='success')
                return render_template("employee.html", user=current_user)
        
            # updates the result date if it isn't empty to correct format
            result_date2 = datetime.strptime(result_date, "%d-%m-%Y %H:%M:%S")
            result_date = result_date2.strftime("%d-%m-%Y")
                
            # checks for a new day 
            if current_date > result_date: 
                
                full_name_val =  select(UserLog.full_name).where(UserLog.employee_num == current_user.employee_num)
                full_name_res = db.session.execute(full_name_val).fetchall()
                for rowa in full_name_res:
                    full_name_result = rowa[0]
                
                employee_num_val =  select(UserLog.employee_num).where(UserLog.employee_num == current_user.employee_num)
                employee_num_res = db.session.execute(employee_num_val).fetchall()
                for rowb in employee_num_res:
                    employee_num_result = rowb[0]
                    
                next_day_user = UserLog(
                        date = current_date, 
                        full_name = full_name_result, 
                        employee_num = employee_num_result,
                        clock_in_time = current_time_in, 
                        clock_out_time = "", 
                        hours_clocked = 0, 
                        project_num = 0,
                        part_num = 0, 
                        hours_allocated = 0)
                db.session.add(next_day_user)
                db.session.commit()
                flash('You have been clocked in.', category='success')
                return render_template("employee.html", user=current_user)
            
            # checks for a second clock in
            if current_date == result_date: 
                flash('You already been clocked in.', category='error')
                return render_template("employee.html", user=current_user)
            
            flash('You have been clocked in', category='success')
            return render_template("employee.html", user=current_user)
        
        # Submitting M# and Tasks 
        if request.form.get('clock_in') != 'Clock In' and request.form.get('clock_out') != 'Clock Out' and request.form.get('submit') == 'Submit Info':
            project_num = request.form.get('project_num')
            part_num = request.form.get('part_num') 
            hours_allocated = request.form.get('hours_allocated')
            
            check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]
                
            if result_date == "": 
                flash('You must clock in first!', category='error')
                return render_template("employee.html", user=current_user)
            
            check_mnum = select(MNumber.m_num)
            result_check_mnum = db.session.execute(check_mnum).fetchall()
            mnum_list = []
            
            for num in result_check_mnum:
                mnum_list.append(str(num).strip('(').strip(')').strip(','))
                
            if request.form.get('submit') == 'Submit Info' and ((project_num == "" and part_num == "") or hours_allocated == "" ):
                flash('There are empty fields.', category='error')
                return render_template("employee.html", user=current_user)
            
            # updates values to 
            if project_num == "":
                project_num = 0
            elif part_num == "":
                part_num = 0    
            
            if str(project_num) in mnum_list or project_num == 0:
                pass
            else: 
                flash('Invalid M#!', category='error')
                return render_template("employee.html", user=current_user)
            
            if request.form.get('submit') == 'Submit Info' and not((int(project_num) >= 1 or int(part_num) >= 1) and int(hours_allocated) <= 8):
                flash('Invalid fields.', category='error')
                return render_template("employee.html", user=current_user)
            
            if request.form.get('submit') == 'Submit Info' and ((int(project_num) >= 1 or int(part_num) >= 1) and int(hours_allocated) <= 8):
                
                full_name_val =  select(UserLog.full_name).where(UserLog.employee_num == current_user.employee_num)
                full_name_res = db.session.execute(full_name_val).fetchall()
                for rowa in full_name_res:
                    full_name_result = rowa[0]
                
                employee_num_val =  select(UserLog.employee_num).where(UserLog.employee_num == current_user.employee_num)
                employee_num_res = db.session.execute(employee_num_val).fetchall()
                for rowb in employee_num_res:
                    employee_num_result = rowb[0]
                    
                check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
                result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
                for row in result_check_date_stmt:
                    result_date = row[0]
                
                hours_allocated_stmt = select(UserLog.hours_allocated).where(UserLog.employee_num == current_user.employee_num)
                hours_allocated_res = db.session.execute(hours_allocated_stmt)
                for row in hours_allocated_res:
                    hours_allocated_res = row[0]
                    
                if hours_allocated_res > 0:
                    next_task_user = UserLog(
                        date = current_date, 
                        full_name = full_name_result, 
                        employee_num = employee_num_result,
                        clock_in_time = result_date, 
                        clock_out_time = "", 
                        hours_clocked = 0, 
                        project_num = project_num,
                        part_num = part_num, 
                        hours_allocated = hours_allocated)
                    db.session.add(next_task_user)
                    db.session.commit()
                    flash('Data submitted!', category='success')
                    return render_template("employee.html", user=current_user)
                     
                print("same row")
                stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num).values({"date": current_date, "project_num": project_num, "part_num": part_num, "hours_allocated": hours_allocated})
                db.session.execute(stmt)
                db.session.commit()
                flash('Data submitted!', category='success')
                return render_template("employee.html", user=current_user)
            
            else: 
                
                flash('Something went wrong.', category='success')
                return render_template("employee.html", user=current_user)
        
        # Clock Out 
        elif request.form.get('clock_out') == 'Clock Out' and request.form.get('submit') != 'Submit Info':
            
            # checks for any clock in in db
            check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]

                
            # checks for any clock out in db    
            check_clock_out = select(UserLog.clock_out_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
            result_check_clock_out = db.session.execute(check_clock_out).fetchall()
            for row in result_check_clock_out:
                result_check_clock_out = row[0]
            
               
            if result_date == "":
                flash('You cannot clock out without clocking in!', category='error')
                return render_template("employee.html", user=current_user)    
            
            result_date2 = datetime.strptime(result_date, "%d-%m-%Y %H:%M:%S")
            result_date = result_date2.strftime("%d-%m-%Y")
            
            
            # check to double clock out
            if result_check_clock_out != "":
                flash('You already clocked out!', category='error')
                return render_template("employee.html", user=current_user)
            
            
            # first time clocking out
            if result_check_clock_out == "":
                
                if current_date == result_date:  
                    now = datetime.now()
                    current_time_out = now.strftime("%d-%m-%Y %H:%M:%S")
                    
                    stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date).values({"clock_out_time": current_time_out})
                    db.session.execute(stmt)
                    db.session.commit()
                    
                    stmt2 = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
                    result = db.session.execute(stmt2)
                    for row in result_check_date_stmt:
                        result1 = row[0]
                    
                    start = datetime.strptime(result1, "%d-%m-%Y %H:%M:%S")
                    end = datetime.strptime(current_time_out, "%d-%m-%Y %H:%M:%S")
                    hours_clocked = end - start
                    
                    hours_clocked = str(hours_clocked)
                    
                    hours_clocked_stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num).values({"hours_clocked": hours_clocked})
                    db.session.execute(hours_clocked_stmt)
                    db.session.commit()
                    
                    flash('Clocked out.', category='success')
                    return render_template("employee.html", user=current_user)
                
            result_check_clock_out2 = datetime.strptime(result_check_clock_out, "%d-%m-%Y %H:%M:%S")
            result_check_clock_out = result_check_clock_out2.strftime("%d-%m-%Y")
                
            if current_date == result_date:  
                now = datetime.now()
                current_time_out = now.strftime("%d-%m-%Y %H:%M:%S")
                
                stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date).values({"clock_out_time": current_time_out})
                db.session.execute(stmt)
                db.session.commit()
                
                stmt2 = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num and UserLog.date == current_date)
                result = db.session.execute(stmt2)
                for row in result_check_date_stmt:
                    result1 = row[0]
                
                start = datetime.strptime(result1, "%d-%m-%Y %H:%M:%S")
                end = datetime.strptime(current_time_out, "%d-%m-%Y %H:%M:%S")
                hours_clocked = end - start
                
                hours_clocked = str(hours_clocked)
                
                hours_clocked_stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num).values({"hours_clocked": hours_clocked})
                db.session.execute(hours_clocked_stmt)
                db.session.commit()
                
                flash('Clocked out.', category='success')
                return render_template("employee.html", user=current_user)
            else:
                flash('Something went wrong with clocking out.', category='error')
                return render_template("employee.html", user=current_user)
    
        else: 
            flash('Something went wrong', category='error')
            return render_template("employee.html", user=current_user)
                   

    return render_template("employee.html", user=current_user)