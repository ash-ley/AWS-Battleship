#!/usr/bin/python
from time import sleep
from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher
import boto3
import requests
import sys

bucketName = "battleship-ta-ash-game"
sqsQueue = "player-turn-queue"

def authenticate():
    provider = InstanceMetadataProvider(iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2))
    creds = provider.load().get_frozen_credentials()
    session = boto3.session.Session(region_name='eu-west-1', aws_access_key_id=creds.access_key, aws_secret_access_key=creds.secret_key, aws_session_token=creds.token)
    return session

def getName():
    playerName = requests.get('http://169.254.169.254/latest/meta-data/tags/instance/Name')
    return playerName.text

def getBattleboard(playerName):
    session = authenticate()
    ssm = session.client('ssm')
    if playerName == "Player-1":
        battleboard = ssm.get_parameter(Name='/battleship/player-1')
    elif playerName == "Player-2":
        battleboard = ssm.get_parameter(Name='/battleship/player-2')
    
    return battleboard['Parameter']['Value']

def putBattleboard(playerName, battleboard):
    session = authenticate()
    ssm = session.client('ssm')
    if playerName == "Player-1":
        battleboard = ssm.put_parameter(
            Name='/battleship/player-1',
            Value=battleboard,
            Overwrite=True
            )
    elif playerName == "Player-2":
        battleboard = ssm.put_parameter(
            Name='/battleship/player-2',
            Value=battleboard,
            Overwrite=True
            )

def putOpponentBattleboard(playerName, battleboard):
    session = authenticate()
    ssm = session.client('ssm')
    if playerName == "Player-1":
        battleboard = ssm.put_parameter(
            Name='/battleship/player-2',
            Value=battleboard,
            Overwrite=True
            )
    elif playerName == "Player-2":
        battleboard = ssm.put_parameter(
            Name='/battleship/player-1',
            Value=battleboard,
            Overwrite=True
            )

def getCoordinates(position):
    if int(position.split(',')[0]) == 1:
        choice = 1 + (int(position.split(',')[1]) - 1)
    elif int(position.split(',')[0]) == 2:
        choice = 6 + (int(position.split(',')[1]) - 1)
    elif int(position.split(',')[0]) == 3:
        choice = 11 + (int(position.split(',')[1]) - 1)
    elif int(position.split(',')[0]) == 4:
        choice = 16 + (int(position.split(',')[1]) - 1)
    elif int(position.split(',')[0]) == 5:
        choice = 21 + (int(position.split(',')[1]) - 1)
    
    return choice

def placeShips(playerName, battleboard):
    myShips = []
    battleboard = list(battleboard)
    for _ in range(3):
        format = False
        while format == False:
            ship = verifyInputPlace()
            format = True
            for x in myShips:
                if ship in x:
                    format = False
                    print("Ship is already placed here, pick again.")
        myShips.append(ship)
        
        counter = 1
        for position,char in enumerate(battleboard):
            if char == '-' or char == 'S' or char == '@' or char == '*':
                if counter == getCoordinates(ship):
                    battleboard[position] = "S"
                counter += 1
    putBattleboard(playerName, ''.join(battleboard))

def shootShip(playerName):
    session = authenticate()
    if playerName == "Player-1":
        battleboard = getBattleboard("Player-2")
    elif playerName == "Player-2":
        battleboard = getBattleboard("Player-1")
    
    battleboard = list(battleboard)
    checkWinner(battleboard, playerName)

    verifyShot = False
    while verifyShot == False:
        shoot = verifyInput()
        counter = 1
        for position,char in enumerate(battleboard):
            if char == '-' or char == 'S' or char == '@' or char == '*':
                if counter == getCoordinates(shoot):
                    if char == '*' or char == '@':
                        print("This coordinate has already been targeted, choose again.")
                        verifyShot = False
                    else:
                        if battleboard[position] == "S":
                            battleboard[position] = "@"
                            print("You just sunk a battleship, take another shot!")
                        elif battleboard[position] == "-":
                            battleboard[position] = "*"
                            print("You missed")
                            verifyShot = True
                counter += 1

    putOpponentBattleboard(playerName, ''.join(battleboard))
    sendSQS(playerName)

def verifyInput():
    wrong = "Wrong coordinates. Examples would be 5,2 1,3 3,3 etc"
    while True:
        shoot = input("Where would you like to shoot? ")
        if len(shoot) == 3:
            if shoot[0].isnumeric and shoot[1] == "," and shoot[2].isnumeric:
                verify = shoot.split(",")

                if verify[0].isnumeric() is True:
                    if verify[1].isnumeric() is True:
                        if int(verify[0]) >= 1 and int(verify[0]) <= 5:
                            if int(verify[1]) >= 1 and int(verify[1]) <= 5:
                                break
                            else:
                                print(wrong)
                        else:
                            print(wrong)
                    else:
                        print(wrong)
                else:
                    print(wrong)
            else:
                print(wrong)
        else:
            print(wrong)
    return shoot

