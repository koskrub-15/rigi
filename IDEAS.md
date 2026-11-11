# Ideas

- Days are counted in UTC: a trip at 00:30 Berlin time lands on the previous day,
  both in the per-day chart and when the optimizer picks a day ticket.
- Stats for a long period must sum the monthly bills, not optimize the whole period
  at once (a weekly ticket across a month boundary gives 947 instead of the real 954).
  The optimizer is also O(days²): ~33 ms for a year, ~300 ms for three.
- Validate `date_from < date_to` (return 422); now an inverted range silently returns zeros.
- Zone codes are static: a photo of a stop's QR works from home. Close it with codes
  that rotate on a validator screen (short `exp`) or a GPS check; add `kid` for key rotation.
- A single ticket is valid for 60 minutes with free transfers, like real tariffs. Now
  every trip is its own single, so two 15-minute rides at 8:00 and 8:30 cost two
  singles. With a time window one single can cover several trips, so inside a day the
  optimizer has to group trips into windows — a small DP of its own, the same "which
  ticket covers which stretch" idea as the week ticket, in hours instead of days.
  Open question: how many zones such a ticket covers when its trips differ.
- Leaderboard of riders by trip count, opt-in only: a `show_in_leaderboard` flag that is
  off by default and a public name like "Konstantin K." instead of the email. Needs real
  users to look alive; with two or three it reads as empty.
- "You ride more than 70% of riders": compare a user with the average, shown only when
  the sample has at least N users, otherwise an average of three reveals the others.
- GPS would make the stats far richer: kilometres, speed, the actual route. A PWA cannot
  track location in the background (`watchPosition` stops when the page is not on
  screen), so full tracking needs a native app. A middle step: record the location at
  the moment of a scan and check it against the zone, which also closes the
  "photo of a stop's QR" hole.
