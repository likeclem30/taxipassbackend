import http.client
from datetime import datetime, timedelta

from flask import abort
from flask_restplus import Namespace, Resource, fields
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from taxipassengers_backend import config
from taxipassengers_backend.db import db
from taxipassengers_backend.models import PassengerModel
from taxipassengers_backend.templates.sms import template
from taxipassengers_backend.token import validate_token_header
from taxipassengers_backend.utils import html_to_string, format_string, send_notification

api = Namespace('api', description='General API operations')


def authentication_header_parser(value):
    payload = validate_token_header(value, config.PUBLIC_KEY)
    if payload is None:
        abort(401)
    return payload


def check_admin_return_payload(parser, super=False):
    args = parser.parse_args()
    tokenPayload = authentication_header_parser(args['Authorization'])

    # check if user is an admin
    if 'admin' not in tokenPayload:
        abort(403)

    # for super admin
    if super:
        if tokenPayload['admin'] != 1:
            abort(403)

    return tokenPayload


# Output formats
model = {
    'id': fields.Integer(),
    'authId': fields.Integer(),
    'firstName': fields.String(),
    'lastName': fields.String(),
    'dateOfBirth': fields.String(),
    'email': fields.String(),
    'phoneNumber': fields.String(),
    'image': fields.String(),
    'rating': fields.Float(),
    'homeLocation': fields.String(),
    'homePickupTime': fields.String(),
    'workLocation': fields.String(),
    'workPickupTime': fields.String(),
    'paymentMethod': fields.String(),
    'phoneNumberStatus': fields.Integer(),
    'emailStatus': fields.Integer(),
    'suspendedAt': fields.DateTime(),
    'updateTimestamp': fields.DateTime(),
    'timestamp': fields.DateTime(),
}
passengerModel = api.model('Passenger', model)

# Input formats
authenticationParser = api.parser()
authenticationParser.add_argument('Authorization',
                                  location='headers',
                                  type=str,
                                  help='Bearer Access Token')

passengerParser = authenticationParser.copy()
# passengerParser.add_argument(
#     'authId',
#     type=int,
#     required=True,
#     help='Passenger\'s authentication Id'
# )
passengerParser.add_argument('first',
                             type=str,
                             required=True,
                             help='User first name')
passengerParser.add_argument('last',
                             type=str,
                             required=True,
                             help='Passenger\'s last name')
passengerParser.add_argument(
    'dob',
    type=str,
    required=False,
    help="Passenger's date of birth format, example '1975-12-30'")
passengerParser.add_argument('email',
                             type=str,
                             required=True,
                             help="Passenger's Email Address")
passengerParser.add_argument('phone',
                             type=str,
                             required=True,
                             help="Passenger's Phone Number")
passengerParser.add_argument('image',
                             type=str,
                             required=False,
                             help="Passenger's Profile image")
passengerParser.add_argument('homeLocation',
                             type=str,
                             required=False,
                             help="Home Address of passenger")
passengerParser.add_argument('homePickupTime',
                             type=str,
                             required=False,
                             help="Passenger's home pickup time")
passengerParser.add_argument('workLocation',
                             type=str,
                             required=False,
                             help="Work Address of passenger")
passengerParser.add_argument('workPickupTime',
                             type=str,
                             required=False,
                             help="Passenger's Work pickup time")
passengerParser.add_argument('paymentMethod',
                             type=str,
                             required=False,
                             help="Payment Method")
passengerParser.add_argument(
    'emailStatus',
    type=int,
    choices=(0, 1),
    required=False,
    help="Has passenger's email address been verified")
passengerParser.add_argument('phoneNumberStatus',
                             type=int,
                             choices=(0, 1),
                             required=False,
                             help="Has passenger's phone number been verified")

updatePassengerParser = passengerParser.copy()
# updatePassengerParser.remove_argument('authId')
updatePassengerParser.replace_argument('first',
                                       type=str,
                                       required=False,
                                       help='Passenger\'s first name')
updatePassengerParser.replace_argument('last',
                                       type=str,
                                       required=False,
                                       help='Passenger\'s last name')
updatePassengerParser.replace_argument('username',
                                       type=str,
                                       required=False,
                                       help='Passenger\'s username')