def verifyInputPlace():
    wrong = "Wrong coordinates. Examples would be 5,2 1,3 3,3 etc"
    while True:
        ship = input("Where would you like to place your ship? ")
        if len(ship) == 3:
            if ship[0].isnumeric and ship[1] == "," and ship[2].isnumeric:
                verify = ship.split(",")

                if verify[0].isnumeric() is True:
                    if verify[1].isnumeric() is True:
                        if int(verify[0]) >= 1 and int(verify[0]) <= 5:
                            if int(verify[1]) >= 1 and int(verify[1]) <= 5:
                                break
                            else:
                                print(wrong)
                        else:
                            print(wrong)
                    else:
                        print(wrong)
                else:
                    print(wrong)
            else:
                print(wrong)
        else:
            print(wrong)
    return ship

def checkWinner(battleboard, playerName):
    session = authenticate()
    s3 = session.client('s3')
    if 'S' not in battleboard:
        print(f"Congratulations {playerName} you win!!")
        winTxt = f"{playerName} has won the game"

        s3.put_object(
            Bucket=bucketName,
            Key='winner',
            Body=winTxt
        )
        sys.exit(1)
    else:
        fileFound = False
        objects = s3.list_objects_v2(Bucket=bucketName)
        for object in objects['Contents']:
            if "winner" in object['Key']:
                fileFound = True
        if (fileFound): 
            object = s3.get_object(
                Bucket=bucketName,
                Key='winner'
            )
            winMsg = object['Body'].read().decode('utf-8')
            print(f"Commiserations, {winMsg}")
            cleanUp()
            sys.exit(1)

def rpsLogic(playerName, hand, opponent):
    if hand == "R" and opponent == "S":
        winner = playerName
    elif hand == "P" and opponent == "R":
        winner = playerName
    elif hand == "S" and opponent == "P":
        winner = playerName
    elif hand == opponent:
        winner = "draw"
    else:
        if playerName == "Player-1":
            winner = "Player-2"
        else:
            winner = "Player-1"
    return winner

def decideStart(playerName):
    session = authenticate()
    s3 = session.client('s3')
    checker = False

    while checker != True:
        hand = input("Let's decide who goes first with a game of Rock, Paper, Scissors\nEnter R/P/S: ")
        if hand.upper() == "R" or hand.upper() == "P" or hand.upper() == "S":
            hand = hand.upper()
            checker = True
        else:
            print("Invalid choice. You can only select R/P/S")
    if playerName == "Player-1":
        s3.put_object(
            Bucket=bucketName,
            Key='player1/rps',
            Body=hand
        )

        print("Checking opponents hand..")
        waiter = s3.get_waiter('object_exists')
        waiter.wait(
            Bucket=bucketName,
            Key='player2/rps',
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 20
            }
        )
        object = s3.get_object(
                Bucket=bucketName,
                Key='player2/rps'
            )
        opponent = object['Body'].read().decode('utf-8')
        playerStart = rpsLogic(playerName, hand, opponent)
    elif playerName == "Player-2":
        s3.put_object(
            Bucket=bucketName,
            Key='player2/rps',
            Body=hand
        )

        print("Checking opponents hand..")
        waiter = s3.get_waiter('object_exists')
        waiter.wait(
            Bucket=bucketName,
            Key='player1/rps',
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 20
            }
        )
        object = s3.get_object(
                Bucket=bucketName,
                Key='player1/rps'
            )
        opponent = object['Body'].read().decode('utf-8')
        playerStart = rpsLogic(playerName, hand, opponent)

    cleanS3(playerName, bucketName)

    if playerStart == 'draw':
        print(f"It's a draw, your hand: {hand} your opponent: {opponent}\nChoose again!")
        decideStart(playerName)
    
    return playerStart

def cleanS3(playerName, bucketName):
    session = authenticate()
    s3 = session.client('s3')
    if playerName == "Player-1":
        s3.delete_object(
            Bucket=bucketName,
            Key='player1/rps'
        )
    else:
        s3.delete_object(
            Bucket=bucketName,
            Key='player2/rps'
        )

def cleanUp():
    session = authenticate()
    ssm = session.client('ssm')
    s3 = session.client('s3')
    s3.delete_object(
            Bucket=bucketName,
            Key='winner'
        )

def sendSQS(playerName):
    session = authenticate()
    sqs = session.client('sqs')

    if playerName == "Player-1":
        body = "Player-2"
    else:
        body = "Player-1"

    queueUrl = getQueue()
    
    sqs.send_message(
        QueueUrl=queueUrl,
        MessageBody=body
    )

def getQueue():
    session = authenticate()
    sqs = session.client('sqs')
    queue = sqs.get_queue_url(
        QueueName=sqsQueue
    )
    return queue["QueueUrl"]

def pollSQS(playerName):
    session = authenticate()
    sqs = session.client('sqs')
    queueUrl = getQueue()

    msg = sqs.receive_message(
        QueueUrl=queueUrl,
        MaxNumberOfMessages=1,
        VisibilityTimeout=2,
        WaitTimeSeconds=20
    )
    return msg[0]['Body']

def main(result):
    playerName = getName()
    placeShips(playerName, getBattleboard(playerName))
    start = decideStart(playerName)

    if start == "Player-1":
        print(getBattleboard(playerName))
        shootShip(playerName)
        sendSQS(playerName)
    elif start == "Player-2":
        print(getBattleboard(playerName))
        shootShip(playerName)
        sendSQS(playerName)
    while result != "win" or result != "lose":
        if pollSQS(playerName) == playerName:
            print(getBattleboard(playerName))
            shootShip(playerName)
        else:
            print("Waiting for other player to make their move")
            sleep(10)

if __name__ == "__main__":
    main("start")
