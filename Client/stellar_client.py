from re import U
# from stellar_sdk.keypair import Keypair
# #stellar_sdk.server used to connect to Stellar-core through the Horizon API
# from stellar_sdk.server import Server
# #stellar_sdk.network is used to get the Passphrase of either the test or main Stellar network 
# from stellar_sdk.network import Network
# #TransactionBuilder is used to create 
# from stellar_sdk import TransactionBuilder
# #stellar_sdk.exceptions is used for Error Dectection in transactions
# from stellar_sdk.exceptions import NotFoundError,BadResponseError,BadRequestError
# #requests is used to initiate the transaction between friendbot and the Public keys
import requests

import mysql.connector      
from input_manager import InputManager
from hashlib import sha256
import time
from cryptography.fernet import Fernet




class StellarClient:

    def __init__(self):
        self.mySQLConfig = {
                        'user': 'sql5436993',
                        'password': 'v7F7jRWVFc',
                        'host': 'sql5.freesqldatabase.com',
                        'database': 'sql5436993',
                        'raise_on_warnings': True
                        }
        pass

    def SQL_initialize(self):
        self.connection = mysql.connector.connect(**self.mySQLConfig)

    def SQL_execute_oneway_statement(self,query):
        try:
            statement = self.connection.cursor()

            statement.execute(query)

            self.connection.commit()

            statement.close()

            queryExecuted = True
        except TypeError as e:
            # InputManager.display_message(f"Error: {e}")
            queryExecuted = False

        
        return queryExecuted
    
    def SQL_execute_twoway_statement(self,query):
        try:
            statement = self.connection.cursor()

            statement.execute(query)

            data = []

            queryResult = statement.fetchone()

            while (queryResult != None):
                registry = queryResult
                data.append(registry)

                queryResult = statement.fetchone()
            
            # print(data)
            
            statement.close()
        except Exception as e:
            # InputManager.display_message(f"Error: {e}")
            data = "Error in query"
        return data
            




    def process_data(self):                                                                                     #<---------- Handles all data required inputs for account creation ---------->
        
        while True:      
                                                                                                   #Starts loop until the new account ID entered is not already registered. 
            #REPLACE WITH STREAMLIT INPUT                                                        
            profileID = InputManager.define_string("Please enter your new account ID")              #Enters the new account ID.
            hashedProfileID = sha256(profileID.encode()).hexdigest()                                #Hashes it and turns it into hex string

            query = f"SELECT EXISTS(SELECT * FROM UserLoginData WHERE hashedUsername = '{hashedProfileID}') "       #Prepares SQL query

            queryResult = self.SQL_execute_twoway_statement(query)[0][0]                                            #Because the function returns an array with tuples, we want the first registry and the first element from the tuple.

            if queryResult:                                                                     #If the account is already registered, display message and continue in loop.
                InputManager.display_message("This account ID is already registered, please try another one")
            else:                                                                                               #If the account is not registered, break the loop.
                break


        #REPLACE WITH STREAMLIT INPUT 
        profileName = InputManager.define_string("Please enter your full name:")                                #Enters the person name.
        #REPLACE WITH STREAMLIT INPUT 
        profileAge = InputManager.define_numbers(message="Please enter your age (Must be greater or equal than 18):", infLimit = 18,typeOfNumber = int)             #Enters the person age with bounds.
        #REPLACE WITH STREAMLIT INPUT 
        profileSex = InputManager.define_string("Please enter the letter corresponding to your sex (Male = M) (Female = F):")                                       #Enters the person sex.
        #REPLACE WITH STREAMLIT INPUT 
        profilePassword = sha256(InputManager.define_string(message="Please enter your password, must be minimum 6 characters long, maximum 30:", infLimit=6, supLimit=30).encode()).hexdigest()   #Enters the new account password with length bounds and hashes it.
        #REPLACE WITH STREAMLIT INPUT 
        publicKey = InputManager.define_string("Please your public key:") 
        #REPLACE WITH STREAMLIT INPUT 
        privateKey = InputManager.define_string("Please your private key:") 

        #Prepares data into a hashMap (Dictionary)
        profileData = {"Username": profileID, "HashedUsername": hashedProfileID, "Name": profileName, "Age": profileAge, "Sex": profileSex, "Password": profilePassword, "PublicKey": publicKey, "PrivateKey": privateKey}      

        return profileData      

    def create_account(self): #Full creation of an account process

        profileData = self.process_data()  #Gets all the needed data for the creation of an account

        encryptKey = Fernet.generate_key()  #Generates a unique encryption key
        fernetKey = Fernet(encryptKey)      #Generates a Fernet object for encrypting things with the key in bytes format
        encryptKey = Fernet.generate_key().decode()     #Passes the key to a string

        #QUERIES FOR UserLoginData TABLE

        query = f"INSERT INTO UserLoginData VALUES(\"{profileData['HashedUsername']}\" , \"{profileData['Password']}\", \"{encryptKey}\")"  #Prepares the SQL query
        queryResult = self.SQL_execute_oneway_statement(query)                                                                              #Executes the SQL query

        if not queryResult:                                                                                 #If this query wasn't successful, print error.
            InputManager.display_message("There was an error while creating your account, query 1")
            return

        #QUERIES FOR UserData TABLE
        usernameSpecialHash = profileData["Username"]+"WDSI"                                                    #We salt the username with a 'WSDI' string for more security
        usernameSpecialHash = sha256(usernameSpecialHash.encode()).hexdigest()                                  #We hash the username

        bytesPrivateKey = profileData["PrivateKey"].encode()                                                    #Gets the private key and pass it into a bytes format
        encryptedPrivateKey = fernetKey.encrypt(bytesPrivateKey).decode()                                       #Encrypts the private key and pass it to string

        bytesName = profileData["Name"].encode()                                                                #Passes the name and pass it into bytes format
        encryptedName = fernetKey.encrypt(bytesName).decode()                                                   #Encrypts the name and pass it to string

        balances = "{}"

        query2 = f"INSERT INTO UserData VALUES(\"{usernameSpecialHash}\",\"{encryptedPrivateKey}\",\"{encryptedName}\", \"{profileData['Sex']}\", {profileData['Age']},\"{balances}\")" #Prepares SQL query
        queryResult2 = self.SQL_execute_oneway_statement(query2)

        if not queryResult2:                                                                                    #If this query wasn't successful, print error.
            InputManager.display_message("There was an error while creating your account, query 2")
            return

        #QUERIES FOR UserPublicKey TABLE
    
        query3 = f"INSERT INTO UserPublicKey VALUES(\"{profileData['Username']}\",\"{profileData['PublicKey']}\")"
        queryResult3 = self.SQL_execute_oneway_statement(query3)

        if not queryResult3:
            InputManager.display_message("There was an error while creating your account, query 2")
            return

        InputManager.display_message("Account succesfully created")                                         #If no errors, display successful creation


    def initialize_client(self):
        self.SQL_initialize()
        while True:                                                                 #Main loop that runs the client console menu.
            print("")
            print("*****************************************************")
            print("WELCOME TO THE STELLAR NETWORK P2P SERVICE")
            print("")
            print("1) Log in")                                                      #Option for log in into your account by typing 1.
            print("2) Create account")                                              #Option for creating an account by typing 2.
            print("3) Exit")                                                        #Option for exiting the menu by typing 3.
            print("")
            print("*****************************************************")
            selectedOption = InputManager.define_numbers(message="Type a number according to your selected option", infLimit = 1, supLimit = 3,typeOfNumber = int) #Calls InputManager function for entering a bounded number and repeating until the number is accepted.
            if selectedOption == 3:                                                 #What it executes when you exit the menu.
                print()
                print("THANKS FOR USING THE STELLAR NETWORK P2P SERVICE")
                print()
                break                                                               #Breaks the main loop and exits the program.
            if selectedOption == 1: #Not coded yet                                  #Executes what you need to log in into your account.
                pass
                # logFlag = self.log_in()                                             #Calls the log in service, if is successful returns 'True' else returns 'False'.
                # if logFlag:                                                         #If the log in service is successful, call the main logged menu.
                    # self.main_menu()

            if selectedOption == 2:                                                 #Executes the necessary for creating an account.
                self.create_account()         



if __name__ == "__main__":
    client = StellarClient()
    client.initialize_client()