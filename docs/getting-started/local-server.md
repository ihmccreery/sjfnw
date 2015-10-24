### Start the server

From inside the root of the repo do

`dev_appserver.py .`

_If you get something like 'command not found', make sure GAE is in your path. Use `echo $PATH` to confirm. See [setup](installation-and-setup.md#update-paths)._

---

### Create accounts (first time only)

The superuser you created in the `syncdb` step of [setup](installation-and-setup#setting-up-the-database) gives you access to the admin site. For using the app locally you'll want to be able to log into the fundraising and grant application areas too.

1. Go to `/admin-advanced`\* and log in with superuser email & pw you created when you ran `syncdb`.
2. Create a `Member` object so you can log into the fundraising app:
    - Click on `+ Add` next to `Members`
    - Enter the email you used to log in, and whatever first & last name you want.
    - Hit `Save`
3. Go back to `/admin-advanced` to create an `Organization` for yourself:
    - Click on `+Add` next to `Organizations`
    - Enter the same email, fill in whatever other fields are required
    - Hit `Save`
4. You should now be able to log into both sides of the app: `/fund/login` and `/apply/login`

\* The advanced admin site is only used by devs (and should eventually be replaced with better admin permissions). Staff use `/admin`, which you can use most of the time, but for this you need additional access.
