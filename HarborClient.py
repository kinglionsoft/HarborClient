#!/usr/bin/env python
#coding=utf-8

import requests
import json
from urllib import parse

class HarborClient:

    def __init__(self, base_url, user_name, password):
        self.base_url = base_url
        self.user_name = user_name
        self.password = password
        self.session_id_key = 'sid'
        # self.csrf = '__csrf'
        # self.gorilla_csrf = '_gorilla_csrf'
        self.headers =  {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Content-Type':'application/json'
        }
        self.cookie=self.login_get_csrf_token()
        self.csrf_token = self.cookie.get('__csrf')
        self.headers['X-Harbor-CSRF-Token'] = self.csrf_token
        self.session_id= self.login_get_session_id()
        self.cookie[self.session_id_key] = self.session_id

    def login_get_csrf_token(self):
        '''
        通过log_out获取到csrf_token
        :return:
        '''
        url = '%s/c/log_out' % (self.base_url)
        response = requests.get(url, headers = self.headers)
        dic = response.cookies.get_dict()
        return dic

    def login_get_session_id(self):
        header_dict = {
            'Accept':'application/json, text/plain, */*',
            'Connection':'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Harbor-CSRF-Token': self.csrf_token
        }
        data_dict = {
            'principal': self.user_name,
            'password': self.password
        }
        req_url = '%s/c/login' % (self.base_url)
        response = requests.post(req_url, data=data_dict, headers=header_dict, cookies = self.cookie, verify=False)

        if 200 == response.status_code:
            return response.cookies.get(self.session_id_key)
        else:
            raise Exception(response.json())

    def delete_artifact(self, project_name, repository_name, reference):
        req_url = '%s/api/v2.0/projects/%s/repositories/%s/artifacts/%s' % (self.base_url, project_name, repository_name, parse.quote(reference))
        response = requests.delete(req_url, cookies = self.cookie, headers = self.headers)
        if response.status_code != 200:
            print('delete %s:%s failed: %s' %(repository_name, reference, response.text))

    def get_artifacts(self, project_name, repository_name):
        req_url = '%s/api/v2.0/projects/%s/repositories/%s/artifacts?page=1&page_size=1000&with_tag=false&with_label=true&with_scan_overview=false&with_signature=false&with_immutable_status=false' % (self.base_url, project_name, repository_name)
        response = requests.get(req_url, cookies = self.cookie)
        result = response.json()
        if response.status_code == 200:
            return result
        else:
            raise Exception(result)

    def clean_artifacts(self, project_name, repository_name, keep = 1):
        print('cleaning ' + repository_name)
        artifacts = self.get_artifacts(project_name, repository_name)
        for a in artifacts[keep:]:
            self.delete_artifact(project_name, repository_name, a['digest'])

    def get_repositories(self, project_name):
        req_url = '%s/api/v2.0/projects/%s/repositories?page=1&page_size=1000' % (self.base_url, project_name)
        response = requests.get(req_url, cookies = self.cookie)
        result = response.json()
        if response.status_code == 200:
            return result
        else:
            raise Exception(result)

    def clean_project(self, project_name):
        repositories = self.get_repositories(project_name)
        pre_len = len(project_name) + 1
        for r in repositories:
            repository = r['name'][pre_len:]
            self.clean_artifacts(project_name, repository)


if __name__ == '__main__' :
    client = HarborClient('<Harbor api base url>', '<username>', '<password>')
    client.clean_project('<project name>')