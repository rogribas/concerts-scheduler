# -*- coding: utf-8 -*-
from datetime import *

def get_raw_day(lowest_event_time, title, num_stages, day_links, stages_html):
    times = [
            '<li><span style="display: none">10:00</span></li>',
            '<li><span style="display: none">10:30</span></li>',
            '<li><span style="display: none">10:30</span></li>',
            '<li><span style="display: none">11:00</span></li>',
            '<li><span style="display: none">11:00</span></li>',
            '<li><span style="display: none">11:30</span></li>',
            '<li><span style="display: none">12:00</span></li>',
            '<li><span style="display: none">12:30</span></li>',
            '<li><span style="display: none">13:00</span></li>',
            '<li><span style="display: none">13:30</span></li>',
            '<li><span style="display: none">14:00</span></li>',
            '<li><span style="display: none">14:30</span></li>',
            '<li><span style="display: none">15:00</span></li>',
            '<li><span style="display: none">15:30</span></li>',
            '<li><span style="display: none">16:00</span></li>',
            '<li><span style="display: none">16:30</span></li>',
			'<li><span style="display: none">17:00</span></li>',
			'<li><span style="display: none">17:30</span></li>',
			'<li><span style="display: none">18:00</span></li>',
			'<li><span style="display: none">18:30</span></li>',
			'<li><span style="display: none">19:00</span></li>',
			'<li><span style="display: none">19:30</span></li>',
			'<li><span style="display: none">20:00</span></li>',
			'<li><span style="display: none">20:30</span></li>',
			'<li><span style="display: none">21:00</span></li>',
			'<li><span style="display: none">21:30</span></li>',
			'<li><span style="display: none">22:00</span></li>',
			'<li><span style="display: none">22:30</span></li>',
			'<li><span style="display: none">23:00</span></li>',
			'<li><span style="display: none">23:30</span></li>',
			'<li><span style="display: none">00:00</span></li>',
            '<li><span style="display: none">00:00</span></li>',
            '<li><span style="display: none">00:30</span></li>',
            '<li><span style="display: none">00:30</span></li>',
            '<li><span style="display: none">01:00</span></li>',
            '<li><span style="display: none">01:00</span></li>',
    ]
    indx_list = 0
    for i, t in enumerate(times):
        if lowest_event_time < t.split('">')[1].split("<")[0]:
            indx_list = i - 1
            break
    times_str = '\n'.join(times[indx_list:])
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
		
		/* Star toggle button styles */
		.star-toggle {
			position: absolute;
			top: 5px;
			right: 8px;
			background: none;
			border: none;
			font-size: 16px;
			cursor: pointer;
			color: #ccc;
			transition: color 0.3s ease;
			z-index: 10;
			padding: 2px;
		}
		
		.star-toggle:hover {
			color: #ffd700;
		}
		
		.star-toggle.highlighted {
			color: #ffd700;
		}
		
		.single-event {
			position: relative;
		}
		
		.single-event.highlighted {
			border-left: 5px solid #ffd700 !important;
		}
		
		/* Show toggle styles */
		.show-toggle-container {
			text-align: center;
			margin: 20px 0;
			padding: 15px;
			background: #f5f5f5;
			border-radius: 8px;
		}
		
		.show-toggle-container h3 {
			margin: 0 0 15px 0;
			color: #333;
			font-size: 18px;
		}
		
		.toggle-switch {
			position: relative;
			display: inline-block;
			width: 180px;
			height: 40px;
			background: #ddd;
			border-radius: 20px;
			cursor: pointer;
			transition: background 0.3s ease;
		}
		
		.toggle-switch.favorites-mode {
			background: #ffd700;
		}
		
		.toggle-slider {
			position: absolute;
			top: 3px;
			left: 3px;
			width: 85px;
			height: 34px;
			background: white;
			border-radius: 17px;
			transition: transform 0.3s ease;
			display: flex;
			align-items: center;
			justify-content: center;
			font-weight: 600;
			font-size: 12px;
			color: #333;
		}
		
		.toggle-switch.favorites-mode .toggle-slider {
			transform: translateX(90px);
		}
		
		.toggle-labels {
			position: absolute;
			top: 0;
			left: 0;
			right: 0;
			bottom: 0;
			display: flex;
			align-items: center;
			justify-content: space-between;
			padding: 0 15px;
			font-size: 12px;
			font-weight: 600;
			color: #666;
			pointer-events: none;
		}
		
		.single-event.hidden-by-filter {
			display: none !important;
		}
		
		.events-group.empty-after-filter {
			display: none !important;
		}
		
		.empty-favorites-message {
			display: none;
			text-align: center;
			padding: 40px 20px;
			color: #666;
			font-style: italic;
		}
		
		.empty-favorites-message.show {
			display: block;
		}
	</style>
</head>
<body>

"""+day_links+"""

<div class="show-toggle-container">
	<div class="toggle-switch" id="showToggle">
		<div class="toggle-slider"></div>
		<div class="toggle-labels">
			<span>ALL SHOWS</span>
			<span>FAVORITES</span>
		</div>
	</div>
</div>

<div class="cd-schedule loading">
	<div class="timeline">
		<ul>
"""
+ times_str + 
"""
		</ul>
	</div> <!-- .timeline -->

	<div class="events">
		<ul>



			"""+stages_html+"""




		</ul>
	</div>

	<div class="empty-favorites-message" id="emptyFavoritesMessage">
		<p>No favorite shows selected yet.</p>
		<p>Click the ★ button on any show to add it to your favorites!</p>
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

<script>
// Cookie utility functions
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + '=' + value + ';expires=' + expires.toUTCString() + ';path=/';
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function getHighlightedEvents() {
    const highlighted = getCookie('highlightedEvents');
    return highlighted ? JSON.parse(highlighted) : [];
}

