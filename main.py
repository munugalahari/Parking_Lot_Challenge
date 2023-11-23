import json
import random
import boto3


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
        Returns a message indicating success or failure.
        """
        if self.parking_spots[spot_number] is not None:
            return f"Car with license plate {car.license_plate} failed to park in spot {spot_number} bcoz it is already occupied."
        else:
            self.parking_spots[spot_number] = car
            return f"Car with license plate {car.license_plate} parked successfully in spot {spot_number}."

    def get_parked_vehicles_json(self):
        """
        Generates a JSON object representing the mapping of parked vehicles to parking spots.
        """
        parked_vehicles = {}
        for spot_number, car in enumerate(self.parking_spots):
            if car is not None:
                parked_vehicles[spot_number] = car.license_plate
        return json.dumps(parked_vehicles)


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


def main():
    """
    Simulates parking cars in a parking lot, generates a JSON mapping of parked vehicles, and uploads it to an S3 bucket.
    """
    # Create a parking lot with 2000 square feet of space
    parking_lot = ParkingLot(total_square_footage=2000)

    # Generate a list of 10 cars with random license plates
    cars = []
    for _ in range(10):
        license_plate = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(7))
        cars.append(Car(license_plate))

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

    session = boto3.Session(
        aws_access_key_id='AKIAWOYP2WEGO4IZGGEG',
        aws_secret_access_key='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',
    )
    s3 = session.client('s3')
    file_name = 'parking_lot_mapping.json'
    bucket_name = 'parking27'
    s3.upload_file(file_name, bucket_name, file_name)


if __name__ == "__main__":
    main()
