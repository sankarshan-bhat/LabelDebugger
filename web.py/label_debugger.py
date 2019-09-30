#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
import requests
#import py_entitymatching as em

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = (
    '/fetchPair', 'fetchPair',
)

class fetchPair:
    def __init__(self):
        self.cdriveApiUrl = "https://api.cdrive.columbusecosystem.com"
        self.token = 'GDzqDPx9pMsq8xGQINZ4onx1ksBZOz'
        self.auth_header = "Bearer " + self.token
        self.features_vector_path = "users/test_wisc2/test/tableB.csv"
        self.out_path = "users/test_wisc2/test"

    def GET(self):
        return render_template('search.html')

    def POST(self):
        post_params = web.input()
        table_a_url = post_params['tableA']
        table_b_url = post_params['tableB']
        label_data_url = post_params['labelledPairs']

    
        top_k = post_params['topK']

        #access_token = request.data['access_token']
        cdrive_download_url = self.cdriveApiUrl+ "/download?path="+ table_a_url
        table_a_resp = requests.get(url = cdrive_download_url, headers={'Authorization': self.auth_header})
        print "table_a_resp", table_a_resp
        data = table_a_resp.json() 
        table_a_file_resp = requests.get(data['download_url'])
        with open("tableA.csv",'wb') as f: 
            f.write(table_a_file_resp.text) 

        cdrive_download_url = self.cdriveApiUrl+ "/download?path="+table_b_url
        table_b_resp = requests.get( url = cdrive_download_url, headers={'Authorization': self.auth_header})
        data = table_b_resp.json() 
        table_b_file_resp = requests.get(data['download_url'])

        with open("tableB.csv",'wb') as f: 
            f.write(table_b_file_resp.text) 

        cdrive_download_url = self.cdriveApiUrl+ "/download?path="+label_data_url
        label_resp = requests.get(url = cdrive_download_url, headers={'Authorization': self.auth_header})
        data = label_resp.json() 

        label_file_resp = requests.get(data['download_url'])
        with open("label.csv",'wb') as f: 
            f.write(label_file_resp.text)

        cdrive_download_url = self.cdriveApiUrl+ "/download?path="+self.features_vector_path
        label_resp = requests.get(url = cdrive_download_url, headers={'Authorization': self.auth_header})
        data = label_resp.json() 

        label_file_resp = requests.get(data['download_url'])
        with open("feature_vector.csv",'wb') as f: 
            f.write(label_file_resp.text)

        #table_A = em.read_csv_metadata(apath, key='id')
        #table_B = em.read_csv_metadata(bpath, key='id')

        print " reaching end"
        #file_arg = {'file': ("results.csv"), 'path':  self.out_path }
        with open('results.csv', 'r') as f:
            f.seek(0)
            file_arg = {'file': ('results.csv', f), 'path': (None, self.out_path)}
            response = requests.post('https://api.cdrive.columbusecosystem.com/upload/', files=file_arg, headers={'Authorization': self.auth_header})

            #response = requests.post('https://api.cdrive.columbusecosystem.com/upload/', files=file_arg, headers={'Authorization':'Bearer ' + access_token})
            print " res", response

        #print response
        search_results = ['generated']
        return render_template('results.html')



if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
