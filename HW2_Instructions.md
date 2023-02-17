# Homework 2: When a Wreck Reaches the World Wide Web

## Introduction

Unfortunately it seems your company never learns. Yet again the company
has decided to cut costs and hire Shoddycorp's Cut-Rate Contracting to 
write another program. But after all, your company insists, their *real*
strength is web sites, and this time they were hired to create a high 
quality web site. As usual they did not live up to that promise, and
are not answering calls or emails yet again. Just like last time, the
task of cleaning up their mess falls to you.

The project Shoddycorp's Cut-Rate Contracting was hired to create a 
web site that facilitated the sale, gifting, and use of gift cards.
They seemed to have delivered on *most* of the bare funcitonality of
the project, but the code is not in good shape. Luckily Kevin Gallagher
(KG) has read through the code already and left some comments around
some of the lines that concern him most. Comments not prefaced by KG were
likely left by the original author. Like with all of Shoddycorp's
Cut-Rate Contracting deliverables, this is not code you would like to
mimic in any way.

## Part 0: Setting up Your Environment

In order to complete this assignment you will need the git VCS, GitHub Actions, 
python 3 and the Django web framework (which you can install with `pip install
django`). Some additional tools that may be useful for this assignment (but are
not necessary) are sqlite, burp suite, the python requests library, and the web
development console of your favorite browser. If you are runing a \*NIX system, 
these tools should be pre-installed and/or available in your distribution's 
package manager. Like in the last assignment we will not be checking for git
best practices like writing good commit messages. However, we will be checking
for signed commits, since they are security relevant. Additionally, it is in
your best interest to continue to follow git best practices.

When you are ready to begin the project, use the Github Classroom invitation to
create your repository. You should also create a GitHub Actions YAML file, which
you will use to test your program later.

After cloning your repository, be sure to generate the database that Django
relies on. This can be done by running the commands:

```
python manage.py makemigrations LegacySite
python manage.py migrate
bash import_dbs.sh
```

Read through the `models.py` and `views.py` files (and the helper
functions in `extras.py`) in the LegacySite folder to get a feel 
for what the web site is doing and how. You can also try running
the test server and interacting with the site by running the
following command and browsing to 127.0.0.1:8000.

```
python manage.py runserver
```

## Part 1: Auditing and Test Cases

For this part, your job will be to find some flaws in the program, and
then create test cases that expose flaws in the program. You should
write:

1. *One* attack, that exploits a XSS (cross-site scripting) 
   vulnerability to call the javascript `alert("hello")`.
2. *One* attack that allows you to force another user to gift
   a gift card to your account without their knowledge.
3. *One* attack that allows you to obtain the salted password for a user
   given their username. The database contains a user named 
   `admin` that you can use for testing the attack.
4. *One* attack that allows you to run arbitrary commands on the server.
5. A text file, `bugs.txt` explaining the bug triggered by each of your
   attacks.

These attacks can take the form of a supplied URL, a gift card file, a web page,
a javascript function, or some other method of attack. To create your attacks,
you may want to look at the HTML source code of the templates and the code of
each view, and find a way they can be exploited. Tools like burp suite can help
in finding ways to attack the site, but are not required.

Please submit these attacks in a folder called `part1` in your git repository:

1. `xss.txt`: A URL starting with `http://localhost:8000/` that, when visited in
   a browser, causes `alert("hello")` to be executed.
2. `xsrf.html`: An HTML page that, when opened in a browser, causes a gift card
   to be gifted to a user named `test2` by the currently logged in user.
3. `sqli.gftcrd`: A gift card file (in JSON format) that, when uploaded to a
   vulnerable form on the site, that will retrieve the `admin` user's password
   hash.
4. `cmdi.txt`: A text file where the first line should be the vulnerable URL,
   and the remaining lines are of the form `variable=value`, representing a POST
   request that will execute the command "echo hello" on the server. For example:

   ```
   http://localhost:8000/foo/2
   var1=bar
   var2=baz
   ```

### Fixes and Testing

Finally, fix the vulnerabilites that are exploited by your attacks, and verify
that the attacks no long succeed on your site. You are allowed to use Django
plugins and other libraries to fix these vulnerabilities if necessary, but
please add any libraries you use to `requirements.txt`. To make sure that these
bugs don't come up again as the code evolves, write some test cases for Django
that verify that the vulnerability is no longer present. Then have GitHub
Actions run these tests with each push.

