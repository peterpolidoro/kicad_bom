"""Command line interface to Loadstar Sensors USB devices."""
import click
import asyncio
import os
import datetime

from .loadstar_sensors_interface import LoadstarSensorsInterface


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS,
               no_args_is_help=True)
@click.option('-p', '--port',
              default=None,
              help='Device name (e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows)')
@click.option('-H', '--high-speed',
              is_flag=True,
              default=False,
              help='Open serial port with high speed baudrate.')
@click.option('--debug',
              is_flag=True,
              default=False,
              help='Print debugging information.')
@click.option('-i', '--info',
              is_flag=True,
              default=False,
              help='Print the device info and exit')
@click.option('-T', '--tare',
              is_flag=True,
              default=False,
              help='Tare before getting sensor values.')
@click.option('-d', '--duration',
              default=10,
              show_default=True,
              help='Duration of sensor value measurements in seconds.')
@click.option('-u', '--units',
              default='gram',
              show_default=True,
              help='Sensor value units.')
@click.option('-f', '--units-format',
              default='.1f',
              show_default=True,
              help='Units format.')
def cli(port,
        high_speed,
        debug,
        info,
        tare,
        duration,
        units,
        units_format):
    """Command line interface for loadstar sensors."""
    asyncio.run(main(port,
                     high_speed,
                     debug,
                     info,
                     tare,
                     duration,
                     units,
                     units_format))


async def sensor_value_callback(sensor_value):
    now = datetime.datetime.now()
    print(f'{now:%Y-%m-%d %H:%M:%S.%f} - sensor_value -> {sensor_value}')
    await asyncio.sleep(0)

async def main(port,
               high_speed,
               debug,
               info,
               tare,
               duration,
               units,
               units_format):
    dev = LoadstarSensorsInterface(debug=debug)
    if high_speed:
        await dev.open_high_speed_serial_connection(port=port)
    else:
        await dev.open_low_speed_serial_connection(port=port)

    dev.set_sensor_value_units(units)
    dev.set_units_format(units_format)

    # clear_screen()
    await dev.print_device_info()

    if info:
        return

    if tare:
        s = 'Press Enter to tare and then continue or q then Enter to quit.\n'
    else:
        s = 'Press Enter to continue or q then Enter to quit.\n'
    input_value = input(s)
    if (input_value == 'q'):
        return

    if tare:
        print('taring...')
        await dev.tare()
        await asyncio.sleep(1)

    dev.start_getting_sensor_values(sensor_value_callback)
    await asyncio.sleep(duration)
    await dev.stop_getting_sensor_values()
    count = dev.get_sensor_value_count()
    duration = dev.get_sensor_value_duration()
    rate = dev.get_sensor_value_rate()
    print(f'{count} sensor values in {duration} at a rate of {rate}')
    await dev.print_device_info()


def clear_screen():
    """Clear command line for various operating systems."""
    if (os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')
