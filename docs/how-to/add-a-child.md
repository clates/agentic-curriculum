# Add a child

This guide shows you how to add a child to a family in the hosted app, and what happens next.
A family can have up to five children.

## Add your first child

A new family has no children, so after sign-up the app opens "Welcome". You fill in the form there.
If you sign in to a family with no children, "This week" sends you to the same page.

## Add another child

1. Open "This week". Press "Add a child" under the child cards. The button is there while the
   family has fewer than five children and the login is on.
2. Fill in the form:
   - **First name.** Use a first name only.
   - **Interests.** Optional. Separate them with commas, such as `dinosaurs, baking, soccer`.
   - **Math grade** and **Reading and writing grade.** Pick `K` or 1 to 8. Pick each one for where
     the child works now, not their age. They can differ.
   - **Notes.** Optional. Anything else the planner should know.
3. Press "Save and plan the week".

The app then opens "This week" with the new child's card.

Keep last names, addresses and anything private out of the form. An AI service reads what you
write to plan activities.

## What happens next

The child's first week starts straight away. You don't wait for Friday.

- Added Monday to Wednesday: the week starts this Monday.
- Added Thursday to Sunday: the week starts next Monday.

The days are in the server's default timezone, `SCHEDULER_DEFAULT_TZ` (New York unless the
operator changed it). If the operator set a timezone for your family, the days are in that one
instead; see [Set a family's timezone](run-the-worker.md#set-a-familys-timezone). With the weekly
loop on, ideas for the week are generated.
With it off, the plan is made but no ideas are. See
[Run the worker](run-the-worker.md#turn-the-loop-on-on-the-server).

The grades are starting points and stay as you set them. The planner adjusts from what the first
few check-ins show the child knows.

## If something goes wrong

- **"You can add up to five children."** The family is full. Delete a child first.
- **The form reports too many interests, or one that is too long.** Use up to 8, each up to 40
  characters.
- **"Something in the form needs fixing."** Check each answer against the limits above and save
  again.
- **"We couldn't save this just now."** Try again.

Fields, limits and responses: [Children reference](../reference/children.md). Why grades are
per subject: [The weekly loop](../explanation/the-weekly-loop.md#why-math-has-its-own-grade).
