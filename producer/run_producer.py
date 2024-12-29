from Producer import Producer


if __name__ == "__main__":
    producer = Producer()

    for i in range(10000):
        # producer(r"C:\Users\ASUS\Desktop\github_projects\traffic_analyser\videos\vlc-record-2024-12-22-18h18m06s-Screen_Recording_20241222_164344_YouTube.mp4-.mp4")
        producer(r"C:\Users\ASUS\Desktop\github_projects\Parking\parking-management\main_vid__300.mp4")
