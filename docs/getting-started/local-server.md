### Start the server

From inside the root of the repo do

`dev_appserver.py .`

_If you get something like 'command not found', make sure GAE is in your path. Use `echo $PATH` to confirm. See [setup](installation-and-setup.md#update-paths)._

_If you see a mySQL connection error, make sure that mySQL is running in another terminal window: `$ mysqld`_

---

### Create accounts (first time only)

The superuser you created during [setup](installation-and-setup#setting-up-the-database) gives you access to the admin site. You'll probably also want access to the fundraising and grant application areas too.

#### Project Central (Giving Project member)

1. Go to `/admin-advanced`\* and log in with superuser credentials you chose.
2. Either of these options:
    - Create a new `Member` object
        - Click on `+ Add` next to `Members`
        - Enter the email you used to log in, and whatever first & last name you want.
        - Save
    - (OR)
    - Pick an existing `Member`
        - Pick a `Member` and click on it to edit
        - Change the login email to match your account's email
        - Save

You should now be able to access Project Central: [/fund](http://localhost:8080/fund)

\* _The advanced admin site is only used by devs (and should eventually be replaced with better admin permissions). `/admin` is used for almost everything, but it does not show `Member`s_

#### Grant application (Organization)

1. Go to `/admin` and log in with superuser credentials you chose.
2. Either of these options:
    - Create a new organization
        - Click on `+Add` next to `Organizations`
        - Enter the same email you used to log in
        - Fill in whatever other fields are required
        - Save
    - (OR)
    - Pick an organization to use
        - Click on it to edit
        - Change the login email to match your account's email
        - Save

You should now be able to access the grant application area: [/apply](http://localhost:8080/apply)
