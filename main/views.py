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

views = Blueprint('views', __name__)


@views.route('/employee', methods=['GET', 'POST'])
@login_required
def employee_portal():
    
    get_Mnum = select(MNumber.m_num)
    res_stmt = db.session.execute(get_Mnum).fetchall()
    Mnum_list = []
    
    for num in res_stmt:
        Mnum_list.append(int(str(num).strip('(').strip(')').strip(',')))
        
    
    get_wc = select(WorkCenter.work_center)
    res_stmt2 = db.session.execute(get_wc).fetchall()
    wc_list = []
    
    for wc in res_stmt2:
        wc_list.append(int(str(wc).strip('(').strip(')').strip(',')))
        
    
    get_npc = select(NPC.npc)
    res_stmt3 = db.session.execute(get_npc).fetchall()
    npc_list = []
    
    for npc in res_stmt3:
        npc_list.append(int(str(npc).strip('(').strip(')').strip(',')))
        
    if request.method == 'POST':
        
        # Gets the current day
        now = datetime.now()
        current_time_in = now.strftime("%Y-%m-%d %H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        
        # Testing different days
        other_date = datetime.today() + timedelta(days=2)
        # today_date_time = today_date_time_og.strftime("%d-%m-%Y %H:%M:%S")
        # current_date = other_date.strftime("%d-%m-%Y")

        # Clock In Press
        if request.form.get('clock_in') == 'Clock In':
            
            result_date = ""
        
            # checks if user clocked in already 
            check_date_stmt = select(UserLog.date).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]
            
            # checks for no prior clock in
            if result_date == "":

                # adds current time into row if no clock in time
                # changed 05-10
                full_name_val =  select(User.full_name).where(User.employee_num == current_user.employee_num)
                full_name_res = db.session.execute(full_name_val).fetchall()
                for rowa in full_name_res:
                    full_name_result = rowa[0]
                
                employee_num_val =  select(User.employee_num).where(User.employee_num == current_user.employee_num)
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
                flash('You have been clocked in.', category='success')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
                
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
                        hours_allocated = 0,
                        npc = -1,
                        machine = "",
                        work_center = -1,
                        work_center_rate = "")
                db.session.add(next_day_user)
                db.session.commit()
                flash('You have been clocked in.', category='success')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            # checks for a second clock in
            if current_date == result_date: 
                flash('You already been clocked in.', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            flash('You have not been clocked in ', category='error')
            return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
        
        # Submitting M# and Tasks 
        if request.form.get('submit') == 'Submit Info':
        
            
            check_clock_out = select(UserLog.clock_out_time).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
            result_check_clock_out = db.session.execute(check_clock_out).fetchall()
            for row in result_check_clock_out:
                result_check_clock_out = row[0]
                
            
            # Can't resubmit info when clocked out    
            if result_check_clock_out != "":
                flash('You already clocked out!', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            
            project_num = request.form.get('search_filter2')
            part_num = request.form.get('part_num') 
            hours_allocated = request.form.get('hours_allocated')
            work_center = request.form.get("search_filter1")
            npc = request.form.get("search_filter3")

            result_date = ""
            
            check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]
            
            if result_date == "": 
                flash('You must clock in first!', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            # check for empty fields   
            if request.form.get('submit') == 'Submit Info' and ((project_num == "" and part_num == "" and npc == "") or hours_allocated == "" or work_center == ""):
                flash('There are empty fields.', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            # updates values to 
            if part_num == "":
                part_num = 0    
                
            if int(hours_allocated) > 8:
                flash('Invalid Hours Input', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)

            if request.form.get('submit') == 'Submit Info' and ((int(project_num) >= 1 or int(part_num) >= 1) and int(hours_allocated) <= 8):
                
                full_name_val =  select(UserLog.full_name).where(UserLog.employee_num == current_user.employee_num)
                full_name_res = db.session.execute(full_name_val).fetchall()
                for rowa in full_name_res:
                    full_name_result = rowa[0]
                
                employee_num_val =  select(UserLog.employee_num).where(UserLog.employee_num == current_user.employee_num)
                employee_num_res = db.session.execute(employee_num_val).fetchall()
                for rowb in employee_num_res:
                    employee_num_result = rowb[0]
                    
                check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
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
                        hours_allocated = hours_allocated,
                        npc = npc,
                        machine = "",
                        work_center = work_center,
                        work_center_rate = "")
                    db.session.add(next_task_user)
                    db.session.commit()
                    flash('Data submitted!', category='success')
                    return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
                     
                # fix this
                # after first clock in 
                stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date).values({"project_num": project_num, "part_num": part_num, "hours_allocated": hours_allocated, "npc": npc, "work_center": work_center})
                db.session.execute(stmt)
                db.session.commit()
                flash('Data submitted!', category='success')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
                    
            
            else: 
                
                flash('Something went wrong.', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
        
        # Clock Out 
        elif request.form.get('clock_out') == 'Clock Out' and request.form.get('submit') != 'Submit Info':
            
            result_date = ""
            # checks for any clock in in db
            check_date_stmt = select(UserLog.clock_in_time).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
            result_check_date_stmt = db.session.execute(check_date_stmt).fetchall()
            for row in result_check_date_stmt:
                result_date = row[0]

            # checks for clock out in db if the same day
            check_clock_out = select(UserLog.clock_out_time).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date)
            result_check_clock_out = db.session.execute(check_clock_out).fetchall()
            for row in result_check_clock_out:
                result_check_clock_out = row[0]

            
            # if there's an empty clock in time, prompt error for not clocking in yet   
            if result_date == "":
                flash('You cannot clock out without clocking in!', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)   
            
            # changes the clock in time to just a date
            result_date2 = datetime.strptime(result_date, "%Y-%m-%d %H:%M:%S")
            result_date3 = result_date2.strftime("%Y-%m-%d")
            
            
            # check to double clock out
            if result_check_clock_out != "":
                flash('You already clocked out!', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
            
            
            # first time clocking out               
            if current_date == result_date3:  
                now = datetime.now()
                current_time_out = now.strftime("%Y-%m-%d %H:%M:%S")
                
                stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date, UserLog.clock_out_time == "").values({"clock_out_time": current_time_out})
                db.session.execute(stmt)
                    
                start = result_date2
                end = datetime.strptime(current_time_out, "%Y-%m-%d %H:%M:%S")
                hours_clocked = end - start
                
                hours_clocked = str(hours_clocked)
                
                hours_clocked_stmt = update(UserLog).where(UserLog.employee_num == current_user.employee_num, UserLog.date == current_date, UserLog.hours_clocked == 0).values({"hours_clocked": hours_clocked})
                db.session.execute(hours_clocked_stmt)
                db.session.commit()
                
                flash('Clocked out.', category='success')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
                
            else:
                flash('Something went wrong with clocking out.', category='error')
                return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
    
        else: 
            flash('Something went wrong', category='error')
            return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)
                   

    return render_template("employee.html", user=current_user, Mnum_list=Mnum_list, wc_list = wc_list, npc_list = npc_list)