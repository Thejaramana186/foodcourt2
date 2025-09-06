from app import create_app #import flask app from the app package 

app = create_app() #instance  call the function to create a flask application 

if __name__ == '__main__': #start the flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
    #run the flask application