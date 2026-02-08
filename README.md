# About
NEMISys stands for Networked Event Management and Integration System
During the management of events, it was found that there may be significant benefits to said events by automation. It stood a fact that a majority of the event management could be automated and centralised to a single database, and records modified therein. This would eleminate the need for elaborate human systems and reduce significant labour. Furthermore, this would also remove limitations from a more manual management of the event, allowing for a greater variety of subevents to take place, as automated result compilation would take mere seconds in the worst case, while that for human compilation does not scale very well with the amount of datapoints.
NEMISys, in perticular, automates the tasks of - 
    1. Onboarding
    2. Data maintainance
    3. Verification checks
    4. Data forwarding to different people concerned with it
    5. Result compilation
    6. Event status monitoring
    7. Event statistics

# Usage
## Installation 
Extract the project repository into a suitable folder and `cd` into it
## Setting up
### Satisfying dependencies
Run `pip install -r requirements.txt` on the root of the project. This will install and resolve all dependencies.
### creds.json
In the root of the project folder, create a file called creds.json
Populate it with your credentials, in the following format,
```
{
    "host":"",
    "dbname":"",
    "user":"",
    "password":"",
    "port": ,
    "salt" : "",
    "APIKeys" : ["",...],
        "Events" : [
        "",
        ...],
    "onsiteEvents" : [
        "",
        ...],
    "preldEvents":[
        "",
        ...],
    "pregradPrels":[
        "",
        ...],
    "liveGradEvents":[
        "",
        ...],
    "limit":{
        "":,
        ...}
}

```


### init.py
Now, run the init.py in the project root. It will prompt for the admin password. Select one and note it down. It will be needed later.

## Running
Once the project is set up, run `main.py`. This should start a development server on `localhost:5000`. Visit this via any http client.

## Production
Log in as the admin (UUID=100000), with the password that was set up while running init.py previously. This will redirect to the `/home` upon a successful login. From here, various actions may be performed. Most of these are listed below.
### Managing Staff
Click the `Go to admin` button on the home page. This will redirect to `/admin`. From here, click on any of the buttons on the sidebar depending on what you want to do and fill in details. Then click on the respective button at the bottom of the `iframe`.<br>
**NOTE: DO NOT USE THIS IF YOU WANT TO MODIFY THE PASSWORD OF A STAFF ACCOUNT. REFER TO THE NEXT SUBHEADING.**
### Modifying staff password
Modifying the password of a staff member is similar to the proceedure for Managing Staff, just a bit more nuanced.
Click the `Go to admin button` on `/home/`. This will redirect to `/admin/`. From here, click on the `modify staff password` button on the sidebar. This will turn the `iframe` into a form with fields for UUID and New Password. Enter in the UUID of the staff that needs their password changed. Importantly, *enter the SHA-256 hash of the new password. Ask the staff that wants their password changed for this, instead of their plaintext password.  This is an intentionally designed feature and ensures that only the staff member knows their password in plaintext, and no one else, as the SHA-256 hash can not be reversed to give the orignal plaintext password.*
### Managing participant data
Participant management can be done by clicking on the `Go to participants` button on the home page. This will redirect to `/participants/`.  From here, the existing participant and school tables may be viewed by clicking on their respective sidebar buttons. Data may be added by uploading a spreadsheet obtained by a form. Refer to the subheading below.
### Adding participant data
Participant data may be added by uploading a spreadsheet (obtained directly by Google Forms) with the following headers —
```
Timestamp
Email Addess
Email
School Name
School Branch/Address
Name of Principal
School Phone Number
School Email
Name of Teacher Incharge
Phone Number of Teacher Incharge
Email ID of Teacher Incharge
Event1 Name of Participant 1
Event1 Class of Participant 1
Event 1 Discord Username of Participant 1
Event1 Name of Participant 2
Event1 Class of Participant 2
Event 1 Discord Username of Participant 2
Event2 Name of Participant 1
Event2 Class of Participant 1
Event 2 Discord Username of Participant 1
...
```
## Event Management
After all participant data has been onboarded, prelims of events that are to be online may be marked. For this, the database must be configured to a state that allows for such. This may be done by making use of the confirmation trigger system.


### Confirming onboarding
Click on the Go to confirmation triggers button on the home page. This will redirect to `/confirm/`. Select `Commence Online Prelims` from the first drop down and click on the `Trigger` button next to that drop down. This will generate attendance tables for events that are supposed to be online.<br>
**NOTE: THIS IS A NON REVERSIBLE ACTION.**

### Filling in online prelims data
Now, have the event heads of all the events with online prelims log into their respective accounts. Ensuring that they do not have `EI` permissions, this will lead them to their respective event management pages. Have them click on the `Mark Prelims Attendance` button and click on the check box next to participants that are present during the online event (or have made submissions). Have them click the `Update Attendance` button at the bottom of their screen. This will generate a new table for them to upload their results in. Have them head back to home. Let their prelims grading conclude and then have them click on the Grade Prelims button on their respective event management pages. This will present them with a table like interface where they can input points. Let them input the points as they have judged the event, and have them click the `Update Results` button at the bottom of the page. This will automatically generate a list of participants from their respective event that have qualified for the finals. Only these participants will show up in the on premise registration and attendance tables. *Ensure all of the events with online prelims have their prelims concluded before moving to the next step.*

