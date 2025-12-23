import streamlit.components.v1 as components
import json

def fullcalendar(events, options=None, height=600):
    """
    Display a FullCalendar component in Streamlit.
    
    Parameters:
    - events: List of event dictionaries with 'title', 'start', 'end', 'color'
    - options: Dictionary of FullCalendar options
    - height: Height of the calendar in pixels
    """
    
    if options is None:
        options = {
            "initialView": "dayGridMonth",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            },
        }
    
    events_json = json.dumps(events)
    options_json = json.dumps(options)
    
    html_code = f"""
    <link href='https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.10/index.global.css' rel='stylesheet' />
    <link href='https://cdn.jsdelivr.net/npm/@fullcalendar/daygrid@6.1.10/index.global.css' rel='stylesheet' />
    <link href='https://cdn.jsdelivr.net/npm/@fullcalendar/timegrid@6.1.10/index.global.css' rel='stylesheet' />
    <link href='https://cdn.jsdelivr.net/npm/@fullcalendar/list@6.1.10/index.global.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.10/index.global.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/@fullcalendar/daygrid@6.1.10/index.global.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/@fullcalendar/timegrid@6.1.10/index.global.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/@fullcalendar/list@6.1.10/index.global.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/@fullcalendar/interaction@6.1.10/index.global.js'></script>
    
    <div id='calendar' style='height: {height}px;'></div>
    
    <script>
        var calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {{
            ...{options_json},
            events: {events_json}
        }});
        calendar.render();
    </script>
    """
    
    components.html(html_code, height=height)
