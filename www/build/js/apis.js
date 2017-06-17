var host = "http://"+location.host;

percentage = function(size, total_size){
	return (size/total_size)*100
}

section_sizes = function(sections){
	sum = 0
	for(var i=0,keys = Object.keys(sections);i<keys.length; i++){
			sum+=sections[keys[i]]
	}
	return sum
}

percentage_graph = function(sections){
	percentage_graph_el = document.getElementById("percentage_graph");

	total_size = section_sizes(sections)

	for(var i=0, keys = Object.keys(sections);i<keys.length; i++){
			if(keys[i]=="__TEXT"){
				percentage_graph_el.innerHTML=percentage_graph_el.innerHTML+`<div class="progress-bar progress-bar-danger" style="width: ${percentage(sections[keys[i]],total_size)}%"></div>`
			}
			else{
				percentage_graph_el.innerHTML=percentage_graph_el.innerHTML+`<div class="progress-bar" style="background-color:${getRandomColor()}; width: ${percentage(sections[keys[i]],total_size)}%"></div>`
			}
	}
}

returnDate = function(){
	var d = new Date();
	return d.toDateString()+" "+d.toLocaleTimeString();
}

clear_lldb_console = function(){
	lldb_console = document.getElementById("lldb_console");
	lldb_console.value = "";
}

clear_command = function(){
	var command = document.getElementById("command")
	command.value = "";
	$('#command').typeahead('setQuery', '');
}

log_error_to_lldb_console = function(msg){
		console.log(msg);
		lldb_console = document.getElementById("lldb_console");
		
		if(lldb_console.value){
			lldb_console.value = lldb_console.value+"\n"+`[Error]\t`+msg;
		}
		else{
			lldb_console.value = `[Error]\t`+msg;	
		}

		set_caret_at_end(lldb_console);

		clear_command();

		var command = document.getElementById("command")
		set_caret_at_end(command);

}

log_to_lldb_console = function(msg){
		lldb_console = document.getElementById("lldb_console");

		if(lldb_console.value){
			lldb_console.value = lldb_console.value+"\n"+`[${returnDate()}]\t`+msg;
		}
		else{
			lldb_console.value = `[${returnDate()}]\t`+msg;	
		}

		set_caret_at_end(lldb_console);

		clear_command();

		var command = document.getElementById("command")
		set_caret_at_end(command);
}


run_command = function(command){

	log_to_lldb_console(command);

	if (command.startsWith("target create"))
		{
			// creating target
			set_target(command);
			return
		}
	else if(command=="clear"){
		// clear log console
		clear_lldb_console();
		return
	}

	else{
		send_command(command);

		return
	}
	
}

check_if_target = function(){
	url = "/if_target";

	var xhr = new XMLHttpRequest();
	xhr.withCredentials = true;

	xhr.addEventListener("readystatechange", function () {
		if (this.readyState === 4) {
				response = JSON.parse(this.responseText);
				if (response["success"]==true){

					disassembly 				= response["disassembly"]
					functions 					= response["functions"]
					strings 					= response["strings"]
					sections 					= response["sections"]
					sections_sizes 				= response["section_sizes"]
					entrypoint					= response["entrypoint"]
					context 					= response["context"]
					binary						= response["binary"]

					entrypoint_el = `<a href=#Entrypoint style="color:red" onclick="get_entrypoint_disassembly()">Entrypoint</a></li>`

					log_to_lldb_console(`target already exists: ${binary}`);
					highlight_context(context);
					highlight_disassembly(disassembly);
					highlight_functions(functions, entrypoint_el);
					highlight_strings(strings);
					highlight_sections(sections);
					
					percentage_graph(sections_sizes);
					// make context active
					// set_context_active();
					return

				}
				else{
					console.log("no target");
				}

			}
	});

	xhr.open('GET', host+url);
	xhr.send(null);	

}



set_target = function(command){
			url = "/set_target"

			var data = JSON.stringify({
				"command": command
			});

			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;

			xhr.addEventListener("readystatechange", function () {
				if (this.readyState === 4) {

						response = JSON.parse(this.responseText);
						if (response["success"]==true){

								disassembly 				= response["disassembly"]
								functions 					= response["functions"]
								strings 					= response["strings"]
								sections 					= response["sections"]
								sections_sizes 				= response["section_sizes"]
								entrypoint					= response["entrypoint"]
								context 					= response["context"]

								entrypoint_el = `<a href=#Entrypoint style="color:red" onclick="get_entrypoint_disassembly()">Entrypoint</a></li>`
								
								highlight_context(context);
								highlight_disassembly(disassembly);
								highlight_functions(functions, entrypoint_el);
								highlight_strings(strings);
								highlight_sections(sections);
								
								percentage_graph(sections_sizes);
								// make context active
								// set_context_active();
								return
							}

						else{
							log_error_to_lldb_console(response["error"]);
						}
					}
				});

				xhr.open("POST", host+url);
				xhr.setRequestHeader("content-type", "application/json");
				xhr.send(data);

}

send_command = function(command){

			url = "/run_command";

			var data = JSON.stringify({
				"command": command
			});

			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;

			xhr.addEventListener("readystatechange", function () {
				if (this.readyState === 4) {

						response = JSON.parse(this.responseText);
						if (response["success"]==true){
								log_to_lldb_console(response["output"]);
								
								var context = response["context"];
								highlight_context(context);

								// return			
							}

						else{
							log_error_to_lldb_console(response["error"]);
							return
						}
					}
				});

				xhr.open("POST", host+url);
				xhr.setRequestHeader("content-type", "application/json");
				xhr.send(data);
}