### Commencing on premise attendance and registration
Click on the `Go to confirmation triggers` button on the home page. This will redirect to `/confirm/`. Select `Commence Regisetrations` from the first drop down and click on the `Trigger` button next to that drop down. This will add participant data for all events for participants that are supposed to be on the school premises.<br>
**NOTE: THIS IS A NON REVERSIBLE ACTION.**

### On premise participant attendance and registrations
Have registrars on the greeting desk ready with their accounts logged in from their machines. Ensuring that they only have the `RG` permission, heading to home would redirect them to `/registry/`. As registrants show up to the premises, have them ask their school and input it into the text field on the side bar. The school name will show up after a few key strokes. Click on the school name in the selection feild and click on the `Fetch Participants` button on the sidebar. Confirm details of individual participants lised in the `iframe` (and modify wherever necessary) and click the check box next to their name to mark their attendance. When this process is done for all participants of a school, click on the `Update Attendance` button at the bottom of the screen. Additionally, new participants may be added by populating a spreadsheet like the one mentioned previously with details of the new showing up school. This may be uploaded into the `iframe` after clicking on the `Add more data button` on the sidebar. Once this is done for all schools that were to show up, proceed to the next step.

### Concluding on premise attendance and registrations
Click on the `Go to confirmation triggers` button on the home page. This will redirect to `/confirm/`. Select Conclude Regisetrations from the first drop down and
click on the `Trigger` button next to that drop down. This will generate attendance tables for events (or rounds thereof) that are supposed to take place on premises.<br>
**NOTE: THIS IS A NON REVERSIBLE ACTION.**

### Filling in all event data
Now, have the event heads of all the on premises events log into their respective accounts. Ensuring that they do not have `EI` permissions, this will lead them to their respective event management pages. For events that had online prelims, the following paragraph is inapplicable. <br>
Have the event heads click on the `Mark Prelims Attendance` button and click on the check box next to participants that are present on the event venue. Have them click the `Update Attendance` button at the bottom of their screen. This will generate a new table for them to upload their results in. Have them head back to home. Let their prelims grading conclude and then have them click on the `Grade Prelims` button on their respective event management pages. This will present them with a table like interface where they can input points. Let them input the points as they have judged the event, and have them click the `Update Results` button at the bottom of the page. This will automatically generate a list of participants from their respective event that have qualified for the finals, and create an attendance table based on the same. Now, as all prelims have concluded, the following paragraph is applicable to all events.<br>
Have the event heads click on the `Mark Finals Attendance` button and click on the check box next to participants that are present on the event venue. Have them click the `Update Attendance` button at the bottom of their screen. This will generate a new table for them to upload their finals results in. Have them head back to home. Let their prelims grading conclude and then have them click on the `Grade Finals` button on their respective event management pages. This will present them with a table like interface where they can input points. Let them input the points as they have judged the event, and have them click the `Update Results` button at the bottom of the page. This will automatically generate generate ranks for all participating schools in that event. Once this process has concluded for all events (i.e. all events have concluded), proceed to the next step.

### Commencing result compilation
Click on the `Go to confirmation triggers` button on the home page. This will redirect to `/confirm/`. Select `Commence Result Compilation` from the first drop down and click on the `Trigger` button next to that drop down. This will start the result compilation process, summing up results from all events per school, and grading them on the basis of their cumulative points, and in case of ties, first the number of first positions secured by said school, then the number of second positions secured by said school, and finally the number of third positions secured by said school.<br>
**NOTE: THIS IS A NON REVERSIBLE ACTION.**

### Confirming compiled results
Considering the high stakes nature of this stage, NEMISys requires manual confirmation for this stage. Further, it allows for manual overrides in case something has went awry. This may be done after all previous steps are completed either by accessing `/home/` through an account that has only the `RC` permissions, or by clicking on the `Go to results` button on `/home` from an account with `EI` or `TC` permissions. This will redirect to `/results/mod`. Here, a multiple table like interface is presented with text field for inputing overrides for points. Once editing is complete, click on the `Update Results` button at the bottom of the screen. This will regenerate ranks based on the new results. Once this is done, proceed to the next step.

### Concluding result compilation and creating award tables
Click on the `Go to confirmation triggers` button on the home page. This will redirect to `/confirm/`. Select `Conclude Result Compilation` from the first drop down and click on the `Trigger` button next to that drop down. This will generate award tables for events based on the rank of school of each participant in the event.<br>
**NOTE: THIS IS A NON REVERSIBLE ACTION.**

### Accessing Certificate Data
Certificate data may be accessed after all the previous steps are done by either visiting the home page from an account with only the `CW` permissions, or by clicking on the `Go to certificates` button on the home page from an account with `TC` or `EI` permissions. This will redirect to `/certs/`, which shows award tables for all events with first second and third place participants.
