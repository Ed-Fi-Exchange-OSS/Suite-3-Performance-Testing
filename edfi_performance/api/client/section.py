# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.calendar_date import CalendarDateClient
from edfi_performance.api.client.class_period import ClassPeriodClient
from edfi_performance.api.client.location import LocationClient
from edfi_performance.api.client.school import SchoolClient


class SectionClient(EdFiAPIClient):
    endpoint = 'sections'

    dependencies = {
        ClassPeriodClient: {},
        'edfi_performance.api.client.course_offering.CourseOfferingClient': {},
        LocationClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.get('schoolId', SchoolClient.shared_elementary_school_id())
        custom_course_code = kwargs.pop('courseCode', 'ELA-01')

        # Create a course offering and its dependencies
        course_offering_reference = self.course_offering_client.create_with_dependencies(
            schoolId=school_id,
            courseReference__courseCode=custom_course_code,
            courseReference__educationOrganizationId=school_id,
            schoolReference__schoolId=school_id)
        course_offering_attrs = course_offering_reference['attributes']

        # Create a class period
        class_period_reference = self.class_period_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
        )

        # Create a location
        location_reference = self.location_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
        )

        # Create a section
        section_attrs = self.factory.build_dict(
            classPeriods__0__classPeriodReference__classPeriodName=class_period_reference['attributes']['classPeriodName'],
            courseOfferingReference__localCourseCode=course_offering_attrs['localCourseCode'],
            courseOfferingReference__schoolId=school_id,
            courseOfferingReference__sessionName=course_offering_attrs['sessionReference']['sessionName'],
            locationReference__classroomIdentificationCode=location_reference['attributes']['classroomIdentificationCode'],
            locationReference__schoolId=school_id,
            **kwargs
        )
        section_id = self.create(**section_attrs)
        return {
            'resource_id': section_id,
            'dependency_ids': {
                'location_reference': location_reference,
                'class_period_reference': class_period_reference,
                'course_offering_reference': course_offering_reference,
            },
            'attributes': section_attrs,
            'localCourseCode': course_offering_attrs['localCourseCode'],
            'schoolId': school_id,
            'schoolYear': 2014,
            'sectionIdentifier': section_attrs['sectionIdentifier'],
            'sessionName': course_offering_attrs['sessionReference']['sessionName'],
            'gradingPeriods':
                course_offering_reference['dependency_ids']['session_reference']['attributes']['gradingPeriods'],
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        depend = reference['dependency_ids']
        self.location_client.delete_with_dependencies(depend['location_reference'])
        self.class_period_client.delete_with_dependencies(depend['class_period_reference'])
        self.course_offering_client.delete_with_dependencies(depend['course_offering_reference'])


class SectionAttendanceTakenEventClient(EdFiAPIClient):
    endpoint = 'sectionAttendanceTakenEvents'

    dependencies = {
        SectionClient: {},
        CalendarDateClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        calendar_date_reference = self.calendar_date_client.create_with_dependencies(
            schoolId=school_id,
        )
        calendar_date_attrs = calendar_date_reference['attributes']

        section_reference = self.section_client.create_with_dependencies(
            schoolId=school_id,
        )
        section_attrs = section_reference['attributes']

        event_attrs = self.factory.build_dict(
            calendarDateReference__schoolId=school_id,
            calendarDateReference__calendarCode=calendar_date_attrs['calendarReference']['calendarCode'],
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
        )
        event_id = self.create(**event_attrs)

        return {
            'resource_id': event_id,
            'dependency_ids': {
                'calendar_date_reference': calendar_date_reference,
                'section_reference': section_reference,
            },
            'attributes': event_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.calendar_date_client.delete_with_dependencies(reference['dependency_ids']['calendar_date_reference'])
        self.section_client.delete_with_dependencies(reference['dependency_ids']['section_reference'])
