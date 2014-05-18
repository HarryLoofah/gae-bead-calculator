#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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

import cgi

import webapp2

MAIN_PAGE_HTML = """\
<!doctype html>
<html>
  <body>
    <form action="/bead_results" method="get">
      <div>
        <p>Enter the total number of beads in your project:</p>
        <textarea input type="text" name="beads_entered" rows="3" cols="20"></textarea>
      </div>
      <div><input type="submit" value="Run"></div>
    </form>
  </body>
</html>
"""

class MainHandler(webapp2.RequestHandler):
            
    def get(self):
        self.response.write(MAIN_PAGE_HTML)
        
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
                self.response.write('<!doctype html><html><body><pre>')
                self.response.write('<p>Error. Please use more than 12 beads.</p>')
                self.response.write('</pre></body></html>')
            
            # If beads is not divisible by 6 or 9, print error message and return
            if int(bead_input) % 6 != 0 and int(bead_input) % 9 != 0:
                self.response.write('<!doctype html><html><body><pre>')
                self.response.write('<p>Please pick a number that is divisible by 6 or 9</p>')
                self.response.write('</pre></body></html>')
                
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
                # If the list contains values, print design elements and start/add numbers.
                self.response.write('<!doctype html><html><body><pre>')
                self.response.write('<p>You can use these short/long design elements:</p>')
                self.response.write(sorted(pass_list))
                self.response.write('<p>Start with this many beads:</p>')
                self.response.write(str(starting_number))
                self.response.write('<p>and then add this many beads:</p>')
                self.response.write(str(beads_to_add))
                self.response.write('</pre></body></html>')
                
            if len(pass_list) == 0:
                # If list contains no values, find next usable number higher than beads.
                higher_list = pass_list
                high_bead = int(bead_input)
                while len(higher_list) == 0:
                    # Iterate, then check that the new number matches modulo criteria.
                    high_bead += 1
                    higher_list = [v for k, v in check_list.iteritems() if int(high_bead) % k == 0]
                    if len(higher_list) != 0 and int(bead_input) >= 12:
                        # Print a message with the suggested higher number
                        # and a list of short and long values when a usable
                        # lower number is found.
                        self.response.write('<!doctype html><html><body><pre>')
                        self.response.write('<p>Try this many beads instead:</p>')
                        self.response.write(str(high_bead))
                        self.response.write('<p>Which gives you these design options:</p>')
                        self.response.write(sorted(higher_list))
                        
                # Also, find the next usable number lower than beads.
                lower_list = pass_list
                low_bead = int(bead_input)
                # Make sure number of beads is >12 to avoid low numbers.
                while len(lower_list) == 0 and low_bead > 12:
                    # Iterate, then check if the new number matches modulo criteria.
                    low_bead -= 1
                    lower_list = [v for k, v in check_list.iteritems() if int(low_bead) % k == 0]
                    if len(lower_list) != 0:
                        # Print a message with the suggested lower number
                        # and a list of long and short values when a usable
                        # lower number is found.
                        self.response.write('<p>Or try this many beads:</p>')
                        self.response.write(str(low_bead))
                        self.response.write('<p>Which gives you these design options:</p>')
                        self.response.write(sorted(lower_list))
                        self.response.write('</pre></body></html>')
                                                
        # Run long_short_values.                
        long_short_values(bead_input)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bead_results', CalcBeadResults),
], debug=False)
