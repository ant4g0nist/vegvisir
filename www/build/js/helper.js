colors = ["#000080", "#00008B", "#0000CD", "#0000FF", "#008080", "#008B8B", "#00BFFF", "#00CED1", "#00FF00", "#00FFFF", "#191970", "#1E90FF", "#40E0D0", "#4169E1", "#4682B4", "#483D8B", "#48D1CC", "#5F9EA0", "#6495ED", "#663399", "#66CDAA", "#6A5ACD", "#6B8E23", "#7B68EE", "#7FFF00", "#7FFFD4", "#800000", "#800080", "#808000", "#87CEEB", "#87CEFA", "#8A2BE2", "#8B008B", "#8B4513", "#9370DB", "#9400D3", "#9932CC", "#A0522D", "#A52A2A", "#ADD8E6", "#AFEEEE", "#B0C4DE", "#B0E0E6", "#B22222", "#B8860B", "#BA55D3", "#BC8F8F", "#BDB76B", "#C0C0C0", "#CD853F", "#D2691E", "#D2B48C", "#D8BFD8", "#DA70D6", "#DAA520", "#DC143C", "#DCDCDC", "#DDA0DD", "#DEB887", "#E0FFFF", "#E6E6FA", "#E9967A", "#EE82EE", "#EEE8AA", "#F08080", "#F0E68C", "#F0FFF0", "#F0FFFF", "#F4A460", "#F5DEB3", "#F5F5DC", "#F5F5F5", "#F5FFFA", "#F8F8FF", "#FA8072", "#FAEBD7", "#FAF0E6", "#FAFAD2", "#FDF5E6", "#FF00FF", "#FF1493", "#FF6347", "#FF69B4", "#FF7F50", "#FF8C00", "#FFA07A", "#FFA500", "#FFB6C1", "#FFC0CB", "#FFD700", "#FFDAB9", "#FFDEAD", "#FFE4B5", "#FFE4C4", "#FFE4E1", "#FFEBCD", "#FFEFD5", "#FFF0F5", "#FFF5EE", "#FFF8DC", "#FFFACD", "#FFFAF0", "#FFFAFA", "#FFFF00", "#FFFFE0", "#FFFFF0", "#FFFFFF"]

rand_item = function rand(items){
    return items[~~(Math.random() * items.length)];
}

getRandomColor = function(){
    return rand_item(colors);
}


lazy_load = function(div_tag_id, ul_tag_id){
	var mincount = 20;
	var maxcount = 40;

	$("#"+ul_tag_id+" li").slice(20).hide();

	$("#"+div_tag_id).scroll(function() {

		if($("#"+div_tag_id).scrollTop() + $("#"+div_tag_id).height() >= $("#"+div_tag_id)[0].scrollHeight) {

			$("#"+ul_tag_id+" li").slice(mincount, maxcount).fadeIn(1000);

			mincount = mincount+20;
			maxcount = maxcount+20;

		}
	});
}

isHex = function(sNum){
  return (typeof sNum === "string") && ! isNaN( parseInt(sNum, 16) );
}

clear_registers    = function(){
	var registers_table = document.getElementById("registers");
    var rowCount = registers_table.rows.length;
    for (var i = rowCount - 1; i > 0; i--) {
        registers_table.deleteRow(i);
    }

}

clear_disassembly  = function(element){
  	if(element){
  		var disassembly_table = element;	
  	}
  	else{
  		var disassembly_table = document.getElementById("disassembly_ul");	
  	}
	// disassembly_table = document.getElementById("disassembly_ul")
    var rowCount = disassembly_table.rows.length;
    for (var i = rowCount - 1; i > 0; i--) {
        disassembly_table.deleteRow(i);
    }
}

