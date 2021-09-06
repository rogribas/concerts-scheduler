# -*- coding: utf-8 -*-
import yaml
import html_resources

STAGE_STRING = (
    '<li class="events-group">'
        '<div class="top-info"><span>%s</span></div>'
        '<ul>'
           '%s'
        '</ul>'
    '</li>')

STRING_EVENT = (
    '<li class="single-event" data-start="%s" data-end="%s" data-content="event-%d" data-event="event-%d">'
        '<a href="#0">'
            '<em class="event-name">%s</em>'
        '</a>'
    '</li>')

STRING_EVENT_FILE = (
    '<div class="event-info">'
    '<div width="500px">'
        '<iframe class="youtube-video" width="420" height="315" z-index="55555"'
            'src="%s">'
        '</iframe>'
    '</div>'
    '</div>')


if __name__ == "__main__":
    schedule_data = yaml.load(open('./schedule.yaml'))
    day_id = 0

    for day in schedule_data:
        day_name = next(iter(day))
        day_stages = []

        stage_id = 0

        lowest_event_time = '22:00'
        for stage in day[day_name]:
            stage_id += 1
            stage_name = next(iter(stage))
            stage_events = []

            for event in stage[stage_name]:
                event_html, event_time = html_resources.get_create_event_html(event, stage_id)
                if int(event_time.split(':')[0]) > 9 and int(event_time.split(':')[0]) < int(lowest_event_time.split(':')[0]):
                    lowest_event_time = event_time
                stage_events.append(event_html)

            stage_html = html_resources.get_stage_html(stage_name, stage_events)
            day_stages.append(stage_html)

        html_resources.create_day_html(lowest_event_time, day_name, day_stages, day_id, [next(iter(d)) for d in schedule_data])
        day_id += 1
