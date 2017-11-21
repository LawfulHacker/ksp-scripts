import curses
import time
from curses import wrapper

import krpc

conn = krpc.connect(name='REPL')


def is_flight():
    conn.krpc.current_game_scene.name == 'flight'


vessel = conn.space_center.active_vessel
flight = vessel.flight()
orbit = vessel.orbit


def format_value(value):
    if isinstance(value, float):
        return f'{value:10.2f}'
    return value


def show_attr_callback(win, label, x, y):
    def callback(value):
        value = format_value(value)
        win.addstr(y, x, f'{label:30} {value}')
        win.refresh()
    return callback


def show_attr(win, obj, attr, x, y):
    attr_stream = conn.add_stream(getattr, obj, attr)
    attr_stream.add_callback(show_attr_callback(win, attr, x, y))
    attr_stream()


# show_attr(flight, 'aerodynamic_force', 0, 9)
# show_attr(flight, '', 0, 11)

# surface_altitude = conn.add_stream(getattr, flight, 'surface_altitude')
# surface_altitude.add_callback(show_surface_altitude)
# surface_altitude()

# mean_altitude = conn.add_stream(getattr, flight, 'mean_altitude')
# mean_altitude.add_callback(show_mean_altitude)
# mean_altitude()

def main(stdscr):
    stdscr.clear()

    begin_x = 0; begin_y = 1
    height = 12; width = 50
    win = curses.newwin(height, width, begin_y, begin_x)

    stdscr.addstr(0, 0, '-- Flight Information --')
    show_attr(win, flight, 'surface_altitude', 0, 1)
    show_attr(win, flight, 'mean_altitude', 0, 2)
    show_attr(win, flight, 'g_force', 0, 3)
    show_attr(win, flight, 'speed', 0, 4)
    show_attr(win, flight, 'velocity', 0, 5)
    show_attr(win, flight, 'latitude', 0, 6)
    show_attr(win, flight, 'longitude', 0, 7)
    show_attr(win, flight, 'atmosphere_density', 0, 8)
    show_attr(win, flight, 'dynamic_pressure', 0, 9)
    show_attr(win, flight, 'terminal_velocity', 0, 10)

    begin_x = 0; begin_y = 15
    height = 3; width = 50
    win = curses.newwin(height, width, begin_y, begin_x)

    stdscr.addstr(14, 0, '-- Vessel Information --')
    show_attr(win, vessel, 'biome', 0, 1)

    begin_x = 0; begin_y = 20
    height = 8; width = 50
    win = curses.newwin(height, width, begin_y, begin_x)

    stdscr.addstr(19, 0, '-- Orbit Information --')
    show_attr(win, orbit, 'apoapsis', 0, 1)
    show_attr(win, orbit, 'periapsis', 0, 2)
    show_attr(win, orbit, 'apoapsis_altitude', 0, 2)
    show_attr(win, orbit, 'periapsis_altitude', 0, 4)
    show_attr(win, orbit, 'speed', 0, 5)
    show_attr(win, orbit, 'period', 0, 6)
    show_attr(win, conn.space_center, 'ut', 0, 7)
    stdscr.refresh()

    begin_x = 0; begin_y = 20
    height = 8; width = 50
    win = curses.newwin(height, width, begin_y, begin_x)

    def info(str):
        win.addstr(0, 0, str)

    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1
    time.sleep(1)

    info('Launch!')

    vessel.control.activate_next_stage()

    fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
    expr = conn.krpc.Expression.less_than(
        conn.krpc.Expression.call(fuel_amount),
        conn.krpc.Expression.constant_float(0.1))
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()

    info('Booster separation')

    vessel.control.activate_next_stage()
    time.sleep(0.5)
    vessel.control.activate_next_stage()

    mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(10000))
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()

    info('Gravity turn')

    vessel.auto_pilot.target_pitch_and_heading(60, 90)

    stdscr.getkey()


if __name__ == '__main__':
    wrapper(main)

