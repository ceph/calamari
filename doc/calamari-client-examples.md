Client XHR Examples
===================

Authenticate
------------

 URL `/api/v1/auth/login/`
 
 Notice the trailing '/'. This is a Django URL so it has a trailing slash. Examples are using httpie.
 
1. Perform a 'GET'. This will set your session and csrf cookie values which are used to verify the header token.
  
 		http -v --form --session mira022 POST mira022.front.sepia.ceph.com:8000/api/v1/auth/login/

2. This will return a cookie containing the CSRF token in the header. Use this as the input to a form POST to the same URL: 			

		http -v --form --session mira022 POST mira022.front.sepia.ceph.com:8000/api/v1/auth/login/ X-CSRFToken:EUCXsEf2NMZfVAkpjErZExhmmdtFNsAu username=admin password=admin submit="Log in"
		
3. This will return a `302` redirect to accounts/profile by default, but you can easily set the location by setting the parameter `next`. e.g. next=/dashboard

4. You should now be logged in. You can use authenticated APIs now like POSTs to /api/v1/user by supplying the token `X-CSRFToken` in the header. This is what an authenticated POST would look like:

		http -v --session mira022 POST mira022.front.sepia.ceph.com:8000/api/v1/user X-CSRFToken:EUCXsEf2NMZfVAkpjErZExhmmdtFNsAu

		POST /api/v1/user HTTP/1.1
		Accept: */*
		Accept-Encoding: gzip, deflate, compress
		Content-Length: 0
		Cookie: csrftoken=EUCXsEf2NMZfVAkpjErZExhmmdtFNsAu; sessionid=ke9fl9jqwfxjurf5oaejotm58bupiqia
		Host: mira022.front.sepia.ceph.com:8000
		User-Agent: HTTPie/0.6.0
		X-CSRFToken: EUCXsEf2NMZfVAkpjErZExhmmdtFNsAu

		HTTP/1.0 400 BAD REQUEST
		Allow: GET, POST, HEAD, OPTIONS
		Content-Type: application/json; charset=utf-8
		Date: Thu, 18 Jul 2013 21:39:23 GMT
		Server: WSGIServer/0.1 Python/2.6.6
		Vary: Accept, Cookie

		{
    		"password": [
        		"This field is required."
    		],
    		"username": [
        		"This field is required."
    		]
		}
		
	If you aren't authenticated you will see this:
	

		http -v POST mira022.front.sepia.ceph.com:8000/api/v1/user
	
		POST /api/v1/user HTTP/1.1
		Accept: */*
		Accept-Encoding: gzip, deflate, compress
		Content-Length: 0
		Host: mira022.front.sepia.ceph.com:8000
		User-Agent: HTTPie/0.6.0



		HTTP/1.0 403 FORBIDDEN
		Allow: GET, POST, HEAD, OPTIONS
		Content-Type: application/json; charset=utf-8
		Date: Thu, 18 Jul 2013 21:42:04 GMT
		Server: WSGIServer/0.1 Python/2.6.6
		Vary: Accept, Cookie	

		{
    		"detail": "Authentication credentials were not 	provided."
		}