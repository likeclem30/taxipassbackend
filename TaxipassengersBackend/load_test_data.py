from taxipassengers_backend.app import create_app
from taxipassengers_backend.models import PassengerModel
from datetime import datetime

if __name__ == '__main__':
    application = create_app()
    application.app_context().push()

    # Create some test data
    test_data = [
        (1, "Jane", "Doe", '1979-7-30', "jane.doe@email.com", "07012345678",
         "No 1 House, Area Name", "09:00",
         "No 1 Office, Street Name", "05:00",
         "card", 1, 1),
        (2, "Jon", "Doe", '1975-1-30', "jon.doe@email.com", "08123456789",
         "No 1 House, Area Name", "06:30",
         "No 1 Office, Street Name", "03:50",
         "card", 1, 0),
        (3, "Craig", "Watson", '1985-11-20', "craig.watson@email.com", "09012345678",
         "No 1 House, Area Name", "08:00",
         "No 1 Office, Street Name", "04:00",
         "card", 0, 0),
        (4, "Sandy", "Berg", '1980-4-10', "sandy.berg@email.com", "09123456789",
         "No 1 House, Area Name", "07:15",
         "No 1 Office, Street Name", "04:15",
         "card", 0, 1),
    ]

    for authId, firstName, lastName, dob, email, phone, \
        homeLocation, homePickupTime, workLocation, workPickupTime, paymentMethod, \
        emailStatus, phoneNumberStatus in test_data:
        user = PassengerModel(
            authId=authId,
            firstName=firstName,
            lastName=lastName,
            dateOfBirth=dob,
            email=email,
            phoneNumber=phone,
            homeLocation=homeLocation,
            homePickupTime=homePickupTime,
            workLocation=workLocation,
            workPickupTime=workPickupTime,
            paymentMethod=paymentMethod,
            emailStatus=emailStatus,
            phoneNumberStatus=phoneNumberStatus,
            timestamp=datetime.now()
        )

        application.db.session.add(user)

    application.db.session.commit()
