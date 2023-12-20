# On-call Support Planning

Genetic Algorithm project to solve the on-call support schedule pain.

This project uses python 3.9 to create a [GA](https://www.mathworks.com/help/gads/what-is-the-genetic-algorithm.html)
to resolve the on-call support (OCS) schedule. 
It takes into account:

- How many people do OCS every day;
- If someone cannot do OCS on a day;
- People cannot do OCS for more than 7 days in a row;
- Members should rotate in the schedule;
- People might not be available to do OCS.

It is a GA so the result is not guaranteed. However, if the code finds a solution, 
it will be a valid one.

## Documentation

1. Clone the code 
```bash
git clone git@github.com:rodolfocugler-hexad/on-call-support-planning.git
```
2. Install the requirements 
```bash
python3 -m pip install -r requirements.txt
```
3. Run the code and create the ./resources/template.json using the option 1
```bash
python3 main.py
```
![template.png](public%2Ftemplate.png)

It will create a json file like the following:

```json
{
    "weekQuantity": 6,
    "numberOfPopulations": 40,
    "numberOfEpochs": 200,
    "numberOfEmployeesDoingOnCall": 2,
    "employeeNames": [
        "Paul",
        "Emma",
        "Ben",
        "Finn",
        "Leon"
    ],
    "startDate": "22/01/2024",
    "22/01/2024": "",
    "23/01/2024": "Paul,Emma,Ben",
    "24/01/2024": "",
    "25/01/2024": "",
    "26/01/2024": "",
    "27/01/2024": "",
    "28/01/2024": "",
    "29/01/2024": "",
    "30/01/2024": "",
    "31/01/2024": "",
    "01/02/2024": "",
    "02/02/2024": "",
    "03/02/2024": ""
}
```

Please, add the name of employees which will do OCS as part of the array called employeeNames;

Also add the names exactly in the same format to the dates which they are not available to do OCS. 
These names should be comma separated.

numberOfPopulations and numberOfEpochs are internal parameters which you can vary and help the 
algorithm.

Another parameter adopted is called DAYS, and it has the default value set to 3;
This parameter also becomes 2 in a specif scenario, although you can set it to 7
if you think your OCS schedule is easy to create;

### Perform the algorithm

Run the code using the option 2 after you manipulate the template.json
```bash
python3 main.py
```

![run.png](public%2Frun.png)

The algorithm will create a csv file called ./resources/result.csv. It holds all the support schedule;

```CSV
Date,Day Of Week,On-Call 1,On-Call 2
22/01/2024,Monday,finn,emma
23/01/2024,Tuesday,finn,emma
24/01/2024,Wednesday,finn,emma
25/01/2024,Thursday,finn,emma
26/01/2024,Friday,finn,emma
27/01/2024,Saturday,finn,emma
28/01/2024,Sunday,finn,emma
29/01/2024,Monday,leon,paul
30/01/2024,Tuesday,leon,paul
31/01/2024,Wednesday,leon,paul
01/02/2024,Thursday,leon,paul
02/02/2024,Friday,leon,paul
03/02/2024,Saturday,leon,paul
04/02/2024,Sunday,leon,paul
05/02/2024,Monday,ben,emma
06/02/2024,Tuesday,ben,emma
07/02/2024,Wednesday,ben,emma
08/02/2024,Thursday,ben,emma
09/02/2024,Friday,ben,emma
10/02/2024,Saturday,ben,emma
11/02/2024,Sunday,ben,emma
12/02/2024,Monday,leon,finn
13/02/2024,Tuesday,leon,finn
14/02/2024,Wednesday,leon,finn
15/02/2024,Thursday,leon,finn
16/02/2024,Friday,leon,finn
17/02/2024,Saturday,leon,finn
18/02/2024,Sunday,leon,finn
19/02/2024,Monday,ben,emma
20/02/2024,Tuesday,ben,emma
21/02/2024,Wednesday,ben,emma
22/02/2024,Thursday,ben,emma
23/02/2024,Friday,ben,emma
24/02/2024,Saturday,ben,emma
25/02/2024,Sunday,ben,emma
26/02/2024,Monday,finn,leon
27/02/2024,Tuesday,finn,leon
28/02/2024,Wednesday,finn,leon
29/02/2024,Thursday,finn,leon
01/03/2024,Friday,finn,leon
02/03/2024,Saturday,finn,leon
03/03/2024,Sunday,finn,leon
```

If the algorithm does not find a solution, you can adjust the parameters
and try again.