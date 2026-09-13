"""
ShadowVoid Recon Module
Dark web OSINT, ARP/NetBIOS scanning, Cloud mapping
"""

import sys
import os
import time
import json
import subprocess
import platform
import socket
from datetime import datetime


class ReconModule:
    def __init__(self, core):
        self.core = core
        self.tor_router = None
        if hasattr(self.core, 'tor_router'):
            self.tor_router = self.core.tor_router

    def scan(self, target, scan_type='full'):
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'scans': {}
        }
        if scan_type in ['full', 'onion']:
            results['scans']['onion'] = self.scan_onion(target)
        if scan_type in ['full', 'i2p']:
            results['scans']['i2p'] = self.scan_i2p(target)
        if scan_type in ['full', 'arp']:
            results['scans']['arp'] = self.scan_arp(target)
        if scan_type in ['full', 'netbios']:
            results['scans']['netbios'] = self.scan_netbios(target)
        if scan_type in ['full', 'cloud']:
            results['scans']['cloud'] = self.scan_cloud(target)
        return results

    def scan_onion(self, target):
        results = {'type': 'onion', 'target': target, 'services': []}
        try:
            if target.endswith('.onion'):
                if self.tor_router and self.tor_router.is_available():
                    results['services'].append({'address': target, 'status': 'active', 'ports': []})
            else:
                from core import DomainGenerator
                dga = DomainGenerator()
                test_domains = dga.generate_domains(50)
                for domain in test_domains:
                    if domain.endswith('.onion'):
                        results['services'].append({'address': domain, 'status': 'possible', 'ports': []})
        except Exception as e:
            results['error'] = str(e)
        return results

    def scan_i2p(self, target):
        results = {'type': 'i2p', 'target': target, 'services': []}
        try:
            from core import I2PRouter
            router = I2PRouter()
            if router.is_available():
                results['services'].append({'address': target + '.i2p', 'status': 'active'})
        except Exception as e:
            results['error'] = str(e)
        return results

    def scan_arp(self, target):
        results = {'type': 'arp', 'target': target, 'hosts': []}
        try:
            if platform.system() == 'Linux':
                output = subprocess.check_output(['arp-scan', '--localnet'],
                                              stderr=subprocess.DEVNULL, timeout=30).decode()
                for line in output.split('\n'):
                    if ':' in line and '.' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            results['hosts'].append({
                                'ip': parts[0],
                                'mac': parts[1],
                                'manufacturer': parts[2] if len(parts) > 2 else 'Unknown'
                            })
        except Exception as e:
            results['error'] = str(e)
        return results

    def scan_netbios(self, target):
        results = {'type': 'netbios', 'target': target, 'hosts': []}
        try:
            if platform.system() == 'Linux':
                output = subprocess.check_output(['nmblookup', '-A', target],
                                              stderr=subprocess.DEVNULL, timeout=10).decode()
                for line in output.split('\n'):
                    if ':' in line and '.' in line:
                        results['hosts'].append({'info': line.strip()})
        except Exception as e:
            results['error'] = str(e)
        return results

    def scan_cloud(self, target):
        results = {'type': 'cloud', 'target': target, 'assets': []}
        try:
            cloud_domains = [
                target + '.aws.amazon.com',
                target + '.azurewebsites.net',
                target + '.cloud.google.com',
                target + '.herokuapp.com',
                target + '.digitaloceanspaces.com'
            ]
            for domain in cloud_domains:
                try:
                    socket.gethostbyname(domain)
                    results['assets'].append({'type': 'cloud', 'domain': domain, 'status': 'resolved'})
                except:
                    pass
        except Exception as e:
            results['error'] = str(e)
        return results
