from edfi_performance.api.client import EdFiAPIClient


class ProgramClient(EdFiAPIClient):
    endpoint = 'programs'

    _program_name = None

    @classmethod
    def shared_program_name(cls):
        if cls._program_name is not None:
            return cls._program_name
        cls._program_name = cls.create_shared_resource('programName', programName='Bilingual')
        return cls._program_name
