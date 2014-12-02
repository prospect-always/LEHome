#!/usr/bin/env python
# encoding: utf-8
# Copyright 2014 Xinyu, He <legendmohe@foxmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import argparse
import threading
import time
import urllib, urllib2
from util.Res import Res
from util.log import *


class remote_server_proxy:
    
    HOST = "http://lehome.sinaapp.com"
    NO_HEAD_FLAG = "*"
    CMD_FETCH_INTERVAL = 3

    def __init__(self, address):
        if not address is None:
            INFO("connect to server: %s " % (address))
            self._home_address = address

            settings = Res.init("init.json")
            self._device_id = settings['id']
            self._trigger_cmd = settings['command']['trigger'][0].encode("utf-8")
            self._finish_cmd = settings['command']['finish'][0].encode("utf-8")
            INFO("load device id:%s" % self._device_id)
        else:
            ERROR("address is empty")

    def _send_cmd_to_home(self, cmd):
        if not cmd is None and not cmd == "":
            INFO("send cmd %s to home." % (cmd, ))
            if cmd.startswith(remote_server_proxy.NO_HEAD_FLAG):
                cmd = cmd[1:]
            else:
                cmd = "%s%s%s" % (self._trigger_cmd, cmd, self._finish_cmd)

            try:
                data = {"cmd": cmd}
                enc_data = urllib.urlencode(data)
                response = urllib2.urlopen(self._home_address, enc_data).read()
            except urllib2.HTTPError, e:
                ERROR(e)
                return False
            except urllib2.URLError, e:
                ERROR(e)
                return False
            else:
                INFO("home response: " + response)
                return True
        else:
            ERROR("cmd is invaild.")
            return False

    def start(self):
        self._fetch_worker()
        # fetch_t = threading.Thread(
        #             target=self._fetch_worker
        #             )
        # fetch_t.daemon = True
        # fetch_t.start()

    def _fetch_worker(self):
        INFO("start fetching cmds from remote server.")
        while True :
            try:
                DEBUG("sending fetch request to remote server.")
                url = remote_server_proxy.HOST + "/cmd/fetch?id=" + self._device_id
                req = urllib2.Request(url)
                cmds = urllib2.urlopen(req, timeout=10).read()
                if len(cmds) != 0 and cmds != "error":
                    INFO("fetch cmds:%s" % cmds)
                    for cmd in cmds.split("|"):
                        self._send_cmd_to_home(cmd)
            except (KeyboardInterrupt, SystemExit):
                raise
            except urllib2.URLError, e:
                WARN(e)
            except Exception, ex:
                ERROR(ex)
            time.sleep(remote_server_proxy.CMD_FETCH_INTERVAL)
        self._sock_context.term()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description='cmd_http_server.py -a address')
    parser.add_argument('-a',
                        action="store",
                        dest="address",
                        default="http://localhost:8000/home/cmd",
                        )
    args = parser.parse_args()
    address = args.address

    INFO("remote server proxy is activate.")
    remote_server_proxy(address).start()