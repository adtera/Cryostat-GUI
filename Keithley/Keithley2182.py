# -*- coding: utf-8 -*-
"""
Driver for the Keithley 2182 Nano-Voltmeter
"""

import threading, visa

import logging

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager('C:\\Windows\\System32\\agvisa32.dll')
except OSError:
    logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class Keithley2182(object):

    """
    The Keithley 2182 is a nano-voltmeter. You can find the full specifications
    list in the `user's guide`_.

    Example usage:

    >>> import instruments as ik
    >>> meter = ik.keithley.Keithley2182.open_gpibusb("/dev/ttyUSB0", 10)
    >>> print meter.measure(meter.Mode.voltage_dc)
    """
    def __init__(self, InstrumentAddress = None):



        self._visa_resource = resource_manager.open_resource(InstrumentAddress)
        # self._visa_resource.read_termination = '\r'
        self.CommunicationLock = threading.Lock()
        self.device = self._visa_resource


    def query(self, command):
        """Sends commands as strings to the device and receives strings from the device

        :param command: string generated by a given function, whom will be sent to the device
        :type command: str

        :return: answer from the device
        """
        with self.CommunicationLock:
            received = self.device.query(command)
        # self.CommunicationLock.release()
        return received.strip().split(',')

    def go(self, command):
        """Sends commands as strings to the device

        :param command: string generated by a given function, whom will be sent to the device
        :type command: str

        """
        with self.CommunicationLock:
            self.device.write(command)




#    def measureTemperature(self):
#        self.sendcmd("SENS:CHAN 1")
#        self.sendcmd("SENS:FUNC 'TEMP'")
#        return self.query("SENS:DATA:FRES?")[0]

    def measureVoltage(self):
        """measure voltage
        :return: voltage in V
        :return type: float
        """
#        self.sendcmd("SENS:CHAN 1")
#        self.sendcmd("SENS:FUNC 'VOLT:DC'")
#        return self.query("SENS:DATA:FRES?")[0]
        self.go(':TRIGger:COUNt 1')
        return float(self.query(':READ?')[0])

    def DisplayOn(self):
        self.go8(':DISPlay:ENABle ON')

    def DisplayOff(self):
        self.go(':DISPlay:ENABle OFF')

    def setRate(self, value='MED', num=None):
        """
        Change the measuring rate

        :SENSe SENSe Subsystem:
            :VOLTage DCV1 and DCV2:
                :NPLCycles <n>
                    Specify integration rate in PLCs:
                       [0.01 to 60 (60Hz)]
                       [0.01 to 50 (50Hz)]
                :APERture <n>
                    Specify integration rate in seconds:
                       [166.67μsec to 1 sec (60Hz)]
                       [200μsec to 1 sec (50Hz)]
            """
        if num is None:
            if value == 'FAS':
                self.go(':SENSe:VOLTage:DC:NPLC 0.1')
            if value == 'MED':
                self.go(':SENSe:VOLTage:DC:NPLC 1')
            if value == 'SLO':
                self.go(':SENSe:VOLTage:DC:NPLC 5')
        else:
            if 0.01 > num > 50:
                raise AssertionError('Keithley2182:setRate: The measuring rate'
                                     ' needs to be between 0.01 and 50 NPLCycles'
                                     ' - that is 200microseconds to 1 second '
                                     '(at a 50Hz powerline - europe)')            
            self.go(':SENSe:VOLTage:DC:NPLC {}'.format(num))


    def more_ACAL(self):
        """Commands Description Default
            For ACAL:
                :CALibration CALibration Subsystem:
                    :UNPRotected
                    :ACALibration ACAL:
                    :INITiate Prepare 2182 for ACAL.
                    :STEP1 Perform full ACAL (100V and 10mV).
                    :STEP2 Perform low level ACAL (10mV only).
                    :DONE Exit ACAL (see Note).
                    :TEMPerature? Read the internal temperature (in °C) at the time
                            of the last ACAL.
            :SENSe SENSe Subsystem:
                :TEMPerature
                    :RTEMperature? Measure the present internal temperature (in °C).
            For Front Autozero:
                :SYSTem SYSTem Subsystem:
                    :FAZero [state] <b> Enable or disable Front Autozero. ON
            For Autozero:
                :SYSTem SYSTem Subsystem:
                    :AZERo [state] <b> Enable or disable Autozero. ON
            For LYSNC:
                :SYSTem SYSTem Subsystem:
                    :LSYNc [state] <b> Enable or disable line cycle synchronization. OFF

            not necessarily necessary:
            For Low Charge Injection:
                :SENSe:VOLTage SENSe Subsystem:
                    :CHANnel2
                        :LQMode <b> Enable or disable Low Charge Injection Mode for
                            Channel 2 (see “Pumpout current (low charge injection
                            mode)” for details).
        """
        pass

    def more_Range(self):
        """Commands Description Default
        :SENSe: SENSe Subsystem:
            :VOLTage Volts function:
                [:CHANnel1] Channel 1 (DCV1):
                    :RANGe Range selection:
                        [:UPPer] <n> Specify expected reading: 0 to 120 (volts). 120
                        : AUTO <b> Enable or disable auto range.

        :CHANnel2 Channel 2 (DCV2):
            :RANGe Range selection:
                [:UPPer] <n> Specify expected reading: 0 to 12 (volts). 12
                : AUTO <b> Enable or disable auto range."""
        pass

    def more_device_operation(self):
        """implement LLO and GTL (local locked out & go to local)"""
        pass

