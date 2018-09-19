# -*- coding: utf-8 -*-
from datetime import *

def get_raw_day(title, num_stages, day_links, stages_html):
    return (
"""<!doctype html>
<html lang="en" class="no-js">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,600" rel="stylesheet">
	<link rel="stylesheet" href="css/reset.css"> <!-- CSS reset -->
	<link rel="stylesheet" href="css/style.css"> <!-- Resource style -->

	<title>"""+title+"""</title>

	<style>
		.cd-schedule .events li.events-group {
			width: calc(100% /"""+str(num_stages)+""")
		}
	</style>
</head>
<body>

"""+day_links+"""
<div class="cd-schedule loading">
	<div class="timeline">
		<ul>
            <li><span>15:00</span></li>
            <li><span>15:30</span></li>
            <li><span>16:00</span></li>
            <li><span>16:30</span></li>
			<li><span>17:00</span></li>
			<li><span>17:30</span></li>
			<li><span>18:00</span></li>
			<li><span>18:30</span></li>
			<li><span>19:00</span></li>
			<li><span>19:30</span></li>
			<li><span>20:00</span></li>
			<li><span>20:30</span></li>
			<li><span>21:00</span></li>
			<li><span>21:30</span></li>
			<li><span>22:00</span></li>
			<li><span>22:30</span></li>
			<li><span>23:00</span></li>
			<li><span>23:30</span></li>
			<li><span>00:00</span></li>
			<li><span>00:30</span></li>
			<li><span>01:00</span></li>
			<li><span>01:30</span></li>
			<li><span>02:00</span></li>
			<li><span>02:30</span></li>
			<li><span>03:00</span></li>
			<li><span>03:30</span></li>
			<li><span>04:00</span></li>
			<li><span>04:30</span></li>
			<li><span>05:00</span></li>
			<li><span>05:30</span></li>
			<li><span>06:00</span></li>
			<li><span>06:30</span></li>
		</ul>
	</div> <!-- .timeline -->

	<div class="events">
		<ul>



			"""+stages_html+"""




		</ul>
	</div>



	<div class="event-modal">
		<header class="header">
			<div class="content">
				<span class="event-date"></span>
				<h3 class="event-name"></h3>
			</div>

			<div class="header-bg"></div>
		</header>

		<div class="body">
			<div class="event-info"></div>
			<div class="body-bg"></div>
		</div>

		<a href="#0" class="close">Close</a>
	</div>

	<div class="cover-layer"></div>
</div> <!-- .cd-schedule -->
<script src="js/modernizr.js"></script>
<script src="js/jquery-3.0.0.min.js"></script>
<script>
	if( !window.jQuery ) document.write('<script src="js/jquery-3.0.0.min.js"><\/script>');
</script>
<script src="js/main.js"></script> <!-- Resource jQuery -->
</body>
</html>
""")


STAGE_HTML = (
"""
<li class="events-group">
   <div class="top-info"><span>%s</span></div>
   <ul>%s</ul>
</li>
""")

DAY_ID = 0
EVENT_ID = 0

def get_day_links(day_id, days):
    day_links = ''
    for idx, day in enumerate(days):
        if idx == day_id:
            day_links += '<a href="./index'+str(idx)+'.html"><button disabled>'+day+'</button></a>'
        else:
            day_links += '<a href="./index'+str(idx)+'.html"><button>'+day+'</button></a>'

    return day_links

def create_day_html(title, stages, day_id, days):
    num_stages = len(stages)
    global DAY_ID
    day_links = get_day_links(day_id, days)
    stages_html = '\n'.join(stages)
    day_html = get_raw_day(title, num_stages, day_links, stages_html)
    # Create day file
    f_day = open('./files/index'+str(DAY_ID)+'.html', 'w')
    f_day.write(day_html)
    f_day.close()
    DAY_ID += 1

def get_stage_html(stage_name, events):
    return STAGE_HTML % (stage_name, ' '.join(events))

def get_event_info(event):
    event_start = event['time']
    event_end = datetime.strptime(event_start, '%H:%M')
    event_end = event_end + timedelta(minutes=45)
    event_end = event_end.strftime('%H:%M')
    event_youtube = event['link']
    event_name = event['event']
    return event_start, event_end, event_name, event_youtube

def get_create_event_html(event_info, stage_id):
    global EVENT_ID
    EVENT_ID += 1
    event_start, event_end, event_name, event_youtube = get_event_info(event_info)

    # Create event file
    f_event = open('./files/event-'+str(EVENT_ID)+'.html', 'w')
    f_event.write('''<div class="event-info">
    	<div width="500px">
    		<iframe class="youtube-video" width="420" height="315" z-index="55555"
    			src="'''+event_youtube+'''">
    		</iframe>
    	</div>
    </div>''')  # python will convert \n to os.linesep
    f_event.close()

    # Return event HTML
    return '''<li class="single-event" data-start="'''+event_start+'''" data-end="'''+event_end+'''"  data-content="event-'''+str(EVENT_ID)+'''" data-event="event-'''+str(stage_id)+'''">
        <a href="#0">
            <em class="event-name">'''+event_name+'''</em>
        </a>
    </li>'''
