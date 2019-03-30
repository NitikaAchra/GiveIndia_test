from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json
import datetime
import time
from urlparse import urlparse
import re

class Node:
    def __init__(self, dataval=None):
        self.dataval = dataval
        self.next = None

class SLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None



class HTTPRequestHandler(BaseHTTPRequestHandler):

    total = {"GET":  {"total": 0, "response_time":0}, 
             "POST": {"total": 0, "response_time":0}, 
             "PUT":  {"total": 0, "response_time":0}, 
             "DELETE": {"total": 0, "response_time":0}}
    last_hour = {"GET":  {"total": 0, "response_time":0}, 
                "POST": {"total": 0, "response_time":0}, 
                "PUT":  {"total": 0, "response_time":0}, 
                "DELETE": {"total": 0, "response_time":0}}
    last_minute = {"GET":  {"total": 0, "response_time":0}, 
                "POST": {"total": 0, "response_time":0}, 
                "PUT":  {"total": 0, "response_time":0}, 
                "DELETE": {"total": 0, "response_time":0}}
    request_list = SLinkedList()

    def insert_node(self,request_data):
        request_node = Node(request_data)
        if(self.request_list.head == None):
            self.request_list.head = request_node
            self.request_list.tail = request_node
        else:
            self.request_list.tail.next = request_node
            self.request_list.tail = self.request_list.tail.next
    
    def toJSON(self,response):
        return json.dumps(response,default=lambda x: getattr(x, '__dict__', str(x)),
            sort_keys=True, indent=4)


    def create_response(self,header,body,path,method):
        response = {}
        if(re.search("^/process*", path)):
            query = urlparse(self.path).query
            query_components = {}
            if(query):
                query_components = dict(qc.split("=") for qc in query.split("&"))
            response = {"timestamp": str(datetime.datetime.now()), "method": method, "path": path, "header": header, "body": body, "query": query_components, "duration": 15}
        elif(re.search("^/stats$", path)):
            response = self.get_stats()   
        return response

    def get_stats(self):
        result = {"Total":{},"Last_hour":{},"Last_minute":{}}
        requests = ["GET","POST","PUT","DELETE"]
        now = time.time()
        list_current = self.request_list.head
        list_prev = None

        while list_current != None:
            current_request = list_current.dataval
            next_request = list_current.next
            request_arrival = current_request["arrival_time"]
            request_type = current_request["type"]
            request_responsetime = current_request["response_time"]
            if ((now - request_arrival) > 3600) :
                self.last_hour[request_type]["total"] -= 1
                self.last_hour[request_type]["response_time"] -= request_responsetime
                if(list_prev != None):
                    list_prev.next = list_current.next
                else:
                    self.request_list.head = next_request
            if((now - request_arrival) > 60):
                self.last_minute[request_type]["total"] -= 1
                self.last_minute[request_type]["response_time"] -= request_responsetime
            list_prev = list_current
            list_current = next_request

        for request_type in requests:
            average_response = 0 if not self.total[request_type]["total"] else (self.total[request_type]["response_time"]/ self.total[request_type]["total"])
            result["Total"][request_type] = {"Total_requests ": self.total[request_type]["total"], 
                        "Average_responsetime ": average_response
                        }

            average_response = 0 if not self.last_hour[request_type]["total"] else (self.last_hour[request_type]["response_time"]/ self.last_hour[request_type]["total"])
            result["Last_hour"][request_type] = {"Total_requests ": self.last_hour[request_type]["total"], 
                        "Average_responsetime ": average_response
                        }

            average_response = 0 if not self.last_minute[request_type]["total"] else (self.last_minute[request_type]["response_time"]/ self.last_minute[request_type]["total"])
            result["Last_minute"][request_type] = {"Total_requests ": self.last_minute[request_type]["total"], 
                        "Average_responsetime ": average_response
                        }

        return result



    def do_GET(self):
        self.total["GET"]["total"] += 1
        self.last_hour["GET"]["total"] += 1
        self.last_minute["GET"]["total"] += 1
        start = time.time()
        time.sleep(15)
        header = self.headers
        path = self.path
        response_data = self.create_response(header,"",self.path,"GET")
        if  not response_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("PATH NOT FOUND")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.toJSON(response_data))
        response_time = time.time() - start
        self.total["GET"]["response_time"] += response_time
        self.last_hour["GET"]["response_time"] += response_time
        self.last_minute["GET"]["response_time"] += response_time
        this_request =	{
                    "type": "GET",
                    "response_time": response_time,
                    "arrival_time": start
                    }
        self.insert_node(this_request)
       

    def do_POST(self):
        self.total["POST"]["total"] += 1
        self.last_hour["POST"]["total"] += 1
        self.last_minute["POST"]["total"] += 1
        start = time.time()
        time.sleep(15)
        content_length = int(self.headers['Content-Length'])
        header = self.headers
        body = self.rfile.read(content_length)
        response_data = self.create_response(header,body,self.path,"POST")
        if  not response_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("PATH NOT FOUND")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.toJSON(response_data))
        response_time = time.time() - start
        self.total["POST"]["response_time"] += response_time
        self.last_hour["POST"]["response_time"] += response_time
        self.last_minute["POST"]["response_time"] += response_time
        this_request =	{
                    "type": "POST",
                    "response_time": response_time,
                    "arrival_time": start
                    }
        self.insert_node(this_request)

    def do_PUT(self):
        self.total["PUT"]["total"] += 1
        self.last_hour["PUT"]["total"] += 1
        self.last_minute["PUT"]["total"] += 1
        now = datetime.datetime.now()
        start = time.time()
        time.sleep(15)
        content_length = int(self.headers['Content-Length'])
        header = self.headers
        body = self.rfile.read(content_length)
        response_data = self.create_response(header,body,self.path,"PUT")
        if  not response_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("PATH NOT FOUND")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.toJSON(response_data))
        response_time = time.time() - start
        self.total["PUT"]["response_time"] += response_time
        self.last_hour["PUT"]["response_time"] += response_time
        self.last_minute["PUT"]["response_time"] += response_time
        this_request =	{
                    "type": "PUT",
                    "response_time": response_time,
                    "arrival_time": start
                    }
        self.insert_node(this_request)

    def do_DELETE(self):
        self.total["DELETE"]["total"] += 1
        self.last_hour["DELETE"]["total"] += 1
        self.last_minute["DELETE"]["total"] += 1
        now = datetime.datetime.now()
        start = time.time()
        time.sleep(15)
        content_length = int(self.headers['Content-Length'])
        header = self.headers
        body = self.rfile.read(content_length)
        response_data = self.create_response(header,body,self.path,"DELETE")
        if  not response_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("PATH NOT FOUND")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.toJSON(response_data))
        response_time = time.time() - start
        self.total["DELETE"]["response_time"] += response_time
        self.last_hour["DELETE"]["response_time"] += response_time
        self.last_minute["DELETE"]["response_time"] += response_time
        this_request =	{
                    "type": "DELETE",
                    "response_time": response_time,
                    "arrival_time": start
                    }
        self.insert_node(this_request)

httpd = HTTPServer(('localhost', 8080), HTTPRequestHandler)
httpd.serve_forever()