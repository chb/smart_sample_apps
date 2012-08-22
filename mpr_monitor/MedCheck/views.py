"""
    File: views.py
    
    Author: William J. Bosl
    Children's Hospital Boston
    300 Longwood Avenue
    Boston, MA 02115
    Email: william.bosl@childrens.harvard.edu
    Web: http://chip.org

    Copyright (C) 2011 William Bosl, Children's Hospital Boston Informatics Program (CHIP)
    http://chip.org. 

    Purpose:
    
    This file is part of a Django-based SMArt application that implements
    a two-step test for medication adherence. It is intended to be used as
    a SMArt web application within the context of a SMArt container. See
    http://www.smartplatforms.org/ for detailed information about SMArt applications.
        
    License information should go here.

    $Log: views.py,v $
"""
# Django imports.
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.template import RequestContext
from django.utils import simplejson 
from django.shortcuts import render_to_response

# The SMArt API uses these libraries
import datetime
import urllib
from mpr_monitor import settings
from smart_client import smart
from smart_client import oauth
import adherenceTests

# Basic configuration:  the consumer key and secret we'll use
# to OAuth-sign requests.
SMART_SERVER_OAUTH = {'consumer_key': '', 
                      'consumer_secret': 'smartapp-secret'}

# The SMArt container we're planning to talk to
SMART_SERVER_PARAMS = {
    'api_base' : ''
}

# Global variables
ISO_8601_DATETIME = '%Y-%m-%d'
last_pill_dates = {}
Global_PATIENT_ID = 0
Global_ADHERE_VARS = 0

#===========================================
# The index page is the generally the first
# page to appear when the application is started.
#===========================================
def index(request):
    indexpage = get_template('index.html')
	
	# Declare global variables that may be modified here
    global Global_PATIENT_ID 
    global Global_ADHERE_VARS 
	
    # Current context information
    oa_params, client, smart_oauth_header = get_smart_client(request)
	 
    # User or physician and the patient name
    user = oa_params["smart_user_id"]
    patientID = oa_params["smart_record_id"]
    
        
    # Get the medication list for this context
    # Note the general pattern: GET /records/{record_id}/medications/
    medications = client.records_X_medications_GET()
    query = """
        PREFIX dcterms:<http://purl.org/dc/terms/>
        PREFIX sp:<http://smartplatforms.org/terms#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT  ?med ?name ?quant ?when
        WHERE {
            ?med rdf:type sp:Medication .
            ?med sp:drugName ?medc.
            ?medc dcterms:title ?name.
            ?med sp:fulfillment ?fill.
            ?fill sp:dispenseDaysSupply ?quant.
            ?fill dcterms:date ?when.
       }
       """
       
    pills = medications.query(query)
    birthday, patient_name = get_birthday_name(client)
    drug = 'all'
    
    # We only want to call the adherence_check once for a specific patient
    if Global_PATIENT_ID == patientID:
        meds_flags, gaps, refill_data, refill_day = Global_ADHERE_VARS
    else:
        tests = adherenceTests.AdherenceTests()
        meds_flags, gaps, refill_data, refill_day = tests.allTests(pills, drug, birthday)		
        Global_ADHERE_VARS = [meds_flags, gaps, refill_data, refill_day]  # save the data for future needs
        Global_PATIENT_ID = patientID
        
	# Medication information will be displayed by drug class. Here we
	# sort all the patient's medications into drug classes defined
	# in this application.
    drug_class_array = {}
    for n in range(len(meds_flags)):
        drug_class_array[meds_flags[n][5]] = 1
    sorted_drug_class_list = sorted(drug_class_array.keys())
                  
	# Send these variables to the page for rendering
    variables = Context({
        'head_title': u'Medication Adherence Monitor',
        'user': user,
        'patientID': patientID,
        'meds_flags': meds_flags,			# Contains all the data needed for tables and plotting 
        'media_root': settings.MEDIA_ROOT,
        'patient_name': patient_name,
        'drug_class_array': sorted_drug_class_list,
        'oauth_header': urllib.quote(smart_oauth_header),
    })
    output = indexpage.render(variables)
    return HttpResponse(output)

    
