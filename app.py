#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from catalog_database_setup import Category, Item, Base, User
import httplib2
import json
import random
import string
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read()
                       )['web']['client_id']

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Check if the category is vaild, returns trun if the category does't exist
# returns false if it does
def categoryCheck(cat):
    cat = session.query(Category).filter_by(name=cat).one_or_none()
    if cat is None:
        return True
    return False


# Check if the category and title are vaild
# returns trun if the category or title does't exist
# returns false if they does
def categoryAndTitleCheck(category, title):
    cat = session.query(Category).filter_by(name=category).one_or_none()
    if cat is None:
        return True
    item = session.query(Item).filter_by(title=title,
                                         category=cat).one_or_none()
    if item is None:
        return True
    return False


# Generate a random uppercase alphanumeric string
# with the length 32 and returns it
def giveState():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in range(32))
    login_session['state'] = state
    return state


# create a user,saves it in the datebase and
# then return the user id from said datebase
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# given a user id returns a user from the database if it has it
# else returns none
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


# given an email
# returns the user id of its owner from the database if it has it
# else returns none
def getUserID(email):
    user = session.query(User).filter_by(email=email).one_or_none()
    if user is None:
        return None
    return user.id


# a modified method from
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py
# used in "Servers, Authorization, and CRUD LESSON 6
#          Creating Google Sign in
#          Step 5 GConnect" from udacity
# this method uses that one-time code given
# by the client from the google+ api server to:
# 1. to retive username,picture and email from the google+ api server
# 2. store the username,picture and email in the database they
#    don't exits in it
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
           .format(access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode()
    result = json.loads(result)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if the database has the users data
    if getUserID(login_session['email']) is None:
        user_id = createUser(login_session)
    login_session['user_id'] = getUserID(login_session['email'])

    flash("you are now logged in as {}".format(login_session['username']))
    return "data has been read"


# a modified method from
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py
# used in "Servers, Authorization, and CRUD LESSON 6
#          Creating Google Sign in
#          Step 5 GConnect" from udacity
# disconnect the user from website and redirect him to the Home page
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'\
        .format(login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected.")
        return redirect(url_for('showHomePage'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        flash("Failed to revoke token for given user 400")
        return redirect(url_for('showHomePage'))


# home page
# shows the last 9 items added into the database
@app.route('/')
@app.route('/catalog/')
def showHomePage():
    # gives a state token to the user if he doesn't have one
    if 'username' not in login_session:
        state = giveState()
    else:
        state = login_session['state']

    print('username' in login_session)
    categorys = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(9).all()
    return render_template("showHomePage.html", categorys=categorys,
                           items=items, message="Latest Items", STATE=state,
                           login_session=login_session)


# category page
# uses the same html file as the home page
# shows all the items in one category
@app.route('/catalog/<string:category>/')
@app.route('/catalog/<string:category>/items/')
def showCategory(category):
    categorys = session.query(Category).all()
    # Check if the category exits in the database
    if categoryCheck(category):
        flash("Invalid category")
        return redirect(url_for(showHomePage))
    # gives a state token to the user if he doesn't have one
    if 'username' not in login_session:
        state = giveState()
    else:
        state = login_session['state']

    cat_id = session.query(Category).filter_by(
        name=category).one_or_none().id
    items = session.query(Item).filter_by(
        cat_id=cat_id).order_by(Item.id.desc()).all()
    return render_template("showHomePage.html", categorys=categorys,
                           items=items,
                           message="{} Items ({} items)".format(
                               category, len(items)),
                           STATE=state, login_session=login_session)


# item page
# shows the item
@app.route('/catalog/<string:category>/<string:title>/')
def showItem(category, title):
    # Check if the item exits in the database
    if categoryAndTitleCheck(category, title):
        flash("Invalid item")
        return redirect(url_for(showHomePage))

    # gives a state token to the user if he doesn't have one
    if 'username' not in login_session:
        state = giveState()
    else:
        state = login_session['state']

    item = session.query(Item).filter_by(title=title).one()
    return render_template("showItem.html", item=item,
                           category=category, STATE=state,
                           login_session=login_session)


# add item page
# lets a logged-in in user add an item
@app.route('/catalog/create/', methods=['GET', 'POST'])
def addItem():
    # Check if the user is logged-in
    if 'username' not in login_session:
        flash("please login")
        return redirect(url_for("showHomePage"))
    # if the http method is a post
    if request.method == 'POST':
        # reads the all the values from the from
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        # Check if the category exits in the database
        if categoryCheck(category):
            flash("Invalid category")
            return redirect(url_for('addItem'))

        cat_id = session.query(Category).filter_by(
            name=request.form['category']).one().id

        # Check if the title or description are emtpy
        if title == "" or description == "":
            flash("Please enter your title and/or description")
            return redirect(url_for('addItem'))
        item = session.query(Item).filter_by(title=title).one_or_none()

        # Check if the title already exits in the database
        if item is not None:
            flash("{} already exists,"
                  " please choose another title".format(title))
            return redirect(url_for('addItem'))
        # makes the item and saves it to the database
        newitem = Item(title=title, description=description,
                       cat_id=cat_id, user_id=login_session['user_id'])
        session.add(newitem)
        session.commit()
        flash("{} has  been successfully added".format(title))
        return redirect(url_for('showHomePage'))
    # returns the form page to the use
    categorys = session.query(Category).all()
    return render_template("addItem.html", categorys=categorys)


# edit item page
# lets a logged-in in user edit an item if he is the owner of it
@app.route('/catalog/<string:category>/<string:title>/edit/',
           methods=['GET', 'POST'])
def editItem(category, title):
    # Check if the user is logged-in
    if 'username' not in login_session:
        flash("please login")
        return redirect(url_for("showItem", category=category, title=title))

    # Check if the item exits in the database
    if categoryAndTitleCheck(category, title):
        flash("Invalid item")
        return redirect(url_for(showHomePage))

    item = session.query(Item).filter_by(title=title).one()

    # Check if the user is the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("you don't have permission to edit this item")
        return redirect(url_for("showItem", category=category, title=title))

    # if the http method is a post
    if request.method == 'POST':
        # reads the all the values from the from
        newTitle = request.form['title']
        newDescription = request.form['description']
        newCategory = request.form['category']

        # Check if the newCategory exits in the database
        if categoryCheck(newCategory):
            flash("Invalid category")
            return redirect(url_for(
                "showItem",
                category=category,
                title=title)
            )

        # Check if the newTitle or newDescription are emtpy
        if newTitle == "" or newDescription == "":
            flash("Please enter your title and/or description")
            return redirect(url_for(
                'editItem',
                category=item.category.name,
                title=item.title)
            )

        # Check if the title already exits in the database
        exits = session.query(Item).filter_by(title=newTitle).one_or_none()
        if exits is not None and exits.id is not item.id:
            flash("{} already exists,"
                  " please choose another title".format(newTitle))
            return redirect(url_for(
                'editItem',
                category=item.category.name,
                title=item.title)
            )

        # edits the item and saves it to the database
        cat_id = session.query(Category).filter_by(name=newCategory).one().id
        item.title = newTitle
        item.description = newDescription
        item.cat_id = cat_id
        session.add(item)
        session.commit()
        flash("{} has been successfully edited".format(newTitle))
        return redirect(url_for(
            'showItem',
            category=item.category.name,
            title=item.title)
        )

    # returns the edit item page to the user
    categorys = session.query(Category).all()
    return render_template("editItem.html", categorys=categorys, item=item)


# delete page
# lets a logged-in in user delete an item if he is the owner of it
@app.route('/catalog/<string:category>/<string:title>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category, title):
    # Check if the user is logged-in
    if 'username' not in login_session:
        flash("please login")
        return redirect(url_for("showItem", category=category, title=title))
    # Check if the item exits in the database
    if categoryAndTitleCheck(category, title):
        flash("Invalid item")
        return redirect(url_for(showHomePage))

    item = session.query(Item).filter_by(title=title).one()

    # Check if the user is the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("you don't have permission to delete this item")
        return redirect(url_for("showItem", category=category, title=title))

    # if the http method is a post
    if request.method == 'POST':
        # delete item
        session.delete(item)
        session.commit()
        flash("{} has been successfully deleted".format(title))
        return redirect(url_for('showHomePage'))
    # returns the delete item page to the user
    return render_template("deleteItem.html", item=item)


# restful api endpoint
# returns an item in a json format
@app.route('/<int:cat_id>/<int:id>.json')
def itemJson(cat_id, id):
    item = session.query(Item).filter_by(id=id, cat_id=cat_id).one_or_none()
    if item is None:
        # Check if the item exits in the database
        return {'error': 'Invalid item'}
    return jsonify(item.serialize)


# restful api endpoint
# returns an category that contains all the items
# from the databese in a json format
@app.route('/catalog.json')
def catalogJson():
    result = {'category': []}
    categorys = session.query(Category).all()
    for category in categorys:
        cs = category.serialize
        cs.update({'item': []})
        items = session.query(Item).filter_by(cat_id=category.id).all()
        for item in items:
            cs['item'].append(item.serialize)
        result['category'].append(cs)
    return jsonify(result)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=8000)