highlight_disassembly = function(disassembly, element){
  	clear_disassembly(element);

  	if(element){
  		var disassembly_table = element;	
  	}
  	else{
  		var disassembly_table = document.getElementById("disassembly_ul");	
  	}
	
	var keys = Object.keys(disassembly);

	for(var i=0; i<keys.length; i++){
		key = keys[i]
		var asm = disassembly[key]
		var addr = key
		var bytes  = asm["bytes"]
		var mnemonic = asm["mnemonic"]
		var ops	=	asm["ops"]

		var row  = disassembly_table.insertRow()
		var cell = row.insertCell(0)
		cell.innerHTML = `<a href='#${addr}'>${addr}</a>`

		var cell = row.insertCell(1)
		cell.innerHTML = mnemonic

		//highlight the address so it'd be possible to add jumps to that.
		var cell = row.insertCell(2)
		if (isHex(ops)){
			cell.innerHTML = `<a href='#${ops}' style="color:red">${ops}</a>`
		}
		else{
			cell.innerHTML = ops
		}

		var cell = row.insertCell(3)
		cell.innerHTML = bytes
	}

	if(element){
		return
	}

	// set_disassembly_active();

}

highlight_strings = function(strings){

    strings_table = document.getElementById("strings");
    names = Object.keys(strings);
    var table_op = []
    for(var i=0; i<names.length; i++){
      offset 		= names[i]
      string 	    = strings[offset]

      // create cells
      op = `<tr>
                <td>${offset}</td>
                <td>${string}</td>
              </tr>
            `
      table_op.push(op)
      // var row  = strings_table.insertRow()
      // var cell = row.insertCell(0)
      // cell.innerHTML = name
      //
      // var cell = row.insertCell(1)
      // cell.innerHTML = offset
    }
    $(".clusterize-scroll").height($(".functions_dissassembly").height());
    var clusterize = new Clusterize({
      rows: table_op,
      scrollId: 'scrollArea',
      contentId: 'contentArea'
    });


}

highlight_sections    = function(sections){
  sections_table = document.getElementById("sections_ul");
	var names = Object.keys(sections);
	console.log(names, sections)
	for(var i=0; i<names.length; i++){
		name 		= names[i]
		file_addr 	= sections[name]["file_addr"]
		file_offset = sections[name]["file_offset"]
		file_size 	= sections[name]["file_size"]
		perm 		= sections[name]["perm"]

		// create cells
		var row  = sections_table.insertRow()
		var cell = row.insertCell(0)
		cell.innerHTML = name

		var cell = row.insertCell(1)
		cell.innerHTML = file_addr

		var cell = row.insertCell(2)
		cell.innerHTML = file_offset

		var cell = row.insertCell(3)
		cell.innerHTML = file_size

		var cell = row.insertCell(4)
		cell.innerHTML = perm

		if(perm.indexOf("x")>-1){
			cell.style.color = "red";
		}
	}
}

highlight_functions   = function(functions, entrypoint_el){
	// external/imported functions
	imported_functions_div = document.getElementById("imported_functions_div");

	// internal
	functions_div = document.getElementById("functions_div");

	var names = Object.keys(functions);

	var imported_functions 	= []
	var funcs 			= []

	for(var i=0, function_names = Object.keys(functions); i< function_names.length; i++)
		{
			name = function_names[i]
			start_addr = functions[name]["start_addr"]
			end_addr = functions[name]["end_addr"]
			external = functions[name]["external"]
			
			if(external){
					imported_functions.push(`<li class="list-unstyled"><a href=#${name} onclick="get_disassembly('${name}','${start_addr}','${end_addr}')">${name}</a></li>`) 
			}
			else{
				funcs.push(`<li class="list-unstyled"><a href=#${name} onclick="get_disassembly('${name}','${start_addr}','${end_addr}')">${name}</a></li>`) 
			}
		}

		functions_div.innerHTML 			=  entrypoint_el + funcs.join(" ");
		imported_functions_div.innerHTML	=  imported_functions.join(" ");

}

highlight_registers = function(registers){
	clear_registers();
	registers_table = document.getElementById("registers")

	registers = registers["qword"];
	
	for(var i=0; i<registers.length; i++){
		name 		= registers[i]["reg"];
		value 		= registers[i]["value"];

		// create cells
		var row  = registers_table.insertRow()
		var cell = row.insertCell(0)
		cell.innerHTML = `${name} : ${value}` 

		
		// var cell = row.insertCell(1)
		// cell.innerHTML = value
	}

}


