#!/usr/bin/python3
''' Automatic tests on the beyt_cafe
These set of tests check if the website is reachable
'''

import sys
import subprocess

command = "kubectl describe service coffeeshop | grep Ingress | awk '{print $3}'"
completed_process = subprocess.run(command, shell=True, text=True, capture_output=True)
site_port = "80"
site_url = completed_process.stdout
site_url = site_url.replace("\n", "")

import pytest
import os
import urllib.request

def test_webserver():
    '''Test 2: checks if the webserver is responding to requests'''
    #check if website is up
    url = urllib.request.urlopen("http://"+site_url+":"+site_port)
    assert url.getcode() == 200
    check_coffee = os.system("curl http://"+site_url+" | grep Espresso")

def test_api():
    #checks the api
    url = urllib.request.urlopen("http://"+site_url+":"+site_port+"/api")
    assert url.getcode() == 200
