cOrr2
=====

Grading is painful. It generally involves (at least in my case) repeating the
same thing hundreds of times in a row. This repetitive task is prone to errors
and may also lead to severe mental disorder.

**cOrr2** puts (more) fun into grading.

cOrr2 is a Web-based grading tool. The input is an XML description (hopefully
a more visual editor can be built in the future) of a grade sheet and the output
is a Web template where you may easily fill grades in.

Here's a simple example of a template:

```
<?xml version="1.0" encoding="UTF-8"?>
<!--
A very simple cOrr2 XML template.
-->
<corr>
    <head>
        <title>ENG101: report #2</title>
        <settings>
            <unique-id section-id="id" field-id="name" />
        </settings>
    </head>

    <body>
        <section id="id" title="Identification">
            <gen id="name" title="Student name" />
        </section>

        <section id="report" title="Text report">
            <gen id="subject" title="Report subject" mandatory="true" />
            <grade id="title" title="Folder/title page" max="5">
                <info>
                    <![CDATA[
                        <p>Include:</p>
                        <ul>
                            <li>Student name and ID</li>
                            <li>School name</li>
                            <li>Date</li>
                            <li>Report title</li>
                        </ul>
                    ]]>
                </info>
            </grade>
            <grade id="indexc" title="Index cards" max="10" />
            <grade id="ownwords" title="Own words" max="15" />
            <grade id="headings" title="Headings" max="15" default="max" />
            <grade id="language" title="Language" max="20">
                <info escape="true">Spelling (5), grammar (10), punctuation (5)</info>
            </grade>
            <grade id="order" title="Logical order, complete" max="20" />
            <grade id="timeline" title="Timeline" max="15" />
            <gen id="comments" title="Comments" multiline="true" />
        </section>
    </body>
</corr>
```

After running cOrr2, go to its URL and you get this:

![cOrr2 output example](http://0x3b.org/ss/thouing952.png)

Once saved, the output is a JSON file which can later be processed to give back
results to students or a report to the school.


dependencies
------------

cOrr2 is built in Python 3 and needs the following packages:

  * [lxml](http://lxml.de/)
  * [Flask](http://flask.pocoo.org/docs/)

`lessc` is also needed to build the CSS file.


getting started
---------------

After cloning, you need to compile the CSS file using `lessc`:

    $ make -C less

Make sure the project's root directory (where `example/` and `bin/` are) is in your
Python's path:

    $ export PYTHONPATH=$(pwd)

and start cOrr2:

    $ python bin/corr examples/simple.xml

You should see something like:

```
INFO:root:Starting cOrr2
INFO:root:Parsing template "examples/simple.xml"
INFO:root:Parsed template:
INFO:root:    Title: ENG101: report #2
INFO:root:    Sections:
INFO:root:        Identification:
INFO:root:            Student name  [general field]
INFO:root:        Text report:
INFO:root:            Report subject  [general field]
INFO:root:            Folder/title page  [grade field]
INFO:root:            Index cards  [grade field]
INFO:root:            Own words  [grade field]
INFO:root:            Headings  [grade field]
INFO:root:            Language  [grade field]
INFO:root:            Logical order, complete  [grade field]
INFO:root:            Timeline  [grade field]
INFO:root:            Comments  [general field]
INFO:root:Starting cOrr2 server
INFO:werkzeug: * Running on http://127.0.0.1:8080/
```

Point your browser to `http://127.0.0.1:8080/` and start grading! When saving,
JSON results files will be written to your current working directory. You may
change this output directory (and other stuff like the host address and port)
using options. Do

    $ python bin/corr -h

to see the list of options.


todo
----

  * cOrr2 visual template editor
  * XML template RELAX NG validation
  * edit already saved results
  * prevent results file overwriting
