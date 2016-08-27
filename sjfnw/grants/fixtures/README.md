## `test_grants.json`

This file has a small number of model instances. This is the default set of
fixtures provided by `BaseGrantTestCase`.

### Grant cycles

These are updated in `BaseGrantTestCase` `setUp` so that they have consistent
open/closed state.

pk | Cycle title        | Status
---|--------------------|-------------------
1  | Open cycle         | open
2  | Another open cycle | open
3  | Closed cycle       | closed
4  | Upcoming cycle     | closed (upcoming)
5  | Let's have a kiki  | open
6  | Oui                | open

### Organizations

pk | Org name             | Org email         | Associated apps          | Associated drafts
---|----------------------|-------------------|--------------------------|---------------------------
1  | Fresh New Org        | neworg@gmail.com  | _none_                   | _none_ 
2  | OfficeMax Foundation | testorg@gmail.com | 1 (cycle 1), 2 (cycle 5) | 1 (cycle 2), 2 (cycle 3)

### Giving projects

pk | GP title
---|-------------------
3  | LGBTQ
4  | Immigration Reform

### Grant applications

pk | Organization  | Grant cycle           | GP(s) assigned                        | Notes
---|---------------|-----------------------|---------------------------------------|---------------------------
1  | OfficeMax (2) | Open cycle (1)        | Immigration Reform Giving Project (4) | Complete as of 11/2013. Includes timeline, all-in-one budget
2  | OfficeMax (2) | Let's have a kiki (5) | _n/a_                                 |

### Draft grant applications

pk | Organization  | Grant cycle                  | Notes
---|---------------|------------------------------|----------------------------
1  | OfficeMax (2) | Closed cycle (3)             | Missing a lot of stuff
2  | OfficeMax (2) | Another open cycle cycle (2) | Complete (as of 5/1/14). No fiscal info, general support (no project info), all-in-one budget option, includes partial timeline