updatePassengerParser.replace_argument('email',
                                       type=str,
                                       required=False,
                                       help="Passenger's Email Address")
updatePassengerParser.replace_argument('phone',
                                       type=str,
                                       required=False,
                                       help="Passenger's Phone Number")
updatePassengerParser.add_argument('suspend',
                                   type=int,
                                   choices=(0, 1),
                                   required=False,
                                   help="Suspend user")
updatePassengerParser.add_argument('rating',
                                   type=float,
                                   required=False,
                                   help="User's rating")

filterParser = authenticationParser.copy()
filterParser.add_argument('search',
                          type=str,
                          location='args',
                          help='Search for passenger by first name')
filterParser.add_argument('status',
                          type=str,
                          choices=('active', 'suspended'),
                          location='args',
                          help='Filter by passenger status')
filterParser.add_argument('phoneStatus',
                          type=str,
                          choices=('unverified', 'verified'),
                          location='args',
                          help='Filter by passenger\'s phone number status')
filterParser.add_argument('emailStatus',
                          type=str,
                          choices=('unverified', 'verified'),
                          location='args',
                          help='Filter by passenger\'s email status')

dateQuery_parser = authenticationParser.copy()
dateQuery_parser.add_argument('startdate',
                              type=str,
                              required=True,
                              help="The start date format '%d/%m/%Y'")
dateQuery_parser.add_argument('enddate',
                              type=str,
                              required=True,
                              help="The end date format '%d/%m/%Y'")

monthQuery_parser = authenticationParser.copy()
monthQuery_parser.add_argument('year',
                               type=str,
                               required=True,
                               help='The year')


@api.route('/get/auth/<int:authId>/')
class GetPassenger(Resource):
    @api.doc('get_auth_passenger')
    @api.marshal_with(passengerModel)
    @api.expect(authenticationParser)
    def get(self, authId: int):
        """
        Get passenger from auth Id
        """
        args = authenticationParser.parse_args()
        authentication_header_parser(args['Authorization'])

        passenger = (
            PassengerModel.query.filter(
                PassengerModel.authId == authId
            ).first()
        )
        if not passenger:
            # The passenger does not exist
            return '', http.client.NOT_FOUND

        return passenger


@api.route('/me/passenger/')
class MePassenger(Resource):
    @api.doc('get_passenger')
    @api.marshal_with(passengerModel)
    @api.expect(authenticationParser)
    def get(self):
        """
        Get passenger from id in bearer token
        """
        args = authenticationParser.parse_args()
        payload = authentication_header_parser(args['Authorization'])

        passenger = (PassengerModel.query.filter(
            PassengerModel.authId == payload['id']).first())
        if not passenger:
            # The passenger does not exist
            return '', http.client.NOT_FOUND

        return passenger

    @api.doc('create_passenger')
    @api.expect(passengerParser)
    def post(self):
        """
        Create a new passenger
        """

        args = passengerParser.parse_args()
        payload = authentication_header_parser(args['Authorization'])

        passenger = (PassengerModel.query.filter(
            PassengerModel.authId == payload['id']).first())
        if passenger:
            result = {
                'result': 'Auth Id has already been used to create a passenger'
            }
            return result, http.client.UNPROCESSABLE_ENTITY

        newPassenger = PassengerModel(authId=payload['id'],
                                      firstName=args['first'],
                                      lastName=args['last'],
                                      dateOfBirth=args['dob'],
                                      email=args['email'],
                                      phoneNumber=args['phone'],
                                      image=args['image'],
                                      homeLocation=args['homeLocation'],
                                      homePickupTime=args['homePickupTime'],
                                      workLocation=args['workLocation'],
                                      workPickupTime=args['workPickupTime'],
                                      paymentMethod=args['paymentMethod'],
                                      emailStatus=1,
                                      timestamp=datetime.utcnow())

        db.session.add(newPassenger)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return '', http.client.UNPROCESSABLE_ENTITY

        # todo: update
        data = {
            'firstName': args['first'],
            'receiverNo': args['last'],
            'pin': '1234'
        }

        email_message = html_to_string('templates/email/welcome.html',
                                       data=data)
        sms_message = format_string(template.WELCOME_MSG, data=data)

        data = {
            'phoneNumber': args['phone'],
            'email': args['email'],
            'subject': "Welcome To Lagos State Intermodal System!",
            'typeMessage': 'Welcome Message',
            'Authorization': args['Authorization']
        }

        send_notification(data, email_message, sms_message)

        result = api.marshal(newPassenger, passengerModel)
        return result, http.client.CREATED


