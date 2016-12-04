# django-errorlog
Django reuseable app to collect the unexpcted exception then generate comprehansive report just like what you get in debug mode and store in database

Introduction
============
Django has it's own error handling machanism, which will send a email to the admin address configed in the settings. It works but there are some shortage.

1. The stack trace include in the email is as same as what you can see in console. It doesn't contains the varible value which can be very useful to debug.

2. Incovinient to trace the errors, it's a email, hard to catoegorized, and hard to track the status.
3. Some times one same error will bring you thousands of emails if this api happens to be visit a lot. You will waste a lot of time to find the different errors from the error happens most.

This module solves these problem in the following way.

1. We are love the Django buildin debug 500 page, it's contains almost all the information we need to debug, like the request infomation, the user, the settings, the stack trace with local vars, etc. So what we do, is to have a middleware to capture the unhandle exception then simply invoke the Django buildin reporter class to generate the full html report of the exception, then store in the database.
2. Each error item have the field to record a. fixed b. vcs version(support hg and git), you can `ignore` it after this bug has been addressed. Then it will gone from the `unfixed_error` list.
3. Errors will be categoried by the type of exception and the location where the exception been raised (location means the python file path and the method name). So in most case, same error that happened multiple times will be showed only once but with the count of how many times it's happend. Then when the error been ignore, all the same error will been marked as ignored.

This Module has been running in my company's website for more than 1 year and helps to solved thousands of bugs.

Change Logs
===========
2016-12-04: 0.1.0
Initial submit. Split the code from the online project. Write the documents, and add the tests. 


Install
=======
 
```bash
pip install django-errorlog
```
Then modify the settings
 
1. add `errorlog` in the INSTALLED_APPS  
2. if you are using django>=1.10, insert `errorlog.middlewares.ErrorLogMiddleware` in the `MIDDLEWARES` at the first line.
3. (optional) if you have your django project live inside a VCS(hg or git), set `VCS_SYSTEM = "hg"` or  `VCS_SYSTEM = "git"` to enable the erro rev tracking.

Then do `python manage.py migrate` to setup the database table.

Then when your views get an 500 error, there will be a new log item stored.


Usage
=====
 buildin shell command
------------------
```python
>>> from errorlog.models import Error
>>> Error.unfixed_errors
{0: <Error:     1 - /test/2/ - ValueError: A>,
 1: <Error:     4 - /test/1/ - ValueError: B>}
>>> error = Error.unfixed_errors[1]
>>> error
 1: <Error:     4 - /test/1/ - ValueError: B>
>>> # in this repr, the first number is the index to make it easy to select; 
>>> # the second number 4 is the the count of the same error happened;
>>> # /test/1/ is the uri of the api;
>>> # ValueError is the exception type; 
>>> # B is the args in the exception.
>>> error.vcs_rev # the git/hg version of error, for hg, it's the incremental number that is orderable
"1"
>>> error.ignore() # this command ignore the whole 4 error logs
```

Django admin
------------
If you use django buildin admin, you should be able to find the Error in the home page.

If you want to see the html error report, you need to build the view youself to transfer the error_html to the browser.

Advance Usage
--------------
You can use Error.log_exception to log one specific error in one certain scope. 

```python
from errorlog.models import Error
with Error.log_exception("name", reraise=False):
	do_something_here()

```
If `reraise = True`, then after being loged, the exception will keep raising out. Caution, if you have database atomic open, since unhandle error will make django to rollback the transaction, so this log will also been rollbacked.

If `reraise = False`, then it will log the exception then stop propogation and continue to run the following code. It's as same as the following code

```python
try:
	do_something_here()
except Exception as e:
    pass
```

Here is an example of how I using it

```python
with Error.log_exception("send_email_through_mailgun", reraise=False):
	response=requests.post(url,parms)
	content=response.content
	status_code=response.status_code
	if status_code!=200:
		raise ValueError("Mailgun failed")
other_stuff()
```
So that I can capture when the mailgun's api return an error, and keep the stuff going.