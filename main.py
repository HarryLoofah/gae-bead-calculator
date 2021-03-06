#!/usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Greg Aitkenhead
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
bead-calculator
============

A simple Python script to help peyote stitch beadworkers start their projects.
BeadCalculator checks to make sure the number of beads used in a project will
work out mathematically and lets the beadworker know what design elements
will be possible for the number of starting beads entered.

##To Use:
1. Measure the object that you'll be beading by stringing beads and wrapping
thread around the object.
2. Enter the number of beads from the initial measurement around the object.
3. BeadCalculator tells you if that number of beads will work, and if it does
not, BeadCalculator suggests an alternative number or numbers to start with.

BeadCalculator also tells the beadworker how many beads to string, how many to
add (when the first two lines of beads are added to the project), and what long
and short side design elements will be available.
"""

import cgi
import logging
import webapp2
import jinja2

from jinja2 import Environment, FileSystemLoader


ENV = Environment(loader=FileSystemLoader('templates'))


class MainHandler(webapp2.RequestHandler):
    """Renders the root of the web-app using base.html as the template."""
    def get(self):
        """Create main web page."""
        template = ENV.get_template('base.html')
        self.response.write(template.render())


class CalcBeadResults(webapp2.RequestHandler):
    """
    Run all logic and create templates depending on value of beads_entered.
    Value 'beads_entered/ comes from textarea value of main-form in base.html.
    """
    def get(self):
        """Gets number of beads entered from base.html form input."""
        bead_input = cgi.escape(self.request.get('beads_entered'))

        def sanity_check(bead_input):
            """Before running full code, check to see that the number entered
            (beads), is greater than 12 and that it is divisible by 6 or 9.
            If 'beads' is less than 12, print error message.
            """
            if int(bead_input) < 12:
                beads_user_chose = str(bead_input)
                more_beads_message = "Please re-try using more than 12 beads."
                template = ENV.get_template('try-again.html')
                self.response.write(
                    template.render(
                        beads_user_chose=beads_user_chose,
                        more_beads_message=more_beads_message)
                )
        # Run sanity_check.
        sanity_check(bead_input)

        def long_short_values(bead_input):
            """
            Returns short and long side numbers of design elements depending on
            whether the beads_entered is mod 6, 9, or 12. If number of beads
            entered is not mod 6 or 9, long_short_values finds the higher and
            lower values matching the above criteria and then suggests those
            numbers to the user. Also shows the new list values so that the
            user can see which option offers the most design choices.
            """
            # Lists of possible results for design elements (values)
            # where key represents the modulo interger.
            check_list = {
                6: (3, 5),
                9: (4, 7),
                12: (5, 9)
            }
            pass_list = [v for k, v in check_list.iteritems()
                         if int(bead_input) % k == 0]

            if len(pass_list) != 0 and int(bead_input) >= 12:
                # Suggest starting bead number and number of beads to add.
                # These formulas are based on the specific 'three drop' peyote
                # stitch pattern used (as opposed to the simpler 'two drop.')
                suggested = int(bead_input)
                beads_to_add = suggested/3
                starting_number = beads_to_add*2
                pass_list = ", ".join(repr(e) for e in sorted(pass_list))
                starting_number = str(starting_number)
                beads_to_add = str(beads_to_add)
                beads_user_chose = str(bead_input)

                # If pass_list contains values, print design elements and
                # start/add numbers. See /templates/pass-test.html, which
                # extends base.html.
                template = ENV.get_template('pass-test.html')
                self.response.write(
                    template.render(
                        beads_user_chose=beads_user_chose,
                        pass_list=pass_list,
                        starting_number=starting_number,
                        beads_to_add=beads_to_add
                    )
                )

            if len(pass_list) == 0:
                # If list contains no values, find next usable number.
                higher_list = pass_list
                high_bead = int(bead_input)

                while len(higher_list) == 0:
                    # Check that new number matches modulo criteria.
                    high_bead += 1
                    higher_list = [v for k, v in check_list.iteritems()
                                   if int(high_bead) % k == 0]

                    if len(higher_list) != 0 and int(bead_input) >= 12:
                        # If pass_list does not contain values,
                        # suggest usable design element numbers
                        # for both next bead higher and next bead lower.
                        high_bead = str(high_bead)
                        higher_list = ", ".join(repr(e) for e in
                                                sorted(higher_list))

                # Also, find the next usable number lower than beads.
                lower_list = pass_list
                low_bead = int(bead_input)

                # Make sure number of beads is >12 to avoid low numbers.
                while len(lower_list) == 0 and low_bead > 12:
                    # Check to see if the new number matches modulo criteria.
                    low_bead -= 1
                    lower_list = [v for k, v in check_list.iteritems()
                                  if int(low_bead) % k == 0]

                    if len(lower_list) != 0:
                        # Suggest design elements for lower bead options.
                        low_bead = str(low_bead)
                        lower_list = ", ".join(
                            repr(e) for e in sorted(lower_list)
                        )
                        beads_user_chose = str(bead_input)
                        template = ENV.get_template('no-pass.html')
                        self.response.write(
                            template.render(
                                beads_user_chose=beads_user_chose,
                                high_bead=high_bead,
                                higher_list=higher_list,
                                low_bead=low_bead,
                                lower_list=lower_list
                            )
                        )
        # Run long_short_values.
        long_short_values(bead_input)


APP = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bead_results', CalcBeadResults)
], debug=False)


# Extra Hanlder like 404 500 etc
def handle_500(request, response, exception):
    """Create custom error responses."""
    logging.exception(exception)
    response.write('Oops! This is a 500 error. ')
    response.write('This program can only process numbers. ')
    response.write('Please use the back arrow and try again.')
    response.set_status(500)

APP.error_handlers[500] = handle_500