@api.route('/passenger/')
class PassengerList(Resource):
    @api.doc('list_passengers')
    @api.marshal_with(passengerModel, as_list=True)
    @api.expect(filterParser)
    def get(self):
        """
        Retrieve all passengers
        """
        args = filterParser.parse_args()
        authentication_header_parser(args['Authorization'])

        query = PassengerModel.query
        if args['search']:
            search_param = args['search']
            param = f'%{search_param}%'
            query = (query.filter(PassengerModel.firstName.ilike(param)))
        if args['status']:
            if args['status'] == 'active' or args['status'] == 'suspended':
                if args['status'] == 'active':
                    query = (query.filter(PassengerModel.suspendedAt == None))
                else:
                    query = (query.filter(PassengerModel.suspendedAt != None))
        if args['emailStatus']:
            if args['emailStatus'] == 'verified' or args[
                    'emailStatus'] == 'unverified':
                emailStatus = 1 if args['emailStatus'] == 'verified' else 0
                query = (query.filter(
                    PassengerModel.emailStatus == emailStatus))
        if args['phoneStatus']:
            if args['phoneStatus'] == 'verified' or args[
                    'phoneStatus'] == 'unverified':
                phoneStatus = 1 if args['phoneStatus'] == 'verified' else 0
                query = (query.filter(
                    PassengerModel.phoneNumberStatus == phoneStatus))

        query = query.order_by('id')
        passengers = query.all()

        return passengers


@api.route('/passenger/<int:passengerId>/')
class Passenger(Resource):
    @api.doc('retrieve_passenger')
    @api.marshal_with(passengerModel)
    @api.expect(authenticationParser)
    def get(self, passengerId: int):
        """
        Retrieve a passenger using Id
        """
        # authenticate bearer token
        args = authenticationParser.parse_args()
        authentication_header_parser(args['Authorization'])

        passenger = PassengerModel.query.get(passengerId)
        if not passenger:
            # The passenger does not exist
            return '', http.client.NOT_FOUND

        return passenger

    @api.doc('update_passenger')
    @api.marshal_with(passengerModel)
    @api.expect(updatePassengerParser)
    def put(self, passengerId: int):
        """
        Update an passenger
        """
        passenger = (PassengerModel.query.filter(
            PassengerModel.id == passengerId).first())
        if not passenger:
            # The passenger does not exist
            return '', http.client.NOT_FOUND

        args = updatePassengerParser.parse_args()
        payload = authentication_header_parser(args['Authorization'])

        # check if the user accessing this endpoint does not own the passenger account to be updated
        if payload['id'] != passenger.authId:
            if 'admin' in payload:
                # check if the admin is a super admin
                # if payload['admin'] != 1:
                #     abort(403)
                pass
            else:
                abort(403)

        oldStatus = passenger.suspendedAt

        passenger.firstName = args['first'] or passenger.firstName
        passenger.lastName = args['last'] or passenger.lastName
        passenger.email = args['email'] or passenger.email
        passenger.phoneNumber = args['phone'] or passenger.phoneNumber
        passenger.rating = args['rating'] or passenger.rating

        passenger.image = args['image'] or passenger.image
        if args['dob'] is not None:
            passenger.dateOfBirth = args['dob']
        if args['homeLocation'] is not None:
            passenger.homeLocation = args['homeLocation']
        if args['homePickupTime'] is not None:
            passenger.homePickupTime = args['homePickupTime']
        if args['workLocation'] is not None:
            passenger.workLocation = args['workLocation']
        if args['workPickupTime'] is not None:
            passenger.workPickupTime = args['workPickupTime']
        if args['paymentMethod'] is not None:
            passenger.paymentMethod = args['paymentMethod']
        if args['phoneNumberStatus'] is not None:
            passenger.phoneNumberStatus = args['phoneNumberStatus']
        if args['emailStatus'] is not None:
            passenger.emailStatus = args['emailStatus']
        if args['suspend'] is not None:
            if args['suspend'] == 1:
                passenger.suspendedAt = datetime.utcnow()
            else:
                passenger.suspendedAt = None

            # send notification after updating passenger status
            if args['suspend'] == 1 and oldStatus is None:
                data = {'name': passenger.firstName}
                email_message = html_to_string(
                    'templates/email/cascading_suspend.html', data=data)
                sms_message = format_string(template.SUSPEND_MSG, data=data)

                data = {
                    'phoneNumber': passenger.phoneNumber,
                    'email': passenger.email,
                    'subject': 'Alert: You have Been Suspended',
                    'typeMessage': 'Passenger Account Suspension',
                    'Authorization': args['Authorization']
                }
                send_notification(data, email_message, sms_message)

        db.session.add(passenger)
        db.session.commit()

        return passenger

    @api.doc('delete_passenger',
             responses={http.client.NO_CONTENT: 'No content'})
    @api.marshal_with(passengerModel)
    @api.expect(authenticationParser)
    def delete(self, passengerId: int):
        """
        Delete an passenger, only accessible by super admin
        """
        # authenticate bearer token
        check_admin_return_payload(authenticationParser, super=True)

        passenger = PassengerModel.query.get(passengerId)
        if not passenger:
            # The passenger does not exist
            return '', http.client.NO_CONTENT

        db.session.delete(passenger)
        db.session.commit()

        return '', http.client.NO_CONTENT


