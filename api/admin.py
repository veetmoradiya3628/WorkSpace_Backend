import json
from turtle import end_fill, pu
from flask import Blueprint, make_response, render_template, request, g
from app import db
from models import Admin, Customer, Location, Subscription_plan, Plan_price, Purchase_hist
from userauth import admin_auth
from datetime import date

admin = Blueprint('admin', __name__)


@admin.route('/admin/profile', methods=['GET'])
@admin_auth
def admin_profile():
    info = Admin.query.join(
        Location, Admin.tbl_location_id == Location.location_id
    ).with_entities(
        Admin.admin_email, Admin.admin_name, Location.address, Location.city, Location.state
    ).filter(Admin.admin_email == g.token).first()

    if bool(info):
        resp = make_response({
            "status": 200,
            "admin": {
                "email": info[0],
                "name": info[1],
                "address": info[2],
                "city": info[3],
                "state": info[4]
            }
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "Admin doesn't exist."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


# all users details for admin side to show list of users
@admin.route('/admin/user_details', methods=['GET'])
@admin_auth
def users_details():
    users = Customer.query.all()
    user_list = []
    for user in users:
        _user = {
            "name": user.name,
            "email": user.email,
            "email_verified": user.email_verify,
            "is_block": user.block_user
        }
        user_list.append(_user)
    resp = make_response({
        "status_code": "200",
        "customers": user_list
    })
    return resp


# all user purchase plan history

@admin.route('/admin/user_purchase_plan_details',methods = ["GET"])
# @admin_auth
def user_details():
    
    userInfo = db.session.query(Customer,Purchase_hist).filter(Customer.customer_id == Purchase_hist.tbl_customer_id).all()
    
    if bool(userInfo):
        
        records = []
        name = desk_no = price = purchase_date = start_date = end_date = None

        for c,p in db.session.query(Customer,Purchase_hist).filter(Customer.customer_id == Purchase_hist.tbl_customer_id).all():
            name = c.name
            desk_no = p.desk_no
            price = p.price
            purchase_date = p.purchase_date
            start_date = p.start_date
            end_date = p.end_date
            
            obj = {
                'Name' : name,
                'Desk no.' : desk_no,
                'Plan price' : price,
                'Purchase date' : purchase_date,
                'Start date' : start_date,
                'End date' : end_date
            }
            
            records.append(obj)
            
        resp = make_response(
            {
                "status_code":200,
                "user_purchsed_plans_details":records
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "No one have purchase any plan"
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

# Changes Required this is not uptodate 
def block_user():
    list_unblock_user = Customer.query.with_entities(Customer.customer_id).filter_by(block_user=0).all()
    today = date.today()
    if bool(list_unblock_user):
        list_user = []
        for i in range(0,len(list_unblock_user)):
            list_user.append(list_unblock_user[i][0])
        
        for i in range(0, len(list_user)):
            purchase_history = Purchase_hist.query.with_entities(
                    Purchase_hist.purchase_date, Purchase_hist.start_date, Purchase_hist.end_date
                ).filter(
                    Purchase_hist.tbl_customer_id == list_user[i]
                ).all()
            

            if bool(purchase_history):
                limit_email = []
                limit_block = []
                for i in range(0, len(purchase_history)):
                    purchase_date = today - purchase_history[i][0]
                    start_date = today - purchase_history[i][1]
                    end_date = today - purchase_history[i][2]

                    if (int(purchase_date.days)>25 and int(purchase_date.days)<30) or (int(start_date.days)>25 and int(start_date.days)<30) or (int(end_date.days)>25 and int(end_date.days)<30):
                        limit_email.append(1)
                    if (int(purchase_date.days)>=30 or int(start_date.days)>=30 or int(end_date.days)>=30):
                        limit_block.append(1)

                if(len(limit_email)>0):
                    print("Compose Mail")
                if(len(limit_block)>0):
                    block = Customer.query.filter(Customer.customer_id == 'vraj12').first()
                    block.block_user = 1
                    db.session.commit()        
            