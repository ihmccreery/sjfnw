from sjfnw import constants as c

PHOTO_FILE_TYPES = ('jpeg', 'jpg', 'png', 'gif', 'bmp')

VIEWER_FILE_TYPES = ('doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf')

ALLOWED_FILE_TYPES = PHOTO_FILE_TYPES + VIEWER_FILE_TYPES + ('txt',)

STATE_CHOICES = [(state, state) for state in c.US_STATES]

STATUS_CHOICES = [
  ('Tribal government', 'Federally recognized American Indian tribal government'),
  ('501c3', '501(c)3 organization as recognized by the IRS'),
  ('501c4', '501(c)4 organization as recognized by the IRS'),
  ('Sponsored', 'Sponsored by a 501(c)3, 501(c)4, or federally recognized tribal government')
]

PRE_SCREENING = (
  (10, 'Received'),
  (20, 'Incomplete'),
  (30, 'Complete'),
  (40, 'Pre-screened out'),
  (45, 'Screened out by sub-committee'),
  (50, 'Pre-screened in')
)

SCREENING = (
  (60, 'Screened out'),
  (70, 'Site visit awarded'),
  (80, 'Grant denied'),
  (90, 'Grant issued'),
  (100, 'Grant paid'),
  (110, 'Year-end report overdue'),
  (120, 'Year-end report received'),
  (130, 'Closed')
)

# index matches question number
NARRATIVE_CHAR_LIMITS = [0, 300, 150, 450, 300, 300, 450, 750, 300]
NARRATIVE_TEXTS = ['Placeholder for 0',
  ('Describe your organization\'s mission, history and major '
   'accomplishments.'),
  ('Social Justice Fund prioritizes groups that are led by the people most '
   'impacted by the issues the group is working on, and continually build '
   'leadership from within their own communities.<ul><li>Who are the '
   'communities most directly impacted by the issues your organization '
   'addresses?</li><li>How are those communities involved in the leadership '
   'of your organization, and how does your organization remain accountable '
   'to those communities?</li><li>What is your organization\'s <span '
   'class="has-more-info" id="nar-2">leadership body?</span></li></ul>'),
  ('Social Justice Fund prioritizes groups that understand and address the '
  'underlying, or root causes of the issues, and that bring people together '
  'to build collective power.<ul><li>What problems, needs or issues does '
  'your work address?</li><li>What are the root causes of these issues?</li>'
  '<li>How does your organization build collective power?</li><li>How will '
  'your work change the root causes and underlying power dynamics of the '
  'identified problems, needs or issues?</li></ul>'),
  ('Please describe your workplan, covering at least the next 12 months. '
   '(You will list the activities and objectives in the timeline form below,)'
   '<ul><li>What are your overall <span class="has-more-info" id="nar-4">'
   'goals, objectives and strategies</span> for the coming year?</li>'
   '<li>How will you assess whether you have met your goals and objectives?'
   '</li></ul>'),
  ('Social Justice Fund prioritizes groups that see themselves as part of a '
   'larger movement for social change, and work towards strengthening that '
   'movement.<ul><li>Describe at least two coalitions, collaborations, '
   'partnerships or networks that you participate in as an approach to '
   'social change.</li><li>What are the purposes and impacts of these '
   'collaborations?</li><li>What is your organization\'s role in these '
   'collaborations?</li><li>If your collaborations cross issue or '
   'constituency lines, how will this will help build a broad, unified, and '
   'effective progressive movement?</li></ul>'),
  ('Social Justice Fund prioritizes groups working on racial justice, '
   'especially those making connections between racism, economic injustice, '
   'homophobia, and other forms of oppression. Tell us how your organization '
   'is working toward racial justice and how you are drawing connections to '
   'economic injustice, homophobia, and other forms of oppression. <i>While '
   'we believe people of color must lead the struggle for racial justice, '
   'we also realize that the demographics of our region make the work of '
   'white anti-racist allies critical to achieving racial justice.</i>'
   'If your organization\'s <span class="has-more-info" id="nar-6">'
   'leadership body</span> is majority white, also describe how you work as '
   'an ally to communities of color. Be as specific as possible, and list at '
   'least one organization led by people of color that we can contact as a '
   'reference for your racial justice work. Include their name, '
   'organization, phone number and email.')
]

HELP_TEXTS = {
  'leadership': ('Your organization\'s leadership body is the group of '
      'people who together make strategic decisions about the '
      'organization\'s direction, provide oversight and guidance, and are '
      'ultimately responsible for the organization\'s mission and ability '
      'to carry out its mission. In most cases, this will be a Board of '
      'Directors, but it might also be a steering committee, collective, '
      'or other leadership structure.'),
  'goals': ('<ul><li>A goal is what your organization wants to achieve or '
      'accomplish. You may have both internal goals (how this work will '
      'impact your organization) and external goals (how this work will '
      'impact your broader community).</li><li>An objective is generally '
      'narrower and more specific than a goal, like a stepping stone along '
      'the way.</li><li>A strategy is a road map for achieving your goal. '
      'How will you get there? A strategy will generally encompass '
      'multiple activities or tactics.</li></ul>'),
}