function saveHighlightedEvents(eventIds) {
    setCookie('highlightedEvents', JSON.stringify(eventIds), 365); // Save for 1 year
}

function getShowMode() {
    const mode = getCookie('showMode');
    return mode || 'all';
}

function saveShowMode(mode) {
    setCookie('showMode', mode, 365);
}

function applyShowFilter() {
    const showMode = getShowMode();
    const highlightedEvents = getHighlightedEvents();
    const toggle = $('#showToggle');
    const slider = toggle.find('.toggle-slider');
    const emptyMessage = $('#emptyFavoritesMessage');
    
    if (showMode === 'favorites') {
        toggle.addClass('favorites-mode');
        
        
        // Hide all non-favorite events
        $('.single-event').each(function() {
            const eventId = $(this).attr('data-event-id');
            if (!highlightedEvents.includes(eventId)) {
                $(this).addClass('hidden-by-filter');
            } else {
                $(this).removeClass('hidden-by-filter');
            }
        });
        
        // Check if any favorites exist and are visible
        const visibleFavorites = $('.single-event.highlighted:not(.hidden-by-filter)').length;
        if (visibleFavorites === 0) {
            emptyMessage.addClass('show');
        } else {
            emptyMessage.removeClass('show');
        }
        
    } else {
        toggle.removeClass('favorites-mode');
        
        $('.single-event').removeClass('hidden-by-filter');
        emptyMessage.removeClass('show');
    }
    
    // Update stage group visibility
    $('.events-group').each(function() {
        const visibleEvents = $(this).find('.single-event:not(.hidden-by-filter)').length;
        if (visibleEvents === 0 && showMode === 'favorites') {
            $(this).addClass('empty-after-filter');
        } else {
            $(this).removeClass('empty-after-filter');
        }
    });
}

// Initialize everything when page loads
$(document).ready(function() {
    const highlightedEvents = getHighlightedEvents();
    
    // Apply saved highlights
    highlightedEvents.forEach(function(eventId) {
        const eventElement = $('[data-event-id="' + eventId + '"]');
        eventElement.addClass('highlighted');
        eventElement.find('.star-toggle').addClass('highlighted');
    });
    
    // Apply saved show mode
    applyShowFilter();
    
    // Handle show toggle clicks
    $('#showToggle').on('click', function() {
        const currentMode = getShowMode();
        const newMode = currentMode === 'all' ? 'favorites' : 'all';
        saveShowMode(newMode);
        applyShowFilter();
    });
    
    // Handle star toggle clicks
    $(document).on('click', '.star-toggle', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = $(this);
        const eventElement = button.closest('.single-event');
        const eventId = eventElement.attr('data-event-id');
        let highlightedEvents = getHighlightedEvents();
        
        if (button.hasClass('highlighted')) {
            // Remove highlight
            button.removeClass('highlighted');
            eventElement.removeClass('highlighted');
            highlightedEvents = highlightedEvents.filter(id => id !== eventId);
        } else {
            // Add highlight
            button.addClass('highlighted');
            eventElement.addClass('highlighted');
            if (!highlightedEvents.includes(eventId)) {
                highlightedEvents.push(eventId);
            }
        }
        
        saveHighlightedEvents(highlightedEvents);
        
        // Reapply filter in case we're in favorites mode
        applyShowFilter();
    });
});
</script>
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
        str_idx = str(idx)
        if idx == 0:
            str_idx = ''
        if idx == day_id:
            day_links += '<a href="./index'+str_idx+'.html"><button disabled>'+day+'</button></a>'
        else:
            day_links += '<a href="./index'+str_idx+'.html"><button>'+day+'</button></a>'

    return day_links

def create_day_html(lowest_event_time, title, stages, day_id, days):
    num_stages = len(stages)
    global DAY_ID
    day_links = get_day_links(day_id, days)
    stages_html = '\n'.join(stages)
    day_html = get_raw_day(lowest_event_time, title, num_stages, day_links, stages_html)
    # Create day file
    if DAY_ID != 0:
        str_day_id = str(DAY_ID)
    else:
        str_day_id = ''
    f_day = open('./docs/index'+str_day_id+'.html', 'w')
    f_day.write(day_html)
    f_day.close()
    DAY_ID += 1

def get_stage_html(stage_name, events):
    return STAGE_HTML % (stage_name, ' '.join(events))

def get_event_info(event):
    event_start = event['time']
    event_end = datetime.strptime(event_start, '%H:%M')
    event_end = event_end + timedelta(minutes=55)
    event_end = event_end.strftime('%H:%M')
    event_youtube = event['link'] if event['link'] else ''
    event_name = event['event']
    event_group = event['group']
    return event_start, event_end, event_name, event_youtube, event_group

def get_create_event_html(event_info, stage_id):
    global EVENT_ID
    EVENT_ID += 1
    event_start, event_end, event_name, event_youtube, event_group = get_event_info(event_info)

    # Return event HTML with star toggle button
    return '''<li class="single-event" data-start="'''+event_start+'''" data-end="'''+event_end+'''"  data-content="event-'''+str(EVENT_ID)+'''" data-event="event-'''+str(stage_id)+'''" data-event-id="event-'''+str(EVENT_ID)+'''">
        <button class="star-toggle" title="Toggle highlight">★</button>
        <a target="_blank" href="'''+event_youtube+'''">
            <em class="event-name" style="display: inline-block; font-size: 8px; color: #eee">'''+event_group+'''</em>
            <em class="event-name">'''+event_name+'''</em>
        </a>
    </li>''', event_info['time']