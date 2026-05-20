import time
import schedule

def retrain():

    print("Retraining model...")

schedule.every().day.at("18:00").do(
    retrain
)

while True:

    schedule.run_pending()

    time.sleep(60)