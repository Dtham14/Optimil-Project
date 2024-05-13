from main import create_app

app = create_app()

# host="0.0.0.0" opens local host 
# need to go to windows firewall ->advanced settings -> new inbound rule for this flask app -> tcp port 5000 

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)