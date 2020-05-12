from edfi_performance.api.client import EdFiAPIClient


class CalendarClient(EdFiAPIClient):
    endpoint = 'calendars'
