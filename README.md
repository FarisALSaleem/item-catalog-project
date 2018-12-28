Introduction
----------------------------------------------------------------------------------------------------
This repository contains python3,js,CSS,HTML files for the item-catalog-project from udacity.

How-to-run
----------------------------------------------------------------------------------------------------
1. make sure that you have the following python3 modules installed 
    1. flask.
    2. sqlalchemy.
    3. oauth2client. 
    4. requests.
    5. httplib2.
2. open cmd/terminal and traverse to this directory.
3. run catalog_database_setup.py to created catalog.db. 
4. run catalog_database_seeder.py to fill the catalog.db with categories. 
5. run app.py to run the web server.
6. use your internet browser of choice and go to http://localhost:8000/.

Note: This code was written for python3 and will not work for python2.

Description
----------------------------------------------------------------------------------------------------
* the catalog_database_setup.py file creates a database with the following 3 tables:
    1. category:
        * id (integer, primary_key)
        * name (varchar(80), not null, unique)
    2. user:
        * id (integer, primary_key)
        * name (varchar(255), not null)
        * email (varchar(255), not null)
        * picture (varchar(255), not null)
    3. item:
        * id (primary_key)
        * title (varchar(255), not null, unique)
        * description (varchar(255), not null)
        * cat_id (integer, ForeignKey('category.id'))
        * user_id (integer, ForeignKey('user.id'))

* the catalog_database_seeder.py file adds a list of categories to the category table.

* the app.py is a flask application connects to catalog.db and performs CRUD operations on the item tables while using google oauth2 authentication and authorization said operations.
* app.py also has a restful API endpoint to retrieve an item or list of categories with their items in a JSON format.

API endpoint example
----------------------------------------------------------------------------------------------------
* list of categories with their items (http://localhost:8000/catalog.json)
'''
{  
   "category":[  
      {  
         "id":1,
         "item":[  
            {  
               "cat_id":1,
               "description":"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ",
               "id":2,
               "title":"foo"
            }
         ],
         "name":"Soccer"
      },
      {  
         "id":2,
         "item":[  

         ],
         "name":"Basketball"
      },
      {  
         "id":3,
         "item":[  
            {  
               "cat_id":3,
               "description":"Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
               "id":3,
               "title":"bar"
            }
         ],
         "name":"Baseball"
      },
      {  
         "id":4,
         "item":[  

         ],
         "name":"Frisbee"
      },
      {  
         "id":5,
         "item":[  

         ],
         "name":"Snowboarding"
      },
      {  
         "id":6,
         "item":[  

         ],
         "name":"Rock Climbing"
      },
      {  
         "id":7,
         "item":[  

         ],
         "name":"Football"
      },
      {  
         "id":8,
         "item":[  

         ],
         "name":"Skating"
      },
      {  
         "id":9,
         "item":[  

         ],
         "name":"Hockey"
      }
   ]
}
'''

* an item (http://localhost:8000/3/3.json)

'''
{  
   "cat_id":3,
   "description":"Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
   "id":3,
   "title":"bar"
}
'''


Repository contains
----------------------------------------------------------------------------------------------------
- catalog_database_setup.py -contains python3 code that creates catalog.db.
- catalog_database_seeder.py -contains python3 code that adds a list of categories to catalog.db.
- app.py -a flask application connects to catalog.db and performs CRUD operations.
- client_secrets.json -contains client secret that is used in google oauth2.
- templates -HTML files that are used in app.py.
- static -CSS and js files that are used in app.py.
 
