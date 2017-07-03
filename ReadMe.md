# Vegvisir:

	A browser based GUI for **LLDB** Debugger. 

## Screenshot:
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/target_create.png)

# Installation:

### Note:
 	Please use the default python that comes with MacOS which is available at /usr/bin/python. This is because the LLDB framework currently only supports default python on MacOS.

~~~
	^^/D/p/Vegvisir >>> which python
	/usr/bin/python

	^^/D/p/Vegvisir >>> python -V
	Python 2.7.10
	
	^^/D/p/Vegvisir >>> sudo pip install -r requirements.txt

~~~

#Usage:

~~~
	^^/D/p/Vegvisir >>> python vegvisir.py

	^^/D/p/Vegvisir >>> #and then point browser to http://127.0.0.1:8086
~~~

## Donation:

If you like the project, you can buy me beers :) 

[![Donate Bitcoin](https://img.shields.io/badge/donate-bitcoin-green.svg)](https://ant4g0nist.github.io)

# Views

### index
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/blank.png)

### auto_suggest
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/auto_suggest.png)

### target_create
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/target_create.png)

### disassembly
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/funcs.png)

### funcs_imported
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/funcs_imported.png)

### sections
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/sections.png)

### strings
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/strings.png)

### help
![Screenshot](https://raw.githubusercontent.com/ant4g0nist/vegvisir/master/Screenshots/help.png)


# Code Sucks:
	Duhhh, the code sucks big time. Lesser the time, more the suckyness. You guys could help me fix things ;)

# TODO:

- [ ] Make lldbcontroller more reliable.
- [ ] Add hex memory view along with search.
- [ ] Add lisa.py support.
- [ ] Make it a pip package.
- [ ] Log events, modules, application stdout and stderr on frontend
- [ ] Better auto suggest of commands
- [ ] keyboard short cuts

### Thanks:

- Capstone
- lldb
- hacker-bootstrap
- adminlte
- typeahead.js
- @happilycoded 
- [@argentum47](https://github.com/argentum47) for help with CSS and stuff

