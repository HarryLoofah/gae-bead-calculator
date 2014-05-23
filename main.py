#!/usr/bin/env python
#
# Copyright 2014 Greg Aitkenhead
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import cgi
import logging

import webapp2
import jinja2

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


class MainHandler(webapp2.RequestHandler):
            
    def get(self):

        template = env.get_template('base.html')
        self.response.write(template.render())
        
class CalcBeadResults(webapp2.RequestHandler):
    
    def get(self):
        bead_input = cgi.escape(self.request.get('beads_entered'))
        
        def sanity_check(bead_input):
            """
            Before running full code, check to see that the number entered
            (beads), is greater than 12 and that it is divisible by 6 or 9.
            """
            # If beads is less than 12, print error message and return.
            if int(bead_input) < 12:
                more_beads_message = "Error. Please use more than 12 beads."

                template = env.get_template('try-again.html')
                self.response.write(template.render(more_beads_message = more_beads_message))
                
        # Run sanity_check.
        sanity_check(bead_input)
        
        def long_short_values(bead_input):
            """
            Returns short and long side of design elements depending on
            whether the number of beads entered in raw_input is mod 6, 9, or 12.
            If number of beads entered is not mod 6 or 9, find the higher and
            lower values that match the above criteria and suggest those numbers to
            the user. Also show the new list values so that the user can see which
            option woulo offer more design choices.
            """
            # Lists of possible results for design elements (values)
            # where key represents the modulo interger.
            check_list = {
                6: (3, 5),
                9: (4, 7),
                12: (5, 9)
                }
            pass_list = [v for k, v in check_list.iteritems() if int(bead_input) % k == 0]
            
            if len(pass_list) != 0 and int(bead_input) >= 12:
                # Suggest starting bead number and number of beads to add.
                # These formulas are based on the specific 'three drop' peyote
                # stitch pattern used (as opposed to the simpler 'two drop.'
                suggested = int(bead_input)
                beads_to_add = suggested/3
                starting_number = beads_to_add*2

                pass_list = ", ".join(repr(e) for e in sorted(pass_list))
                starting_number = str(starting_number)
                beads_to_add = str(beads_to_add)

                # If pass_list contains values, print design elements and start/add numbers.
                template = env.get_template('pass-test.html')
                self.response.write(template.render(
                                                    pass_list = pass_list, 
                                                    starting_number = starting_number, 
                                                    beads_to_add = beads_to_add))
                
            if len(pass_list) == 0:
                # If list contains no values, find next usable number higher than beads.
                higher_list = pass_list
                high_bead = int(bead_input)
                while len(higher_list) == 0:
                    # Iterate, then check that the new number matches modulo criteria.
                    high_bead += 1
                    higher_list = [v for k, v in check_list.iteritems() if int(high_bead) % k == 0]
                    if len(higher_list) != 0 and int(bead_input) >= 12:
                        # If pass_list does not contain values,
                        # suggest usable design element numbers
                        # for both next bead higher and next bead lower.
                        high_bead = str(high_bead)
                        higher_list = ", ".join(repr(e) for e in sorted(higher_list))


                # Also, find the next usable number lower than beads.
                lower_list = pass_list
                low_bead = int(bead_input)
                # Make sure number of beads is >12 to avoid low numbers.
                while len(lower_list) == 0 and low_bead > 12:
                    # Iterate, then check if the new number matches modulo criteria.
                    low_bead -= 1
                    lower_list = [v for k, v in check_list.iteritems() if int(low_bead) % k == 0]
                    if len(lower_list) != 0:
                        # Suggest design elements for lower bead options.

                        low_bead = str(low_bead)
                        lower_list = ", ".join(repr(e) for e in sorted(lower_list))

                        template = env.get_template('no-pass.html')
                        self.response.write(template.render(
                                                    high_bead = high_bead, 
                                                    higher_list = higher_list,
                                                    low_bead = low_bead, 
                                                    lower_list = lower_list))
                                                
        # Run long_short_values.                
        long_short_values(bead_input)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bead_results', CalcBeadResults),
], debug=False)


# Extra Hanlder like 404 500 etc
def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('Oops! This is a 500 error. ')
    response.write('This program can only process numbers. ')
    response.write('Please use the back arrow and try again.')
    response.set_status(500)

app.error_handlers[500] = handle_500
