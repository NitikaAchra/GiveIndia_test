from flask import jsonify
from flask import Flask, url_for
from flask import request
from flask import Response
import datetime
import time
from urlparse import urlparse
app = Flask(__name__)


class Node:
    def __init__(self, dataval=None):
        self.dataval = dataval
        self.next = None

class SLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

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
active = {"GET":0,"POST":0,"PUT":0,"DELETE":0}


def insert_node(request_data):
    request_node = Node(request_data)
    if(request_list.head == None):
        request_list.head = request_node
        request_list.tail = request_node
    else:
        request_list.tail.next = request_node
        request_list.tail = request_list.tail.next

def get_stats():
    result = {"Total":{},"Last_hour":{},"Last_minute":{}, "Active":{}}
    requests = ["GET","POST","PUT","DELETE"]
    now = time.time()
    list_current = request_list.head
    list_prev = None

    while list_current != None:
        current_request = list_current.dataval
        next_request = list_current.next
        request_arrival = current_request["arrival_time"]
        request_type = current_request["type"]
        request_responsetime = current_request["response_time"]
        if ((now - request_arrival) > 3600) :
            last_hour[request_type]["total"] -= 1
            last_hour[request_type]["response_time"] -= request_responsetime
            if(list_prev != None):
                list_prev.next = list_current.next
            else:
                request_list.head = next_request
        if((now - request_arrival) > 60):
            last_minute[request_type]["total"] -= 1
            last_minute[request_type]["response_time"] -= request_responsetime
        list_prev = list_current
        list_current = next_request

    for request_type in requests:
        average_response = 0 if not total[request_type]["total"] else (total[request_type]["response_time"]/ total[request_type]["total"])
        result["Total"][request_type] = {"Total_requests ": total[request_type]["total"], 
                    "Average_responsetime ": average_response
                    }

        average_response = 0 if not last_hour[request_type]["total"] else (last_hour[request_type]["response_time"]/ last_hour[request_type]["total"])
        result["Last_hour"][request_type] = {"Total_requests ": last_hour[request_type]["total"], 
                    "Average_responsetime ": average_response
                    }

        average_response = 0 if not last_minute[request_type]["total"] else (last_minute[request_type]["response_time"]/ last_minute[request_type]["total"])
        result["Last_minute"][request_type] = {"Total_requests ": last_minute[request_type]["total"], 
                    "Average_responsetime ": average_response
                    }
        result["Active"][request_type] = active[request_type]
    return result

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp
    

@app.route('/stats', methods = ['GET', 'POST', 'PUT'])
def api_stats():
    stats = get_stats()
    resp = jsonify(stats)
    resp.status_code = 200
    return resp


@app.route('/process/', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def api_process():
    start = time.time()
    time.sleep(15)
    total[request.method]["total"] += 1
    last_hour[request.method]["total"] += 1
    last_minute[request.method]["total"] += 1
    active[request.method] +=1
    query_components = {}
    query = urlparse(request.url).query
    if(query):
        query_components = dict(qc.split("=") for qc in query.split("&"))
    response = {"timestamp": str(datetime.datetime.now()), 
                "method": request.method, 
                "path": request.path, 
                #"header": request.headers, 
                "body": request.data, 
                "query": query_components, 
                "duration": 15}
    resp = jsonify(response)
    resp.status_code = 200
    response_time = time.time() - start
    total[request.method]["response_time"] += response_time
    last_hour[request.method]["response_time"] += response_time
    last_minute[request.method]["response_time"] += response_time
    this_request =	{
            "type": request.method,
            "response_time": response_time,
            "arrival_time": start
            }
    insert_node(this_request)
    active[request.method] -=1
    return resp
    

if __name__ == '__main__':
    app.run()