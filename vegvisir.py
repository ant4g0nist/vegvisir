#!/usr/bin/python

import os
import json
from app.config import config
from app.core import lldbcontroller as LLDBController
from flask import Flask, request, Response, render_template, jsonify
from flask_cors import CORS

name 	= "vegvisir"
app     = Flask(name ,template_folder="www", static_folder="www/")

app.config.update(
    DEBUG=True,
 	TEMPLATES_AUTO_RELOAD=True
)

CORS(app, supports_credentials=False)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://%s:%s'%(config.HOST, config.PORT))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,auth')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'false')
    response.headers.add('Access-Control-Expose-Headers', 'auth')

    return response

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/if_target', methods=["GET"])
def if_target():
	try:
		if lldbContr.ifTarget():
			
			entrypoint 				= lldbContr.getEntryPoint()
			functions 				= lldbContr.doReturnFunctions()
			sections,section_sizes  = lldbContr.doReturnSections()
			disassembly  			= lldbContr.capDisassemble(long(entrypoint, 16), 0x100)
			strings					= lldbContr.doReturnStrings()
			context					= lldbContr.context()
			binary					= lldbContr.exe
			return jsonify({"success":True, "binary":binary, "entrypoint":entrypoint, "functions":functions,"sections":sections,"section_sizes":section_sizes,"disassembly":disassembly,"strings":strings,"context":context})
		else:
			print 'No target'
			return jsonify({"success":False,"targe":False})

	except Exception,e:
		return jsonify({"success":False,"error":"%s"%e})


@app.route('/set_target', methods=["POST"])
def set_target():
	req = request.json
	path = str(req["command"]).replace("target create ","")

	if path and os.path.isfile(path):
		lldbContr.setTarget(str(path), "")
		lldbContr.capstoneinit()

		if lldbContr.target:
			entrypoint 				= lldbContr.getEntryPoint()
			functions 				= lldbContr.doReturnFunctions()
			sections,section_sizes  = lldbContr.doReturnSections()
			disassembly  			= lldbContr.capDisassemble(long(entrypoint,16), 0x100)
			strings					= lldbContr.doReturnStrings()
			context					= lldbContr.context()

			return jsonify({"success":True, "entrypoint":entrypoint, "functions":functions,"sections":sections,"section_sizes":section_sizes,"disassembly":disassembly,"strings":strings,"context":context})

	return jsonify({"success":False, "error":"Please give a valid binary path."})

@app.route('/run_command', methods=['POST'])
def run_command():
	req = request.json
	command = str(req["command"])

	try:
		success, op = lldbContr.runCommands(command)

		if success:
			context	= lldbContr.context();
			return jsonify({"success":True,"output":op,"context":context})

		return jsonify({"success":False,"error":op})

	except Exception, e:
		return jsonify({"success":False, "error":"There was an error while running the command. Error:%s"%(e)})		

@app.route('/get_disassembly', methods=['GET'])
def get_disassembly():

	func_name 	= str(request.args.get("func"))
	start_addr 	= str(request.args.get("start_addr"))
	end_addr 	= str(request.args.get("end_addr"))
	
	disassembly = lldbContr.disassemble(func_name, start_addr, end_addr)

	if disassembly:
		return jsonify({"success":True, "disassembly":disassembly})

	return jsonify({"success":False, "error":"non readable"})

@app.route('/get_entrypoint_disassembly', methods=['GET'])
def get_entrypoint_disassembly():
	entrypoint 				= lldbContr.getEntryPoint()
	disassembly  			= lldbContr.capDisassemble(long(entrypoint,16), 0x100)

	if disassembly:
		return jsonify({"success":True, "disassembly":disassembly})

	return jsonify({"success":False, "error":"non readable"})

if __name__ == '__main__':

	lldbContr 	= 	LLDBController.LLDBController()

	app.run(host=config.HOST, port=config.PORT)
