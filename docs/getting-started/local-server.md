### Start the server

From inside the root of the repo do

`dev_appserver.py .`

_If you get something like 'command not found', make sure Google App Engine is in your path. Use `echo $PATH` to confirm. See [setup](installation-and-setup.md#update-paths)._

_If you see a mySQL connection error, make sure that mySQL is running in another terminal window: `$ mysqld`_

---

### Create accounts (first time only)

The superuser you created during [setup](installation-and-setup#setting-up-the-database) gives you access to the admin site. You'll probably also want access to the fundraising and grant application areas too.

#### Project Central (Giving Project member)

1. Go to `/admin` and log in with superuser credentials you chose.
2. Create a new `Member` object
  - Click on `+ Add` next to `Members`
  - Enter the email you used to log in, and whatever first & last name you want.
  - Save

You should now be able to access Project Central: [/fund](http://localhost:8080/fund)

#### Grant application (Organization)

1. Go to `/admin` and log in with superuser credentials you chose.
2. Create a new organization
  - Click on `+Add` next to `Organizations`
  - Enter the same email you used to log in
  - Fill in whatever other fields are required
  - Save

You should now be able to access the grant application area: [/apply](http://localhost:8080/apply)
