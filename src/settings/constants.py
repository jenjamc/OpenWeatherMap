from decimal import Decimal
from enum import StrEnum

COST_CALL_PER_MINUTE: Decimal = Decimal('0.4')


class ErrorMessages(StrEnum):
    USER_DOES_NOT_EXIST = 'User does not exist'
    INVALID_ACCESS_TOKEN = 'Invalid access token'
    INVALID_PASSWORD = 'Invalid email or password'
    USER_ALREADY_REGISTERED = 'User already registered'
    TENANT_DOES_NOT_EXIST = 'Tenant does not exist'
    CALL_DOES_NOT_EXIST = 'Call does not exist'
    BALANCE_DOES_NOT_EXIST = 'Balance does not exist'
    INSUFFICIENT_FUNDS = 'insufficient funds'
    OBJECT_DOES_NOT_EXISTS = '{} does not exists'
    INVALID_CITY = 'Selected city does not exists'


class WebhookEvents(StrEnum):
    CALL_STARTED = 'call_started'
    CALL_ENDED = 'call_ended'