highlight_context = function(context){
	// registers, disas, jump, address or None, msg
	if(context[0]){

		var registers 	= context[0];
		var disassembly = context[1];
		var symbol		= context[2]
		var jump 		= context[3];
		
		if(jump)
			{
				var address = context[4];
				// disassembly--> goes in context

				var jump_el = document.getElementById("context_jump");
				jump_el.innerText = `jumping to :${address}`;
			}
			else{

				var jump_el = document.getElementById("context_jump");
				jump_el.innerText = `jump False`;	

			}

			var context_disassembly_el = document.getElementById("context_disassembly");
			highlight_disassembly(disassembly, context_disassembly_el);

			var symbol_el = document.getElementById("context_symbol");
			symbol_el.innerText = ` Name  :  ${symbol}`; 
			highlight_registers(registers);

			// context = document.getElementById("context");

	}
	else{
		console.log(context[1]);
	}

}

load_lldb_help_modal = function(){

		var lldb_help_modal = document.getElementById("lldb_help_modal")
        var commands_els = []

		for(var i=0,commands=Object.keys(lldb_commands_help);i<commands.length;i++){

					var command = commands[i];
					var info 	= lldb_commands_help[command];

					var row  = lldb_help_modal.insertRow()
					var cell = row.insertCell(0)
					cell.innerHTML = command

					var cell = row.insertCell(1)
					cell.innerHTML = info
		}

}

set_caret_at_end = function(elem) {
        var elemLen = elem.value.length;
        elem.selectionStart = elemLen;
        elem.selectionEnd = elemLen;
        elem.focus();
    }

set_disassembly_active = function(){
		// get tabs_ul--> check active child, change it back to context
		var tabs_ul = document.getElementById('tabs_ul');
		var active	= tabs_ul.querySelector(".active");

		if (active.id=="disassembly_li"){
			return 
		}

		var disassembly	= tabs_ul.querySelector("#disassembly_li");
		disassembly.setAttribute("class", "active");
		active.setAttribute("class", "");

		//
		var tabs_div = document.getElementById('tabs_content');
		var active	= tabs_div.querySelector(".active");
		var disassembly	= tabs_div.querySelector("#disassembly");

		disassembly.setAttribute("class", "tab-pane active");
		active.setAttribute("class", "tab-pane");

		return true
}

set_context_active = function(){
		// get tabs_ul--> check active child, change it back to context
		var tabs_ul = document.getElementById('tabs_ul');
		var active	= tabs_ul.querySelector(".active");
		var context	= tabs_ul.querySelector("#context_li");
		context.setAttribute("class", "active");
		active.setAttribute("class", "");

		//
		var tabs_div = document.getElementById('tabs_content');
		var active	= tabs_div.querySelector(".active");
		var context	= tabs_div.querySelector("#context");

		context.setAttribute("class", "tab-pane active");
		active.setAttribute("class", "tab-pane");

		return true
}

get_disassembly = function(function_name, start_addr, end_addr){
	url = `/get_disassembly?func=${function_name}&start_addr=${start_addr}&end_addr=${end_addr}`

	var xhr = new XMLHttpRequest();
	xhr.withCredentials = true;
	xhr.addEventListener("readystatechange", function () {
			if (this.readyState === 4) {
				response = JSON.parse(this.responseText);
				if (response["success"]==true){
					
					highlight_disassembly(response["disassembly"])					
					set_disassembly_active();
				}
				else{
					console.log('damn');
				}
			}
	});

	xhr.open("GET", host+url);
	xhr.setRequestHeader("content-type", "application/json");
	xhr.send(null);	
}

get_entrypoint_disassembly = function(){
	url = "/get_entrypoint_disassembly"

	var xhr = new XMLHttpRequest();
	xhr.withCredentials = true;
	xhr.addEventListener("readystatechange", function () {
			if (this.readyState === 4) {
				response = JSON.parse(this.responseText);
				if (response["success"]==true){
					
					highlight_disassembly(response["disassembly"])					
				}
				else{
					console.log('damn');
				}
			}
	});

	xhr.open("GET", host+url);
	xhr.setRequestHeader("content-type", "application/json");
	xhr.send(null);	

}
