import bottle
from bottle import run, request, Bottle

def main():
    request_handler = Bottle()

    @request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
    def alert_unregisered_serial(serial):
        print ("Serial {} is unregistered.".format(serial))

    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()