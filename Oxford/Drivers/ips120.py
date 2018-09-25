"""Module containing a class to interface with an Oxford Instruments IPS 120-10.

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    ips120: a class for interfacing with a IPS 120-10 magnet power supply

"""
from datetime import datetime
import time
import logging



from Oxford.Drivers.driver import AbstractSerialDeviceDriver

# import visa
# from pyvisa.errors import VisaIOError

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

# try:
#     # the pyvisa manager we'll use to connect to the GPIB resources
#     resource_manager = visa.ResourceManager()
# except OSError:
#     logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class ips120(AbstractSerialDeviceDriver):
    """Driver class for the Intelligent Power Supply 120-10 from Oxford Instruments. """

    def __init__(self, adress, **kwargs):
        """Connect to an IPS 120-10 at the specified RS232 address

        Args:
            adress(str): RS232 address of the IPS 120-10 (at the local machine)
        """
        super(ips120, self).__init__(**kwargs)


    def setControl(self, state=3):
        """Set the LOCAL / REMOTE control state of the IPS 120-10

        0 - Local & Locked (default state)
        1 - Remote & Locked
        2 - Local & Unlocked
        3 - Remote & Unlocked

        Args:
            state(int): the state in which to place the IPS 120-10
        """
        if not isinstance(state, int):
            raise AssertionError('PS: setControl: Argument must be integer')
        if state not in [0,1,2,3]:
            raise AssertionError('PS: setControl: Argument must be one of [0,1,2,3]')

        self.write("$C{}".format(state))

    def readField(self):
        """Read the current magnetic field in Tesla

        Returns:
            field(float): current magnetic field in Tesla
        """
        value_str = self.query('R7')
        # self._visa_resource.wait_for_srq()
        # value_str = self._visa_resource.read()

        if value[0] != 'R' or value == '':
            raise AssertionError('PS: readField: Bad reply: {}'.format(value))
        return float(value_str.strip('R+'))

    def readFieldSetpoint(self):
        """Read the current set point for the magnetic field in Tesla

        Returns:
            setpoint(float): current set point for the magnetic field in Tesla
        """
        value_str = self.query('R8')
        # self._visa_resource.wait_for_srq()
        # value_str = self._visa_resource.read()

        if value[0] != 'R' or value == '':
            raise AssertionError('PS: readFieldSetpoint: Bad reply: {}'.format(value))

        return float(value_str.strip('R+'))

    def readFieldSweepRate(self):
        """Read the current magnetic field sweep rate in Tesla/min

        Returns:
            sweep_rate(float): current magnetic field sweep rate in Tesla/min
        """
        value_str = self.query('R9')
        # self._visa_resource.wait_for_srq()
        # value_str = self._visa_resource.read()

        if value[0] != 'R' or value == '':
            raise AssertionError('PS: readFieldSweepRate: Bad reply: {}'.format(value))

        return float(value_str.strip('R+'))

    def setActivity(self, state=1):
        """Set the field activation method

        0 - Hold
        1 - To Set Point
        2 - To Zero
        3 - Clamp (clamp the power supply output)

        Args:
            state(int): the field activation method
        """

        if not isinstance(state, int):
            raise AssertionError('PS: setActivity: Argument must be integer')
        if state not in [0,1,2,3]:
            raise AssertionError('PS: setActivity: Argument must be one of [0,1,2,3]')

        self.write("$A{}".format(state))

    def setSwitchHeater(self, state=1):
        """Set the switch heater activation state

        0 - Heater Off              (close switch)
        1 - Heater On if PSU=Magnet (open switch)
        2 - Heater On, no checks    (open switch)

        Args:
            state(int): the switch heater activation state
        """
        if not isinstance(state, int):
            raise AssertionError('PS: setSwitchHeater: Argument must be integer')
        if state not in [0,1,2]:
            raise AssertionError('PS: setSwitchHeater: Argument must be one of [0,1,2]')
        self.write("$H{}".format(state))

        # TODO: add timer to account for time it takes for switch to activate

    def setFieldSetpoint(self, field):
        """Set the magnetic field set point, in Tesla

        Args:
            field(float): the magnetic field set point, in Tesla
        """
        MAX_FIELD = 8
        if not abs(field) < MAX_FIELD:
            raise AssertionError('PS: setFieldSetpoint: Field must be less than {}'.format(MAX_FIELD))

        self.write("$J{}".format(field))

    def setFieldSweepRate(self, rate):
        """Set the magnetic field sweep rate, in Tesla/min

        Args:
            rate(float): the magnetic field sweep rate, in Tesla/min
        """
        self.write("$T{}".format(rate))

    def setDisplay(self, display):
        """Set the display to show amps or tesla

        Args:
            display(str): One of ['amps','tesla']
        """
        if display not in ['amps','tesla']:
            raise AssertionError("PS: setDisplay: Argument must be one of ['amps','tesla']")

        mode_dict = {'amps':8,
                     'tesla':9
                    }

        self.write("$M{}".format(mode_dict[display]))

    def waitForField(self, timeout=600, error_margin=0.01):
        """Wait for the field to reach the set point

        Args:
            timeout(int): maximum time to wait, in seconds
            error_margin(float): how close the field needs to be to the set point, in tesla

        Returns:
            (bool): whether the field set point was reached
        """

        start_time = datetime.now()
        stop_time = start_time + datetime.timedelta(seconds=timeout)

        while datetime.now() < stop_time:
            field = self.readField()
            set_point = self.readFieldSetpoint()

            if abs(field - set_point) < error_margin:
                return True

            time.sleep(5)

        return False