Brief overview of what is provided to each test class that inherits from `BaseFundTestCase`

**NOTE**: It is easy for documentation to get out of sync with code. If anything in here doesn't seem to match the results you're getting, take a look at the source:

| Location | Contains |
|----------|----------|
| [`sjfnw/tests.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/tests.py) | `BaseTestCase` |
| [`sjfnw/fund/base.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/fund/base.py) | `BaseFundTestCase` |
| [`sjfnw/fund/fixtures/`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/fund/fixtures) | fixtures used by fund tests |


#### Fixtures

By inheriting, your test will use the fixtures specified by `BaseFundTestCase` unless you overwrite that property.

#### `setUp` creates 2 giving projects

Usage:

```python
  # inside of your test's setUp method
  def setUp(self):
    super(TestClass, self).setUp()
```

Creates:  
    - Post-training GP (Fundraising training date has passed; estimates are required)  
    - Pre-training GP (Fundraising training has not happened; estimates not required)

### Test memberships

These can be used by calling one of the following methods, which create the necessary objects and then log the test user in.

Usage:
```python
  # call from inside setUp, or in an individual test method
  self.use_test_acct() # or one of the others listed below
```

#### Testy - `use_test_acct()`

- `testacct@gmail.com` User and Member (`self.member_id`)
- 2 Memberships:
    - Post-training project (`self.ship_id`) _default_
      - One Donor (`self.donor_id`) with one incomplete, overdue step (`self.step_id`)
    - LGBTQ Giving project (membership id is `1`)
      - 8 donors
      - See `sjfnw/fund/fixtures/testy.json` for details

#### Newbie - `use_new_acct()`

- `newacct@gmail.com` User and Member (`self.member_id`)
- 2 Memberships:
    - Pre-training (`self.pre_id`) _default_
    - Post-training (`self.post_id`)
- No Donors

_default_ means that `member.current` is set to that membership, so it will be used when the user logs into Project Central.

#### Admin - `use_admin_acct()`

- User with email `admin@gmail.com` that is a superuser
- No Member or Organization object associated; this one is just for testing admin site features.
