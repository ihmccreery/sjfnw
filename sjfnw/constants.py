# Cron jobs
FUND_EMAIL = 'Project Central <projectcentral@socialjusticefund.org>'
GRANT_EMAIL = 'Social Justice Fund Grants <grants@socialjusticefund.org>'
APP_BASE_URL = 'https://sjf-nw.appspot.com'

# Support pages
SUPPORT_EMAIL = 'techsupport@socialjusticefund.org'
GOOGLE_FORM = 'https://docs.google.com/forms/d/{}/viewform?entry.804197744='
FUND_SUPPORT_FORM = GOOGLE_FORM.format('1ssR9lwBO-8Z0qygh89Wu5XK6YwxSmjIFUtOwlJOjLWw')
GRANT_SUPPORT_FORM = GOOGLE_FORM.format('1SKjXMmDgXeM0IFp0yiJTJgLt6smP8b3P3dbOb4AWTck')


# Grants forms
ALLOWED_FILE_TYPES = ('jpeg', 'jpg', 'png', 'gif', 'bmp', 'doc', 'docx',
                      'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt')
PHOTO_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp']
VIEWER_FORMATS = ('doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf',
                  'mpeg4', 'mov', 'avi', 'wmv')
TIMELINE_FIELDS = [
  'timeline_0', 'timeline_1', 'timeline_2', 'timeline_3', 'timeline_4',
  'timeline_5', 'timeline_6', 'timeline_7', 'timeline_8', 'timeline_9',
  'timeline_10', 'timeline_11', 'timeline_12', 'timeline_13', 'timeline_14'
]
US_STATES = ['ID', 'MT', 'OR', 'WA', 'WY',
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IL', 'IN',
    'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'NE', 'NV',
    'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'PA', 'RI', 'SC', 'SD', 'TN',
    'TX', 'UT', 'VT', 'VA', 'WV', 'WI']

# Membership middleware
NO_MEMBER = 0
NO_MEMBERSHIP = 1
NO_APPROVED = 2
APPROVED = 3