check_parser = api.parser()
check_parser.add_argument('userId', type=int, required=True, help='User Id')
check_parser.add_argument('dob', type=str, required=True, help='Date of Birth')


@api.route('/check/dob/')
class PassengerCheckDob(Resource):
    @api.doc('Cross-check if passenger\'s date of birth')
    @api.expect(check_parser)
    def get(self):
        """
        Verifies passenger's date of birth
        """
        args = check_parser.parse_args()
        passenger = (PassengerModel.query.filter(
            PassengerModel.authId == args['userId']).order_by('id').first())
        if not passenger:
            # The passenger is not present
            return '', http.client.NOT_FOUND
        if passenger.dateOfBirth != args['dob']:
            # Wrong Passenger details provided
            return '', http.client.UNAUTHORIZED

        result = api.marshal(passenger, passengerModel)

        return result, http.client.OK


@api.route('/stat/sumquery/')
class PassengerSummaryQuery(Resource):
    @api.doc('query count in db: total count')
    @api.expect(authenticationParser)
    def get(self):
        """
        Help find total records in database
        """
        args = authenticationParser.parse_args()
        authentication_header_parser(args['Authorization'])

        count = (PassengerModel.query.count())
        return count


@api.route('/stat/datequery/')
class PassengerDateQuery(Resource):
    @api.doc('query count in db: daily')
    @api.expect(dateQuery_parser)
    def get(self):
        """
        Help find the daily signup within a range of dates
        """
        args = dateQuery_parser.parse_args()
        authentication_header_parser(args['Authorization'])

        start_date_str = args['startdate']
        end_date_str = args['enddate']

        start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()

        result = {}

        if start_date > end_date:
            return '', http.client.BAD_REQUEST

        while start_date <= end_date:
            passengers = (db.session.query(func.count(
                PassengerModel.id)).filter(
                    func.date(PassengerModel.timestamp) == start_date).all())
            date = start_date.strftime("%d/%m/%Y")
            result[date] = passengers[0][0]

            start_date = start_date + timedelta(days=1)

        return result


@api.route('/stat/monthquery/')
class PassengerMonthQuery(Resource):
    @api.doc('query count in db: monthly')
    @api.expect(monthQuery_parser)
    def get(self):
        """
        Help find the daily signup within a range of month
        """
        args = monthQuery_parser.parse_args()
        authentication_header_parser(args['Authorization'])

        str_year = args['year']
        try:
            year = int(str_year)
        except ValueError:
            return '', http.client.BAD_REQUEST

        result = {}

        if year < 2020:
            return '', http.client.BAD_REQUEST

        for month in range(1, 13):
            passengers = (db.session.query(func.count(
                PassengerModel.id)).filter(
                    func.extract('year', PassengerModel.timestamp) ==
                    year).filter(
                        func.extract('month', PassengerModel.timestamp) ==
                        month).all())

            result[f'{month}'] = passengers[0][0]

        return result
