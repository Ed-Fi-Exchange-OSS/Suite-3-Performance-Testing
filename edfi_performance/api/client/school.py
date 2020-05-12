from edfi_performance.api.client import EdFiAPIClient, get_config_value, _import_from_dotted_path


class SchoolClient(EdFiAPIClient):
    endpoint = 'schools'

    _high_school_id = None
    _elementary_school_id = None

    @classmethod
    def shared_high_school_id(cls):
        if cls._high_school_id is not None:
            return cls._high_school_id
        cls._high_school_id = cls.create_shared_resource('schoolId')
        cls._create_school_course_code(cls._high_school_id, 'ALG-2')
        cls._create_school_graduation_plan(cls._high_school_id, 2020)
        return cls._high_school_id

    @classmethod
    def shared_elementary_school_id(cls):
        if cls._elementary_school_id is not None:
            return cls._elementary_school_id
        cls._elementary_school_id = cls.create_shared_resource('schoolId')
        cls._create_school_course_code(cls._elementary_school_id, 'ELA-01')
        return cls._elementary_school_id

    @classmethod
    def _create_school_course_code(cls, school_id, course_code):
        client_class = _import_from_dotted_path('edfi_performance.api.client.course.CourseClient')
        client_instance = client_class(get_config_value('host'), token=client_class.token)
        client_instance.create(
            educationOrganizationReference__educationOrganizationId=school_id,
            courseCode=course_code
        )

    @classmethod
    def _create_school_graduation_plan(cls, school_id, school_year):
        client_class = _import_from_dotted_path('edfi_performance.api.client.graduation_plan.GraduationPlanClient')
        client_instance = client_class(get_config_value('host'), token=client_class.token)
        client_instance.create(
            educationOrganizationReference__educationOrganizationId=school_id,
            graduationSchoolYearTypeReference__schoolYear=school_year
        )


class SchoolYearTypeClient(EdFiAPIClient):
    """
    The ODS API prevents clients from creating, updating, or deleting instances
    of SchoolYearType.
    """
    endpoint = 'schoolYearTypes'

    def create_with_dependencies(self, **kwargs):
        pass  # Cannot be created, modified, or deleted because it is a core enumeration defined by the API implementer

    def delete_with_dependencies(self, reference, **kwargs):
        pass  # Cannot be created, modified, or deleted because it is a core enumeration defined by the API implementer
