from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserLog, MNumber, NPC, WorkCenter
from . import db
import json
from sqlalchemy.sql import select, update
import time 
from datetime import datetime, timedelta
import pandas as pd

def scan_in(employee_num):
    
    enum_res = ""
    # check whether employee num in db
    check_enum = select(User.employee_num).where(User.employee_num == employee_num)
    result_check_enum_stmt = db.session.execute(check_enum).fetchall()
    for e_row in result_check_enum_stmt:
        enum_res = e_row[0]
        
    if enum_res == "":
        flash('Employee Not Found!', category='error')
        return render_template("clock_in_out.html", user=current_user)
    
    
    now = datetime.now()
    current_time_in = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    result_date = ""
        
    # checks if user clocked in already 
    check_date_stmt = select(UserLog.date).where(UserLog.employee_num == employee_num, UserLog.date == current_date)
    result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
    for row in result_check_date_stmt:
        result_date = row[0]
    
    # checks for no prior clock in
    if result_date == "":

        full_name_val =  select(User.full_name).where(User.employee_num == employee_num)
        full_name_res = db.session.execute(full_name_val).fetchall()
        for rowa in full_name_res:
            full_name_result = rowa[0]
        
        employee_num_val =  select(User.employee_num).where(User.employee_num == employee_num)
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
                hours_allocated = 0,
                npc = -1,
                machine = "",
                work_center = -1,
                work_center_rate = "")
        db.session.add(next_day_user)
        db.session.commit()
        flash('User Clocked In!', category='success')
        return render_template("clock_in_out.html", user=current_user)
    
    # updates the result date if it isn't empty to correct format
    # result_date2 = datetime.strptime(result_date, "%Y-%m-%d %H:%M:%S")
    # print(result_date2)
    # result_date = result_date2.strftime("%Y-%m-%d")
        
    # checks for a new day 
    if current_date > result_date: 
        
        full_name_val =  select(UserLog.full_name).where(UserLog.employee_num == employee_num)
        full_name_res = db.session.execute(full_name_val).fetchall()
        for rowa in full_name_res:
            full_name_result = rowa[0]
        
        employee_num_val =  select(UserLog.employee_num).where(UserLog.employee_num == employee_num)
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
                hours_allocated = 0,
                npc = -1,
                machine = "",
                work_center = -1,
                work_center_rate = "")
        print("ASd")
        db.session.add(next_day_user)
        db.session.commit()
    
    # checks for a second clock in
    if current_date == result_date: 
        flash('User Already Clocked In!', category='error')
        return render_template("clock_in_out.html", user=current_user)
    
    flash('User has not been clocked in ', category='error')
    return render_template("clock_in_out.html", user=current_user)

def scan_out(employee_num):
    
    now = datetime.now()
    current_time_in = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    result_date = ""
    # checks for any clock in in db
    check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == employee_num, UserLog.date == current_date)
    result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
    for row in result_check_date_stmt:
        result_date = row[0]

    # checks for clock out in db if the same day
    check_clock_out = select(UserLog.clock_out_time).where(UserLog.employee_num == employee_num, UserLog.date == current_date)
    result_check_clock_out = db.session.execute(check_clock_out).fetchall()
    for row in result_check_clock_out:
        result_check_clock_out = row[0]

    
    # if there's an empty clock in time, prompt error for not clocking in yet   
    if result_date == "":
        flash('You cannot clock out without clocking in!', category='error')
        return render_template("clock_in_out.html", user=current_user)   
    
    # changes the clock in time to just a date
    result_date2 = datetime.strptime(result_date, "%Y-%m-%d %H:%M:%S")
    result_date3 = result_date2.strftime("%Y-%m-%d")
    
    
    # check to double clock out
    if result_check_clock_out != "":
        flash('You already clocked out!', category='error')
        return render_template("clock_in_out.html", user=current_user)
    
    
    # first time clocking out               
    if current_date == result_date3:  
        now = datetime.now()
        current_time_out = now.strftime("%Y-%m-%d %H:%M:%S")
        
        stmt = update(UserLog).where(UserLog.employee_num == employee_num, UserLog.date == current_date, UserLog.clock_out_time == "").values({"clock_out_time": current_time_out})
        db.session.execute(stmt)
            
        print(result_date)
        start = result_date2
        end = datetime.strptime(current_time_out, "%Y-%m-%d %H:%M:%S")
        hours_clocked = end - start
        
        hours_clocked = str(hours_clocked)
        
        hours_clocked_stmt = update(UserLog).where(UserLog.employee_num == employee_num, UserLog.date == current_date, UserLog.hours_clocked == 0).values({"hours_clocked": hours_clocked})
        db.session.execute(hours_clocked_stmt)
        db.session.commit()
        
        flash('Clocked out.', category='success')
        return render_template("clock_in_out.html", user=current_user)
        
    else:
        flash('Something went wrong with clocking out.', category='error')
        return render_template("clock_in_out.html", user=current_user)