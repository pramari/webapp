Feature: Anonymous browsing pramari.

  Scenario: anonymously surf to the pramari homepage.
     Given we are using `pramari-webapp`
      When we surf to `/`
      Then webapp will serve a homepage with 200 OK.