#===================================================
# Creates data and serves information about 
# adherence for specific medications.
#===================================================
def risk(request):
    """ This function creates data and serves detailed  
    information about adherence for specific medications."""
	
	# Declare global variables that may be modified here
    global Global_PATIENT_ID 
    global Global_ADHERE_VARS 
	
    # Get the name of the drug if a specific one was requested.
    # The default is 'all' drugs.
    drug = request.GET.get('drug', 'all')
       
    # Current context information
    oa_params, client, smart_oauth_header = get_smart_client(request)
           
    # Get the medication list for this context
    medications = client.records_X_medications_GET()
    query = """
        PREFIX dcterms:<http://purl.org/dc/terms/>
        PREFIX sp:<http://smartplatforms.org/terms#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT  ?med ?name ?quant ?when
        WHERE {
            ?med rdf:type sp:Medication .
            ?med sp:drugName ?medc.
            ?medc dcterms:title ?name.
            ?med sp:fulfillment ?fill.
            ?fill sp:dispenseDaysSupply ?quant.
            ?fill dcterms:date ?when.
       }
       """    
    pills = medications.query(query)
    
    # The the fulfillment gap and MPR prediction data    
    meds_flags, gaps, refill_data, refill_day = Global_ADHERE_VARS

    names = []
    if drug == 'all':   # get all the drugs for this patient
        for pill in pills: 
            name = pill[1]
            names.append(name)
            d = pill[3]
    else: # only use the specified drug name
        meds_flags_new = []
        names.append(drug)      
        for item in meds_flags:
            if drug == item[0]:
                meds_flags_new.append(item)
        meds_flags = meds_flags_new 
                
    ad_data = []
    med_names = []

    for n in names:
        d = {}
        d["title"] = str(n)
        med_names.append(n)
        d["subtitle"] = 'adherence'
        d["measures"] = [1.0]
        ad_data.append(d)
           
    drug_class_array = {}
    for n in range(len(meds_flags)):
        drug_class_array[meds_flags[n][5]] = 1
    sorted_drug_class_array = sorted(drug_class_array.keys())
                            
    # Determine width and height of chart by the number of drugs to be shown
    width = 400
    height = 100
    if len(names) == 1:
        width = 500
        height = 200
    
    variables = RequestContext(request, {
                'head_title': u'Predicted 1-year medication possession ratio (MPR)',
                'med_names': med_names,
                'meds_flags': meds_flags,
                'refill_day': simplejson.dumps(refill_day),
                'refill': simplejson.dumps(refill_data),
                'gaps': simplejson.dumps(gaps),
                'width': width,
                'height': height,
                'drug_class_array': sorted_drug_class_array,
                'oauth_header': urllib.quote(smart_oauth_header),
                })     
    response = render_to_response("risk.html", context_instance=variables )
    return HttpResponse(response)

#===================================================
# Page to display information about the MPR
# Monitor app.
#===================================================
def about(request):
    """ This function creates a page with information about the MPR Monitor app."""
	
	# Get the template
    page = get_template('about.html')
            
    # Current context information
    oa_params, client, smart_oauth_header = get_smart_client(request)
    variables = Context({
        'oauth_header': urllib.quote(smart_oauth_header),
    })
    
	# Render the page
    output = page.render(variables)
    return HttpResponse(output)

#===================================================
# This function creates a page that gives instructions
# for using the MPR Monitor app.
#===================================================
def choose_med(request):
    """ This function creates a page with instructions for the MPR Monitor app."""
    page = get_template('choose_med.html')
    
    # Current context information
    oa_params, client, smart_oauth_header = get_smart_client(request)
    variables = Context({
        'oauth_header': urllib.quote(smart_oauth_header),
    })
    
	# Render the page
    output = page.render(variables)
    return HttpResponse(output)
	
#===================================================
# Convenience function to get oa_params and ret
# variables from the SmartClient and return them.
#===================================================
def get_smart_client(request):
    """ Initialize a new SmartClient and return oa_params, ret."""

    try:
        smart_oauth_header_quoted = request.GET.get('oauth_header')
        smart_oauth_header = urllib.unquote(smart_oauth_header_quoted)
    except:
        return "Couldn't find a parameter to match the name 'oauth_header'"

    oa_params = oauth.parse_header(smart_oauth_header)
    
    resource_tokens={'oauth_token':       oa_params['smart_oauth_token'],
                     'oauth_token_secret':oa_params['smart_oauth_token_secret']}
                     
    SMART_SERVER_PARAMS['api_base'] = oa_params['smart_container_api_base']
    SMART_SERVER_OAUTH['consumer_key'] = oa_params['smart_app_id']

    ret = smart.SmartClient(SMART_SERVER_OAUTH['consumer_key'], 
                       SMART_SERVER_PARAMS, 
                       SMART_SERVER_OAUTH, 
                       resource_tokens)
    ret.record_id=oa_params['smart_record_id']
    return oa_params, ret, smart_oauth_header

#===================================================
# Function to get birthday and patient name from
# the client records and return them.
#===================================================
def get_birthday_name(client):
    """Function to get birthday and patient name from the client records and return them."""
	    
    demographics = client.records_X_demographics_GET()
        
    query_demo = """
        PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        PREFIX v:<http://www.w3.org/2006/vcard/ns#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT  ?firstname ?lastname ?gender ?birthday
        WHERE {
               ?r v:n ?n .
               ?n rdf:type v:Name .
               ?n v:given-name ?firstname .
               ?n v:family-name ?lastname .
               ?r foaf:gender ?gender .
               ?r v:bday ?birthday .
        }
        """       
  
    # Get the birthday 
    demo = demographics.query(query_demo)
    for d in demo:
        patient_name = d[0] + " " + d[1]
        birthday = d[3]
        
    return birthday, patient_name