Tests can be run using Django's [built-in test
infrastructure](https://docs.djangoproject.com/en/4.0/topics/testing/tools/).
Just create your tests in `LegacySite/tests.py` and then run `python manage.py
test`. You should be able to write all of your tests using the built-in
Django test client--there's no need to use something like Selenium. This will
also simplify your GitHub Actions testing, which can also just run `python
manage.py test`.

You also do not need to carry out the actual attack in the test; you can just
check that your fix is working as intended. For example, when testing CSRF, it
would be difficult to actually open the `xsrf.html` page and carry out the CSRF
attack from inside the test case. Instead, you can mimic what the attack does
by making a request to the right URL without a CSRF token and checking that the
site returns an error. Likewise for verifying your fix for XSS you can check
that when getting the attack URL the `<script>` tag is properly escaped.

Note that by default, Django runs your tests with an empty database — which
means many pages will not work as you expect. The solution for this is to use
the "fixtures" feature, which lets you load sample data into the test database
before it runs the test:

```
$ mkdir LegacySite/fixtures
$ python manage.py dumpdata > LegacySite/fixtures/testdata.json
```

Then add at the top of your test case in `LegacySite/tests.py`:

```
class MyTestCase(TestCase):
    fixtures = ['testdata.json']
    # rest of test code goes here
```

This will save a copy of the current database contents into
`LegacySite/fixtures/testdata.json`, and load it when you run the test. You can
update the fixture data by re-running the `python manage.py dumpdata` command.
Don't forget to add the `LegacySite/fixtures/testdata.json` file to git so that
it is available when you run your GitHub Actions workflow!

## Part 2: Encrypting the Database 

Currently the website uses a database that contains valuable gift card
data. If an attacker gets access to this gift card data, they can use 
the cards they got to obtain free merchandise, or even pay of their
tuition with the NYU tuition gift cards! For this reason your company 
needs to make sure that even if the database somehow leaks, the attacker
will have a hard time using the cards.

Your company asked Shoddycorp's Cut-Rate Contracting to encrypt the 
database, but it seems they did not know how to do that, or did not want
to. The code you received does not encrypt the database at all, but your
company wants to ensure the data's protection at rest.

Your second job, therefore, is to modify this code to encrypt the gift card
data in the database. You are allowed to use Django plugins or external
libraries to implement this. Please see the lecture content for tips on proper
key management and the different methods of doing database encryption.

When you are finished with this part of the assignment, please briefly explain
how you implemented the database encryption, how you managed keys, and why you
choose to manage keys that way. You should also note any problems you
encountered implementing database encryption and how these were resolved. This
should be stored in a file called `encryption_explanation.txt` in a folder
called `part2` in the git repository. 

When you finish this part of the assignment, please mark your part 2 
submission by tagging the desired commit with the tag "part_2_complete".

Hints:

* You may want to look into the [djfernet](https://djfernet.readthedocs.io/en/latest/) package.

* You only need to encrypt the `Card.data` field, but you can try encrypting other fields if you like.

* Not all database fields can be encrypted -- in particular, keys that are used for the structure of the database, like primary and foreign keys, cannot be encrypted.

* You should test the functionality of the site after encrypting a field. You may find that some functionality no longer works after encrypting a field (in particular, the logic used in the `use_card_view` to find a card in the database that matches what the user uploaded will no longer work once you encrypt the card data). You should modify the application code to fix this.

## Grading

Total points: 100

Part 1 is worth 65 points:

* 20 points for your attack cases (5 points for each attack)
* 20 points for all fixes (5 points for each fix)
* 10 points for the bug writeup
* 10 points for GitHub Actions testing
* 05 points for signed git commits

Part 2 is worth 35 points:

* 15 points for encrypted database models
* 15 points for proper key management
* 05 points for your writeup

## What to Submit

On Brightspace, submit a link to your GitHub repository. 

The repository should contain:

* Part 1
  * At least one signed commit
  * A directory named `part1` that contains your attack cases.
  * A GitHub Actions YAML that runs your tests.
  * A commit with the fixed version of the code (if you like, this
    commit can also contain the files mentioned above).
* Part 2
  * A directory named `part2` which contains your 
    `encryption_explanation.txt` file.
  * A commit with the version of the code that supports DB encryption
    (if you like, this commit can also contain the files mentioned above).

## Concluding Remarks

Despite the fixes you've made, there are almost certainly still many
bugs lurking in the program. Although it is possible to get to a secure
program by repeatedly finding and fixing bugs, it's a lot of work.

Though this program may be salvagable in its current state, it would be 
better in this case to rewrite it from scratch, using proper style, 
using Django addons for security purposes, and sticking to using ORMs 
and avoiding reflected unfiltered user input to the users. The code as
it exists now is difficult to read, and therefore difficult to fix. It
also unecessarily uses home-brewed solutions for things that can be solved
easily with common libraries or Django built-ins. This is certainly not
code that you should seek to reproduce, or use as an example of good code.
