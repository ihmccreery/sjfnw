We use github's built-in issues system to keep track of dev tasks: see [issues](https://github.com/aisapatino/sjfnw/issues) tab.

## Overview

- **Always search issues before creating a new one to make sure it hasn't already been filed.**
- Everything that a dev thinks needs to be done or that is requested/suggested by staff/other users is recorded as an issue.
- Issues are organized using milestones and labels - see below for details. Short version:
  - Current active milestone always starts with ★
  - Priority labels: `p1` is highest priority, `p4` is lowest
- **If you are looking for something to do, check the [`ready` label](https://github.com/aisapatino/sjfnw/issues?q=is%3Aopen+is%3Aissue+label%3Aready)**. That's used for tasks that should be ready to work on.

## Milestones

- There is always an active milestone for current tasks. It has a due date and always starts with a ★ to make it easier to find in the dropdown.
- Three milestones for broad sorting:
  - `Backlog - to do` tasks that we definitely want to do. Look through this when picking tasks for the active milestone.
  - `Backlog - lower priority` tasks that we'd like to do, but may not get to.
  - `Future ideas` tasks that are too time consuming and/or not beneficial enough to prioritize. These are often ideas without much definition.

## Labels

Labels are used for more fine-grained categorizing of issues. See the [labels](https://github.com/aisapatino/sjfnw/labels) page for a current list. This may get out of sync, but is meant to provide some explanation for how they're organized.

Labels are prefixed so that they are in order in the dropdown, making it easier to apply them. They are often abbreviated so that issues list isn't too cluttered.

```
area:
  admin            related to the admin site (included custom admin pages like reporting)
  grants           related to the grant application portal
  project central  related to the fundraising app

lang(uage):        this is a new set of labels and isn't thoroughly applied yet. it is
  html/css         intended as a way for potential contributors to identify front-end focused tasks
  js               that don't involve much python/django

(priority):
  p1               most important/urgent. definitely should get done
  p2               important, but not pressing
  p3               would like to do eventually
  p4               other ideas, some of which may never be implemented

status:
  archived         closed without fixing/doing
  staff            waiting on information/direction from staff
  ready            ready to be worked on  - issue should be clearly described with links/refs if applicable

type:
  bug              unintended behavior that breaks or interferes with existing functionality
  dev              development work that may not have an effect from the user perspective. ex: code refactors
  meta             umbrella issue. things like "figure out steps to do x" or "design review."
                   will usually not result in code changes, but in more specific tickets being created
  feature          add new functionality
  performance      usually refers to reducing load times
  tests            related to automated tests
  ui/ux            improvements to appearance or interaction flow 

mobile             (not prefixed) mobile-specific
```