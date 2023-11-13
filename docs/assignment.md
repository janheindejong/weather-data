
# Assignment: Sensor measurements API

The goal of this assignment is to verify that you can apply software engineering techniques in 
practice. To do so, we ask that you build a backend for a hypothetical part of our product.

## Instructions

Modern greenhouses contain lots of sensors to measure the climate in the greenhouse and the 
environment around the plants. The environment consists of parameters such as air temperature, 
humidity, CO2 concentration and access to water and nutrients. These parameters are influenced 
by conditions outside, as well as control mechanisms inside the greenhouse. To achieve the right 
environment, the grower manipulates mechanical components of the greenhouse based on forecasted 
external weather conditions. These components include but are not limited to: screens, 
ventilation (through opening windows) and heating systems. 

We want to give growers insights in the current and historical environmental parameters so they 
can assess the performance of their growing strategy. I.e. did they manage to keep the temperature, 
humidity etc. within the right bounds to create the ideal growing conditions for the plants.
To be able to build a dashboard with these insights, we need a backend that exposes the right 
information through one or more API endpoints that can be consumed by the frontend.

For this assignment, you're going to build a part of the backend that deals with meteo (weather) 
data.

## Requirements

Your solution should include the following functionality:

1. An API endpoint that can be used to push raw data (according to the provided format) 
   from the climate computer to your service (see below for access to data)
2. One or more API endpoints to expose the meteo data in a _sane_ and _convenient_ 
   format for consumption by the frontend. The frontend expects at least the following 
   functionality:
   
   - Expose the _latest_ weather conditions (i.e. show what's happening _now_)
   - Expose the development of the weather parameters over the last 24h in 15 min increments
   - Expose the average for each of the weather parameters for the last 24h
   - Expose the development of the weather parameters over the last 7 days in 1 day increments 
     (average per day)
   - Expose the average of the weather parameters over the last 7 days

**Some hints and tips:**

- It's up to you how you store the measurements. Can be in-memory, in a database, etc.
- The format of the raw data is _not necessarily_ the ideal format to expose the data in for the 
  frontend. Consider the design of your API output well!
- Consider **all** aspects of API design, including but not limited to: paths, return codes, 
  input/output formats etc.

### Bonus objectives

- Store the sensor data in a persistent way (i.e. not in-memory) so it's available between restarts
- Add authentication between the API and allow for different roles between the "write" endpoint 
  and the "read" endpoints
- Provide a way to ingest raw data in bulk

### Non-functional requirements

- Use Python 3.10 or higher _or_ use Golang 1.19 or higher
- Maintainability is favoured over performance. No complex performance optimizations should be 
  needed. Another developer should be able to continue where you left off
- It should be possible to run the project (and all of its components) on any machine, including 
  our laptops
- This assignment was designed to be completed in 6-8h. The evaluation will take into account the 
  choices you make and what you focus on given the time you have. However, it's up to you if you 
  spend less or more time on it.
- Please make sure the final commit to your repository is done at least 24 hours before the start 
  of your interview

## Deliverables

This assignment should be delivered in the following way:

- All code is pushed to your private copy of this repository.
- Documentation is provided in the README.md on how the solution works, and how to run and test it.
- Any information, (dummy)-data, files, and other assets that are needed to run this project, are 
  provided in this repository.

## Assessment Criteria

The solution will be assessed on the following criteria:

- How is your code structured? Is it easy to read and follow?
- How clear is the documentation?
- How is the API design? Is it easy for a frontend developer to use?
- What does your (internal) data model look like? How does your solution represent and store data?
- Are there any clear bugs in your code?
- How does the solution perform?
- Can you clearly and concisely describe the process you have followed and the choices you have made?
- Can you describe the biggest short-comings of your solution and which steps could be taken to 
  improve on that?

**NOTE:** your experience as a software engineer influences our expectations on the completeness of 
your solution - both in terms of requirements and bonus objectives met. In other words: we expect 
different things from someone with 1 year of experience than from someone with 10 years of experience.

## Additional information and assumptions

- The required raw data to test your solution can be found through this link: https://drive.google.com/drive/folders/1TV20EVuxcmaqro7e0HfmX2j6HtILNwXB?usp=sharing


