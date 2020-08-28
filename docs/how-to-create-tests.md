# How to Create Tests

## Resource Tests

When creating a test for a new resource, you will be creating 4 different classes:

1. Factory
2. Client
3. PipecleanTest
4. VolumeTest (if necessary)

### 1. Factory

The factory class contains all of the attributes and their corresponding values for the new resource. It consists of the basic and common attributes needed for the new resource to be created. This allows us to create a resource without having to specify each and every attribute.

Perform the following steps to create a factory (let's call our example resource 'Course'):

1. Create the file for the resource factory:
    * ~Ed-Fi-X-Performance\edfi_performance\factories\resources\course.py
    * Replace 'course' with the name of your new resource
2. Add the following import statements to the top of the file:

   ```python
   import factory
   from .. import APIFactory
   ```

3. Add the class
    * `class CourseFactory(APIFactory):`
    * Leave the body of the class empty, for now
4. Go to Swagger and determine which attributes need to be contained in this factory class
    * Be sure to include the attributes that make up the primary key of this resource and all other required attributes
    * Note which attribute(s) will need to be different every time this resource is created to ensure a resource is created every time
    * For course, courseCode and educationOrganizationId made up the primary key
    * Refer to the json version of the resource (this will be useful for our factory class)
5. In the body of the class, start writing out the common attributes. It will look something like this:

   ```python
   import factory
   from .. import APIFactory
   from ..descriptors.utils import build_descriptor
   from ..utils import RandomSuffixAttribute
   
   class CourseFactory(APIFactory):
       courseTitle = 'Algebra I'
       educationOrganizationReference = factory.Dict(
           dict(
               educationOrganizationId=255901
           )
       )
       academicSubjectDescriptor = build_descriptor('AcademicSubject', 'Mathematics')
       courseCode = RandomSuffixAttribute('ALG-1')
       numberOfParts = 1
       identificationCodes = factory.List([
           factory.Dict(
               dict(
                   courseIdentificationSystemDescriptor=build_descriptor('CourseIdentificationSystem',    'LEA course code'),
                   identificationCode="ALG-1"
               )
           ),
       ])
       ...
   ```

6. Notice a few things:
    * The variable names must match the json attribute names from Swagger
    * For descriptors, use the build_descriptor method with the first argument being the descriptor name and the second argument being the code value of the specific descriptor
    * For reference attributes (educationOrganizationReference), surround the inner attribute(s) with the Factory Boy style (as seen above)
    * For the primary key attribute (courseCode), set the variable equal to a random value. We used `RandomSuffixAttribute` for a random string
    * We had to import `RandomSuffixAttribute` and `build_descriptor` to get access to those methods
    * For random integers, you can use `UniquePrimaryKeyAttribute`. For random dates, you can use `RandomDateAttribute`
7. Your resource factory should now be finished. Remember to replace 'course' with the name of your new resource.

### 2. Client

The client class contains an endpoint for the URL of the resource. This class creates and deletes a resource based on the data from the factory class, which you created earlier. Optionally, a client class will have a list of dependent resource clients that it needs in order to create the resource at hand. If so, then there will also be a custom `create_with_dependencies()` and `delete_with_dependencies()` method. Having a central place to perform these common actions will make writing pipeclean and volume tests easier.

Perform the following steps to create a simple (zero dependents) client:

1. Create the file for the resource client:
    * ~Ed-Fi-X-Performance\edfi_performance\api\client\course.py
    * Replace 'course' with the name of your new resource
2. Add the following import statements to the top of the file (Your import for the factory may look different):

   ```python
   from edfi_performance.api.client import EdFiAPIClient
   ```

3. Add the class along with the endpoint value for the specific resource

   ```python
   class CourseClient(EdFiAPIClient):
       endpoint = 'courses'
   ```

4. For a simple resource, you would be finished. The EdFiAPIClient class that is inherited creates and deletes the resource behind the scenes. This class contains methods for GET, POST, PUT, and DELETE actions on the API. It also dynamically generates the factory class based on the file name and file path so be sure to stay consistent with the file-creation steps above. Remember to replace 'course' with the name of your new resource.

### 3. Pipeclean Test

The Pipeclean Test class methodically exercises all 5 endpoints for a given resource: GET, POST, GET (by id), PUT, and DELETE. This class contains the name and new value of the attribute that is going to be updated. Each Pipeclean Test class inherits from EdFiPipecleanTestBase, which is where the sequence of requests are made. Once this sequence of requests has reached the end, the locust client will move on to the next pipeclean test.

Perform the following steps to create a simple pipeclean test:

1. Create the file for the resource pipeclean test:
    * ~Ed-Fi-X-Performance\edfi_performance\tasks\pipeclean\course.py
    * Replace 'course' with the name of your new resource
2. Add the following import statements to the top of the file (Your import for the client may look different):

   ```python
   from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase
   ```

3. Add the pipeclean test class along with the name and value for the resource attribute that will be updated

   ```python
   class CoursePipecleanTest(EdFiPipecleanTestBase):
       update_attribute_name = 'courseTitle'
       update_attribute_value = "Algebra II"
   ```

4. For a simple pipeclean test, you would be finished. As explained earlier, the EdFiPipecleanTestBase performs the 5 API calls and moves on to the next resource test. Also, the client class is dynamically generated here so be sure to stay consistent with the file-creation steps above. Remember to replace 'course' with the name of your new resource.

### 4. Volume Test

The Volume Test class exercises 3 endpoints for a given resource: POST, PUT and DELETE. Each Volume Test inherits from EdFiVolumeTestBase, which contains a `run_scenario()` method that makes calls to POST, PUT, and DELETE for each resource. Most Volume Test classes will contain a task where two calls to `run_scenario()` are made for two different scenarios.

Perform the following steps to create a simple volume test:

1. Create the file for the resource volume test:
    * ~Ed-Fi-X-Performance\edfi_performance\tasks\volume\course.py
    * Replace 'course' with the name of your new resource
2. Add the following import statements to the top of the file (Your import for the client may look different):

   ```python
   from locust import task
   from edfi_performance.tasks.volume import EdFiVolumeTestBase
   ```

3. Add the volume test class along with task method. Keep the task method empty for now.

   ```python
   class CourseVolumeTest(EdFiVolumeTestBase):
       @task
       def run_calendar_scenarios(self):
           pass
   ```

4. At this point, this volume test can run but no meaningful requests will be made. Most volume tests have 2 scenarios so let's add them. Make two calls to `run_scenario()` and fill them with different arguments for each scenario. It may look something like this:

   ```python
   from locust import task

   from edfi_performance.api.client.school import SchoolClient
   from edfi_performance.factories.descriptors.utils import build_descriptor
   from edfi_performance.factories.utils import RandomSuffixAttribute
   from edfi_performance.tasks.volume import EdFiVolumeTestBase


   class CourseVolumeTest(EdFiVolumeTestBase):
       @task
       def run_course_scenarios(self):
           self.run_scenario('courseTitle', "Algebra II")
           self.run_scenario('levelCharacteristics', [{'courseLevelCharacteristicDescriptor':
                                                       build_descriptor('courseLevelCharacteristic',    'Basic')}],
                             academicSubjectDescriptor=build_descriptor('AcademicSubject', 'Fine and    Performing Arts'),
                             courseTitle='Art, Grade 1',
                             courseCode=RandomSuffixAttribute('ART 01'))
   ```

5. Notice a few things:
    * A few new imports were added
    * The method name must be decorated with `@task` so locust knows that it's a locust task
    * The first two parameters for `run_scenario()` include the name of the attribute to be updated and its corresponding value
    * Each additional argument must be formatted as shown above in the second scenario, since those are the values that differ from the first
    * Note that if there were no values to update, you wouldn't pass any arguments 
    * Normally, your first scenario would just take in the update values since the factory will have all of its attributes
    * The second scenario would take in the update values, along with any key-value pairs

6. At this point, both scenario volume tests should run successfully and you should be finished. However, you could add another task method that deliberately fails. This kind of task will ensure the correct response is returned by a bad request. It may look something like this:

   ```python
   from locust import task

   from edfi_performance.api.client.school import SchoolClient
   from edfi_performance.factories.descriptors.utils import build_descriptor
   from edfi_performance.factories.utils import RandomSuffixAttribute
   from edfi_performance.tasks.volume import EdFiVolumeTestBase

   class CourseVolumeTest(EdFiVolumeTestBase):
       @task(weight=100)
       def run_course_scenarios(self):
           self.run_scenario('courseTitle', "Algebra II")
           self.run_scenario('levelCharacteristics', [{'courseLevelCharacteristicDescriptor':
                                                       build_descriptor('courseLevelCharacteristic', 'Basic')}],
                             academicSubjectDescriptor=build_descriptor('AcademicSubject', 'Fine and Performing Arts'),
                             courseTitle='Art, Grade 1',
                             courseCode=RandomSuffixAttribute('ART 01'))

       @task(weight=1)
       def deliberate_failure_scenario(self):
           self.run_unsuccessful_scenario(educationOrganizationReference__educationOrganizationId='INVALID ID',
                                          succeed_on=[403])
   ```

7. Notice a few things:
    * We now have two tasks with different weights. This is because we don't want bad requests to occur very often. In this case, there is a 1% chance of this bad request occurring
    * In the `deliberate_failure_scenario()`, a call to `run_unsuccessful_scenario()` is made. This method takes in succeed_on, a list containing the expected status code(s). It also takes in any keyword arguments that will make this test fail with a 403 response.

8. At this point, you have a complete volume test class. The EdFiVolumeTestBase allows the client class to be dynamically generated so be sure to stay consistent with the file-creation steps above. Remember to replace 'course' with the name of your new resource.

## Composite Tests

When creating a test for a new composite, you will be creating 2 different types of classes:

1. Client
2. PipecleanTest

### 1. Client

The client classes for a composite include one specific client class for each different endpoint, as well as a general one for the entire composite. The general client class will have a URL prefix and a json object to hold the constants. This class will inherit from `EdFiCompositeClient`. The specific client class will just have the endpoint name and will inherit from the general client class.

Perform the following steps to create clients for a composite:

1. Create the file for the composite clients:
    * ~Ed-Fi-X-Performance\edfi_performance\api\client\enrollment.py
    * Replace 'enrollment' with the name of your new composite

2. Refer to `~Ed-Fi-X-Performance\edfi_performance\api\client\enrollment.py` to see how these clients are implemented. Notice a few things:
    * The general client, `EnrollmentCompositeClient`, contains the URL prefix and the json object of constants, as expected. Your attributes will differ since it's for a different composite with different resources
    * The specific clients contain an endpoint and they inherit from `EnrollmentCompositeClient`, as expected. There are 5 specific clients here since the enrollment composite is composed of 5 resources.

3. At this point, you are finished with the client classes. Because the general client (`EnrollmentCompositeClient`) inherits from `EdFiCompositeClient`, it contains all the methods needed to make the special GET requests. Continue to the next part for more info on these special GET requests.

### 2. Pipeclean Test

The Pipeclean Test class for a composite exercises multiple GET requests for the various resources in the composite. The basic pipeclean test class contains a list of the resources in the composite and inherits from `EdFiCompositePipecleanTestBase`. This base class contains the common pipeclean scenario for many of the composite resources. In this common scenario, a call to `get_composite_list(...)` is eventually made, where the special GET request is constructed. The special GET requests for a specific resource in the composite will look something like this:

* `/ed-fi/enrollment/localEducationAgencies/{localEducationAgency_id}/schools`
* `/ed-fi/enrollment/sections/{section_id}/schools`
* `/ed-fi/enrollment/staffs/{staff_id}/schools`
* `/ed-fi/enrollment/students/{student_id}/schools`

In this case, these are all special GET requests for the school resource in the enrollment composite. Note that localEducationAgencies, sections, staffs, and students are the other resources a part of this composite. The other two GET requests for this resource include the basic GET all and the GET by id requests.

Perform the following steps to create a pipeclean test for a composite:

1. Create the file for the composite pipeclean test:
    * ~Ed-Fi-X-Performance\edfi_performance\tasks\pipeclean\enrollment.py
    * Replace 'enrollment' with the name of your new composite

2. Refer to `~Ed-Fi-X-Performance\edfi_performance\tasks\pipeclean\enrollment.py` to see how these pipeclean tests are implemented. Notice a few things:
    * The `LocalEducationAgencyEnrollmentCompositePipecleanTest` class overrides the `_run_pipeclean_scenario(...)` method since it only needs to perform the 2 basic GET requests: GET all and GET by id
    * The remaining pipeclean tests contain the list of the enrollment composite resources and inherit from `EdFiCompositePipecleanTestBase`, as expected.
    * The list of composite resources is located near the top since it is shared by most of the pipeclean tests

3. After adding this, you should be finished with these tests and they should run. Make sure the client and pipeclean test class names follow the same naming convention and are on the correct file path. Remember to replace 'enrollment' with the name of your new composite.