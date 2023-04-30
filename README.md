# minnehack-2023
Project for Minnehack 2023

## Inspiration
Bookend is an electronic library management tool aimed to make classroom library management easier for
elementary school educators. Teachers typically have hundreds of books in their library, with many books lent out to their students at a time.

Some teachers use spreadsheets to keep track of their library, but constantly updating a spreadsheet is time-consuming and can lead to confusion.

_Bookend_ is the much needed successor, providing a robust system for book tracking and putting an **end** to Google Sheet back-ends!

## What it does
_Bookend_ utilizes a handheld bar code scanner to scan book ISBN bar codes to add and track books for your personal library.

_Bookend_ can:
  - Manage your library
  - Search books by title or ISBN
  - Track which books users have checked-out
  - Export your library and users as a .csv
  - Scan books with your mobile phone to add books to your library
  - Automatically gather book metadata when ISBN is provided

## How we built it
We built the _Bookend_ website using **Django**, a python web framework. We chose Django, because it takes care of much of the database and data-layer automagically, allowing developers to focus on the user experience, rather than how the data flows through the system.

We also chose to build a cross-platform mobile  companion app using **Flutter**, so that users without a bar code scanners could still easily add books to their library.

During the early phases of development, we leveraged **Figma** to create UI mock-ups of _Bookend_ to quickly determine which UI/UX choices would benefit our user the most. These mock-ups led to a design with large buttons and text, perfect for touch devices, in case the user would like to create their own _Bookend_ kiosk.

Since not every developer is familiar with Python and Django, we built a **Docker** image that can easily be deployed with a single command!

## Challenges we ran into
The team had a limited knowledge of Django coming into this competition. We were all also pretty rusty on our CSS. What seemed to be trivial things like centering elements and navbar/footer placement ended up being more difficult than anticipated.

We attempted to add SSL to our public server using Let's Encrypt, but after toying with it for a while it become a low priority for us.

## Accomplishments that we're proud of
We're proud that we were able to put together a project like this with a new framework (to us at least). None of us would consider ourselves professional web developers, but given the knowledge and time limitations, we are very happy with the end result.

## What we learned
We learned that when we all start to get tired, it helps to begin pair programming, as it allows for one person to focus on code, while the other person can better grasp the problem being tackled.
