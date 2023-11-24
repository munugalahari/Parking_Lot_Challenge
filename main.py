import json
import random
import string

import boto3
import creds


class ParkingLot:
    """
    Represents a parking lot with a certain number of parking spots.
    """

    def __init__(self, total_square_footage):
        """
        Initializes the parking lot with the specified total square footage.
        """
        self.total_square_footage = total_square_footage
        self.parking_spot_size = 8 * 12  # Assuming standard parking spot size of 8x12 feet
        self.num_parking_spots = self.total_square_footage // self.parking_spot_size
        self.parking_spots = [None] * self.num_parking_spots  # Initialize parking spots as empty

    def park_car(self, car, spot_number):
        """
        Attempts to park a car in the specified parking spot.
        If the spot is occupied, try to park in a different spot until successful.
        Returns a message indicating success and failure.
        """
        attempts = 0
        original_spot = spot_number
        while self.parking_spots[spot_number] is not None:
            spot_number = random.randint(0, self.num_parking_spots - 1)

            # If all spots are occupied, return a message indicating failure after a certain number of attempts
            attempts += 1
            if attempts > self.num_parking_spots:
                return f"Car with license plate {car.license_plate} could not park. Parking lot is full."

            print(
                f"Attempt {attempts}: Car with license plate {car.license_plate} trying to park in spot {spot_number}.")

        self.parking_spots[spot_number] = car
        return f"Car with license plate {car.license_plate} parked successfully in spot {spot_number}."

    def get_parked_vehicles_json(self):
        """
        Generates a JSON object representing the mapping of parked vehicles to parking spots.
        """
        return json.dumps(
            {spot_number: car.license_plate for spot_number, car in enumerate(self.parking_spots) if car is not None})


class Car:
    """
    Represents a car with a license plate.
    """

    def __init__(self, license_plate):
        """
        Initializes a car with the given license plate.
        """
        self.license_plate = license_plate

    def park(self, parking_lot, spot_number):
        """
        Attempts to park the car in the specified parking spot in the parking lot.
        Returns the result of the parking attempt.
        """
        return parking_lot.park_car(self, spot_number)

    def __str__(self):
        """
        Returns the license plate of the car.
        """
        return self.license_plate


def generate_license_plate():
    """
    Generates a random alphanumeric license plate with the first 3 characters from the alphabet
    and the remaining 4 characters from random numbers.
    """
    alphabets = random.choices(string.ascii_uppercase, k=3)
    numbers = random.choices(string.digits, k=4)
    return ''.join(alphabets + numbers)


def main():
    """
    Simulates parking cars in a parking lot, generates a JSON mapping of parked vehicles, and uploads it to an S3 bucket
    """
    # Create a parking lot with 2000 square feet of space
    parking_lot = ParkingLot(total_square_footage=2000)

    # Generate a list of 10 cars with random license plates
    cars = [Car(generate_license_plate()) for _ in range(10)]

    # Attempt to park each car in the parking lot until it's full or the car list is empty
    for car in cars:
        # Choose a random parking spot
        spot_number = random.randint(0, parking_lot.num_parking_spots - 1)

        # Park the car in the chosen spot
        result = car.park(parking_lot, spot_number)
        print(result)

        # Exit the loop if the parking lot is full
        if None not in parking_lot.parking_spots:
            print("Parking lot is full. Exiting program.")
            break

    # Generate a JSON mapping of parked vehicles to parking spots
    json_mapping = parking_lot.get_parked_vehicles_json()

    # Save the JSON mapping to a file
    with open('parking_lot_mapping.json', 'w') as file:
        file.write(json_mapping)

    try:
        session = boto3.Session(
            aws_access_key_id=creds.aws_access_key_id,
            aws_secret_access_key=creds.aws_secret_access_key,
        )
        s3 = session.client('s3')
        file_name = 'parking_lot_mapping.json'
        bucket_name = 'parking27'
        s3.upload_file(file_name, bucket_name, file_name)
        print(f"File {file_name} uploaded successfully to S3 bucket {bucket_name}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


if __name__ == "__main__":
    main()
