import httpx

def simple_wsgi_app(environ, start_response):
    """A simple WSGI application that returns 'hello'."""
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'hello']

def main():
                                             
    transport = httpx.WSGITransport(app=simple_wsgi_app)

                                                     
                                                                            
    with httpx.Client(transport=transport, base_url="http://testserver") as client:
        response = client.get("/")

                           
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    main()
